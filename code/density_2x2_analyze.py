"""
Statistics of the 2x2 intervention (CPU only). Reads the output of density_2x2.py.
    python density_2x2_analyze.py                  # native-speaker judgments
    python density_2x2_analyze.py --judgments none
Each language and seed has four cells (small / large size x low / high density); effects are paired by seed:
  density effect   = high - low density (same size)
  size effect      = 45k - 20k (same density)
  interaction      = (high - low)@45k - (high - low)@20k
+/- is the s.d. across seeds; "pooled" = mean of the four languages' effects (languages equally weighted).
Output: results/miracl/density_2x2/summary[_none].md
"""
import argparse, glob, json, os, re

import numpy as np

PROJ = os.environ.get("PROJ", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
R = os.path.join(PROJ, "results", "miracl")
D = os.path.join(R, "density_2x2")
LANGS = ["sw", "te", "yo", "id"]


def auc(pos, neg):
    neg = np.sort(neg)
    lo, hi = np.searchsorted(neg, pos, "left"), np.searchsorted(neg, pos, "right")
    return float(np.mean((lo + (hi - lo) / 2) / len(neg)))


def ms(v):
    v = np.asarray(v, float)
    return "—" if not len(v) else (f"{v.mean():+.3f} ± {v.std(ddof=1):.3f}" if len(v) > 1 else f"{v.mean():+.3f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--judgments", default=os.path.join(R, "review_judgments_native.json"))
    a = ap.parse_args()
    J = {} if a.judgments == "none" else json.load(open(a.judgments))
    res = {}
    for p in glob.glob(os.path.join(D, "*", "*_s*.npz")):
        m = re.match(r"(\d+)_(low|high)_s(\d+)\.npz$", os.path.basename(p))
        lang = os.path.basename(os.path.dirname(p))
        if not m:
            continue
        z = np.load(p)
        keep = np.array([J.get(lang, {}).get(str(z["qids"][j]), {}).get("label") != "bad" for j in z["items"]])
        r = {"corpus": int(z["corpus"]), "n_A": int(z["n_A"]), "n_A_all": int(z["n_A_all"]),
             "dens": float(z["n_ga10"][keep].mean()), "hit": float(z["hit5"][keep].mean()), "n": int(keep.sum())}
        for f in ("rel_knn10", "knn10"):
            sp = -z[f"pois_{f}"][keep]
            thr = float(np.quantile(-z[f"rand_{f}"], 0.95))
            r[f] = auc(sp, -z[f"match_{f}"]); r[f"tpr_{f}"] = float((sp > thr).mean())
            r[f"eff_{f}"] = float((z["hit5"][keep] & ~(sp > thr)).mean())
        res[(lang, int(m.group(1)), m.group(2), int(m.group(3)))] = r
    if not res:
        raise SystemExit("no results; run density_2x2.py first")
    sizes = sorted({k[1] for k in res}); seeds = sorted({k[3] for k in res})
    s0, s1 = sizes[0], sizes[-1]
    L = [f"# Controlled intervention: size x local density (fixed number of passages; judgments {'none' if a.judgments == 'none' else os.path.basename(a.judgments)})", "",
         "## 0. Manipulation check and sample", "", "| lang | size | passages | same-topic passages added at high density (all of A) | questions | same-topic neighbours: low / high | hit@5: low / high |",
         "|---|---|---|---|---|---|---|"]
    for lg in LANGS:
        for n in sizes:
            lo = [res[(lg, n, "low", s)] for s in seeds if (lg, n, "low", s) in res]
            hi = [res[(lg, n, "high", s)] for s in seeds if (lg, n, "high", s) in res]
            if lo and hi:
                L.append(f"| {lg} | {n:,} | {lo[0]['corpus']:,} / {hi[0]['corpus']:,} | {hi[0]['n_A']:,} ({hi[0]['n_A_all']:,}) | {lo[0]['n']} | "
                         f"{np.mean([x['dens'] for x in lo]):.2f} / {np.mean([x['dens'] for x in hi]):.2f} | "
                         f"{np.mean([x['hit'] for x in lo]):.2f} / {np.mean([x['hit'] for x in hi]):.2f} |")
    for f in ("rel_knn10", "knn10"):
        L += ["", f"## {f}: AUROC of the four cells (mean) and effects (paired by seed, +/- s.d. across seeds)", "",
              f"| lang | low@{s0//1000}k | high@{s0//1000}k | low@{s1//1000}k | high@{s1//1000}k | density effect@{s0//1000}k | density effect@{s1//1000}k | "
              f"size effect@low | size effect@high | interaction |", "|---|---|---|---|---|---|---|---|---|---|"]
        pooled = {k: [] for k in ("d0", "d1", "s_lo", "s_hi", "inter")}
        for lg in LANGS:
            ok = [s for s in seeds if all((lg, n, m, s) in res for n in (s0, s1) for m in ("low", "high"))]
            if not ok:
                continue
            g = lambda n, m: np.array([res[(lg, n, m, s)][f] for s in ok])
            d0, d1 = g(s0, "high") - g(s0, "low"), g(s1, "high") - g(s1, "low")
            sl, sh = g(s1, "low") - g(s0, "low"), g(s1, "high") - g(s0, "high")
            for k, v in zip(pooled, (d0, d1, sl, sh, d1 - d0)):
                pooled[k].append(v.mean())
            L.append(f"| {lg} | {g(s0, 'low').mean():.3f} | {g(s0, 'high').mean():.3f} | {g(s1, 'low').mean():.3f} | "
                     f"{g(s1, 'high').mean():.3f} | {ms(d0)} | {ms(d1)} | {ms(sl)} | {ms(sh)} | {ms(d1 - d0)} |")
        if pooled["d0"]:
            L.append("| pooled (languages equally weighted) | | | | | " + " | ".join(f"{np.mean(v):+.3f}" for v in pooled.values()) + " |")
        L += ["", f"### {f}: TPR@5% and surviving-poison rate after filtering (mean)", "",
              "| lang | size | TPR@5% low / high | surviving-poison rate low / high |", "|---|---|---|---|"]
        for lg in LANGS:
            for n in sizes:
                lo = [res[(lg, n, "low", s)] for s in seeds if (lg, n, "low", s) in res]
                hi = [res[(lg, n, "high", s)] for s in seeds if (lg, n, "high", s) in res]
                if lo and hi:
                    L.append(f"| {lg} | {n:,} | {np.mean([x['tpr_' + f] for x in lo]):.2f} / {np.mean([x['tpr_' + f] for x in hi]):.2f} | "
                             f"{np.mean([x['eff_' + f] for x in lo]):.2f} / {np.mean([x['eff_' + f] for x in hi]):.2f} |")
    L += ["", "Reading: a negative density effect = more same-topic evidence makes detection harder (with the total number of passages fixed, this is an interventional effect);",
          "a positive size effect = at the same density, larger corpora are easier. With two sizes and five seeds, the interaction is descriptive only."]
    out = os.path.join(D, f"summary{'' if a.judgments != 'none' else '_none'}.md")
    open(out, "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
