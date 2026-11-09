# Does the two-layer relative feature help or hurt (sub45000, exclusion bad)

`rel_knn10 = knn10 - c`, c = mean knn10 of the neighbours (solved from knn10 - rel_knn10, not recomputed).

- **signal cancellation** `S_c/S_k`: whether the neighbours of a poison are also isolated. Near 1 = signal removed; negative = subtracting c amplifies the signal

- **noise ratio** `sd_rel/sd_k`: <1 = c moves with knn10, subtracting is cleaner; >1 = c is extra noise

- **net effect** `d'_rel/d'_k`: >1 relative feature better, <1 absolute feature better

| lang | variant | form | n | S_k | S_c | cancellation | sd_k | sd_rel | noise ratio | d'_k | d'_rel | net effect |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sw | native | bb | 34 | +0.0730 | +0.0267 | +0.37 | 0.0757 | 0.0389 | 0.51 | 0.96 | 1.19 | **1.23** |
| sw | native | adv | 34 | +0.1490 | +0.0782 | +0.53 | 0.0866 | 0.0439 | 0.51 | 1.72 | 1.61 | **0.94** |
| sw | trans | bb | 54 | +0.0466 | +0.0348 | +0.75 | 0.0785 | 0.0327 | 0.42 | 0.59 | 0.36 | **0.61** |
| sw | trans | adv | 54 | +0.0889 | +0.0687 | +0.77 | 0.0858 | 0.0331 | 0.39 | 1.04 | 0.61 | **0.59** |
| sw | en | bb | 54 | +0.0604 | +0.0296 | +0.49 | 0.0776 | 0.0352 | 0.45 | 0.78 | 0.87 | **1.12** |
| sw | en | adv | 54 | +0.1192 | +0.0671 | +0.56 | 0.0873 | 0.0369 | 0.42 | 1.37 | 1.41 | **1.04** |
| te | native | bb | 39 | +0.1335 | +0.0662 | +0.50 | 0.0853 | 0.0450 | 0.53 | 1.56 | 1.50 | **0.96** |
| te | native | adv | 39 | +0.1331 | +0.0624 | +0.47 | 0.0791 | 0.0472 | 0.60 | 1.68 | 1.50 | **0.89** |
| te | trans | bb | 78 | +0.1326 | +0.0834 | +0.63 | 0.0892 | 0.0437 | 0.49 | 1.49 | 1.13 | **0.76** |
| te | trans | adv | 78 | +0.1394 | +0.0691 | +0.50 | 0.0807 | 0.0510 | 0.63 | 1.73 | 1.38 | **0.80** |
| te | en | bb | 78 | +0.1574 | +0.0991 | +0.63 | 0.0948 | 0.0407 | 0.43 | 1.66 | 1.43 | **0.86** |
| te | en | adv | 78 | +0.1737 | +0.0678 | +0.39 | 0.0850 | 0.0501 | 0.59 | 2.04 | 2.11 | **1.03** |
| yo | native | bb | 61 | +0.1339 | +0.0433 | +0.32 | 0.0618 | 0.0474 | 0.77 | 2.17 | 1.91 | **0.88** |
| yo | native | adv | 61 | +0.2130 | +0.0919 | +0.43 | 0.0538 | 0.0509 | 0.95 | 3.96 | 2.38 | **0.60** |
| yo | trans | bb | 66 | +0.1035 | +0.0471 | +0.45 | 0.0663 | 0.0449 | 0.68 | 1.56 | 1.26 | **0.80** |
| yo | trans | adv | 66 | +0.1545 | +0.0770 | +0.50 | 0.0618 | 0.0443 | 0.72 | 2.50 | 1.75 | **0.70** |
| yo | en | bb | 66 | +0.1301 | +0.0525 | +0.40 | 0.0636 | 0.0467 | 0.73 | 2.04 | 1.66 | **0.81** |
| yo | en | adv | 66 | +0.2100 | +0.0878 | +0.42 | 0.0586 | 0.0489 | 0.83 | 3.58 | 2.50 | **0.70** |
| id | native | bb | 20 | +0.0412 | +0.0290 | +0.70 | 0.0947 | 0.0356 | 0.38 | 0.44 | 0.34 | **0.79** |
| id | native | adv | 20 | +0.0643 | +0.0365 | +0.57 | 0.0922 | 0.0392 | 0.42 | 0.70 | 0.71 | **1.02** |
| id | trans | bb | 30 | +0.0533 | +0.0465 | +0.87 | 0.0999 | 0.0333 | 0.33 | 0.53 | 0.20 | **0.38** |
| id | trans | adv | 30 | +0.0662 | +0.0412 | +0.62 | 0.0888 | 0.0352 | 0.40 | 0.75 | 0.71 | **0.95** |
| id | en | bb | 30 | +0.0775 | +0.0540 | +0.70 | 0.1011 | 0.0340 | 0.34 | 0.77 | 0.69 | **0.90** |
| id | en | adv | 30 | +0.0895 | +0.0497 | +0.55 | 0.0936 | 0.0343 | 0.37 | 0.96 | 1.16 | **1.22** |

## Attribution by language

net effect = (1 - cancellation) / noise ratio. The two 'deviation' columns are this language's deviation from the **cross-language median** on each term (log scale, additive); the term with the larger absolute value is why it differs from the other languages.

| lang | median net effect | cancellation | noise ratio | cancellation deviation | noise deviation | difference mainly from |
|---|---|---|---|---|---|---|
| sw | 0.99 | +0.54 | 0.44 | -0.05 | +0.12 | **noise ratio**, more favourable |
| te | 0.88 | +0.50 | 0.56 | +0.05 | -0.12 | **noise ratio**, less favourable |
| yo | 0.75 | +0.42 | 0.75 | +0.18 | -0.42 | **noise ratio**, less favourable |
| id | 0.93 | +0.66 | 0.37 | -0.34 | +0.29 | **signal cancellation**, less favourable |

Absolute levels as well:

- sw: net effect 0.99 -> comparable
- te: net effect 0.88 -> absolute feature better
- yo: net effect 0.75 -> absolute feature better
- id: net effect 0.93 -> absolute feature better


## Corpus profile (random benign passages)

| lang | benign passages | median nn1 | near-duplicate rate | median knn10 | sd(knn10) | sd(c) | corr(knn10, c) |
|---|---|---|---|---|---|---|---|
| sw | 28,754 | 0.772 | 0.025 | 0.699 | 0.0869 | 0.0756 | +0.923 |
| te | 22,035 | 0.790 | 0.020 | 0.719 | 0.1246 | 0.1168 | +0.955 |
| yo | 28,762 | 0.821 | 0.050 | 0.789 | 0.0843 | 0.0715 | +0.918 |
| id | 22,601 | 0.687 | 0.016 | 0.626 | 0.1006 | 0.0905 | +0.945 |

near-duplicate rate = fraction with nn1 > 0.95. The higher corr(knn10, c), the more common fluctuation subtracting c removes; the lower, the more c is mainly noise.

