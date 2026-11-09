# Manual check of machine-translated poisons

## 1. Does the translation still express the specified wrong answer (translation of the first injected poison per question)

| lang | questions | y | partly | n | ? | share y (95% CI) |
|---|---|---|---|---|---|---|
| sw | 47 | 37 | 3 | 6 | 1 | 79% (65%–88%) |
| te | 52 | 46 | 2 | 2 | 2 | 88% (77%–95%) |
| yo | 60 | 50 | 6 | 4 | 0 | 83% (72%–91%) |
| id | 28 | 21 | 1 | 4 | 2 | 75% (57%–87%) |

## 2. Automatic matching vs human judgment

Precision = among questions the automatic check marks 'kept', the share judged y by humans; recall = among questions judged y by humans, the share the automatic check also marks 'kept'.

| lang | strict: precision | strict: recall | loose: precision | loose: recall |
|---|---|---|---|---|
| sw | 79% (29) | 62% (37) | 82% (44) | 97% (37) |
| te | 89% (9) | 17% (46) | 91% (44) | 87% (46) |
| yo | 83% (36) | 60% (50) | 82% (50) | 82% (50) |
| id | 85% (20) | 81% (21) | 81% (26) | 100% (21) |

## 3. trans/bb ASR recomputed on questions whose translation really expresses the wrong answer (Qwen3-14B, native judgments)

| lang | all: questions / attacked / defended | human y: questions / attacked / defended | human y or partly: questions / attacked / defended | human n questions: attacked |
|---|---|---|---|---|
| sw | 47 / 0.28 / 0.26 | 37 / 0.35 / 0.32 | 40 / 0.33 / 0.30 | 0.00 (6 questions) |
| te | 52 / 0.15 / 0.08 | 46 / 0.17 / 0.09 | 48 / 0.17 / 0.08 | 0.00 (2 questions) |
| yo | 26 / 0.50 / 0.19 | 22 / 0.55 / 0.23 | 23 / 0.52 / 0.22 | 0.33 (3 questions) |
| id | 28 / 0.32 / 0.21 | 21 / 0.43 / 0.29 | 22 / 0.41 / 0.27 | 0.00 (4 questions) |

Questions judged n should not count as valid attacks in the first place: if their ASR is low, the original trans ASR was pulled down by these 'broken translation' questions.
