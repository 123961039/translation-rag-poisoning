# Does the two-layer relative feature help or hurt (sub131924, exclusion bad)

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
| te | native | bb | 39 | +0.1370 | +0.0550 | +0.40 | 0.0808 | 0.0421 | 0.52 | 1.70 | 1.95 | **1.15** |
| te | native | adv | 39 | +0.1396 | +0.0570 | +0.41 | 0.0760 | 0.0429 | 0.56 | 1.84 | 1.93 | **1.05** |
| te | trans | bb | 78 | +0.1344 | +0.0733 | +0.55 | 0.0848 | 0.0429 | 0.51 | 1.58 | 1.42 | **0.90** |
| te | trans | adv | 78 | +0.1489 | +0.0638 | +0.43 | 0.0775 | 0.0470 | 0.61 | 1.92 | 1.81 | **0.94** |
| te | en | bb | 78 | +0.1536 | +0.0849 | +0.55 | 0.0890 | 0.0407 | 0.46 | 1.73 | 1.69 | **0.98** |
| te | en | adv | 78 | +0.1815 | +0.0636 | +0.35 | 0.0804 | 0.0483 | 0.60 | 2.26 | 2.44 | **1.08** |
| yo | native | bb | 61 | +0.1352 | +0.0446 | +0.33 | 0.0615 | 0.0479 | 0.78 | 2.20 | 1.89 | **0.86** |
| yo | native | adv | 61 | +0.2131 | +0.0916 | +0.43 | 0.0533 | 0.0518 | 0.97 | 4.00 | 2.35 | **0.59** |
| yo | trans | bb | 66 | +0.1044 | +0.0485 | +0.46 | 0.0660 | 0.0452 | 0.68 | 1.58 | 1.24 | **0.78** |
| yo | trans | adv | 66 | +0.1542 | +0.0780 | +0.51 | 0.0615 | 0.0445 | 0.72 | 2.51 | 1.71 | **0.68** |
| yo | en | bb | 66 | +0.1310 | +0.0531 | +0.41 | 0.0635 | 0.0470 | 0.74 | 2.06 | 1.66 | **0.80** |
| yo | en | adv | 66 | +0.2092 | +0.0883 | +0.42 | 0.0580 | 0.0493 | 0.85 | 3.61 | 2.45 | **0.68** |
| id | native | bb | 20 | +0.0460 | +0.0311 | +0.68 | 0.0882 | 0.0360 | 0.41 | 0.52 | 0.41 | **0.79** |
| id | native | adv | 20 | +0.0859 | +0.0550 | +0.64 | 0.0917 | 0.0397 | 0.43 | 0.94 | 0.78 | **0.83** |
| id | trans | bb | 30 | +0.0585 | +0.0511 | +0.87 | 0.0949 | 0.0322 | 0.34 | 0.62 | 0.23 | **0.37** |
| id | trans | adv | 30 | +0.0828 | +0.0524 | +0.63 | 0.0888 | 0.0350 | 0.39 | 0.93 | 0.87 | **0.93** |
| id | en | bb | 30 | +0.0890 | +0.0623 | +0.70 | 0.0991 | 0.0332 | 0.33 | 0.90 | 0.80 | **0.90** |
| id | en | adv | 30 | +0.0965 | +0.0506 | +0.52 | 0.0896 | 0.0351 | 0.39 | 1.08 | 1.31 | **1.21** |

## Attribution by language

net effect = (1 - cancellation) / noise ratio. The two 'deviation' columns are this language's deviation from the **cross-language median** on each term (log scale, additive); the term with the larger absolute value is why it differs from the other languages.

| lang | median net effect | cancellation | noise ratio | cancellation deviation | noise deviation | difference mainly from |
|---|---|---|---|---|---|---|
| sw | 1.16 | +0.45 | 0.44 | -0.02 | +0.11 | **noise ratio**, more favourable |
| te | 1.01 | +0.42 | 0.54 | +0.04 | -0.11 | **noise ratio**, less favourable |
| yo | 0.73 | +0.43 | 0.76 | +0.02 | -0.44 | **noise ratio**, less favourable |
| id | 0.86 | +0.66 | 0.39 | -0.49 | +0.22 | **signal cancellation**, less favourable |

Absolute levels as well:

- sw: net effect 1.16 -> relative feature better
- te: net effect 1.01 -> comparable
- yo: net effect 0.73 -> absolute feature better
- id: net effect 0.86 -> absolute feature better


## Corpus profile (random benign passages)

| lang | benign passages | median nn1 | near-duplicate rate | median knn10 | sd(knn10) | sd(c) | corr(knn10, c) |
|---|---|---|---|---|---|---|---|
| sw | 48,434 | 0.807 | 0.053 | 0.741 | 0.0805 | 0.0701 | +0.926 |
| te | 40,581 | 0.820 | 0.044 | 0.754 | 0.1167 | 0.1079 | +0.954 |
| yo | 29,937 | 0.822 | 0.055 | 0.791 | 0.0840 | 0.0717 | +0.923 |
| id | 39,942 | 0.725 | 0.032 | 0.656 | 0.1002 | 0.0898 | +0.946 |

near-duplicate rate = fraction with nn1 > 0.95. The higher corr(knn10, c), the more common fluctuation subtracting c removes; the lower, the more c is mainly noise.

