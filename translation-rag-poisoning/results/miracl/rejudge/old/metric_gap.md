# Can choosing by AUROC pick the wrong feature? (rel_knn10 vs knn10, full corpus, exclusion bad)

A = `rel_knn10` (analysis_excl-bad.json)   B = `knn10` (analysis_excl-bad_knn10.json). Differences are A - B; positive means A is better.

| lang | variant | form | n | tolerance | AUROC A/B | dAUROC | TPR@5% A/B | dTPR@5% | agree@5% | TPR@1% A/B | dTPR@1% | agree@1% |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| id | en | adv | 30 | 0.10 | 0.920/0.861 | +0.060 | 0.57/0.40 | +0.17 | yes | 0.27/0.20 | +0.07 | yes |
| id | en | bb | 30 | 0.10 | 0.872/0.791 | +0.081 | 0.33/0.23 | +0.10 | yes | 0.03/0.03 | +0.00 | floor |
| id | native | adv | 20 | 0.15 | 0.882/0.839 | +0.043 | 0.45/0.35 | +0.10 | yes | 0.20/0.10 | +0.10 | yes |
| id | native | bb | 20 | 0.15 | 0.794/0.730 | +0.064 | 0.30/0.15 | +0.15 | yes | 0.15/0.00 | +0.15 | yes |
| id | trans | adv | 30 | 0.10 | 0.870/0.823 | +0.048 | 0.40/0.23 | +0.17 | yes | 0.10/0.03 | +0.07 | yes |
| id | trans | bb | 30 | 0.10 | 0.773/0.723 | +0.050 | 0.27/0.10 | +0.17 | yes | 0.03/0.00 | +0.03 | floor |
| sw | en | adv | 54 | 0.06 | 0.912/0.847 | +0.065 | 0.56/0.37 | +0.19 | yes | 0.22/0.20 | +0.02 | yes |
| sw | en | bb | 54 | 0.06 | 0.824/0.724 | +0.099 | 0.30/0.31 | -0.02 | yes | 0.06/0.15 | -0.09 | **no** |
| sw | native | adv | 34 | 0.09 | 0.950/0.917 | +0.033 | 0.74/0.53 | +0.21 | yes | 0.50/0.26 | +0.24 | yes |
| sw | native | bb | 34 | 0.09 | 0.885/0.786 | +0.099 | 0.47/0.35 | +0.12 | yes | 0.24/0.15 | +0.09 | yes |
| sw | trans | adv | 54 | 0.06 | 0.774/0.763 | +0.011 | 0.22/0.28 | -0.06 | yes | 0.04/0.13 | -0.09 | yes |
| sw | trans | bb | 54 | 0.06 | 0.727/0.669 | +0.058 | 0.17/0.22 | -0.06 | yes | 0.02/0.07 | -0.06 | yes |
| te | en | adv | 78 | 0.04 | 0.979/0.967 | +0.012 | 0.94/0.83 | +0.10 | yes | 0.68/0.49 | +0.19 | yes |
| te | en | bb | 78 | 0.04 | 0.933/0.877 | +0.056 | 0.71/0.32 | +0.38 | yes | 0.36/0.10 | +0.26 | yes |
| te | native | adv | 39 | 0.08 | 0.943/0.906 | +0.037 | 0.79/0.33 | +0.46 | yes | 0.54/0.13 | +0.41 | yes |
| te | native | bb | 39 | 0.08 | 0.942/0.890 | +0.052 | 0.77/0.38 | +0.38 | yes | 0.56/0.13 | +0.44 | yes |
| te | trans | adv | 78 | 0.04 | 0.941/0.925 | +0.016 | 0.78/0.60 | +0.18 | yes | 0.46/0.17 | +0.29 | yes |
| te | trans | bb | 78 | 0.04 | 0.908/0.861 | +0.047 | 0.62/0.28 | +0.33 | yes | 0.32/0.09 | +0.23 | yes |
| yo | en | adv | 66 | 0.05 | 0.969/0.988 | -0.019 | 0.79/0.89 | -0.11 | yes | 0.52/0.67 | -0.15 | yes |
| yo | en | bb | 66 | 0.05 | 0.896/0.929 | -0.033 | 0.62/0.76 | -0.14 | yes | 0.30/0.32 | -0.02 | yes |
| yo | native | adv | 61 | 0.05 | 0.964/0.990 | -0.026 | 0.79/0.85 | -0.07 | yes | 0.51/0.41 | +0.10 | **no** |
| yo | native | bb | 61 | 0.05 | 0.921/0.931 | -0.010 | 0.72/0.74 | -0.02 | yes | 0.34/0.21 | +0.13 | yes |
| yo | trans | adv | 66 | 0.05 | 0.901/0.949 | -0.048 | 0.62/0.71 | -0.09 | yes | 0.21/0.24 | -0.03 | yes |
| yo | trans | bb | 66 | 0.05 | 0.824/0.860 | -0.036 | 0.48/0.44 | +0.05 | **no** | 0.17/0.12 | +0.05 | yes |

