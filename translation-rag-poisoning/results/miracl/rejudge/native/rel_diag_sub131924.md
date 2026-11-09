# Does the two-layer relative feature help or hurt (sub131924, exclusion bad)

`rel_knn10 = knn10 - c`, c = mean knn10 of the neighbours (solved from knn10 - rel_knn10, not recomputed).

- **signal cancellation** `S_c/S_k`: whether the neighbours of a poison are also isolated. Near 1 = signal removed; negative = subtracting c amplifies the signal

- **noise ratio** `sd_rel/sd_k`: <1 = c moves with knn10, subtracting is cleaner; >1 = c is extra noise

- **net effect** `d'_rel/d'_k`: >1 relative feature better, <1 absolute feature better

| lang | variant | form | n | S_k | S_c | cancellation | sd_k | sd_rel | noise ratio | d'_k | d'_rel | net effect |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sw | native | bb | 28 | +0.0966 | +0.0290 | +0.30 | 0.0746 | 0.0388 | 0.52 | 1.30 | 1.74 | **1.34** |
| sw | native | adv | 28 | +0.1736 | +0.0739 | +0.43 | 0.0834 | 0.0457 | 0.55 | 2.08 | 2.18 | **1.05** |
| sw | trans | bb | 47 | +0.0533 | +0.0239 | +0.45 | 0.0760 | 0.0349 | 0.46 | 0.70 | 0.84 | **1.20** |
| sw | trans | adv | 47 | +0.0920 | +0.0533 | +0.58 | 0.0816 | 0.0371 | 0.45 | 1.13 | 1.04 | **0.92** |
| sw | en | bb | 47 | +0.0660 | +0.0209 | +0.32 | 0.0731 | 0.0338 | 0.46 | 0.90 | 1.33 | **1.48** |
| sw | en | adv | 47 | +0.1221 | +0.0564 | +0.46 | 0.0819 | 0.0358 | 0.44 | 1.49 | 1.83 | **1.23** |
| te | native | bb | 33 | +0.1432 | +0.0652 | +0.45 | 0.0812 | 0.0405 | 0.50 | 1.76 | 1.93 | **1.09** |
| te | native | adv | 33 | +0.1486 | +0.0654 | +0.44 | 0.0769 | 0.0416 | 0.54 | 1.93 | 2.00 | **1.04** |
| te | trans | bb | 52 | +0.1406 | +0.0872 | +0.62 | 0.0854 | 0.0426 | 0.50 | 1.65 | 1.25 | **0.76** |
| te | trans | adv | 52 | +0.1548 | +0.0787 | +0.51 | 0.0772 | 0.0455 | 0.59 | 2.01 | 1.67 | **0.83** |
| te | en | bb | 52 | +0.1606 | +0.0979 | +0.61 | 0.0904 | 0.0417 | 0.46 | 1.78 | 1.50 | **0.85** |
| te | en | adv | 52 | +0.1847 | +0.0814 | +0.44 | 0.0811 | 0.0471 | 0.58 | 2.28 | 2.19 | **0.96** |
| yo | native | bb | 24 | +0.1267 | +0.0467 | +0.37 | 0.0618 | 0.0474 | 0.77 | 2.05 | 1.69 | **0.82** |
| yo | native | adv | 24 | +0.2125 | +0.1058 | +0.50 | 0.0531 | 0.0498 | 0.94 | 4.00 | 2.14 | **0.54** |
| yo | trans | bb | 26 | +0.1042 | +0.0464 | +0.44 | 0.0667 | 0.0467 | 0.70 | 1.56 | 1.24 | **0.79** |
| yo | trans | adv | 26 | +0.1557 | +0.0733 | +0.47 | 0.0620 | 0.0457 | 0.74 | 2.51 | 1.80 | **0.72** |
| yo | en | bb | 26 | +0.1198 | +0.0514 | +0.43 | 0.0638 | 0.0439 | 0.69 | 1.88 | 1.56 | **0.83** |
| yo | en | adv | 26 | +0.2022 | +0.0890 | +0.44 | 0.0571 | 0.0416 | 0.73 | 3.54 | 2.72 | **0.77** |
| id | native | bb | 17 | +0.0536 | +0.0295 | +0.55 | 0.0890 | 0.0360 | 0.40 | 0.60 | 0.67 | **1.11** |
| id | native | adv | 17 | +0.0945 | +0.0501 | +0.53 | 0.0925 | 0.0389 | 0.42 | 1.02 | 1.14 | **1.12** |
| id | trans | bb | 28 | +0.0654 | +0.0527 | +0.80 | 0.0957 | 0.0349 | 0.36 | 0.68 | 0.37 | **0.54** |
| id | trans | adv | 28 | +0.0878 | +0.0555 | +0.63 | 0.0899 | 0.0370 | 0.41 | 0.98 | 0.87 | **0.89** |
| id | en | bb | 28 | +0.0962 | +0.0630 | +0.65 | 0.0996 | 0.0365 | 0.37 | 0.97 | 0.91 | **0.94** |
| id | en | adv | 28 | +0.1029 | +0.0519 | +0.50 | 0.0901 | 0.0376 | 0.42 | 1.14 | 1.36 | **1.19** |

## Attribution by language

net effect = (1 - cancellation) / noise ratio. The two 'deviation' columns are this language's deviation from the **cross-language median** on each term (log scale, additive); the term with the larger absolute value is why it differs from the other languages.

| lang | median net effect | cancellation | noise ratio | cancellation deviation | noise deviation | difference mainly from |
|---|---|---|---|---|---|---|
| sw | 1.22 | +0.44 | 0.46 | +0.05 | +0.06 | **noise ratio**, more favourable |
| te | 0.90 | +0.48 | 0.52 | -0.04 | -0.06 | **noise ratio**, less favourable |
| yo | 0.78 | +0.44 | 0.73 | +0.04 | -0.40 | **noise ratio**, less favourable |
| id | 1.03 | +0.59 | 0.41 | -0.27 | +0.18 | **signal cancellation**, less favourable |

Absolute levels as well:

- sw: net effect 1.22 -> relative feature better
- te: net effect 0.90 -> absolute feature better
- yo: net effect 0.78 -> absolute feature better
- id: net effect 1.03 -> comparable


## Corpus profile (random benign passages)

| lang | benign passages | median nn1 | near-duplicate rate | median knn10 | sd(knn10) | sd(c) | corr(knn10, c) |
|---|---|---|---|---|---|---|---|
| sw | 48,434 | 0.807 | 0.053 | 0.741 | 0.0805 | 0.0701 | +0.926 |
| te | 40,581 | 0.820 | 0.044 | 0.754 | 0.1167 | 0.1079 | +0.954 |
| yo | 29,937 | 0.822 | 0.055 | 0.791 | 0.0840 | 0.0717 | +0.923 |
| id | 39,942 | 0.725 | 0.032 | 0.656 | 0.1002 | 0.0898 | +0.946 |

near-duplicate rate = fraction with nn1 > 0.95. The higher corr(knn10, c), the more common fluctuation subtracting c removes; the lower, the more c is mainly noise.

