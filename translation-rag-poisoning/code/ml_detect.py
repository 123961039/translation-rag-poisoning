"""
MIRACL ingestion-time detection (single view): length control + relative isolation for every language x poison variant x prefix form.
    python ml_detect.py                       # all languages; includes the trans variant if poison.jsonl exists
    python ml_detect.py --lang sw te --boot 500
    python ml_detect.py --subsample 131924      # scale comparison: downsample each corpus to the sw size before detection
                                                # (languages already smaller stay unchanged; rowmap uses the same seed as ml_attack --sizes, so results align)
Method
  - reference groups: random benign / length-matched benign (stratified in 5-word buckets of this variant's poison length, no gold) / gold
  - features (smaller = more isolated): nn1, knn10, rel_nn1, rel_knn10 (self minus neighbour mean), lof_knn10 (neighbours' mean distance / own distance)
    neighbours of neighbours are leave-one-out (the candidate is removed from its neighbours' lists); poisons are not in the corpus (one injected per question)
  - AUROC oriented as "more isolated = more suspicious", with bootstrap 95% CI; length_only = word count only (shorter = more suspicious) as a reference
  - low-resource passages are short (median 11 words in yo) and poisons are longer, so length_only can fall below 0.5; this difference is itself reported
Output: results/miracl/detect_summary.md / .json; per-sample features in results/miracl/<lang>/detect_feats.npz (later analyses need no GPU)
"""
import argparse, json, os, time

import numpy as np
from sentence_transformers import SentenceTransformer

from ml_common import (LANGS, M3_PATH, ROOT, gpu_topk, load_corpus_emb, load_qrels, load_query_emb,
                       ml_data, ml_results)
from ml_eval_retrieval import subsample_rows
from length_control import NEGS, lenmatch_sample, score_rows
from relative_isolation import strip_self_both
from ml_attack import VARIANTS, load_items, texts_of

FEATS = ["nn1", "knn10", "rel_nn1", "rel_knn10", "lof_knn10"]


