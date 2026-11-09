"""Recompute every annotation statistic reported in the paper from the released item-level records (CPU, seconds).

    python annotation/analyze_annotation.py            # writes annotation/results/recomputed.md and checks it

Inputs: annotation/data/*.csv (anonymized labels, one row per annotated item; see annotation/README.md) and,
for the Task C ASR breakdown, results/miracl/rejudge/native/asr_answers_excl-bad.jsonl.
Label values: y / n / ? (cannot decide) / partly. Each language has one native annotator.
"""
import collections, csv, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "data")
LANGS = ["sw", "te", "yo", "id"]
QC = ["Q1_translation_same", "Q2_passage_answers", "Q3_wrong_is_false", "Q4_same_type"]


def rows(name):
    return list(csv.DictReader(open(os.path.join(D, name), encoding="utf-8")))


def kappa(x, y):
    """Cohen's kappa treating every distinct label (including ?) as a category; returns (kappa, raw agreement)."""
    n = len(x)
    if n == 0:
        return float("nan"), float("nan")
    po = sum(a == b for a, b in zip(x, y)) / n
    pe = sum((x.count(c) / n) * (y.count(c) / n) for c in set(x) | set(y))
    return ((po - pe) / (1 - pe) if pe < 1 else float("nan")), po


def wilson(k, n, z=1.96):
    if n == 0:
        return float("nan"), float("nan")
    p = k / n; den = 1 + z * z / n; mid = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return mid - half, mid + half


fk = lambda k: "-" if k != k else f"{k:.2f}"
valid = lambda r: all(r[c] == "y" for c in QC)
label = lambda r: "ok" if valid(r) else ("bad" if any(r[c] == "n" for c in QC) else "unsure")
out = {}
L = ["# Annotation statistics recomputed from annotation/data/", ""]

# ---------------- Task A: question validity
A1, AY = rows("taskA_round1.csv"), rows("taskA_yo_expansion.csv")
L += ["## Task A: question validity (valid = all four criteria y)", "",
      "| lang | items | valid | share (95% CI) | fails Q1 / Q2 / Q3 / Q4 | kappa vs. LLM-assisted first pass (n) |", "|---|---|---|---|---|---|"]
for lg in LANGS:
    g = [r for r in A1 if r["lang"] == lg] + ([r for r in AY] if lg == "yo" else [])
    v = sum(map(valid, g)); lo, hi = wilson(v, len(g))
    fails = " / ".join(str(sum(r[c] == "n" for r in g)) for c in QC)
    both = [(r["first_pass_label"], label(r)) for r in g if r.get("first_pass_label") in ("ok", "bad") and label(r) in ("ok", "bad")]
    k, _ = kappa([a for a, _ in both], [b for _, b in both])
    out[f"A_valid_{lg}"] = (v, len(g))
    L.append(f"| {lg} | {len(g)} | {v} | {v / len(g):.0%} ({lo:.0%}-{hi:.0%}) | {fails} | {fk(k)} ({len(both)}) |")
L += ["", "yo includes the 52 expansion questions (no first-pass label). The paper's question filter "
      "(results/miracl/review_judgments_native.json) is derived from these labels: ok = all y, bad = any n, unsure otherwise.", ""]

# ---------------- Task B: naturalness (blind)
B1 = rows("taskB_round1.csv")
L += ["## Task B: share judged 'reads like a person wrote it' (blind; source hidden from the annotator)", "",
      "| lang | real Wikipedia | MT poison | LLM-written native poison |", "|---|---|---|---|"]
for lg in LANGS:
    cells = []
    for src in ("real_corpus", "mt", "native_llm"):
        g = [r["natural"] for r in B1 if r["lang"] == lg and r["source"] == src and r["natural"] in ("y", "n")]
        k = g.count("y"); out[f"B_{lg}_{src}"] = round(100 * k / len(g))
        cells.append(f"{k}/{len(g)} = {k / len(g):.0%}")
    L.append(f"| {lg} | " + " | ".join(cells) + " |")
L += ["", "The 'coherent' column of real passages is not used: real passages were truncated by word count when the sheets were built.", ""]

# ---------------- test-retest (round 2, about one week later, same annotator)
RA, RB = rows("taskA_retest.csv"), rows("taskB_retest.csv")
first_A = {r["item_id"]: r for r in A1}
first_B = {r["row_id"]: r for r in B1}
L += ["## Test-retest agreement (round 1 vs. round 2, same annotator)", "",
      "| lang | Task A items | Task A agreement | Task A kappa (valid) | Task B rows | Task B kappa (natural) |", "|---|---|---|---|---|---|"]
pa1, pa2 = [], []
for lg in LANGS:
    pr = [(first_A[r["round1_item_id"]], r) for r in RA if r["lang"] == lg and r["round1_item_id"] in first_A]
    v1 = ["ok" if valid(a) else "bad" for a, _ in pr]; v2 = ["ok" if valid(b) else "bad" for _, b in pr]
    pa1 += v1; pa2 += v2
    ka, po = kappa(v1, v2)
    pb = [(first_B[r["round1_row_id"]]["natural"], r["natural"]) for r in RB if r["lang"] == lg and r["round1_row_id"] in first_B]
    kb, _ = kappa([a for a, _ in pb], [b for _, b in pb])
    out[f"retestA_{lg}"], out[f"retestB_{lg}"] = round(ka, 2), round(kb, 2)
    L.append(f"| {lg} | {len(pr)} | {po:.0%} | {fk(ka)} | {len(pb)} | {fk(kb)} |")
