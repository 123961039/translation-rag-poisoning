# Does the two-layer relative feature help or hurt (sub45000, exclusion bad)

`rel_knn10 = knn10 - c`, c = mean knn10 of the neighbours (solved from knn10 - rel_knn10, not recomputed).

- **signal cancellation** `S_c/S_k`: whether the neighbours of a poison are also isolated. Near 1 = signal removed; negative = subtracting c amplifies the signal

- **noise ratio** `sd_rel/sd_k`: <1 = c moves with knn10, subtracting is cleaner; >1 = c is extra noise

- **net effect** `d'_rel/d'_k`: >1 relative feature better, <1 absolute feature better

| lang | variant | form | n | S_k | S_c | cancellation | sd_k | sd_rel | noise ratio | d'_k | d'_rel | net effect |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sw | native | bb | 28 | +0.0862 | +0.0342 | +0.40 | 0.0770 | 0.0399 | 0.52 | 1.12 | 1.30 | **1.16** |
| sw | native | adv | 28 | +0.1635 | +0.0851 | +0.52 | 0.0884 | 0.0463 | 0.52 | 1.85 | 1.70 | **0.92** |
| sw | trans | bb | 47 | +0.0462 | +0.0302 | +0.65 | 0.0782 | 0.0357 | 0.46 | 0.59 | 0.45 | **0.76** |
| sw | trans | adv | 47 | +0.0915 | +0.0653 | +0.71 | 0.0853 | 0.0370 | 0.43 | 1.07 | 0.71 | **0.66** |
| sw | en | bb | 47 | +0.0586 | +0.0257 | +0.44 | 0.0763 | 0.0364 | 0.48 | 0.77 | 0.90 | **1.18** |
| sw | en | adv | 47 | +0.1200 | +0.0647 | +0.54 | 0.0872 | 0.0396 | 0.45 | 1.38 | 1.40 | **1.02** |
| te | native | bb | 33 | +0.1412 | +0.0779 | +0.55 | 0.0856 | 0.0427 | 0.50 | 1.65 | 1.48 | **0.90** |
| te | native | adv | 33 | +0.1431 | +0.0700 | +0.49 | 0.0799 | 0.0473 | 0.59 | 1.79 | 1.55 | **0.86** |
| te | trans | bb | 52 | +0.1415 | +0.0973 | +0.69 | 0.0895 | 0.0435 | 0.49 | 1.58 | 1.02 | **0.64** |
| te | trans | adv | 52 | +0.1466 | +0.0848 | +0.58 | 0.0803 | 0.0489 | 0.61 | 1.83 | 1.27 | **0.69** |
| te | en | bb | 52 | +0.1665 | +0.1117 | +0.67 | 0.0956 | 0.0409 | 0.43 | 1.74 | 1.34 | **0.77** |
| te | en | adv | 52 | +0.1783 | +0.0867 | +0.49 | 0.0855 | 0.0468 | 0.55 | 2.08 | 1.96 | **0.94** |
| yo | native | bb | 24 | +0.1254 | +0.0447 | +0.36 | 0.0620 | 0.0469 | 0.76 | 2.02 | 1.72 | **0.85** |
| yo | native | adv | 24 | +0.2121 | +0.1051 | +0.50 | 0.0535 | 0.0489 | 0.92 | 3.97 | 2.19 | **0.55** |
| yo | trans | bb | 26 | +0.1030 | +0.0440 | +0.43 | 0.0671 | 0.0471 | 0.70 | 1.54 | 1.25 | **0.82** |
| yo | trans | adv | 26 | +0.1557 | +0.0697 | +0.45 | 0.0624 | 0.0463 | 0.74 | 2.50 | 1.86 | **0.74** |
| yo | en | bb | 26 | +0.1182 | +0.0497 | +0.42 | 0.0641 | 0.0452 | 0.70 | 1.84 | 1.52 | **0.82** |
| yo | en | adv | 26 | +0.2019 | +0.0873 | +0.43 | 0.0577 | 0.0425 | 0.74 | 3.50 | 2.70 | **0.77** |
| id | native | bb | 17 | +0.0514 | +0.0332 | +0.65 | 0.0943 | 0.0351 | 0.37 | 0.54 | 0.52 | **0.95** |
| id | native | adv | 17 | +0.0738 | +0.0372 | +0.50 | 0.0926 | 0.0378 | 0.41 | 0.80 | 0.97 | **1.22** |
| id | trans | bb | 28 | +0.0620 | +0.0499 | +0.80 | 0.0996 | 0.0338 | 0.34 | 0.62 | 0.36 | **0.57** |
| id | trans | adv | 28 | +0.0727 | +0.0463 | +0.64 | 0.0890 | 0.0340 | 0.38 | 0.82 | 0.78 | **0.95** |
| id | en | bb | 28 | +0.0867 | +0.0576 | +0.66 | 0.1006 | 0.0343 | 0.34 | 0.86 | 0.85 | **0.99** |
| id | en | adv | 28 | +0.0968 | +0.0521 | +0.54 | 0.0934 | 0.0358 | 0.38 | 1.04 | 1.25 | **1.20** |

## Attribution by language

net effect = (1 - cancellation) / noise ratio. The two 'deviation' columns are this language's deviation from the **cross-language median** on each term (log scale, additive); the term with the larger absolute value is why it differs from the other languages.

| lang | median net effect | cancellation | noise ratio | cancellation deviation | noise deviation | difference mainly from |
|---|---|---|---|---|---|---|
| sw | 0.97 | +0.53 | 0.47 | +0.04 | +0.06 | **noise ratio**, more favourable |
| te | 0.82 | +0.57 | 0.52 | -0.04 | -0.06 | **noise ratio**, less favourable |
| yo | 0.79 | +0.43 | 0.74 | +0.23 | -0.40 | **noise ratio**, less favourable |
| id | 0.97 | +0.64 | 0.38 | -0.23 | +0.27 | **noise ratio**, more favourable |

Absolute levels as well:

- sw: net effect 0.97 -> comparable
- te: net effect 0.82 -> absolute feature better
- yo: net effect 0.79 -> absolute feature better
- id: net effect 0.97 -> comparable


## Corpus profile (random benign passages)

| lang | benign passages | median nn1 | near-duplicate rate | median knn10 | sd(knn10) | sd(c) | corr(knn10, c) |
|---|---|---|---|---|---|---|---|
| sw | 28,754 | 0.772 | 0.025 | 0.699 | 0.0869 | 0.0756 | +0.923 |
| te | 22,035 | 0.790 | 0.020 | 0.719 | 0.1246 | 0.1168 | +0.955 |
| yo | 28,762 | 0.821 | 0.050 | 0.789 | 0.0843 | 0.0715 | +0.918 |
| id | 22,601 | 0.687 | 0.016 | 0.626 | 0.1006 | 0.0905 | +0.945 |

near-duplicate rate = fraction with nn1 > 0.95. The higher corr(knn10, c), the more common fluctuation subtracting c removes; the lower, the more c is mainly noise.