def two_layer(corpus, Q, self_idx, K=50, M=10):
    """Two-layer neighbour features of candidate vectors Q; self_idx is the candidate's corpus row (-1 if not in the corpus)"""
    S, I = gpu_topk([corpus], Q, K + 1)
    S, I = strip_self_both(S, I, self_idx, K)
    nn1, knn10 = S[:, 0], S[:, :10].mean(1)
    U, inv = np.unique(I[:, :M], return_inverse=True)
    inv = inv.reshape(-1, M)
    Su, Iu = gpu_topk([corpus], np.asarray(corpus[U]), 12)
    Sp, Ip = Su[inv], Iu[inv]
    keep = (Ip != U[inv][..., None]) & (Ip != self_idx[:, None, None])
    order = np.argsort(~keep, axis=2, kind="stable")[..., :10]
    Sp = np.take_along_axis(Sp, order, 2)
    nn1_y, knn10_y = Sp[..., 0], Sp.mean(2)
    return {"nn1": nn1, "knn10": knn10, "rel_nn1": nn1 - nn1_y.mean(1), "rel_knn10": knn10 - knn10_y.mean(1),
            "lof_knn10": (1 - knn10_y).mean(1) / (1 - knn10 + 1e-6)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", nargs="+", default=LANGS)
    ap.add_argument("--n_clean", type=int, default=10000)
    ap.add_argument("--n_match", type=int, default=10000)
    ap.add_argument("--width", type=int, default=5)
    ap.add_argument("--K", type=int, default=50)
    ap.add_argument("--M", type=int, default=10)
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--subsample", type=int, default=0,
                    help="downsample the corpus to this many passages (all dev gold passages kept); 0 = full corpus")
    args = ap.parse_args()
    tag = f"_sub{args.subsample}" if args.subsample else ""

    model = SentenceTransformer(M3_PATH, device="cuda").half()
    model.max_seq_length = 512
    enc = lambda xs: model.encode(xs, batch_size=128, normalize_embeddings=True,
                                  convert_to_numpy=True, show_progress_bar=False).astype(np.float16)
    summary = []

    for lang in args.lang:
        items, src = load_items(lang)
        if not items:
            print(f"[{lang}] no poison file, skipped")
            continue
        t0 = time.time()
        corpus, cids = load_corpus_emb(lang)
        N = corpus.shape[0]
        L = np.load(os.path.join(ml_data(lang), "corpus_len_words.npy"))
        assert len(L) == N, "corpus_len_words.npy does not match the corpus size; run ml_check.py first"
        if args.subsample and args.subsample < N:
            # exactly the same rowmap as ml_attack.py --sizes (same seed, same must-keep set), so results align by question
            qrels = load_qrels(lang, "dev")
            _, qid2row = load_query_emb(lang)
            c2r = {c: i for i, c in enumerate(cids)}
            must = np.array(sorted({c2r[d] for q in qrels if q in qid2row for d in qrels[q] if d in c2r}))
            rowmap = subsample_rows(N, args.subsample, must, args.seed)
            corpus = np.asarray(corpus[rowmap])
            cids = [cids[r] for r in rowmap]
            L, N = L[rowmap], len(rowmap)
            print(f"[{lang}] corpus downsampled -> {N:,} passages (including all {len(must):,} dev gold passages)", flush=True)
        cid2row = {c: i for i, c in enumerate(cids)}
        gold = np.array(sorted({cid2row[d] for it in items for d in it["gold_ids"] if d in cid2row}))
        rng = np.random.default_rng(args.seed)
        rand = np.sort(rng.choice(N, size=min(args.n_clean, N), replace=False))

        # poison texts and length-matched samples per variant / form
        combos = {}
        for v in VARIANTS:
            for f in ("bb", "adv"):
                txt = [t for it in items for t in texts_of(it, v, f)[:1]]   # one per question (single view)
                if not txt:
                    continue
                plen = np.array([len(t.split()) for t in txt])
                match, rep = lenmatch_sample(L, plen, args.n_match, args.width, gold,
                                             np.random.default_rng(args.seed + 1))
                want, got = sum(b["want"] for b in rep), sum(b["got"] for b in rep)
                assert got > 0, (f"{lang}/{v}/{f}: no corpus passage has a poison length ({plen.min()}-{plen.max()} words); "
                                 f"length matching impossible")
                if got < want:   # this can get worse after downsampling, so report it explicitly
                    short = [b["bucket"] for b in rep if b["got"] < b["want"]]
                    print(f"  Warning: {v}/{f} length matching found only {got}/{want} passages; short buckets {short}", flush=True)
                combos[(v, f)] = {"txt": txt, "plen": plen, "match": match}

        # features of all benign passages are computed once together
        clean_rows = np.unique(np.concatenate([rand, gold] + [c["match"] for c in combos.values()]))
        Fc = two_layer(corpus, np.asarray(corpus[clean_rows]), clean_rows, args.K, args.M)
        pos = {r: i for i, r in enumerate(clean_rows)}
        print(f"\n[{lang}] {len(items)} questions ({src}), corpus {N:,}; benign features {len(clean_rows):,}, "
              f"{(time.time() - t0) / 60:.1f} min", flush=True)

        save = {"clean_rows": clean_rows, "clean_len": L[clean_rows], **{f"clean_{k}": v for k, v in Fc.items()}}
        for (v, f), c in combos.items():
            P = enc(c["txt"])
            Fp = two_layer(corpus, P, np.full(len(P), -1), args.K, args.M)
            idx = {g: np.array([pos[r] for r in rows]) for g, rows in
                   [("clean-random", rand), ("clean-lenmatch", c["match"]), ("clean-gold", gold)]}
            label = np.concatenate([np.full(len(idx[g]), i) for i, g in enumerate(NEGS)] + [np.full(len(P), 3)])
            vals = {k: np.concatenate([Fc[k][idx[g]] for g in NEGS] + [Fp[k]]) for k in FEATS}
            vals["length_only"] = np.concatenate([L[clean_rows][idx[g]] for g in NEGS] + [c["plen"]]).astype(float)
            rows = score_rows(vals, label, args.boot, np.random.default_rng(args.seed + 2))
            for k, r in rows.items():
                summary.append({"lang": lang, "corpus": int(N), "variant": v, "form": f, "feature": k,
                                "n_poison": len(P), "n_match": int(len(c["match"])),
                                "len_mean": {g: float(vals["length_only"][label == i].mean())
                                             for i, g in enumerate(NEGS + ["poison"])}, **r})
            best = max(FEATS, key=lambda k: rows[k]["AUROC_vs_clean-lenmatch"])
            print(f"  {v:6s} {f:3s} n={len(P):3d} words poison/matched {c['plen'].mean():5.1f}/{L[c['match']].mean():5.1f} | "
                  f"vs length-matched: " + "  ".join(f"{k} {rows[k]['AUROC_vs_clean-lenmatch']:.3f}" for k in FEATS)
                  + f" | length_only vs random {rows['length_only']['AUROC_vs_clean-random']:.3f} | best {best}", flush=True)
            save.update({f"{v}_{f}_len": c["plen"], f"{v}_{f}_match": c["match"],
                         **{f"{v}_{f}_{k}": Fp[k] for k in FEATS}})
        np.savez(os.path.join(ml_results(lang), f"detect_feats{tag}.npz"), rand=rand, gold=gold, **save)

    out = os.path.join(ROOT, "results", "miracl")
    json.dump(summary, open(os.path.join(out, f"detect_summary{tag}.json"), "w"), indent=1, ensure_ascii=False)
    cell = lambda r, g: (f"{r[f'AUROC_vs_{g}']:.3f}" + (f" ({r[f'CI_vs_{g}'][0]:.2f}–{r[f'CI_vs_{g}'][1]:.2f})"
                                                       if r[f"CI_vs_{g}"] else ""))
    head = (f"# Ingestion-time detection (scale comparison: corpora downsampled to {args.subsample:,} passages; smaller languages unchanged)\n"
            if args.subsample else "# Ingestion-time detection (full corpora)\n")
    lines = [head, "| lang | corpus | variant | form | questions | matched group | feature | vs random | vs length-matched | vs gold |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for r in summary:
        lines.append(f"| {r['lang']} | {r['corpus']:,} | {r['variant']} | {r['form']} | {r['n_poison']} | "
                     f"{r['n_match']:,} | {r['feature']} | "
                     f"{cell(r, 'clean-random')} | {cell(r, 'clean-lenmatch')} | {cell(r, 'clean-gold')} |")
    open(os.path.join(out, f"detect_summary{tag}.md"), "w").write("\n".join(lines) + "\n")
    print(f"\nfull table: {out}/detect_summary{tag}.md; per-sample features: results/miracl/<lang>/detect_feats{tag}.npz")


if __name__ == "__main__":
    main()