tolerance = max(0.02, 3/n). TPR granularity is 1/n, so with n=30 a difference of 0.03 is a single poison and does not count. 'floor' = TPR@1% <= 2/n on both sides, near 0, direction undecidable.


## How much the same feature difference is amplified in deployment metrics

- |dTPR@5%| > |dAUROC|: **22/24** rows, median amplification **3.4x**
- |dTPR@1%| > |dAUROC|: **16/22** rows, median amplification **3.8x**

(Rows with |dAUROC| <= 0.01 are excluded to avoid dividing by near 0; floor rows are excluded as well.)

## Do the two metrics lead to opposite choices?

The two operating points are reported separately. TPR@5% is rarely at the floor and is more reliable than TPR@1%; TPR@1% is closer to real deployment but coarse when there are few poisons.

### Operating point FPR=5%

**In 1/24 decidable rows, AUROC and TPR@5% point to different features**:

- yo/trans/bb (n=66, tolerance 0.05): AUROC picks `knn10` (-0.036), TPR@5% picks `rel_knn10` (+0.05, i.e. 3 poisons, 1.1x)

### Operating point FPR=1%

**In 2/22 decidable rows, AUROC and TPR@1% point to different features** (2 more rows at the floor are undecidable):

- yo/native/adv (n=61, tolerance 0.05): AUROC picks `knn10` (-0.026), TPR@1% picks `rel_knn10` (+0.10, i.e. 6 poisons, 1.2x)
- sw/en/bb (n=54, tolerance 0.06): AUROC picks `rel_knn10` (+0.099), TPR@1% picks `knn10` (-0.09, i.e. 5 poisons, 2.7x)

### By language (do the six rows of a language point to the same feature?)

- id: 6/6 rows of TPR@5% point to `rel_knn10`, max |dAUROC| 0.081, TPR@5% ratio 1.3-2.7x
- sw: 3/6 rows of TPR@5% point to `knn10`, max |dAUROC| 0.099, TPR@5% ratio 1.1-1.5x
- te: 6/6 rows of TPR@5% point to `rel_knn10`, max |dAUROC| 0.056, TPR@5% ratio 1.1-2.4x
- yo: 5/6 rows of TPR@5% point to `knn10`, max |dAUROC| 0.048, TPR@5% ratio 1.0-1.2x

Six rows of a language (three variants x two forms) pointing to the same feature are much more robust than single-row disagreements; the six rows are not independent samples, but a consistent direction with multiplicative magnitude cannot be explained by granularity noise.

## Why

AUROC is the area under the whole ROC curve and weights all operating points equally. Ingestion filtering can only operate at the narrow left end: flagging 5% of benign documents is already the limit, and in practice it is usually pushed below 1%. Two features can have almost the same area and still differ several-fold in this region; the difference lies in the tail of the suspicion scores, to which the area is insensitive.

**The primary metric should therefore be TPR at a fixed low FPR, with AUROC as a secondary metric.**

