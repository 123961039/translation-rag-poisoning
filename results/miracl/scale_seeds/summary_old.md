# Scale-control robustness (trans/bb, question judgments: old, seeds [0, 1, 2, 3, 4])

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
| sw | full | 131,924 | 54 | 0.730 ± 0.005 | — |
| sw | 45,000 | 45,501 | 54 | 0.617 ± 0.012 (d -0.113 ± 0.016) | 0.711 ± 0.005 (d -0.018 ± 0.009) |
| sw | 20,000 | 20,643 | 54 | 0.559 ± 0.013 (d -0.171 ± 0.017) | 0.707 ± 0.023 (d -0.022 ± 0.026) |
| te | full | 518,079 | 78 | 0.906 ± 0.002 | — |
| te | 131,924 | 132,525 | 78 | 0.845 ± 0.006 (d -0.062 ± 0.007) | 0.880 ± 0.007 (d -0.027 ± 0.008) |
| te | 45,000 | 45,728 | 78 | 0.799 ± 0.008 (d -0.107 ± 0.008) | 0.860 ± 0.011 (d -0.047 ± 0.011) |
| te | 20,000 | 20,766 | 78 | 0.776 ± 0.010 (d -0.130 ± 0.009) | 0.855 ± 0.023 (d -0.052 ± 0.021) |
| yo | full | 49,043 | 66 | 0.825 ± 0.000 | — |
| yo | 45,000 | 45,012 | 66 | 0.827 ± 0.005 (d 0.002 ± 0.004) | 0.831 ± 0.006 (d 0.007 ± 0.006) |
| yo | 20,000 | 20,083 | 66 | 0.816 ± 0.010 (d -0.009 ± 0.010) | 0.854 ± 0.006 (d 0.029 ± 0.006) |
| id | full | 1,446,315 | 30 | 0.767 ± 0.004 | — |
| id | 131,924 | 134,502 | 30 | 0.577 ± 0.025 (d -0.190 ± 0.025) | 0.650 ± 0.021 (d -0.117 ± 0.021) |
| id | 45,000 | 47,751 | 30 | 0.552 ± 0.030 (d -0.215 ± 0.028) | 0.652 ± 0.029 (d -0.115 ± 0.027) |
| id | 20,000 | 22,805 | 30 | 0.558 ± 0.017 (d -0.209 ± 0.015) | 0.659 ± 0.013 (d -0.108 ± 0.012) |

## 1. AUROC (knn10): mean +/- sd across seeds; brackets: paired drop relative to full

| lang | size | passages | questions | keep | nokeep |
|---|---|---|---|---|---|
| sw | full | 131,924 | 54 | 0.670 ± 0.002 | — |
| sw | 45,000 | 45,501 | 54 | 0.631 ± 0.005 (d -0.039 ± 0.006) | 0.704 ± 0.010 (d 0.034 ± 0.011) |
| sw | 20,000 | 20,643 | 54 | 0.604 ± 0.008 (d -0.066 ± 0.009) | 0.724 ± 0.012 (d 0.054 ± 0.013) |
| te | full | 518,079 | 78 | 0.860 ± 0.001 | — |
| te | 131,924 | 132,525 | 78 | 0.825 ± 0.006 (d -0.035 ± 0.005) | 0.850 ± 0.003 (d -0.009 ± 0.003) |
| te | 45,000 | 45,728 | 78 | 0.808 ± 0.002 (d -0.052 ± 0.003) | 0.847 ± 0.003 (d -0.013 ± 0.003) |
| te | 20,000 | 20,766 | 78 | 0.795 ± 0.006 (d -0.064 ± 0.007) | 0.846 ± 0.005 (d -0.013 ± 0.006) |
| yo | full | 49,043 | 66 | 0.859 ± 0.001 | — |
| yo | 45,000 | 45,012 | 66 | 0.858 ± 0.002 (d -0.001 ± 0.003) | 0.861 ± 0.001 (d 0.002 ± 0.002) |
| yo | 20,000 | 20,083 | 66 | 0.849 ± 0.005 (d -0.010 ± 0.006) | 0.870 ± 0.006 (d 0.010 ± 0.007) |
| id | full | 1,446,315 | 30 | 0.722 ± 0.003 | — |
| id | 131,924 | 134,502 | 30 | 0.608 ± 0.007 (d -0.114 ± 0.008) | 0.705 ± 0.010 (d -0.017 ± 0.011) |
| id | 45,000 | 47,751 | 30 | 0.563 ± 0.007 (d -0.159 ± 0.010) | 0.719 ± 0.013 (d -0.004 ± 0.015) |
| id | 20,000 | 22,805 | 30 | 0.535 ± 0.003 (d -0.187 ± 0.005) | 0.735 ± 0.008 (d 0.013 ± 0.007) |

