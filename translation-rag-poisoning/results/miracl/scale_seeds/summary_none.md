# Scale-control robustness (trans/bb, question judgments: none, seeds [0, 1, 2, 3, 4])

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
| sw | full | 131,924 | 88 | 0.763 ± 0.004 | — |
| sw | 45,000 | 45,501 | 88 | 0.667 ± 0.014 (d -0.096 ± 0.017) | 0.745 ± 0.005 (d -0.018 ± 0.008) |
| sw | 20,000 | 20,643 | 88 | 0.608 ± 0.013 (d -0.155 ± 0.015) | 0.736 ± 0.020 (d -0.027 ± 0.023) |
| te | full | 518,079 | 100 | 0.898 ± 0.002 | — |
| te | 131,924 | 132,525 | 100 | 0.825 ± 0.005 (d -0.073 ± 0.006) | 0.867 ± 0.006 (d -0.030 ± 0.008) |
| te | 45,000 | 45,728 | 100 | 0.782 ± 0.007 (d -0.115 ± 0.008) | 0.851 ± 0.011 (d -0.047 ± 0.012) |
| te | 20,000 | 20,766 | 100 | 0.760 ± 0.008 (d -0.138 ± 0.008) | 0.846 ± 0.016 (d -0.052 ± 0.015) |
| yo | full | 49,043 | 80 | 0.802 ± 0.000 | — |
| yo | 45,000 | 45,012 | 80 | 0.803 ± 0.005 (d 0.000 ± 0.005) | 0.807 ± 0.006 (d 0.005 ± 0.006) |
| yo | 20,000 | 20,083 | 80 | 0.786 ± 0.012 (d -0.016 ± 0.012) | 0.828 ± 0.008 (d 0.026 ± 0.008) |
| id | full | 1,446,315 | 62 | 0.787 ± 0.004 | — |
| id | 131,924 | 134,502 | 62 | 0.578 ± 0.009 (d -0.208 ± 0.008) | 0.651 ± 0.009 (d -0.135 ± 0.007) |
| id | 45,000 | 47,751 | 62 | 0.546 ± 0.015 (d -0.241 ± 0.013) | 0.638 ± 0.020 (d -0.149 ± 0.017) |
| id | 20,000 | 22,805 | 62 | 0.546 ± 0.022 (d -0.241 ± 0.023) | 0.637 ± 0.014 (d -0.150 ± 0.016) |

## 1. AUROC (knn10): mean +/- sd across seeds; brackets: paired drop relative to full

| lang | size | passages | questions | keep | nokeep |
|---|---|---|---|---|---|
| sw | full | 131,924 | 88 | 0.686 ± 0.002 | — |
| sw | 45,000 | 45,501 | 88 | 0.648 ± 0.004 (d -0.038 ± 0.005) | 0.712 ± 0.009 (d 0.026 ± 0.010) |
| sw | 20,000 | 20,643 | 88 | 0.621 ± 0.006 (d -0.065 ± 0.006) | 0.729 ± 0.008 (d 0.043 ± 0.009) |
| te | full | 518,079 | 100 | 0.866 ± 0.001 | — |
| te | 131,924 | 132,525 | 100 | 0.833 ± 0.004 (d -0.033 ± 0.003) | 0.859 ± 0.002 (d -0.008 ± 0.001) |
| te | 45,000 | 45,728 | 100 | 0.818 ± 0.002 (d -0.049 ± 0.003) | 0.857 ± 0.003 (d -0.010 ± 0.003) |
| te | 20,000 | 20,766 | 100 | 0.806 ± 0.007 (d -0.060 ± 0.008) | 0.857 ± 0.006 (d -0.009 ± 0.006) |
| yo | full | 49,043 | 80 | 0.859 ± 0.001 | — |
| yo | 45,000 | 45,012 | 80 | 0.857 ± 0.002 (d -0.001 ± 0.003) | 0.860 ± 0.001 (d 0.002 ± 0.002) |
| yo | 20,000 | 20,083 | 80 | 0.850 ± 0.005 (d -0.009 ± 0.006) | 0.871 ± 0.006 (d 0.012 ± 0.006) |
| id | full | 1,446,315 | 62 | 0.703 ± 0.003 | — |
| id | 131,924 | 134,502 | 62 | 0.588 ± 0.006 (d -0.115 ± 0.007) | 0.684 ± 0.005 (d -0.019 ± 0.005) |
| id | 45,000 | 47,751 | 62 | 0.540 ± 0.005 (d -0.163 ± 0.006) | 0.692 ± 0.012 (d -0.011 ± 0.012) |
| id | 20,000 | 22,805 | 62 | 0.512 ± 0.004 (d -0.191 ± 0.006) | 0.710 ± 0.006 (d 0.007 ± 0.006) |