ka, po = kappa(pa1, pa2); out["retestA_pooled"] = round(ka, 2)
L += [f"| pooled | {len(pa1)} | {po:.0%} | {fk(ka)} | | |", ""]

# ---------------- Task C: does the MT poison still state the target answer?
C = rows("taskC_translation_check.csv")
L += ["## Task C: translated poison still states the target (wrong) answer", "",
      "| lang | items | y | partly | n | ? | share y (95% CI) | strict string match: recall of y |", "|---|---|---|---|---|---|---|---|"]
for lg in LANGS:
    g = [r for r in C if r["lang"] == lg]; c = collections.Counter(r["states_wrong_answer"] for r in g)
    lo, hi = wilson(c["y"], len(g)); hy = [r for r in g if r["states_wrong_answer"] == "y"]
    rec = sum(r["auto_strict_match"] == "1" for r in hy) / len(hy)
    out[f"C_{lg}"] = (round(100 * c["y"] / len(g)), len(g))
    L.append(f"| {lg} | {len(g)} | {c['y']} | {c['partly']} | {c['n']} | {c['?']} | {c['y'] / len(g):.0%} ({lo:.0%}-{hi:.0%}) | {rec:.0%} |")
L += ["", "yo pools the original questions (round 2) and the 52 expansion questions.", ""]

# ---------------- Task D: verification of the automatic ASR judgment
T = rows("taskD_asr_check.csv")
auto = lambda r: r["auto_hit_target"] == "1" and r["auto_hit_correct"] == "0"
human = lambda r: r["says_wrong"] == "y" and r["says_correct"] != "y"
kw, _ = kappa([r["auto_hit_target"] == "1" for r in T], [r["says_wrong"] == "y" for r in T])
kc, _ = kappa([r["auto_hit_correct"] == "1" for r in T], [r["says_correct"] == "y" for r in T])
tp = [r for r in T if auto(r)]
out["D_kappa_wrong"], out["D_kappa_correct"] = round(kw, 2), round(kc, 2)
out["D_precision"] = round(100 * sum(map(human, tp)) / len(tp))
L += ["## Task D: automatic vs. human ASR judgment (stratified sample)", "",
      f"{len(T)} answers. kappa 'states the wrong answer' = {kw:.2f}; kappa 'states the correct answer' = {kc:.2f}; "
      f"precision of automatic successes = {sum(map(human, tp))}/{len(tp)} ({out['D_precision']}%); "
      f"automatic failures judged successes by humans: {sum(human(r) and not auto(r) for r in T)}.", "",
      "| lang | answers | agreement (strict ASR) |", "|---|---|---|"]
for lg in LANGS:
    g = [r for r in T if r["lang"] == lg]
    out[f"D_{lg}"] = (len(g), round(100 * sum(auto(r) == human(r) for r in g) / len(g)))
    L.append(f"| {lg} | {len(g)} | {out[f'D_{lg}'][1]}% |")
L += ["", "The sample is stratified by the automatic judgment (with partial matches oversampled), so these agreements "
      "describe each stratum and are not population accuracies.", ""]

open(os.path.join(HERE, "results", "recomputed.md"), "w").write("\n".join(L) + "\n")
print("\n".join(L))

# ---------------- the released question filter must follow from these labels
# round 1: ok = all y, bad = any n, unsure otherwise; yo expansion (merge_yo_new.py): ok = all y, bad otherwise
J = json.load(open(os.path.join(HERE, "..", "results", "miracl", "review_judgments_native.json")))
derived = [(r["lang"], r["qid"], label(r)) for r in A1] + [("yo", r["qid"], "ok" if valid(r) else "bad") for r in AY]
mism = [(l, q, lab, J.get(l, {}).get(q, {}).get("label")) for l, q, lab in derived if J.get(l, {}).get(q, {}).get("label") != lab]
print(f"question filter: {len(derived)} items, {len(mism)} mismatches with review_judgments_native.json", *mism[:5])

# ---------------- check against the paper (Table II and Sec. V-A)
paper = {"A_valid_sw": (47, 88), "A_valid_te": (52, 100), "A_valid_yo": (26, 80), "A_valid_id": (28, 62),
         "retestA_sw": 0.81, "retestA_te": 0.90, "retestA_yo": 0.59, "retestA_id": 0.88, "retestA_pooled": 0.85,
         "retestB_sw": 0.95, "retestB_te": 0.13, "retestB_yo": 0.21, "retestB_id": 0.46,
         "B_sw_real_corpus": 99, "B_sw_mt": 95, "B_sw_native_llm": 7, "B_te_real_corpus": 99, "B_te_mt": 97, "B_te_native_llm": 59,
         "B_yo_real_corpus": 96, "B_yo_mt": 96, "B_yo_native_llm": 20, "B_id_real_corpus": 87, "B_id_mt": 92, "B_id_native_llm": 78,
         "C_sw": (79, 47), "C_te": (88, 52), "C_yo": (83, 60), "C_id": (75, 28),
         "D_sw": (40, 88), "D_te": (40, 100), "D_yo": (23, 100), "D_id": (40, 100),
         "D_kappa_wrong": 0.90, "D_kappa_correct": 0.83, "D_precision": 98}
bad = [(k, out.get(k), v) for k, v in paper.items() if out.get(k) != v] + [("question filter", len(mism), 0)] * bool(mism)
for k, got, want in bad:
    print(f"[FAIL] {k}: got {got}, paper {want}")
print(f"\n{'ALL ANNOTATION CHECKS PASSED' if not bad else f'{len(bad)} CHECK(S) FAILED'} ({len(paper)} checks)")
sys.exit(1 if bad else 0)
