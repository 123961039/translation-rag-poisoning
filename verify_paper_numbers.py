"""Recompute the key numbers reported in the paper from the FINAL result files and check them.

    python verify_paper_numbers.py            # CPU only, a few seconds; exits 1 on any mismatch

Only files listed in FINAL_RESULTS_MANIFEST.md are read.
"""
import json, math, os, re, sys

from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results", "miracl")
LANGS = ["sw", "te", "yo", "id"]
PAPER_COUNTS = {"sw": 47, "te": 52, "yo": 26, "id": 28}
fails = 0


def check(name, got, want, tol=0.005):
    global fails
    ok = abs(got - want) <= tol + 1e-12
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


# ---------- generation level (Table 7 and abstract) ----------
ans = {}
for line in open(os.path.join(R, "rejudge/native/asr_answers_excl-bad.jsonl")):
    r = json.loads(line)
    ans[(r["lang"], r["cond"], r["variant"], r["form"], r["qid"])] = r
succ = lambda r: bool(r["hit_target"]) and not bool(r["hit_correct"])

paper_asr = {"sw": (0.28, 0.26), "te": (0.15, 0.08), "yo": (0.50, 0.19), "id": (0.32, 0.21)}
paper_clean = {"sw": (0.83, 0.83), "te": (0.92, 0.85), "yo": (0.69, 0.62), "id": (0.64, 0.64)}
prim_p, total_pairs, total_c = [], 0, 0
strict_successes, clean_to_target = 0, 0
for lang in LANGS:
    qs = sorted({k[4] for k in ans if k[:4] == (lang, "attacked", "trans", "bb")})
    a = [succ(ans[(lang, "attacked", "trans", "bb", q)]) for q in qs]
    check(f"Abstract {lang} validated trans/bb questions", len(qs), PAPER_COUNTS[lang], tol=0)
    strict_successes += sum(a)
    clean_to_target += sum(
        success and bool(ans[(lang, "clean", "-", "-", q)]["hit_correct"])
        for q, success in zip(qs, a)
    )
    d = [succ(ans[(lang, "defended", "trans", "bb", q)]) for q in qs]
    check(f"{lang} trans/bb ASR attacked", np.mean(a), paper_asr[lang][0])
    check(f"{lang} trans/bb ASR defended", np.mean(d), paper_asr[lang][1])
    b = sum(x and not y for x, y in zip(a, d)); c = sum(y and not x for x, y in zip(a, d))
    prim_p.append(mcnemar(b, c))
    cq = sorted({k[4] for k in ans if k[:2] == (lang, "clean")})
    check(f"{lang} clean acc", np.mean([ans[(lang, "clean", "-", "-", q)]["hit_correct"] for q in cq]), paper_clean[lang][0])
    check(f"{lang} clean acc defended", np.mean([ans[(lang, "clean_defended", "-", "-", q)]["hit_correct"] for q in cq]),
          paper_clean[lang][1])
check("Abstract strict ASR successes (of 153)", strict_successes, 43, tol=0)
check("Abstract strict successes after a correct clean answer", clean_to_target, 32, tol=0)
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

# ---------- detector benchmark (Table 3) ----------
B = json.load(open(os.path.join(R, "baselines/summary.json")))
want = {"rel_knn10": (0.867, 0.503, 0.228), "knn10": (0.815, 0.376, 0.123), "lof_knn10": (0.818, 0.356, 0.119),
        "maha": (0.791, 0.328, 0.108), "iforest": (0.620, 0.081, 0.008), "judge": (0.640, 0.166, 0.062),
        "evidence": (0.926, 0.629, 0.297)}
for m, (au, t5, t1) in want.items():
    label = "kNN distance ratio" if m == "lof_knn10" else m
    check(f"{label} mean AUROC", np.mean([r[m]["auc"] for r in B]), au, tol=0.0015)
    check(f"{label} mean TPR@5%", np.mean([r[m]["tpr5"] for r in B]), t5, tol=0.0015)
    check(f"{label} mean TPR@1%", np.mean([r[m]["tpr1"] for r in B]), t1, tol=0.0015)
others = ["knn10", "lof_knn10", "maha", "iforest"]
check("rel_knn10 best distance/density AUROC (of 12)",
      sum(r["rel_knn10"]["auc"] >= max(r[m]["auc"] for m in others) for r in B), 9, tol=0)

# ---------- scale (Figure 3) ----------
S = json.load(open(os.path.join(R, "scale_seeds/summary.json")))
mean_auc = lambda lang, size, mode, f: np.mean([v[f]["auc"] for k, v in S.items() if k.startswith(f"{lang}|{size}|{mode}|")])
for lang, keep, nokeep in (("sw", -0.108, -0.027), ("te", -0.110, -0.036), ("id", -0.240, -0.110)):
    full = mean_auc(lang, "full", "full", "rel_knn10")
    check(f"{lang} rel_knn10 drop to 45k (keep)", mean_auc(lang, "45000", "keep", "rel_knn10") - full, keep, tol=0.002)
    check(f"{lang} rel_knn10 drop to 45k (nokeep)", mean_auc(lang, "45000", "nokeep", "rel_knn10") - full, nokeep, tol=0.002)

