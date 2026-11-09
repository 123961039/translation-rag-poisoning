# Results under three question-judgment sets (native, old review, no exclusion)

Main comparison trans/bb. All analyses use --exclude bad; 'no exclusion' = empty judgment file.

## 0. Questions kept by each judgment set (detection table B, trans/bb)

| judgments | sw | te | yo | id |
|---|---|---|---|---|
| native | 47 | 52 | 26 | 28 |
| old review | 54 | 78 | 66 | 30 |
| no exclusion | 88 | 100 | 80 | 62 |

## 1. Scale control: AUROC (vs length-matched), feature rel_knn10

| lang | judgments | full | 131,924 | 45,000 | d(45k-full) |
|---|---|---|---|---|---|
| sw | native | 0.738 | 0.738 | 0.642 | -0.096 |
| sw | old review | 0.727 | 0.727 | 0.624 | -0.103 |
| sw | no exclusion | 0.761 | 0.761 | 0.675 | -0.085 |
| te | native | 0.890 | 0.823 | 0.784 | -0.106 |
| te | old review | 0.908 | 0.844 | 0.798 | -0.110 |
| te | no exclusion | 0.899 | 0.821 | 0.778 | -0.121 |
| yo | native | 0.824 | 0.824 | 0.827 | 0.003 |
| yo | old review | 0.824 | 0.824 | 0.826 | 0.002 |
| yo | no exclusion | 0.802 | 0.802 | 0.801 | -0.001 |
| id | native | 0.820 | 0.605 | 0.622 | -0.199 |
| id | old review | 0.773 | 0.576 | 0.573 | -0.200 |
| id | no exclusion | 0.792 | 0.577 | 0.554 | -0.238 |

Spearman rho between endpoint dAUROC and shrink factor (full / 45k actual passages) (n=4, exact permutation two-sided p):

- native: rho = -1.000, p = 0.083
- old review: rho = -1.000, p = 0.083
- no exclusion: rho = -1.000, p = 0.083

## 1. Scale control: AUROC (vs length-matched), feature knn10

| lang | judgments | full | 131,924 | 45,000 | d(45k-full) |
|---|---|---|---|---|---|
| sw | native | 0.666 | 0.666 | 0.634 | -0.032 |
| sw | old review | 0.669 | 0.669 | 0.633 | -0.036 |
| sw | no exclusion | 0.685 | 0.685 | 0.652 | -0.033 |
| te | native | 0.868 | 0.842 | 0.829 | -0.039 |
| te | old review | 0.861 | 0.828 | 0.806 | -0.055 |
| te | no exclusion | 0.867 | 0.835 | 0.816 | -0.051 |
| yo | native | 0.860 | 0.860 | 0.853 | -0.007 |
| yo | old review | 0.860 | 0.860 | 0.855 | -0.005 |
| yo | no exclusion | 0.860 | 0.860 | 0.854 | -0.006 |
| id | native | 0.727 | 0.629 | 0.588 | -0.138 |
| id | old review | 0.723 | 0.602 | 0.558 | -0.165 |
| id | no exclusion | 0.704 | 0.583 | 0.541 | -0.163 |

Spearman rho between endpoint dAUROC and shrink factor (full / 45k actual passages) (n=4, exact permutation two-sided p):

- native: rho = -1.000, p = 0.083
- old review: rho = -1.000, p = 0.083
- no exclusion: rho = -1.000, p = 0.083

## 2. Surviving-poison rate after filtering at 5% FPR, feature rel_knn10

| lang | judgments | shared questions | full | 45,000 |
|---|---|---|---|---|
| sw | native | 28 | 0.75 (0.57–0.89) | 0.89 (0.79–1.00) |
| sw | old review | 34 | 0.79 (0.65–0.91) | 0.91 (0.82–1.00) |
| sw | no exclusion | 56 | 0.70 (0.57–0.80) | 0.80 (0.70–0.91) |
| te | native | 33 | 0.39 (0.24–0.55) | 0.48 (0.30–0.64) |
| te | old review | 39 | 0.33 (0.18–0.46) | 0.44 (0.28–0.59) |
| te | no exclusion | 51 | 0.37 (0.24–0.51) | 0.49 (0.35–0.63) |
| yo | native | 24 | 0.42 (0.21–0.62) | 0.46 (0.25–0.67) |
| yo | old review | 61 | 0.49 (0.36–0.62) | 0.49 (0.36–0.62) |
| yo | no exclusion | 70 | 0.54 (0.43–0.67) | 0.54 (0.43–0.66) |
| id | native | 17 | 0.71 (0.47–0.94) | 0.88 (0.71–1.00) |
| id | old review | 20 | 0.70 (0.50–0.90) | 0.90 (0.75–1.00) |
| id | no exclusion | 40 | 0.72 (0.57–0.85) | 0.95 (0.88–1.00) |

