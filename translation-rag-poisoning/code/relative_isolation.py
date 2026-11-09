"""
Relative isolation: after length control, absolute isolation (nn1/knn10) in the single view holds up only on HotpotQA.
This tests whether "relative isolation" recovers the signal under length matching -- compare a text's isolation with that of its neighbours,
removing the effect of topic density (some topics are sparse to begin with), in the spirit of the local outlier factor (LOF).
    python relative_isolation.py                    # three datasets, bb version
    python relative_isolation.py --variant adv      # poison texts without the question prefix
Samples are identical to length_control.py (same seed), so the tables can be compared directly.

Features (all "smaller = more isolated"; AUROC uses the negated value, same direction as length_control)
  nn1, knn10            absolute isolation (reproduces length_control, as a check)
  rel_nn1, rel_knn10    own value - mean of the same feature over the first M neighbours
  lof_knn10             LOF-style ratio: mean distance of the neighbours / own distance, distance = 1 - knn10
  res_nn1, res_knn10    length residual: minus the expected value for passages of the same length (estimated from the random benign group in 5-word buckets)
Output: results/<ds>/relative_isolation_<variant>.json, results/relative_isolation_summary_<variant>.md
"""
import argparse, json, os, time

import numpy as np

from common import ROOT, gpu_topk, results_dir
from length_control import (NEGS, corpus_emb, corpus_lengths, encode_poison, make_groups,
                            print_table, score_rows)


def strip_self_both(S, I, self_idx, K):
    keep = I != self_idx[:, None]
    order = np.argsort(~keep, axis=1, kind="stable")[:, :K]
    return np.take_along_axis(S, order, 1), np.take_along_axis(I, order, 1)


def length_expect(L_ref, v_ref, width, min_n=30):
    """Estimate the expected feature value per length bucket; buckets with too few samples are linearly interpolated from neighbouring bucket centres"""
    b = L_ref // width
    ub, cnt = np.unique(b, return_counts=True)
    ok = ub[cnt >= min_n]
    centers = (ok + 0.5) * width
    means = np.array([v_ref[b == u].mean() for u in ok])
    return lambda L: np.interp(L, centers, means)


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
    groups, _ = make_groups(ds, items, pois_len, N, L, args)
    print(f"  poison {len(texts)} | " + " | ".join(f"{g} {len(v)}" for g, v in groups.items()), flush=True)

    P = encode_poison(texts, args.device)
    cand = np.concatenate([corpus[g] for g in groups.values()] + [P])
    self_idx = np.concatenate(list(groups.values()) + [np.full(len(P), -1)])
    label = np.concatenate([np.full(len(g), i) for i, g in enumerate(groups.values())] + [np.full(len(P), 3)])
    lens = np.concatenate([L[g] for g in groups.values()] + [pois_len]).astype(float)

    # first layer: neighbours of the candidate texts
    t0 = time.time()
    S, I = gpu_topk([corpus], cand, args.K + 1, device=args.device)
    S, I = strip_self_both(S, I, self_idx, args.K)
    nn1, knn10 = S[:, 0], S[:, :10].mean(1)

    # second layer: neighbours of each of the first M neighbours y. Leave-one-out: remove both y itself and the candidate x from y's neighbours,
    # otherwise a benign passage x (in the corpus) would appear among y's neighbours while a poison would not, and the two reference frames would differ
    U, inv = np.unique(I[:, :args.M], return_inverse=True)
    inv = inv.reshape(-1, args.M)
    Su, Iu = gpu_topk([corpus], corpus[U], 12, device=args.device)
    Sp, Ip = Su[inv], Iu[inv]                                  # (n, M, 12)
    keep = (Ip != U[inv][..., None]) & (Ip != self_idx[:, None, None])
    order = np.argsort(~keep, axis=2, kind="stable")[..., :10]
    Sp = np.take_along_axis(Sp, order, 2)                      # (n, M, 10)
    nn1_y, knn10_y = Sp[..., 0], Sp.mean(2)                    # (n, M)
    print(f"  two-layer neighbour search: {len(cand):,} + {len(U):,} texts, {(time.time() - t0) / 60:.1f} min", flush=True)

    eps = 1e-6
    vals = {
        "nn1": nn1,
        "knn10": knn10,
        "rel_nn1": nn1 - nn1_y.mean(1),
        "rel_knn10": knn10 - knn10_y.mean(1),
        "lof_knn10": (1 - knn10_y).mean(1) / (1 - knn10 + eps),   # smaller = more isolated
    }
    ref = label == 0   # random benign group estimates the length expectation
    for f in ("nn1", "knn10"):
        vals[f"res_{f}"] = vals[f] - length_expect(lens[ref], vals[f][ref], args.width)(lens)
    vals["length_only"] = lens

    rows = score_rows(vals, label, args.boot, np.random.default_rng(args.seed + 2))
    print_table(rows)
    out = {"variant": args.variant, "M": args.M, "K": args.K,
           "n": {k: int(len(v)) for k, v in groups.items()} | {"poison": len(P)}, "features": rows}
    json.dump(out, open(os.path.join(rd, f"relative_isolation_{args.variant}.json"), "w"),
              indent=2, ensure_ascii=False)
    return out


def write_summary(res, args):
    feats = list(next(iter(res.values()))["features"])
    lines = [f"# Relative isolation (single view, {args.variant}; direction: more isolated = more suspicious)", "",
             f"Samples as in length_control (random {args.n_clean} / length-matched {args.n_match}); M = {args.M}; "
             f"brackets: {args.boot}-sample bootstrap 95% CI.", "",
             "## vs length-matched benign", "", "| feature | " + " | ".join(res) + " |", "|---" * (len(res) + 1) + "|"]
    cell = lambda r, g: f"{r[f'AUROC_vs_{g}']:.3f}" + (
        f" ({r[f'CI_vs_{g}'][0]:.2f}–{r[f'CI_vs_{g}'][1]:.2f})" if r[f"CI_vs_{g}"] else "")
    for f in feats:
        lines.append(f"| {f} | " + " | ".join(cell(o["features"][f], "clean-lenmatch") for o in res.values()) + " |")
    for g, name in [("clean-random", "random benign"), ("clean-gold", "gold")]:
        lines += ["", f"## vs {name}", "", "| feature | " + " | ".join(res) + " |", "|---" * (len(res) + 1) + "|"]
        for f in feats:
            lines.append(f"| {f} | " + " | ".join(cell(o["features"][f], g) for o in res.values()) + " |")
    p = os.path.join(ROOT, "results", f"relative_isolation_summary_{args.variant}.md")
    open(p, "w").write("\n".join(lines) + "\n")
    print("\n" + "\n".join(lines) + f"\n\nsummary saved: {p}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", nargs="+", default=["nq", "hotpotqa", "msmarco"],
                    choices=["nq", "hotpotqa", "msmarco"])
    ap.add_argument("--variant", default="bb", choices=["bb", "adv"])
    ap.add_argument("--n_clean", type=int, default=20000)
    ap.add_argument("--n_match", type=int, default=20000)
    ap.add_argument("--width", type=int, default=5)
    ap.add_argument("--K", type=int, default=50)
    ap.add_argument("--M", type=int, default=10, help="use the first M neighbours as reference")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--device", default="cuda")
    args = ap.parse_args()
    res = {ds: run(ds, args) for ds in args.dataset}
    write_summary(res, args)


if __name__ == "__main__":
    main()
