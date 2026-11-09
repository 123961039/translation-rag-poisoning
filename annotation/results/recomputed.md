# Annotation statistics recomputed from annotation/data/

## Task A: question validity (valid = all four criteria y)

| lang | items | valid | share (95% CI) | fails Q1 / Q2 / Q3 / Q4 | kappa vs. LLM-assisted first pass (n) |
|---|---|---|---|---|---|
| sw | 88 | 47 | 53% (43%-63%) | 21 / 26 / 15 / 1 | 0.53 (82) |
| te | 100 | 52 | 52% (42%-62%) | 5 / 40 / 5 / 5 | 0.24 (94) |
| yo | 80 | 26 | 32% (23%-43%) | 39 / 24 / 9 / 8 | 0.62 (27) |
| id | 62 | 28 | 45% (33%-57%) | 4 / 29 / 12 / 0 | 0.37 (54) |

yo includes the 52 expansion questions (no first-pass label). The paper's question filter (results/miracl/review_judgments_native.json) is derived from these labels: ok = all y, bad = any n, unsure otherwise.

## Task B: share judged 'reads like a person wrote it' (blind; source hidden from the annotator)

| lang | real Wikipedia | MT poison | LLM-written native poison |
|---|---|---|---|
| sw | 86/87 = 99% | 84/88 = 95% | 4/56 = 7% |
| te | 99/100 = 99% | 97/100 = 97% | 30/51 = 59% |
| yo | 27/28 = 96% | 27/28 = 96% | 4/20 = 20% |
| id | 52/60 = 87% | 57/62 = 92% | 31/40 = 78% |

The 'coherent' column of real passages is not used: real passages were truncated by word count when the sheets were built.

## Test-retest agreement (round 1 vs. round 2, same annotator)

| lang | Task A items | Task A agreement | Task A kappa (valid) | Task B rows | Task B kappa (natural) |
|---|---|---|---|---|---|
| sw | 22 | 91% | 0.81 | 58 | 0.95 |
| te | 25 | 96% | 0.90 | 63 | 0.13 |
| yo | 7 | 86% | 0.59 | 19 | 0.21 |
| id | 16 | 94% | 0.88 | 41 | 0.46 |
| pooled | 70 | 93% | 0.85 | | |

## Task C: translated poison still states the target (wrong) answer

| lang | items | y | partly | n | ? | share y (95% CI) | strict string match: recall of y |
|---|---|---|---|---|---|---|---|
| sw | 47 | 37 | 3 | 6 | 1 | 79% (65%-88%) | 62% |
| te | 52 | 46 | 2 | 2 | 2 | 88% (77%-95%) | 17% |
| yo | 60 | 50 | 6 | 4 | 0 | 83% (72%-91%) | 60% |
| id | 28 | 21 | 1 | 4 | 2 | 75% (57%-87%) | 81% |

yo pools the original questions (round 2) and the 52 expansion questions.

## Task D: automatic vs. human ASR judgment (stratified sample)

143 answers. kappa 'states the wrong answer' = 0.90; kappa 'states the correct answer' = 0.83; precision of automatic successes = 50/51 (98%); automatic failures judged successes by humans: 4.

| lang | answers | agreement (strict ASR) |
|---|---|---|
| sw | 40 | 88% |
| te | 40 | 100% |
| yo | 23 | 100% |
| id | 40 | 100% |

The sample is stratified by the automatic judgment (with partial matches oversampled), so these agreements describe each stratum and are not population accuracies.

