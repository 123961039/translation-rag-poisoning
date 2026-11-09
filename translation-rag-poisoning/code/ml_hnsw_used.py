"""
Approximate-index (HNSW) sensitivity of the ingestion-time detectors knn10 / rel_knn10.

The paper's features use EXACT top-k search (ml_detect.py). Here we recompute the same two-layer
features with a FAISS HNSW index and compare, on the same candidates:
  * neighbour recall@10 of HNSW vs exact (validation sample),
  * score agreement (Spearman, mean |diff|),
  * AUROC (poison vs length-matched benign) and TPR@5%/1% FPR (threshold from random benign),
  * build time, query latency, peak memory.
Exact features for benign candidates are read from detect_feats*.npz (computed by ml_detect.py);
exact features for poisons are recomputed here by brute force with the same embeddings used for HNSW,
so that exact-vs-HNSW differences come only from the index.

Usage
    python ml_hnsw.py --phase encode                       # encode poison texts once (GPU if available, else CPU)
    python ml_hnsw.py --phase run --lang sw yo             # full corpora (needs ~1.5 GB RAM for sw)
    python ml_hnsw.py --phase run --lang sw te yo id --size 45000   # downsampled corpora, same rows as the paper
    python ml_hnsw.py --phase summary                      # collect everything into results/miracl/hnsw/summary.md
Outputs: results/miracl/hnsw/
"""
import argparse, glob, json, os, resource, time

import numpy as np

from ml_common import LANGS, M3_PATH, ROOT, load_corpus_emb, load_keep, load_qrels, load_query_emb, ml_results

COMBOS = [("trans", "bb"), ("trans", "adv"), ("native", "bb"), ("en", "bb")]
OUT = os.path.join(ROOT, "results", "miracl", "hnsw")
JUDG = os.path.join(ROOT, "results", "miracl", "review_judgments_native.json")


# ---------------------------------------------------------------- helpers copied from the pipeline
def load_items(lang):                         # = ml_attack.load_items (without heavy imports)
    for name in ("poison.jsonl", "poison_gen.jsonl"):
        p = os.path.join(ml_results(lang), name)
        if os.path.exists(p):
            return [json.loads(l) for l in open(p)]
    return []


def texts_of(it, variant, form):              # = ml_attack.texts_of
    adv = it.get(f"{variant}_adv") or []
    return [f"{it['question']} {t}" for t in adv] if form == "bb" else list(adv)


def subsample_rows(N, n, must, seed):         # = ml_eval_retrieval.subsample_rows
    rng = np.random.default_rng(seed)
    keep = np.zeros(N, bool)
    keep[rng.choice(N, size=min(n, N), replace=False)] = True
    keep[must] = True
    return np.flatnonzero(keep)


def poison_texts(lang, combos=None):
    """Per combo: texts in the same order as ml_detect (first text of every item that has one) + native-valid mask."""
    items = load_items(lang)
    keep, _ = load_keep(lang, items, "bad", JUDG)
    out = {}
    for v, f in COMBOS:
        if combos and f"{v}_{f}" not in combos:
            continue
        txt, valid = [], []
        for it, k in zip(items, keep):
            t = texts_of(it, v, f)[:1]
            if t:
                txt.append(t[0]); valid.append(k)
        out[f"{v}_{f}"] = (txt, np.array(valid, bool))
    return out


def peak_mb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024


# ---------------------------------------------------------------- phase 1: encode poisons
def encode(args):
    import torch
    from sentence_transformers import SentenceTransformer
    cuda = torch.cuda.is_available()
    if cuda:
        model = SentenceTransformer(M3_PATH, device="cuda").half()      # identical to ml_detect.py
    else:
        torch.set_num_threads(max(1, os.cpu_count() or 1))
        try:
            model = SentenceTransformer(M3_PATH, device="cpu", model_kwargs={"torch_dtype": torch.bfloat16})
        except TypeError:   # old sentence-transformers without model_kwargs: fp32 needs ~2.5 GB RAM
            print("sentence-transformers too old for bf16 loading; loading fp32 (needs ~2.5 GB RAM)", flush=True)
            model = SentenceTransformer(M3_PATH, device="cpu")
    model.max_seq_length = 512
    print(f"encoder on {'GPU fp16' if cuda else 'CPU bf16'}", flush=True)
    os.makedirs(OUT, exist_ok=True)
    for lang in args.lang:
        p = os.path.join(OUT, f"poison_emb_{lang}.npz")
        if os.path.exists(p) and not args.force:
            print(f"[{lang}] exists, skip ({p})"); continue
        save, t0 = {}, time.time()
        for key, (txt, valid) in poison_texts(lang, args.combos).items():
            E = model.encode(txt, batch_size=32 if cuda else 4, normalize_embeddings=True,
                             convert_to_numpy=True, show_progress_bar=not cuda)
            save[key] = E.astype(np.float16); save[key + "_valid"] = valid
            print(f"[{lang}] {key}: {len(txt)} texts, {time.time() - t0:.0f}s", flush=True)
        save["device"] = np.array("cuda-fp16" if cuda else "cpu-bf16")
        np.savez_compressed(p, **save)


