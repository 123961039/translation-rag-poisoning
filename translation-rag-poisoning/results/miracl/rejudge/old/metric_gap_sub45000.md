# Can choosing by AUROC pick the wrong feature? (rel_knn10 vs knn10, sub45000, exclusion bad)

A = `rel_knn10` (analysis_excl-bad_sub45000.json)   B = `knn10` (analysis_excl-bad_knn10_sub45000.json). Differences are A - B; positive means A is better.

| lang | variant | form | n | tolerance | AUROC A/B | dAUROC | TPR@5% A/B | dTPR@5% | agree@5% | TPR@1% A/B | dTPR@1% | agree@1% |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| id | en | adv | 30 | 0.10 | 0.810/0.735 | +0.074 | 0.37/0.27 | +0.10 | yes | 0.07/0.10 | -0.03 | yes |
| id | en | bb | 30 | 0.10 | 0.709/0.650 | +0.059 | 0.23/0.10 | +0.13 | yes | 0.00/0.03 | -0.03 | floor |
| id | native | adv | 20 | 0.15 | 0.698/0.645 | +0.053 | 0.30/0.20 | +0.10 | yes | 0.10/0.05 | +0.05 | floor |
| id | native | bb | 20 | 0.15 | 0.607/0.545 | +0.061 | 0.15/0.10 | +0.05 | yes | 0.00/0.00 | +0.00 | floor |
| id | trans | adv | 30 | 0.10 | 0.708/0.661 | +0.047 | 0.23/0.10 | +0.13 | yes | 0.03/0.03 | +0.00 | floor |
| id | trans | bb | 30 | 0.10 | 0.573/0.558 | +0.015 | 0.07/0.03 | +0.03 | floor | 0.00/0.00 | +0.00 | floor |
| sw | en | adv | 54 | 0.06 | 0.849/0.818 | +0.031 | 0.35/0.35 | +0.00 | yes | 0.19/0.19 | +0.00 | yes |
| sw | en | bb | 54 | 0.06 | 0.739/0.687 | +0.052 | 0.22/0.28 | -0.06 | **no** | 0.04/0.07 | -0.04 | yes |
| sw | native | adv | 34 | 0.09 | 0.895/0.885 | +0.010 | 0.53/0.38 | +0.15 | yes | 0.21/0.21 | +0.00 | yes |
| sw | native | bb | 34 | 0.09 | 0.812/0.740 | +0.073 | 0.32/0.26 | +0.06 | yes | 0.15/0.00 | +0.15 | yes |
| sw | trans | adv | 54 | 0.06 | 0.690/0.744 | -0.055 | 0.09/0.20 | -0.11 | yes | 0.00/0.06 | -0.06 | yes |
| sw | trans | bb | 54 | 0.06 | 0.624/0.633 | -0.009 | 0.06/0.17 | -0.11 | yes | 0.00/0.04 | -0.04 | floor |
| te | en | adv | 78 | 0.04 | 0.931/0.924 | +0.007 | 0.74/0.50 | +0.24 | yes | 0.37/0.21 | +0.17 | yes |
| te | en | bb | 78 | 0.04 | 0.850/0.826 | +0.024 | 0.49/0.18 | +0.31 | yes | 0.03/0.10 | -0.08 | **no** |
| te | native | adv | 39 | 0.08 | 0.859/0.851 | +0.008 | 0.62/0.18 | +0.44 | yes | 0.10/0.13 | -0.03 | yes |
| te | native | bb | 39 | 0.08 | 0.856/0.833 | +0.024 | 0.64/0.23 | +0.41 | yes | 0.10/0.08 | +0.03 | yes |
| te | trans | adv | 78 | 0.04 | 0.849/0.869 | -0.020 | 0.54/0.22 | +0.32 | **no** | 0.15/0.09 | +0.06 | **no** |
| te | trans | bb | 78 | 0.04 | 0.798/0.806 | -0.008 | 0.46/0.12 | +0.35 | yes | 0.01/0.04 | -0.03 | yes |
| yo | en | adv | 66 | 0.05 | 0.968/0.987 | -0.019 | 0.79/0.88 | -0.09 | yes | 0.47/0.68 | -0.21 | yes |
| yo | en | bb | 66 | 0.05 | 0.894/0.926 | -0.033 | 0.62/0.76 | -0.14 | yes | 0.21/0.33 | -0.12 | yes |
| yo | native | adv | 61 | 0.05 | 0.967/0.989 | -0.022 | 0.79/0.84 | -0.05 | yes | 0.39/0.38 | +0.02 | yes |
| yo | native | bb | 61 | 0.05 | 0.921/0.928 | -0.007 | 0.77/0.69 | +0.08 | yes | 0.30/0.21 | +0.08 | yes |
| yo | trans | adv | 66 | 0.05 | 0.904/0.947 | -0.044 | 0.53/0.70 | -0.17 | yes | 0.18/0.24 | -0.06 | yes |
| yo | trans | bb | 66 | 0.05 | 0.826/0.855 | -0.029 | 0.48/0.41 | +0.08 | **no** | 0.11/0.12 | -0.02 | yes |

