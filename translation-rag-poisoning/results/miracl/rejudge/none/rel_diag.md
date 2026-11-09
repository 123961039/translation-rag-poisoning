# Does the two-layer relative feature help or hurt (full corpus, exclusion bad)

`rel_knn10 = knn10 - c`, c = mean knn10 of the neighbours (solved from knn10 - rel_knn10, not recomputed).

- **signal cancellation** `S_c/S_k`: whether the neighbours of a poison are also isolated. Near 1 = signal removed; negative = subtracting c amplifies the signal

- **noise ratio** `sd_rel/sd_k`: <1 = c moves with knn10, subtracting is cleaner; >1 = c is extra noise

- **net effect** `d'_rel/d'_k`: >1 relative feature better, <1 absolute feature better

| lang | variant | form | n | S_k | S_c | cancellation | sd_k | sd_rel | noise ratio | d'_k | d'_rel | net effect |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sw | native | bb | 56 | +0.1009 | +0.0299 | +0.30 | 0.0732 | 0.0363 | 0.50 | 1.38 | 1.96 | **1.42** |
| sw | native | adv | 56 | +0.1675 | +0.0716 | +0.43 | 0.0808 | 0.0403 | 0.50 | 2.07 | 2.38 | **1.15** |
| sw | trans | bb | 88 | +0.0576 | +0.0251 | +0.44 | 0.0748 | 0.0343 | 0.46 | 0.77 | 0.95 | **1.23** |
| sw | trans | adv | 88 | +0.0930 | +0.0534 | +0.57 | 0.0813 | 0.0354 | 0.44 | 1.14 | 1.12 | **0.98** |
| sw | en | bb | 88 | +0.0704 | +0.0226 | +0.32 | 0.0731 | 0.0350 | 0.48 | 0.96 | 1.37 | **1.42** |
| sw | en | adv | 88 | +0.1232 | +0.0562 | +0.46 | 0.0815 | 0.0348 | 0.43 | 1.51 | 1.93 | **1.28** |
| te | native | bb | 51 | +0.1462 | +0.0516 | +0.35 | 0.0755 | 0.0409 | 0.54 | 1.94 | 2.31 | **1.19** |
| te | native | adv | 51 | +0.1505 | +0.0534 | +0.36 | 0.0722 | 0.0415 | 0.57 | 2.09 | 2.34 | **1.12** |
| te | trans | bb | 100 | +0.1426 | +0.0690 | +0.48 | 0.0794 | 0.0431 | 0.54 | 1.80 | 1.71 | **0.95** |
| te | trans | adv | 100 | +0.1628 | +0.0635 | +0.39 | 0.0726 | 0.0484 | 0.67 | 2.24 | 2.05 | **0.92** |
| te | en | bb | 100 | +0.1619 | +0.0785 | +0.49 | 0.0827 | 0.0406 | 0.49 | 1.96 | 2.05 | **1.05** |
| te | en | adv | 100 | +0.2032 | +0.0727 | +0.36 | 0.0752 | 0.0442 | 0.59 | 2.70 | 2.95 | **1.09** |
| yo | native | bb | 70 | +0.1346 | +0.0465 | +0.35 | 0.0614 | 0.0476 | 0.78 | 2.19 | 1.85 | **0.84** |
| yo | native | adv | 70 | +0.2135 | +0.0966 | +0.45 | 0.0535 | 0.0521 | 0.97 | 3.99 | 2.24 | **0.56** |
| yo | trans | bb | 80 | +0.1038 | +0.0539 | +0.52 | 0.0657 | 0.0448 | 0.68 | 1.58 | 1.11 | **0.70** |
| yo | trans | adv | 80 | +0.1557 | +0.0810 | +0.52 | 0.0612 | 0.0457 | 0.75 | 2.54 | 1.63 | **0.64** |
| yo | en | bb | 80 | +0.1304 | +0.0563 | +0.43 | 0.0634 | 0.0467 | 0.74 | 2.06 | 1.59 | **0.77** |
| yo | en | adv | 80 | +0.2109 | +0.0923 | +0.44 | 0.0583 | 0.0494 | 0.85 | 3.62 | 2.40 | **0.66** |
| id | native | bb | 40 | +0.0763 | +0.0294 | +0.38 | 0.0790 | 0.0380 | 0.48 | 0.97 | 1.24 | **1.28** |
| id | native | adv | 40 | +0.1212 | +0.0560 | +0.46 | 0.0804 | 0.0399 | 0.50 | 1.51 | 1.64 | **1.08** |
| id | trans | bb | 62 | +0.0747 | +0.0381 | +0.51 | 0.0840 | 0.0346 | 0.41 | 0.89 | 1.06 | **1.19** |
| id | trans | adv | 62 | +0.1027 | +0.0482 | +0.47 | 0.0795 | 0.0346 | 0.43 | 1.29 | 1.58 | **1.22** |
| id | en | bb | 62 | +0.1015 | +0.0486 | +0.48 | 0.0867 | 0.0332 | 0.38 | 1.17 | 1.59 | **1.36** |
| id | en | adv | 62 | +0.1201 | +0.0463 | +0.39 | 0.0792 | 0.0358 | 0.45 | 1.52 | 2.06 | **1.36** |

## Attribution by language

net effect = (1 - cancellation) / noise ratio. The two 'deviation' columns are this language's deviation from the **cross-language median** on each term (log scale, additive); the term with the larger absolute value is why it differs from the other languages.

| lang | median net effect | cancellation | noise ratio | cancellation deviation | noise deviation | difference mainly from |
|---|---|---|---|---|---|---|
| sw | 1.25 | +0.43 | 0.47 | +0.01 | +0.09 | **noise ratio**, more favourable |
| te | 1.07 | +0.37 | 0.56 | +0.11 | -0.09 | **signal cancellation**, more favourable |
| yo | 0.68 | +0.45 | 0.76 | -0.01 | -0.40 | **noise ratio**, less favourable |
| id | 1.25 | +0.47 | 0.44 | -0.05 | +0.14 | **noise ratio**, more favourable |

Absolute levels as well:

- sw: net effect 1.25 -> relative feature better
- te: net effect 1.07 -> relative feature better
- yo: net effect 0.68 -> absolute feature better
- id: net effect 1.25 -> relative feature better


## Corpus profile (random benign passages)

| lang | benign passages | median nn1 | near-duplicate rate | median knn10 | sd(knn10) | sd(c) | corr(knn10, c) |
|---|---|---|---|---|---|---|---|
| sw | 48,434 | 0.807 | 0.053 | 0.741 | 0.0805 | 0.0701 | +0.926 |
| te | 57,809 | 0.857 | 0.107 | 0.799 | 0.1050 | 0.0954 | +0.951 |
| yo | 29,937 | 0.822 | 0.055 | 0.791 | 0.0840 | 0.0717 | +0.923 |
| id | 63,119 | 0.809 | 0.085 | 0.738 | 0.0918 | 0.0806 | +0.936 |

near-duplicate rate = fraction with nn1 > 0.95. The higher corr(knn10, c), the more common fluctuation subtracting c removes; the lower, the more c is mainly noise.

