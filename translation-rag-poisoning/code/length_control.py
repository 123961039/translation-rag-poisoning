"""
Length control: is the "poison text is more isolated" signal (single view) merely due to poison texts being shorter?

Three modes (the CPU-only instance has about 0.5 cores / 2 GB RAM; defaults are set for that configuration):
  1) lengths only (CPU, a few minutes)
       python length_control.py --mode lengths
     count corpus words and cache them, draw length-matched samples, compute the "length only" AUROC
  2) CPU neighbour features on a small sample (run per dataset; the remaining time is printed after the first 5%)
       nohup python length_control.py --device cpu --dataset nq > lc_cpu_nq.log 2>&1 &
     defaults: 2000 length-matched, 1000 random (subsampled from the 20k of the earlier experiment), all gold, all poisons
     if the process is killed by the system (log shows only "Killed"), add --mem_mb 100
  3) GPU, full size (about 10 minutes for three datasets)
       python length_control.py
     20k length-matched and 20k random; the random / gold columns reproduce features_bb.json exactly

Method
  - corpus word count = len(doc_format(title, text).split()), consistent with the embedding format and aligned with embedding rows,
    cached at emb/<ds>/<model>/corpus_len_words.npy
  - length-matched benign passages (no gold) are stratified by the poison word-count distribution (5-word buckets by default)
  - neighbours are searched in the original corpus only (single view), self removed; nn1 / knn10 / dup computed
  - AUROC oriented as "more isolated = more suspicious" (score = -feature), with bootstrap 95% CI;
    "length only" (score = -word count) is given as a reference
Output: results/<ds>/length_control_<variant>[_cpu|_lengths].json and a summary md under results/
"""
import argparse, json, math, os, time

import numpy as np
import pyarrow.parquet as pq
from sklearn.metrics import roc_auc_score

from common import EMB_MODEL, ROOT, corpus_parquet, doc_format, emb_dir, results_dir

FEATS = ["nn1", "knn10", "dup"]
NEGS = ["clean-random", "clean-lenmatch", "clean-gold"]
OLD_N_CLEAN = 20000   # number of random benign passages in the earlier English experiment


# ---------------------------------------------------------------- corpus
def corpus_emb(ds):
    """mmap the vectors only, without loading the id list (the MS MARCO id list alone takes about 1 GB)"""
    return np.load(os.path.join(emb_dir(ds), "corpus_emb_fp16.npy"), mmap_mode="r")


def gold_rows(ds, gold_ids, N):
    """Scan corpus_ids.txt line by line to find gold row indices and check the row count"""
    want, rows, n = set(gold_ids), [], 0
    with open(os.path.join(emb_dir(ds), "corpus_ids.txt")) as f:
        for i, line in enumerate(f):
            n += 1
            if line.rstrip("\n") in want:
                rows.append(i)
    assert n == N, f"{n} ids but {N} vectors"
    return np.array(sorted(rows), dtype=np.int64)


def n_words(title, text):
    return len(doc_format((title or "").strip(), (text or "").strip()).split())


def corpus_lengths(ds, N):
    path = os.path.join(emb_dir(ds), "corpus_len_words.npy")
    if os.path.exists(path):
        L = np.load(path)
        assert L.shape[0] == N, f"cached word-count array has length {L.shape[0]} != corpus size {N}; delete {path} and recompute"
        return L
    t0 = time.time()
    pf = pq.ParquetFile(corpus_parquet(ds))
    cols = [c for c in ("title", "text") if c in pf.schema_arrow.names]
    L = np.empty(N, dtype=np.int32)
    pos = 0
    # same traversal order as the corpus embedding step -> aligned with embedding rows
    for b in pf.iter_batches(batch_size=50_000, columns=cols):
        d = b.to_pydict()
        n = b.num_rows
        titles = d.get("title", [None] * n)
        L[pos:pos + n] = [n_words(t, x) for t, x in zip(titles, d["text"])]
        pos += n
        if pos // 1_000_000 != (pos - n) // 1_000_000:
            print(f"    word counts {pos:,}/{N:,}  {time.time() - t0:.0f} s", flush=True)
    assert pos == N, f"parquet rows {pos} != embedding rows {N}"
    np.save(path, L)
    print(f"  corpus word counts done: {N:,} passages, {time.time() - t0:.0f} s, cached at {path}")
    return L


