"""
Robustness experiment for the scale control (GPU): addresses "insufficient controls in the scale comparison" (review item 3).
The original scale control had a single random seed and always kept all dev gold passages when downsampling. This adds:
  1. several random seeds (default 0-4): redraw the corpus subset, random benign passages and length-matched controls at each size, to check stability
  2. gold kept vs not kept: from the same random subset of a seed, one copy adds back all dev gold passages as before (keep),
     one does not (nokeep); the two differ only by those gold passages -- this measures the effect of "forcing gold to be kept" on detection difficulty
  3. an extra smaller size 20,000: previously sw was shrunk only one step and yo not at all; this level gives every language a shrunk point
  4. article mode (added in v2): random subset + all passages of the articles containing gold (MIRACL passage id "article#passage").
     Closer to a real small corpus than keep: if an article is in the corpus, its other passages usually are too
  5. local density (added in v2): for each poison, how many of its top-10 neighbours come from the question's gold articles, similarity to gold,
     and the number of passages of the gold articles in the corpus. Stored in *_dens.npz, used by density_analyze.py to test
     "is detection difficulty determined by local density or by corpus size". Existing results without dens are filled in automatically (only this part, fast)
Each (language, size, keep/nokeep, seed) result is stored in its own npz and skipped if it exists: reruns after interruption resume.
    python scale_seeds.py                               # default: trans/bb, seeds 0-4, sizes full 131924 45000 20000,
                                                        #       modes keep nokeep article
    python scale_seeds.py --seeds 0 1 2 --lang te id    # run a part first
    python scale_seeds.py --variants trans en native    # more poison variants (time multiplies)
Output: results/miracl/scale_seeds/<lang>/<size>_<keep|nokeep|article>_s<seed>.npz and the matching _dens.npz
Self-check: seed 0 + keep should match the original detect_feats_sub*.npz exactly (checked in scale_seeds_analyze.py).
All statistics are left to scale_seeds_analyze.py on CPU (filtering questions by judgments, AUROC / TPR / surviving-poison rate).
"""
import argparse, os, sys, time

import numpy as np

from ml_common import LANGS, M3_PATH, ROOT, gpu_topk, load_corpus_emb, load_qrels, load_query_emb, ml_data
from ml_eval_retrieval import subsample_rows
from length_control import lenmatch_sample
from ml_detect import FEATS, two_layer
from ml_attack import load_items, merge_top5, texts_of


