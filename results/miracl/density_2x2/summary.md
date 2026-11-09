# Controlled intervention: size x local density (fixed number of passages; judgments review_judgments_native.json)

## 0. Manipulation check and sample

| lang | size | passages | same-topic passages added at high density (all of A) | questions | same-topic neighbours: low / high | hit@5: low / high |
|---|---|---|---|---|---|---|
| sw | 20,000 | 20,000 / 20,000 | 2,602 (2,602) | 47 | 1.66 / 5.29 | 1.00 / 0.98 |
| sw | 45,000 | 45,000 / 45,000 | 2,602 (2,602) | 47 | 1.61 / 4.74 | 1.00 / 0.98 |
| te | 20,000 | 20,000 / 20,000 | 1,471 (1,471) | 52 | 1.02 / 6.03 | 1.00 / 1.00 |
| te | 45,000 | 45,000 / 45,000 | 1,471 (1,471) | 52 | 1.02 / 5.40 | 1.00 / 1.00 |
| yo | 20,000 | 20,000 / 20,000 | 448 (448) | 26 | 1.34 / 2.66 | 1.00 / 1.00 |
| yo | 45,000 | 45,000 / 45,000 | 448 (448) | 26 | 1.31 / 2.52 | 1.00 / 1.00 |
| id | 20,000 | 20,000 / 20,000 | 3,055 (3,055) | 28 | 2.45 / 7.64 | 1.00 / 0.99 |
| id | 45,000 | 45,000 / 45,000 | 3,055 (3,055) | 28 | 2.32 / 7.11 | 1.00 / 0.99 |

## rel_knn10: AUROC of the four cells (mean) and effects (paired by seed, +/- s.d. across seeds)

| lang | low@20k | high@20k | low@45k | high@45k | density effect@20k | density effect@45k | size effect@low | size effect@high | interaction |
|---|---|---|---|---|---|---|---|---|---|
| sw | 0.561 | 0.601 | 0.631 | 0.654 | +0.040 ± 0.011 | +0.023 ± 0.017 | +0.070 ± 0.021 | +0.053 ± 0.017 | -0.017 ± 0.010 |
| te | 0.738 | 0.782 | 0.781 | 0.799 | +0.044 ± 0.021 | +0.018 ± 0.005 | +0.043 ± 0.024 | +0.017 ± 0.011 | -0.026 ± 0.024 |
| yo | 0.860 | 0.804 | 0.870 | 0.828 | -0.056 ± 0.004 | -0.043 ± 0.002 | +0.010 ± 0.010 | +0.024 ± 0.010 | +0.013 ± 0.005 |
| id | 0.482 | 0.606 | 0.538 | 0.625 | +0.124 ± 0.019 | +0.086 ± 0.023 | +0.056 ± 0.018 | +0.018 ± 0.007 | -0.038 ± 0.013 |
| pooled (languages equally weighted) | | | | | +0.038 | +0.021 | +0.045 | +0.028 | -0.017 |

### rel_knn10: TPR@5% and surviving-poison rate after filtering (mean)

| lang | size | TPR@5% low / high | surviving-poison rate low / high |
|---|---|---|---|
| sw | 20,000 | 0.08 / 0.06 | 0.92 / 0.91 |
| sw | 45,000 | 0.14 / 0.10 | 0.86 / 0.88 |
| te | 20,000 | 0.32 / 0.37 | 0.68 / 0.63 |
| te | 45,000 | 0.38 / 0.42 | 0.62 / 0.58 |
| yo | 20,000 | 0.45 / 0.40 | 0.55 / 0.60 |
| yo | 45,000 | 0.60 / 0.54 | 0.40 / 0.46 |
| id | 20,000 | 0.03 / 0.06 | 0.97 / 0.93 |
| id | 45,000 | 0.05 / 0.11 | 0.95 / 0.89 |

## knn10: AUROC of the four cells (mean) and effects (paired by seed, +/- s.d. across seeds)

| lang | low@20k | high@20k | low@45k | high@45k | density effect@20k | density effect@45k | size effect@low | size effect@high | interaction |
|---|---|---|---|---|---|---|---|---|---|
| sw | 0.648 | 0.516 | 0.684 | 0.582 | -0.133 ± 0.006 | -0.102 ± 0.002 | +0.036 ± 0.007 | +0.067 ± 0.004 | +0.031 ± 0.007 |
| te | 0.829 | 0.735 | 0.840 | 0.768 | -0.094 ± 0.004 | -0.072 ± 0.004 | +0.011 ± 0.003 | +0.034 ± 0.004 | +0.022 ± 0.004 |
| yo | 0.858 | 0.833 | 0.872 | 0.854 | -0.025 ± 0.003 | -0.018 ± 0.001 | +0.015 ± 0.004 | +0.022 ± 0.003 | +0.007 ± 0.004 |
| id | 0.593 | 0.395 | 0.623 | 0.441 | -0.197 ± 0.007 | -0.182 ± 0.004 | +0.031 ± 0.004 | +0.046 ± 0.003 | +0.015 ± 0.007 |
| pooled (languages equally weighted) | | | | | -0.112 | -0.094 | +0.023 | +0.042 | +0.019 |

### knn10: TPR@5% and surviving-poison rate after filtering (mean)

| lang | size | TPR@5% low / high | surviving-poison rate low / high |
|---|---|---|---|
| sw | 20,000 | 0.18 / 0.09 | 0.82 / 0.89 |
| sw | 45,000 | 0.23 / 0.10 | 0.77 / 0.88 |
| te | 20,000 | 0.20 / 0.05 | 0.80 / 0.95 |
| te | 45,000 | 0.21 / 0.09 | 0.79 / 0.91 |
| yo | 20,000 | 0.42 / 0.29 | 0.58 / 0.71 |
| yo | 45,000 | 0.51 / 0.33 | 0.49 / 0.67 |
| id | 20,000 | 0.06 / 0.05 | 0.94 / 0.94 |
| id | 45,000 | 0.09 / 0.05 | 0.91 / 0.94 |

Reading: a negative density effect = more same-topic evidence makes detection harder (with the total number of passages fixed, this is an interventional effect);
a positive size effect = at the same density, larger corpora are easier. With two sizes and five seeds, the interaction is descriptive only.
