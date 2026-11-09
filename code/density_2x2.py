"""
Controlled intervention: corpus size x local evidence density (GPU, about 20-40 minutes).
The observational "local density" is counted from the poison's neighbours and shares information with the detection score, so a significant regression is not causal.
Here we manipulate the corpus directly and **fix the total number of passages**:
  G  = gold passages of the attacked questions (kept in both conditions, so questions stay answerable)
  A  = the remaining passages of the gold articles ("same-topic evidence")
  B  = all other passages (background)
  low density : G + random background (N - |G|) passages                  -> no A in the corpus
  high density: G + A + random background (N - |G| - |A|) passages        -> total is also N
  Both conditions draw background from the same random permutation; the high-density background is a prefix of the low-density one, so they differ only in "A replaces an equal amount of background".
Sizes N in {20000, 45000} (available for all four languages), 5 seeds per cell. Negatives (random benign passages for thresholds, length-matched benign passages)
are drawn from the background only, so their source distribution is the same in both conditions. Manipulation check: number of A or G passages among the poison's top-10 neighbours.
If A is too large (id), it is truncated to N/2 - |G|; the actual size is recorded.
    python density_2x2.py                      # four languages, trans/bb
    python density_2x2.py --lang te id --seeds 0 1 2
Output: results/miracl/density_2x2/<lang>/<N>_<low|high>_s<seed>.npz; statistics: python density_2x2_analyze.py
"""
import argparse, os, time

import numpy as np

from ml_common import LANGS, M3_PATH, ROOT, gpu_topk, load_corpus_emb, load_query_emb, ml_data
from length_control import lenmatch_sample
from ml_detect import FEATS, two_layer
from ml_attack import load_items, merge_top5, texts_of


def fmt_t(s):
    s = int(s); return f"{s // 60}:{s % 60:02d}"


