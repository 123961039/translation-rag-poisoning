"""
Second-encoder robustness check for the detector benchmark (Table 3).

Question: do the detection results depend on BGE-M3?  This script re-embeds the four MIRACL corpora
with another dense encoder and recomputes the distance / density detectors (knn10, rel_knn10, kNN distance ratio,
Mahalanobis, Isolation Forest) on EXACTLY the same poisons and the same benign passages as
results/miracl/baselines/<lang>.npz, so the two encoders are directly comparable.  No LLM is needed.

    cd code
    # 1) download the encoder once (any sentence-transformers model works)
    #    HF_ENDPOINT=https://hf-mirror.com huggingface-cli download intfloat/multilingual-e5-large \
    #        --local-dir $HF_MODELS/multilingual-e5-large
    # 2) embed + score + summarize (GPU; about as long as the BGE-M3 embedding, i.e. under 1 h in total)
    python second_encoder.py --model $HF_MODELS/multilingual-e5-large --name me5-large \
        --doc_prefix "passage: " --query_prefix "query: "
    # stages can be run separately and are resumable:
    python second_encoder.py --name me5-large --stage summary          # CPU only, rewrites the tables

Prefixes: multilingual-e5 expects "passage: " / "query: ".  For an encoder without prefixes pass
--doc_prefix "" --query_prefix "".

What is held fixed (same as the BGE-M3 benchmark)
  poisons        first poison per question, variants native / trans / en, forms bb and adv
  benign         the 2,000 random benign passages (thresholds) and the 1,000 length-matched benign
                 passages per variant (AUROC) stored in baselines/<lang>.npz; for the adv form, 1,000
                 length-matched passages are drawn from detect_feats.npz with --seed
  question filter native-speaker judgments (results/miracl/review_judgments_native.json)
  scores         two-layer leave-one-out neighbour features, identical to ml_detect.two_layer (K=50, M=10)
What changes: the vectors (corpus, poisons, queries) and therefore neighbours, thresholds and hit@5.

Output
  emb/miracl/<lang>/<name>/corpus_emb_fp16.npy                 (not part of the repository)
  results/miracl/encoder2/<name>/<lang>.npz                     per-item scores
  results/miracl/encoder2/<name>/summary.md, summary.json       tables, side by side with BGE-M3
"""
import argparse, hashlib, json, os, time

import numpy as np

from ml_common import LANGS, ROOT, corpus_parquet, doc_format, ml_results

VARIANTS = ["trans", "native", "en"]
FORMS = ["bb", "adv"]
METHODS = [("rel_knn10", "rel_knn10"), ("knn10", "knn10"), ("lof_knn10", "kNN distance ratio"),
           ("maha", "Mahalanobis"), ("iforest", "Isolation Forest")]
SELFTEST = False


# ---------------------------------------------------------------- helpers (same logic as the main pipeline)
def load_items(lang):
    for name in ("poison.jsonl", "poison_gen.jsonl"):
        p = os.path.join(ml_results(lang), name)
        if os.path.exists(p):
            return [json.loads(l) for l in open(p, encoding="utf-8")]
    return []


def texts_of(it, variant, form):
    adv = it.get(f"{variant}_adv") or []
    return [f"{it['question']} {t}" for t in adv] if form == "bb" else list(adv)


def topk(corpus, Q, k):
    """Exact inner-product top-k.  GPU: the repository's common.gpu_topk.  Self-test: numpy."""
    if not SELFTEST:
        from common import gpu_topk
        return gpu_topk([corpus], Q, k)
    Q = np.asarray(Q, np.float32)
    S = np.empty((len(Q), k), np.float32); I = np.empty((len(Q), k), np.int64)
    C = np.asarray(corpus, np.float32)
    for a in range(0, len(Q), 512):
        s = Q[a:a + 512] @ C.T
        i = np.argpartition(-s, k - 1, axis=1)[:, :k]
        v = np.take_along_axis(s, i, 1)
        o = np.argsort(-v, axis=1, kind="stable")
        S[a:a + 512], I[a:a + 512] = np.take_along_axis(v, o, 1), np.take_along_axis(i, o, 1)
    return S, I


