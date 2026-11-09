# Effect of corpus size on generation-level ASR (Qwen3-14B, native-speaker judgments, full vs 45k, paired by question)

45k is identical to ml_detect --subsample 45000 (seed 0, all dev gold passages kept); defense features use the matching size.

| lang | variant | condition | questions | full ASR | 45k ASR | 45k higher / lower (questions) | p | clean correct at both sizes: questions / full / 45k |
|---|---|---|---|---|---|---|---|---|
| sw | trans | attacked | 47 | 0.28 | 0.28 | 2 / 2 | 1.000 | 34 / 0.21 / 0.24 |
| sw | trans | defended | 47 | 0.26 | 0.26 | 3 / 3 | 1.000 | 34 / 0.21 / 0.21 |
| te | trans | attacked | 52 | 0.15 | 0.17 | 3 / 2 | 1.000 | 46 / 0.11 / 0.17 |
| te | trans | defended | 52 | 0.08 | 0.12 | 3 / 1 | 0.625 | 46 / 0.04 / 0.11 |
| yo | trans | attacked | 26 | 0.50 | 0.50 | 0 / 0 | 1.000 | 18 / 0.56 / 0.56 |
| yo | trans | defended | 26 | 0.19 | 0.19 | 0 / 0 | 1.000 | 18 / 0.17 / 0.17 |
| id | trans | attacked | 28 | 0.32 | 0.29 | 1 / 2 | 1.000 | 18 / 0.33 / 0.33 |
| id | trans | defended | 28 | 0.21 | 0.21 | 2 / 2 | 1.000 | 18 / 0.17 / 0.22 |
| sw | native | attacked | 28 | 0.25 | 0.25 | 1 / 1 | 1.000 | 22 / 0.14 / 0.14 |
| sw | native | defended | 28 | 0.07 | 0.11 | 1 / 0 | 1.000 | 22 / 0.05 / 0.09 |
| te | native | attacked | 33 | 0.27 | 0.33 | 3 / 1 | 0.625 | 28 / 0.21 / 0.29 |
| te | native | defended | 33 | 0.09 | 0.18 | 3 / 0 | 0.250 | 28 / 0.07 / 0.11 |
| yo | native | attacked | 24 | 0.75 | 0.75 | 0 / 0 | 1.000 | 16 / 0.75 / 0.75 |
| yo | native | defended | 24 | 0.12 | 0.08 | 0 / 1 | 1.000 | 16 / 0.12 / 0.06 |
| id | native | attacked | 17 | 0.35 | 0.18 | 1 / 4 | 0.375 | 11 / 0.27 / 0.18 |
| id | native | defended | 17 | 0.24 | 0.18 | 2 / 3 | 1.000 | 11 / 0.18 / 0.18 |
| sw | en | attacked | 47 | 0.21 | 0.19 | 1 / 2 | 1.000 | 34 / 0.21 / 0.21 |
| sw | en | defended | 47 | 0.17 | 0.17 | 3 / 3 | 1.000 | 34 / 0.15 / 0.18 |
| te | en | attacked | 52 | 0.17 | 0.23 | 4 / 1 | 0.375 | 46 / 0.17 / 0.24 |
| te | en | defended | 52 | 0.08 | 0.15 | 5 / 1 | 0.219 | 46 / 0.07 / 0.15 |
| yo | en | attacked | 26 | 0.88 | 0.85 | 0 / 1 | 1.000 | 18 / 0.94 / 0.89 |
| yo | en | defended | 26 | 0.38 | 0.42 | 1 / 0 | 1.000 | 18 / 0.44 / 0.44 |
| id | en | attacked | 28 | 0.11 | 0.18 | 3 / 1 | 0.625 | 18 / 0.11 / 0.22 |
| id | en | defended | 28 | 0.07 | 0.11 | 2 / 1 | 1.000 | 18 / 0.06 / 0.11 |

## Clean accuracy (does shrinking the corpus make questions unanswerable?)

| lang | full | 45k |
|---|---|---|
| sw | 0.83 | 0.77 |
| te | 0.92 | 0.92 |
| yo | 0.69 | 0.69 |
| id | 0.64 | 0.79 |

Note: the 45k version keeps all dev gold passages (as in the scale experiments), so clean accuracy should not drop much;
changes in ASR mainly reflect weaker detection (defended) and changed retrieval ranking (attacked).
