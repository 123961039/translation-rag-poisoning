# Does the two-layer relative feature help or hurt (full corpus, exclusion bad)

`rel_knn10 = knn10 - c`, c = mean knn10 of the neighbours (solved from knn10 - rel_knn10, not recomputed).

- **signal cancellation** `S_c/S_k`: whether the neighbours of a poison are also isolated. Near 1 = signal removed; negative = subtracting c amplifies the signal

- **noise ratio** `sd_rel/sd_k`: <1 = c moves with knn10, subtracting is cleaner; >1 = c is extra noise

- **net effect** `d'_rel/d'_k`: >1 relative feature better, <1 absolute feature better

| lang | variant | form | n | S_k | S_c | cancellation | sd_k | sd_rel | noise ratio | d'_k | d'_rel | net effect |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sw | native | bb | 34 | +0.0839 | +0.0251 | +0.30 | 0.0728 | 0.0368 | 0.51 | 1.15 | 1.59 | **1.38** |
| sw | native | adv | 34 | +0.1594 | +0.0675 | +0.42 | 0.0816 | 0.0440 | 0.54 | 1.95 | 2.09 | **1.07** |
| sw | trans | bb | 54 | +0.0545 | +0.0296 | +0.54 | 0.0758 | 0.0315 | 0.42 | 0.72 | 0.79 | **1.10** |
| sw | trans | adv | 54 | +0.0902 | +0.0584 | +0.65 | 0.0818 | 0.0325 | 0.40 | 1.10 | 0.98 | **0.89** |
| sw | en | bb | 54 | +0.0681 | +0.0261 | +0.38 | 0.0741 | 0.0337 | 0.45 | 0.92 | 1.25 | **1.36** |
| sw | en | adv | 54 | +0.1226 | +0.0593 | +0.48 | 0.0817 | 0.0342 | 0.42 | 1.50 | 1.85 | **1.23** |
| te | native | bb | 39 | +0.1452 | +0.0453 | +0.31 | 0.0761 | 0.0422 | 0.55 | 1.91 | 2.37 | **1.24** |
| te | native | adv | 39 | +0.1467 | +0.0460 | +0.31 | 0.0730 | 0.0421 | 0.58 | 2.01 | 2.39 | **1.19** |
| te | trans | bb | 78 | +0.1395 | +0.0620 | +0.44 | 0.0793 | 0.0423 | 0.53 | 1.76 | 1.83 | **1.04** |
| te | trans | adv | 78 | +0.1611 | +0.0566 | +0.35 | 0.0728 | 0.0478 | 0.66 | 2.21 | 2.19 | **0.99** |
| te | en | bb | 78 | +0.1569 | +0.0713 | +0.45 | 0.0823 | 0.0405 | 0.49 | 1.91 | 2.12 | **1.11** |
| te | en | adv | 78 | +0.1992 | +0.0636 | +0.32 | 0.0746 | 0.0453 | 0.61 | 2.67 | 2.99 | **1.12** |
| yo | native | bb | 61 | +0.1352 | +0.0446 | +0.33 | 0.0615 | 0.0479 | 0.78 | 2.20 | 1.89 | **0.86** |
| yo | native | adv | 61 | +0.2131 | +0.0916 | +0.43 | 0.0533 | 0.0518 | 0.97 | 4.00 | 2.35 | **0.59** |
| yo | trans | bb | 66 | +0.1044 | +0.0485 | +0.46 | 0.0660 | 0.0452 | 0.68 | 1.58 | 1.24 | **0.78** |
| yo | trans | adv | 66 | +0.1542 | +0.0780 | +0.51 | 0.0615 | 0.0445 | 0.72 | 2.51 | 1.71 | **0.68** |
| yo | en | bb | 66 | +0.1310 | +0.0531 | +0.41 | 0.0635 | 0.0470 | 0.74 | 2.06 | 1.66 | **0.80** |
| yo | en | adv | 66 | +0.2092 | +0.0883 | +0.42 | 0.0580 | 0.0493 | 0.85 | 3.61 | 2.45 | **0.68** |
| id | native | bb | 20 | +0.0742 | +0.0314 | +0.42 | 0.0785 | 0.0400 | 0.51 | 0.94 | 1.07 | **1.13** |
| id | native | adv | 20 | +0.1158 | +0.0579 | +0.50 | 0.0806 | 0.0360 | 0.45 | 1.44 | 1.61 | **1.12** |
| id | trans | bb | 30 | +0.0787 | +0.0474 | +0.60 | 0.0823 | 0.0325 | 0.39 | 0.96 | 0.96 | **1.01** |
| id | trans | adv | 30 | +0.1043 | +0.0553 | +0.53 | 0.0776 | 0.0320 | 0.41 | 1.34 | 1.53 | **1.14** |
| id | en | bb | 30 | +0.1052 | +0.0587 | +0.56 | 0.0852 | 0.0298 | 0.35 | 1.24 | 1.56 | **1.26** |
| id | en | adv | 30 | +0.1202 | +0.0528 | +0.44 | 0.0786 | 0.0341 | 0.43 | 1.53 | 1.98 | **1.29** |

## Attribution by language

net effect = (1 - cancellation) / noise ratio. The two 'deviation' columns are this language's deviation from the **cross-language median** on each term (log scale, additive); the term with the larger absolute value is why it differs from the other languages.

| lang | median net effect | cancellation | noise ratio | cancellation deviation | noise deviation | difference mainly from |
|---|---|---|---|---|---|---|
| sw | 1.16 | +0.45 | 0.44 | -0.02 | +0.13 | **noise ratio**, more favourable |
| te | 1.12 | +0.34 | 0.57 | +0.17 | -0.13 | **signal cancellation**, more favourable |
| yo | 0.73 | +0.43 | 0.76 | +0.02 | -0.42 | **noise ratio**, less favourable |
| id | 1.14 | +0.52 | 0.42 | -0.14 | +0.16 | **noise ratio**, more favourable |

Absolute levels as well:

- sw: net effect 1.16 -> relative feature better
- te: net effect 1.12 -> relative feature better
- yo: net effect 0.73 -> absolute feature better
- id: net effect 1.14 -> relative feature better


## Corpus profile (random benign passages)

| lang | benign passages | median nn1 | near-duplicate rate | median knn10 | sd(knn10) | sd(c) | corr(knn10, c) |
|---|---|---|---|---|---|---|---|
| sw | 48,434 | 0.807 | 0.053 | 0.741 | 0.0805 | 0.0701 | +0.926 |
| te | 57,809 | 0.857 | 0.107 | 0.799 | 0.1050 | 0.0954 | +0.951 |
| yo | 29,937 | 0.822 | 0.055 | 0.791 | 0.0840 | 0.0717 | +0.923 |
| id | 63,119 | 0.809 | 0.085 | 0.738 | 0.0918 | 0.0806 | +0.936 |

near-duplicate rate = fraction with nn1 > 0.95. The higher corr(knn10, c), the more common fluctuation subtracting c removes; the lower, the more c is mainly noise.

