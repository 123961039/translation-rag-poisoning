# Can choosing by AUROC pick the wrong feature? (rel_knn10 vs knn10, sub45000, exclusion bad)

A = `rel_knn10` (analysis_excl-bad_sub45000.json)   B = `knn10` (analysis_excl-bad_knn10_sub45000.json). Differences are A - B; positive means A is better.

| lang | variant | form | n | tolerance | AUROC A/B | dAUROC | TPR@5% A/B | dTPR@5% | agree@5% | TPR@1% A/B | dTPR@1% | agree@1% |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| id | en | adv | 62 | 0.05 | 0.815/0.734 | +0.081 | 0.39/0.23 | +0.16 | yes | 0.06/0.10 | -0.03 | yes |
| id | en | bb | 62 | 0.05 | 0.708/0.633 | +0.075 | 0.21/0.11 | +0.10 | yes | 0.02/0.03 | -0.02 | floor |
| id | native | adv | 40 | 0.07 | 0.717/0.662 | +0.055 | 0.33/0.17 | +0.15 | yes | 0.07/0.05 | +0.02 | yes |
| id | native | bb | 40 | 0.07 | 0.624/0.553 | +0.071 | 0.15/0.07 | +0.07 | yes | 0.00/0.00 | +0.00 | floor |
| id | trans | adv | 62 | 0.05 | 0.699/0.655 | +0.044 | 0.18/0.10 | +0.08 | yes | 0.03/0.05 | -0.02 | yes |
| id | trans | bb | 62 | 0.05 | 0.554/0.541 | +0.013 | 0.05/0.05 | +0.00 | yes | 0.00/0.00 | +0.00 | floor |
| sw | en | adv | 88 | 0.03 | 0.863/0.822 | +0.041 | 0.38/0.36 | +0.01 | yes | 0.19/0.22 | -0.02 | yes |
| sw | en | bb | 88 | 0.03 | 0.768/0.700 | +0.067 | 0.26/0.26 | +0.00 | yes | 0.10/0.08 | +0.02 | yes |
| sw | native | adv | 56 | 0.05 | 0.918/0.902 | +0.015 | 0.64/0.43 | +0.21 | yes | 0.29/0.23 | +0.05 | yes |
| sw | native | bb | 56 | 0.05 | 0.863/0.797 | +0.066 | 0.46/0.32 | +0.14 | yes | 0.20/0.05 | +0.14 | yes |
| sw | trans | adv | 88 | 0.03 | 0.729/0.756 | -0.027 | 0.20/0.20 | +0.00 | yes | 0.07/0.06 | +0.01 | yes |
| sw | trans | bb | 88 | 0.03 | 0.675/0.652 | +0.023 | 0.14/0.17 | -0.03 | yes | 0.02/0.03 | -0.01 | yes |
| te | en | adv | 100 | 0.03 | 0.929/0.930 | -0.001 | 0.72/0.57 | +0.15 | yes | 0.32/0.25 | +0.07 | yes |
| te | en | bb | 100 | 0.03 | 0.840/0.839 | +0.001 | 0.44/0.20 | +0.24 | yes | 0.03/0.11 | -0.08 | yes |
| te | native | adv | 51 | 0.06 | 0.853/0.856 | -0.003 | 0.57/0.22 | +0.35 | yes | 0.12/0.12 | +0.00 | yes |
| te | native | bb | 51 | 0.06 | 0.847/0.834 | +0.013 | 0.57/0.25 | +0.31 | yes | 0.10/0.10 | +0.00 | yes |
| te | trans | adv | 100 | 0.03 | 0.838/0.875 | -0.037 | 0.49/0.27 | +0.22 | **no** | 0.15/0.08 | +0.07 | **no** |
| te | trans | bb | 100 | 0.03 | 0.778/0.816 | -0.038 | 0.41/0.13 | +0.28 | **no** | 0.03/0.04 | -0.01 | yes |
| yo | en | adv | 80 | 0.04 | 0.969/0.988 | -0.019 | 0.80/0.89 | -0.09 | yes | 0.44/0.66 | -0.22 | yes |
| yo | en | bb | 80 | 0.04 | 0.887/0.926 | -0.039 | 0.56/0.72 | -0.16 | yes | 0.19/0.33 | -0.14 | yes |
| yo | native | adv | 70 | 0.04 | 0.964/0.989 | -0.026 | 0.76/0.83 | -0.07 | yes | 0.37/0.37 | +0.00 | yes |
| yo | native | bb | 70 | 0.04 | 0.915/0.928 | -0.013 | 0.74/0.69 | +0.06 | yes | 0.29/0.20 | +0.09 | yes |
| yo | trans | adv | 80 | 0.04 | 0.904/0.950 | -0.046 | 0.50/0.70 | -0.20 | yes | 0.17/0.25 | -0.08 | yes |
| yo | trans | bb | 80 | 0.04 | 0.801/0.854 | -0.053 | 0.41/0.39 | +0.02 | yes | 0.10/0.11 | -0.01 | yes |

