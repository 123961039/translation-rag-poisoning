"""
Strictly paired comparison of the three poison generation methods (CPU only).
In the per-variant detection tables the question sets differ (native generation fails more often) and length-matched negatives are drawn separately.
Here only questions that have poisons for all three variants and are kept by the judgments are used; negatives are the same random benign passages for all variants,
plus a shared "length-matched union" (union of the three variants' length-matched samples). Differences use bootstrap paired by question.
    python ml_paired_variants.py                         # native-speaker judgments, full corpora
    python ml_paired_variants.py --judgments none
    python ml_paired_variants.py --feats _sub45000       # another size
Output: results/miracl/paired_variants[_<judgments>][<size>].md / .json
"""
import argparse, json, os

import numpy as np

PROJ = os.environ.get("PROJ", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
R = os.path.join(PROJ, "results", "miracl")
LANGS = ["sw", "te", "yo", "id"]
VARIANTS = ["native", "trans", "en"]
PAIRS = [("trans", "native"), ("trans", "en"), ("en", "native")]


def auc(pos, neg):
    neg = np.sort(neg)
    lo, hi = np.searchsorted(neg, pos, "left"), np.searchsorted(neg, pos, "right")
    return float(np.mean((lo + (hi - lo) / 2) / len(neg)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--judgments", default=os.path.join(R, "review_judgments_native.json"), help='"none" = no filtering')
    ap.add_argument("--feats", default="")
    ap.add_argument("--forms", nargs="+", default=["bb", "adv"])
    ap.add_argument("--boot", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    J = {} if args.judgments == "none" else json.load(open(args.judgments))
    jname = "none" if args.judgments == "none" else ("native" if "native" in os.path.basename(args.judgments) else "old")
    rng = np.random.default_rng(args.seed)

    L = [f"# Paired comparison of poison generation methods (shared questions and negatives; judgments {jname}; size {args.feats or 'full'})", "",
         "Lower AUROC = harder to detect. Difference = former - latter; negative means the former is harder to detect; brackets: 95% CI from bootstrap paired by question, "
         "* if it excludes 0.", ""]
    res = []
    for feat in ["rel_knn10", "knn10"]:
        L += [f"## {feat}", "", "| lang | form | shared questions | negatives | native | trans | en | "
              + " | ".join(f"{a}−{b}" for a, b in PAIRS) + " |", "|---|---|---|---|---|---|---|" + "---|" * len(PAIRS)]
        for lang in LANGS:
            rd = os.path.join(R, lang)
            p = os.path.join(rd, f"detect_feats{args.feats}.npz")
            if not os.path.exists(p):
                continue
            z = np.load(p)
            items = [json.loads(l) for l in open(os.path.join(rd, "poison.jsonl"))]
            pos_c = {r: i for i, r in enumerate(z["clean_rows"])}
            cf = -z[f"clean_{feat}"]
            for form in args.forms:
                has = {v: [j for j, it in enumerate(items) if it.get(f"{v}_adv")] for v in VARIANTS}
                if not all(f"{v}_{form}_{feat}" in z for v in VARIANTS):
                    continue
                keep = {j for j, it in enumerate(items) if J.get(lang, {}).get(it["qid"], {}).get("label") != "bad"}
                common = sorted(set(has["native"]) & set(has["trans"]) & set(has["en"]) & keep)
                if len(common) < 5:
                    continue
                sp = {v: -z[f"{v}_{form}_{feat}"][[has[v].index(j) for j in common]] for v in VARIANTS}
                negs = {"random": cf[[pos_c[r] for r in z["rand"]]],
                        "length-matched union": cf[[pos_c[r] for r in np.unique(np.concatenate(
                            [z[f"{v}_{form}_match"] for v in VARIANTS]))]]}
                for nname, sn in negs.items():
                    a = {v: auc(sp[v], sn) for v in VARIANTS}
                    cells = []
                    n = len(common)
                    for x, y in PAIRS:
                        bs = []
                        for _ in range(args.boot):
                            ix = rng.integers(0, n, n)
                            bs.append(auc(sp[x][ix], sn) - auc(sp[y][ix], sn))
                        lo, hi = np.percentile(bs, [2.5, 97.5])
                        star = "*" if lo > 0 or hi < 0 else ""
                        cells.append(f"{a[x] - a[y]:+.3f} ({lo:+.2f}, {hi:+.2f}){star}")
                        res.append({"feat": feat, "lang": lang, "form": form, "neg": nname, "n": n, "pair": f"{x}-{y}",
                                    "diff": a[x] - a[y], "ci": [float(lo), float(hi)], **{f"auc_{v}": a[v] for v in VARIANTS}})
                    L.append(f"| {lang} | {form} | {n} | {nname} | {a['native']:.3f} | {a['trans']:.3f} | {a['en']:.3f} | "
                             + " | ".join(cells) + " |")
        L.append("")
    L += ["Note: negatives are identical for the three variants, so differences come only from the poison texts. 'random' negatives do not control length; "
          "'length-matched union' covers the length distributions of all three variants; a conclusion is robust only if both agree."]
    tag = ("" if jname == "native" else f"_{jname}") + args.feats
    out = os.path.join(R, f"paired_variants{tag}.md")
    open(out, "w").write("\n".join(L) + "\n")
    json.dump(res, open(os.path.join(R, f"paired_variants{tag}.json"), "w"), indent=1, ensure_ascii=False)
    print("\n".join(L)); print(f"\nsaved {out}")


if __name__ == "__main__":
    main()
