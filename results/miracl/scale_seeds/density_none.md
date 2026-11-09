# Detection difficulty: corpus size vs local density (trans/bb, judgments none, seeds [0, 1, 2, 3, 4])

Modes: keep = random subset + all dev gold passages; article = random subset + all passages of the gold articles; nokeep = random subset only. All three use the same random subset for a given seed.

## 1. AUROC (rel_knn10, vs length-matched): mean +/- s.d. across seeds; in brackets the paired drop relative to the full corpus

| lang | size | keep | article | nokeep |
|---|---|---|---|---|
| sw | full | 0.763 ± 0.004 | | |
| sw | 45,000 | 0.667 ± 0.014 (delta -0.096 ± 0.017; 45,502 passages) | 0.698 ± 0.009 (delta -0.066 ± 0.011; 51,155 passages) | 0.745 ± 0.005 (delta -0.018 ± 0.008; 45,000 passages) |
| sw | 20,000 | 0.608 ± 0.013 (delta -0.155 ± 0.015; 20,643 passages) | 0.658 ± 0.010 (delta -0.105 ± 0.012; 27,924 passages) | 0.736 ± 0.020 (delta -0.027 ± 0.023; 20,000 passages) |
| te | full | 0.898 ± 0.002 | | |
| te | 131,924 | 0.825 ± 0.005 (delta -0.073 ± 0.006; 132,525 passages) | 0.837 ± 0.003 (delta -0.061 ± 0.004; 141,375 passages) | 0.867 ± 0.006 (delta -0.030 ± 0.008; 131,924 passages) |
| te | 45,000 | 0.782 ± 0.007 (delta -0.115 ± 0.008; 45,729 passages) | 0.817 ± 0.005 (delta -0.080 ± 0.007; 56,604 passages) | 0.851 ± 0.011 (delta -0.047 ± 0.012; 45,000 passages) |
| te | 20,000 | 0.760 ± 0.008 (delta -0.138 ± 0.008; 20,767 passages) | 0.811 ± 0.003 (delta -0.086 ± 0.004; 32,209 passages) | 0.846 ± 0.016 (delta -0.052 ± 0.015; 20,000 passages) |
| yo | full | 0.802 ± 0.000 | | |
| yo | 45,000 | 0.803 ± 0.005 (delta 0.000 ± 0.005; 45,012 passages) | 0.801 ± 0.006 (delta -0.002 ± 0.005; 45,051 passages) | 0.807 ± 0.006 (delta 0.005 ± 0.006; 45,000 passages) |
| yo | 20,000 | 0.786 ± 0.012 (delta -0.016 ± 0.012; 20,084 passages) | 0.762 ± 0.012 (delta -0.040 ± 0.012; 20,384 passages) | 0.828 ± 0.008 (delta 0.026 ± 0.008; 20,000 passages) |
| id | full | 0.787 ± 0.004 | | |
| id | 131,924 | 0.578 ± 0.009 (delta -0.208 ± 0.008; 134,502 passages) | 0.651 ± 0.010 (delta -0.136 ± 0.009; 166,766 passages) | 0.651 ± 0.009 (delta -0.135 ± 0.007; 131,924 passages) |
| id | 45,000 | 0.546 ± 0.015 (delta -0.241 ± 0.013; 47,751 passages) | 0.608 ± 0.012 (delta -0.178 ± 0.010; 82,140 passages) | 0.638 ± 0.020 (delta -0.149 ± 0.017; 45,000 passages) |
| id | 20,000 | 0.546 ± 0.022 (delta -0.241 ± 0.023; 22,806 passages) | 0.604 ± 0.003 (delta -0.183 ± 0.003; 57,814 passages) | 0.637 ± 0.014 (delta -0.150 ± 0.016; 20,000 passages) |

## 1. AUROC (knn10, vs length-matched): mean +/- s.d. across seeds; in brackets the paired drop relative to the full corpus

