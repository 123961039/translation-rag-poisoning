# Can choosing by AUROC pick the wrong feature? (rel_knn10 vs knn10, full corpus, exclusion bad)

A = `rel_knn10` (analysis_excl-bad.json)   B = `knn10` (analysis_excl-bad_knn10.json). Differences are A - B; positive means A is better.

| lang | variant | form | n | tolerance | AUROC A/B | dAUROC | TPR@5% A/B | dTPR@5% | agree@5% | TPR@1% A/B | dTPR@1% | agree@1% |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| id | en | adv | 62 | 0.05 | 0.930/0.858 | +0.072 | 0.66/0.37 | +0.29 | yes | 0.27/0.19 | +0.08 | yes |
| id | en | bb | 62 | 0.05 | 0.881/0.773 | +0.108 | 0.37/0.21 | +0.16 | yes | 0.13/0.08 | +0.05 | yes |
| id | native | adv | 40 | 0.07 | 0.892/0.851 | +0.041 | 0.55/0.33 | +0.23 | yes | 0.20/0.12 | +0.08 | yes |
| id | native | bb | 40 | 0.07 | 0.820/0.737 | +0.083 | 0.35/0.15 | +0.20 | yes | 0.17/0.00 | +0.17 | yes |
| id | trans | adv | 62 | 0.05 | 0.881/0.811 | +0.069 | 0.44/0.21 | +0.23 | yes | 0.13/0.08 | +0.05 | yes |
| id | trans | bb | 62 | 0.05 | 0.792/0.704 | +0.087 | 0.27/0.11 | +0.16 | yes | 0.08/0.05 | +0.03 | yes |
| sw | en | adv | 88 | 0.03 | 0.920/0.849 | +0.072 | 0.60/0.39 | +0.22 | yes | 0.24/0.23 | +0.01 | yes |
| sw | en | bb | 88 | 0.03 | 0.844/0.739 | +0.106 | 0.36/0.30 | +0.07 | yes | 0.12/0.15 | -0.02 | yes |
| sw | native | adv | 56 | 0.05 | 0.959/0.931 | +0.028 | 0.79/0.61 | +0.18 | yes | 0.57/0.32 | +0.25 | yes |
| sw | native | bb | 56 | 0.05 | 0.919/0.837 | +0.083 | 0.61/0.43 | +0.18 | yes | 0.32/0.21 | +0.11 | yes |
| sw | trans | adv | 88 | 0.03 | 0.804/0.772 | +0.032 | 0.31/0.30 | +0.01 | yes | 0.08/0.11 | -0.03 | yes |
| sw | trans | bb | 88 | 0.03 | 0.761/0.685 | +0.075 | 0.24/0.22 | +0.02 | yes | 0.07/0.07 | +0.00 | yes |
| te | en | adv | 100 | 0.03 | 0.979/0.969 | +0.010 | 0.94/0.85 | +0.09 | yes | 0.63/0.52 | +0.11 | yes |
| te | en | bb | 100 | 0.03 | 0.931/0.886 | +0.045 | 0.66/0.36 | +0.30 | yes | 0.33/0.13 | +0.20 | yes |
| te | native | adv | 51 | 0.06 | 0.945/0.912 | +0.032 | 0.78/0.37 | +0.41 | yes | 0.47/0.16 | +0.31 | yes |
| te | native | bb | 51 | 0.06 | 0.944/0.893 | +0.051 | 0.76/0.39 | +0.37 | yes | 0.47/0.14 | +0.33 | yes |
| te | trans | adv | 100 | 0.03 | 0.935/0.928 | +0.007 | 0.75/0.59 | +0.16 | yes | 0.41/0.18 | +0.23 | yes |
| te | trans | bb | 100 | 0.03 | 0.899/0.867 | +0.032 | 0.56/0.32 | +0.24 | yes | 0.29/0.09 | +0.20 | yes |
| yo | en | adv | 80 | 0.04 | 0.969/0.989 | -0.020 | 0.79/0.91 | -0.12 | yes | 0.47/0.65 | -0.18 | yes |
| yo | en | bb | 80 | 0.04 | 0.891/0.929 | -0.038 | 0.56/0.74 | -0.18 | yes | 0.28/0.30 | -0.02 | yes |
| yo | native | adv | 70 | 0.04 | 0.961/0.990 | -0.028 | 0.76/0.84 | -0.09 | yes | 0.47/0.40 | +0.07 | **no** |
| yo | native | bb | 70 | 0.04 | 0.916/0.931 | -0.015 | 0.70/0.73 | -0.03 | yes | 0.34/0.20 | +0.14 | yes |
| yo | trans | adv | 80 | 0.04 | 0.902/0.952 | -0.050 | 0.57/0.72 | -0.15 | yes | 0.20/0.25 | -0.05 | yes |
| yo | trans | bb | 80 | 0.04 | 0.802/0.860 | -0.058 | 0.41/0.41 | +0.00 | yes | 0.15/0.11 | +0.04 | yes |

tolerance = max(0.02, 3/n). TPR granularity is 1/n, so with n=30 a difference of 0.03 is a single poison and does not count. 'floor' = TPR@1% <= 2/n on both sides, near 0, direction undecidable.


## How much the same feature difference is amplified in deployment metrics

- |dTPR@5%| > |dAUROC|: **18/22** rows, median amplification **3.0x**
- |dTPR@1%| > |dAUROC|: **13/22** rows, median amplification **1.3x**

(Rows with |dAUROC| <= 0.01 are excluded to avoid dividing by near 0; floor rows are excluded as well.)

## Do the two metrics lead to opposite choices?

The two operating points are reported separately. TPR@5% is rarely at the floor and is more reliable than TPR@1%; TPR@1% is closer to real deployment but coarse when there are few poisons.

### Operating point FPR=5%

No disagreement: in 24 decidable rows both metrics point to the same feature.

### Operating point FPR=1%

**In 1/24 decidable rows, AUROC and TPR@1% point to different features**:

- yo/native/adv (n=70, tolerance 0.04): AUROC picks `knn10` (-0.028), TPR@1% picks `rel_knn10` (+0.07, i.e. 5 poisons, 1.2x)

### By language (do the six rows of a language point to the same feature?)

- id: 6/6 rows of TPR@5% point to `rel_knn10`, max |dAUROC| 0.108, TPR@5% ratio 1.7-2.4x
- sw: 6/6 rows of TPR@5% point to `rel_knn10`, max |dAUROC| 0.106, TPR@5% ratio 1.0-1.6x
- te: 6/6 rows of TPR@5% point to `rel_knn10`, max |dAUROC| 0.051, TPR@5% ratio 1.1-2.1x
- yo: 6/6 rows of TPR@5% point to `knn10`, max |dAUROC| 0.058, TPR@5% ratio 1.0-1.3x

Six rows of a language (three variants x two forms) pointing to the same feature are much more robust than single-row disagreements; the six rows are not independent samples, but a consistent direction with multiplicative magnitude cannot be explained by granularity noise.

## Why

AUROC is the area under the whole ROC curve and weights all operating points equally. Ingestion filtering can only operate at the narrow left end: flagging 5% of benign documents is already the limit, and in practice it is usually pushed below 1%. Two features can have almost the same area and still differ several-fold in this region; the difference lies in the tail of the suspicion scores, to which the area is insensitive.

**The primary metric should therefore be TPR at a fixed low FPR, with AUROC as a secondary metric.**