# ---------------------------------------------------------------- sampling
def lenmatch_sample(L, pois_len, n_target, width, exclude, rng):
    """Stratified sampling by the poison length-bucket proportions; if a bucket is too small, take all of it and record it"""
    pb = pois_len // width
    cb = L // width
    bins, cnt = np.unique(pb, return_counts=True)
    want = np.round(n_target * cnt / cnt.sum()).astype(int)
    excl = np.zeros(L.shape[0], bool)
    excl[exclude] = True
    picks, report = [], []
    for b, c, w in zip(bins, cnt, want):
        pool = np.flatnonzero((cb == b) & ~excl)
        take = min(w, len(pool))
        if take:
            picks.append(rng.choice(pool, size=take, replace=False))
        report.append({"bucket": f"{b * width}-{b * width + width - 1}", "n_poison": int(c),
                       "want": int(w), "got": int(take), "pool": int(len(pool))})
    idx = np.sort(np.concatenate(picks)) if picks else np.empty(0, dtype=np.int64)
    return idx, report


def make_groups(ds, items, pois_len, N, L, args):
    # random benign: first draw 20k as in the earlier experiment (same seed, same call), then subsample if fewer are needed
    rng = np.random.default_rng(args.seed)
    clean20k = np.sort(rng.choice(N, size=min(OLD_N_CLEAN, N), replace=False))
    if args.n_clean < len(clean20k):
        clean_idx = np.sort(np.random.default_rng(args.seed + 3).choice(clean20k, args.n_clean, replace=False))
    else:
        clean_idx = clean20k
    gold_idx = gold_rows(ds, [d for it in items for d in it["gold_ids"]], N)
    match_idx, buckets = lenmatch_sample(L, pois_len, args.n_match, args.width, gold_idx,
                                         np.random.default_rng(args.seed + 1))
    short = [b for b in buckets if b["got"] < b["want"]]
    if short:
        print("  Warning: these length buckets were too small and were taken entirely:", short)
    return {"clean-random": clean_idx, "clean-lenmatch": match_idx, "clean-gold": gold_idx}, buckets


# ---------------------------------------------------------------- neighbours
def strip_self(S, I, self_idx, K):   # same as in the earlier experiment (re-implemented here to avoid importing sentence_transformers)
    keep = I != self_idx[:, None]
    order = np.argsort(~keep, axis=1, kind="stable")[:, :K]
    return np.take_along_axis(S, order, 1)


def feats(S, tau):
    return {"nn1": S[:, 0], "knn10": S[:, :10].mean(1), "dup": (S > tau).sum(1).astype(float)}


def cgroup_cpus():
    """CPU quota of the container (about 0.5 cores on a CPU-only instance); os.cpu_count() reports host cores"""
    try:
        q, p = open("/sys/fs/cgroup/cpu.max").read().split()[:2]
        if q != "max":
            return max(1, math.ceil(int(q) / int(p)))
    except Exception:
        pass
    try:
        q = int(open("/sys/fs/cgroup/cpu/cpu.cfs_quota_us").read())
        p = int(open("/sys/fs/cgroup/cpu/cpu.cfs_period_us").read())
        if q > 0:
            return max(1, math.ceil(q / p))
    except Exception:
        pass
    return os.cpu_count() or 1


