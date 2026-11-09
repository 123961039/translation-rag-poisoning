# Controlled intervention: size x local density (fixed number of passages; judgments none)

## 0. Manipulation check and sample

| lang | size | passages | same-topic passages added at high density (all of A) | questions | same-topic neighbours: low / high | hit@5: low / high |
|---|---|---|---|---|---|---|
| sw | 20,000 | 20,000 / 20,000 | 2,602 (2,602) | 88 | 1.67 / 5.40 | 1.00 / 0.98 |
| sw | 45,000 | 45,000 / 45,000 | 2,602 (2,602) | 88 | 1.61 / 4.77 | 1.00 / 0.98 |
| te | 20,000 | 20,000 / 20,000 | 1,471 (1,471) | 100 | 1.02 / 5.44 | 1.00 / 1.00 |
| te | 45,000 | 45,000 / 45,000 | 1,471 (1,471) | 100 | 1.01 / 4.81 | 1.00 / 1.00 |
| yo | 20,000 | 20,000 / 20,000 | 448 (448) | 80 | 1.23 / 2.50 | 0.99 / 0.99 |
| yo | 45,000 | 45,000 / 45,000 | 448 (448) | 80 | 1.20 / 2.28 | 0.99 / 0.99 |
| id | 20,000 | 20,000 / 20,000 | 3,055 (3,055) | 62 | 2.61 / 7.15 | 1.00 / 0.98 |
| id | 45,000 | 45,000 / 45,000 | 3,055 (3,055) | 62 | 2.45 / 6.59 | 1.00 / 0.98 |

## rel_knn10: AUROC of the four cells (mean) and effects (paired by seed, +/- s.d. across seeds)

| lang | low@20k | high@20k | low@45k | high@45k | density effect@20k | density effect@45k | size effect@low | size effect@high | interaction |
|---|---|---|---|---|---|---|---|---|---|
| sw | 0.605 | 0.619 | 0.681 | 0.679 | +0.014 ± 0.007 | -0.002 ± 0.013 | +0.076 ± 0.018 | +0.061 ± 0.013 | -0.015 ± 0.011 |
| te | 0.748 | 0.781 | 0.782 | 0.798 | +0.032 ± 0.017 | +0.016 ± 0.005 | +0.034 ± 0.021 | +0.017 ± 0.009 | -0.016 ± 0.018 |
| yo | 0.808 | 0.751 | 0.841 | 0.799 | -0.057 ± 0.006 | -0.042 ± 0.000 | +0.033 ± 0.008 | +0.048 ± 0.008 | +0.015 ± 0.006 |
| id | 0.447 | 0.622 | 0.502 | 0.630 | +0.175 ± 0.016 | +0.128 ± 0.011 | +0.055 ± 0.017 | +0.008 ± 0.010 | -0.047 ± 0.013 |
| pooled (languages equally weighted) | | | | | +0.041 | +0.025 | +0.049 | +0.034 | -0.016 |

### rel_knn10: TPR@5% and surviving-poison rate after filtering (mean)

| lang | size | TPR@5% low / high | surviving-poison rate low / high |
|---|---|---|---|
| sw | 20,000 | 0.09 / 0.08 | 0.91 / 0.89 |
| sw | 45,000 | 0.16 / 0.13 | 0.84 / 0.85 |
| te | 20,000 | 0.33 / 0.40 | 0.67 / 0.60 |
| te | 45,000 | 0.40 / 0.45 | 0.60 / 0.55 |
| yo | 20,000 | 0.33 / 0.27 | 0.67 / 0.72 |
| yo | 45,000 | 0.46 / 0.40 | 0.54 / 0.60 |
| id | 20,000 | 0.03 / 0.08 | 0.97 / 0.90 |
| id | 45,000 | 0.05 / 0.13 | 0.95 / 0.85 |

## knn10: AUROC of the four cells (mean) and effects (paired by seed, +/- s.d. across seeds)

| lang | low@20k | high@20k | low@45k | high@45k | density effect@20k | density effect@45k | size effect@low | size effect@high | interaction |
|---|---|---|---|---|---|---|---|---|---|
| sw | 0.660 | 0.528 | 0.697 | 0.598 | -0.132 ± 0.006 | -0.098 ± 0.002 | +0.036 ± 0.005 | +0.071 ± 0.002 | +0.034 ± 0.005 |
| te | 0.817 | 0.735 | 0.829 | 0.767 | -0.082 ± 0.005 | -0.062 ± 0.004 | +0.012 ± 0.002 | +0.032 ± 0.004 | +0.020 ± 0.004 |
| yo | 0.856 | 0.829 | 0.874 | 0.855 | -0.027 ± 0.003 | -0.019 ± 0.001 | +0.018 ± 0.004 | +0.026 ± 0.003 | +0.008 ± 0.004 |
| id | 0.547 | 0.394 | 0.579 | 0.438 | -0.152 ± 0.008 | -0.141 ± 0.002 | +0.032 ± 0.006 | +0.044 ± 0.004 | +0.012 ± 0.007 |
| pooled (languages equally weighted) | | | | | -0.098 | -0.080 | +0.024 | +0.043 | +0.019 |

### knn10: TPR@5% and surviving-poison rate after filtering (mean)

| lang | size | TPR@5% low / high | surviving-poison rate low / high |
|---|---|---|---|
| sw | 20,000 | 0.15 / 0.07 | 0.85 / 0.91 |
| sw | 45,000 | 0.23 / 0.11 | 0.77 / 0.87 |
| te | 20,000 | 0.14 / 0.05 | 0.86 / 0.95 |
| te | 45,000 | 0.16 / 0.08 | 0.84 / 0.92 |
| yo | 20,000 | 0.39 / 0.28 | 0.60 / 0.71 |
| yo | 45,000 | 0.47 / 0.38 | 0.52 / 0.60 |
| id | 20,000 | 0.04 / 0.03 | 0.96 / 0.95 |
| id | 45,000 | 0.07 / 0.05 | 0.93 / 0.93 |

Reading: a negative density effect = more same-topic evidence makes detection harder (with the total number of passages fixed, this is an interventional effect);
a positive size effect = at the same density, larger corpora are easier. With two sizes and five seeds, the interaction is descriptive only.