def two_layer(corpus, Q, self_idx, K=50, M=10):
    """Copy of ml_detect.two_layer: features of candidates Q; self_idx = corpus row of the candidate, -1 if not in the corpus."""
    S, I = topk(corpus, Q, K + 1)
    keep = I != self_idx[:, None]
    order = np.argsort(~keep, axis=1, kind="stable")[:, :K]
    S, I = np.take_along_axis(S, order, 1), np.take_along_axis(I, order, 1)
    knn10 = S[:, :10].mean(1)
    U, inv = np.unique(I[:, :M], return_inverse=True)
    inv = inv.reshape(-1, M)
    Su, Iu = topk(corpus, np.asarray(corpus[U]), 12)
    Sp, Ip = Su[inv], Iu[inv]
    keep = (Ip != U[inv][..., None]) & (Ip != self_idx[:, None, None])
    order = np.argsort(~keep, axis=2, kind="stable")[..., :10]
    Sp = np.take_along_axis(Sp, order, 2)
    knn10_y = Sp.mean(2)
    return {"knn10": knn10, "rel_knn10": knn10 - knn10_y.mean(1),
            "lof_knn10": (1 - knn10_y).mean(1) / (1 - knn10 + 1e-6)}


def auc(pos, neg):
    neg = np.sort(neg)
    lo, hi = np.searchsorted(neg, pos, "left"), np.searchsorted(neg, pos, "right")
    return float(np.mean((lo + (hi - lo) / 2) / len(neg)))


class FakeEncoder:
    """Self-test only: deterministic random unit vectors, no model."""
    dim = 64

    def get_sentence_embedding_dimension(self):
        return self.dim

    def encode(self, texts, **kw):
        out = np.empty((len(texts), self.dim), np.float32)
        for i, t in enumerate(texts):
            seed = int.from_bytes(hashlib.md5(t.encode("utf-8")).digest()[:8], "little")
            out[i] = np.random.default_rng(seed).standard_normal(self.dim)
        return out / np.linalg.norm(out, axis=1, keepdims=True)


def load_encoder(args):
    if SELFTEST:
        return FakeEncoder()
    from sentence_transformers import SentenceTransformer
    m = SentenceTransformer(args.model, device=args.device)
    if args.device == "cuda":
        m.half()
    m.max_seq_length = args.max_len
    return m


def emb_dir(lang, name):
    d = os.path.join(ROOT, "emb", "miracl", lang, name)
    os.makedirs(d, exist_ok=True)
    return d


def out_dir(name):
    d = os.path.join(ROOT, "results", "miracl", "encoder2", name)
    os.makedirs(d, exist_ok=True)
    return d


# ---------------------------------------------------------------- stage 1: embed the corpus (resumable)
def embed_lang(model, lang, args):
    import pyarrow.parquet as pq
    out = emb_dir(lang, args.name)
    pf = pq.ParquetFile(corpus_parquet(lang))
    N = pf.metadata.num_rows
    dim = model.get_sentence_embedding_dimension()
    emb_path, prog_path = os.path.join(out, "corpus_emb_fp16.npy"), os.path.join(out, "progress.json")
    done = json.load(open(prog_path))["done"] if os.path.exists(prog_path) else 0
    if done >= N:
        print(f"[{lang}] corpus already embedded ({N:,} passages)", flush=True)
        return
    print(f"\n[{lang}] embedding {N:,} passages, {dim} dims, about {N * dim * 2 / 2**30:.2f} GB; resuming from {done:,}", flush=True)
    emb = np.lib.format.open_memmap(emb_path, mode="r+" if os.path.exists(emb_path) and done > 0 else "w+",
                                    dtype=np.float16, shape=(N, dim))
    pos, t0, done0 = 0, time.time(), done
    for batch in pf.iter_batches(batch_size=args.chunk, columns=["title", "text"]):
        n = batch.num_rows
        if pos + n <= done:
            pos += n
            continue
        d = batch.to_pydict()
        texts = [args.doc_prefix + doc_format((t or "").strip(), (x or "").strip()) for t, x in zip(d["title"], d["text"])]
        start = max(done - pos, 0)
        vec = model.encode(texts[start:], batch_size=args.batch, normalize_embeddings=True,
                           convert_to_numpy=True, show_progress_bar=False)
        emb[pos + start: pos + n] = np.asarray(vec).astype(np.float16)
        emb.flush()
        pos += n
        done = pos
        json.dump({"done": done, "total": N}, open(prog_path, "w"))
        rate = (done - done0) / (time.time() - t0 + 1e-9)
        print(f"  {done:,}/{N:,} ({done / N:.1%})  {rate:.0f} passages/s  about {(N - done) / max(rate, 1e-9) / 60:.0f} min left", flush=True)
    del emb


