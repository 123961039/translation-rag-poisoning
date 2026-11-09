# Query-log overlap detection (s >= 0.8; isolation rel_knn10; target total FPR 5%; exclusion bad)

## 1. The query-log signal itself

| lang | log | variant | form | n | mean poison s | poison flagged | flagged after deleting ? | FPR: random benign | FPR: gold |
|---|---|---|---|---|---|---|---|---|---|
| sw | full | native | bb | 34 | 0.98 | 0.97 (0.91–1.00) | 0.97 | 0.001 | 0.034 |
| sw | full | native | adv | 34 | 0.62 | 0.18 (0.06–0.32) | 0.18 | 0.001 | 0.034 |
| sw | full | trans | bb | 54 | 0.99 | 0.98 (0.94–1.00) | 0.98 | 0.001 | 0.034 |
| sw | full | trans | adv | 54 | 0.47 | 0.07 (0.02–0.15) | 0.07 | 0.001 | 0.034 |
| sw | full | en | bb | 54 | 0.99 | 0.98 (0.94–1.00) | 0.98 | 0.001 | 0.034 |
| sw | full | en | adv | 54 | 0.26 | 0.00 (0.00–0.00) | 0.00 | 0.001 | 0.034 |
| sw | excl_target | native | bb | 34 | 0.61 | 0.21 (0.09–0.35) | 0.21 | 0.001 | 0.020 |
| sw | excl_target | native | adv | 34 | 0.49 | 0.06 (0.00–0.15) | 0.06 | 0.001 | 0.020 |
| sw | excl_target | trans | bb | 54 | 0.57 | 0.19 (0.09–0.28) | 0.19 | 0.001 | 0.020 |
| sw | excl_target | trans | adv | 54 | 0.40 | 0.04 (0.00–0.09) | 0.04 | 0.001 | 0.020 |
| sw | excl_target | en | bb | 54 | 0.59 | 0.20 (0.09–0.31) | 0.20 | 0.001 | 0.020 |
| sw | excl_target | en | adv | 54 | 0.24 | 0.00 (0.00–0.00) | 0.00 | 0.001 | 0.020 |
| te | full | native | bb | 39 | 1.00 | 1.00 (1.00–1.00) | 1.00 | 0.000 | 0.000 |
| te | full | native | adv | 39 | 0.65 | 0.10 (0.03–0.21) | 0.10 | 0.000 | 0.000 |
| te | full | trans | bb | 78 | 0.84 | 0.73 (0.63–0.82) | 0.73 | 0.000 | 0.000 |
| te | full | trans | adv | 78 | 0.34 | 0.00 (0.00–0.00) | 0.00 | 0.000 | 0.000 |
| te | full | en | bb | 78 | 1.00 | 1.00 (1.00–1.00) | 1.00 | 0.000 | 0.000 |
| te | full | en | adv | 78 | 0.02 | 0.00 (0.00–0.00) | 0.00 | 0.000 | 0.000 |
| te | excl_target | native | bb | 39 | 0.41 | 0.08 (0.00–0.15) | 0.08 | 0.000 | 0.000 |
| te | excl_target | native | adv | 39 | 0.30 | 0.00 (0.00–0.00) | 0.00 | 0.000 | 0.000 |
| te | excl_target | trans | bb | 78 | 0.46 | 0.04 (0.00–0.09) | 0.04 | 0.000 | 0.000 |
| te | excl_target | trans | adv | 78 | 0.33 | 0.00 (0.00–0.00) | 0.00 | 0.000 | 0.000 |
| te | excl_target | en | bb | 78 | 0.38 | 0.08 (0.03–0.14) | 0.08 | 0.000 | 0.000 |
| te | excl_target | en | adv | 78 | 0.02 | 0.00 (0.00–0.00) | 0.00 | 0.000 | 0.000 |
| yo | full | native | bb | 61 | 1.00 | 1.00 (1.00–1.00) | 1.00 | 0.000 | 0.000 |
| yo | full | native | adv | 61 | 0.39 | 0.05 (0.00–0.11) | 0.05 | 0.000 | 0.000 |
| yo | full | trans | bb | 66 | 1.00 | 1.00 (1.00–1.00) | 1.00 | 0.000 | 0.000 |
| yo | full | trans | adv | 66 | 0.26 | 0.00 (0.00–0.00) | 0.00 | 0.000 | 0.000 |
| yo | full | en | bb | 66 | 1.00 | 1.00 (1.00–1.00) | 1.00 | 0.000 | 0.000 |
| yo | full | en | adv | 66 | 0.24 | 0.00 (0.00–0.00) | 0.00 | 0.000 | 0.000 |
| yo | excl_target | native | bb | 61 | 0.48 | 0.02 (0.00–0.05) | 0.02 | 0.000 | 0.000 |
| yo | excl_target | native | adv | 61 | 0.23 | 0.00 (0.00–0.00) | 0.00 | 0.000 | 0.000 |
| yo | excl_target | trans | bb | 66 | 0.49 | 0.02 (0.00–0.05) | 0.02 | 0.000 | 0.000 |
| yo | excl_target | trans | adv | 66 | 0.21 | 0.00 (0.00–0.00) | 0.00 | 0.000 | 0.000 |
| yo | excl_target | en | bb | 66 | 0.49 | 0.02 (0.00–0.05) | 0.02 | 0.000 | 0.000 |
| yo | excl_target | en | adv | 66 | 0.13 | 0.00 (0.00–0.00) | 0.00 | 0.000 | 0.000 |
| id | full | native | bb | 20 | 0.97 | 0.95 (0.85–1.00) | 0.95 | 0.001 | 0.011 |
| id | full | native | adv | 20 | 0.67 | 0.35 (0.15–0.60) | 0.35 | 0.001 | 0.011 |
| id | full | trans | bb | 30 | 0.98 | 0.97 (0.90–1.00) | 0.97 | 0.001 | 0.011 |
| id | full | trans | adv | 30 | 0.56 | 0.13 (0.03–0.27) | 0.13 | 0.001 | 0.011 |
| id | full | en | bb | 30 | 1.00 | 1.00 (1.00–1.00) | 1.00 | 0.001 | 0.011 |
| id | full | en | adv | 30 | 0.36 | 0.00 (0.00–0.00) | 0.00 | 0.001 | 0.011 |
| id | excl_target | native | bb | 20 | 0.55 | 0.10 (0.00–0.25) | 0.10 | 0.001 | 0.006 |
| id | excl_target | native | adv | 20 | 0.47 | 0.00 (0.00–0.00) | 0.00 | 0.001 | 0.006 |
| id | excl_target | trans | bb | 30 | 0.58 | 0.17 (0.03–0.30) | 0.17 | 0.001 | 0.006 |
| id | excl_target | trans | adv | 30 | 0.47 | 0.03 (0.00–0.10) | 0.03 | 0.001 | 0.006 |
| id | excl_target | en | bb | 30 | 0.53 | 0.17 (0.03–0.33) | 0.17 | 0.001 | 0.006 |
| id | excl_target | en | adv | 30 | 0.32 | 0.00 (0.00–0.00) | 0.00 | 0.001 | 0.006 |