Ranking at 45k (higher = more dangerous):

- native: sw 0.89 > id 0.88 > te 0.48 > yo 0.46
- old review: sw 0.91 > id 0.90 > yo 0.49 > te 0.44
- no exclusion: id 0.95 > sw 0.80 > yo 0.54 > te 0.49

## 2. Surviving-poison rate after filtering at 5% FPR, feature knn10

| lang | judgments | shared questions | full | 45,000 |
|---|---|---|---|---|
| sw | native | 28 | 0.68 (0.50–0.86) | 0.79 (0.64–0.93) |
| sw | old review | 34 | 0.74 (0.59–0.88) | 0.82 (0.68–0.94) |
| sw | no exclusion | 56 | 0.70 (0.57–0.82) | 0.80 (0.70–0.91) |
| te | native | 33 | 0.70 (0.52–0.85) | 0.88 (0.76–0.97) |
| te | old review | 39 | 0.72 (0.56–0.87) | 0.87 (0.77–0.97) |
| te | no exclusion | 51 | 0.73 (0.59–0.84) | 0.88 (0.78–0.96) |
| yo | native | 24 | 0.54 (0.33–0.75) | 0.62 (0.42–0.79) |
| yo | old review | 61 | 0.52 (0.39–0.66) | 0.56 (0.43–0.67) |
| yo | no exclusion | 70 | 0.54 (0.43–0.66) | 0.57 (0.46–0.69) |
| id | native | 17 | 0.88 (0.71–1.00) | 0.94 (0.82–1.00) |
| id | old review | 20 | 0.85 (0.70–1.00) | 0.95 (0.85–1.00) |
| id | no exclusion | 40 | 0.88 (0.75–0.97) | 0.97 (0.93–1.00) |

Ranking at 45k (higher = more dangerous):

- native: id 0.94 > te 0.88 > sw 0.79 > yo 0.62
- old review: id 0.95 > te 0.87 > sw 0.82 > yo 0.56
- no exclusion: id 0.97 > te 0.88 > sw 0.80 > yo 0.57

## 3. Feature preference: rows where rel_knn10 AUROC exceeds knn10 (3 variants x 2 forms per language)

| size | judgments | sw | te | yo | id |
|---|---|---|---|---|---|
| full | native | 6/6 | 5/6 | 0/6 | 6/6 |
| full | old review | 6/6 | 6/6 | 0/6 | 6/6 |
| full | no exclusion | 6/6 | 6/6 | 0/6 | 6/6 |
| 45,000 | native | 5/6 | 2/6 | 0/6 | 6/6 |
| 45,000 | old review | 4/6 | 4/6 | 0/6 | 6/6 |
| 45,000 | no exclusion | 5/6 | 2/6 | 0/6 | 6/6 |

## 4. Generation-level ASR

### trans/bb

| lang | judgments | questions | clean accuracy | attacked ASR | defended ASR (realistic) | recovered |
|---|---|---|---|---|---|---|
| sw | native | 47 | 0.83 (0.72–0.94) | 0.28 (0.15–0.40) | 0.26 (0.13–0.38) | 8% |
| sw | old review | 54 | 0.80 (0.69–0.91) | 0.39 (0.26–0.52) | 0.33 (0.20–0.46) | 14% |
| sw | no exclusion | 88 | 0.60 (0.50–0.70) | 0.31 (0.22–0.41) | 0.26 (0.17–0.36) | 15% |
| te | native | 52 | 0.92 (0.85–0.98) | 0.15 (0.06–0.25) | 0.08 (0.02–0.15) | 50% |
| te | old review | 78 | 0.90 (0.82–0.96) | 0.21 (0.12–0.29) | 0.05 (0.01–0.10) | 75% |
| te | no exclusion | 100 | 0.85 (0.78–0.91) | 0.16 (0.09–0.24) | 0.04 (0.01–0.08) | 75% |
| yo | native | 26 | 0.69 (0.54–0.85) | 0.50 (0.31–0.69) | 0.19 (0.08–0.35) | 62% |
| yo | old review | 14 | 0.79 (0.57–1.00) | 0.71 (0.43–0.93) | 0.57 (0.29–0.79) | 20% |
| yo | no exclusion | 80 | 0.39 (0.29–0.50) | 0.42 (0.31–0.54) | 0.28 (0.19–0.38) | 35% |
| id | native | 28 | 0.64 (0.46–0.82) | 0.32 (0.14–0.50) | 0.21 (0.07–0.36) | 33% |
| id | old review | 30 | 0.60 (0.40–0.77) | 0.37 (0.20–0.53) | 0.30 (0.13–0.47) | 18% |
| id | no exclusion | 62 | 0.39 (0.27–0.50) | 0.37 (0.26–0.48) | 0.31 (0.21–0.42) | 17% |

### en/bb