def auc(pos, neg):
    neg = np.sort(neg)
    lo, hi = np.searchsorted(neg, pos, "left"), np.searchsorted(neg, pos, "right")
    return float(np.mean((lo + (hi - lo) / 2) / len(neg)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", nargs="+", default=LANGS)
    ap.add_argument("--sizes", nargs="+", type=int, default=[20000, 45000])
    ap.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2, 3, 4])
    ap.add_argument("--variant", default="trans")
    ap.add_argument("--form", default="bb")
    ap.add_argument("--n_clean", type=int, default=10000)
    ap.add_argument("--n_match", type=int, default=10000)
    a = ap.parse_args()
    out_root = os.path.join(ROOT, "results", "miracl", "density_2x2")
    jobs = [(l, n, m, s) for l in a.lang for n in a.sizes for m in ("low", "high") for s in a.seeds]
    path = lambda l, n, m, s: os.path.join(out_root, l, f"{n}_{m}_s{s}.npz")
    todo = [j for j in jobs if not os.path.exists(path(*j))]
    print(f"{len(jobs)} jobs in total, {len(todo)} to run now", flush=True)
    if not todo:
        return
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(M3_PATH, device="cuda").half(); model.max_seq_length = 512
    enc = lambda xs: model.encode(xs, batch_size=128, normalize_embeddings=True, convert_to_numpy=True,
                                  show_progress_bar=False).astype(np.float16)
    T0, done, cur = time.time(), 0, None
    key = f"{a.variant}_{a.form}"
    for lang, N, mode, seed in todo:
        t0 = time.time()
        if cur != lang:
            items, _ = load_items(lang)
            corpus_full, cids = load_corpus_emb(lang)
            NF = corpus_full.shape[0]
            Lw = np.load(os.path.join(ml_data(lang), "corpus_len_words.npy"))
            c2r = {c: i for i, c in enumerate(cids)}
            _, art = np.unique(np.array([c.split("#")[0] for c in cids]), return_inverse=True)
            G = np.array(sorted({c2r[d] for it in items for d in it["gold_ids"] if d in c2r}), dtype=np.int64)
            Aall = np.setdiff1d(np.flatnonzero(np.isin(art, np.unique(art[G]))), G)
            Bk = np.setdiff1d(np.arange(NF), np.concatenate([G, Aall]))
            qemb, qid2row = load_query_emb(lang)
            Q = qemb[[qid2row[it["qid"]] for it in items]]
            idx = np.array([j for j, it in enumerate(items) if it.get(f"{a.variant}_adv")])
            texts = [texts_of(items[j], a.variant, a.form)[0] for j in idx]
            P = enc(texts); plen = np.array([len(t.split()) for t in texts])
            it_art = [np.unique(art[[c2r[d] for d in items[j]["gold_ids"] if d in c2r]]) for j in idx]
            print(f"[{lang}] corpus {NF:,}, G {len(G):,}, A {len(Aall):,}, background {len(Bk):,}", flush=True)
            cur = lang
        rng = np.random.default_rng(seed)
        perm = rng.permutation(Bk)
        total = min(N, len(G) + len(Bk))          # if the background is too small (yo 45k), both conditions shrink to the same total
        A = Aall
        cap = total // 2 - len(G)
        if len(A) > cap:                           # the same |A| fixes the background size in both conditions, so totals are equal
            A = np.sort(np.random.default_rng(seed + 100).choice(Aall, cap, replace=False))
        nb = total - len(G) - (len(A) if mode == "high" else 0)
        bg = np.sort(perm[:nb])
        rows = np.sort(np.concatenate([G, bg] + ([A] if mode == "high" else [])))
        corpus = np.asarray(corpus_full[rows]); Ns = len(rows)
        pos_of = np.full(NF, -1, np.int64); pos_of[rows] = np.arange(Ns)
        bg_sub = pos_of[bg]
        Lsub = Lw[rows]
        # negatives are drawn from the background only
        excl = np.ones(Ns, bool); excl[bg_sub] = False
        rand = np.sort(rng.choice(bg_sub, min(a.n_clean, len(bg_sub)), replace=False))
        match, _ = lenmatch_sample(Lsub, plen, a.n_match, 5, np.flatnonzero(excl), np.random.default_rng(seed + 1))
        clean_rows = np.unique(np.concatenate([rand, match]))
        Fc = two_layer(corpus, np.asarray(corpus[clean_rows]), clean_rows)
        cp = {r: i for i, r in enumerate(clean_rows)}
        Fp = two_layer(corpus, P, np.full(len(P), -1))
        # retrieval hits (all poisons in the index at once) and manipulation check
        Sc, Ic = gpu_topk([corpus], Q, 5)
        Sp = Q.astype(np.float32) @ P.astype(np.float32).T
        top = merge_top5(Sc, Ic, Sp, idx)
        hit = np.array([(-1 - p) in top[j] for p, j in enumerate(idx)])
        _, In = gpu_topk([corpus], P, 10)
        nart = art[rows[In]]
        n_ga10 = np.array([int(np.isin(nart[p], it_art[p]).sum()) for p in range(len(idx))])
        save = {"corpus": Ns, "n_G": len(G), "n_A": len(A) if mode == "high" else 0, "n_A_all": len(Aall),
                "items": idx, "qids": np.array([it["qid"] for it in items]), "hit5": hit, "n_ga10": n_ga10}
        for k in FEATS:
            save[f"pois_{k}"] = Fp[k].astype(np.float32)
            save[f"rand_{k}"] = Fc[k][[cp[r] for r in rand]].astype(np.float32)
            save[f"match_{k}"] = Fc[k][[cp[r] for r in match]].astype(np.float32)
        p = path(lang, N, mode, seed); os.makedirs(os.path.dirname(p), exist_ok=True)
        np.savez_compressed(p[:-4] + ".tmp.npz", **save); os.replace(p[:-4] + ".tmp.npz", p)
        done += 1; el = time.time() - T0
        print(f"[{'#' * int(30 * done / len(todo)):<30}] {done}/{len(todo)} elapsed {fmt_t(el)} remaining "
              f"{fmt_t(el / done * (len(todo) - done))} | {lang} N={Ns:,} {mode} seed {seed}: "
              f"A {save['n_A']:,}, same-topic neighbours {n_ga10.mean():.2f}/10, AUROC rel "
              f"{auc(-Fp['rel_knn10'], -save['match_rel_knn10']):.3f} / knn {auc(-Fp['knn10'], -save['match_knn10']):.3f}"
              f", this step {fmt_t(time.time() - t0)}", flush=True)
    print(f"\nall done, total time {fmt_t(time.time() - T0)}. Next: python density_2x2_analyze.py")


if __name__ == "__main__":
    main()
