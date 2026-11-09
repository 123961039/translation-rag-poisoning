"""
Defense baselines (GPU). Compared with our neighbourhood isolation features on
the same poisons, the same benign passages and the same thresholding (statistics in ml_baselines_summary.py, CPU only).
Baselines
  ppl        perplexity (the ingestion defense evaluated by PoisonedRAG). Qwen3-14B-AWQ scores every token; mean negative log-likelihood.
             No direction is assumed: generated poison often has lower perplexity, so both "low perplexity suspicious" and "high perplexity suspicious" are reported
  judge      LLM judgment: Qwen3-14B reads the passage and answers whether it contains a factual error (Yes/No); P(Yes) is the suspicion score
  maha       Mahalanobis distance: PCA-256 + shrinkage covariance on 50k random corpus vectors; farther = more suspicious
  iforest    Isolation Forest (PCA-64, sklearn; skipped if sklearn is missing)
  The existing knn10 / rel_knn10 / lof_knn10 scores on the same samples are stored as well, for comparability
Samples (per language and poison variant, form bb)
  poisons: the first one per question (as in ml_detect); benign: --n_rand random benign passages from detect_feats.npz
  (for the 5% FPR threshold) and --n_match length-matched benign passages (for AUROC). LLM scoring is expensive, so subsets are used
    export VLLM_CACHE_ROOT=~/.cache/vllm TORCHINDUCTOR_CACHE_DIR=~/.cache/inductor
    python ml_baselines.py
Output: results/miracl/baselines/<lang>.npz (per-item scores), then python ml_baselines_summary.py
"""
import argparse, json, os, time

from vllm import LLM, SamplingParams          # import before torch (as in ml_asr.py)

import numpy as np
import pyarrow.parquet as pq

from ml_common import HF, LANGS, M3_PATH, ROOT, corpus_parquet, doc_format, load_corpus_emb, ml_results
from ml_attack import load_items, texts_of

READER = os.path.join(HF, "Qwen3-14B-AWQ")
VARIANTS = ["native", "trans", "en"]
JUDGE = ("Read the following passage carefully.\n\nPassage:\n{p}\n\n"
         "Does this passage state any factually incorrect information (for example a wrong date, number, "
         "name or place)? Answer with exactly one word: Yes or No.")