## 2. Effect of forcing gold to be kept (AUROC difference keep - nokeep on the same seed)

Positive = easier to detect after adding gold back; negative = adding gold back makes poisons look less isolated, harder to detect.

| lang | size | gold passages added | share of corpus | rel_knn10 | knn10 |
|---|---|---|---|---|---|
| sw | 45,000 | 502 | 1.1% | -0.077 ± 0.011 | -0.064 ± 0.005 |
| sw | 20,000 | 643 | 3.1% | -0.128 ± 0.009 | -0.108 ± 0.004 |
| te | 131,924 | 601 | 0.5% | -0.042 ± 0.004 | -0.025 ± 0.002 |
| te | 45,000 | 729 | 1.6% | -0.068 ± 0.008 | -0.039 ± 0.003 |
| te | 20,000 | 767 | 3.7% | -0.086 ± 0.011 | -0.051 ± 0.003 |
| yo | 45,000 | 12 | 0.0% | -0.005 ± 0.003 | -0.003 ± 0.002 |
| yo | 20,000 | 84 | 0.4% | -0.042 ± 0.008 | -0.022 ± 0.001 |
| id | 131,924 | 2,578 | 1.9% | -0.073 ± 0.011 | -0.096 ± 0.004 |
| id | 45,000 | 2,751 | 5.8% | -0.092 ± 0.011 | -0.152 ± 0.009 |
| id | 20,000 | 2,806 | 12.3% | -0.090 ± 0.011 | -0.198 ± 0.006 |

## 3. Across languages: Spearman rho between AUROC drop and shrink factor (full / actual passages), per seed

With only 4 language points the smallest exact permutation p is 0.083; what matters is whether seeds agree in direction.

- rel_knn10 / 131,924 / keep: seed0 rho=-1.00, seed1 rho=-1.00, seed2 rho=-1.00, seed3 rho=-1.00, seed4 rho=-1.00 (min p 0.083)
- rel_knn10 / 131,924 / nokeep: seed0 rho=-1.00, seed1 rho=-1.00, seed2 rho=-1.00, seed3 rho=-1.00, seed4 rho=-1.00 (min p 0.083)
- rel_knn10 / 45,000 / keep: seed0 rho=-1.00, seed1 rho=-1.00, seed2 rho=-1.00, seed3 rho=-1.00, seed4 rho=-1.00 (min p 0.083)
- rel_knn10 / 45,000 / nokeep: seed0 rho=-1.00, seed1 rho=-1.00, seed2 rho=-1.00, seed3 rho=-1.00, seed4 rho=-1.00 (min p 0.083)
- rel_knn10 / 20,000 / keep: seed0 rho=-1.00, seed1 rho=-0.80, seed2 rho=-0.80, seed3 rho=-0.80, seed4 rho=-0.80 (min p 0.083)
- rel_knn10 / 20,000 / nokeep: seed0 rho=-1.00, seed1 rho=-1.00, seed2 rho=-1.00, seed3 rho=-0.80, seed4 rho=-1.00 (min p 0.083)
- knn10 / 131,924 / keep: seed0 rho=-1.00, seed1 rho=-1.00, seed2 rho=-1.00, seed3 rho=-1.00, seed4 rho=-1.00 (min p 0.083)
- knn10 / 131,924 / nokeep: seed0 rho=-1.00, seed1 rho=-1.00, seed2 rho=-1.00, seed3 rho=-1.00, seed4 rho=-1.00 (min p 0.083)
- knn10 / 45,000 / keep: seed0 rho=-1.00, seed1 rho=-1.00, seed2 rho=-1.00, seed3 rho=-1.00, seed4 rho=-1.00 (min p 0.083)
- knn10 / 45,000 / nokeep: seed0 rho=-0.60, seed1 rho=-0.80, seed2 rho=-0.80, seed3 rho=-0.60, seed4 rho=+0.00 (min p 0.333)
- knn10 / 20,000 / keep: seed0 rho=-1.00, seed1 rho=-1.00, seed2 rho=-0.80, seed3 rho=-0.80, seed4 rho=-0.80 (min p 0.083)
- knn10 / 20,000 / nokeep: seed0 rho=+0.00, seed1 rho=-0.60, seed2 rho=+0.00, seed3 rho=-0.60, seed4 rho=-0.60 (min p 0.417)

