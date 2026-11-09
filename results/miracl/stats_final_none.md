# Statistical fixes (judgments: none)

## 1. Paired test of the defense effect (attacked -> realistic defense, paired by question)

b = attack succeeds, fails after defense; c = attack fails, succeeds after defense. p is exact McNemar (two-sided); Holm correction: primary family = trans/bb of the 4 languages, secondary family = 12 language x variant (bb).

| lang | variant | questions | attacked | defended | difference (pp, 95% CI) | b / c | p | Holm p (primary) | Holm p (12) |
|---|---|---|---|---|---|---|---|---|---|
| sw | trans | 88 | 0.31 | 0.26 | -4.5 (-9.1, -1.1) | 4 / 0 | 0.1250 | 0.2500 | 0.3750 |
| te | trans | 100 | 0.16 | 0.04 | -12.0 (-19.0, -6.0) | 12 / 0 | 0.0005 | 0.0020 | 0.0049 |
| yo | trans | 80 | 0.42 | 0.28 | -15.0 (-23.8, -7.5) | 12 / 0 | 0.0005 | 0.0020 | 0.0049 |
| id | trans | 62 | 0.37 | 0.31 | -6.5 (-12.9, -1.6) | 4 / 0 | 0.1250 | 0.2500 | 0.3750 |
| sw | native | 56 | 0.30 | 0.12 | -17.9 (-28.6, -8.9) | 10 / 0 | 0.0020 | — | 0.0137 |
| te | native | 51 | 0.25 | 0.10 | -15.7 (-25.5, -5.9) | 8 / 0 | 0.0078 | — | 0.0469 |
| yo | native | 70 | 0.67 | 0.19 | -48.6 (-60.0, -37.1) | 34 / 0 | 0.0000 | — | 0.0000 |
| id | native | 40 | 0.47 | 0.30 | -17.5 (-30.0, -7.5) | 7 / 0 | 0.0156 | — | 0.0781 |
| sw | en | 88 | 0.23 | 0.16 | -6.8 (-12.5, -2.3) | 6 / 0 | 0.0312 | — | 0.1250 |
| te | en | 100 | 0.15 | 0.04 | -11.0 (-17.0, -5.0) | 11 / 0 | 0.0010 | — | 0.0078 |
| yo | en | 80 | 0.56 | 0.26 | -30.0 (-40.0, -20.0) | 24 / 0 | 0.0000 | — | 0.0000 |
| id | en | 62 | 0.24 | 0.19 | -4.8 (-11.3, +0.0) | 3 / 0 | 0.2500 | — | 0.3750 |

Wording: only Holm-corrected p < 0.05 is called a 'significant reduction'; the rest are 'reductions in the same direction (not significant)' with absolute question counts.

## 2. Only questions answered correctly under clean (removing questions that could not be answered anyway)

| lang | variant | all: questions / attacked / defended | clean-correct: questions / attacked / defended |
|---|---|---|---|
| sw | trans | 88 / 0.31 / 0.26 | 53 / 0.28 / 0.26 |
| te | trans | 100 / 0.16 / 0.04 | 85 / 0.16 / 0.05 |
| yo | trans | 80 / 0.42 / 0.28 | 31 / 0.52 / 0.29 |
| id | trans | 62 / 0.37 / 0.31 | 24 / 0.29 / 0.17 |
| sw | native | 56 / 0.30 / 0.12 | 34 / 0.32 / 0.18 |
| te | native | 51 / 0.25 / 0.10 | 42 / 0.24 / 0.10 |
| yo | native | 70 / 0.67 / 0.19 | 27 / 0.70 / 0.11 |
| id | native | 40 / 0.47 / 0.30 | 15 / 0.33 / 0.20 |
| sw | en | 88 / 0.23 / 0.16 | 53 / 0.26 / 0.17 |
| te | en | 100 / 0.15 / 0.04 | 85 / 0.15 / 0.05 |
| yo | en | 80 / 0.56 / 0.26 | 31 / 0.81 / 0.35 |
| id | en | 62 / 0.24 / 0.19 | 24 / 0.12 / 0.08 |

## 3. yo: original and added questions, stratified (trans/bb)

| subset | valid questions | clean accuracy | hit@5 | AUROC (rel_knn10) | TPR@5% | attacked ASR | defended ASR |
|---|---|---|---|---|---|---|---|
| original | 28 | 0.46 | 1.00 | 0.712 | 0.18 | 0.57 (16/28) | 0.43 (12/28) |
| added | 52 | 0.35 | 0.98 | 0.851 | 0.54 | 0.35 (18/52) | 0.19 (10/52) |
| pooled | 80 | 0.39 | 0.99 | 0.802 | 0.41 | 0.42 (34/80) | 0.28 (22/80) |

Added and original questions were generated with different model precision (AWQ vs unquantised), so differences cannot be attributed directly; the paper reports strata and notes this for pooled conclusions.
