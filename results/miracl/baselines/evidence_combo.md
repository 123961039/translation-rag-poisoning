# Evidence check: ablation and combination (form bb, judgments native)

Only benign passages scored by the evidence check are used (random / length-matched counts listed per row), so rel_knn10 differs slightly from summary.md.
'w/o same article': poison evidence excludes the gold article; benign evidence excludes the passage's own article. 'OR': both scores mapped to quantiles among random benign passages, maximum taken, then thresholded; the total FPR is unchanged.

## A. AUROC

| lang | variant | questions | rel_knn10 | evidence | evidence w/o same article | rel OR evidence | rel OR evidence w/o same article |
|---|---|---|---|---|---|---|---|
| sw | trans | 47 | 0.735 (0.65–0.81) | **0.943 (0.91–0.96)** | 0.855 (0.81–0.90) | 0.907 (0.88–0.93) | 0.859 (0.82–0.90) |
| sw | native | 28 | 0.901 (0.84–0.95) | **0.939 (0.91–0.96)** | 0.863 (0.81–0.92) | 0.931 (0.90–0.96) | 0.927 (0.89–0.96) |
| sw | en | 47 | 0.844 (0.78–0.89) | **0.942 (0.91–0.96)** | 0.828 (0.77–0.88) | 0.931 (0.91–0.95) | 0.897 (0.86–0.92) |
| te | trans | 52 | 0.890 (0.85–0.93) | **0.956 (0.95–0.97)** | 0.902 (0.86–0.94) | 0.953 (0.94–0.97) | 0.918 (0.89–0.94) |
| te | native | 33 | 0.945 (0.92–0.97) | 0.965 (0.95–0.98) | 0.922 (0.89–0.95) | **0.970 (0.96–0.98)** | 0.948 (0.92–0.97) |
| te | en | 52 | 0.922 (0.89–0.95) | 0.954 (0.94–0.97) | 0.864 (0.83–0.89) | **0.959 (0.95–0.97)** | 0.916 (0.89–0.94) |
| yo | trans | 26 | 0.810 (0.73–0.88) | **0.923 (0.88–0.96)** | 0.870 (0.81–0.92) | 0.909 (0.86–0.95) | 0.894 (0.85–0.93) |
| yo | native | 24 | 0.913 (0.83–0.96) | 0.919 (0.86–0.96) | 0.912 (0.88–0.94) | 0.932 (0.89–0.97) | **0.939 (0.90–0.97)** |
| yo | en | 26 | 0.883 (0.84–0.93) | 0.923 (0.87–0.96) | 0.856 (0.80–0.91) | **0.942 (0.92–0.96)** | 0.921 (0.89–0.95) |
| id | trans | 28 | 0.819 (0.76–0.87) | 0.873 (0.81–0.93) | 0.865 (0.81–0.91) | **0.884 (0.84–0.92)** | 0.876 (0.84–0.91) |
| id | native | 17 | 0.852 (0.78–0.92) | 0.900 (0.84–0.95) | 0.889 (0.84–0.93) | **0.920 (0.88–0.95)** | 0.900 (0.86–0.95) |
| id | en | 28 | 0.890 (0.85–0.93) | 0.870 (0.82–0.91) | 0.860 (0.80–0.91) | 0.895 (0.86–0.93) | **0.902 (0.87–0.93)** |

## B. TPR@5%FPR

| lang | variant | questions | rel_knn10 | evidence | evidence w/o same article | rel OR evidence | rel OR evidence w/o same article |
|---|---|---|---|---|---|---|---|
| sw | trans | 47 | 0.17 | **0.55** | 0.38 | 0.38 | 0.32 |
| sw | native | 28 | **0.57** | 0.36 | 0.39 | 0.54 | 0.54 |
| sw | en | 47 | 0.32 | **0.57** | 0.30 | 0.40 | 0.36 |
| te | trans | 52 | 0.54 | **0.90** | 0.71 | 0.85 | 0.69 |
| te | native | 33 | 0.79 | 0.85 | 0.67 | **0.91** | 0.85 |
| te | en | 52 | 0.60 | **0.88** | 0.56 | 0.87 | 0.77 |
| yo | trans | 26 | 0.58 | 0.62 | 0.54 | **0.73** | 0.62 |
| yo | native | 24 | **0.75** | 0.58 | 0.50 | 0.71 | 0.75 |
| yo | en | 26 | 0.58 | 0.73 | 0.50 | **0.77** | 0.69 |
| id | trans | 28 | 0.32 | **0.46** | 0.39 | 0.46 | 0.43 |
| id | native | 17 | 0.35 | 0.53 | 0.41 | **0.65** | 0.59 |
| id | en | 28 | 0.54 | 0.50 | 0.39 | **0.57** | 0.57 |

