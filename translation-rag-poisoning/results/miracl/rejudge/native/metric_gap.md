# Can choosing by AUROC pick the wrong feature? (rel_knn10 vs knn10, full corpus, exclusion bad)

A = `rel_knn10` (analysis_excl-bad.json)   B = `knn10` (analysis_excl-bad_knn10.json). Differences are A - B; positive means A is better.

| lang | variant | form | n | tolerance | AUROC A/B | dAUROC | TPR@5% A/B | dTPR@5% | agree@5% | TPR@1% A/B | dTPR@1% | agree@1% |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| id | en | adv | 28 | 0.11 | 0.933/0.865 | +0.068 | 0.64/0.43 | +0.21 | yes | 0.36/0.18 | +0.18 | yes |
| id | en | bb | 28 | 0.11 | 0.896/0.794 | +0.102 | 0.50/0.29 | +0.21 | yes | 0.18/0.07 | +0.11 | yes |
| id | native | adv | 17 | 0.18 | 0.918/0.855 | +0.063 | 0.59/0.41 | +0.18 | yes | 0.35/0.18 | +0.18 | yes |
| id | native | bb | 17 | 0.18 | 0.848/0.748 | +0.100 | 0.35/0.24 | +0.12 | yes | 0.18/0.00 | +0.18 | yes |
| id | trans | adv | 28 | 0.11 | 0.889/0.821 | +0.068 | 0.50/0.21 | +0.29 | yes | 0.07/0.11 | -0.04 | yes |
| id | trans | bb | 28 | 0.11 | 0.820/0.727 | +0.094 | 0.29/0.14 | +0.14 | yes | 0.07/0.04 | +0.04 | floor |
| sw | en | adv | 47 | 0.06 | 0.913/0.843 | +0.069 | 0.57/0.38 | +0.19 | yes | 0.23/0.21 | +0.02 | yes |
| sw | en | bb | 47 | 0.06 | 0.838/0.720 | +0.119 | 0.32/0.30 | +0.02 | yes | 0.11/0.15 | -0.04 | yes |
| sw | native | adv | 28 | 0.11 | 0.958/0.928 | +0.029 | 0.75/0.64 | +0.11 | yes | 0.54/0.39 | +0.14 | yes |
| sw | native | bb | 28 | 0.11 | 0.902/0.816 | +0.086 | 0.57/0.50 | +0.07 | yes | 0.29/0.25 | +0.04 | yes |
| sw | trans | adv | 47 | 0.06 | 0.790/0.768 | +0.021 | 0.34/0.30 | +0.04 | yes | 0.06/0.13 | -0.06 | yes |
| sw | trans | bb | 47 | 0.06 | 0.738/0.666 | +0.072 | 0.21/0.23 | -0.02 | yes | 0.04/0.09 | -0.04 | yes |
| te | en | adv | 52 | 0.06 | 0.973/0.965 | +0.007 | 0.90/0.83 | +0.08 | yes | 0.58/0.44 | +0.13 | yes |
| te | en | bb | 52 | 0.06 | 0.919/0.883 | +0.036 | 0.60/0.38 | +0.21 | yes | 0.31/0.15 | +0.15 | yes |
| te | native | adv | 33 | 0.09 | 0.953/0.915 | +0.039 | 0.79/0.42 | +0.36 | yes | 0.48/0.21 | +0.27 | yes |
| te | native | bb | 33 | 0.09 | 0.951/0.898 | +0.053 | 0.79/0.42 | +0.36 | yes | 0.48/0.18 | +0.30 | yes |
| te | trans | adv | 52 | 0.06 | 0.922/0.928 | -0.006 | 0.67/0.60 | +0.08 | yes | 0.40/0.17 | +0.23 | yes |
| te | trans | bb | 52 | 0.06 | 0.890/0.868 | +0.022 | 0.54/0.35 | +0.19 | yes | 0.29/0.12 | +0.17 | yes |
| yo | en | adv | 26 | 0.12 | 0.975/0.986 | -0.011 | 0.81/0.85 | -0.04 | yes | 0.54/0.62 | -0.08 | yes |
| yo | en | bb | 26 | 0.12 | 0.881/0.904 | -0.023 | 0.54/0.65 | -0.12 | yes | 0.27/0.23 | +0.04 | yes |
| yo | native | adv | 24 | 0.12 | 0.958/0.990 | -0.031 | 0.75/0.92 | -0.17 | yes | 0.38/0.33 | +0.04 | yes |
| yo | native | bb | 24 | 0.12 | 0.902/0.916 | -0.015 | 0.75/0.67 | +0.08 | yes | 0.25/0.12 | +0.12 | yes |
| yo | trans | adv | 26 | 0.12 | 0.914/0.950 | -0.036 | 0.65/0.73 | -0.08 | yes | 0.23/0.23 | +0.00 | yes |
| yo | trans | bb | 26 | 0.12 | 0.824/0.860 | -0.035 | 0.58/0.42 | +0.15 | **no** | 0.15/0.15 | +0.00 | yes |

