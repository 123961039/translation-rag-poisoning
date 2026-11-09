"""Is AUROC good enough? (CPU only, a few seconds)

Two features can differ very little in AUROC yet catch several times more poisons at a fixed FPR, because AUROC covers the whole
curve while ingestion filtering operates only at its left end (FPR 1%-5%). This script aligns the results of two features by
(language, variant, form), compares AUROC and TPR differences row by row, and answers a question with practical consequences:

    if features are chosen by AUROC, can the choice be wrong?

    python ml_metric_gap.py                              # default rel_knn10 vs knn10, full corpora
    python ml_metric_gap.py --feats _sub45000            # downsampled corpora
    python ml_metric_gap.py --a knn10 --b nn1

Input: results/miracl/analysis_excl-<level>[_<feat>][<size suffix>].json (output of ml_analyze.py)
Output: results/miracl/metric_gap[_<size suffix>].md / .json
"""
import argparse, glob, json, os

from ml_common import ROOT

OUT = os.path.join(ROOT, "results", "miracl")
DEFAULT_FEAT = "rel_knn10"


def load_B(level, feat, feats):
    """Locate files by the args recorded inside them, not by their names"""
    for p in sorted(glob.glob(os.path.join(OUT, f"analysis_excl-{level}*.json"))):
        try:
            J = json.load(open(p))
        except Exception:
            continue
        a = J.get("args", {})
        if a.get("feat", DEFAULT_FEAT) == feat and a.get("feats", "") == feats:
            return {(r["lang"], r["variant"], r["form"]): r for r in J["B"]}, os.path.basename(p)
    return None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", default=DEFAULT_FEAT, help="feature A (pre-registered main feature)")
    ap.add_argument("--b", default="knn10", help="feature B (comparison)")
    ap.add_argument("--exclude", default="bad", choices=["none", "bad", "unsure"])
    ap.add_argument("--feats", default="", help='size suffix, e.g. "_sub45000"; default full corpus')
    ap.add_argument("--tol", type=float, default=0.02, help="minimum absolute tolerance")
    ap.add_argument("--min_items", type=float, default=3.0,
                    help="a TPR difference must amount to at least this many poisons to count (TPR granularity = 1/n)")
    args = ap.parse_args()

    A, pa = load_B(args.exclude, args.a, args.feats)
    B, pb = load_B(args.exclude, args.b, args.feats)
    for feat, got in ((args.a, A), (args.b, B)):
        if got is None:
            print(f"no analysis file for main feature {feat}, size suffix '{args.feats}', exclusion {args.exclude}.\n"
                  f"Run first: python ml_analyze.py --exclude {args.exclude} --feat {feat}"
                  + (f" --feats {args.feats} --size {args.feats.lstrip('_')}" if args.feats else ""))
            return
    keys = [k for k in A if k in B]
    if not keys:
        print("the two files share no (language, variant, form) rows")
        return

    g = lambda r, k: r[k][0]
    rows = []
    for k in keys:
        a, b = A[k], B[k]
        n = min(a.get("n", 0), b.get("n", 0)) or 1
        rows.append({"key": k, "n": n,
                     # TPR granularity is 1/n: one poison = 1/n. Tolerance = max(absolute tolerance, MIN_ITEMS poisons)
                     "tol": max(args.tol, args.min_items / n),
                     # when both sides are near 0, ratios and directions are meaningless; marked separately
                     "floor1": max(g(a, "tpr@1%"), g(b, "tpr@1%")) <= 2.0 / n,
                     "floor5": max(g(a, "tpr@5%"), g(b, "tpr@5%")) <= 2.0 / n,
                     "d_auc":  g(a, "auc_lenmatch") - g(b, "auc_lenmatch"),
                     "d_tpr1": g(a, "tpr@1%") - g(b, "tpr@1%"),
                     "d_tpr5": g(a, "tpr@5%") - g(b, "tpr@5%"),
                     "auc": (g(a, "auc_lenmatch"), g(b, "auc_lenmatch")),
                     "t1":  (g(a, "tpr@1%"), g(b, "tpr@1%")),
                     "t5":  (g(a, "tpr@5%"), g(b, "tpr@5%"))})

    size = "full corpus" if not args.feats else args.feats.lstrip("_")
    L = [f"# Can choosing by AUROC pick the wrong feature? ({args.a} vs {args.b}, {size}, exclusion {args.exclude})", "",
         f"A = `{args.a}` ({pa})   B = `{args.b}` ({pb}). Differences are A - B; positive means A is better.", "",
         "| lang | variant | form | n | tolerance | AUROC A/B | dAUROC | TPR@5% A/B | dTPR@5% | agree@5% | "
         "TPR@1% A/B | dTPR@1% | agree@1% |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    dis5, dis1, floored = [], [], []
    for r in sorted(rows, key=lambda r: r["key"]):
        l, v, f = r["key"]
        t = r["tol"]
        sa = (r["d_auc"] > args.tol) - (r["d_auc"] < -args.tol)
        verdict = {}
        for fp, dk, fl, bag in ((5, "d_tpr5", "floor5", dis5), (1, "d_tpr1", "floor1", dis1)):
            st = (r[dk] > t) - (r[dk] < -t)
            if r[fl]:
                verdict[fp] = "floor"          # both sides near 0, direction undecidable
                if fp == 1:
                    floored.append(r)
            elif sa and st and sa != st:
                verdict[fp] = "**no**"
                bag.append(r)
            else:
                verdict[fp] = "yes"
        r["verdict"] = verdict
        L.append(f"| {l} | {v} | {f} | {r['n']} | {t:.2f} | "
                 f"{r['auc'][0]:.3f}/{r['auc'][1]:.3f} | {r['d_auc']:+.3f} | "
                 f"{r['t5'][0]:.2f}/{r['t5'][1]:.2f} | {r['d_tpr5']:+.2f} | {verdict[5]} | "
                 f"{r['t1'][0]:.2f}/{r['t1'][1]:.2f} | {r['d_tpr1']:+.2f} | {verdict[1]} |")
    L += ["", f"tolerance = max({args.tol}, {args.min_items:g}/n). TPR granularity is 1/n, "
              f"so with n=30 a difference of 0.03 is a single poison and does not count. "
              f"'floor' = TPR@1% <= 2/n on both sides, near 0, direction undecidable.", ""]

    # ---------- amplification: how much larger the same feature difference is in TPR than in AUROC ----------
    med = lambda x: sorted(x)[len(x) // 2] if x else float("nan")
    use5 = [r for r in rows if abs(r["d_auc"]) > 0.01 and not r["floor5"]]
    use1 = [r for r in rows if abs(r["d_auc"]) > 0.01 and not r["floor1"]]
    amp5 = [abs(r["d_tpr5"]) / abs(r["d_auc"]) for r in use5]
    amp1 = [abs(r["d_tpr1"]) / abs(r["d_auc"]) for r in use1]
    big5 = sum(1 for r in use5 if abs(r["d_tpr5"]) > abs(r["d_auc"]))
    big1 = sum(1 for r in use1 if abs(r["d_tpr1"]) > abs(r["d_auc"]))

    L += ["", "## How much the same feature difference is amplified in deployment metrics", "",
          f"- |dTPR@5%| > |dAUROC|: **{big5}/{len(use5)}** rows, median amplification **{med(amp5):.1f}x**",
          f"- |dTPR@1%| > |dAUROC|: **{big1}/{len(use1)}** rows, median amplification **{med(amp1):.1f}x**", ""]
    if len(use1) < len(rows) - 2:
        L += [f"Warning: only {len(use1)}/{len(rows)} rows can be used for the TPR@1% amplification; "
              f"in the others both features have TPR@1% near 0 (too few poisons, 1/n granularity too coarse). "
              f"TPR@1% conclusions are unreliable at this size; use TPR@5%.", ""]
    L += ["(Rows with |dAUROC| <= 0.01 are excluded to avoid dividing by near 0; floor rows are excluded as well.)", ""]

    L += ["## Do the two metrics lead to opposite choices?", "",
          "The two operating points are reported separately. TPR@5% is rarely at the floor and is more reliable than TPR@1%; "
          "TPR@1% is closer to real deployment but coarse when there are few poisons.", ""]
    for fp, bag, fl in ((5, dis5, "floor5"), (1, dis1, "floor1")):
        nfl = sum(1 for r in rows if r[fl])
        jud = len(rows) - nfl
        L += [f"### Operating point FPR={fp}%", ""]
        if bag:
            L += [f"**In {len(bag)}/{jud} decidable rows, AUROC and TPR@{fp}% point to different features**"
                  + (f" ({nfl} more rows at the floor are undecidable)" if nfl else "") + ":", ""]
            for r in sorted(bag, key=lambda r: -abs(r[f"d_tpr{fp}"])):
                l, v, f_ = r["key"]
                d = r[f"d_tpr{fp}"]
                wa = args.a if r["d_auc"] > 0 else args.b
                wt = args.a if d > 0 else args.b
                hi, lo = max(r[f"t{fp}"]), min(r[f"t{fp}"])
                L.append(f"- {l}/{v}/{f_} (n={r['n']}, tolerance {r['tol']:.2f}): "
                         f"AUROC picks `{wa}` ({r['d_auc']:+.3f}), "
                         f"TPR@{fp}% picks `{wt}` ({d:+.2f}, i.e. {abs(d) * r['n']:.0f} poisons"
                         + (f", {hi / lo:.1f}x" if lo > 0 else "") + ")")
            L += [""]
        else:
            L += [f"No disagreement: in {jud} decidable rows both metrics point to the same feature"
                  + (f" ({nfl} more rows at the floor)" if nfl else "") + ".", ""]

    # a consistent direction across a whole language is much more robust than single-row disagreements
    L += ["### By language (do the six rows of a language point to the same feature?)", ""]
    by_lang = {}
    for r in rows:
        by_lang.setdefault(r["key"][0], []).append(r)
    for lg, rs in sorted(by_lang.items()):
        if len(rs) < 3:
            continue
        n5 = sum(1 for r in rs if r["d_tpr5"] > 0)
        amax = max(abs(r["d_auc"]) for r in rs)
        ratios = [max(r["t5"]) / min(r["t5"]) for r in rs if min(r["t5"]) > 0]
        side = args.a if n5 > len(rs) / 2 else args.b
        agree = max(n5, len(rs) - n5)
        note = ""
        if agree == len(rs) and amax <= 0.03:
            note = f"  <- **AUROC shows no difference (all within +/-{amax:.3f}), TPR@5% all in the same direction**"
        L.append(f"- {lg}: {agree}/{len(rs)} rows of TPR@5% point to `{side}`, "
                 f"max |dAUROC| {amax:.3f}"
                 + (f", TPR@5% ratio {min(ratios):.1f}-{max(ratios):.1f}x" if ratios else "") + note)
    L += ["", "Six rows of a language (three variants x two forms) pointing to the same feature are much more robust than single-row disagreements; "
              "the six rows are not independent samples, but a consistent direction with multiplicative magnitude cannot be explained by granularity noise.", ""]

    L += ["## Why", "",
          "AUROC is the area under the whole ROC curve and weights all operating points equally. Ingestion filtering can only operate at the narrow "
          "left end: flagging 5% of benign documents is already the limit, and in practice it is usually pushed below 1%. Two features "
          "can have almost the same area and still differ several-fold in this region; the difference lies in the tail of the suspicion scores, "
          "to which the area is insensitive.", "",
          "**The primary metric should therefore be TPR at a fixed low FPR, with AUROC as a secondary metric.**", ""]

    tag = args.feats
    open(os.path.join(OUT, f"metric_gap{tag}.md"), "w").write("\n".join(L) + "\n")
    json.dump({"rows": [{**r, "key": list(r["key"]), "verdict": r.get("verdict", {})} for r in rows],
               "n_floored": len(floored),
               "amp5_median": med(amp5), "amp1_median": med(amp1),
               "disagree_tpr5": [list(r["key"]) for r in dis5],
               "disagree_tpr1": [list(r["key"]) for r in dis1], "args": vars(args)},
              open(os.path.join(OUT, f"metric_gap{tag}.json"), "w"), indent=1, ensure_ascii=False)
    print("\n".join(L))
    print(f"\nsaved {OUT}/metric_gap{tag}.md")


if __name__ == "__main__":
    main()