| lang | size | keep | article | nokeep |
|---|---|---|---|---|
| sw | full | 0.686 ± 0.002 | | |
| sw | 45,000 | 0.648 ± 0.004 (delta -0.038 ± 0.005; 45,502 passages) | 0.608 ± 0.003 (delta -0.078 ± 0.004; 51,155 passages) | 0.712 ± 0.009 (delta 0.026 ± 0.010; 45,000 passages) |
| sw | 20,000 | 0.621 ± 0.006 (delta -0.065 ± 0.006; 20,643 passages) | 0.579 ± 0.002 (delta -0.107 ± 0.003; 27,924 passages) | 0.729 ± 0.008 (delta 0.043 ± 0.009; 20,000 passages) |
| te | full | 0.866 ± 0.001 | | |
| te | 131,924 | 0.833 ± 0.004 (delta -0.033 ± 0.003; 132,525 passages) | 0.808 ± 0.003 (delta -0.058 ± 0.002; 141,375 passages) | 0.859 ± 0.002 (delta -0.008 ± 0.001; 131,924 passages) |
| te | 45,000 | 0.818 ± 0.002 (delta -0.049 ± 0.003; 45,729 passages) | 0.778 ± 0.002 (delta -0.088 ± 0.003; 56,604 passages) | 0.857 ± 0.003 (delta -0.010 ± 0.003; 45,000 passages) |
| te | 20,000 | 0.806 ± 0.007 (delta -0.060 ± 0.008; 20,767 passages) | 0.769 ± 0.005 (delta -0.097 ± 0.005; 32,209 passages) | 0.857 ± 0.006 (delta -0.009 ± 0.006; 20,000 passages) |
| yo | full | 0.859 ± 0.001 | | |
| yo | 45,000 | 0.857 ± 0.002 (delta -0.001 ± 0.003; 45,012 passages) | 0.856 ± 0.002 (delta -0.002 ± 0.003; 45,051 passages) | 0.860 ± 0.001 (delta 0.002 ± 0.002; 45,000 passages) |
| yo | 20,000 | 0.850 ± 0.005 (delta -0.009 ± 0.006; 20,084 passages) | 0.836 ± 0.006 (delta -0.023 ± 0.006; 20,384 passages) | 0.871 ± 0.006 (delta 0.012 ± 0.006; 20,000 passages) |
| id | full | 0.703 ± 0.003 | | |
| id | 131,924 | 0.588 ± 0.006 (delta -0.115 ± 0.007; 134,502 passages) | 0.517 ± 0.004 (delta -0.186 ± 0.004; 166,766 passages) | 0.684 ± 0.005 (delta -0.019 ± 0.005; 131,924 passages) |
| id | 45,000 | 0.540 ± 0.005 (delta -0.163 ± 0.006; 47,751 passages) | 0.487 ± 0.001 (delta -0.216 ± 0.004; 82,140 passages) | 0.692 ± 0.012 (delta -0.011 ± 0.012; 45,000 passages) |
| id | 20,000 | 0.512 ± 0.004 (delta -0.191 ± 0.006; 22,806 passages) | 0.518 ± 0.003 (delta -0.185 ± 0.006; 57,814 passages) | 0.710 ± 0.006 (delta 0.007 ± 0.006; 20,000 passages) |

## 2. Local density: number of the poison's top-10 neighbours from the question's gold article (in brackets: share whose nearest neighbour is from the gold article)

| lang | size | keep | article | nokeep |
|---|---|---|---|---|
| sw | full | 3.81 (74%) | | |
| sw | 45,000 | 3.13 (76%) | 4.44 (78%) | 2.27 (51%) |
| sw | 20,000 | 2.74 (82%) | 4.75 (80%) | 1.51 (39%) |
| te | full | 2.90 (85%) | | |
| te | 131,924 | 1.97 (91%) | 3.77 (92%) | 1.24 (41%) |
| te | 45,000 | 1.52 (94%) | 4.51 (95%) | 0.62 (23%) |
| te | 20,000 | 1.35 (95%) | 4.91 (96%) | 0.37 (14%) |
| yo | full | 2.26 (74%) | | |
| yo | 45,000 | 2.21 (74%) | 2.28 (74%) | 2.11 (71%) |
| yo | 20,000 | 1.76 (81%) | 2.46 (82%) | 1.06 (51%) |
| id | full | 3.69 (61%) | | |
| id | 131,924 | 2.99 (78%) | 5.33 (76%) | 1.27 (34%) |
| id | 45,000 | 3.04 (84%) | 5.76 (81%) | 0.63 (22%) |
| id | 20,000 | 3.02 (88%) | 5.89 (85%) | 0.35 (13%) |

