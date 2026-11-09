# Query-log overlap detection (s >= 0.8; isolation rel_knn10; target total FPR 5%; exclusion bad)

## 1. The query-log signal itself

| lang | log | variant | form | n | mean poison s | poison flagged | flagged after deleting ? | FPR: random benign | FPR: gold |
|---|---|---|---|---|---|---|---|---|---|
| sw | full | native | bb | 28 | 1.00 | 1.00 (1.00–1.00) | 1.00 | 0.001 | 0.034 |
| sw | full | native | adv | 28 | 0.60 | 0.14 (0.04–0.29) | 0.14 | 0.001 | 0.034 |
| sw | full | trans | bb | 47 | 0.96 | 0.94 (0.87–1.00) | 0.94 | 0.001 | 0.034 |
| sw | full | trans | adv | 47 | 0.48 | 0.09 (0.02–0.17) | 0.09 | 0.001 | 0.034 |
| sw | full | en | bb | 47 | 1.00 | 1.00 (1.00–1.00) | 1.00 | 0.001 | 0.034 |
| sw | full | en | adv | 47 | 0.29 | 0.04 (0.00–0.11) | 0.04 | 0.001 | 0.034 |
| sw | excl_target | native | bb | 28 | 0.61 | 0.25 (0.11–0.39) | 0.25 | 0.001 | 0.020 |
| sw | excl_target | native | adv | 28 | 0.47 | 0.07 (0.00–0.18) | 0.07 | 0.001 | 0.020 |
| sw | excl_target | trans | bb | 47 | 0.56 | 0.21 (0.11–0.32) | 0.21 | 0.001 | 0.020 |
| sw | excl_target | trans | adv | 47 | 0.41 | 0.02 (0.00–0.06) | 0.02 | 0.001 | 0.020 |
| sw | excl_target | en | bb | 47 | 0.59 | 0.21 (0.11–0.34) | 0.21 | 0.001 | 0.020 |
| sw | excl_target | en | adv | 47 | 0.25 | 0.00 (0.00–0.00) | 0.00 | 0.001 | 0.020 |
| te | full | native | bb | 33 | 1.00 | 1.00 (1.00–1.00) | 1.00 | 0.000 | 0.000 |
| te | full | native | adv | 33 | 0.62 | 0.09 (0.00–0.21) | 0.09 | 0.000 | 0.000 |
| te | full | trans | bb | 52 | 0.94 | 0.90 (0.83–0.98) | 0.90 | 0.000 | 0.000 |
| te | full | trans | adv | 52 | 0.31 | 0.00 (0.00–0.00) | 0.00 | 0.000 | 0.000 |
| te | full | en | bb | 52 | 1.00 | 1.00 (1.00–1.00) | 1.00 | 0.000 | 0.000 |
| te | full | en | adv | 52 | 0.03 | 0.00 (0.00–0.00) | 0.00 | 0.000 | 0.000 |
| te | excl_target | native | bb | 33 | 0.40 | 0.06 (0.00–0.15) | 0.06 | 0.000 | 0.000 |
| te | excl_target | native | adv | 33 | 0.29 | 0.00 (0.00–0.00) | 0.00 | 0.000 | 0.000 |
| te | excl_target | trans | bb | 52 | 0.50 | 0.02 (0.00–0.06) | 0.02 | 0.000 | 0.000 |
| te | excl_target | trans | adv | 52 | 0.30 | 0.00 (0.00–0.00) | 0.00 | 0.000 | 0.000 |
| te | excl_target | en | bb | 52 | 0.42 | 0.06 (0.00–0.13) | 0.06 | 0.000 | 0.000 |
| te | excl_target | en | adv | 52 | 0.02 | 0.00 (0.00–0.00) | 0.00 | 0.000 | 0.000 |
| yo | full | native | bb | 24 | 1.00 | 1.00 (1.00–1.00) | 1.00 | 0.000 | 0.000 |
| yo | full | native | adv | 24 | 0.40 | 0.08 (0.00–0.21) | 0.08 | 0.000 | 0.000 |
| yo | full | trans | bb | 26 | 1.00 | 1.00 (1.00–1.00) | 1.00 | 0.000 | 0.000 |
| yo | full | trans | adv | 26 | 0.25 | 0.00 (0.00–0.00) | 0.00 | 0.000 | 0.000 |
| yo | full | en | bb | 26 | 1.00 | 1.00 (1.00–1.00) | 1.00 | 0.000 | 0.000 |
| yo | full | en | adv | 26 | 0.23 | 0.00 (0.00–0.00) | 0.00 | 0.000 | 0.000 |
| yo | excl_target | native | bb | 24 | 0.46 | 0.00 (0.00–0.00) | 0.00 | 0.000 | 0.000 |
| yo | excl_target | native | adv | 24 | 0.26 | 0.00 (0.00–0.00) | 0.00 | 0.000 | 0.000 |
| yo | excl_target | trans | bb | 26 | 0.46 | 0.00 (0.00–0.00) | 0.00 | 0.000 | 0.000 |
| yo | excl_target | trans | adv | 26 | 0.20 | 0.00 (0.00–0.00) | 0.00 | 0.000 | 0.000 |
| yo | excl_target | en | bb | 26 | 0.46 | 0.00 (0.00–0.00) | 0.00 | 0.000 | 0.000 |
| yo | excl_target | en | adv | 26 | 0.13 | 0.00 (0.00–0.00) | 0.00 | 0.000 | 0.000 |
| id | full | native | bb | 17 | 0.96 | 0.94 (0.82–1.00) | 0.94 | 0.001 | 0.011 |
| id | full | native | adv | 17 | 0.62 | 0.24 (0.06–0.47) | 0.24 | 0.001 | 0.011 |
| id | full | trans | bb | 28 | 0.96 | 0.93 (0.82–1.00) | 0.93 | 0.001 | 0.011 |
| id | full | trans | adv | 28 | 0.60 | 0.18 (0.04–0.32) | 0.18 | 0.001 | 0.011 |
| id | full | en | bb | 28 | 0.97 | 0.96 (0.89–1.00) | 0.96 | 0.001 | 0.011 |
| id | full | en | adv | 28 | 0.39 | 0.00 (0.00–0.00) | 0.00 | 0.001 | 0.011 |
| id | excl_target | native | bb | 17 | 0.51 | 0.00 (0.00–0.00) | 0.00 | 0.001 | 0.006 |
| id | excl_target | native | adv | 17 | 0.45 | 0.00 (0.00–0.00) | 0.00 | 0.001 | 0.006 |
| id | excl_target | trans | bb | 28 | 0.54 | 0.11 (0.00–0.21) | 0.11 | 0.001 | 0.006 |
| id | excl_target | trans | adv | 28 | 0.48 | 0.07 (0.00–0.18) | 0.07 | 0.001 | 0.006 |
| id | excl_target | en | bb | 28 | 0.49 | 0.11 (0.00–0.21) | 0.11 | 0.001 | 0.006 |
| id | excl_target | en | adv | 28 | 0.33 | 0.00 (0.00–0.00) | 0.00 | 0.001 | 0.006 |

