# Evidence check: ablation and combination (form bb, judgments none)

Only benign passages scored by the evidence check are used (random / length-matched counts listed per row), so rel_knn10 differs slightly from summary.md.
'w/o same article': poison evidence excludes the gold article; benign evidence excludes the passage's own article. 'OR': both scores mapped to quantiles among random benign passages, maximum taken, then thresholded; the total FPR is unchanged.

## A. AUROC

| lang | variant | questions | rel_knn10 | evidence | evidence w/o same article | rel OR evidence | rel OR evidence w/o same article |
|---|---|---|---|---|---|---|---|
| sw | trans | 88 | 0.758 (0.70–0.81) | **0.906 (0.88–0.93)** | 0.842 (0.81–0.88) | 0.875 (0.85–0.90) | 0.842 (0.81–0.88) |
| sw | native | 56 | 0.919 (0.88–0.95) | 0.896 (0.87–0.92) | 0.854 (0.82–0.89) | **0.935 (0.91–0.95)** | 0.926 (0.90–0.95) |
| sw | en | 88 | 0.849 (0.81–0.88) | 0.894 (0.86–0.92) | 0.819 (0.78–0.86) | **0.908 (0.88–0.93)** | 0.884 (0.86–0.91) |
| te | trans | 100 | 0.900 (0.87–0.92) | 0.920 (0.89–0.94) | 0.906 (0.88–0.93) | **0.932 (0.92–0.95)** | 0.919 (0.90–0.94) |
| te | native | 51 | 0.939 (0.90–0.96) | 0.945 (0.91–0.97) | 0.917 (0.88–0.95) | **0.964 (0.95–0.97)** | 0.947 (0.93–0.96) |
| te | en | 100 | 0.933 (0.91–0.95) | 0.910 (0.89–0.93) | 0.861 (0.84–0.89) | **0.948 (0.94–0.96)** | 0.923 (0.90–0.94) |
| yo | trans | 80 | 0.787 (0.74–0.83) | **0.920 (0.90–0.94)** | 0.895 (0.87–0.92) | 0.893 (0.87–0.92) | 0.877 (0.85–0.90) |
| yo | native | 70 | 0.926 (0.89–0.95) | 0.919 (0.89–0.94) | 0.909 (0.89–0.93) | 0.936 (0.92–0.95) | **0.942 (0.93–0.96)** |
| yo | en | 80 | 0.892 (0.87–0.92) | 0.916 (0.89–0.94) | 0.872 (0.84–0.90) | **0.932 (0.91–0.95)** | 0.904 (0.88–0.93) |
| id | trans | 62 | 0.790 (0.75–0.83) | 0.853 (0.81–0.89) | **0.863 (0.83–0.89)** | 0.850 (0.81–0.89) | 0.848 (0.81–0.88) |
| id | native | 40 | 0.823 (0.75–0.88) | 0.884 (0.85–0.92) | 0.875 (0.84–0.91) | **0.897 (0.87–0.92)** | 0.884 (0.84–0.92) |
| id | en | 62 | **0.871 (0.84–0.90)** | 0.832 (0.79–0.87) | 0.846 (0.81–0.88) | 0.861 (0.83–0.89) | 0.871 (0.84–0.90) |

## B. TPR@5%FPR

| lang | variant | questions | rel_knn10 | evidence | evidence w/o same article | rel OR evidence | rel OR evidence w/o same article |
|---|---|---|---|---|---|---|---|
| sw | trans | 88 | 0.22 | **0.42** | 0.28 | 0.34 | 0.30 |
| sw | native | 56 | **0.61** | 0.23 | 0.25 | 0.57 | 0.55 |
| sw | en | 88 | 0.36 | **0.43** | 0.24 | 0.41 | 0.39 |
| te | trans | 100 | 0.56 | **0.77** | 0.66 | 0.73 | 0.66 |
| te | native | 51 | 0.76 | 0.84 | 0.71 | **0.88** | 0.80 |
| te | en | 100 | 0.66 | 0.73 | 0.54 | **0.81** | 0.76 |
| yo | trans | 80 | 0.44 | 0.61 | 0.54 | **0.64** | 0.56 |
| yo | native | 70 | **0.73** | 0.54 | 0.53 | 0.70 | 0.73 |
| yo | en | 80 | 0.60 | 0.68 | 0.42 | **0.70** | 0.60 |
| id | trans | 62 | 0.29 | 0.39 | 0.39 | **0.44** | 0.40 |
| id | native | 40 | 0.35 | 0.47 | 0.42 | **0.50** | 0.50 |
| id | en | 62 | 0.39 | 0.35 | 0.32 | **0.45** | 0.45 |

