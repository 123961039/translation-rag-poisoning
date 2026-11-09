# Scale-control robustness (trans/bb, question judgments: native, seeds [0, 1, 2, 3, 4])

keep = all dev gold passages added back when downsampling (original procedure); nokeep = the same random subset of the same seed, without adding gold. AUROC is always against length-matched benign passages; +/- is the sd across seeds.

## 0. Self-check: does seed 0 + keep reproduce the original results

| lang | size | max poison feature diff | length-matched controls | hit@5 |
|---|---|---|---|---|
| sw | full | 0.0e+00 | consistent | consistent |
| sw | 45,000 | 0.0e+00 | consistent | consistent |
| te | full | 0.0e+00 | consistent | consistent |
| te | 131,924 | 0.0e+00 | consistent | consistent |
| te | 45,000 | 0.0e+00 | consistent | consistent |
| yo | full | 0.0e+00 | consistent | consistent |
| yo | 45,000 | 0.0e+00 | consistent | consistent |
| id | full | 2.6e-02 | consistent | consistent |
| id | 131,924 | 1.6e-03 | consistent | consistent |
| id | 45,000 | 8.7e-03 | consistent | consistent |

The poison feature difference should be 0 or below 1e-3 (tie order of fp16 retrieval may differ); larger means the code or data changed.

## 1. AUROC (rel_knn10): mean +/- sd across seeds; brackets: paired drop relative to full

| lang | size | passages | questions | keep | nokeep |
|---|---|---|---|---|---|
| sw | full | 131,924 | 47 | 0.741 ± 0.004 | — |
| sw | 45,000 | 45,501 | 47 | 0.632 ± 0.016 (d -0.108 ± 0.019) | 0.714 ± 0.013 (d -0.027 ± 0.017) |
| sw | 20,000 | 20,643 | 47 | 0.581 ± 0.011 (d -0.159 ± 0.014) | 0.703 ± 0.028 (d -0.037 ± 0.031) |
| te | full | 518,079 | 52 | 0.888 ± 0.002 | — |
| te | 131,924 | 132,525 | 52 | 0.828 ± 0.011 (d -0.060 ± 0.012) | 0.869 ± 0.013 (d -0.019 ± 0.014) |
| te | 45,000 | 45,728 | 52 | 0.778 ± 0.015 (d -0.110 ± 0.015) | 0.852 ± 0.024 (d -0.036 ± 0.024) |
| te | 20,000 | 20,766 | 52 | 0.751 ± 0.012 (d -0.137 ± 0.011) | 0.842 ± 0.020 (d -0.046 ± 0.019) |
| yo | full | 49,043 | 26 | 0.824 ± 0.000 | — |
| yo | 45,000 | 45,012 | 26 | 0.833 ± 0.008 (d 0.009 ± 0.008) | 0.841 ± 0.012 (d 0.017 ± 0.012) |
| yo | 20,000 | 20,083 | 26 | 0.839 ± 0.020 (d 0.015 ± 0.020) | 0.886 ± 0.017 (d 0.062 ± 0.017) |
| id | full | 1,446,315 | 28 | 0.815 ± 0.004 | — |
| id | 131,924 | 134,502 | 28 | 0.602 ± 0.017 (d -0.213 ± 0.014) | 0.682 ± 0.024 (d -0.133 ± 0.022) |
| id | 45,000 | 47,751 | 28 | 0.575 ± 0.044 (d -0.240 ± 0.041) | 0.705 ± 0.049 (d -0.110 ± 0.046) |
| id | 20,000 | 22,805 | 28 | 0.581 ± 0.013 (d -0.234 ± 0.014) | 0.705 ± 0.021 (d -0.110 ± 0.022) |

## 1. AUROC (knn10): mean +/- sd across seeds; brackets: paired drop relative to full

