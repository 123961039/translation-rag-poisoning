# Can choosing by AUROC pick the wrong feature? (rel_knn10 vs knn10, sub45000, exclusion bad)

A = `rel_knn10` (analysis_excl-bad_sub45000.json)   B = `knn10` (analysis_excl-bad_knn10_sub45000.json). Differences are A - B; positive means A is better.

| lang | variant | form | n | tolerance | AUROC A/B | dAUROC | TPR@5% A/B | dTPR@5% | agree@5% | TPR@1% A/B | dTPR@1% | agree@1% |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| id | en | adv | 28 | 0.11 | 0.825/0.763 | +0.062 | 0.43/0.29 | +0.14 | yes | 0.11/0.14 | -0.04 | yes |
| id | en | bb | 28 | 0.11 | 0.749/0.686 | +0.063 | 0.25/0.14 | +0.11 | yes | 0.00/0.07 | -0.07 | floor |
| id | native | adv | 17 | 0.18 | 0.760/0.685 | +0.075 | 0.47/0.29 | +0.18 | yes | 0.06/0.06 | +0.00 | floor |
| id | native | bb | 17 | 0.18 | 0.663/0.592 | +0.071 | 0.18/0.06 | +0.12 | yes | 0.00/0.00 | +0.00 | floor |
| id | trans | adv | 28 | 0.11 | 0.729/0.687 | +0.042 | 0.18/0.11 | +0.07 | yes | 0.04/0.07 | -0.04 | floor |
| id | trans | bb | 28 | 0.11 | 0.622/0.588 | +0.033 | 0.11/0.07 | +0.04 | yes | 0.00/0.00 | +0.00 | floor |
| sw | en | adv | 47 | 0.06 | 0.851/0.817 | +0.034 | 0.36/0.36 | +0.00 | yes | 0.19/0.21 | -0.02 | yes |
| sw | en | bb | 47 | 0.06 | 0.749/0.682 | +0.067 | 0.21/0.28 | -0.06 | **no** | 0.09/0.06 | +0.02 | yes |
| sw | native | adv | 28 | 0.11 | 0.905/0.902 | +0.003 | 0.54/0.54 | +0.00 | yes | 0.36/0.32 | +0.04 | yes |
| sw | native | bb | 28 | 0.11 | 0.835/0.779 | +0.056 | 0.36/0.39 | -0.04 | yes | 0.18/0.04 | +0.14 | yes |
| sw | trans | adv | 47 | 0.06 | 0.711/0.753 | -0.041 | 0.15/0.19 | -0.04 | yes | 0.04/0.06 | -0.02 | yes |
| sw | trans | bb | 47 | 0.06 | 0.642/0.634 | +0.008 | 0.09/0.17 | -0.09 | yes | 0.04/0.02 | +0.02 | floor |
| te | en | adv | 52 | 0.06 | 0.920/0.930 | -0.010 | 0.65/0.56 | +0.10 | yes | 0.27/0.25 | +0.02 | yes |
| te | en | bb | 52 | 0.06 | 0.839/0.848 | -0.008 | 0.42/0.25 | +0.17 | yes | 0.02/0.13 | -0.12 | yes |
| te | native | adv | 33 | 0.09 | 0.872/0.871 | +0.002 | 0.61/0.27 | +0.33 | yes | 0.15/0.15 | +0.00 | yes |
| te | native | bb | 33 | 0.09 | 0.863/0.851 | +0.012 | 0.61/0.30 | +0.30 | yes | 0.09/0.15 | -0.06 | yes |
| te | trans | adv | 52 | 0.06 | 0.834/0.887 | -0.053 | 0.46/0.25 | +0.21 | **no** | 0.12/0.10 | +0.02 | yes |
| te | trans | bb | 52 | 0.06 | 0.784/0.829 | -0.045 | 0.37/0.13 | +0.23 | **no** | 0.02/0.08 | -0.06 | yes |
| yo | en | adv | 26 | 0.12 | 0.974/0.985 | -0.011 | 0.77/0.85 | -0.08 | yes | 0.38/0.62 | -0.23 | yes |
| yo | en | bb | 26 | 0.12 | 0.874/0.899 | -0.025 | 0.50/0.65 | -0.15 | yes | 0.23/0.23 | +0.00 | yes |
| yo | native | adv | 24 | 0.12 | 0.965/0.989 | -0.025 | 0.75/0.92 | -0.17 | yes | 0.25/0.33 | -0.08 | yes |
| yo | native | bb | 24 | 0.12 | 0.905/0.913 | -0.009 | 0.79/0.62 | +0.17 | yes | 0.25/0.12 | +0.12 | yes |
| yo | trans | adv | 26 | 0.12 | 0.922/0.948 | -0.026 | 0.58/0.73 | -0.15 | yes | 0.27/0.23 | +0.04 | yes |
| yo | trans | bb | 26 | 0.12 | 0.827/0.853 | -0.026 | 0.54/0.35 | +0.19 | **no** | 0.12/0.15 | -0.04 | yes |