## 3. Within-question regression: suspicion percentile ~ log10(corpus size) + local density (question fixed effects, cluster bootstrap 95% CI)

log10(size) coefficient = change in percentile for a tenfold larger corpus (positive = larger corpora are easier); local-density coefficient = change in percentile per additional gold-article passage among the top-10 neighbours (negative = denser is harder). 'alone' = only that variable in the model; 'joint' = both variables.

| feature | lang | obs | log10(size): alone | log10(size): joint | local density: alone | local density: joint |
|---|---|---|---|---|---|---|
| rel_knn10 | sw | 3,080 | +0.114 (+0.080, +0.148) | +0.140 (+0.105, +0.175) | -0.009 (-0.018, +0.000) | -0.016 (-0.026, -0.007) |
| rel_knn10 | te | 5,000 | +0.063 (+0.046, +0.079) | +0.068 (+0.055, +0.082) | -0.004 (-0.012, +0.002) | -0.007 (-0.014, -0.000) |
| rel_knn10 | yo | 2,800 | +0.029 (-0.014, +0.068) | +0.086 (+0.044, +0.128) | -0.037 (-0.050, -0.026) | -0.044 (-0.056, -0.032) |
| rel_knn10 | id | 3,100 | +0.101 (+0.077, +0.125) | +0.118 (+0.099, +0.137) | -0.008 (-0.016, -0.000) | -0.014 (-0.023, -0.006) |
| rel_knn10 | pooled | 13,980 | +0.082 (+0.069, +0.094) | +0.095 (+0.084, +0.108) | -0.008 (-0.012, -0.004) | -0.012 (-0.017, -0.008) |
| knn10 | sw | 3,080 | +0.027 (+0.009, +0.043) | +0.081 (+0.060, +0.102) | -0.029 (-0.034, -0.024) | -0.033 (-0.038, -0.028) |
| knn10 | te | 5,000 | +0.030 (+0.022, +0.037) | +0.046 (+0.038, +0.053) | -0.016 (-0.019, -0.013) | -0.018 (-0.020, -0.015) |
| knn10 | yo | 2,800 | +0.017 (+0.003, +0.030) | +0.041 (+0.028, +0.055) | -0.016 (-0.019, -0.012) | -0.019 (-0.023, -0.015) |
| knn10 | id | 3,100 | +0.040 (+0.024, +0.054) | +0.083 (+0.071, +0.096) | -0.033 (-0.037, -0.029) | -0.037 (-0.041, -0.033) |
| knn10 | pooled | 13,980 | +0.033 (+0.026, +0.040) | +0.063 (+0.055, +0.071) | -0.025 (-0.027, -0.023) | -0.028 (-0.031, -0.025) |

For 'pooled', fixed effects are by language x question, so differences between languages are absorbed; only changes of the same poison across corpora are compared.

## 4. Stratified by local density: does corpus size still matter? (mean rel_knn10 percentile, four languages pooled)

| local density (gold-article passages in top-10) | full | 131,924 | 45,000 | 20,000 |
|---|---|---|---|---|
| 0 | 0.949 (85) | 0.832 (351) | 0.828 (716) | 0.813 (935) |
| 1-2 | 0.875 (755) | 0.803 (1149) | 0.784 (2260) | 0.759 (2305) |
| 3 or more | 0.751 (810) | 0.680 (930) | 0.663 (1974) | 0.634 (1710) |

Numbers in brackets are observations (poison x mode x seed). A flat row means corpus size no longer matters at equal density.