# ---------------------------------------------------------------- exact search (CPU brute force)
def exact_topk(corpus, Q, k, chunk=5000, qbatch=2000):
    """corpus: (N,d) fp16 array/mmap; Q: (n,d) float32. Returns (S,I) sorted desc. Memory-bounded."""
    outS, outI = [], []
    for q0 in range(0, Q.shape[0], qbatch):
        Qb = Q[q0:q0 + qbatch]
        bestS = np.full((len(Qb), k), -np.inf, np.float32); bestI = np.full((len(Qb), k), -1, np.int64)
        for s in range(0, corpus.shape[0], chunk):
            S = Qb @ np.asarray(corpus[s:s + chunk], np.float32).T
            kk = min(k, S.shape[1])
            part = np.argpartition(-S, kk - 1, axis=1)[:, :kk]
            allS = np.concatenate([bestS, np.take_along_axis(S, part, 1)], 1)
            allI = np.concatenate([bestI, part + s], 1)
            o = np.argsort(-allS, 1, kind="stable")[:, :k]
            bestS, bestI = np.take_along_axis(allS, o, 1), np.take_along_axis(allI, o, 1)
        outS.append(bestS); outI.append(bestI)
    return np.concatenate(outS), np.concatenate(outI)


def batched(search, corpus, k, Q=None, rows=None, bs=10000):
    """Search either explicit queries Q or corpus rows (materialised batch by batch to bound memory)."""
    n = len(Q) if Q is not None else len(rows)
    outS, outI = [], []
    for s in range(0, n, bs):
        q = Q[s:s + bs] if Q is not None else np.asarray(corpus[rows[s:s + bs]], np.float32)
        S, I = search(np.ascontiguousarray(q, dtype=np.float32), k)
        outS.append(np.asarray(S, np.float32)); outI.append(np.asarray(I, np.int64))
    return np.concatenate(outS), np.concatenate(outI)


def two_layer(search, corpus, self_idx, Q=None, rows=None, M=10):
    """Same definition as ml_detect.two_layer. Candidates are queries Q (poisons) or corpus rows (benign)."""
    S, I = batched(search, corpus, M + 1, Q=Q, rows=rows)
    keep = I != self_idx[:, None]
    o = np.argsort(~keep, 1, kind="stable")[:, :M]
    S, I = np.take_along_axis(S, o, 1), np.take_along_axis(I, o, 1)
    knn = S.mean(1)
    U, inv = np.unique(I, return_inverse=True)
    inv = inv.reshape(-1, M)
    Su, Iu = batched(search, corpus, 12, rows=U)
    Sp, Ip = Su[inv], Iu[inv]
    ok = (Ip != U[inv][..., None]) & (Ip != self_idx[:, None, None])
    o2 = np.argsort(~ok, axis=2, kind="stable")[..., :10]
    knn_y = np.take_along_axis(Sp, o2, 2).mean(2)
    return {"knn10": knn, "rel_knn10": knn - knn_y.mean(1), "nbr": I}


# ---------------------------------------------------------------- metrics
def auroc(pos, neg):
    from scipy.stats import rankdata
    r = rankdata(np.concatenate([pos, neg]))
    return (r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))


def metrics(feat_pos, feat_match, feat_rand):
    sp, sm, sr = -feat_pos, -feat_match, -feat_rand          # more isolated = more suspicious
    return {"auroc": float(auroc(sp, sm)),
            "tpr5": float((sp > np.quantile(sr, 0.95)).mean()),
            "tpr1": float((sp > np.quantile(sr, 0.99)).mean())}