def cpu_topk(corpus, queries, k, mem_mb=200):
    """Exact inner-product top-k on CPU: fp32, corpus read in chunks, score matrix kept around mem_mb"""
    import torch
    q = torch.from_numpy(np.ascontiguousarray(queries, dtype=np.float32))
    m, N = q.shape[0], corpus.shape[0]
    chunk = max(2048, int(mem_mb * 2**20 / 4 / m))
    best_s = torch.full((m, k), -1e4)
    best_i = torch.full((m, k), -1, dtype=torch.int64)
    t0, nxt = time.time(), 0.05
    for s in range(0, N, chunk):
        c = torch.from_numpy(np.asarray(corpus[s:s + chunk], dtype=np.float32))
        ts, ti = (q @ c.T).topk(min(k, c.shape[0]), dim=1)
        cs = torch.cat([best_s, ts], 1)
        ci = torch.cat([best_i, ti + s], 1)
        best_s, bi = cs.topk(k, dim=1)
        best_i = ci.gather(1, bi)
        done = min(s + chunk, N) / N
        if done >= nxt or done == 1:
            el = time.time() - t0
            print(f"    neighbour search {done:5.1%}  elapsed {el / 60:.1f} min  remaining {el / done * (1 - done) / 60:.1f} min",
                  flush=True)
            nxt += 0.05
    return best_s.numpy(), best_i.numpy()


def encode_poison(texts, device):
    import torch
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(EMB_MODEL, device=device)
    if device == "cuda":
        model = model.half()   # as in the earlier experiment; fp32 on CPU, the difference is negligible
    P = model.encode(texts, batch_size=64 if device == "cpu" else 256,
                     normalize_embeddings=True, convert_to_numpy=True).astype(np.float16)
    del model
    if device == "cuda":
        torch.cuda.empty_cache()
    return P


# ---------------------------------------------------------------- AUROC
def auc_ci(pos, neg, n_boot, rng):
    """pos/neg are suspicion scores (larger = more suspicious); returns AUROC and stratified bootstrap 95% CI"""
    y = np.r_[np.ones(len(pos)), np.zeros(len(neg))]
    auc = float(roc_auc_score(y, np.r_[pos, neg]))
    if not n_boot:
        return auc, None
    bs = []
    for _ in range(n_boot):
        p = pos[rng.integers(0, len(pos), len(pos))]
        n = neg[rng.integers(0, len(neg), len(neg))]
        bs.append(roc_auc_score(y, np.r_[p, n]))
    return auc, [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]


def score_rows(values, label, n_boot, rng):
    """values: {feature name: array}; label: 0/1/2 = NEGS, 3 = poison"""
    rows = {}
    for fn, v in values.items():
        v = np.asarray(v, float)
        susp = -v                                   # more isolated / shorter -> more suspicious
        row = {"mean": {g: float(v[label == gi].mean()) for gi, g in enumerate(NEGS + ["poison"])}}
        for gi, g in enumerate(NEGS):
            a, ci = auc_ci(susp[label == 3], susp[label == gi], n_boot, rng)
            row[f"AUROC_vs_{g}"] = a
            row[f"CI_vs_{g}"] = ci
        rows[fn] = row
    return rows


def verdict(a):
    if a < 0.55:
        return "below 0.55: the signal comes mainly from length"
    if a >= 0.7:
        return ">= 0.7: the signal holds after controlling for length"
    return "between 0.55 and 0.7: the signal is weakened by length; inspect further"


def print_table(rows):
    print(f"  {'feature':12s} {'vs random':>16s} {'vs length-matched':>18s} {'vs gold':>16s}")
    for fn, r in rows.items():
        cells = []
        for g in NEGS:
            ci = r[f"CI_vs_{g}"]
            cells.append(f"{r[f'AUROC_vs_{g}']:.3f}" + (f" [{ci[0]:.2f},{ci[1]:.2f}]" if ci else ""))
        print(f"  {fn:12s} {cells[0]:>16s} {cells[1]:>18s} {cells[2]:>16s}")