## 2. Effect of forcing gold to be kept (AUROC difference keep - nokeep on the same seed)

Positive = easier to detect after adding gold back; negative = adding gold back makes poisons look less isolated, harder to detect.

| lang | size | gold passages added | share of corpus | rel_knn10 | knn10 |
|---|---|---|---|---|---|
| sw | 45,000 | 502 | 1.1% | -0.095 ± 0.009 | -0.074 ± 0.006 |
| sw | 20,000 | 643 | 3.1% | -0.149 ± 0.011 | -0.120 ± 0.004 |
| te | 131,924 | 601 | 0.5% | -0.035 ± 0.005 | -0.025 ± 0.003 |
| te | 45,000 | 729 | 1.6% | -0.060 ± 0.009 | -0.039 ± 0.004 |
| te | 20,000 | 767 | 3.7% | -0.079 ± 0.013 | -0.051 ± 0.004 |
| yo | 45,000 | 12 | 0.0% | -0.004 ± 0.003 | -0.003 ± 0.002 |
| yo | 20,000 | 84 | 0.4% | -0.038 ± 0.007 | -0.021 ± 0.001 |
| id | 131,924 | 2,578 | 1.9% | -0.073 ± 0.005 | -0.097 ± 0.006 |
| id | 45,000 | 2,751 | 5.8% | -0.100 ± 0.009 | -0.156 ± 0.009 |
| id | 20,000 | 2,806 | 12.3% | -0.101 ± 0.023 | -0.200 ± 0.009 |

## 3. Across languages: Spearman rho between AUROC drop and shrink factor (full / actual passages), per seed

With only 4 language points the smallest exact permutation p is 0.083; what matters is whether seeds agree in direction.

- rel_knn10 / 131,924 / keep: seed0 rho=-1.00, seed1 rho=-1.00, seed2 rho=-1.00, seed3 rho=-1.00, seed4 rho=-1.00 (min p 0.083)
- rel_knn10 / 131,924 / nokeep: seed0 rho=-1.00, seed1 rho=-1.00, seed2 rho=-1.00, seed3 rho=-1.00, seed4 rho=-1.00 (min p 0.083)
- rel_knn10 / 45,000 / keep: seed0 rho=-1.00, seed1 rho=-0.80, seed2 rho=-1.00, seed3 rho=-0.80, seed4 rho=-0.80 (min p 0.083)
- rel_knn10 / 45,000 / nokeep: seed0 rho=-1.00, seed1 rho=-1.00, seed2 rho=-1.00, seed3 rho=-1.00, seed4 rho=-1.00 (min p 0.083)
- rel_knn10 / 20,000 / keep: seed0 rho=-0.80, seed1 rho=-0.80, seed2 rho=-0.80, seed3 rho=-0.80, seed4 rho=-0.80 (min p 0.333)
- rel_knn10 / 20,000 / nokeep: seed0 rho=-1.00, seed1 rho=-1.00, seed2 rho=-1.00, seed3 rho=-0.80, seed4 rho=-1.00 (min p 0.083)
- knn10 / 131,924 / keep: seed0 rho=-1.00, seed1 rho=-1.00, seed2 rho=-1.00, seed3 rho=-1.00, seed4 rho=-1.00 (min p 0.083)
- knn10 / 131,924 / nokeep: seed0 rho=-1.00, seed1 rho=-0.78, seed2 rho=-1.00, seed3 rho=-0.78, seed4 rho=-1.00 (min p 0.083)
- knn10 / 45,000 / keep: seed0 rho=-1.00, seed1 rho=-1.00, seed2 rho=-1.00, seed3 rho=-1.00, seed4 rho=-1.00 (min p 0.083)
- knn10 / 45,000 / nokeep: seed0 rho=-0.60, seed1 rho=-0.80, seed2 rho=-0.80, seed3 rho=+0.00, seed4 rho=+0.00 (min p 0.333)
- knn10 / 20,000 / keep: seed0 rho=-1.00, seed1 rho=-1.00, seed2 rho=-0.80, seed3 rho=-0.80, seed4 rho=-0.80 (min p 0.083)
- knn10 / 20,000 / nokeep: seed0 rho=+0.00, seed1 rho=+0.00, seed2 rho=+0.00, seed3 rho=-0.60, seed4 rho=-0.60 (min p 0.417)