# ---------------------------------------------------------------- phase 2: run
def run_one(lang, size, args):
    import faiss
    faiss.omp_set_num_threads(args.threads)
    from scipy.stats import spearmanr
    corpus, cids = load_corpus_emb(lang)
    N = corpus.shape[0]
    tag = "" if size == "full" else f"_sub{size}"
    if size != "full" and int(size) < N:          # identical rows to ml_detect.py --subsample
        qrels = load_qrels(lang, "dev")
        _, qid2row = load_query_emb(lang)
        c2r = {c: i for i, c in enumerate(cids)}
        must = np.array(sorted({c2r[d] for q in qrels if q in qid2row for d in qrels[q] if d in c2r}))
        corpus = np.asarray(corpus[subsample_rows(N, int(size), must, args.seed)])
        N = corpus.shape[0]
    Z = np.load(os.path.join(ml_results(lang), f"detect_feats{tag}.npz"))
    PE = np.load(os.path.join(OUT, f"poison_emb_{lang}.npz"))
    clean_rows = Z["clean_rows"]; pos = {r: i for i, r in enumerate(clean_rows)}
    combos = [f"{v}_{f}" for v, f in COMBOS if f"{v}_{f}_match" in Z.files and f"{v}_{f}" in PE.files]
    cand = np.unique(np.concatenate([Z["rand"]] + [Z[f"{c}_match"] for c in combos]))
    ci = np.array([pos[r] for r in cand])
    res = {"lang": lang, "size": size, "N": int(N), "n_clean": int(len(cand)), "device_encode": str(PE["device"]),
           "threads": args.threads, "combos": {}, "index": {}}
    print(f"\n[{lang} {size}] N={N:,}, benign candidates {len(cand):,}, combos {combos}", flush=True)

    # exact features for poisons (brute force) + validation of the benign exact features from the npz
    ex_search = lambda Q, k: exact_topk(corpus, Q, k)
    t0 = time.time()
    exact_p = {c: two_layer(ex_search, corpus, np.full(len(PE[c]), -1), Q=PE[c].astype(np.float32)) for c in combos}
    t_exact = (time.time() - t0) / sum(len(PE[c]) for c in combos)
    rng = np.random.default_rng(args.seed)
    vs = np.sort(rng.choice(cand, size=min(args.n_val, len(cand)), replace=False))
    exact_v = two_layer(ex_search, corpus, vs, rows=vs)
    vi = np.array([pos[r] for r in vs])
    res["validation"] = {
        "benign_knn10_maxdiff_vs_npz": float(np.abs(exact_v["knn10"] - Z["clean_knn10"][vi]).max()),
        "benign_rel_maxdiff_vs_npz": float(np.abs(exact_v["rel_knn10"] - Z["clean_rel_knn10"][vi]).max()),
        "poison_rel_maxdiff_vs_npz": {c: float(np.abs(exact_p[c]["rel_knn10"] - Z[f"{c}_rel_knn10"]).max())
                                      for c in combos},
        "exact_cpu_sec_per_poison": t_exact}
    print(f"  validation: {json.dumps(res['validation'])}", flush=True)

    # exact metrics (benign from npz, poison recomputed)
    def collect(feat_b, feat_p):
        out = {}
        for c in combos:
            m = PE[f"{c}_valid"]
            mi = np.array([pos[r] for r in Z[f"{c}_match"]]); ri = np.array([pos[r] for r in Z["rand"]])
            out[c] = {f: metrics(feat_p[c][f][m], feat_b[f][mi], feat_b[f][ri]) for f in ("knn10", "rel_knn10")}
            out[c]["n_poison"] = int(m.sum())
        return out
    exact_b = {"knn10": Z["clean_knn10"], "rel_knn10": Z["clean_rel_knn10"]}
    res["combos"]["exact"] = collect(exact_b, exact_p)

    for M in args.M:
        index = faiss.IndexHNSWFlat(corpus.shape[1], M, faiss.METRIC_INNER_PRODUCT)
        index.hnsw.efConstruction = args.efc
        t0 = time.time()
        for s in range(0, N, 20000):
            index.add(np.asarray(corpus[s:s + 20000], np.float32))
        t_build = time.time() - t0
        print(f"  HNSW M={M} built in {t_build:.0f}s, peak RSS {peak_mb():.0f} MB", flush=True)
        for ef in args.ef:
            index.hnsw.efSearch = ef
            hs = lambda Q, k: index.search(Q, k)
            t0 = time.time()
            hp = {c: two_layer(hs, corpus, np.full(len(PE[c]), -1), Q=PE[c].astype(np.float32)) for c in combos}
            t_poison = (time.time() - t0) / sum(len(PE[c]) for c in combos)
            hb_full = two_layer(hs, corpus, cand, rows=cand)
            hb = {f: np.zeros(len(clean_rows)) for f in ("knn10", "rel_knn10")}
            for f in hb:
                hb[f][ci] = hb_full[f]
            hv = two_layer(hs, corpus, vs, rows=vs)
            recall = float(np.mean([len(set(a) & set(b)) / 10 for a, b in zip(hv["nbr"], exact_v["nbr"])]))
            key = f"hnsw_M{M}_ef{ef}"
            res["combos"][key] = collect(hb, hp)
            res["index"][key] = {
                "build_sec": t_build, "recall10": recall, "sec_per_poison_two_layer": t_poison,
                "spearman_rel_benign": float(spearmanr(hb_full["rel_knn10"], Z["clean_rel_knn10"][ci])[0]),
                "mean_absdiff_rel_benign": float(np.abs(hb_full["rel_knn10"] - Z["clean_rel_knn10"][ci]).mean()),
                "peak_rss_mb": peak_mb()}
            print(f"  {key}: recall@10 {recall:.3f}, {1000 * t_poison:.1f} ms/poison, "
                  f"trans_bb rel AUROC {res['combos'][key].get('trans_bb', {}).get('rel_knn10', {}).get('auroc', float('nan')):.3f}"
                  f" (exact {res['combos']['exact'].get('trans_bb', {}).get('rel_knn10', {}).get('auroc', float('nan')):.3f})",
                  flush=True)
        del index
    os.makedirs(OUT, exist_ok=True)
    json.dump(res, open(os.path.join(OUT, f"hnsw_{lang}_{size}.json"), "w"), indent=1)