## C. TPR@1%FPR

| lang | variant | questions | rel_knn10 | evidence | evidence w/o same article | rel OR evidence | rel OR evidence w/o same article |
|---|---|---|---|---|---|---|---|
| sw | trans | 47 | 0.04 | **0.19** | 0.09 | 0.17 | 0.09 |
| sw | native | 28 | **0.32** | 0.14 | 0.04 | 0.29 | 0.29 |
| sw | en | 47 | 0.13 | 0.21 | 0.13 | **0.28** | 0.17 |
| te | trans | 52 | 0.31 | 0.44 | 0.17 | **0.56** | 0.35 |
| te | native | 33 | 0.55 | 0.52 | 0.15 | **0.70** | 0.33 |
| te | en | 52 | 0.37 | 0.50 | 0.21 | **0.56** | 0.38 |
| yo | trans | 26 | 0.15 | **0.27** | 0.27 | 0.27 | 0.23 |
| yo | native | 24 | 0.25 | 0.21 | 0.29 | 0.29 | **0.38** |
| yo | en | 26 | 0.27 | 0.15 | 0.15 | **0.31** | 0.23 |
| id | trans | 28 | 0.07 | **0.32** | 0.25 | 0.32 | 0.25 |
| id | native | 17 | 0.18 | **0.35** | 0.24 | 0.24 | 0.12 |
| id | en | 28 | 0.18 | 0.25 | 0.25 | **0.29** | 0.25 |

## D. Surviving-poison rate after filtering (5% FPR, lower is better)

| lang | variant | questions | rel_knn10 | evidence | evidence w/o same article | rel OR evidence | rel OR evidence w/o same article |
|---|---|---|---|---|---|---|---|
| sw | trans | 47 | 0.81 | **0.45** | 0.60 | 0.62 | 0.66 |
| sw | native | 28 | **0.43** | 0.61 | 0.57 | 0.46 | 0.46 |
| sw | en | 47 | 0.66 | **0.43** | 0.68 | 0.60 | 0.62 |
| te | trans | 52 | 0.46 | **0.10** | 0.29 | 0.15 | 0.31 |
| te | native | 33 | 0.21 | 0.15 | 0.33 | **0.09** | 0.15 |
| te | en | 52 | 0.40 | **0.10** | 0.42 | 0.13 | 0.23 |
| yo | trans | 26 | 0.42 | 0.38 | 0.46 | **0.27** | 0.38 |
| yo | native | 24 | **0.25** | 0.42 | 0.50 | 0.29 | 0.25 |
| yo | en | 26 | 0.42 | 0.27 | 0.50 | **0.23** | 0.31 |
| id | trans | 28 | 0.68 | **0.50** | 0.57 | 0.54 | 0.57 |
| id | native | 17 | 0.65 | 0.41 | 0.47 | **0.35** | 0.41 |
| id | en | 28 | 0.46 | 0.50 | 0.61 | **0.43** | 0.43 |

## E. Summary

| metric | rel_knn10 | evidence | evidence w/o same article | rel OR evidence | rel OR evidence w/o same article |
|---|---|---|---|---|---|
| mean AUROC | 0.867 | 0.926 | 0.874 | 0.928 | 0.908 |
| mean TPR@5% | 0.508 | 0.629 | 0.479 | 0.653 | 0.598 |
| mean TPR@1% | 0.234 | 0.297 | 0.186 | 0.355 | 0.255 |
| mean surviving-poison rate | 0.488 | 0.359 | 0.500 | 0.347 | 0.399 |

## F. Share of poisons whose top-5 evidence (original setting) contains a gold-article passage

| lang | variant | share |
|---|---|---|
| sw | trans | 0.94 |
| sw | native | 0.96 |
| sw | en | 0.94 |
| te | trans | 0.98 |
| te | native | 0.97 |
| te | en | 0.98 |
| yo | trans | 0.96 |
| yo | native | 0.92 |
| yo | en | 0.96 |
| id | trans | 0.89 |
| id | native | 0.88 |
| id | en | 0.93 |

## G. Cost

Evidence check (Qwen3-14B-AWQ, NVIDIA GeForce RTX 4080 SUPER): 4.3 passages/s, mean prompt 828 tokens (excludes evidence retrieval and encoding time; prefix caching disabled, close to the real cost of one-by-one ingestion).
For comparison: rel_knn10 scores 10k-700k passages/s and encoding runs at 654-1,084 passages/s (efficiency.md).
Benign passages left with fewer than 5 evidence passages after removing their own article: sw 15/2479, te 6/2488, yo 43/2407, id 13/2496