# ---------------------------------------------------------------- stage 2: scores on the same poisons / benign passages
def score_lang(model, lang, args):
    outp = os.path.join(out_dir(args.name), f"{lang}.npz")
    if os.path.exists(outp) and not args.redo:
        print(f"[{lang}] scores exist ({outp}); use --redo to recompute", flush=True)
        return
    t0 = time.time()
    items = load_items(lang)
    zb = np.load(os.path.join(ROOT, "results", "miracl", "baselines", f"{lang}.npz"))
    zd = np.load(os.path.join(ml_results(lang), "detect_feats.npz"))
    corpus = np.load(os.path.join(emb_dir(lang, args.name), "corpus_emb_fp16.npy"), mmap_mode="r")
    N = corpus.shape[0]
    assert int(zb["neg_rows"].max()) < N and int(zd["clean_rows"].max()) < N, \
        f"{lang}: the corpus has {N:,} rows but the benchmark refers to larger row ids; is corpus.parquet the same file?"
    enc = lambda xs: np.asarray(model.encode(xs, batch_size=args.batch, normalize_embeddings=True,
                                             convert_to_numpy=True, show_progress_bar=False)).astype(np.float16)
    rng = np.random.default_rng(args.seed)

    rand = zb["rand"]
    match = {}
    for v in VARIANTS:
        if f"match_{v}" in zb.files:
            match[(v, "bb")] = zb[f"match_{v}"]
        k = f"{v}_adv_match"
        if f"{v}_items" in zb.files and k in zd.files:
            match[(v, "adv")] = np.sort(rng.choice(zd[k], min(args.n_match, len(zd[k])), replace=False))
    clean_rows = np.unique(np.concatenate([zb["neg_rows"]] + list(match.values())))
    Fc = two_layer(corpus, np.asarray(corpus[clean_rows]), clean_rows)

    # Mahalanobis / Isolation Forest, fitted as in ml_baselines.py
    fit_rows = np.sort(rng.choice(N, min(50000, N), replace=False))
    X = np.asarray(corpus[fit_rows], np.float32)
    mu = X.mean(0); Xc = X - mu
    _, _, Vt = np.linalg.svd(Xc[:20000], full_matrices=False)
    W = Vt[:min(256, Vt.shape[0])].T
    Z = Xc @ W
    cov = np.cov(Z, rowvar=False)
    icov = np.linalg.inv(cov + 1e-3 * np.trace(cov) / cov.shape[0] * np.eye(cov.shape[0]))
    maha = lambda E: np.einsum("ij,jk,ik->i", (E - mu) @ W, icov, (E - mu) @ W)
    try:
        from sklearn.ensemble import IsolationForest
        iso = IsolationForest(n_estimators=200, random_state=args.seed).fit(Z[:, :64])
        iso_s = lambda E: -iso.score_samples(((E - mu) @ W)[:, :64])
    except ImportError:
        iso_s = None
        print("  sklearn not installed; Isolation Forest skipped", flush=True)

    Ec = np.asarray(corpus[clean_rows], np.float32)
    d = {"clean_rows": clean_rows, "rand": rand, "qids": np.array([it["qid"] for it in items]),
         "neg_knn10": -Fc["knn10"], "neg_rel_knn10": -Fc["rel_knn10"], "neg_lof_knn10": -Fc["lof_knn10"],
         "neg_maha": maha(Ec)}                                   # all scores: larger = more suspicious
    if iso_s:
        d["neg_iforest"] = iso_s(Ec)

    # queries of the attacked questions -> 5th best corpus score, for hit@5 with one injected poison
    Q = enc([args.query_prefix + it["question"] for it in items])
    S5 = topk(corpus, Q, 5)[0][:, 4]
    Q32 = Q.astype(np.float32)

    log = []
    for v in VARIANTS:
        if f"{v}_items" not in zb.files:
            continue
        idx = zb[f"{v}_items"]
        d[f"{v}_items"] = idx
        for f in FORMS:
            if (v, f) not in match:
                continue
            E = enc([args.doc_prefix + texts_of(items[j], v, f)[0] for j in idx])
            Fp = two_layer(corpus, E, np.full(len(E), -1))
            E32 = E.astype(np.float32)
            d[f"match_{v}_{f}"] = match[(v, f)]
            d[f"{v}_{f}_knn10"], d[f"{v}_{f}_rel_knn10"], d[f"{v}_{f}_lof_knn10"] = -Fp["knn10"], -Fp["rel_knn10"], -Fp["lof_knn10"]
            d[f"{v}_{f}_maha"] = maha(E32)
            if iso_s:
                d[f"{v}_{f}_iforest"] = iso_s(E32)
            d[f"{v}_{f}_hit"] = (Q32[idx] * E32).sum(1) > S5[idx]      # ties go to the corpus, as in ml_attack.merge_top5
            log.append(f"{v}/{f} n={len(idx)} hit@5={d[f'{v}_{f}_hit'].mean():.2f}")
    np.savez_compressed(outp, **d)
    print(f"[{lang}] corpus {N:,}; benign {len(clean_rows):,}; " + ", ".join(log)
          + f" (all questions, before the validity filter); {(time.time() - t0) / 60:.1f} min -> {outp}", flush=True)