# ---------------------------------------------------------------- main
def run(ds, args):
    print(f"\n================ {ds} ================", flush=True)
    rd = results_dir(ds)
    items = [json.loads(l) for l in open(os.path.join(rd, "poison.jsonl"))]
    key = "poison_texts" if args.variant == "bb" else "adv_texts"
    texts = [t for it in items for t in it[key]]
    pois_len = np.array([len(t.split()) for t in texts])

    corpus = corpus_emb(ds)
    N = corpus.shape[0]
    L = corpus_lengths(ds, N)
    groups, buckets = make_groups(ds, items, pois_len, N, L, args)
    print(f"  poisons {len(texts)} | " + " | ".join(f"{g} {len(v)}" for g, v in groups.items()), flush=True)

    label = np.concatenate([np.full(len(g), i) for i, g in enumerate(groups.values())] + [np.full(len(texts), 3)])
    lens = np.concatenate([L[g] for g in groups.values()] + [pois_len]).astype(float)
    out = {"mode": args.mode, "device": args.device,
           "n": {k: int(len(v)) for k, v in groups.items()} | {"poison": len(texts)},
           "len_mean": {g: float(lens[label == gi].mean()) for gi, g in enumerate(NEGS + ["poison"])},
           "len_median": {g: float(np.median(lens[label == gi])) for gi, g in enumerate(NEGS + ["poison"])},
           "buckets": buckets}
    brng = np.random.default_rng(args.seed + 2)
    vals = {"length_only": lens}

    if args.mode == "full":
        P = encode_poison(texts, args.device)
        import gc; gc.collect()
        cand = np.concatenate([corpus[g] for g in groups.values()] + [P])
        self_idx = np.concatenate(list(groups.values()) + [np.full(len(P), -1)])  # poisons are not in the corpus
        t0 = time.time()
        if args.device == "cpu":
            S, I = cpu_topk(corpus, cand, args.K + 1, mem_mb=args.mem_mb)
        else:
            from common import gpu_topk
            S, I = gpu_topk([corpus], cand, args.K + 1, device=args.device)
        print(f"  neighbour search {len(cand):,} x {N:,}, {(time.time() - t0) / 60:.1f} min", flush=True)
        vals |= feats(strip_self(S, I, self_idx, args.K), args.tau)

    out["features"] = score_rows(vals, label, args.boot, brng)

    if args.mode == "full":
        # check against earlier results (old table uses the raw direction, here 1 - value). The full random group should match exactly; subsamples only approximately
        old_p = os.path.join(rd, f"features_{args.variant}.json")
        if os.path.exists(old_p):
            old = json.load(open(old_p))
            tol = 0.01 if args.n_clean >= OLD_N_CLEAN else 0.04
            diffs = {}
            for f in FEATS:
                for g in ("clean-random", "clean-gold"):
                    o = old.get(f"single/{f}", {}).get(f"AUROC_vs_{g}")
                    if o is not None:
                        diffs[f"{f}/{g}"] = abs((1 - o) - out["features"][f][f"AUROC_vs_{g}"])
            if diffs:
                out["max_diff_vs_old"] = float(max(diffs.values()))
                flag = "OK" if out["max_diff_vs_old"] < tol else "WARNING: differs from earlier results, investigate"
                print(f"  check against features_{args.variant}.json: max difference {out['max_diff_vs_old']:.4f}"
                      f" (tolerance {tol}) {flag}")
        best = max(FEATS, key=lambda f: out["features"][f]["AUROC_vs_clean-lenmatch"])
        out["best_lenmatch"] = {"feature": best, "AUROC": out["features"][best]["AUROC_vs_clean-lenmatch"]}

    print("  mean word count: " + "  ".join(f"{g} {out['len_mean'][g]:.1f}" for g in NEGS + ["poison"]))
    print_table(out["features"])
    if "best_lenmatch" in out:
        b = out["best_lenmatch"]
        print(f"  best on length-matched: {b['feature']} = {b['AUROC']:.3f} -> {verdict(b['AUROC'])}")

    json.dump(out, open(os.path.join(rd, f"length_control_{args.variant}{args.tag}.json"), "w"),
              indent=2, ensure_ascii=False)
    return out