def summary(_args):
    rows = [json.load(open(p)) for p in sorted(glob.glob(os.path.join(OUT, "hnsw_*_*.json")))]
    L = ["# HNSW vs exact search for knn10 / rel_knn10 (native-valid poisons, length-matched benign for AUROC,"
         " random benign for thresholds)\n",
         "| lang | corpus | index | recall@10 | ms/passage | build s | trans/bb rel AUROC | ΔAUROC | TPR@5% | ΔTPR@5% |"
         " TPR@1% | ΔTPR@1% | knn10 ΔAUROC | max |ΔAUROC| any combo/feature |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        ex = r["combos"]["exact"]
        for key, ix in r["index"].items():
            h = r["combos"][key]
            tb, eb = h.get("trans_bb", {}), ex.get("trans_bb", {})
            if not tb:
                continue
            mx = max(abs(h[c][f]["auroc"] - ex[c][f]["auroc"]) for c in h for f in ("knn10", "rel_knn10"))
            L.append(f"| {r['lang']} | {r['N']:,} | {key} | {ix['recall10']:.3f} | {1000 * ix['sec_per_poison_two_layer']:.1f} |"
                     f" {ix['build_sec']:.0f} | {tb['rel_knn10']['auroc']:.3f} | {tb['rel_knn10']['auroc'] - eb['rel_knn10']['auroc']:+.3f} |"
                     f" {tb['rel_knn10']['tpr5']:.2f} | {tb['rel_knn10']['tpr5'] - eb['rel_knn10']['tpr5']:+.2f} |"
                     f" {tb['rel_knn10']['tpr1']:.2f} | {tb['rel_knn10']['tpr1'] - eb['rel_knn10']['tpr1']:+.2f} |"
                     f" {tb['knn10']['auroc'] - eb['knn10']['auroc']:+.3f} | {mx:.3f} |")
        L.append(f"| {r['lang']} | {r['N']:,} | exact (CPU brute force) | 1.000 |"
                 f" {1000 * r['validation']['exact_cpu_sec_per_poison']:.1f} | – | {ex['trans_bb']['rel_knn10']['auroc']:.3f} | – |"
                 f" {ex['trans_bb']['rel_knn10']['tpr5']:.2f} | – | {ex['trans_bb']['rel_knn10']['tpr1']:.2f} | – | – | – |")
    L += ["", "## Validation (exact recomputation vs. the paper's features)", "",
          "| lang | corpus | encoder | benign knn10 max|Δ| | benign rel max|Δ| | poison rel max|Δ| (per combo) |", "|---|---|---|---|---|---|"]
    for r in rows:
        v = r["validation"]
        L.append(f"| {r['lang']} | {r['N']:,} | {r['device_encode']} | {v['benign_knn10_maxdiff_vs_npz']:.1e} |"
                 f" {v['benign_rel_maxdiff_vs_npz']:.1e} | " + ", ".join(f"{c} {x:.1e}" for c, x in v['poison_rel_maxdiff_vs_npz'].items()) + " |")
    open(os.path.join(OUT, "summary.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["encode", "run", "summary"], required=True)
    ap.add_argument("--lang", nargs="+", default=LANGS)
    ap.add_argument("--size", default="full", help="full or a subsample size used in the paper (131924 / 45000)")
    ap.add_argument("--M", type=int, nargs="+", default=[16, 32])
    ap.add_argument("--efc", type=int, default=200)
    ap.add_argument("--ef", type=int, nargs="+", default=[16, 64, 256])
    ap.add_argument("--n_val", type=int, default=500)
    ap.add_argument("--threads", type=int, default=os.cpu_count() or 1)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--combos", nargs="+", default=None,
                    help="subset of trans_bb trans_adv native_bb en_bb (default: all four)")
    args = ap.parse_args()
    if args.phase == "encode":
        encode(args)
    elif args.phase == "run":
        for lang in args.lang:
            run_one(lang, args.size, args)
        summary(args)
    else:
        summary(args)


if __name__ == "__main__":
    main()