# ---------------------------------------------------------------- stage 3: tables (CPU)
def summarize(args):
    R = os.path.join(ROOT, "results", "miracl")
    J = json.load(open(os.path.join(R, "review_judgments_native.json")))
    ref = {}
    p = os.path.join(R, "baselines", "summary.json")
    if os.path.exists(p):
        ref = {(r["lang"], r["variant"]): r for r in json.load(open(p))}
    rng = np.random.default_rng(args.seed)
    res = []
    for lang in args.lang:
        p = os.path.join(out_dir(args.name), f"{lang}.npz")
        if not os.path.exists(p):
            print(f"[{lang}] no scores, skipped")
            continue
        z = dict(np.load(p))
        rows, qids = z["clean_rows"], z["qids"]
        ri = np.searchsorted(rows, z["rand"])
        for v in VARIANTS:
            if f"{v}_items" not in z:
                continue
            idx = z[f"{v}_items"]
            keep = np.array([J.get(lang, {}).get(str(qids[j]), {}).get("label") != "bad" for j in idx])
            for f in FORMS:
                if f"match_{v}_{f}" not in z:
                    continue
                mi = np.searchsorted(rows, z[f"match_{v}_{f}"])
                hit = z[f"{v}_{f}_hit"][keep]
                row = {"lang": lang, "variant": v, "form": f, "n": int(keep.sum()), "hit": float(hit.mean())}
                for m, _ in METHODS:
                    if f"{v}_{f}_{m}" not in z:
                        continue
                    sp, sn = z[f"{v}_{f}_{m}"][keep].astype(float), z[f"neg_{m}"].astype(float)
                    thr5, thr1 = np.quantile(sn[ri], 0.95), np.quantile(sn[ri], 0.99)
                    bs = [auc(sp[rng.integers(0, len(sp), len(sp))], sn[mi]) for _ in range(args.boot)]
                    row[m] = {"auc": auc(sp, sn[mi]), "ci": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
                              "tpr5": float((sp > thr5).mean()), "tpr1": float((sp > thr1).mean()),
                              "eff": float((hit & ~(sp > thr5)).mean())}
                res.append(row)
    if not res:
        raise SystemExit("no scores found; run the score stage first")

    bb = [r for r in res if r["form"] == "bb"]
    adv = [r for r in res if r["form"] == "adv"]
    have = [(m, n) for m, n in METHODS if all(m in r for r in res)]
    mean = lambda rs, m, k: float(np.mean([r[m][k] for r in rs]))
    L = [f"# Second encoder: {args.name} (native-validated questions; same poisons and benign passages as the BGE-M3 benchmark)", ""]

    L += [f"## A. Mean over the {len(bb)} bb settings (Table 3)", "",
          f"| detector | AUROC {args.name} | AUROC BGE-M3 | TPR@5% {args.name} | TPR@5% BGE-M3 | TPR@1% {args.name} | TPR@1% BGE-M3 | Surv. {args.name} | Surv. BGE-M3 |",
          "|---|---|---|---|---|---|---|---|---|"]
    for m, n in have:
        rr = [ref[(r["lang"], r["variant"])] for r in bb if (r["lang"], r["variant"]) in ref and m in ref[(r["lang"], r["variant"])]]
        b = (lambda k: f"{np.mean([x[m][k] for x in rr]):.3f}") if len(rr) == len(bb) else (lambda k: "n/a")
        L.append(f"| {n} | {mean(bb, m, 'auc'):.3f} | {b('auc')} | {mean(bb, m, 'tpr5'):.3f} | {b('tpr5')} | "
                 f"{mean(bb, m, 'tpr1'):.3f} | {b('tpr1')} | {mean(bb, m, 'eff'):.3f} | {b('eff')} |")
    L.append("")

    for title, rs in [("B. Per setting, bb form: AUROC (95% CI) / TPR@5% / TPR@1%", bb),
                      ("C. Per setting, adv form (no question prefix)", adv)]:
        if not rs:
            continue
        L += [f"## {title}", "", "| lang | variant | n | hit@5 | " + " | ".join(n for _, n in have) + " | best |",
              "|---|---|---|---|" + "---|" * (len(have) + 1)]
        for r in rs:
            best = max(have, key=lambda mn: r[mn[0]]["auc"])[1]
            cells = [f"{r[m]['auc']:.3f} ({r[m]['ci'][0]:.2f}–{r[m]['ci'][1]:.2f}) / {r[m]['tpr5']:.2f} / {r[m]['tpr1']:.2f}" for m, _ in have]
            L.append(f"| {r['lang']} | {r['variant']} | {r['n']} | {r['hit']:.2f} | " + " | ".join(cells) + f" | {best} |")
        L.append("")

    L += ["## D. Do the paper's qualitative claims hold with this encoder?", ""]
    for form, rs in [("bb", bb), ("adv", adv)]:
        if not rs:
            continue
        nbest = sum(max(have, key=lambda mn: r[mn[0]]["auc"])[0] == "rel_knn10" for r in rs)
        gt = sum(r["rel_knn10"]["auc"] > r["knn10"]["auc"] for r in rs)
        gt5 = sum(r["rel_knn10"]["tpr5"] > r["knn10"]["tpr5"] for r in rs)
        eq5 = sum(r["rel_knn10"]["tpr5"] == r["knn10"]["tpr5"] for r in rs)
        L.append(f"- {form}: rel_knn10 has the best AUROC among the distance/density detectors in {nbest}/{len(rs)} settings; "
                 f"rel_knn10 > knn10 by AUROC in {gt}/{len(rs)}, by TPR@5% in {gt5}/{len(rs)} (ties {eq5}).")
        by = {(r["lang"], r["variant"]): r for r in rs}
        langs = [l for l in args.lang if (l, "trans") in by and (l, "en") in by]
        if langs:
            lower = [l for l in langs if by[(l, "trans")]["rel_knn10"]["auc"] < by[(l, "en")]["rel_knn10"]["auc"]]
            L.append(f"- {form}: translated poison is harder to detect than English poison (rel_knn10 AUROC, unpaired, all valid questions of each variant) "
                     f"in {len(lower)}/{len(langs)} languages" + (f" ({', '.join(lower)})." if lower else "."))
    L += ["", "Notes. Thresholds are the 95th / 99th percentile of the 2,000 random benign passages under this encoder. "
          "hit@5 is recomputed with this encoder (one poison injected per question). "
          "The BGE-M3 columns are read from results/miracl/baselines/summary.json. "
          "Section D compares variants on all valid questions of each variant, not on the shared questions of Table 2."]
    od = out_dir(args.name)
    open(os.path.join(od, "summary.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    json.dump(res, open(os.path.join(od, "summary.json"), "w"), indent=1, ensure_ascii=False)
    print("\n".join(L)); print(f"\nsaved {od}/summary.md")


def main():
    global SELFTEST
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=os.path.join(os.environ.get("HF_MODELS", os.path.join(ROOT, "models")), "multilingual-e5-large"),
                    help="local path or hub name of a sentence-transformers model")
    ap.add_argument("--name", default="me5-large", help="short tag used in output folders")
    ap.add_argument("--doc_prefix", default="passage: ")
    ap.add_argument("--query_prefix", default="query: ")
    ap.add_argument("--lang", nargs="+", default=LANGS)
    ap.add_argument("--stage", default="all", choices=["all", "embed", "score", "summary"])
    ap.add_argument("--batch", type=int, default=256)
    ap.add_argument("--chunk", type=int, default=50_000)
    ap.add_argument("--max_len", type=int, default=512)
    ap.add_argument("--n_match", type=int, default=1000)
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--redo", action="store_true")
    ap.add_argument("--selftest", action="store_true", help="no model / GPU: random vectors, only checks that the code runs")
    args = ap.parse_args()
    SELFTEST = args.selftest
    if SELFTEST:
        args.name = "selftest"
    if args.stage in ("all", "embed", "score"):
        model = load_encoder(args)
        for lang in args.lang:
            if args.stage in ("all", "embed"):
                embed_lang(model, lang, args)
            if args.stage in ("all", "score"):
                score_lang(model, lang, args)
    if args.stage in ("all", "summary"):
        summarize(args)


if __name__ == "__main__":
    main()