tolerance = max(0.02, 3/n). TPR granularity is 1/n, so with n=30 a difference of 0.03 is a single poison and does not count. 'floor' = TPR@1% <= 2/n on both sides, near 0, direction undecidable.


## How much the same feature difference is amplified in deployment metrics

- |dTPR@5%| > |dAUROC|: **19/22** rows, median amplification **3.5x**
- |dTPR@1%| > |dAUROC|: **14/21** rows, median amplification **1.8x**

Warning: only 21/24 rows can be used for the TPR@1% amplification; in the others both features have TPR@1% near 0 (too few poisons, 1/n granularity too coarse). TPR@1% conclusions are unreliable at this size; use TPR@5%.

(Rows with |dAUROC| <= 0.01 are excluded to avoid dividing by near 0; floor rows are excluded as well.)

## Do the two metrics lead to opposite choices?

The two operating points are reported separately. TPR@5% is rarely at the floor and is more reliable than TPR@1%; TPR@1% is closer to real deployment but coarse when there are few poisons.

### Operating point FPR=5%

**In 1/24 decidable rows, AUROC and TPR@5% point to different features**:

- yo/trans/bb (n=26, tolerance 0.12): AUROC picks `knn10` (-0.035), TPR@5% picks `rel_knn10` (+0.15, i.e. 4 poisons, 1.4x)

### Operating point FPR=1%

No disagreement: in 23 decidable rows both metrics point to the same feature (1 more rows at the floor).

### By language (do the six rows of a language point to the same feature?)

- id: 6/6 rows of TPR@5% point to `rel_knn10`, max |dAUROC| 0.102, TPR@5% ratio 1.4-2.3x
- sw: 5/6 rows of TPR@5% point to `rel_knn10`, max |dAUROC| 0.119, TPR@5% ratio 1.1-1.5x
- te: 6/6 rows of TPR@5% point to `rel_knn10`, max |dAUROC| 0.053, TPR@5% ratio 1.1-1.9x
- yo: 4/6 rows of TPR@5% point to `knn10`, max |dAUROC| 0.036, TPR@5% ratio 1.0-1.4x

Six rows of a language (three variants x two forms) pointing to the same feature are much more robust than single-row disagreements; the six rows are not independent samples, but a consistent direction with multiplicative magnitude cannot be explained by granularity noise.

## Why

AUROC is the area under the whole ROC curve and weights all operating points equally. Ingestion filtering can only operate at the narrow left end: flagging 5% of benign documents is already the limit, and in practice it is usually pushed below 1%. Two features can have almost the same area and still differ several-fold in this region; the difference lies in the tail of the suspicion scores, to which the area is insensitive.

**The primary metric should therefore be TPR at a fixed low FPR, with AUROC as a secondary metric.**