def fmt_t(s):
    s = int(s)
    return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}" if s >= 3600 else f"{s // 60}:{s % 60:02d}"


def atomic_save(path, d):
    tmp = path[:-4] + ".tmp.npz"
    np.savez_compressed(tmp, **d)
    os.replace(tmp, path)                  # rename after writing: an interruption leaves no half-written file


def auc(pos, neg):
    neg = np.sort(neg)
    lo, hi = np.searchsorted(neg, pos, "left"), np.searchsorted(neg, pos, "right")
    return float(np.mean((lo + (hi - lo) / 2) / len(neg)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", nargs="+", default=LANGS)
    ap.add_argument("--sizes", nargs="+", default=["full", "131924", "45000", "20000"])
    ap.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2, 3, 4])
    ap.add_argument("--variants", nargs="+", default=["trans"])
    ap.add_argument("--forms", nargs="+", default=["bb"])
    ap.add_argument("--modes", nargs="+", default=["keep", "nokeep", "article"],
                    choices=["keep", "nokeep", "article"])
    ap.add_argument("--n_clean", type=int, default=10000)     # same default as ml_detect.py
    ap.add_argument("--n_match", type=int, default=10000)
    ap.add_argument("--width", type=int, default=5)
    ap.add_argument("--K", type=int, default=50)
    ap.add_argument("--M", type=int, default=10)
    args = ap.parse_args()
    out_root = os.path.join(ROOT, "results", "miracl", "scale_seeds")

    # ---------- list all jobs first, to compute progress ----------
    N_of = {lang: load_corpus_emb(lang)[0].shape[0] for lang in args.lang}
    jobs = []
    for lang in args.lang:
        for size in args.sizes:
            if size == "full":
                modes = ["full"]
            elif int(size) >= N_of[lang]:
                continue                       # corpus not larger than this size: same as full, skip
            else:
                modes = args.modes
            for m in modes:
                for s in args.seeds:
                    p = os.path.join(out_root, lang, f"{size}_{m}_s{s}.npz")
                    jobs.append((lang, size, m, s, p))
    dens_of = lambda p: p[:-4] + "_dens.npz"
    todo = [j for j in jobs if not (os.path.exists(j[4]) and os.path.exists(dens_of(j[4])))]
    n_main = sum(not os.path.exists(j[4]) for j in todo)
    print(f"{len(jobs)} jobs in total, {len(jobs) - len(todo)} done, {len(todo)} to run now"
          f" ({n_main} new, {len(todo) - n_main} only filling in local density)", flush=True)
    if not todo:
        print("nothing to run. Next step: python scale_seeds_analyze.py"); return

    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(M3_PATH, device="cuda").half()
    model.max_seq_length = 512
    enc = lambda xs: model.encode(xs, batch_size=128, normalize_embeddings=True,
                                  convert_to_numpy=True, show_progress_bar=False).astype(np.float16)

    T0, done, cache_lang = time.time(), 0, None
    for lang, size, mode, seed, path in todo:
        t0 = time.time()
        if cache_lang != lang:                 # prepare the shared part of each language only once
            items, _ = load_items(lang)
            corpus_full, cids = load_corpus_emb(lang)
            N = corpus_full.shape[0]
            L_full = np.load(os.path.join(ml_data(lang), "corpus_len_words.npy"))
            qemb, qid2row = load_query_emb(lang)
            c2r = {c: i for i, c in enumerate(cids)}
            qrels = load_qrels(lang, "dev")
            must = np.array(sorted({c2r[d] for q in qrels if q in qid2row for d in qrels[q] if d in c2r}))
            item_gold = np.array(sorted({c2r[d] for it in items for d in it["gold_ids"] if d in c2r}))
            # article id: passage ids look like "1392#5"; the part before # is the article
            _, art = np.unique(np.array([c.split("#")[0] for c in cids]), return_inverse=True)
            must_art = np.flatnonzero(np.isin(art, np.unique(art[must])))   # all passages of the articles containing any dev gold passage
            it_gold = [np.array([c2r[d] for d in it["gold_ids"] if d in c2r], dtype=np.int64) for it in items]
            it_art = [np.unique(art[g]) for g in it_gold]
            Q = qemb[[qid2row[it["qid"]] for it in items]]
            P = {}
            for v in args.variants:
                for f in args.forms:
                    idx = [j for j, it in enumerate(items) if it.get(f"{v}_adv")]
                    if idx:
                        P[(v, f)] = (np.array(idx), enc([texts_of(items[j], v, f)[0] for j in idx]))
            cache_lang = lang

        # ---------- corpus subset ----------
        if size == "full":
            rowmap, corpus = None, corpus_full
            Ns, L, n_added = N, L_full, 0
        else:
            n = int(size)
            extra = {"keep": must, "article": must_art, "nokeep": np.array([], dtype=np.int64)}[mode]
            rowmap = subsample_rows(N, n, extra, seed)
            n_added = len(rowmap) - min(n, N)
            corpus = np.asarray(corpus_full[rowmap])
            Ns, L = len(rowmap), L_full[rowmap]
        pos_of = np.full(N, -1, np.int64)
        pos_of[rowmap if rowmap is not None else np.arange(N)] = np.arange(Ns)
        gold = np.sort(pos_of[item_gold][pos_of[item_gold] >= 0])
        must_in = int((pos_of[must] >= 0).sum())

        os.makedirs(os.path.dirname(path), exist_ok=True)
        msg, short = [], []
        if os.path.exists(path):
            msg.append("main result exists, only filling in local density")
        else:
            # ---------- benign controls (drawn exactly as in ml_detect.py) ----------
            rand = np.sort(np.random.default_rng(seed).choice(Ns, size=min(args.n_clean, Ns), replace=False))
            save = {"corpus": Ns, "n_gold_added": n_added, "dev_gold_in_corpus": must_in, "n_dev_gold": len(must),
                    "rand": rand, "qids": np.array([it["qid"] for it in items])}
            matches, short = {}, []
            for (v, f), (idx, _) in P.items():
                plen = np.array([len(texts_of(items[j], v, f)[0].split()) for j in idx])
                m, rep = lenmatch_sample(L, plen, args.n_match, args.width, gold, np.random.default_rng(seed + 1))
                got, want = sum(b["got"] for b in rep), sum(b["want"] for b in rep)
                if got < want:
                    short.append(f"{v}/{f} {got}/{want}")
                matches[(v, f)] = m
            clean_rows = np.unique(np.concatenate([rand] + list(matches.values())))
            Fc = two_layer(corpus, np.asarray(corpus[clean_rows]), clean_rows, args.K, args.M)
            cpos = {r: i for i, r in enumerate(clean_rows)}
            for k in FEATS:
                save[f"rand_{k}"] = Fc[k][[cpos[r] for r in rand]].astype(np.float32)

            # ---------- poisons: features + retrieval hits (one per question, all questions' poisons in the corpus at once, as in ml_attack.py) ----------
            Sc, Ic = gpu_topk([corpus], Q, 5)
            msg = []
            for (v, f), (idx, Pv) in P.items():
                Fp = two_layer(corpus, Pv, np.full(len(Pv), -1), args.K, args.M)
                Sp = Q.astype(np.float32) @ Pv.astype(np.float32).T
                top = merge_top5(Sc, Ic, Sp, idx)
                hit = np.array([(-1 - p) in top[j] for p, j in enumerate(idx)])
                key = f"{v}_{f}"
                save[f"{key}_items"] = idx
                save[f"{key}_hit5"] = hit
                save[f"{key}_match"] = matches[(v, f)]
                for k in FEATS:
                    save[f"{key}_pois_{k}"] = Fp[k].astype(np.float32)
                    save[f"{key}_match_{k}"] = Fc[k][[cpos[r] for r in matches[(v, f)]]].astype(np.float32)
                a = {k: auc(-Fp[k], -save[f"{key}_match_{k}"]) for k in ("rel_knn10", "knn10")}
                msg.append(f"{key} AUROC rel {a['rel_knn10']:.3f} / knn {a['knn10']:.3f}, hit@5 {hit.mean():.2f}")

            atomic_save(path, save)

        # ---------- local density: how many passages of the question's gold articles surround the poison ----------
        dp = dens_of(path)
        if not os.path.exists(dp):
            full_row = rowmap if rowmap is not None else np.arange(N)
            in_corpus = pos_of >= 0
            dens = {"corpus": Ns}
            for (v, f), (idx, Pv) in P.items():
                Sd, Id = gpu_topk([corpus], Pv, 10)
                nart = art[full_row[Id]]                                  # article of each neighbour
                n_ga10, top1_ga, g_in, g_sim, art_mass = [], [], [], [], []
                for p, j in enumerate(idx):
                    ga = it_art[j]
                    hitm = np.isin(nart[p], ga)
                    n_ga10.append(int(hitm.sum())); top1_ga.append(bool(hitm[0]))
                    g = it_gold[j][in_corpus[it_gold[j]]]
                    g_in.append(len(g) > 0)
                    g_sim.append(float((np.asarray(corpus_full[g], np.float32) @ Pv[p].astype(np.float32)).max())
                                 if len(g) else np.nan)
                    art_mass.append(int((in_corpus & np.isin(art, ga)).sum()) if len(ga) else 0)
                key = f"{v}_{f}"
                dens.update({f"{key}_items": idx, f"{key}_n_goldart_top10": np.array(n_ga10),
                             f"{key}_top1_goldart": np.array(top1_ga), f"{key}_gold_in_corpus": np.array(g_in),
                             f"{key}_gold_sim": np.array(g_sim, np.float32), f"{key}_goldart_mass": np.array(art_mass),
                             f"{key}_nn1": Sd[:, 0].astype(np.float32)})
                msg.append(f"{key} neighbours from gold articles {np.mean(n_ga10):.2f}/10, nearest neighbour from gold article {np.mean(top1_ga):.0%}")
            atomic_save(dp, dens)

        done += 1
        el = time.time() - T0
        eta = el / done * (len(todo) - done)
        bar = "#" * int(30 * done / len(todo))
        print(f"[{bar:<30}] {done}/{len(todo)}  elapsed {fmt_t(el)}  remaining {fmt_t(eta)} | "
              f"{lang} {size} {mode} seed{seed}: corpus {Ns:,} ({n_added:,} added), this step {fmt_t(time.time() - t0)} | "
              + "; ".join(msg) + (f" | WARNING: length matches short by {short}" if short else ""), flush=True)

    print(f"\nAll done, total time {fmt_t(time.time() - T0)}. Next step (CPU is enough): python density_analyze.py")


if __name__ == "__main__":
    main()