| lang | judgments | questions | clean accuracy | attacked ASR | defended ASR (realistic) | recovered |
|---|---|---|---|---|---|---|
| sw | native | 47 | 0.83 (0.72–0.94) | 0.21 (0.11–0.34) | 0.17 (0.08–0.28) | 20% |
| sw | old review | 54 | 0.80 (0.69–0.91) | 0.30 (0.19–0.43) | 0.22 (0.11–0.33) | 25% |
| sw | no exclusion | 88 | 0.60 (0.50–0.70) | 0.23 (0.15–0.32) | 0.16 (0.09–0.24) | 30% |
| te | native | 52 | 0.92 (0.85–0.98) | 0.17 (0.08–0.27) | 0.08 (0.02–0.15) | 56% |
| te | old review | 78 | 0.90 (0.82–0.96) | 0.17 (0.09–0.24) | 0.04 (0.00–0.09) | 77% |
| te | no exclusion | 100 | 0.85 (0.78–0.91) | 0.15 (0.08–0.22) | 0.04 (0.01–0.08) | 73% |
| yo | native | 26 | 0.69 (0.54–0.85) | 0.88 (0.77–1.00) | 0.38 (0.19–0.58) | 57% |
| yo | old review | 14 | 0.79 (0.57–1.00) | 0.86 (0.64–1.00) | 0.57 (0.29–0.86) | 33% |
| yo | no exclusion | 80 | 0.39 (0.29–0.50) | 0.56 (0.45–0.68) | 0.26 (0.16–0.36) | 53% |
| id | native | 28 | 0.64 (0.46–0.82) | 0.11 (0.00–0.21) | 0.07 (0.00–0.18) | 33% |
| id | old review | 30 | 0.60 (0.40–0.77) | 0.20 (0.07–0.33) | 0.17 (0.03–0.30) | 17% |
| id | no exclusion | 62 | 0.39 (0.27–0.50) | 0.24 (0.15–0.35) | 0.19 (0.10–0.29) | 20% |

### native/bb

| lang | judgments | questions | clean accuracy | attacked ASR | defended ASR (realistic) | recovered |
|---|---|---|---|---|---|---|
| sw | native | 28 | 0.83 (0.72–0.94) | 0.25 (0.11–0.43) | 0.07 (0.00–0.18) | 71% |
| sw | old review | 34 | 0.80 (0.69–0.91) | 0.29 (0.15–0.44) | 0.12 (0.03–0.24) | 60% |
| sw | no exclusion | 56 | 0.60 (0.50–0.70) | 0.30 (0.18–0.43) | 0.12 (0.04–0.21) | 59% |
| te | native | 33 | 0.92 (0.85–0.98) | 0.27 (0.12–0.42) | 0.09 (0.00–0.21) | 67% |
| te | old review | 39 | 0.90 (0.82–0.96) | 0.26 (0.13–0.41) | 0.08 (0.00–0.15) | 70% |
| te | no exclusion | 51 | 0.85 (0.78–0.91) | 0.25 (0.14–0.37) | 0.10 (0.02–0.18) | 62% |
| yo | native | 24 | 0.69 (0.54–0.85) | 0.75 (0.54–0.92) | 0.12 (0.00–0.25) | 83% |
| yo | old review | 11 | 0.79 (0.57–1.00) | 0.82 (0.55–1.00) | 0.27 (0.09–0.55) | 67% |
| yo | no exclusion | 70 | 0.39 (0.29–0.50) | 0.67 (0.56–0.79) | 0.19 (0.10–0.29) | 72% |
| id | native | 17 | 0.64 (0.46–0.82) | 0.35 (0.12–0.59) | 0.24 (0.06–0.41) | 33% |
| id | old review | 20 | 0.60 (0.40–0.77) | 0.55 (0.35–0.75) | 0.35 (0.15–0.55) | 36% |
| id | no exclusion | 40 | 0.39 (0.27–0.50) | 0.47 (0.33–0.62) | 0.30 (0.17–0.45) | 37% |

### Cost of false alarms (gold wrongly removed)

| lang | native | old review | no exclusion |
|---|---|---|---|
| sw | 1/66 | 1/75 | 3/119 |
| te | 3/52 | 8/75 | 10/96 |
| yo | 2/34 | 0/18 | 8/90 |
| id | 0/39 | 0/43 | 0/83 |

## 5. Self-check

old review set rerun vs original files (_backup_cpu_20261028_205307): 144 AUROC rows compared, max difference 9.16e-02 -> WARNING: inconsistent, investigate before using the new results (explained in ../selfcheck_explain.md: the difference is confined to yo, whose added questions were never judged in the old review)

Other outputs (metric_gap, rel_diag, prefix, querylog) are in each set's directory with the original file names; scale_control is split by feature into scale_control_rel_knn10.* / scale_control_knn10.*.
