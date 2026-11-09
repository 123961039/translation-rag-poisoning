# Query-log overlap detection (s >= 0.8; isolation rel_knn10; target total FPR 5%; exclusion bad)

## 1. The query-log signal itself

| lang | log | variant | form | n | mean poison s | poison flagged | flagged after deleting ? | FPR: random benign | FPR: gold |
|---|---|---|---|---|---|---|---|---|---|
| sw | full | native | bb | 56 | 0.98 | 0.96 (0.91–1.00) | 0.96 | 0.001 | 0.034 |
| sw | full | native | adv | 56 | 0.57 | 0.14 (0.07–0.23) | 0.14 | 0.001 | 0.034 |
| sw | full | trans | bb | 88 | 0.97 | 0.95 (0.91–0.99) | 0.95 | 0.001 | 0.034 |
| sw | full | trans | adv | 88 | 0.46 | 0.08 (0.03–0.14) | 0.08 | 0.001 | 0.034 |
| sw | full | en | bb | 88 | 0.99 | 0.99 (0.97–1.00) | 0.99 | 0.001 | 0.034 |
| sw | full | en | adv | 88 | 0.28 | 0.02 (0.00–0.06) | 0.02 | 0.001 | 0.034 |
| sw | excl_target | native | bb | 56 | 0.58 | 0.18 (0.09–0.29) | 0.18 | 0.001 | 0.020 |
| sw | excl_target | native | adv | 56 | 0.44 | 0.04 (0.00–0.09) | 0.04 | 0.001 | 0.020 |
| sw | excl_target | trans | bb | 88 | 0.57 | 0.19 (0.11–0.28) | 0.19 | 0.001 | 0.020 |
| sw | excl_target | trans | adv | 88 | 0.40 | 0.03 (0.00–0.08) | 0.03 | 0.001 | 0.020 |
| sw | excl_target | en | bb | 88 | 0.58 | 0.20 (0.12–0.30) | 0.20 | 0.001 | 0.020 |
| sw | excl_target | en | adv | 88 | 0.26 | 0.00 (0.00–0.00) | 0.00 | 0.001 | 0.020 |
| te | full | native | bb | 51 | 0.99 | 0.98 (0.94–1.00) | 0.98 | 0.000 | 0.000 |
| te | full | native | adv | 51 | 0.65 | 0.16 (0.06–0.26) | 0.16 | 0.000 | 0.000 |
| te | full | trans | bb | 100 | 0.86 | 0.76 (0.68–0.84) | 0.76 | 0.000 | 0.000 |
| te | full | trans | adv | 100 | 0.31 | 0.00 (0.00–0.00) | 0.00 | 0.000 | 0.000 |
| te | full | en | bb | 100 | 1.00 | 1.00 (1.00–1.00) | 1.00 | 0.000 | 0.000 |
| te | full | en | adv | 100 | 0.02 | 0.00 (0.00–0.00) | 0.00 | 0.000 | 0.000 |
| te | excl_target | native | bb | 51 | 0.42 | 0.08 (0.02–0.16) | 0.08 | 0.000 | 0.000 |
| te | excl_target | native | adv | 51 | 0.30 | 0.00 (0.00–0.00) | 0.00 | 0.000 | 0.000 |
| te | excl_target | trans | bb | 100 | 0.48 | 0.03 (0.00–0.07) | 0.03 | 0.000 | 0.000 |
| te | excl_target | trans | adv | 100 | 0.31 | 0.00 (0.00–0.00) | 0.00 | 0.000 | 0.000 |
| te | excl_target | en | bb | 100 | 0.41 | 0.07 (0.03–0.12) | 0.07 | 0.000 | 0.000 |
| te | excl_target | en | adv | 100 | 0.01 | 0.00 (0.00–0.00) | 0.00 | 0.000 | 0.000 |
| yo | full | native | bb | 70 | 1.00 | 1.00 (1.00–1.00) | 1.00 | 0.000 | 0.000 |
| yo | full | native | adv | 70 | 0.41 | 0.09 (0.03–0.16) | 0.09 | 0.000 | 0.000 |
| yo | full | trans | bb | 80 | 1.00 | 1.00 (1.00–1.00) | 1.00 | 0.000 | 0.000 |
| yo | full | trans | adv | 80 | 0.26 | 0.00 (0.00–0.00) | 0.00 | 0.000 | 0.000 |
| yo | full | en | bb | 80 | 1.00 | 1.00 (1.00–1.00) | 1.00 | 0.000 | 0.000 |
| yo | full | en | adv | 80 | 0.23 | 0.00 (0.00–0.00) | 0.00 | 0.000 | 0.000 |
| yo | excl_target | native | bb | 70 | 0.48 | 0.03 (0.00–0.07) | 0.03 | 0.000 | 0.000 |
| yo | excl_target | native | adv | 70 | 0.24 | 0.01 (0.00–0.04) | 0.01 | 0.000 | 0.000 |
| yo | excl_target | trans | bb | 80 | 0.49 | 0.03 (0.00–0.06) | 0.03 | 0.000 | 0.000 |
| yo | excl_target | trans | adv | 80 | 0.21 | 0.00 (0.00–0.00) | 0.00 | 0.000 | 0.000 |
| yo | excl_target | en | bb | 80 | 0.49 | 0.03 (0.00–0.06) | 0.03 | 0.000 | 0.000 |
| yo | excl_target | en | adv | 80 | 0.13 | 0.00 (0.00–0.00) | 0.00 | 0.000 | 0.000 |
| id | full | native | bb | 40 | 0.99 | 0.97 (0.93–1.00) | 0.97 | 0.001 | 0.011 |
| id | full | native | adv | 40 | 0.62 | 0.30 (0.17–0.45) | 0.30 | 0.001 | 0.011 |
| id | full | trans | bb | 62 | 0.98 | 0.97 (0.92–1.00) | 0.97 | 0.001 | 0.011 |
| id | full | trans | adv | 62 | 0.51 | 0.11 (0.05–0.19) | 0.11 | 0.001 | 0.011 |
| id | full | en | bb | 62 | 1.00 | 1.00 (1.00–1.00) | 1.00 | 0.001 | 0.011 |
| id | full | en | adv | 62 | 0.33 | 0.00 (0.00–0.00) | 0.00 | 0.001 | 0.011 |
| id | excl_target | native | bb | 40 | 0.56 | 0.10 (0.03–0.20) | 0.10 | 0.001 | 0.006 |
| id | excl_target | native | adv | 40 | 0.47 | 0.03 (0.00–0.10) | 0.03 | 0.001 | 0.006 |
| id | excl_target | trans | bb | 62 | 0.57 | 0.13 (0.05–0.23) | 0.13 | 0.001 | 0.006 |
| id | excl_target | trans | adv | 62 | 0.43 | 0.03 (0.00–0.08) | 0.03 | 0.001 | 0.006 |
| id | excl_target | en | bb | 62 | 0.55 | 0.15 (0.06–0.24) | 0.15 | 0.001 | 0.006 |
| id | excl_target | en | adv | 62 | 0.29 | 0.00 (0.00–0.00) | 0.00 | 0.001 | 0.006 |

