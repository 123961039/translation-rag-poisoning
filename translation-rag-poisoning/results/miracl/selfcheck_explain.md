# Explanation of the self-check warning: old review rerun vs original files

original: _backup_cpu_20261028_205307; rerun: rejudge/old/

| lang | rows compared | max AUROC diff | questions (original -> rerun, trans/bb full) |
|---|---|---|---|
| sw | 36 | 0.00e+00 | 54 → 54 |
| te | 36 | 0.00e+00 | 78 → 78 |
| yo | 36 | 9.16e-02 | 14 → 66 |
| id | 36 | 0.00e+00 | 30 → 30 |

The yo expansion added 52 questions, 52 of which are not in the old review judgment file. load_keep keeps all unjudged questions,
so under the old review the number of kept yo questions grows and AUROC changes accordingly. The other three languages are bit-identical, so code and environment did not change.

In the paper, the yo entry of the 'old review' robustness column must note: added questions were not covered by the old review and are kept.
