# Detection difficulty: corpus size vs local density (trans/bb, judgments native, seeds [0, 1, 2, 3, 4])

Modes: keep = random subset + all dev gold passages; article = random subset + all passages of the gold articles; nokeep = random subset only. All three use the same random subset for a given seed.

## 1. AUROC (rel_knn10, vs length-matched): mean +/- s.d. across seeds; in brackets the paired drop relative to the full corpus

| lang | size | keep | article | nokeep |
|---|---|---|---|---|
| sw | full | 0.741 ± 0.004 | | |
| sw | 45,000 | 0.632 ± 0.016 (delta -0.108 ± 0.019; 45,502 passages) | 0.676 ± 0.010 (delta -0.065 ± 0.013; 51,155 passages) | 0.714 ± 0.013 (delta -0.027 ± 0.017; 45,000 passages) |
| sw | 20,000 | 0.581 ± 0.011 (delta -0.159 ± 0.014; 20,643 passages) | 0.641 ± 0.008 (delta -0.099 ± 0.010; 27,924 passages) | 0.703 ± 0.028 (delta -0.037 ± 0.031; 20,000 passages) |
| te | full | 0.888 ± 0.002 | | |
| te | 131,924 | 0.828 ± 0.011 (delta -0.060 ± 0.012; 132,525 passages) | 0.841 ± 0.006 (delta -0.047 ± 0.007; 141,375 passages) | 0.869 ± 0.013 (delta -0.019 ± 0.014; 131,924 passages) |
| te | 45,000 | 0.778 ± 0.015 (delta -0.110 ± 0.015; 45,729 passages) | 0.814 ± 0.008 (delta -0.075 ± 0.009; 56,604 passages) | 0.852 ± 0.024 (delta -0.036 ± 0.024; 45,000 passages) |
| te | 20,000 | 0.751 ± 0.012 (delta -0.137 ± 0.011; 20,767 passages) | 0.807 ± 0.007 (delta -0.081 ± 0.007; 32,209 passages) | 0.842 ± 0.020 (delta -0.046 ± 0.019; 20,000 passages) |
| yo | full | 0.824 ± 0.000 | | |
| yo | 45,000 | 0.833 ± 0.008 (delta 0.009 ± 0.008; 45,012 passages) | 0.833 ± 0.009 (delta 0.008 ± 0.009; 45,051 passages) | 0.841 ± 0.012 (delta 0.017 ± 0.012; 45,000 passages) |
| yo | 20,000 | 0.839 ± 0.020 (delta 0.015 ± 0.020; 20,084 passages) | 0.817 ± 0.017 (delta -0.007 ± 0.018; 20,384 passages) | 0.886 ± 0.017 (delta 0.062 ± 0.017; 20,000 passages) |
| id | full | 0.815 ± 0.004 | | |
| id | 131,924 | 0.602 ± 0.017 (delta -0.213 ± 0.014; 134,502 passages) | 0.665 ± 0.008 (delta -0.150 ± 0.004; 166,766 passages) | 0.682 ± 0.024 (delta -0.133 ± 0.022; 131,924 passages) |
| id | 45,000 | 0.575 ± 0.044 (delta -0.240 ± 0.041; 47,751 passages) | 0.615 ± 0.019 (delta -0.200 ± 0.016; 82,140 passages) | 0.705 ± 0.049 (delta -0.110 ± 0.046; 45,000 passages) |
| id | 20,000 | 0.581 ± 0.013 (delta -0.234 ± 0.014; 22,806 passages) | 0.614 ± 0.006 (delta -0.201 ± 0.007; 57,814 passages) | 0.705 ± 0.021 (delta -0.110 ± 0.022; 20,000 passages) |

## 1. AUROC (knn10, vs length-matched): mean +/- s.d. across seeds; in brackets the paired drop relative to the full corpus