| lang | size | passages | questions | keep | nokeep |
|---|---|---|---|---|---|
| sw | full | 131,924 | 47 | 0.667 ± 0.002 | — |
| sw | 45,000 | 45,501 | 47 | 0.632 ± 0.005 (d -0.035 ± 0.006) | 0.704 ± 0.011 (d 0.037 ± 0.012) |
| sw | 20,000 | 20,643 | 47 | 0.607 ± 0.010 (d -0.060 ± 0.010) | 0.726 ± 0.014 (d 0.059 ± 0.016) |
| te | full | 518,079 | 52 | 0.867 ± 0.001 | — |
| te | 131,924 | 132,525 | 52 | 0.840 ± 0.004 (d -0.027 ± 0.004) | 0.864 ± 0.004 (d -0.002 ± 0.005) |
| te | 45,000 | 45,728 | 52 | 0.827 ± 0.004 (d -0.040 ± 0.005) | 0.866 ± 0.007 (d -0.001 ± 0.007) |
| te | 20,000 | 20,766 | 52 | 0.818 ± 0.008 (d -0.049 ± 0.008) | 0.868 ± 0.009 (d 0.001 ± 0.009) |
| yo | full | 49,043 | 26 | 0.859 ± 0.001 | — |
| yo | 45,000 | 45,012 | 26 | 0.857 ± 0.003 (d -0.001 ± 0.004) | 0.862 ± 0.004 (d 0.003 ± 0.004) |
| yo | 20,000 | 20,083 | 26 | 0.848 ± 0.011 (d -0.011 ± 0.011) | 0.875 ± 0.012 (d 0.016 ± 0.013) |
| id | full | 1,446,315 | 28 | 0.725 ± 0.002 | — |
| id | 131,924 | 134,502 | 28 | 0.631 ± 0.005 (d -0.094 ± 0.005) | 0.732 ± 0.006 (d 0.007 ± 0.006) |
| id | 45,000 | 47,751 | 28 | 0.584 ± 0.010 (d -0.141 ± 0.011) | 0.749 ± 0.017 (d 0.023 ± 0.018) |
| id | 20,000 | 22,805 | 28 | 0.557 ± 0.004 (d -0.168 ± 0.007) | 0.761 ± 0.009 (d 0.036 ± 0.008) |

## 2. Effect of forcing gold to be kept (AUROC difference keep - nokeep on the same seed)

Positive = easier to detect after adding gold back; negative = adding gold back makes poisons look less isolated, harder to detect.

| lang | size | gold passages added | share of corpus | rel_knn10 | knn10 |
|---|---|---|---|---|---|
| sw | 45,000 | 502 | 1.1% | -0.082 ± 0.010 | -0.072 ± 0.007 |
| sw | 20,000 | 643 | 3.1% | -0.122 ± 0.018 | -0.119 ± 0.008 |
| te | 131,924 | 601 | 0.5% | -0.041 ± 0.008 | -0.025 ± 0.004 |
| te | 45,000 | 729 | 1.6% | -0.074 ± 0.013 | -0.039 ± 0.004 |
| te | 20,000 | 767 | 3.7% | -0.091 ± 0.008 | -0.050 ± 0.003 |
| yo | 45,000 | 12 | 0.0% | -0.008 ± 0.006 | -0.004 ± 0.002 |
| yo | 20,000 | 84 | 0.4% | -0.046 ± 0.014 | -0.027 ± 0.003 |
| id | 131,924 | 2,578 | 1.9% | -0.080 ± 0.012 | -0.101 ± 0.006 |
| id | 45,000 | 2,751 | 5.8% | -0.131 ± 0.007 | -0.165 ± 0.008 |
| id | 20,000 | 2,806 | 12.3% | -0.124 ± 0.027 | -0.204 ± 0.011 |

## 3. Across languages: Spearman rho between AUROC drop and shrink factor (full / actual passages), per seed

With only 4 language points the smallest exact permutation p is 0.083; what matters is whether seeds agree in direction.

