"""
Is detection difficulty driven by corpus size or by local density around the poison? (CPU only)
Reads the main results *.npz and local-density files *_dens.npz written by scale_seeds.py.
    python density_analyze.py                                       # native-speaker judgments
    python density_analyze.py --judgments none                      # no filtering (more questions, more stable estimates)
Output: results/miracl/scale_seeds/density[_<judgments>].md
Approach
  For every (size, mode, seed), each poison has a "suspicion percentile" = the share of length-matched benign passages it is more suspicious than
  (the mean over poisons is the AUROC). The same poison appears in many corpora, so we can compare within question:
  demean by question (fixed effects), then regress the percentile on log10(corpus size) and local density jointly.
  The three sampling modes separate the two: keep preserves the gold passages in small corpora (high local density); nokeep lowers both.
  If the size coefficient is close to 0 once local density is controlled, the "scale effect" is really a local-density effect.
  CIs are cluster bootstrap by question (all observations of a question resampled together).
Tables
  1. AUROC under the three modes (including the article mode) and the drop relative to the full corpus
  2. Local density: number of top-10 neighbours from the question's gold article, share whose nearest neighbour is from the gold article
  3. Within-question regression: percentile ~ log10(size) + local density
  4. Stratified: does corpus size still matter within density strata?
"""
import argparse, glob, json, os, re

import numpy as np