# ---------- AUROC vs TPR disagreement (Figure 4b) ----------
for fn, want_n in (("metric_gap.json", 1), ("metric_gap_sub45000.json", 4)):
    rows = json.load(open(os.path.join(R, "rejudge/native", fn)))["rows"]
    check(f"{fn} disagreements (of 24)", sum(r["verdict"]["5"] != "yes" for r in rows), want_n, tol=0)

# ---------- 2x2 density (Figure 4a) ----------
txt = open(os.path.join(R, "density_2x2/summary.md"), encoding="utf-8").read()
pooled = re.findall(r"\| pooled \(languages equally weighted\) \| \| \| \| \| ([-+]\d\.\d+) \| ([-+]\d\.\d+) \|", txt)
check("rel_knn10 pooled density effect @20k", float(pooled[0][0]), 0.038, tol=0.0005)
check("knn10 pooled density effect @20k", float(pooled[1][0]), -0.112, tol=0.0005)
check("knn10 pooled density effect @45k", float(pooled[1][1]), -0.094, tol=0.0005)

# ---------- held-out novelty LOF (Table 4) ----------
def novelty_metrics(z):
    held, rand, match, qids = (z[key] for key in ("held_rows", "rand_rows", "match_rows", "qids"))
    if (len(rand) != len(np.unique(rand)) or len(match) != len(np.unique(match))
            or not np.array_equal(held, np.union1d(rand, match))
            or len(qids) != len(np.unique(qids))):
        raise ValueError("Invalid held-out row sets or duplicate question IDs")
    ri, mi = np.searchsorted(held, rand), np.searchsorted(held, match)
    labels = np.r_[np.ones(len(qids)), np.zeros(len(match))]
    metrics = {}
    for method in ("standard_LOF", "knn10", "rel_knn10", "knn_distance_ratio"):
        scores = z[method]
        if scores.shape != (len(held) + len(qids),) or not np.isfinite(scores).all():
            raise ValueError(f"Invalid score array: {method}")
        pos = scores[len(held):]
        t1, t5 = np.quantile(scores[ri], [0.99, 0.95])
        metrics[method] = (
            roc_auc_score(labels, np.r_[pos, scores[mi]]),
            np.count_nonzero(pos > t1),
            np.count_nonzero(pos > t5),
        )
    return metrics


novelty_dir = Path(R) / "novelty_lof"
paper_novelty = {
    "yo": ((0.823, 1, 8), (0.863, 4, 13), (0.847, 4, 12)),
    "sw": ((0.631, 1, 5), (0.658, 4, 11), (0.726, 3, 10)),
    "te": ((0.748, 2, 17), (0.856, 6, 18), (0.893, 15, 28)),
    "id": ((0.650, 1, 5), (0.717, 1, 4), (0.818, 2, 9)),
}
total_hits = {"standard_LOF": 0, "rel_knn10": 0}
total_n = 0
for lang, expected in paper_novelty.items():
    with np.load(novelty_dir / f"{lang}.npz", allow_pickle=False) as z:
        metrics = novelty_metrics(z)
        n = len(z["qids"])
        total_n += n
        check(f"Table 4 {lang} candidates", n, PAPER_COUNTS[lang], tol=0)
        check(f"Table 4 {lang} random rows", len(z["rand_rows"]), 2000, tol=0)
        check(f"Table 4 {lang} matched rows", len(z["match_rows"]), 1000, tol=0)
        if lang == "yo":
            with np.load(novelty_dir / "yo_sklearn.npz", allow_pickle=False) as reference:
                for field in ("held_rows", "rand_rows", "match_rows", "qids"):
                    check(f"Yoruba sklearn {field} alignment", np.array_equal(z[field], reference[field]), 1, tol=0)
                ref_metrics = novelty_metrics(reference)
            for method, (auc, h1, h5) in metrics.items():
                ref_auc, ref_h1, ref_h5 = ref_metrics[method]
                check(f"Yoruba sklearn {method} AUROC delta", auc - ref_auc, 0, tol=0.001)
                check(f"Yoruba sklearn {method} TPR@1% count", h1, ref_h1, tol=0)
                check(f"Yoruba sklearn {method} TPR@5% count", h5, ref_h5, tol=0)
        for method, (want_auc, want_h1, want_h5) in zip(("standard_LOF", "knn10", "rel_knn10"), expected):
            auc, h1, h5 = metrics[method]
            label = f"Table 4 {lang} {method}"
            check(f"{label} AUROC", auc, want_auc, tol=0.0005)
            check(f"{label} TPR@1% count (of {n})", h1, want_h1, tol=0)
            check(f"{label} TPR@5% count (of {n})", h5, want_h5, tol=0)
        for method in total_hits:
            total_hits[method] += metrics[method][2]