## 4. Deployment metrics (rel_knn10, 5% FPR): TPR@5% and surviving-poison rate after filtering (hit@5 and not flagged)

| lang | size | mode | TPR@5% | hit@5 | surviving rate |
|---|---|---|---|---|---|
| sw | full | full | 0.23 ± 0.01 | 0.97 ± 0.00 | 0.73 ± 0.01 |
| sw | 45,000 | keep | 0.14 ± 0.01 | 0.98 ± 0.01 | 0.84 ± 0.01 |
| sw | 45,000 | nokeep | 0.21 ± 0.03 | 1.00 ± 0.01 | 0.78 ± 0.03 |
| sw | 20,000 | keep | 0.09 ± 0.02 | 0.99 ± 0.01 | 0.90 ± 0.03 |
| sw | 20,000 | nokeep | 0.17 ± 0.03 | 1.00 ± 0.00 | 0.83 ± 0.03 |
| te | full | full | 0.57 ± 0.01 | 0.98 ± 0.00 | 0.43 ± 0.01 |
| te | 131,924 | keep | 0.46 ± 0.02 | 1.00 ± 0.00 | 0.54 ± 0.02 |
| te | 131,924 | nokeep | 0.54 ± 0.03 | 1.00 ± 0.00 | 0.46 ± 0.03 |
| te | 45,000 | keep | 0.41 ± 0.03 | 1.00 ± 0.00 | 0.59 ± 0.03 |
| te | 45,000 | nokeep | 0.50 ± 0.02 | 1.00 ± 0.00 | 0.50 ± 0.02 |
| te | 20,000 | keep | 0.33 ± 0.04 | 1.00 ± 0.00 | 0.67 ± 0.04 |
| te | 20,000 | nokeep | 0.44 ± 0.03 | 1.00 ± 0.00 | 0.56 ± 0.03 |
| yo | full | full | 0.41 ± 0.02 | 0.99 ± 0.00 | 0.59 ± 0.02 |
| yo | 45,000 | keep | 0.40 ± 0.02 | 0.99 ± 0.00 | 0.60 ± 0.02 |
| yo | 45,000 | nokeep | 0.41 ± 0.03 | 0.99 ± 0.00 | 0.59 ± 0.03 |
| yo | 20,000 | keep | 0.34 ± 0.03 | 0.99 ± 0.01 | 0.66 ± 0.03 |
| yo | 20,000 | nokeep | 0.38 ± 0.03 | 0.99 ± 0.01 | 0.62 ± 0.03 |
| id | full | full | 0.28 ± 0.01 | 0.95 ± 0.00 | 0.71 ± 0.01 |
| id | 131,924 | keep | 0.09 ± 0.01 | 1.00 ± 0.01 | 0.91 ± 0.01 |
| id | 131,924 | nokeep | 0.14 ± 0.05 | 1.00 ± 0.00 | 0.86 ± 0.05 |
| id | 45,000 | keep | 0.06 ± 0.01 | 1.00 ± 0.00 | 0.94 ± 0.01 |
| id | 45,000 | nokeep | 0.10 ± 0.06 | 1.00 ± 0.00 | 0.90 ± 0.06 |
| id | 20,000 | keep | 0.05 ± 0.03 | 1.00 ± 0.00 | 0.95 ± 0.03 |
| id | 20,000 | nokeep | 0.08 ± 0.03 | 1.00 ± 0.00 | 0.92 ± 0.03 |

