"""
Evidence check vs rel_knn10: ablation and combination (CPU only).
On the benign passages actually scored by the evidence check (random AND checked for thresholds, length-matched AND checked for AUROC), compare:
  rel_knn10 | evidence check | evidence check w/o same article | rel_knn10 OR evidence | rel_knn10 OR evidence w/o same article
Combination: each score is mapped to its quantile among random benign passages, the maximum is taken (suspicious if either is), and 5% / 1% thresholds are set on random benign passages,
so the combined FPR equals that of a single method (a fair comparison).
    python evidence_combo.py                     # native-speaker judgments
    python evidence_combo.py --judgments none
Output: results/miracl/baselines/evidence_combo[_none].md
"""
import argparse, json, os

import numpy as np
from tqdm import tqdm

PROJ = os.environ.get("PROJ", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
R = os.path.join(PROJ, "results", "miracl")
D = os.path.join(R, "baselines")
LANGS = ["sw", "te", "yo", "id"]
VARIANTS = ["trans", "native", "en"]


def auc(pos, neg):
    neg = np.sort(neg)
    lo, hi = np.searchsorted(neg, pos, "left"), np.searchsorted(neg, pos, "right")
    return float(np.mean((lo + (hi - lo) / 2) / len(neg)))


def cdf(ref):
    ref = np.sort(ref)
    return lambda x: (np.searchsorted(ref, x, "left") + np.searchsorted(ref, x, "right")) / (2 * len(ref))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--judgments", default=os.path.join(R, "review_judgments_native.json"))
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    J = {} if a.judgments == "none" else json.load(open(a.judgments))
    jname = "none" if a.judgments == "none" else "native"
    rng = np.random.default_rng(0)
    cost = json.load(open(os.path.join(D, "evidence_cost.json"))) if os.path.exists(os.path.join(D, "evidence_cost.json")) else {}
    M = [("rel", "rel_knn10"), ("ev", "evidence"), ("evn", "evidence w/o same article"), ("rel|ev", "rel OR evidence"), ("rel|evn", "rel OR evidence w/o same article")]
    rows = []
    for lang in tqdm(LANGS, desc="languages"):
        z = dict(np.load(os.path.join(D, f"{lang}.npz")))
        for suf in ("evidence", "evidence_noart"):
            p = os.path.join(D, f"{lang}_{suf}.npz")
            if os.path.exists(p):
                z.update(dict(np.load(p)))
        if "neg_evidence_noart" not in z:
            continue
        detail = [json.loads(l) for l in open(os.path.join(R, lang, "attack_detail.jsonl"))]
        neg_rows, qids = z["neg_rows"], z["qids"]
        scored = ~np.isnan(z["neg_evidence"]) & ~np.isnan(z["neg_evidence_noart"])
        ri = np.searchsorted(neg_rows, z["rand"]); ri = ri[scored[ri]]
        for v in VARIANTS:
            if f"{v}_items" not in z:
                continue
            idx = z[f"{v}_items"]
            keep = np.array([J.get(lang, {}).get(str(qids[j]), {}).get("label") != "bad" for j in idx])
            mi = np.searchsorted(neg_rows, z[f"match_{v}"]); mi = mi[scored[mi]]
            hit = np.array([bool(detail[j].get(f"full/{v}/bb/single/hit5", False)) for j in idx])[keep]
            raw = {"rel": "rel_knn10", "ev": "evidence", "evn": "evidence_noart"}
            P = {k: z[f"{v}_{s}"][keep].astype(float) for k, s in raw.items()}
            ok = ~np.any([np.isnan(x) for x in P.values()], axis=0)
            P = {k: x[ok] for k, x in P.items()}; hit = hit[ok]
            N = {k: z[f"neg_{s}"].astype(float) for k, s in raw.items()}
            U = {k: (cdf(N[k][ri])(P[k]), cdf(N[k][ri])(N[k])) for k in raw}
            for c, (x, y) in (("rel|ev", ("rel", "ev")), ("rel|evn", ("rel", "evn"))):
                P[c] = np.maximum(U[x][0], U[y][0]); N[c] = np.maximum(U[x][1], U[y][1])
            r = {"lang": lang, "variant": v, "n": int(keep.sum()), "n_rand": int(len(ri)), "n_match": int(len(mi)),
                 "goldart": float(np.mean(z[f"{v}_goldart_in_ev"][keep])) if f"{v}_goldart_in_ev" in z else float("nan")}
            for k, _ in M:
                sp, sr, sm = P[k], N[k][ri], N[k][mi]
                t5, t1 = np.quantile(sr, 0.95), np.quantile(sr, 0.99)
                bs = [auc(sp[rng.integers(0, len(sp), len(sp))], sm) for _ in range(a.boot)]
                r[k] = {"auc": auc(sp, sm), "ci": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
                        "tpr5": float(np.mean(sp > t5)), "tpr1": float(np.mean(sp > t1)), "eff": float(np.mean(hit & ~(sp > t5)))}
            rows.append(r)
    if not rows:
        raise SystemExit("no *_evidence_noart.npz; run ml_evidence_ablation.py first")
    L = [f"# Evidence check: ablation and combination (form bb, judgments {jname})", "",
         "Only benign passages scored by the evidence check are used (random / length-matched counts listed per row), so rel_knn10 differs slightly from summary.md.",
         "'w/o same article': poison evidence excludes the gold article; benign evidence excludes the passage's own article. "
         "'OR': both scores mapped to quantiles among random benign passages, maximum taken, then thresholded; the total FPR is unchanged.", ""]
    head = "| lang | variant | questions | " + " | ".join(n for _, n in M) + " |"
    sep = "|---|---|---|" + "---|" * len(M)
    for title, key, fmt, better in [("A. AUROC", "auc", lambda x: f"{x['auc']:.3f} ({x['ci'][0]:.2f}–{x['ci'][1]:.2f})", max),
                                    ("B. TPR@5%FPR", "tpr5", lambda x: f"{x['tpr5']:.2f}", max),
                                    ("C. TPR@1%FPR", "tpr1", lambda x: f"{x['tpr1']:.2f}", max),
                                    ("D. Surviving-poison rate after filtering (5% FPR, lower is better)", "eff", lambda x: f"{x['eff']:.2f}", min)]:
        L += [f"## {title}", "", head, sep]
        for r in rows:
            b = better((k for k, _ in M), key=lambda k: r[k][key])
            L.append(f"| {r['lang']} | {r['variant']} | {r['n']} | " +
                     " | ".join(("**" + fmt(r[k]) + "**") if k == b else fmt(r[k]) for k, _ in M) + " |")
        L.append("")
    L += ["## E. Summary", "", "| metric | " + " | ".join(n for _, n in M) + " |", "|---|" + "---|" * len(M)]
    for key, nm in (("auc", "mean AUROC"), ("tpr5", "mean TPR@5%"), ("tpr1", "mean TPR@1%"), ("eff", "mean surviving-poison rate")):
        L.append(f"| {nm} | " + " | ".join(f"{np.mean([r[k][key] for r in rows]):.3f}" for k, _ in M) + " |")
    L += ["", "## F. Share of poisons whose top-5 evidence (original setting) contains a gold-article passage", "", "| lang | variant | share |", "|---|---|---|"]
    L += [f"| {r['lang']} | {r['variant']} | {r['goldart']:.2f} |" for r in rows]
    if cost:
        L += ["", "## G. Cost", "",
              f"Evidence check ({os.path.basename(cost['reader'])}, {cost['gpu']}): {cost['passages_per_sec']:.1f} passages/s, "
              f"mean prompt {cost['mean_prompt_tokens']:.0f} tokens ({cost['note']}).",
              "For comparison: rel_knn10 scores 10k-700k passages/s and encoding runs at 654-1,084 passages/s (efficiency.md).",
              "Benign passages left with fewer than 5 evidence passages after removing their own article: " + ", ".join(f"{l} {d['neg_short']}/{d['neg_n']}" for l, d in cost["diag"].items())]
    suffix = "" if jname == "native" else "_none"
    out = os.path.join(D, f"evidence_combo{suffix}.md")
    open(out, "w").write("\n".join(L) + "\n")
    print("\n".join(L)); print(f"\nsaved {out}")


if __name__ == "__main__":
    main()