## C. TPR@1%FPR

| lang | variant | questions | rel_knn10 | evidence | evidence w/o same article | rel OR evidence | rel OR evidence w/o same article |
|---|---|---|---|---|---|---|---|
| sw | trans | 88 | 0.08 | **0.15** | 0.07 | 0.15 | 0.11 |
| sw | native | 56 | **0.38** | 0.09 | 0.02 | 0.27 | 0.25 |
| sw | en | 88 | 0.15 | 0.16 | 0.11 | **0.24** | 0.17 |
| te | trans | 100 | 0.36 | 0.35 | 0.17 | **0.46** | 0.36 |
| te | native | 51 | 0.53 | 0.43 | 0.16 | **0.67** | 0.37 |
| te | en | 100 | 0.38 | 0.33 | 0.17 | **0.47** | 0.37 |
| yo | trans | 80 | 0.17 | 0.20 | **0.28** | 0.25 | 0.23 |
| yo | native | 70 | **0.34** | 0.14 | 0.21 | 0.34 | 0.34 |
| yo | en | 80 | 0.28 | 0.23 | 0.16 | **0.31** | 0.24 |
| id | trans | 62 | 0.08 | **0.24** | 0.19 | 0.23 | 0.18 |
| id | native | 40 | 0.20 | **0.23** | 0.17 | 0.17 | 0.10 |
| id | en | 62 | 0.16 | 0.19 | 0.19 | **0.23** | 0.18 |

## D. Surviving-poison rate after filtering (5% FPR, lower is better)

| lang | variant | questions | rel_knn10 | evidence | evidence w/o same article | rel OR evidence | rel OR evidence w/o same article |
|---|---|---|---|---|---|---|---|
| sw | trans | 88 | 0.75 | **0.56** | 0.68 | 0.64 | 0.67 |
| sw | native | 56 | **0.39** | 0.75 | 0.73 | 0.43 | 0.45 |
| sw | en | 88 | 0.61 | **0.55** | 0.73 | 0.58 | 0.59 |
| te | trans | 100 | 0.44 | **0.23** | 0.34 | 0.27 | 0.34 |
| te | native | 51 | 0.24 | 0.16 | 0.29 | **0.12** | 0.20 |
| te | en | 100 | 0.34 | 0.25 | 0.45 | **0.19** | 0.24 |
| yo | trans | 80 | 0.56 | 0.38 | 0.45 | **0.36** | 0.44 |
| yo | native | 70 | **0.27** | 0.44 | 0.46 | 0.30 | 0.27 |
| yo | en | 80 | 0.40 | 0.33 | 0.56 | **0.30** | 0.40 |
| id | trans | 62 | 0.69 | 0.56 | 0.56 | **0.53** | 0.56 |
| id | native | 40 | 0.65 | **0.50** | 0.53 | 0.50 | 0.50 |
| id | en | 62 | 0.60 | 0.61 | 0.65 | **0.53** | 0.53 |

## E. Summary

| metric | rel_knn10 | evidence | evidence w/o same article | rel OR evidence | rel OR evidence w/o same article |
|---|---|---|---|---|---|
| mean AUROC | 0.866 | 0.900 | 0.872 | 0.911 | 0.897 |
| mean TPR@5% | 0.497 | 0.540 | 0.442 | 0.597 | 0.559 |
| mean TPR@1% | 0.259 | 0.228 | 0.159 | 0.315 | 0.241 |
| mean surviving-poison rate | 0.496 | 0.442 | 0.536 | 0.396 | 0.432 |

## F. Share of poisons whose top-5 evidence (original setting) contains a gold-article passage

| lang | variant | share |
|---|---|---|
| sw | trans | 0.93 |
| sw | native | 0.95 |
| sw | en | 0.92 |
| te | trans | 0.95 |
| te | native | 0.94 |
| te | en | 0.96 |
| yo | trans | 0.90 |
| yo | native | 0.87 |
| yo | en | 0.96 |
| id | trans | 0.84 |
| id | native | 0.80 |
| id | en | 0.85 |

## G. Cost

Evidence check (Qwen3-14B-AWQ, NVIDIA GeForce RTX 4080 SUPER): 4.3 passages/s, mean prompt 828 tokens (excludes evidence retrieval and encoding time; prefix caching disabled, close to the real cost of one-by-one ingestion).
For comparison: rel_knn10 scores 10k-700k passages/s and encoding runs at 654-1,084 passages/s (efficiency.md).
Benign passages left with fewer than 5 evidence passages after removing their own article: sw 15/2479, te 6/2488, yo 43/2407, id 13/2496