tolerance = max(0.02, 3/n). TPR granularity is 1/n, so with n=30 a difference of 0.03 is a single poison and does not count. 'floor' = TPR@1% <= 2/n on both sides, near 0, direction undecidable.


## How much the same feature difference is amplified in deployment metrics

- |dTPR@5%| > |dAUROC|: **15/18** rows, median amplification **2.6x**
- |dTPR@1%| > |dAUROC|: **8/14** rows, median amplification **1.1x**

Warning: only 14/24 rows can be used for the TPR@1% amplification; in the others both features have TPR@1% near 0 (too few poisons, 1/n granularity too coarse). TPR@1% conclusions are unreliable at this size; use TPR@5%.

(Rows with |dAUROC| <= 0.01 are excluded to avoid dividing by near 0; floor rows are excluded as well.)

## Do the two metrics lead to opposite choices?

The two operating points are reported separately. TPR@5% is rarely at the floor and is more reliable than TPR@1%; TPR@1% is closer to real deployment but coarse when there are few poisons.

### Operating point FPR=5%

**In 3/23 decidable rows, AUROC and TPR@5% point to different features** (1 more rows at the floor are undecidable):

- te/trans/adv (n=78, tolerance 0.04): AUROC picks `knn10` (-0.020), TPR@5% picks `rel_knn10` (+0.32, i.e. 25 poisons, 2.5x)
- yo/trans/bb (n=66, tolerance 0.05): AUROC picks `knn10` (-0.029), TPR@5% picks `rel_knn10` (+0.08, i.e. 5 poisons, 1.2x)
- sw/en/bb (n=54, tolerance 0.06): AUROC picks `rel_knn10` (+0.052), TPR@5% picks `knn10` (-0.06, i.e. 3 poisons, 1.3x)

### Operating point FPR=1%

**In 2/18 decidable rows, AUROC and TPR@1% point to different features** (6 more rows at the floor are undecidable):

- te/en/bb (n=78, tolerance 0.04): AUROC picks `rel_knn10` (+0.024), TPR@1% picks `knn10` (-0.08, i.e. 6 poisons, 4.0x)
- te/trans/adv (n=78, tolerance 0.04): AUROC picks `knn10` (-0.020), TPR@1% picks `rel_knn10` (+0.06, i.e. 5 poisons, 1.7x)

### By language (do the six rows of a language point to the same feature?)

- id: 6/6 rows of TPR@5% point to `rel_knn10`, max |dAUROC| 0.074, TPR@5% ratio 1.4-2.3x
- sw: 4/6 rows of TPR@5% point to `knn10`, max |dAUROC| 0.073, TPR@5% ratio 1.0-3.0x
- te: 6/6 rows of TPR@5% point to `rel_knn10`, max |dAUROC| 0.024, TPR@5% ratio 1.5-4.0x  <- **AUROC shows no difference (all within +/-0.024), TPR@5% all in the same direction**
- yo: 4/6 rows of TPR@5% point to `knn10`, max |dAUROC| 0.044, TPR@5% ratio 1.1-1.3x

Six rows of a language (three variants x two forms) pointing to the same feature are much more robust than single-row disagreements; the six rows are not independent samples, but a consistent direction with multiplicative magnitude cannot be explained by granularity noise.

## Why

AUROC is the area under the whole ROC curve and weights all operating points equally. Ingestion filtering can only operate at the narrow left end: flagging 5% of benign documents is already the limit, and in practice it is usually pushed below 1%. Two features can have almost the same area and still differ several-fold in this region; the difference lies in the tail of the suspicion scores, to which the area is insensitive.

**The primary metric should therefore be TPR at a fixed low FPR, with AUROC as a secondary metric.**

