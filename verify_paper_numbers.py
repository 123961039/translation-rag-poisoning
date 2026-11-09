"""Recompute the key numbers reported in the paper from the FINAL result files and check them.

    python verify_paper_numbers.py            # CPU only, a few seconds; exits 1 on any mismatch

Only files listed in FINAL_RESULTS_MANIFEST.md are read.
"""
import json, math, os, re, sys

import numpy as np

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results", "miracl")
LANGS = ["sw", "te", "yo", "id"]
fails = 0


def check(name, got, want, tol=0.005):
    global fails
    ok = abs(got - want) <= tol
    fails += not ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got:.4f}, paper {want}")


def mcnemar(b, c):
    n = b + c
    return 1.0 if n == 0 else min(1.0, 2 * sum(math.comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n)


def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    out, run = [0.0] * len(ps), 0.0
    for r, i in enumerate(order):
        run = max(run, min(1.0, (len(ps) - r) * ps[i]))
        out[i] = run
    return out


# ---------- generation level (Table III, Fig. ASR) ----------
ans = {}
for line in open(os.path.join(R, "rejudge/native/asr_answers_excl-bad.jsonl")):
    r = json.loads(line)
    ans[(r["lang"], r["cond"], r["variant"], r["form"], r["qid"])] = r
succ = lambda r: bool(r["hit_target"]) and not bool(r["hit_correct"])

paper_asr = {"sw": (0.28, 0.26), "te": (0.15, 0.08), "yo": (0.50, 0.19), "id": (0.32, 0.21)}
paper_clean = {"sw": (0.83, 0.83), "te": (0.92, 0.85), "yo": (0.69, 0.62), "id": (0.64, 0.64)}
prim_p, total_pairs, total_c = [], 0, 0
for lang in LANGS:
    qs = sorted({k[4] for k in ans if k[:4] == (lang, "attacked", "trans", "bb")})
    a = [succ(ans[(lang, "attacked", "trans", "bb", q)]) for q in qs]
    d = [succ(ans[(lang, "defended", "trans", "bb", q)]) for q in qs]
    check(f"{lang} trans/bb ASR attacked", np.mean(a), paper_asr[lang][0])
    check(f"{lang} trans/bb ASR defended", np.mean(d), paper_asr[lang][1])
    b = sum(x and not y for x, y in zip(a, d)); c = sum(y and not x for x, y in zip(a, d))
    prim_p.append(mcnemar(b, c))
    cq = sorted({k[4] for k in ans if k[:2] == (lang, "clean")})
    check(f"{lang} clean acc", np.mean([ans[(lang, "clean", "-", "-", q)]["hit_correct"] for q in cq]), paper_clean[lang][0])
    check(f"{lang} clean acc defended", np.mean([ans[(lang, "clean_defended", "-", "-", q)]["hit_correct"] for q in cq]),
          paper_clean[lang][1])
for v in ("trans", "native", "en"):
    for lang in LANGS:
        qs = sorted({k[4] for k in ans if k[:4] == (lang, "attacked", v, "bb")})
        total_pairs += len(qs)
        total_c += sum(succ(ans[(lang, "defended", v, "bb", q)]) and not succ(ans[(lang, "attacked", v, "bb", q)])
                       for q in qs)
check("Holm p (primary family) yo", holm(prim_p)[2], 0.0312, tol=0.0005)
check("paired cases (12 settings)", total_pairs, 408, tol=0)
check("new successes introduced (c)", total_c, 0, tol=0)

fp = json.load(open(os.path.join(R, "rejudge/native/asr_summary_excl-bad.json")))["fp_stats"]
for lang, want in zip(LANGS, ["1/66", "3/52", "2/34", "0/39"]):
    got = f"{fp[lang]['gold_flagged']}/{fp[lang]['gold_in_topk']}"
    fails += got != want
    print(f"[{'PASS' if got == want else 'FAIL'}] {lang} gold removed: got {got}, paper {want}")

# ---------- detector benchmark (Table II) ----------
B = json.load(open(os.path.join(R, "baselines/summary.json")))
want = {"rel_knn10": (0.867, 0.503, 0.228), "knn10": (0.815, 0.376, 0.123), "lof_knn10": (0.818, 0.356, 0.119),
        "maha": (0.791, 0.328, 0.108), "iforest": (0.620, 0.081, 0.008), "judge": (0.640, 0.166, 0.062),
        "evidence": (0.926, 0.629, 0.297)}
for m, (au, t5, t1) in want.items():
    check(f"{m} mean AUROC", np.mean([r[m]["auc"] for r in B]), au, tol=0.0015)
    check(f"{m} mean TPR@5%", np.mean([r[m]["tpr5"] for r in B]), t5, tol=0.0015)
    check(f"{m} mean TPR@1%", np.mean([r[m]["tpr1"] for r in B]), t1, tol=0.0015)
others = ["knn10", "lof_knn10", "maha", "iforest"]
check("rel_knn10 best distance/density AUROC (of 12)",
      sum(r["rel_knn10"]["auc"] >= max(r[m]["auc"] for m in others) for r in B), 9, tol=0)

# ---------- scale (Fig. scale) ----------
S = json.load(open(os.path.join(R, "scale_seeds/summary.json")))
mean_auc = lambda lang, size, mode, f: np.mean([v[f]["auc"] for k, v in S.items() if k.startswith(f"{lang}|{size}|{mode}|")])
for lang, keep, nokeep in (("sw", -0.108, -0.027), ("te", -0.110, -0.036), ("id", -0.240, -0.110)):
    full = mean_auc(lang, "full", "full", "rel_knn10")
    check(f"{lang} rel_knn10 drop to 45k (keep)", mean_auc(lang, "45000", "keep", "rel_knn10") - full, keep, tol=0.002)
    check(f"{lang} rel_knn10 drop to 45k (nokeep)", mean_auc(lang, "45000", "nokeep", "rel_knn10") - full, nokeep, tol=0.002)

# ---------- AUROC vs TPR disagreement (Fig. gap) ----------
for fn, want_n in (("metric_gap.json", 1), ("metric_gap_sub45000.json", 4)):
    rows = json.load(open(os.path.join(R, "rejudge/native", fn)))["rows"]
    check(f"{fn} disagreements (of 24)", sum(r["verdict"]["5"] != "yes" for r in rows), want_n, tol=0)

# ---------- 2x2 density (Fig. density) ----------
txt = open(os.path.join(R, "density_2x2/summary.md"), encoding="utf-8").read()
pooled = re.findall(r"\| pooled \(languages equally weighted\) \| \| \| \| \| ([-+]\d\.\d+) \| ([-+]\d\.\d+) \|", txt)
check("rel_knn10 pooled density effect @20k", float(pooled[0][0]), 0.038, tol=0.0005)
check("knn10 pooled density effect @20k", float(pooled[1][0]), -0.112, tol=0.0005)
check("knn10 pooled density effect @45k", float(pooled[1][1]), -0.094, tol=0.0005)

# ---------- HNSW (Table hnsw) ----------
H = lambda lang, size: json.load(open(os.path.join(R, "hnsw", f"hnsw_{lang}_{size}.json")))
for lang, key, want_rec, want_dauc, want_dtpr1 in (("te", "hnsw_M16_ef16", 0.888, -0.015, -0.25),
                                                    ("id", "hnsw_M16_ef16", 0.898, -0.062, -0.07),
                                                    ("te", "hnsw_M32_ef256", 0.979, 0.000, 0.00)):
    r = H(lang, "full"); h, e = r["combos"][key]["trans_bb"]["rel_knn10"], r["combos"]["exact"]["trans_bb"]["rel_knn10"]
    check(f"HNSW {lang} {key} recall@10", r["index"][key]["recall10"], want_rec, tol=0.0006)
    check(f"HNSW {lang} {key} dAUROC rel", h["auroc"] - e["auroc"], want_dauc, tol=0.0006)
    check(f"HNSW {lang} {key} dTPR@1% rel", h["tpr1"] - e["tpr1"], want_dtpr1, tol=0.006)
mx = max(abs(r["combos"]["hnsw_M32_ef256"][c][f]["auroc"] - r["combos"]["exact"][c][f]["auroc"])
         for r in (H(l, s) for l in LANGS for s in ("full", "45000")) for c in r["combos"]["exact"] for f in ("knn10", "rel_knn10"))
check("HNSW M32/ef256 max |dAUROC| all settings", mx, 0.005, tol=0.0006)

print(f"\n{'ALL CHECKS PASSED' if fails == 0 else f'{fails} CHECK(S) FAILED'}")
sys.exit(1 if fails else 0)