- rel_knn10 / 131,924 / keep: seed0 rho=-1.00, seed1 rho=-1.00, seed2 rho=-1.00, seed3 rho=-1.00, seed4 rho=-1.00 (min p 0.083)
- rel_knn10 / 131,924 / nokeep: seed0 rho=-1.00, seed1 rho=-1.00, seed2 rho=-1.00, seed3 rho=-1.00, seed4 rho=-1.00 (min p 0.083)
- rel_knn10 / 45,000 / keep: seed0 rho=-1.00, seed1 rho=-1.00, seed2 rho=-1.00, seed3 rho=-0.80, seed4 rho=-0.80 (min p 0.083)
- rel_knn10 / 45,000 / nokeep: seed0 rho=-1.00, seed1 rho=-1.00, seed2 rho=-1.00, seed3 rho=-0.80, seed4 rho=-0.80 (min p 0.083)
- rel_knn10 / 20,000 / keep: seed0 rho=-0.80, seed1 rho=-0.80, seed2 rho=-0.80, seed3 rho=-0.80, seed4 rho=-0.80 (min p 0.333)
- rel_knn10 / 20,000 / nokeep: seed0 rho=-1.00, seed1 rho=-1.00, seed2 rho=-1.00, seed3 rho=-0.80, seed4 rho=-0.80 (min p 0.083)
- knn10 / 131,924 / keep: seed0 rho=-1.00, seed1 rho=-1.00, seed2 rho=-1.00, seed3 rho=-1.00, seed4 rho=-1.00 (min p 0.083)
- knn10 / 131,924 / nokeep: seed0 rho=+1.00, seed1 rho=+0.33, seed2 rho=-0.33, seed3 rho=+0.33, seed4 rho=+0.33 (min p 0.083)
- knn10 / 45,000 / keep: seed0 rho=-1.00, seed1 rho=-1.00, seed2 rho=-1.00, seed3 rho=-0.80, seed4 rho=-0.80 (min p 0.083)
- knn10 / 45,000 / nokeep: seed0 rho=+0.40, seed1 rho=-0.60, seed2 rho=+0.00, seed3 rho=+0.40, seed4 rho=+0.40 (min p 0.417)
- knn10 / 20,000 / keep: seed0 rho=-1.00, seed1 rho=-1.00, seed2 rho=-0.80, seed3 rho=-0.80, seed4 rho=-0.80 (min p 0.083)
- knn10 / 20,000 / nokeep: seed0 rho=+0.40, seed1 rho=+0.00, seed2 rho=+0.00, seed3 rho=+0.00, seed4 rho=+0.40 (min p 0.750)

## 4. Deployment metrics (rel_knn10, 5% FPR): TPR@5% and surviving-poison rate after filtering (hit@5 and not flagged)

| lang | size | mode | TPR@5% | hit@5 | surviving rate |
|---|---|---|---|---|---|
| sw | full | full | 0.20 ± 0.02 | 0.98 ± 0.00 | 0.77 ± 0.02 |
| sw | 45,000 | keep | 0.09 ± 0.02 | 0.99 ± 0.01 | 0.90 ± 0.02 |
| sw | 45,000 | nokeep | 0.19 ± 0.03 | 1.00 ± 0.01 | 0.81 ± 0.03 |
| sw | 20,000 | keep | 0.08 ± 0.02 | 0.99 ± 0.01 | 0.91 ± 0.02 |
| sw | 20,000 | nokeep | 0.16 ± 0.03 | 1.00 ± 0.00 | 0.84 ± 0.03 |
| te | full | full | 0.55 ± 0.01 | 0.96 ± 0.00 | 0.45 ± 0.01 |
| te | 131,924 | keep | 0.43 ± 0.04 | 1.00 ± 0.00 | 0.57 ± 0.04 |
| te | 131,924 | nokeep | 0.50 ± 0.04 | 1.00 ± 0.00 | 0.50 ± 0.04 |
| te | 45,000 | keep | 0.35 ± 0.04 | 1.00 ± 0.00 | 0.65 ± 0.04 |
| te | 45,000 | nokeep | 0.45 ± 0.03 | 1.00 ± 0.00 | 0.55 ± 0.03 |
| te | 20,000 | keep | 0.32 ± 0.04 | 1.00 ± 0.00 | 0.68 ± 0.04 |
| te | 20,000 | nokeep | 0.42 ± 0.04 | 1.00 ± 0.00 | 0.58 ± 0.04 |
| yo | full | full | 0.58 ± 0.00 | 1.00 ± 0.00 | 0.42 ± 0.00 |
| yo | 45,000 | keep | 0.55 ± 0.02 | 1.00 ± 0.00 | 0.45 ± 0.02 |
| yo | 45,000 | nokeep | 0.55 ± 0.02 | 1.00 ± 0.00 | 0.45 ± 0.02 |
| yo | 20,000 | keep | 0.49 ± 0.07 | 1.00 ± 0.00 | 0.51 ± 0.07 |
| yo | 20,000 | nokeep | 0.52 ± 0.06 | 1.00 ± 0.00 | 0.48 ± 0.06 |
| id | full | full | 0.29 ± 0.02 | 0.96 ± 0.00 | 0.71 ± 0.02 |
| id | 131,924 | keep | 0.06 ± 0.02 | 1.00 ± 0.00 | 0.94 ± 0.02 |
| id | 131,924 | nokeep | 0.17 ± 0.06 | 1.00 ± 0.00 | 0.83 ± 0.06 |
| id | 45,000 | keep | 0.06 ± 0.03 | 1.00 ± 0.00 | 0.94 ± 0.03 |
| id | 45,000 | nokeep | 0.16 ± 0.11 | 1.00 ± 0.00 | 0.84 ± 0.11 |
| id | 20,000 | keep | 0.04 ± 0.02 | 1.00 ± 0.00 | 0.96 ± 0.02 |
| id | 20,000 | nokeep | 0.09 ± 0.06 | 1.00 ± 0.00 | 0.91 ± 0.06 |