tolerance = max(0.02, 3/n). TPR granularity is 1/n, so with n=30 a difference of 0.03 is a single poison and does not count. 'floor' = TPR@1% <= 2/n on both sides, near 0, direction undecidable.


## How much the same feature difference is amplified in deployment metrics

- |dTPR@5%| > |dAUROC|: **16/19** rows, median amplification **2.4x**
- |dTPR@1%| > |dAUROC|: **8/14** rows, median amplification **1.5x**

Warning: only 14/24 rows can be used for the TPR@1% amplification; in the others both features have TPR@1% near 0 (too few poisons, 1/n granularity too coarse). TPR@1% conclusions are unreliable at this size; use TPR@5%.

(Rows with |dAUROC| <= 0.01 are excluded to avoid dividing by near 0; floor rows are excluded as well.)

## Do the two metrics lead to opposite choices?

The two operating points are reported separately. TPR@5% is rarely at the floor and is more reliable than TPR@1%; TPR@1% is closer to real deployment but coarse when there are few poisons.

### Operating point FPR=5%

**In 4/24 decidable rows, AUROC and TPR@5% point to different features**:

- te/trans/bb (n=52, tolerance 0.06): AUROC picks `knn10` (-0.045), TPR@5% picks `rel_knn10` (+0.23, i.e. 12 poisons, 2.7x)
- te/trans/adv (n=52, tolerance 0.06): AUROC picks `knn10` (-0.053), TPR@5% picks `rel_knn10` (+0.21, i.e. 11 poisons, 1.8x)
- yo/trans/bb (n=26, tolerance 0.12): AUROC picks `knn10` (-0.026), TPR@5% picks `rel_knn10` (+0.19, i.e. 5 poisons, 1.6x)
- sw/en/bb (n=47, tolerance 0.06): AUROC picks `rel_knn10` (+0.067), TPR@5% picks `knn10` (-0.06, i.e. 3 poisons, 1.3x)

### Operating point FPR=1%

No disagreement: in 18 decidable rows both metrics point to the same feature (6 more rows at the floor).

### By language (do the six rows of a language point to the same feature?)

- id: 6/6 rows of TPR@5% point to `rel_knn10`, max |dAUROC| 0.075, TPR@5% ratio 1.5-3.0x
- sw: 6/6 rows of TPR@5% point to `knn10`, max |dAUROC| 0.067, TPR@5% ratio 1.0-2.0x
- te: 6/6 rows of TPR@5% point to `rel_knn10`, max |dAUROC| 0.053, TPR@5% ratio 1.2-2.7x
- yo: 4/6 rows of TPR@5% point to `knn10`, max |dAUROC| 0.026, TPR@5% ratio 1.1-1.6x

Six rows of a language (three variants x two forms) pointing to the same feature are much more robust than single-row disagreements; the six rows are not independent samples, but a consistent direction with multiplicative magnitude cannot be explained by granularity noise.

## Why

AUROC is the area under the whole ROC curve and weights all operating points equally. Ingestion filtering can only operate at the narrow left end: flagging 5% of benign documents is already the limit, and in practice it is usually pushed below 1%. Two features can have almost the same area and still differ several-fold in this region; the difference lies in the tail of the suspicion scores, to which the area is insensitive.

**The primary metric should therefore be TPR at a fixed low FPR, with AUROC as a secondary metric.**

