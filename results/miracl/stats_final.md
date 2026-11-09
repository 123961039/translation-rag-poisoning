# Statistical fixes (judgments: native)

## 1. Paired test of the defense effect (attacked -> realistic defense, paired by question)

b = attack succeeds, fails after defense; c = attack fails, succeeds after defense. p is exact McNemar (two-sided); Holm correction: primary family = trans/bb of the 4 languages, secondary family = 12 language x variant (bb).

| lang | variant | questions | attacked | defended | difference (pp, 95% CI) | b / c | p | Holm p (primary) | Holm p (12) |
|---|---|---|---|---|---|---|---|---|---|
| sw | trans | 47 | 0.28 | 0.26 | -2.1 (-6.4, +0.0) | 1 / 0 | 1.0000 | 1.0000 | 1.0000 |
| te | trans | 52 | 0.15 | 0.08 | -7.7 (-15.4, -1.9) | 4 / 0 | 0.1250 | 0.3750 | 0.7500 |
| yo | trans | 26 | 0.50 | 0.19 | -30.8 (-50.0, -15.4) | 8 / 0 | 0.0078 | 0.0312 | 0.0781 |
| id | trans | 28 | 0.32 | 0.21 | -10.7 (-25.0, +0.0) | 3 / 0 | 0.2500 | 0.5000 | 1.0000 |
| sw | native | 28 | 0.25 | 0.07 | -17.9 (-32.1, -3.6) | 5 / 0 | 0.0625 | — | 0.5000 |
| te | native | 33 | 0.27 | 0.09 | -18.2 (-33.3, -6.1) | 6 / 0 | 0.0312 | — | 0.2812 |
| yo | native | 24 | 0.75 | 0.12 | -62.5 (-83.3, -41.7) | 15 / 0 | 0.0001 | — | 0.0007 |
| id | native | 17 | 0.35 | 0.24 | -11.8 (-29.4, +0.0) | 2 / 0 | 0.5000 | — | 1.0000 |
| sw | en | 47 | 0.21 | 0.17 | -4.3 (-10.6, +0.0) | 2 / 0 | 0.5000 | — | 1.0000 |
| te | en | 52 | 0.17 | 0.08 | -9.6 (-17.3, -1.9) | 5 / 0 | 0.0625 | — | 0.5000 |
| yo | en | 26 | 0.88 | 0.38 | -50.0 (-69.2, -30.8) | 13 / 0 | 0.0002 | — | 0.0027 |
| id | en | 28 | 0.11 | 0.07 | -3.6 (-10.7, +0.0) | 1 / 0 | 1.0000 | — | 1.0000 |

Wording: only Holm-corrected p < 0.05 is called a 'significant reduction'; the rest are 'reductions in the same direction (not significant)' with absolute question counts.

## 2. Only questions answered correctly under clean (removing questions that could not be answered anyway)

| lang | variant | all: questions / attacked / defended | clean-correct: questions / attacked / defended |
|---|---|---|---|
| sw | trans | 47 / 0.28 / 0.26 | 39 / 0.23 / 0.23 |
| te | trans | 52 / 0.15 / 0.08 | 48 / 0.15 / 0.08 |
| yo | trans | 26 / 0.50 / 0.19 | 18 / 0.56 / 0.17 |
| id | trans | 28 / 0.32 / 0.21 | 18 / 0.33 / 0.17 |
| sw | native | 28 / 0.25 / 0.07 | 25 / 0.24 / 0.08 |
| te | native | 33 / 0.27 / 0.09 | 30 / 0.27 / 0.10 |
| yo | native | 24 / 0.75 / 0.12 | 16 / 0.75 / 0.12 |
| id | native | 17 / 0.35 / 0.24 | 11 / 0.27 / 0.18 |
| sw | en | 47 / 0.21 / 0.17 | 39 / 0.23 / 0.18 |
| te | en | 52 / 0.17 / 0.08 | 48 / 0.19 / 0.08 |
| yo | en | 26 / 0.88 / 0.38 | 18 / 0.94 / 0.44 |
| id | en | 28 / 0.11 / 0.07 | 18 / 0.11 / 0.06 |

## 3. yo: original and added questions, stratified (trans/bb)

| subset | valid questions | clean accuracy | hit@5 | AUROC (rel_knn10) | TPR@5% | attacked ASR | defended ASR |
|---|---|---|---|---|---|---|---|
| original | 8 | 0.75 | 1.00 | 0.646 | 0.25 | 0.75 (6/8) | 0.50 (4/8) |
| added | 18 | 0.67 | 1.00 | 0.903 | 0.72 | 0.39 (7/18) | 0.06 (1/18) |
| pooled | 26 | 0.69 | 1.00 | 0.824 | 0.58 | 0.50 (13/26) | 0.19 (5/26) |

Added and original questions were generated with different model precision (AWQ vs unquantised), so differences cannot be attributed directly; the paper reports strata and notes this for pooled conclusions.
