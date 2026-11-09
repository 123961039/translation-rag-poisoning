"""
Baseline retrieval evaluation on MIRACL dev (bge-m3 dense, exact inner product on GPU).
    python ml_eval_retrieval.py
    python ml_eval_retrieval.py --langs id --subsample 131924   # downsample the high-resource corpus to the sw size
--subsample: keep n random passages + all dev gold passages (the same scheme as the later scale experiments).
Output: results/miracl/<lang>/retrieval[_sub<n>].json and a summary table in the terminal (with reference values from the paper).
"""
import argparse, json, math, os, time

import numpy as np

from ml_common import (LANGS, REF_NDCG10, gpu_topk, load_corpus_emb, load_qrels, load_query_emb,
                       ml_results)


def ndcg_at(ranked, rel, k):
    dcg = sum(rel.get(d, 0) / math.log2(i + 2) for i, d in enumerate(ranked[:k]))
    ideal = sorted(rel.values(), reverse=True)[:k]
    idcg = sum(r / math.log2(i + 2) for i, r in enumerate(ideal))
    return dcg / idcg if idcg else 0.0


def subsample_rows(N, n, must, seed):
    rng = np.random.default_rng(seed)
    keep = np.zeros(N, bool)
    keep[rng.choice(N, size=min(n, N), replace=False)] = True
    keep[must] = True
    return np.flatnonzero(keep)


def run(lang, args):
    corpus, cids = load_corpus_emb(lang)
    N = corpus.shape[0]
    qrels = load_qrels(lang, "dev")
    qemb, qid2row = load_query_emb(lang)
    qids = [q for q in qrels if q in qid2row]
    cid2row = {c: i for i, c in enumerate(cids)}
    missing = sum(d not in cid2row for q in qids for d in qrels[q])
    rows = np.arange(N)
    if args.subsample:
        gold = np.array(sorted({cid2row[d] for q in qids for d in qrels[q] if d in cid2row}))
        rows = subsample_rows(N, args.subsample, gold, args.seed)
        blocks = [np.asarray(corpus[rows])]
    else:
        blocks = [corpus]
    t0 = time.time()
    S, I = gpu_topk(blocks, qemb[[qid2row[q] for q in qids]], 100)
    dt = time.time() - t0
    m = {"nDCG@10": [], "R@5": [], "R@20": [], "R@100": []}
    for qi, q in enumerate(qids):
        ranked = [cids[rows[j]] for j in I[qi]]
        rel = qrels[q]
        m["nDCG@10"].append(ndcg_at(ranked, rel, 10))
        for k in (5, 20, 100):
            m[f"R@{k}"].append(len(set(ranked[:k]) & set(rel)) / len(rel))
    out = {k: float(np.mean(v)) for k, v in m.items()}
    out.update({"lang": lang, "n_queries": len(qids), "corpus_size": int(len(rows)), "full_corpus": int(N),
                "gold_missing_in_corpus": int(missing), "ms_per_query": dt / len(qids) * 1000,
                "ref_nDCG@10": REF_NDCG10.get(lang)})
    tag = f"_sub{args.subsample}" if args.subsample else ""
    json.dump(out, open(os.path.join(ml_results(lang), f"retrieval{tag}.json"), "w"), indent=2)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--langs", nargs="+", default=LANGS)
    ap.add_argument("--subsample", type=int, default=0)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    res = [run(l, args) for l in args.langs]
    print(f"\n{'lang':4s} {'corpus':>10s} {'queries':>5s} {'nDCG@10':>8s} {'paper':>8s} {'R@5':>6s} {'R@20':>6s} {'R@100':>6s} {'missing gold':>8s}")
    for r in res:
        ref = f"{r['ref_nDCG@10'] / 100:.3f}" if r["ref_nDCG@10"] else "-"
        print(f"{r['lang']:4s} {r['corpus_size']:>10,} {r['n_queries']:>5d} {r['nDCG@10']:8.3f} {ref:>8s} "
              f"{r['R@5']:6.3f} {r['R@20']:6.3f} {r['R@100']:6.3f} {r['gold_missing_in_corpus']:>8d}")
    print("(reference values are approximate and the paper removes passages with the query's id; differences within 0.03 are normal)")


if __name__ == "__main__":
    main()