Gold FPR = fraction of truly relevant passages that would be wrongly removed; this is the main cost of the signal.

## 2. Surviving-poison rate under the attacker's best response (lower is better; outside brackets: attacker's best choice)

| lang | log | variant | questions | actual FPR | no defense | isolation only | query log + isolation |
|---|---|---|---|---|---|---|---|
| sw | full | native | 28 | 0.050 | 0.96 (0.89–1.00) bb | 0.43 (0.25–0.61) bb | 0.18 (0.04–0.32) adv |
| sw | full | trans | 47 | 0.050 | 0.98 (0.94–1.00) bb | 0.77 (0.64–0.87) bb | 0.53 (0.40–0.66) adv |
| sw | full | en | 47 | 0.050 | 0.98 (0.94–1.00) bb | 0.66 (0.53–0.79) bb | 0.34 (0.21–0.49) adv |
| sw | excl_target | native | 28 | 0.050 | 0.96 (0.89–1.00) bb | 0.43 (0.25–0.61) bb | 0.29 (0.14–0.46) bb |
| sw | excl_target | trans | 47 | 0.050 | 0.98 (0.94–1.00) bb | 0.77 (0.64–0.87) bb | 0.57 (0.45–0.72) bb |
| sw | excl_target | en | 47 | 0.050 | 0.98 (0.94–1.00) bb | 0.66 (0.53–0.79) bb | 0.51 (0.36–0.66) bb |
| te | full | native | 33 | 0.050 | 0.97 (0.94–1.00) bb | 0.21 (0.09–0.36) bb | 0.21 (0.09–0.36) adv |
| te | full | trans | 52 | 0.050 | 0.96 (0.90–1.00) bb | 0.46 (0.33–0.60) bb | 0.29 (0.17–0.40) adv |
| te | full | en | 52 | 0.050 | 0.96 (0.90–1.00) bb | 0.40 (0.27–0.54) bb | 0.08 (0.02–0.15) adv |
| te | excl_target | native | 33 | 0.050 | 0.97 (0.94–1.00) bb | 0.21 (0.09–0.36) bb | 0.21 (0.12–0.36) bb |
| te | excl_target | trans | 52 | 0.050 | 0.96 (0.90–1.00) bb | 0.46 (0.33–0.60) bb | 0.46 (0.33–0.60) bb |
| te | excl_target | en | 52 | 0.050 | 0.96 (0.90–1.00) bb | 0.40 (0.27–0.54) bb | 0.38 (0.27–0.52) bb |
| yo | full | native | 24 | 0.050 | 1.00 (1.00–1.00) bb | 0.25 (0.12–0.42) bb | 0.21 (0.04–0.38) adv |
| yo | full | trans | 26 | 0.050 | 1.00 (1.00–1.00) bb | 0.42 (0.27–0.62) bb | 0.31 (0.15–0.50) adv |
| yo | full | en | 26 | 0.050 | 1.00 (1.00–1.00) bb | 0.46 (0.27–0.65) bb | 0.15 (0.04–0.31) adv |
| yo | excl_target | native | 24 | 0.050 | 1.00 (1.00–1.00) bb | 0.25 (0.12–0.46) bb | 0.25 (0.12–0.46) bb |
| yo | excl_target | trans | 26 | 0.050 | 1.00 (1.00–1.00) bb | 0.42 (0.27–0.62) bb | 0.42 (0.27–0.62) bb |
| yo | excl_target | en | 26 | 0.050 | 1.00 (1.00–1.00) bb | 0.46 (0.27–0.65) bb | 0.46 (0.27–0.65) bb |
| id | full | native | 17 | 0.050 | 0.88 (0.71–1.00) bb | 0.65 (0.41–0.88) bb | 0.35 (0.12–0.59) adv |
| id | full | trans | 28 | 0.050 | 0.96 (0.89–1.00) bb | 0.71 (0.54–0.86) bb | 0.32 (0.14–0.50) adv |
| id | full | en | 28 | 0.050 | 1.00 (1.00–1.00) bb | 0.50 (0.32–0.68) bb | 0.32 (0.14–0.50) adv |
| id | excl_target | native | 17 | 0.050 | 0.88 (0.71–1.00) bb | 0.65 (0.41–0.88) bb | 0.65 (0.41–0.88) bb |
| id | excl_target | trans | 28 | 0.050 | 0.96 (0.89–1.00) bb | 0.71 (0.54–0.86) bb | 0.61 (0.43–0.79) bb |
| id | excl_target | en | 28 | 0.050 | 1.00 (1.00–1.00) bb | 0.50 (0.32–0.68) bb | 0.43 (0.28–0.64) bb |

excl_target is the pessimistic setting: the attacked questions never appeared in the log. The gap between the two settings is what the attacker gains by targeting new questions.