Gold FPR = fraction of truly relevant passages that would be wrongly removed; this is the main cost of the signal.

## 2. Surviving-poison rate under the attacker's best response (lower is better; outside brackets: attacker's best choice)

| lang | log | variant | questions | actual FPR | no defense | isolation only | query log + isolation |
|---|---|---|---|---|---|---|---|
| sw | full | native | 34 | 0.050 | 0.97 (0.91–1.00) bb | 0.53 (0.35–0.71) bb | 0.21 (0.09–0.35) adv |
| sw | full | trans | 54 | 0.050 | 0.96 (0.91–1.00) bb | 0.80 (0.69–0.89) bb | 0.59 (0.46–0.72) adv |
| sw | full | en | 54 | 0.050 | 0.96 (0.91–1.00) bb | 0.67 (0.54–0.78) bb | 0.35 (0.22–0.48) adv |
| sw | excl_target | native | 34 | 0.050 | 0.97 (0.91–1.00) bb | 0.53 (0.35–0.71) bb | 0.38 (0.24–0.56) bb |
| sw | excl_target | trans | 54 | 0.050 | 0.96 (0.91–1.00) bb | 0.80 (0.69–0.91) bb | 0.63 (0.54–0.76) bb |
| sw | excl_target | en | 54 | 0.050 | 0.96 (0.91–1.00) bb | 0.67 (0.54–0.80) bb | 0.52 (0.39–0.65) bb |
| te | full | native | 39 | 0.050 | 1.00 (1.00–1.00) adv | 0.23 (0.10–0.38) bb | 0.18 (0.05–0.31) adv |
| te | full | trans | 78 | 0.050 | 0.97 (0.94–1.00) bb | 0.38 (0.28–0.49) bb | 0.19 (0.12–0.28) adv |
| te | full | en | 78 | 0.050 | 0.96 (0.92–1.00) bb | 0.29 (0.20–0.40) bb | 0.05 (0.01–0.12) adv |
| te | excl_target | native | 39 | 0.050 | 1.00 (1.00–1.00) adv | 0.23 (0.10–0.38) bb | 0.23 (0.13–0.38) bb |
| te | excl_target | trans | 78 | 0.050 | 0.97 (0.94–1.00) bb | 0.38 (0.28–0.50) bb | 0.38 (0.28–0.49) bb |
| te | excl_target | en | 78 | 0.050 | 0.96 (0.91–1.00) bb | 0.29 (0.20–0.40) bb | 0.28 (0.18–0.38) bb |
| yo | full | native | 61 | 0.050 | 0.98 (0.95–1.00) bb | 0.28 (0.18–0.39) bb | 0.20 (0.10–0.31) adv |
| yo | full | trans | 66 | 0.050 | 0.98 (0.95–1.00) bb | 0.52 (0.39–0.62) bb | 0.35 (0.23–0.47) adv |
| yo | full | en | 66 | 0.050 | 0.97 (0.92–1.00) bb | 0.38 (0.27–0.48) bb | 0.20 (0.11–0.29) adv |
| yo | excl_target | native | 61 | 0.050 | 0.98 (0.95–1.00) bb | 0.28 (0.18–0.39) bb | 0.28 (0.18–0.39) bb |
| yo | excl_target | trans | 66 | 0.050 | 0.98 (0.95–1.00) bb | 0.52 (0.38–0.65) bb | 0.52 (0.39–0.64) bb |
| yo | excl_target | en | 66 | 0.050 | 0.97 (0.92–1.00) bb | 0.38 (0.27–0.49) bb | 0.38 (0.27–0.50) bb |
| id | full | native | 20 | 0.050 | 1.00 (1.00–1.00) bb | 0.70 (0.50–0.90) bb | 0.40 (0.20–0.60) adv |
| id | full | trans | 30 | 0.050 | 0.93 (0.83–1.00) bb | 0.70 (0.53–0.87) bb | 0.50 (0.33–0.70) adv |
| id | full | en | 30 | 0.050 | 0.93 (0.83–1.00) bb | 0.63 (0.47–0.80) bb | 0.37 (0.20–0.53) adv |
| id | excl_target | native | 20 | 0.050 | 1.00 (1.00–1.00) bb | 0.70 (0.50–0.85) bb | 0.60 (0.40–0.80) bb |
| id | excl_target | trans | 30 | 0.050 | 0.93 (0.83–1.00) bb | 0.70 (0.53–0.87) bb | 0.57 (0.43–0.77) bb |
| id | excl_target | en | 30 | 0.050 | 0.93 (0.80–1.00) bb | 0.63 (0.47–0.80) bb | 0.53 (0.37–0.70) bb |

excl_target is the pessimistic setting: the attacked questions never appeared in the log. The gap between the two settings is what the attacker gains by targeting new questions.
