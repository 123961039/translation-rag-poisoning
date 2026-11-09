# Generation-level ASR across reader models (native-validated questions, top-5, defense rel_knn10 @ 5% FPR)

Each cell: models in order Qwen3-14B, orig prompt; Qwen3-14B, no-unknown; Qwen2.5-7B, no-unknown. Cross-model conclusions use only the two runs with the same prompt.

## clean: accuracy / unknown rate

| lang | questions | Qwen3-14B, orig prompt | Qwen3-14B, no-unknown | Qwen2.5-7B, no-unknown |
|---|---|---|---|---|
| sw | 47 | 0.83 / 0.00 | 0.79 / 0.00 | 0.70 / 0.00 |
| te | 52 | 0.92 / 0.00 | 0.87 / 0.00 | 0.73 / 0.00 |
| yo | 26 | 0.69 / 0.00 | 0.62 / 0.00 | 0.54 / 0.00 |
| id | 28 | 0.64 / 0.04 | 0.64 / 0.00 | 0.61 / 0.00 |

## trans/bb: attacked ASR -> ASR under realistic defense (fraction recovered)

| lang | questions | Qwen3-14B, orig prompt | Qwen3-14B, no-unknown | Qwen2.5-7B, no-unknown |
|---|---|---|---|---|
| sw | 47 | 0.28 (0.15-0.40) -> 0.26 (8%) | 0.19 (0.09-0.30) -> 0.19 (0%) | 0.26 (0.13-0.38) -> 0.23 (8%) |
| te | 52 | 0.15 (0.06-0.25) -> 0.08 (50%) | 0.17 (0.08-0.29) -> 0.08 (56%) | 0.35 (0.23-0.48) -> 0.13 (61%) |
| yo | 26 | 0.50 (0.31-0.69) -> 0.19 (62%) | 0.50 (0.31-0.69) -> 0.19 (62%) | 0.50 (0.31-0.69) -> 0.31 (38%) |
| id | 28 | 0.32 (0.14-0.50) -> 0.21 (33%) | 0.25 (0.11-0.43) -> 0.21 (14%) | 0.25 (0.11-0.39) -> 0.18 (29%) |

## en/bb: attacked ASR -> ASR under realistic defense (fraction recovered)

| lang | questions | Qwen3-14B, orig prompt | Qwen3-14B, no-unknown | Qwen2.5-7B, no-unknown |
|---|---|---|---|---|
| sw | 47 | 0.21 (0.11-0.34) -> 0.17 (20%) | 0.15 (0.06-0.28) -> 0.13 (14%) | 0.38 (0.26-0.53) -> 0.19 (50%) |
| te | 52 | 0.17 (0.08-0.27) -> 0.08 (56%) | 0.15 (0.06-0.25) -> 0.08 (50%) | 0.38 (0.25-0.52) -> 0.13 (65%) |
| yo | 26 | 0.88 (0.77-1.00) -> 0.38 (57%) | 0.73 (0.58-0.88) -> 0.38 (47%) | 0.46 (0.27-0.65) -> 0.27 (42%) |
| id | 28 | 0.11 (0.00-0.21) -> 0.07 (33%) | 0.14 (0.04-0.29) -> 0.07 (50%) | 0.21 (0.07-0.39) -> 0.11 (50%) |

## native/bb: attacked ASR -> ASR under realistic defense (fraction recovered)

| lang | questions | Qwen3-14B, orig prompt | Qwen3-14B, no-unknown | Qwen2.5-7B, no-unknown |
|---|---|---|---|---|
| sw | 28 | 0.25 (0.11-0.43) -> 0.07 (71%) | 0.21 (0.07-0.39) -> 0.07 (67%) | 0.39 (0.21-0.57) -> 0.14 (64%) |
| te | 33 | 0.27 (0.12-0.42) -> 0.09 (67%) | 0.24 (0.12-0.39) -> 0.09 (62%) | 0.52 (0.33-0.67) -> 0.12 (76%) |
| yo | 24 | 0.75 (0.54-0.92) -> 0.12 (83%) | 0.71 (0.50-0.88) -> 0.08 (88%) | 0.67 (0.46-0.83) -> 0.21 (69%) |
| id | 17 | 0.35 (0.12-0.59) -> 0.24 (33%) | 0.24 (0.06-0.47) -> 0.12 (50%) | 0.35 (0.12-0.53) -> 0.18 (50%) |

## Utility cost of the defense: clean accuracy -> clean_defended accuracy

| lang | Qwen3-14B, orig prompt | Qwen3-14B, no-unknown | Qwen2.5-7B, no-unknown |
|---|---|---|---|
| sw | 0.83 → 0.83 | 0.79 → 0.79 | 0.70 → 0.68 |
| te | 0.92 → 0.85 | 0.87 → 0.81 | 0.73 → 0.71 |
| yo | 0.69 → 0.62 | 0.62 → 0.54 | 0.54 → 0.54 |
| id | 0.64 → 0.64 | 0.64 → 0.64 | 0.61 → 0.64 |

Note: which passages the defense removes depends only on retrieval and isolation features, not on the reader, so 'false alarms / gold wrongly removed' are identical across models.
yo has 26 questions (including the expansion); CIs are wide, do not interpret differences within 0.1.