tolerance = max(0.02, 3/n). TPR granularity is 1/n, so with n=30 a difference of 0.03 is a single poison and does not count. 'floor' = TPR@1% <= 2/n on both sides, near 0, direction undecidable.


## How much the same feature difference is amplified in deployment metrics

- |dTPR@5%| > |dAUROC|: **16/21** rows, median amplification **2.2x**
- |dTPR@1%| > |dAUROC|: **7/18** rows, median amplification **0.5x**

Warning: only 18/24 rows can be used for the TPR@1% amplification; in the others both features have TPR@1% near 0 (too few poisons, 1/n granularity too coarse). TPR@1% conclusions are unreliable at this size; use TPR@5%.

(Rows with |dAUROC| <= 0.01 are excluded to avoid dividing by near 0; floor rows are excluded as well.)

## Do the two metrics lead to opposite choices?

The two operating points are reported separately. TPR@5% is rarely at the floor and is more reliable than TPR@1%; TPR@1% is closer to real deployment but coarse when there are few poisons.

### Operating point FPR=5%

**In 2/24 decidable rows, AUROC and TPR@5% point to different features**:

- te/trans/bb (n=100, tolerance 0.03): AUROC picks `knn10` (-0.038), TPR@5% picks `rel_knn10` (+0.28, i.e. 28 poisons, 3.2x)
- te/trans/adv (n=100, tolerance 0.03): AUROC picks `knn10` (-0.037), TPR@5% picks `rel_knn10` (+0.22, i.e. 22 poisons, 1.8x)

### Operating point FPR=1%

**In 1/21 decidable rows, AUROC and TPR@1% point to different features** (3 more rows at the floor are undecidable):

- te/trans/adv (n=100, tolerance 0.03): AUROC picks `knn10` (-0.037), TPR@1% picks `rel_knn10` (+0.07, i.e. 7 poisons, 1.9x)

### By language (do the six rows of a language point to the same feature?)

- id: 5/6 rows of TPR@5% point to `rel_knn10`, max |dAUROC| 0.081, TPR@5% ratio 1.0-2.0x
- sw: 3/6 rows of TPR@5% point to `knn10`, max |dAUROC| 0.067, TPR@5% ratio 1.0-1.5x
- te: 6/6 rows of TPR@5% point to `rel_knn10`, max |dAUROC| 0.038, TPR@5% ratio 1.3-3.2x
- yo: 4/6 rows of TPR@5% point to `knn10`, max |dAUROC| 0.053, TPR@5% ratio 1.1-1.4x

Six rows of a language (three variants x two forms) pointing to the same feature are much more robust than single-row disagreements; the six rows are not independent samples, but a consistent direction with multiplicative magnitude cannot be explained by granularity noise.

## Why

AUROC is the area under the whole ROC curve and weights all operating points equally. Ingestion filtering can only operate at the narrow left end: flagging 5% of benign documents is already the limit, and in practice it is usually pushed below 1%. Two features can have almost the same area and still differ several-fold in this region; the difference lies in the tail of the suspicion scores, to which the area is insensitive.

**The primary metric should therefore be TPR at a fixed low FPR, with AUROC as a secondary metric.**

