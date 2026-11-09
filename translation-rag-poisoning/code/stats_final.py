"""
Statistical fixes for review items P0-2 / P0-3 (CPU only, one or two minutes).
  1. paired test of the defense effect: pairs "attack succeeds -> fails after defense" on the same question; exact McNemar (two-sided),
     paired bootstrap 95% CI of the difference (percentage points), Holm correction for multiple comparisons (primary family = trans/bb of the 4 languages;
     secondary family = bb of 4 languages x 3 variants)
  2. clean-correct subset: only questions answered correctly without attack, removing questions that "could not be answered anyway" from ASR
  3. yo original (8) vs added (18) questions, stratified: clean accuracy, hit@5, detection AUROC / TPR@5%, ASR
    python stats_final.py                     # native judgments
    python stats_final.py --set none          # no exclusion
Output: results/miracl/stats_final[_none].md
"""
import argparse, json, math, os

import numpy as np

PROJ = os.environ.get("PROJ", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
R = os.path.join(PROJ, "results", "miracl")
LANGS = ["sw", "te", "yo", "id"]
VARIANTS = ["trans", "native", "en"]


def mcnemar_exact(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    p = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * p)


def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    adj, run = [0.0] * len(ps), 0.0
    for r, i in enumerate(order):
        run = max(run, min(1.0, (len(ps) - r) * ps[i]))
        adj[i] = run
    return adj


def auc(pos, neg):
    neg = np.sort(neg)
    lo, hi = np.searchsorted(neg, pos, "left"), np.searchsorted(neg, pos, "right")
    return float(np.mean((lo + (hi - lo) / 2) / len(neg)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="native", choices=["native", "none"])
    ap.add_argument("--boot", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)
    rows = [json.loads(l) for l in open(os.path.join(R, "rejudge", a.set, "asr_answers_excl-bad.jsonl"))]
    asr = lambda r: bool(r["hit_target"]) and not r["hit_correct"]
    idx = {(r["lang"], r["cond"], r["variant"], r["form"], r["qid"]): r for r in rows}

    def pairs(lang, v, f, cond_b="defended", keep=None):
        out = []
        for (l, c, vv, ff, q), r in idx.items():
            if l == lang and c == "attacked" and vv == v and ff == f and (keep is None or keep(q)):
                d = idx.get((l, cond_b, vv, ff, q))
                if d:
                    out.append((asr(r), asr(d)))
        return out

    L = [f"# Statistical fixes (judgments: {a.set})", "",
         "## 1. Paired test of the defense effect (attacked -> realistic defense, paired by question)", "",
         "b = attack succeeds, fails after defense; c = attack fails, succeeds after defense. p is exact McNemar (two-sided); "
         "Holm correction: primary family = trans/bb of the 4 languages, secondary family = 12 language x variant (bb).", "",
         "| lang | variant | questions | attacked | defended | difference (pp, 95% CI) | b / c | p | Holm p (primary) | Holm p (12) |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    res = []
    for v in VARIANTS:
        for lg in LANGS:
            P = pairs(lg, v, "bb")
            if not P:
                continue
            x = np.array([p[0] for p in P], float); y = np.array([p[1] for p in P], float)
            b = int(((x == 1) & (y == 0)).sum()); c = int(((x == 0) & (y == 1)).sum())
            bs = [(y[i] - x[i]).mean() for i in (rng.integers(0, len(x), len(x)) for _ in range(a.boot))]
            res.append({"lang": lg, "v": v, "n": len(x), "att": x.mean(), "dfd": y.mean(), "d": (y - x).mean(),
                        "ci": np.percentile(bs, [2.5, 97.5]), "b": b, "c": c, "p": mcnemar_exact(b, c)})
    prim = [r for r in res if r["v"] == "trans"]
    for r, h in zip(prim, holm([r["p"] for r in prim])):
        r["holm1"] = h
    for r, h in zip(res, holm([r["p"] for r in res])):
        r["holm12"] = h
    for r in res:
        L.append(f"| {r['lang']} | {r['v']} | {r['n']} | {r['att']:.2f} | {r['dfd']:.2f} | "
                 f"{100 * r['d']:+.1f} ({100 * r['ci'][0]:+.1f}, {100 * r['ci'][1]:+.1f}) | {r['b']} / {r['c']} | "
                 f"{r['p']:.4f} | {r.get('holm1', float('nan')):.4f} | {r['holm12']:.4f} |".replace("| nan |", "| — |"))
    L += ["", "Wording: only Holm-corrected p < 0.05 is called a 'significant reduction'; the rest are 'reductions in the same direction (not significant)' with absolute question counts.", ""]

    # ---- 2. clean-correct subset ----
    L += ["## 2. Only questions answered correctly under clean (removing questions that could not be answered anyway)", "",
          "| lang | variant | all: questions / attacked / defended | clean-correct: questions / attacked / defended |", "|---|---|---|---|"]
    for v in VARIANTS:
        for lg in LANGS:
            ok = {q for (l, c, vv, ff, q), r in idx.items() if l == lg and c == "clean" and r["hit_correct"]}
            P1, P2 = pairs(lg, v, "bb"), pairs(lg, v, "bb", keep=lambda q: q in ok)
            if P1:
                f = lambda P: f"{len(P)} / {np.mean([p[0] for p in P]):.2f} / {np.mean([p[1] for p in P]):.2f}" if P else "—"
                L.append(f"| {lg} | {v} | {f(P1)} | {f(P2)} |")
    L.append("")

    # ---- 3. yo original vs added questions ----
    items = [json.loads(l) for l in open(os.path.join(R, "yo", "poison.jsonl"))]
    J = json.load(open(os.path.join(R, "review_judgments_native.json")))["yo"] if a.set == "native" else {}
    is_new = {it["qid"]: it.get("batch") == "yo_expand_2026-10-29" for it in items}
    valid = {it["qid"] for it in items if J.get(it["qid"], {}).get("label") != "bad"}
    detail = [json.loads(l) for l in open(os.path.join(R, "yo", "attack_detail.jsonl"))]
    z = np.load(os.path.join(R, "yo", "detect_feats.npz"))
    pos = {r: i for i, r in enumerate(z["clean_rows"])}
    thr = float(np.quantile(-z["clean_rel_knn10"][[pos[r] for r in z["rand"]]], 0.95))
    has = [j for j, it in enumerate(items) if it.get("trans_adv")]
    sm = -z["clean_rel_knn10"][[pos[r] for r in z["trans_bb_match"]]]
    L += ["## 3. yo: original and added questions, stratified (trans/bb)", "",
          "| subset | valid questions | clean accuracy | hit@5 | AUROC (rel_knn10) | TPR@5% | attacked ASR | defended ASR |",
          "|---|---|---|---|---|---|---|---|"]
    for name, sel in [("original", lambda q: not is_new[q]), ("added", lambda q: is_new[q]), ("pooled", lambda q: True)]:
        qs = {q for q in valid if sel(q)}
        sp = np.array([-z["trans_bb_rel_knn10"][k] for k, j in enumerate(has) if items[j]["qid"] in qs])
        hit = [bool(detail[j].get("full/trans/bb/single/hit5")) for j in has if items[j]["qid"] in qs]
        cl = [r["hit_correct"] for (l, c, vv, ff, q), r in idx.items() if l == "yo" and c == "clean" and q in qs]
        P = pairs("yo", "trans", "bb", keep=lambda q: q in qs)
        L.append(f"| {name} | {len(qs)} | {np.mean(cl):.2f} | {np.mean(hit):.2f} | {auc(sp, sm):.3f} | "
                 f"{np.mean(sp > thr):.2f} | {np.mean([p[0] for p in P]):.2f} ({sum(p[0] for p in P)}/{len(P)}) | "
                 f"{np.mean([p[1] for p in P]):.2f} ({sum(p[1] for p in P)}/{len(P)}) |")
    L += ["", "Added and original questions were generated with different model precision (AWQ vs unquantised), so differences cannot be attributed directly; the paper reports strata and notes this for pooled conclusions."]
    out = os.path.join(R, f"stats_final{'' if a.set == 'native' else '_' + a.set}.md")
    open(out, "w").write("\n".join(L) + "\n")
    print("\n".join(L)); print(f"\nsaved {out}")


if __name__ == "__main__":
    main()