## 4. Deployment metrics (knn10, 5% FPR): TPR@5% and surviving-poison rate after filtering (hit@5 and not flagged)

| lang | size | mode | TPR@5% | hit@5 | surviving rate |
|---|---|---|---|---|---|
| sw | full | full | 0.21 ± 0.02 | 0.98 ± 0.00 | 0.77 ± 0.02 |
| sw | 45,000 | keep | 0.19 ± 0.03 | 0.99 ± 0.01 | 0.80 ± 0.02 |
| sw | 45,000 | nokeep | 0.26 ± 0.05 | 1.00 ± 0.01 | 0.74 ± 0.06 |
| sw | 20,000 | keep | 0.12 ± 0.02 | 0.99 ± 0.01 | 0.87 ± 0.03 |
| sw | 20,000 | nokeep | 0.24 ± 0.03 | 1.00 ± 0.00 | 0.76 ± 0.03 |
| te | full | full | 0.35 ± 0.00 | 0.96 ± 0.00 | 0.62 ± 0.00 |
| te | 131,924 | keep | 0.27 ± 0.02 | 1.00 ± 0.00 | 0.73 ± 0.02 |
| te | 131,924 | nokeep | 0.30 ± 0.03 | 1.00 ± 0.00 | 0.70 ± 0.03 |
| te | 45,000 | keep | 0.18 ± 0.05 | 1.00 ± 0.00 | 0.82 ± 0.05 |
| te | 45,000 | nokeep | 0.32 ± 0.03 | 1.00 ± 0.00 | 0.68 ± 0.03 |
| te | 20,000 | keep | 0.17 ± 0.03 | 1.00 ± 0.00 | 0.83 ± 0.03 |
| te | 20,000 | nokeep | 0.31 ± 0.04 | 1.00 ± 0.00 | 0.69 ± 0.04 |
| yo | full | full | 0.39 ± 0.06 | 1.00 ± 0.00 | 0.61 ± 0.06 |
| yo | 45,000 | keep | 0.35 ± 0.03 | 1.00 ± 0.00 | 0.65 ± 0.03 |
| yo | 45,000 | nokeep | 0.38 ± 0.04 | 1.00 ± 0.00 | 0.62 ± 0.04 |
| yo | 20,000 | keep | 0.38 ± 0.06 | 1.00 ± 0.00 | 0.62 ± 0.06 |
| yo | 20,000 | nokeep | 0.49 ± 0.05 | 1.00 ± 0.00 | 0.51 ± 0.05 |
| id | full | full | 0.14 ± 0.00 | 0.96 ± 0.00 | 0.86 ± 0.00 |
| id | 131,924 | keep | 0.09 ± 0.03 | 1.00 ± 0.00 | 0.91 ± 0.03 |
| id | 131,924 | nokeep | 0.19 ± 0.03 | 1.00 ± 0.00 | 0.81 ± 0.03 |
| id | 45,000 | keep | 0.06 ± 0.02 | 1.00 ± 0.00 | 0.94 ± 0.02 |
| id | 45,000 | nokeep | 0.15 ± 0.05 | 1.00 ± 0.00 | 0.85 ± 0.05 |
| id | 20,000 | keep | 0.06 ± 0.02 | 1.00 ± 0.00 | 0.94 ± 0.02 |
| id | 20,000 | nokeep | 0.24 ± 0.02 | 1.00 ± 0.00 | 0.76 ± 0.02 |

The surviving rate here uses all kept questions of the variant (not the questions shared by the three variants as in ml_analyze table C), so there are more questions and the numbers need not match table C.