| lang | size | keep | article | nokeep |
|---|---|---|---|---|
| sw | full | 0.667 ± 0.002 | | |
| sw | 45,000 | 0.632 ± 0.005 (delta -0.035 ± 0.006; 45,502 passages) | 0.591 ± 0.004 (delta -0.076 ± 0.006; 51,155 passages) | 0.704 ± 0.011 (delta 0.037 ± 0.012; 45,000 passages) |
| sw | 20,000 | 0.607 ± 0.010 (delta -0.060 ± 0.010; 20,643 passages) | 0.561 ± 0.002 (delta -0.106 ± 0.003; 27,924 passages) | 0.726 ± 0.014 (delta 0.059 ± 0.016; 20,000 passages) |
| te | full | 0.867 ± 0.001 | | |
| te | 131,924 | 0.840 ± 0.004 (delta -0.027 ± 0.004; 132,525 passages) | 0.811 ± 0.003 (delta -0.056 ± 0.003; 141,375 passages) | 0.864 ± 0.004 (delta -0.002 ± 0.005; 131,924 passages) |
| te | 45,000 | 0.827 ± 0.004 (delta -0.040 ± 0.005; 45,729 passages) | 0.779 ± 0.002 (delta -0.088 ± 0.003; 56,604 passages) | 0.866 ± 0.007 (delta -0.001 ± 0.007; 45,000 passages) |
| te | 20,000 | 0.818 ± 0.008 (delta -0.049 ± 0.008; 20,767 passages) | 0.768 ± 0.005 (delta -0.099 ± 0.005; 32,209 passages) | 0.868 ± 0.009 (delta 0.001 ± 0.009; 20,000 passages) |
| yo | full | 0.859 ± 0.001 | | |
| yo | 45,000 | 0.857 ± 0.003 (delta -0.001 ± 0.004; 45,012 passages) | 0.857 ± 0.003 (delta -0.002 ± 0.004; 45,051 passages) | 0.862 ± 0.004 (delta 0.003 ± 0.004; 45,000 passages) |
| yo | 20,000 | 0.848 ± 0.011 (delta -0.011 ± 0.011; 20,084 passages) | 0.837 ± 0.011 (delta -0.022 ± 0.011; 20,384 passages) | 0.875 ± 0.012 (delta 0.016 ± 0.013; 20,000 passages) |
| id | full | 0.725 ± 0.002 | | |
| id | 131,924 | 0.631 ± 0.005 (delta -0.094 ± 0.005; 134,502 passages) | 0.539 ± 0.003 (delta -0.186 ± 0.003; 166,766 passages) | 0.732 ± 0.006 (delta 0.007 ± 0.006; 131,924 passages) |
| id | 45,000 | 0.584 ± 0.010 (delta -0.141 ± 0.011; 47,751 passages) | 0.507 ± 0.004 (delta -0.219 ± 0.006; 82,140 passages) | 0.749 ± 0.017 (delta 0.023 ± 0.018; 45,000 passages) |
| id | 20,000 | 0.557 ± 0.004 (delta -0.168 ± 0.007; 22,806 passages) | 0.539 ± 0.004 (delta -0.186 ± 0.007; 57,814 passages) | 0.761 ± 0.009 (delta 0.036 ± 0.008; 20,000 passages) |

## 2. Local density: number of the poison's top-10 neighbours from the question's gold article (in brackets: share whose nearest neighbour is from the gold article)

| lang | size | keep | article | nokeep |
|---|---|---|---|---|
| sw | full | 3.98 (70%) | | |
| sw | 45,000 | 3.08 (77%) | 4.45 (76%) | 2.21 (52%) |
| sw | 20,000 | 2.72 (85%) | 4.69 (79%) | 1.51 (40%) |
| te | full | 3.23 (87%) | | |
| te | 131,924 | 2.16 (93%) | 4.25 (94%) | 1.45 (46%) |
| te | 45,000 | 1.64 (97%) | 5.06 (98%) | 0.73 (27%) |
| te | 20,000 | 1.42 (98%) | 5.45 (98%) | 0.43 (16%) |
| yo | full | 2.50 (73%) | | |
| yo | 45,000 | 2.43 (75%) | 2.52 (75%) | 2.30 (72%) |
| yo | 20,000 | 1.88 (86%) | 2.62 (86%) | 1.04 (54%) |
| id | full | 4.11 (86%) | | |
| id | 131,924 | 2.99 (91%) | 6.11 (92%) | 1.26 (37%) |
| id | 45,000 | 2.88 (94%) | 6.54 (94%) | 0.54 (21%) |
| id | 20,000 | 2.87 (96%) | 6.61 (96%) | 0.36 (14%) |

