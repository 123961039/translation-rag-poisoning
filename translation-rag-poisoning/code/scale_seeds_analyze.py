"""
Statistics of the scale-control robustness experiment (CPU only, one or two minutes). Reads the output of scale_seeds.py.
    python scale_seeds_analyze.py                                   # default: filter questions by native judgments
    python scale_seeds_analyze.py --judgments ../results/miracl/review_judgments.json   # old review
    python scale_seeds_analyze.py --judgments none                  # no exclusion
Output: results/miracl/scale_seeds/summary[_<judgments>].md / .json
Tables
  0. self-check: does seed 0 + keep match the original detect_feats*.npz and attack_detail.jsonl
  1. AUROC at each size (vs length-matched): mean +/- sd across seeds, and paired drop relative to full
  2. effect of forcing gold to be kept: keep - nokeep on the same seed
  3. across languages: Spearman rho between drop and shrink factor, per seed
  4. TPR@5% and surviving-poison rate after filtering (5% FPR)
"""
import argparse, glob, itertools, json, os, re

import numpy as np

PROJ = os.environ.get("PROJ", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
R = os.path.join(PROJ, "results", "miracl")
D = os.path.join(R, "scale_seeds")
LANGS = ["sw", "te", "yo", "id"]
FEATS = ["rel_knn10", "knn10"]


def auc(pos, neg):
    neg = np.sort(neg)
    lo, hi = np.searchsorted(neg, pos, "left"), np.searchsorted(neg, pos, "right")
    return float(np.mean((lo + (hi - lo) / 2) / len(neg)))


def rank(x):
    """Average ranks (ties averaged)"""
    x = np.asarray(x, float); o = np.argsort(x, kind="stable"); r = np.empty(len(x)); i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and x[o[j + 1]] == x[o[i]]:
            j += 1
        r[o[i:j + 1]] = (i + j) / 2; i = j + 1
    return r


def spearman(x, y):
    a, b = rank(np.asarray(x)), rank(np.asarray(y))
    return float(np.corrcoef(a, b)[0, 1])


def perm_p(x, y):
    r0 = abs(spearman(x, y))
    ps = list(itertools.permutations(y))
    return sum(abs(spearman(x, list(p))) >= r0 - 1e-12 for p in ps) / len(ps)


def ms(v, d=3):
    v = [x for x in v if x is not None and not np.isnan(x)]
    if not v:
        return "—"
    return f"{np.mean(v):.{d}f}" + (f" ± {np.std(v, ddof=1):.{d}f}" if len(v) > 1 else "")


def size_label(s):
    return "full" if s == "full" else f"{int(s):,}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--judgments", default=os.path.join(R, "review_judgments_native.json"),
                    help='judgment file; "none" = no exclusion')
    ap.add_argument("--variant", default="trans")
    ap.add_argument("--form", default="bb")
    args = ap.parse_args()
    key = f"{args.variant}_{args.form}"
    J = {} if args.judgments == "none" else json.load(open(args.judgments))
    jname = ("none" if args.judgments == "none" else
             "native" if "native" in os.path.basename(args.judgments) else "old")

    # ---------- read all results ----------
    res = {}          # (lang, size, mode, seed) -> {feat: {...}, corpus, ...}
    for p in sorted(glob.glob(os.path.join(D, "*", "*_s*.npz"))):
        lang = os.path.basename(os.path.dirname(p))
        m = re.match(r"(full|\d+)_(full|keep|nokeep)_s(\d+)\.npz$", os.path.basename(p))
        if not m or lang not in LANGS:
            continue
        size, mode, seed = m.group(1), m.group(2), int(m.group(3))
        z = np.load(p)
        if f"{key}_items" not in z:
            continue
        qids = z["qids"]; idx = z[f"{key}_items"]
        keep = np.array([J.get(lang, {}).get(str(qids[j]), {}).get("label") != "bad" for j in idx])
        hit = z[f"{key}_hit5"][keep]
        r = {"corpus": int(z["corpus"]), "n_gold_added": int(z["n_gold_added"]), "n": int(keep.sum())}
        for f in FEATS:
            sp = -z[f"{key}_pois_{f}"][keep]
            sm = -z[f"{key}_match_{f}"]
            thr = float(np.quantile(-z[f"rand_{f}"], 0.95))
            flag = sp > thr
            r[f] = {"auc": auc(sp, sm), "tpr5": float(flag.mean()), "eff": float((hit & ~flag).mean()),
                    "hit": float(hit.mean())}
        res[(lang, size, mode, seed)] = r
    if not res:
        raise SystemExit(f"no results under {D}; run scale_seeds.py first")
    seeds = sorted({k[3] for k in res})
    sizes = sorted({k[1] for k in res}, key=lambda s: -float("inf") if s == "full" else -int(s))
    full_n = {l: res[(l, "full", "full", seeds[0])]["corpus"] for l in LANGS if (l, "full", "full", seeds[0]) in res}

    L = [f"# Scale-control robustness ({args.variant}/{args.form}, question judgments: {jname}, seeds {seeds})", "",
         "keep = all dev gold passages added back when downsampling (original procedure); nokeep = the same random subset of the same seed, without adding gold. "
         "AUROC is always against length-matched benign passages; +/- is the sd across seeds.", ""]

    # ---------- 0. self-check ----------
    L += ["## 0. Self-check: does seed 0 + keep reproduce the original results", ""]
    chk = []
    for lang in LANGS:
        rd = os.path.join(R, lang)
        detail = {}
        dp = os.path.join(rd, "attack_detail.jsonl")
        if os.path.exists(dp):
            detail = [json.loads(l) for l in open(dp)]
        for size in sizes:
            mode = "full" if size == "full" else "keep"
            p = os.path.join(D, lang, f"{size}_{mode}_s0.npz")
            old = os.path.join(rd, "detect_feats.npz" if size == "full" else f"detect_feats_sub{size}.npz")
            if not (os.path.exists(p) and os.path.exists(old)):
                continue
            a, b = np.load(p), np.load(old)
            k = f"{args.variant}_{args.form}_rel_knn10"
            if k not in b:
                continue
            dfeat = float(np.max(np.abs(a[f"{key}_pois_rel_knn10"] - b[k])))
            same_match = np.array_equal(a[f"{key}_match"], b[f"{args.variant}_{args.form}_match"])
            hk = f"{'full' if size == 'full' else 'sub' + size}/{args.variant}/{args.form}/single/hit5"
            hit_ok = "—"
            if detail and hk in detail[0]:
                idx = a[f"{key}_items"]
                hit_ok = "consistent" if all(bool(detail[j][hk]) == bool(h) for j, h in zip(idx, a[f"{key}_hit5"])) else "WARNING: inconsistent"
            chk.append(f"| {lang} | {size_label(size)} | {dfeat:.1e} | {'consistent' if same_match else 'WARNING: inconsistent'} | {hit_ok} |")
    if chk:
        L += ["| lang | size | max poison feature diff | length-matched controls | hit@5 |", "|---|---|---|---|---|"] + chk
        L += ["", "The poison feature difference should be 0 or below 1e-3 (tie order of fp16 retrieval may differ); larger means the code or data changed.", ""]
    else:
        L += ["(no original files to compare, or seed 0 not run yet)", ""]

    # ---------- 1. AUROC ----------
    for f in FEATS:
        L += [f"## 1. AUROC ({f}): mean +/- sd across seeds; brackets: paired drop relative to full", "",
              "| lang | size | passages | questions | keep | nokeep |", "|---|---|---|---|---|---|"]
        for lang in LANGS:
            for size in sizes:
                row = []
                for mode in (["full"] if size == "full" else ["keep", "nokeep"]):
                    a = [res[(lang, size, mode, s)][f]["auc"] for s in seeds if (lang, size, mode, s) in res]
                    d = [res[(lang, size, mode, s)][f]["auc"] - res[(lang, "full", "full", s)][f]["auc"]
                         for s in seeds if (lang, size, mode, s) in res and (lang, "full", "full", s) in res]
                    row.append("—" if not a else ms(a) + ("" if size == "full" else f" (d {ms(d)})"))
                if all(c == "—" for c in row):
                    continue
                any_k = next((res[k] for k in res if k[0] == lang and k[1] == size), None)
                cs = [res[k]["corpus"] for k in res if k[0] == lang and k[1] == size and k[2] in ("full", "keep")]
                L.append(f"| {lang} | {size_label(size)} | {int(np.mean(cs)):,} | {any_k['n']} | "
                         + (f"{row[0]} | — |" if size == "full" else f"{row[0]} | {row[1]} |"))
        L.append("")

    # ---------- 2. keep − nokeep ----------
    L += ["## 2. Effect of forcing gold to be kept (AUROC difference keep - nokeep on the same seed)", "",
          "Positive = easier to detect after adding gold back; negative = adding gold back makes poisons look less isolated, harder to detect.", "",
          "| lang | size | gold passages added | share of corpus | " + " | ".join(FEATS) + " |", "|---|---|---|---|" + "---|" * len(FEATS)]
    for lang in LANGS:
        for size in sizes:
            if size == "full":
                continue
            ks = [s for s in seeds if (lang, size, "keep", s) in res and (lang, size, "nokeep", s) in res]
            if not ks:
                continue
            add = np.mean([res[(lang, size, "keep", s)]["n_gold_added"] for s in ks])
            frac = np.mean([res[(lang, size, "keep", s)]["n_gold_added"] / res[(lang, size, "keep", s)]["corpus"] for s in ks])
            cells = [ms([res[(lang, size, "keep", s)][f]["auc"] - res[(lang, size, "nokeep", s)][f]["auc"] for s in ks])
                     for f in FEATS]
            L.append(f"| {lang} | {size_label(size)} | {add:,.0f} | {frac:.1%} | " + " | ".join(cells) + " |")
    L.append("")

    # ---------- 3. Spearman across languages ----------
    L += ["## 3. Across languages: Spearman rho between AUROC drop and shrink factor (full / actual passages), per seed", "",
          "With only 4 language points the smallest exact permutation p is 0.083; what matters is whether seeds agree in direction.", ""]
    for f in FEATS:
        for size in sizes:
            if size == "full":
                continue
            for mode in ("keep", "nokeep"):
                rs = []
                for s in seeds:
                    pts = [(full_n[l] / res[(l, size, mode, s)]["corpus"],
                            res[(l, size, mode, s)][f]["auc"] - res[(l, "full", "full", s)][f]["auc"])
                           for l in LANGS if (l, size, mode, s) in res and (l, "full", "full", s) in res and l in full_n]
                    # languages whose corpus is not larger than this size are not shrunk: drop 0, factor 1 (they are internal controls)
                    have = {l for l in LANGS if (l, size, mode, s) in res}
                    pts += [(1.0, 0.0) for l in LANGS if l not in have and (l, "full", "full", s) in res]
                    if len(pts) == 4:
                        x, y = zip(*pts)
                        rs.append((s, spearman(x, y), perm_p(list(x), list(y))))
                if rs:
                    L.append(f"- {f} / {size_label(size)} / {mode}: " + ", ".join(f"seed{s} rho={r:+.2f}" for s, r, _ in rs)
                             + f" (min p {min(p for *_, p in rs):.3f})")
    L.append("")

    # ---------- 4. TPR and surviving-poison rate ----------
    for f in FEATS:
        L += [f"## 4. Deployment metrics ({f}, 5% FPR): TPR@5% and surviving-poison rate after filtering (hit@5 and not flagged)", "",
              "| lang | size | mode | TPR@5% | hit@5 | surviving rate |", "|---|---|---|---|---|---|"]
        for lang in LANGS:
            for size in sizes:
                for mode in (["full"] if size == "full" else ["keep", "nokeep"]):
                    v = [res[(lang, size, mode, s)][f] for s in seeds if (lang, size, mode, s) in res]
                    if v:
                        L.append(f"| {lang} | {size_label(size)} | {mode} | {ms([x['tpr5'] for x in v], 2)} | "
                                 f"{ms([x['hit'] for x in v], 2)} | {ms([x['eff'] for x in v], 2)} |")
        L.append("")
    L += ["The surviving rate here uses all kept questions of the variant (not the questions shared by the three variants as in ml_analyze table C), so there are more questions and the numbers need not match table C."]

    suffix = "" if jname == "native" else f"_{jname}"
    out = os.path.join(D, f"summary{suffix}.md")
    open(out, "w").write("\n".join(L) + "\n")
    json.dump({f"{k[0]}|{k[1]}|{k[2]}|{k[3]}": v for k, v in res.items()},
              open(os.path.join(D, f"summary{suffix}.json"), "w"), indent=1, ensure_ascii=False)
    print("\n".join(L))
    print(f"\nsaved {out}")


if __name__ == "__main__":
    main()