PROJ = os.environ.get("PROJ", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
R = os.path.join(PROJ, "results", "miracl")
D = os.path.join(R, "scale_seeds")
LANGS = ["sw", "te", "yo", "id"]
FEATS = ["rel_knn10", "knn10"]
MODES = ["keep", "article", "nokeep"]


def pct(sp, sm):
    """Share of benign passages each poison is more suspicious than (ties count half); the mean is the AUROC"""
    sm = np.sort(sm)
    lo, hi = np.searchsorted(sm, sp, "left"), np.searchsorted(sm, sp, "right")
    return (lo + (hi - lo) / 2) / len(sm)


def ms(v, d=3):
    v = [x for x in v if x is not None and not np.isnan(x)]
    if not v:
        return "—"
    return f"{np.mean(v):.{d}f}" + (f" ± {np.std(v, ddof=1):.{d}f}" if len(v) > 1 else "")


def size_label(s):
    return "full" if s == "full" else f"{int(s):,}"


def fe_ols(y, X, g):
    """OLS after demeaning by group g; returns coefficients"""
    yd, Xd = y.copy(), X.copy()
    for u in np.unique(g):
        m = g == u
        yd[m] -= yd[m].mean(); Xd[m] -= Xd[m].mean(0)
    keep = np.abs(Xd).sum(1) > 0
    if keep.sum() < X.shape[1] + 2:
        return np.full(X.shape[1], np.nan)
    return np.linalg.lstsq(Xd[keep], yd[keep], rcond=None)[0]


def cluster_boot(y, X, g, B, rng):
    est = fe_ols(y, X, g)
    groups = np.unique(g)
    idx = {u: np.flatnonzero(g == u) for u in groups}
    bs = []
    for _ in range(B):
        pick = rng.choice(groups, len(groups), replace=True)
        rows = np.concatenate([idx[u] for u in pick])
        gg = np.concatenate([np.full(len(idx[u]), k) for k, u in enumerate(pick)])
        bs.append(fe_ols(y[rows], X[rows], gg))
    bs = np.array(bs)
    return est, np.nanpercentile(bs, 2.5, 0), np.nanpercentile(bs, 97.5, 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--judgments", default=os.path.join(R, "review_judgments_native.json"), help='"none" = no filtering')
    ap.add_argument("--variant", default="trans")
    ap.add_argument("--form", default="bb")
    ap.add_argument("--boot", type=int, default=500)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    key = f"{args.variant}_{args.form}"
    J = {} if args.judgments == "none" else json.load(open(args.judgments))
    jname = "none" if args.judgments == "none" else ("native" if "native" in os.path.basename(args.judgments) else "old")
    rng = np.random.default_rng(args.seed)

    # ---------- load: one row per poison x corpus ----------
    rows, runs = [], {}
    n_missing_dens = 0
    for p in sorted(glob.glob(os.path.join(D, "*", "*_s*.npz"))):
        m = re.match(r"(full|\d+)_(full|keep|nokeep|article)_s(\d+)\.npz$", os.path.basename(p))
        lang = os.path.basename(os.path.dirname(p))
        if not m or lang not in LANGS:
            continue
        size, mode, seed = m.group(1), m.group(2), int(m.group(3))
        z = np.load(p)
        if f"{key}_items" not in z:
            continue
        dp = p[:-4] + "_dens.npz"
        dz = np.load(dp) if os.path.exists(dp) else None
        n_missing_dens += dz is None
        qids, idx = z["qids"], z[f"{key}_items"]
        keep = np.array([J.get(lang, {}).get(str(qids[j]), {}).get("label") != "bad" for j in idx])
        r = {"corpus": int(z["corpus"]), "n": int(keep.sum())}
        P = {}
        for f in FEATS:
            P[f] = pct(-z[f"{key}_pois_{f}"], -z[f"{key}_match_{f}"])
            r[f] = float(P[f][keep].mean())
        if dz is not None:
            assert np.array_equal(dz[f"{key}_items"], idx)
            r["n_ga10"] = float(dz[f"{key}_n_goldart_top10"][keep].mean())
            r["top1_ga"] = float(dz[f"{key}_top1_goldart"][keep].mean())
            r["gold_in"] = float(dz[f"{key}_gold_in_corpus"][keep].mean())
            for t in np.flatnonzero(keep):
                rows.append({"lang": lang, "item": int(idx[t]), "size": size, "mode": mode, "seed": seed,
                             "logN": np.log10(z["corpus"]), "n_ga10": float(dz[f"{key}_n_goldart_top10"][t]),
                             "top1_ga": float(dz[f"{key}_top1_goldart"][t]),
                             **{f"p_{f}": float(P[f][t]) for f in FEATS}})
        runs[(lang, size, mode, seed)] = r
    if not runs:
        raise SystemExit(f"no results under {D}; run scale_seeds.py first")
    seeds = sorted({k[3] for k in runs})
    sizes = sorted({k[1] for k in runs}, key=lambda s: -float("inf") if s == "full" else -int(s))

    L = [f"# Detection difficulty: corpus size vs local density ({args.variant}/{args.form}, judgments {jname}, seeds {seeds})", "",
         "Modes: keep = random subset + all dev gold passages; article = random subset + all passages of the gold articles; "
         "nokeep = random subset only. All three use the same random subset for a given seed.", ""]
    if n_missing_dens:
        L += [f"Warning: {n_missing_dens} results lack a local-density file (*_dens.npz) and are excluded from sections 2-4. Re-running scale_seeds.py adds them.", ""]

    # ---------- 1. AUROC ----------
    for f in FEATS:
        L += [f"## 1. AUROC ({f}, vs length-matched): mean +/- s.d. across seeds; in brackets the paired drop relative to the full corpus", "",
              "| lang | size | " + " | ".join(MODES) + " |", "|---|---|" + "---|" * len(MODES)]
        for lang in LANGS:
            for size in sizes:
                if size == "full":
                    a = [runs[(lang, "full", "full", s)][f] for s in seeds if (lang, "full", "full", s) in runs]
                    if a:
                        L.append(f"| {lang} | full | {ms(a)} |" + " |" * (len(MODES) - 1))
                    continue
                cells = []
                for mode in MODES:
                    ks = [s for s in seeds if (lang, size, mode, s) in runs]
                    a = [runs[(lang, size, mode, s)][f] for s in ks]
                    d = [runs[(lang, size, mode, s)][f] - runs[(lang, "full", "full", s)][f]
                         for s in ks if (lang, "full", "full", s) in runs]
                    n_c = np.mean([runs[(lang, size, mode, s)]["corpus"] for s in ks]) if ks else 0
                    cells.append("—" if not a else f"{ms(a)} (delta {ms(d)}; {n_c:,.0f} passages)")
                if any(c != "—" for c in cells):
                    L.append(f"| {lang} | {size_label(size)} | " + " | ".join(cells) + " |")
        L.append("")

    # ---------- 2. local density ----------
    L += ["## 2. Local density: number of the poison's top-10 neighbours from the question's gold article (in brackets: share whose nearest neighbour is from the gold article)", "",
          "| lang | size | " + " | ".join(MODES) + " |", "|---|---|" + "---|" * len(MODES)]
    for lang in LANGS:
        for size in sizes:
            ms_ = ["full"] if size == "full" else MODES
            cells = []
            for mode in ms_:
                v = [runs[(lang, size, mode, s)] for s in seeds if (lang, size, mode, s) in runs and "n_ga10" in runs[(lang, size, mode, s)]]
                cells.append("—" if not v else f"{np.mean([x['n_ga10'] for x in v]):.2f} ({np.mean([x['top1_ga'] for x in v]):.0%})")
            if any(c != "—" for c in cells):
                L.append(f"| {lang} | {size_label(size)} | " + " | ".join(cells) + (" |" * (len(MODES) - 1) if size == "full" else "") + " |")
    L.append("")

    # ---------- 3. within-question regression ----------
    if rows:
        L += ["## 3. Within-question regression: suspicion percentile ~ log10(corpus size) + local density (question fixed effects, cluster bootstrap 95% CI)", "",
              "log10(size) coefficient = change in percentile for a tenfold larger corpus (positive = larger corpora are easier); "
              "local-density coefficient = change in percentile per additional gold-article passage among the top-10 neighbours (negative = denser is harder). "
              "'alone' = only that variable in the model; 'joint' = both variables.", "",
              "| feature | lang | obs | log10(size): alone | log10(size): joint | local density: alone | local density: joint |",
              "|---|---|---|---|---|---|---|"]
        fmtc = lambda e, lo, hi: f"{e:+.3f} ({lo:+.3f}, {hi:+.3f})"
        for f in FEATS:
            for lang in LANGS + ["pooled"]:
                sub = [r for r in rows if lang == "pooled" or r["lang"] == lang]
                if len(sub) < 30:
                    continue
                y = np.array([r[f"p_{f}"] for r in sub])
                g = np.array([f"{r['lang']}|{r['item']}" for r in sub])
                xN = np.array([[r["logN"]] for r in sub]); xD = np.array([[r["n_ga10"]] for r in sub])
                eN = cluster_boot(y, xN, g, args.boot, rng)
                eD = cluster_boot(y, xD, g, args.boot, rng)
                eB = cluster_boot(y, np.hstack([xN, xD]), g, args.boot, rng)
                L.append(f"| {f} | {lang} | {len(sub):,} | {fmtc(eN[0][0], eN[1][0], eN[2][0])} | "
                         f"{fmtc(eB[0][0], eB[1][0], eB[2][0])} | {fmtc(eD[0][0], eD[1][0], eD[2][0])} | "
                         f"{fmtc(eB[0][1], eB[1][1], eB[2][1])} |")
        L += ["", "For 'pooled', fixed effects are by language x question, so differences between languages are absorbed; only changes of the same poison across corpora are compared.", ""]

        # ---------- 4. stratified ----------
        L += ["## 4. Stratified by local density: does corpus size still matter? (mean rel_knn10 percentile, four languages pooled)", "",
              "| local density (gold-article passages in top-10) | " + " | ".join(size_label(s) for s in sizes) + " |",
              "|---|" + "---|" * len(sizes)]
        bins = [(0, 0, "0"), (1, 2, "1-2"), (3, 10, "3 or more")]
        for lo, hi, name in bins:
            cells = []
            for size in sizes:
                v = [r["p_rel_knn10"] for r in rows if r["size"] == size and lo <= r["n_ga10"] <= hi]
                cells.append(f"{np.mean(v):.3f} ({len(v)})" if len(v) >= 20 else "—")
            L.append(f"| {name} | " + " | ".join(cells) + " |")
        L += ["", "Numbers in brackets are observations (poison x mode x seed). A flat row means corpus size no longer matters at equal density."]

    suffix = "" if jname == "native" else f"_{jname}"
    out = os.path.join(D, f"density{suffix}.md")
    open(out, "w").write("\n".join(L) + "\n")
    print("\n".join(L)); print(f"\nsaved {out}")


if __name__ == "__main__":
    main()