check("Table 4 pooled candidates", total_n, 153, tol=0)
check("Table 4 rel_knn10 TPR@5% count (of 153)", total_hits["rel_knn10"], 59, tol=0)
check("Table 4 standard novelty LOF TPR@5% count (of 153)", total_hits["standard_LOF"], 35, tol=0)


# ---------- paired GPU timings (Table 6, left block) ----------
def read_ingestion_log(path, default_lang=None):
    repetitions, results = {}, {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith(("rep=", "RESULT ")):
            continue
        fields = dict(field.split("=", 1) for field in line.removeprefix("RESULT ").split())
        cell = (fields.get("lang", default_lang), int(fields["batch"]))
        if line.startswith("RESULT "):
            if cell in results:
                raise ValueError(f"{path.name}: duplicate RESULT {cell}")
            results[cell] = fields
        else:
            rep = int(fields["rep"])
            rounds = repetitions.setdefault(cell, {})
            if rep in rounds:
                raise ValueError(f"{path.name}: duplicate round {rep} for {cell}")
            rounds[rep] = (float(fields["encode_s"]), float(fields["encode_screen_s"]))
    return repetitions, results


paper_overhead = {
    "yo": (5.37, 7.97, 1.82),
    "sw": (6.21, 8.77, 4.80),
    "te": (13.97, 10.41, 16.24),
    "id": (33.23, 22.81, 55.24),
}
paper_rate = {"yo": 856, "sw": 930, "te": 586, "id": 536}
batch_sizes = (1, 128, 1000)
timing_dir = Path(R) / "ingestion_distinct"
for filename, languages, default_lang in (
    ("id.log", ("id",), "id"),
    ("sw_te_yo.log", ("sw", "te", "yo"), None),
):
    reps, logged = read_ingestion_log(timing_dir / filename, default_lang)
    cells = {(lang, batch) for lang in languages for batch in batch_sizes}
    if set(reps) != cells or set(logged) != cells:
        raise ValueError(f"{filename}: unexpected timing cells")
    for lang in languages:
        for batch, n, paper_pct in zip(batch_sizes, (64, 896, 1000), paper_overhead[lang]):
            rounds = reps[lang, batch]
            if set(rounds) != set(range(1, 7)):
                raise ValueError(f"{filename}: expected rounds 1–6 for {lang} batch {batch}")
            base, full = np.array(list(rounds.values())).T
            label = f"Table 6 {lang} batch {batch}"
            result = logged[lang, batch]
            check(f"{label} passages per round", int(result["n"]), n, tol=0)
            pct = np.median(100 * (full / base - 1))
            # rep times have four decimals and the logged median has two.
            half_tick = 0.00005
            low = np.median(100 * ((full - half_tick) / (base + half_tick) - 1))
            high = np.median(100 * ((full + half_tick) / (base - half_tick) - 1))
            tol = max(pct - low, high - pct) + 0.005
            check(f"{label} paired overhead % (log)", pct, float(result["paired_overhead_pct"]), tol=tol)
            check(f"{label} paired overhead % (paper)", pct, paper_pct, tol=tol)
            if batch == 1000:
                rate = n / np.median(full)
                rate_tol = n / (np.median(full) - half_tick) - rate
                check(f"{label} screened docs/s (log)", rate, float(result["screened_docs_s"]), tol=rate_tol + 0.05)
                check(f"{label} screened docs/s (paper)", rate, paper_rate[lang], tol=rate_tol + 0.5)


# ---------- HNSW (Table 6, right block) ----------
H = lambda lang, size: json.load(open(os.path.join(R, "hnsw", f"hnsw_{lang}_{size}.json")))
paper_hnsw = {
    "yo": (0.15, 0.952, -0.08, 0.998, -0.04),
    "sw": (0.04, 0.967, -0.02, 0.998, 0.00),
    "te": (0.29, 0.888, -0.25, 0.979, 0.00),
    "id": (0.07, 0.898, -0.07, 0.974, -0.04),
}
for lang, (want_exact, rec16, delta16, rec32, delta32) in paper_hnsw.items():
    r = H(lang, "full")
    exact = r["combos"]["exact"]["trans_bb"]["rel_knn10"]["tpr1"]
    check(f"Table 6 {lang} exact TPR@1%", exact, want_exact)
    for key, recall, delta in (("hnsw_M16_ef16", rec16, delta16), ("hnsw_M32_ef256", rec32, delta32)):
        approx = r["combos"][key]["trans_bb"]["rel_knn10"]["tpr1"]
        check(f"Table 6 {lang} {key} recall@10", r["index"][key]["recall10"], recall, tol=0.0005)
        check(f"Table 6 {lang} {key} dTPR@1%", approx - exact, delta)
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
