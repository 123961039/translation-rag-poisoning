# Does the two-layer relative feature help or hurt (full corpus, exclusion bad)

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
| te | native | bb | 33 | +0.1506 | +0.0534 | +0.35 | 0.0767 | 0.0412 | 0.54 | 1.96 | 2.36 | **1.20** |
| te | native | adv | 33 | +0.1551 | +0.0542 | +0.35 | 0.0744 | 0.0425 | 0.57 | 2.08 | 2.37 | **1.14** |
| te | trans | bb | 52 | +0.1438 | +0.0724 | +0.50 | 0.0804 | 0.0443 | 0.55 | 1.79 | 1.61 | **0.90** |
| te | trans | adv | 52 | +0.1636 | +0.0684 | +0.42 | 0.0729 | 0.0492 | 0.67 | 2.24 | 1.93 | **0.86** |
| te | en | bb | 52 | +0.1617 | +0.0805 | +0.50 | 0.0838 | 0.0431 | 0.51 | 1.93 | 1.89 | **0.98** |
| te | en | adv | 52 | +0.1996 | +0.0739 | +0.37 | 0.0757 | 0.0465 | 0.61 | 2.64 | 2.70 | **1.02** |
| yo | native | bb | 24 | +0.1267 | +0.0467 | +0.37 | 0.0618 | 0.0474 | 0.77 | 2.05 | 1.69 | **0.82** |
| yo | native | adv | 24 | +0.2125 | +0.1058 | +0.50 | 0.0531 | 0.0498 | 0.94 | 4.00 | 2.14 | **0.54** |
| yo | trans | bb | 26 | +0.1042 | +0.0464 | +0.44 | 0.0667 | 0.0467 | 0.70 | 1.56 | 1.24 | **0.79** |
| yo | trans | adv | 26 | +0.1557 | +0.0733 | +0.47 | 0.0620 | 0.0457 | 0.74 | 2.51 | 1.80 | **0.72** |
| yo | en | bb | 26 | +0.1198 | +0.0514 | +0.43 | 0.0638 | 0.0439 | 0.69 | 1.88 | 1.56 | **0.83** |
| yo | en | adv | 26 | +0.2022 | +0.0890 | +0.44 | 0.0571 | 0.0416 | 0.73 | 3.54 | 2.72 | **0.77** |
| id | native | bb | 17 | +0.0804 | +0.0274 | +0.34 | 0.0809 | 0.0398 | 0.49 | 0.99 | 1.33 | **1.34** |
| id | native | adv | 17 | +0.1250 | +0.0550 | +0.44 | 0.0820 | 0.0364 | 0.44 | 1.52 | 1.93 | **1.26** |
| id | trans | bb | 28 | +0.0809 | +0.0408 | +0.50 | 0.0840 | 0.0338 | 0.40 | 0.96 | 1.19 | **1.23** |
| id | trans | adv | 28 | +0.1060 | +0.0505 | +0.48 | 0.0793 | 0.0341 | 0.43 | 1.34 | 1.62 | **1.22** |
| id | en | bb | 28 | +0.1083 | +0.0498 | +0.46 | 0.0871 | 0.0339 | 0.39 | 1.24 | 1.72 | **1.39** |
| id | en | adv | 28 | +0.1245 | +0.0472 | +0.38 | 0.0803 | 0.0377 | 0.47 | 1.55 | 2.05 | **1.32** |

## Attribution by language

net effect = (1 - cancellation) / noise ratio. The two 'deviation' columns are this language's deviation from the **cross-language median** on each term (log scale, additive); the term with the larger absolute value is why it differs from the other languages.

| lang | median net effect | cancellation | noise ratio | cancellation deviation | noise deviation | difference mainly from |
|---|---|---|---|---|---|---|
| sw | 1.22 | +0.44 | 0.46 | +0.00 | +0.10 | **noise ratio**, more favourable |
| te | 1.00 | +0.39 | 0.56 | +0.08 | -0.10 | **noise ratio**, less favourable |
| yo | 0.78 | +0.44 | 0.73 | -0.00 | -0.36 | **noise ratio**, less favourable |
| id | 1.29 | +0.45 | 0.44 | -0.02 | +0.15 | **noise ratio**, more favourable |

Absolute levels as well:

- sw: net effect 1.22 -> relative feature better
- te: net effect 1.00 -> comparable
- yo: net effect 0.78 -> absolute feature better
- id: net effect 1.29 -> relative feature better


## Corpus profile (random benign passages)

| lang | benign passages | median nn1 | near-duplicate rate | median knn10 | sd(knn10) | sd(c) | corr(knn10, c) |
|---|---|---|---|---|---|---|---|
| sw | 48,434 | 0.807 | 0.053 | 0.741 | 0.0805 | 0.0701 | +0.926 |
| te | 57,809 | 0.857 | 0.107 | 0.799 | 0.1050 | 0.0954 | +0.951 |
| yo | 29,937 | 0.822 | 0.055 | 0.791 | 0.0840 | 0.0717 | +0.923 |
| id | 63,119 | 0.809 | 0.085 | 0.738 | 0.0918 | 0.0806 | +0.936 |

near-duplicate rate = fraction with nn1 > 0.95. The higher corr(knn10, c), the more common fluctuation subtracting c removes; the lower, the more c is mainly noise.

