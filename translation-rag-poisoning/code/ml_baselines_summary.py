"""
Statistics of the defense-baseline comparison (CPU only). Reads the output of ml_baselines.py.
    python ml_baselines_summary.py                          # native-speaker judgments
    python ml_baselines_summary.py --judgments none         # no filtering
Output: results/miracl/baselines/summary[_<judgments>].md
Tables (per language x poison variant, form bb; all methods use the same poisons and the same benign passages)
  A. AUROC (poison vs length-matched benign), 95% CI from bootstrapping poisoned questions in brackets
  B. TPR@5%FPR: threshold at the 95% quantile of random benign scores
  C. Surviving-poison rate: poison in the top-5 (full corpus, one injected per question) and not flagged by the method
"""
import argparse, json, os

import numpy as np

PROJ = os.environ.get("PROJ", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
R = os.path.join(PROJ, "results", "miracl")
D = os.path.join(R, "baselines")
LANGS = ["sw", "te", "yo", "id"]
VARIANTS = ["trans", "native", "en"]
METHODS = [("rel_knn10", "rel_knn10 (ours)"), ("knn10", "knn10 (ours)"), ("lof_knn10", "LOF"),
           ("maha", "Mahalanobis"), ("iforest", "Isolation Forest"), ("ppl_low", "perplexity, low suspicious"),
           ("ppl_high", "perplexity, high suspicious"), ("judge", "LLM judge (no evidence)"), ("evidence", "evidence check (LLM + retrieved evidence)")]


def auc(pos, neg):
    neg = np.sort(neg)
    lo, hi = np.searchsorted(neg, pos, "left"), np.searchsorted(neg, pos, "right")
    return float(np.mean((lo + (hi - lo) / 2) / len(neg)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--judgments", default=os.path.join(R, "review_judgments_native.json"), help='"none" = no filtering')
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    J = {} if args.judgments == "none" else json.load(open(args.judgments))
    jname = "none" if args.judgments == "none" else ("native" if "native" in os.path.basename(args.judgments) else "old")
    rng = np.random.default_rng(args.seed)

    res = []
    for lang in LANGS:
        p = os.path.join(D, f"{lang}.npz")
        if not os.path.exists(p):
            continue
        z = dict(np.load(p))
        pe = os.path.join(D, f"{lang}_evidence.npz")          # evidence-check baseline (ml_baselines_evidence.py) merged if present
        if os.path.exists(pe):
            z.update(dict(np.load(pe)))
        neg_rows = z["neg_rows"]
        ri = np.searchsorted(neg_rows, z["rand"])
        detail = [json.loads(l) for l in open(os.path.join(R, lang, "attack_detail.jsonl"))]
        qids = z["qids"]
        for v in VARIANTS:
            if f"{v}_items" not in z:
                continue
            idx = z[f"{v}_items"]
            keep = np.array([J.get(lang, {}).get(str(qids[j]), {}).get("label") != "bad" for j in idx])
            mi = np.searchsorted(neg_rows, z[f"match_{v}"])
            hk = f"full/{v}/bb/single/hit5"
            hit = np.array([bool(detail[j].get(hk, False)) for j in idx])[keep]
            row = {"lang": lang, "variant": v, "n": int(keep.sum()), "hit": float(hit.mean())}
            for m, _ in METHODS:
                if f"{v}_{m}" not in z or f"neg_{m}" not in z:
                    continue
                sp = z[f"{v}_{m}"][keep].astype(float)
                sn = z[f"neg_{m}"].astype(float)
                ok = ~np.isnan(sp)
                sp = sp[ok]
                sm, sr = sn[mi], sn[ri]
                sm, sr = sm[~np.isnan(sm)], sr[~np.isnan(sr)]
                thr = float(np.quantile(sr, 0.95))
                thr1 = float(np.quantile(sr, 0.99))
                flag = sp > thr
                bs = [auc(sp[rng.integers(0, len(sp), len(sp))], sm) for _ in range(args.boot)]
                row[m] = {"auc": auc(sp, sm), "ci": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
                          "tpr5": float(flag.mean()), "tpr1": float((sp > thr1).mean()),
                          "eff": float((hit[ok] & ~flag).mean()), "n_neg": int(len(sm))}
            res.append(row)
    if not res:
        raise SystemExit(f"no results under {D}; run ml_baselines.py first")

    have = [(m, n) for m, n in METHODS if any(m in r for r in res)]
    head = "| lang | variant | questions | " + " | ".join(n for _, n in have) + " |"
    sep = "|---|---|---|" + "---|" * len(have)
    L = [f"# Ingestion-time detection vs baseline methods (form bb, judgments {jname})", "",
         "All methods use the same poisons and the same benign passages (2000 random benign for thresholds, 1000 length-matched benign for AUROC). "
         "Perplexity and the LLM judge both use Qwen3-14B-AWQ. The best method per row is in bold.", ""]

    def best(r, key):
        vals = {m: r[m][key] for m, _ in have if m in r}
        return max(vals, key=vals.get) if key != "eff" else min(vals, key=vals.get)

    for title, key, fmt in [("A. AUROC (vs length-matched benign passages, higher is better)", "auc",
                             lambda x: f"{x['auc']:.3f} ({x['ci'][0]:.2f}–{x['ci'][1]:.2f})"),
                            ("B. TPR@5%FPR (higher is better)", "tpr5", lambda x: f"{x['tpr5']:.2f}"),
                            ("B2. TPR@1%FPR (higher is better; granularity 1/n with few poisons)", "tpr1", lambda x: f"{x['tpr1']:.2f}"),
                            ("C. Surviving-poison rate (5% FPR, lower is better)", "eff", lambda x: f"{x['eff']:.2f}")]:
        L += [f"## {title}", "", head, sep]
        for r in res:
            b = best(r, key)
            cells = [("**" + fmt(r[m]) + "**" if m == b else fmt(r[m])) if m in r else "—" for m, _ in have]
            L.append(f"| {r['lang']} | {r['variant']} | {r['n']} | " + " | ".join(cells) + " |")
        L.append("")
    L += ["hit@5 before filtering, for table C: " + ", ".join(f"{r['lang']}/{r['variant']} {r['hit']:.2f}" for r in res), "",
          "Both perplexity directions are listed because it is not known in advance whether poison (generated / machine-translated) has higher or lower perplexity; "
          "compare using a direction fixed in advance, not by picking the better-looking column.",
          "The evidence check scored only a subset of benign passages (1000 random for thresholds, 500 length-matched per variant); the other methods use all benign passages. "
          "It is a factual-consistency check with retrieved evidence, distinct from the LLM judge without evidence."]
    suffix = "" if jname == "native" else f"_{jname}"
    out = os.path.join(D, f"summary{suffix}.md")
    open(out, "w").write("\n".join(L) + "\n")
    json.dump(res, open(os.path.join(D, f"summary{suffix}.json"), "w"), indent=1, ensure_ascii=False)
    print("\n".join(L)); print(f"\nsaved {out}")


if __name__ == "__main__":
    main()