Gold FPR = fraction of truly relevant passages that would be wrongly removed; this is the main cost of the signal.

## 2. Surviving-poison rate under the attacker's best response (lower is better; outside brackets: attacker's best choice)

| lang | log | variant | questions | actual FPR | no defense | isolation only | query log + isolation |
|---|---|---|---|---|---|---|---|
| sw | full | native | 56 | 0.050 | 0.98 (0.95–1.00) bb | 0.39 (0.27–0.52) bb | 0.14 (0.05–0.25) adv |
| sw | full | trans | 88 | 0.050 | 0.97 (0.93–1.00) bb | 0.73 (0.64–0.82) bb | 0.52 (0.42–0.62) adv |
| sw | full | en | 88 | 0.050 | 0.97 (0.92–1.00) bb | 0.61 (0.51–0.72) bb | 0.34 (0.25–0.44) adv |
| sw | excl_target | native | 56 | 0.050 | 0.98 (0.95–1.00) bb | 0.39 (0.27–0.52) bb | 0.30 (0.20–0.43) bb |
| sw | excl_target | trans | 88 | 0.050 | 0.97 (0.92–1.00) bb | 0.73 (0.64–0.82) bb | 0.57 (0.48–0.67) bb |
| sw | excl_target | en | 88 | 0.050 | 0.97 (0.92–1.00) bb | 0.61 (0.51–0.72) bb | 0.48 (0.37–0.58) bb |
| te | full | native | 51 | 0.050 | 0.98 (0.96–1.00) bb | 0.24 (0.14–0.35) bb | 0.16 (0.06–0.27) adv |
| te | full | trans | 100 | 0.050 | 0.98 (0.94–1.00) bb | 0.44 (0.35–0.54) bb | 0.21 (0.13–0.30) adv |
| te | full | en | 100 | 0.050 | 0.97 (0.94–1.00) bb | 0.34 (0.25–0.44) bb | 0.04 (0.01–0.08) adv |
| te | excl_target | native | 51 | 0.050 | 0.98 (0.96–1.00) bb | 0.24 (0.14–0.35) bb | 0.22 (0.14–0.35) bb |
| te | excl_target | trans | 100 | 0.050 | 0.98 (0.95–1.00) bb | 0.44 (0.34–0.55) bb | 0.43 (0.34–0.54) bb |
| te | excl_target | en | 100 | 0.050 | 0.97 (0.93–1.00) bb | 0.34 (0.25–0.44) bb | 0.32 (0.23–0.41) bb |
| yo | full | native | 70 | 0.050 | 0.99 (0.96–1.00) bb | 0.30 (0.20–0.41) bb | 0.20 (0.11–0.30) adv |
| yo | full | trans | 80 | 0.050 | 0.99 (0.96–1.00) bb | 0.59 (0.47–0.69) bb | 0.40 (0.30–0.51) adv |
| yo | full | en | 80 | 0.050 | 0.97 (0.94–1.00) bb | 0.44 (0.33–0.55) bb | 0.20 (0.11–0.30) adv |
| yo | excl_target | native | 70 | 0.050 | 0.99 (0.96–1.00) bb | 0.30 (0.20–0.40) bb | 0.30 (0.20–0.41) bb |
| yo | excl_target | trans | 80 | 0.050 | 0.99 (0.96–1.00) bb | 0.59 (0.49–0.69) bb | 0.57 (0.46–0.69) bb |
| yo | excl_target | en | 80 | 0.050 | 0.97 (0.94–1.00) bb | 0.44 (0.33–0.55) bb | 0.42 (0.31–0.54) bb |
| id | full | native | 40 | 0.050 | 0.95 (0.88–1.00) bb | 0.65 (0.50–0.78) bb | 0.35 (0.23–0.50) adv |
| id | full | trans | 62 | 0.050 | 0.95 (0.89–1.00) bb | 0.71 (0.60–0.82) bb | 0.40 (0.27–0.53) adv |
| id | full | en | 62 | 0.050 | 0.97 (0.92–1.00) bb | 0.61 (0.48–0.73) bb | 0.29 (0.18–0.40) adv |
| id | excl_target | native | 40 | 0.050 | 0.95 (0.88–1.00) bb | 0.65 (0.53–0.80) bb | 0.57 (0.40–0.72) bb |
| id | excl_target | trans | 62 | 0.050 | 0.95 (0.90–1.00) bb | 0.71 (0.60–0.82) bb | 0.61 (0.50–0.73) bb |
| id | excl_target | en | 62 | 0.050 | 0.97 (0.92–1.00) bb | 0.61 (0.48–0.73) bb | 0.52 (0.39–0.63) bb |

excl_target is the pessimistic setting: the attacked questions never appeared in the log. The gap between the two settings is what the attacker gains by targeting new questions.