## 4. Deployment metrics (rel_knn10, 5% FPR): TPR@5% and surviving-poison rate after filtering (hit@5 and not flagged)

| lang | size | mode | TPR@5% | hit@5 | surviving rate |
|---|---|---|---|---|---|
| sw | full | full | 0.16 ± 0.01 | 0.96 ± 0.00 | 0.80 ± 0.01 |
| sw | 45,000 | keep | 0.07 ± 0.02 | 0.97 ± 0.02 | 0.90 ± 0.03 |
| sw | 45,000 | nokeep | 0.16 ± 0.03 | 1.00 ± 0.01 | 0.84 ± 0.03 |
| sw | 20,000 | keep | 0.06 ± 0.02 | 0.99 ± 0.02 | 0.93 ± 0.03 |
| sw | 20,000 | nokeep | 0.12 ± 0.03 | 1.00 ± 0.00 | 0.88 ± 0.03 |
| te | full | full | 0.62 ± 0.01 | 0.97 ± 0.00 | 0.38 ± 0.01 |
| te | 131,924 | keep | 0.52 ± 0.03 | 1.00 ± 0.00 | 0.48 ± 0.03 |
| te | 131,924 | nokeep | 0.58 ± 0.03 | 1.00 ± 0.00 | 0.42 ± 0.03 |
| te | 45,000 | keep | 0.46 ± 0.04 | 1.00 ± 0.00 | 0.54 ± 0.04 |
| te | 45,000 | nokeep | 0.55 ± 0.03 | 1.00 ± 0.00 | 0.45 ± 0.03 |
| te | 20,000 | keep | 0.37 ± 0.05 | 1.00 ± 0.00 | 0.63 ± 0.05 |
| te | 20,000 | nokeep | 0.48 ± 0.03 | 1.00 ± 0.00 | 0.52 ± 0.03 |
| yo | full | full | 0.48 ± 0.02 | 0.98 ± 0.00 | 0.52 ± 0.02 |
| yo | 45,000 | keep | 0.46 ± 0.03 | 0.98 ± 0.00 | 0.54 ± 0.03 |
| yo | 45,000 | nokeep | 0.48 ± 0.04 | 0.98 ± 0.00 | 0.52 ± 0.04 |
| yo | 20,000 | keep | 0.39 ± 0.04 | 0.99 ± 0.01 | 0.60 ± 0.04 |
| yo | 20,000 | nokeep | 0.44 ± 0.03 | 0.99 ± 0.01 | 0.55 ± 0.03 |
| id | full | full | 0.27 ± 0.00 | 0.93 ± 0.00 | 0.70 ± 0.00 |
| id | 131,924 | keep | 0.04 ± 0.03 | 0.99 ± 0.01 | 0.95 ± 0.02 |
| id | 131,924 | nokeep | 0.11 ± 0.09 | 1.00 ± 0.00 | 0.89 ± 0.09 |
| id | 45,000 | keep | 0.05 ± 0.02 | 1.00 ± 0.00 | 0.95 ± 0.02 |
| id | 45,000 | nokeep | 0.13 ± 0.09 | 1.00 ± 0.00 | 0.87 ± 0.09 |
| id | 20,000 | keep | 0.02 ± 0.03 | 1.00 ± 0.00 | 0.98 ± 0.03 |
| id | 20,000 | nokeep | 0.09 ± 0.05 | 1.00 ± 0.00 | 0.91 ± 0.05 |

