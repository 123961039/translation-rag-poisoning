# Test-retest agreement (round 1 vs round 2, same annotator)

## Task A: question validity

| lang | questions | validity agreement | κ valid | κ Q1 | κ Q2 | κ Q3 | κ Q4 | κ valid on disputed questions (n) |
|---|---|---|---|---|---|---|---|---|
| sw | 22 | 91% | 0.81 | 1.00 | 0.67 | 0.72 | — | 0.65 (13) |
| te | 25 | 96% | 0.90 | 0.65 | 0.90 | 0.10 | — | 0.76 (15) |
| yo | 7 | 86% | 0.59 | 0.28 | 0.46 | 0.03 | — | 0.00 (4) |
| id | 16 | 94% | 0.88 | 0.64 | 0.76 | 0.44 | — | 0.80 (10) |
| pooled | 70 | 93% | 0.85 | | | | | |

Interpretation of κ (Landis & Koch): 0.41-0.60 moderate, 0.61-0.80 substantial, >0.80 almost perfect.

## Task B: does it read as human-written

| lang | rows | naturalness agreement | κ natural | κ coherent | natural rate round 1 -> round 2: real / machine-translated / LLM-written |
|---|---|---|---|---|---|
| sw | 58 | 98% | 0.95 | 0.86 | 100%→100% (22) / 100%→100% (22) / 7%→0% (14) |
| te | 63 | 86% | 0.13 | 0.87 | 96%→88% (25) / 100%→92% (25) / 77%→85% (13) |
| yo | 19 | 53% | 0.21 | 0.57 | 100%→14% (7) / 86%→71% (7) / 20%→0% (5) |
| id | 41 | 90% | 0.46 | 0.77 | 87%→100% (15) / 94%→94% (16) / 80%→80% (10) |

Note: the coherence of real passages is affected by truncation in both rounds, so κ for coherence is for reference only.