## 4. Deployment metrics (knn10, 5% FPR): TPR@5% and surviving-poison rate after filtering (hit@5 and not flagged)

| lang | size | mode | TPR@5% | hit@5 | surviving rate |
|---|---|---|---|---|---|
| sw | full | full | 0.20 ± 0.01 | 0.97 ± 0.00 | 0.76 ± 0.01 |
| sw | 45,000 | keep | 0.18 ± 0.02 | 0.98 ± 0.01 | 0.80 ± 0.01 |
| sw | 45,000 | nokeep | 0.24 ± 0.04 | 1.00 ± 0.01 | 0.76 ± 0.04 |
| sw | 20,000 | keep | 0.11 ± 0.02 | 0.99 ± 0.01 | 0.88 ± 0.02 |
| sw | 20,000 | nokeep | 0.23 ± 0.03 | 1.00 ± 0.00 | 0.77 ± 0.03 |
| te | full | full | 0.32 ± 0.00 | 0.98 ± 0.00 | 0.66 ± 0.00 |
| te | 131,924 | keep | 0.21 ± 0.01 | 1.00 ± 0.00 | 0.79 ± 0.01 |
| te | 131,924 | nokeep | 0.26 ± 0.02 | 1.00 ± 0.00 | 0.74 ± 0.02 |
| te | 45,000 | keep | 0.15 ± 0.02 | 1.00 ± 0.00 | 0.85 ± 0.02 |
| te | 45,000 | nokeep | 0.26 ± 0.02 | 1.00 ± 0.00 | 0.74 ± 0.02 |
| te | 20,000 | keep | 0.13 ± 0.02 | 1.00 ± 0.00 | 0.87 ± 0.02 |
| te | 20,000 | nokeep | 0.25 ± 0.03 | 1.00 ± 0.00 | 0.75 ± 0.03 |
| yo | full | full | 0.40 ± 0.02 | 0.99 ± 0.00 | 0.58 ± 0.02 |
| yo | 45,000 | keep | 0.39 ± 0.02 | 0.99 ± 0.00 | 0.59 ± 0.02 |
| yo | 45,000 | nokeep | 0.40 ± 0.02 | 0.99 ± 0.00 | 0.58 ± 0.02 |
| yo | 20,000 | keep | 0.35 ± 0.02 | 0.99 ± 0.01 | 0.64 ± 0.03 |
| yo | 20,000 | nokeep | 0.44 ± 0.02 | 0.99 ± 0.01 | 0.55 ± 0.02 |
| id | full | full | 0.11 ± 0.00 | 0.95 ± 0.00 | 0.85 ± 0.00 |
| id | 131,924 | keep | 0.07 ± 0.01 | 1.00 ± 0.01 | 0.93 ± 0.02 |
| id | 131,924 | nokeep | 0.12 ± 0.01 | 1.00 ± 0.00 | 0.88 ± 0.01 |
| id | 45,000 | keep | 0.05 ± 0.01 | 1.00 ± 0.00 | 0.95 ± 0.01 |
| id | 45,000 | nokeep | 0.11 ± 0.03 | 1.00 ± 0.00 | 0.89 ± 0.03 |
| id | 20,000 | keep | 0.05 ± 0.01 | 1.00 ± 0.00 | 0.95 ± 0.01 |
| id | 20,000 | nokeep | 0.15 ± 0.02 | 1.00 ± 0.00 | 0.85 ± 0.02 |

The surviving rate here uses all kept questions of the variant (not the questions shared by the three variants as in ml_analyze table C), so there are more questions and the numbers need not match table C.