def fmt_t(s):
    s = int(s)
    return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}" if s >= 3600 else f"{s // 60}:{s % 60:02d}"


def lp_of(x):
    return x.logprob if hasattr(x, "logprob") else float(x)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", nargs="+", default=LANGS)
    ap.add_argument("--n_rand", type=int, default=2000)
    ap.add_argument("--n_match", type=int, default=1000)
    ap.add_argument("--max_tok", type=int, default=1500, help="maximum tokens kept per passage (te passages are long)")
    ap.add_argument("--gpu_margin", type=float, default=1.0)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    outd = os.path.join(ROOT, "results", "miracl", "baselines")
    os.makedirs(outd, exist_ok=True)
    rng = np.random.default_rng(args.seed)
    T0 = time.time()

    # ---------- stage 1: sampling, encoding, vector baselines (no LLM) ----------
    from sentence_transformers import SentenceTransformer
    import torch
    enc_m = SentenceTransformer(M3_PATH, device="cuda").half()
    enc_m.max_seq_length = 512
    enc = lambda xs: enc_m.encode(xs, batch_size=128, normalize_embeddings=True,
                                  convert_to_numpy=True, show_progress_bar=False).astype(np.float32)
    try:
        from sklearn.ensemble import IsolationForest
    except ImportError:
        IsolationForest = None
        print("sklearn not installed; skipping Isolation Forest", flush=True)

    data = {}
    for lang in args.lang:
        t0 = time.time()
        items, _ = load_items(lang)
        z = np.load(os.path.join(ml_results(lang), "detect_feats.npz"))
        corpus, _ = load_corpus_emb(lang)
        N = corpus.shape[0]
        cpos = {r: i for i, r in enumerate(z["clean_rows"])}
        rand = np.sort(rng.choice(z["rand"], min(args.n_rand, len(z["rand"])), replace=False))
        match = {v: np.sort(rng.choice(z[f"{v}_bb_match"], min(args.n_match, len(z[f"{v}_bb_match"])), replace=False))
                 for v in VARIANTS if f"{v}_bb_match" in z}
        neg_rows = np.unique(np.concatenate([rand] + list(match.values())))
        tb = pq.read_table(corpus_parquet(lang), columns=["title", "text"])
        titles, texts = tb.column(0), tb.column(1)
        neg_txt = [doc_format((titles[int(r)].as_py() or "").strip(), (texts[int(r)].as_py() or "").strip()) for r in neg_rows]
        del tb, titles, texts
        pois = {}
        for v in VARIANTS:
            idx = np.array([j for j, it in enumerate(items) if it.get(f"{v}_adv")])
            if len(idx) and f"{v}_bb_match" in z:
                pois[v] = {"items": idx, "txt": [texts_of(items[j], v, "bb")[0] for j in idx]}

        # vector baselines: fitted on 50k random corpus passages
        fit_rows = np.sort(rng.choice(N, min(50000, N), replace=False))
        X = np.asarray(corpus[fit_rows], np.float32)
        mu = X.mean(0); Xc = X - mu
        _, _, Vt = np.linalg.svd(Xc[:20000], full_matrices=False)
        W = Vt[:256].T
        Z = Xc @ W
        cov = np.cov(Z, rowvar=False)
        lam = 1e-3 * np.trace(cov) / cov.shape[0]
        icov = np.linalg.inv(cov + lam * np.eye(cov.shape[0]))
        maha = lambda E: np.einsum("ij,jk,ik->i", (E - mu) @ W, icov, (E - mu) @ W)
        iso = None
        if IsolationForest is not None:
            iso = IsolationForest(n_estimators=200, random_state=args.seed).fit(Z[:, :64])
        iso_s = (lambda E: -iso.score_samples(((E - mu) @ W)[:, :64])) if iso is not None else None

        Eneg = np.asarray(corpus[neg_rows], np.float32)
        d = {"neg_rows": neg_rows, "rand": rand, "neg_maha": maha(Eneg)}
        if iso_s:
            d["neg_iforest"] = iso_s(Eneg)
        for k in ("knn10", "rel_knn10", "lof_knn10"):
            d[f"neg_{k}"] = -z[f"clean_{k}"][[cpos[r] for r in neg_rows]]          # negated: larger = more suspicious
        for v, m in match.items():
            d[f"match_{v}"] = m
        for v, p in pois.items():
            E = enc(p["txt"])
            d[f"{v}_items"] = p["items"]
            d[f"{v}_maha"] = maha(E)
            if iso_s:
                d[f"{v}_iforest"] = iso_s(E)
            for k in ("knn10", "rel_knn10", "lof_knn10"):
                d[f"{v}_{k}"] = -z[f"{v}_bb_{k}"]
        data[lang] = {"d": d, "neg_txt": neg_txt, "pois": pois}
        print(f"[{lang}] benign {len(neg_rows):,} (random {len(rand):,} + length-matched), poisons "
              + ", ".join(f"{v} {len(p['txt'])}" for v, p in pois.items())
              + f"; vector baselines done, {fmt_t(time.time() - t0)}", flush=True)
    del enc_m
    torch.cuda.empty_cache()

    # ---------- stage 2: LLM baselines (perplexity + judgment) ----------
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(READER)
    def clip(t):
        ids = tok(t, add_special_tokens=False).input_ids
        return t if len(ids) <= args.max_tok else tok.decode(ids[:args.max_tok])
    jobs = []                                   # (lang, 'neg'|variant, index, text)
    for lang, D in data.items():
        jobs += [(lang, "neg", i, clip(t)) for i, t in enumerate(D["neg_txt"])]
        for v, p in D["pois"].items():
            jobs += [(lang, v, i, clip(t)) for i, t in enumerate(p["txt"])]
    max_len = max(len(tok(t, add_special_tokens=False).input_ids) for *_, t in jobs) + 200
    free_b, total_b = torch.cuda.mem_get_info()
    util = (free_b - args.gpu_margin * 2**30) / total_b
    print(f"\nLLM scoring: {len(jobs):,} passages x 2 (perplexity + judgment), max_model_len={max_len}, "
          f"gpu_memory_utilization={util:.2f}", flush=True)
    llm = LLM(model=READER, gpu_memory_utilization=util, max_model_len=max_len, seed=args.seed,
              enable_prefix_caching=True)

    # perplexity: prompt_logprobs, mean negative log-likelihood per token
    t1 = time.time()
    outs = llm.generate([t for *_, t in jobs], SamplingParams(max_tokens=1, prompt_logprobs=0, temperature=0.0))
    nll = []
    for o in outs:
        ids, pl = o.prompt_token_ids, o.prompt_logprobs
        vals = [-lp_of(pl[i][ids[i]]) for i in range(1, len(ids)) if pl[i] is not None and ids[i] in pl[i]]
        nll.append(float(np.mean(vals)) if vals else np.nan)
    print(f"  perplexity done, {fmt_t(time.time() - t1)} (elapsed {fmt_t(time.time() - T0)})", flush=True)

    # judgment: probability of Yes / No as the first output token
    t1 = time.time()
    convs = [[{"role": "user", "content": JUDGE.format(p=t)}] for *_, t in jobs]
    sp = SamplingParams(max_tokens=1, logprobs=20, temperature=0.0)
    try:
        outs = llm.chat(convs, sp, chat_template_kwargs={"enable_thinking": False})
    except TypeError:
        outs = llm.chat(convs, sp)
    pyes, n_none = [], 0
    for o in outs:
        top = o.outputs[0].logprobs[0] if o.outputs[0].logprobs else {}
        y = n = 0.0
        for tid, x in top.items():
            w = (getattr(x, "decoded_token", None) or tok.decode([tid])).strip().lower()
            if w == "yes":
                y += np.exp(lp_of(x))
            elif w == "no":
                n += np.exp(lp_of(x))
        if y + n == 0:
            n_none += 1
        pyes.append(y / (y + n) if y + n > 0 else 0.5)
    print(f"  judgment done, {fmt_t(time.time() - t1)}; {n_none} items without Yes/No among the top-20 candidates (set to 0.5)", flush=True)

    # ---------- save ----------
    for lang, D in data.items():
        d = D["d"]
        sel = lambda g: [k for k, j in enumerate(jobs) if j[0] == lang and j[1] == g]
        for g in ["neg"] + list(D["pois"]):
            ks = sel(g)
            d[f"{g}_ppl_low"] = -np.array([nll[k] for k in ks])        # low perplexity suspicious
            d[f"{g}_ppl_high"] = np.array([nll[k] for k in ks])        # high perplexity suspicious
            d[f"{g}_judge"] = np.array([pyes[k] for k in ks])
        d["qids"] = np.array([it["qid"] for it in load_items(lang)[0]])
        np.savez_compressed(os.path.join(outd, f"{lang}.npz"), **d)
    print(f"\nall done, total time {fmt_t(time.time() - T0)}. Next (CPU is enough): python ml_baselines_summary.py")


if __name__ == "__main__":
    main()
