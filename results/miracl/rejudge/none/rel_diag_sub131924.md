# Does the two-layer relative feature help or hurt (sub131924, exclusion bad)

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
| te | native | bb | 51 | +0.1370 | +0.0629 | +0.46 | 0.0812 | 0.0429 | 0.53 | 1.69 | 1.73 | **1.03** |
| te | native | adv | 51 | +0.1413 | +0.0644 | +0.46 | 0.0759 | 0.0437 | 0.58 | 1.86 | 1.76 | **0.95** |
| te | trans | bb | 100 | +0.1369 | +0.0810 | +0.59 | 0.0849 | 0.0440 | 0.52 | 1.61 | 1.27 | **0.79** |
| te | trans | adv | 100 | +0.1510 | +0.0716 | +0.47 | 0.0774 | 0.0476 | 0.62 | 1.95 | 1.67 | **0.85** |
| te | en | bb | 100 | +0.1582 | +0.0934 | +0.59 | 0.0893 | 0.0416 | 0.47 | 1.77 | 1.56 | **0.88** |
| te | en | adv | 100 | +0.1855 | +0.0739 | +0.40 | 0.0807 | 0.0474 | 0.59 | 2.30 | 2.35 | **1.02** |
| yo | native | bb | 70 | +0.1346 | +0.0465 | +0.35 | 0.0614 | 0.0476 | 0.78 | 2.19 | 1.85 | **0.84** |
| yo | native | adv | 70 | +0.2135 | +0.0966 | +0.45 | 0.0535 | 0.0521 | 0.97 | 3.99 | 2.24 | **0.56** |
| yo | trans | bb | 80 | +0.1038 | +0.0539 | +0.52 | 0.0657 | 0.0448 | 0.68 | 1.58 | 1.11 | **0.70** |
| yo | trans | adv | 80 | +0.1557 | +0.0810 | +0.52 | 0.0612 | 0.0457 | 0.75 | 2.54 | 1.63 | **0.64** |
| yo | en | bb | 80 | +0.1304 | +0.0563 | +0.43 | 0.0634 | 0.0467 | 0.74 | 2.06 | 1.59 | **0.77** |
| yo | en | adv | 80 | +0.2109 | +0.0923 | +0.44 | 0.0583 | 0.0494 | 0.85 | 3.62 | 2.40 | **0.66** |
| id | native | bb | 40 | +0.0481 | +0.0309 | +0.64 | 0.0868 | 0.0348 | 0.40 | 0.55 | 0.50 | **0.89** |
| id | native | adv | 40 | +0.0901 | +0.0538 | +0.60 | 0.0903 | 0.0394 | 0.44 | 1.00 | 0.92 | **0.92** |
| id | trans | bb | 62 | +0.0552 | +0.0462 | +0.84 | 0.0950 | 0.0337 | 0.35 | 0.58 | 0.27 | **0.46** |
| id | trans | adv | 62 | +0.0804 | +0.0501 | +0.62 | 0.0891 | 0.0353 | 0.40 | 0.90 | 0.86 | **0.95** |
| id | en | bb | 62 | +0.0857 | +0.0572 | +0.67 | 0.0987 | 0.0346 | 0.35 | 0.87 | 0.82 | **0.95** |
| id | en | adv | 62 | +0.0948 | +0.0458 | +0.48 | 0.0887 | 0.0362 | 0.41 | 1.07 | 1.35 | **1.27** |

## Attribution by language

net effect = (1 - cancellation) / noise ratio. The two 'deviation' columns are this language's deviation from the **cross-language median** on each term (log scale, additive); the term with the larger absolute value is why it differs from the other languages.

| lang | median net effect | cancellation | noise ratio | cancellation deviation | noise deviation | difference mainly from |
|---|---|---|---|---|---|---|
| sw | 1.25 | +0.43 | 0.47 | +0.04 | +0.08 | **noise ratio**, more favourable |
| te | 0.91 | +0.47 | 0.55 | -0.02 | -0.08 | **noise ratio**, less favourable |
| yo | 0.68 | +0.45 | 0.76 | +0.02 | -0.40 | **noise ratio**, less favourable |
| id | 0.94 | +0.63 | 0.40 | -0.39 | +0.24 | **signal cancellation**, less favourable |

Absolute levels as well:

- sw: net effect 1.25 -> relative feature better
- te: net effect 0.91 -> absolute feature better
- yo: net effect 0.68 -> absolute feature better
- id: net effect 0.94 -> absolute feature better


## Corpus profile (random benign passages)

| lang | benign passages | median nn1 | near-duplicate rate | median knn10 | sd(knn10) | sd(c) | corr(knn10, c) |
|---|---|---|---|---|---|---|---|
| sw | 48,434 | 0.807 | 0.053 | 0.741 | 0.0805 | 0.0701 | +0.926 |
| te | 40,581 | 0.820 | 0.044 | 0.754 | 0.1167 | 0.1079 | +0.954 |
| yo | 29,937 | 0.822 | 0.055 | 0.791 | 0.0840 | 0.0717 | +0.923 |
| id | 39,942 | 0.725 | 0.032 | 0.656 | 0.1002 | 0.0898 | +0.946 |

near-duplicate rate = fraction with nn1 > 0.95. The higher corr(knn10, c), the more common fluctuation subtracting c removes; the lower, the more c is mainly noise.