def write_summary(res, args):
    what = "length only" if args.mode == "lengths" else f"single-view neighbour features ({args.device})"
    lines = [f"# Length control: {what}, {args.variant}, direction: more isolated / shorter = more suspicious", "",
             f"Length-matched: {args.n_match} passages stratified in {args.width}-word buckets of poison length (no gold); "
             f"{args.n_clean} random benign passages; CIs are {args.boot}-sample bootstrap 95% intervals.", "",
             "| dataset | mean words random / matched / gold / poison | feature | vs random | vs length-matched | vs gold |",
             "|---|---|---|---|---|---|"]
    for ds, o in res.items():
        lm = " / ".join(f"{o['len_mean'][g]:.1f}" for g in NEGS + ["poison"])
        for j, (fn, r) in enumerate(o["features"].items()):
            cell = lambda g: f"{r[f'AUROC_vs_{g}']:.3f}" + (
                f" ({r[f'CI_vs_{g}'][0]:.2f}–{r[f'CI_vs_{g}'][1]:.2f})" if r[f"CI_vs_{g}"] else "")
            lines.append(f"| {ds if j == 0 else ''} | {lm if j == 0 else ''} | {fn} | "
                         f"{cell('clean-random')} | {cell('clean-lenmatch')} | {cell('clean-gold')} |")
    if args.mode == "full":
        lines += ["", "Verdict (best feature on the length-matched column; note the optimistic bias of taking the best):"]
        for ds, o in res.items():
            b = o["best_lenmatch"]
            lines.append(f"- {ds}: {b['feature']} = {b['AUROC']:.3f}, {verdict(b['AUROC'])}")
    p = os.path.join(ROOT, "results", f"length_control_summary_{args.variant}{args.tag}_{'-'.join(res)}.md")
    open(p, "w").write("\n".join(lines) + "\n")
    print("\n" + "\n".join(lines) + f"\n\nsummary saved: {p}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="full", choices=["full", "lengths"],
                    help="lengths = only count lengths and compute the AUROC of length itself, no model, no neighbour search")
    ap.add_argument("--dataset", nargs="+", default=["nq", "hotpotqa", "msmarco"],
                    choices=["nq", "hotpotqa", "msmarco"])
    ap.add_argument("--variant", default="bb", choices=["bb", "adv"])
    ap.add_argument("--device", default="cuda", choices=["cuda", "cpu"])
    ap.add_argument("--n_clean", type=int, default=None,
                    help="number of random benign passages (subsampled from the earlier 20k); default GPU 20000 / CPU 1000")
    ap.add_argument("--n_match", type=int, default=None, help="number of length-matched passages; default GPU 20000 / CPU 2000")
    ap.add_argument("--width", type=int, default=5, help="length bucket width (words)")
    ap.add_argument("--K", type=int, default=50)
    ap.add_argument("--tau", type=float, default=0.9)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--boot", type=int, default=1000, help="bootstrap samples, 0 = no CI")
    ap.add_argument("--mem_mb", type=int, default=200, help="memory limit of the score matrix in CPU mode (MB)")
    ap.add_argument("--threads", type=int, default=0, help="CPU threads, 0 = container quota")
    args = ap.parse_args()

    args.n_clean = args.n_clean or (1000 if args.device == "cpu" else OLD_N_CLEAN)
    args.n_match = args.n_match or (2000 if args.device == "cpu" else 20000)
    args.tag = "_lengths" if args.mode == "lengths" else ("_cpu" if args.device == "cpu" else "")
    if args.mode == "full" and args.device == "cpu":
        import torch
        torch.set_num_threads(args.threads or cgroup_cpus())
        print(f"CPU mode: {torch.get_num_threads()} threads, random {args.n_clean} / length-matched {args.n_match}")
    res = {ds: run(ds, args) for ds in args.dataset}
    write_summary(res, args)


if __name__ == "__main__":
    main()