## 4. Deployment metrics (knn10, 5% FPR): TPR@5% and surviving-poison rate after filtering (hit@5 and not flagged)

| lang | size | mode | TPR@5% | hit@5 | surviving rate |
|---|---|---|---|---|---|
| sw | full | full | 0.20 ± 0.01 | 0.96 ± 0.00 | 0.76 ± 0.01 |
| sw | 45,000 | keep | 0.19 ± 0.04 | 0.97 ± 0.02 | 0.79 ± 0.02 |
| sw | 45,000 | nokeep | 0.26 ± 0.05 | 1.00 ± 0.01 | 0.74 ± 0.05 |
| sw | 20,000 | keep | 0.11 ± 0.02 | 0.99 ± 0.02 | 0.87 ± 0.03 |
| sw | 20,000 | nokeep | 0.23 ± 0.04 | 1.00 ± 0.00 | 0.77 ± 0.04 |
| te | full | full | 0.28 ± 0.00 | 0.97 ± 0.00 | 0.69 ± 0.00 |
| te | 131,924 | keep | 0.19 ± 0.02 | 1.00 ± 0.00 | 0.81 ± 0.02 |
| te | 131,924 | nokeep | 0.22 ± 0.02 | 1.00 ± 0.00 | 0.78 ± 0.02 |
| te | 45,000 | keep | 0.13 ± 0.02 | 1.00 ± 0.00 | 0.87 ± 0.02 |
| te | 45,000 | nokeep | 0.23 ± 0.03 | 1.00 ± 0.00 | 0.77 ± 0.03 |
| te | 20,000 | keep | 0.12 ± 0.02 | 1.00 ± 0.00 | 0.88 ± 0.02 |
| te | 20,000 | nokeep | 0.21 ± 0.03 | 1.00 ± 0.00 | 0.79 ± 0.03 |
| yo | full | full | 0.43 ± 0.02 | 0.98 ± 0.00 | 0.56 ± 0.02 |
| yo | 45,000 | keep | 0.41 ± 0.02 | 0.98 ± 0.00 | 0.57 ± 0.02 |
| yo | 45,000 | nokeep | 0.42 ± 0.02 | 0.98 ± 0.00 | 0.56 ± 0.02 |
| yo | 20,000 | keep | 0.36 ± 0.03 | 0.99 ± 0.01 | 0.63 ± 0.03 |
| yo | 20,000 | nokeep | 0.45 ± 0.02 | 0.99 ± 0.01 | 0.55 ± 0.01 |
| id | full | full | 0.10 ± 0.00 | 0.93 ± 0.00 | 0.83 ± 0.00 |
| id | 131,924 | keep | 0.05 ± 0.03 | 0.99 ± 0.01 | 0.95 ± 0.04 |
| id | 131,924 | nokeep | 0.09 ± 0.04 | 1.00 ± 0.00 | 0.91 ± 0.04 |
| id | 45,000 | keep | 0.02 ± 0.02 | 1.00 ± 0.00 | 0.98 ± 0.02 |
| id | 45,000 | nokeep | 0.08 ± 0.03 | 1.00 ± 0.00 | 0.92 ± 0.03 |
| id | 20,000 | keep | 0.02 ± 0.02 | 1.00 ± 0.00 | 0.98 ± 0.02 |
| id | 20,000 | nokeep | 0.13 ± 0.02 | 1.00 ± 0.00 | 0.87 ± 0.02 |

The surviving rate here uses all kept questions of the variant (not the questions shared by the three variants as in ml_analyze table C), so there are more questions and the numbers need not match table C.
