# Does the two-layer relative feature help or hurt (sub45000, exclusion bad)

`rel_knn10 = knn10 - c`, c = mean knn10 of the neighbours (solved from knn10 - rel_knn10, not recomputed).

- **signal cancellation** `S_c/S_k`: whether the neighbours of a poison are also isolated. Near 1 = signal removed; negative = subtracting c amplifies the signal

- **noise ratio** `sd_rel/sd_k`: <1 = c moves with knn10, subtracting is cleaner; >1 = c is extra noise

- **net effect** `d'_rel/d'_k`: >1 relative feature better, <1 absolute feature better

| lang | variant | form | n | S_k | S_c | cancellation | sd_k | sd_rel | noise ratio | d'_k | d'_rel | net effect |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sw | native | bb | 56 | +0.0895 | +0.0315 | +0.35 | 0.0759 | 0.0381 | 0.50 | 1.18 | 1.52 | **1.29** |
| sw | native | adv | 56 | +0.1567 | +0.0796 | +0.51 | 0.0856 | 0.0411 | 0.48 | 1.83 | 1.87 | **1.02** |
| sw | trans | bb | 88 | +0.0502 | +0.0294 | +0.58 | 0.0775 | 0.0354 | 0.46 | 0.65 | 0.59 | **0.91** |
| sw | trans | adv | 88 | +0.0921 | +0.0626 | +0.68 | 0.0854 | 0.0368 | 0.43 | 1.08 | 0.80 | **0.74** |
| sw | en | bb | 88 | +0.0624 | +0.0252 | +0.40 | 0.0767 | 0.0371 | 0.48 | 0.81 | 1.00 | **1.23** |
| sw | en | adv | 88 | +0.1198 | +0.0632 | +0.53 | 0.0868 | 0.0384 | 0.44 | 1.38 | 1.47 | **1.07** |
| te | native | bb | 51 | +0.1344 | +0.0724 | +0.54 | 0.0857 | 0.0445 | 0.52 | 1.57 | 1.39 | **0.89** |
| te | native | adv | 51 | +0.1352 | +0.0676 | +0.50 | 0.0791 | 0.0476 | 0.60 | 1.71 | 1.42 | **0.83** |
| te | trans | bb | 100 | +0.1361 | +0.0908 | +0.67 | 0.0892 | 0.0445 | 0.50 | 1.53 | 1.02 | **0.67** |
| te | trans | adv | 100 | +0.1421 | +0.0761 | +0.54 | 0.0805 | 0.0507 | 0.63 | 1.76 | 1.30 | **0.74** |
| te | en | bb | 100 | +0.1622 | +0.1066 | +0.66 | 0.0949 | 0.0412 | 0.43 | 1.71 | 1.35 | **0.79** |
| te | en | adv | 100 | +0.1780 | +0.0775 | +0.44 | 0.0852 | 0.0492 | 0.58 | 2.09 | 2.04 | **0.98** |
| yo | native | bb | 70 | +0.1334 | +0.0454 | +0.34 | 0.0617 | 0.0474 | 0.77 | 2.16 | 1.86 | **0.86** |
| yo | native | adv | 70 | +0.2133 | +0.0969 | +0.45 | 0.0539 | 0.0516 | 0.96 | 3.95 | 2.26 | **0.57** |
| yo | trans | bb | 80 | +0.1028 | +0.0528 | +0.51 | 0.0659 | 0.0448 | 0.68 | 1.56 | 1.12 | **0.72** |
| yo | trans | adv | 80 | +0.1561 | +0.0803 | +0.51 | 0.0615 | 0.0455 | 0.74 | 2.54 | 1.66 | **0.66** |
| yo | en | bb | 80 | +0.1294 | +0.0563 | +0.44 | 0.0636 | 0.0464 | 0.73 | 2.03 | 1.58 | **0.78** |
| yo | en | adv | 80 | +0.2115 | +0.0916 | +0.43 | 0.0588 | 0.0492 | 0.84 | 3.60 | 2.44 | **0.68** |
| id | native | bb | 40 | +0.0444 | +0.0306 | +0.69 | 0.0931 | 0.0346 | 0.37 | 0.48 | 0.40 | **0.83** |
| id | native | adv | 40 | +0.0689 | +0.0389 | +0.56 | 0.0908 | 0.0383 | 0.42 | 0.76 | 0.78 | **1.03** |
| id | trans | bb | 62 | +0.0511 | +0.0463 | +0.91 | 0.0997 | 0.0330 | 0.33 | 0.51 | 0.15 | **0.28** |
| id | trans | adv | 62 | +0.0651 | +0.0422 | +0.65 | 0.0888 | 0.0348 | 0.39 | 0.73 | 0.66 | **0.90** |
| id | en | bb | 62 | +0.0755 | +0.0525 | +0.70 | 0.1003 | 0.0331 | 0.33 | 0.75 | 0.69 | **0.92** |
| id | en | adv | 62 | +0.0890 | +0.0484 | +0.54 | 0.0924 | 0.0340 | 0.37 | 0.96 | 1.19 | **1.24** |

## Attribution by language

net effect = (1 - cancellation) / noise ratio. The two 'deviation' columns are this language's deviation from the **cross-language median** on each term (log scale, additive); the term with the larger absolute value is why it differs from the other languages.

| lang | median net effect | cancellation | noise ratio | cancellation deviation | noise deviation | difference mainly from |
|---|---|---|---|---|---|---|
| sw | 1.05 | +0.52 | 0.47 | +0.02 | +0.08 | **noise ratio**, more favourable |
| te | 0.81 | +0.54 | 0.55 | -0.02 | -0.08 | **noise ratio**, less favourable |
| yo | 0.70 | +0.44 | 0.75 | +0.16 | -0.40 | **noise ratio**, less favourable |
| id | 0.91 | +0.67 | 0.37 | -0.36 | +0.31 | **signal cancellation**, less favourable |

Absolute levels as well:

- sw: net effect 1.05 -> comparable
- te: net effect 0.81 -> absolute feature better
- yo: net effect 0.70 -> absolute feature better
- id: net effect 0.91 -> absolute feature better


## Corpus profile (random benign passages)

| lang | benign passages | median nn1 | near-duplicate rate | median knn10 | sd(knn10) | sd(c) | corr(knn10, c) |
|---|---|---|---|---|---|---|---|
| sw | 28,754 | 0.772 | 0.025 | 0.699 | 0.0869 | 0.0756 | +0.923 |
| te | 22,035 | 0.790 | 0.020 | 0.719 | 0.1246 | 0.1168 | +0.955 |
| yo | 28,762 | 0.821 | 0.050 | 0.789 | 0.0843 | 0.0715 | +0.918 |
| id | 22,601 | 0.687 | 0.016 | 0.626 | 0.1006 | 0.0905 | +0.945 |

near-duplicate rate = fraction with nn1 > 0.95. The higher corr(knn10, c), the more common fluctuation subtracting c removes; the lower, the more c is mainly noise.