## 3. Within-question regression: suspicion percentile ~ log10(corpus size) + local density (question fixed effects, cluster bootstrap 95% CI)

log10(size) coefficient = change in percentile for a tenfold larger corpus (positive = larger corpora are easier); local-density coefficient = change in percentile per additional gold-article passage among the top-10 neighbours (negative = denser is harder). 'alone' = only that variable in the model; 'joint' = both variables.

| feature | lang | obs | log10(size): alone | log10(size): joint | local density: alone | local density: joint |
|---|---|---|---|---|---|---|
| rel_knn10 | sw | 1,645 | +0.119 (+0.072, +0.174) | +0.146 (+0.105, +0.187) | -0.007 (-0.021, +0.006) | -0.015 (-0.028, -0.002) |
| rel_knn10 | te | 2,600 | +0.064 (+0.034, +0.089) | +0.073 (+0.051, +0.095) | -0.005 (-0.018, +0.005) | -0.008 (-0.020, +0.001) |
| rel_knn10 | yo | 910 | -0.043 (-0.119, +0.022) | +0.026 (-0.038, +0.089) | -0.039 (-0.059, -0.019) | -0.041 (-0.060, -0.022) |
| rel_knn10 | id | 1,400 | +0.085 (+0.059, +0.112) | +0.107 (+0.082, +0.135) | -0.009 (-0.016, -0.002) | -0.015 (-0.022, -0.007) |
| rel_knn10 | pooled | 6,555 | +0.075 (+0.056, +0.092) | +0.091 (+0.075, +0.106) | -0.008 (-0.015, -0.002) | -0.012 (-0.018, -0.006) |
| knn10 | sw | 1,645 | +0.015 (-0.010, +0.041) | +0.079 (+0.046, +0.110) | -0.030 (-0.036, -0.024) | -0.034 (-0.042, -0.028) |
| knn10 | te | 2,600 | +0.025 (+0.014, +0.037) | +0.043 (+0.033, +0.054) | -0.016 (-0.020, -0.013) | -0.018 (-0.022, -0.015) |
| knn10 | yo | 910 | +0.014 (-0.010, +0.036) | +0.047 (+0.019, +0.076) | -0.016 (-0.021, -0.009) | -0.020 (-0.026, -0.013) |
| knn10 | id | 1,400 | +0.026 (+0.008, +0.043) | +0.081 (+0.062, +0.102) | -0.034 (-0.038, -0.029) | -0.038 (-0.043, -0.033) |
| knn10 | pooled | 6,555 | +0.024 (+0.014, +0.032) | +0.060 (+0.049, +0.071) | -0.025 (-0.028, -0.022) | -0.028 (-0.031, -0.025) |

For 'pooled', fixed effects are by language x question, so differences between languages are absorbed; only changes of the same poison across corpora are compared.

## 4. Stratified by local density: does corpus size still matter? (mean rel_knn10 percentile, four languages pooled)

| local density (gold-article passages in top-10) | full | 131,924 | 45,000 | 20,000 |
|---|---|---|---|---|
| 0 | — | 0.869 (134) | 0.842 (318) | 0.834 (424) |
| 1-2 | 0.882 (325) | 0.810 (547) | 0.782 (994) | 0.768 (1016) |
| 3 or more | 0.764 (425) | 0.720 (519) | 0.667 (983) | 0.631 (855) |

Numbers in brackets are observations (poison x mode x seed). A flat row means corpus size no longer matters at equal density.
