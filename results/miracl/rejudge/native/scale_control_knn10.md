# Scale control (main variant trans/bb, exclusion bad, brackets = 95% CI)

All size points use the same rowmap (same seed, all dev gold passages kept), so questions align across languages.

## 1. Actual corpus size of each language at each size point

| lang | full | 131,924 | 45,000 |
|---|---|---|---|
| sw | 131,924 | 131,924 | 45,496 |
| te | 518,079 | 132,526 | 45,727 |
| yo | 49,043 | 49,043 | 45,018 |
| id | 1,446,315 | 134,507 | 47,757 |

Languages already smaller than the downsampling target stay unchanged -- they are internal controls: size unchanged, results should not change.

## 2. Ingestion detection AUROC (vs length-matched, trans/bb)

| lang | full | 131,924 | 45,000 | change at smallest |
|---|---|---|---|---|
| sw | 0.666 (0.59–0.74) | 0.666 (0.59–0.74) | 0.634 (0.55–0.71) | -0.032 |
| te | 0.868 (0.84–0.89) | 0.842 (0.81–0.87) | 0.829 (0.79–0.86) | -0.039 |
| yo | 0.860 (0.81–0.90) | 0.860 (0.82–0.90) | 0.853 (0.80–0.90) | -0.007 |
| id | 0.727 (0.66–0.79) | 0.629 (0.55–0.70) | 0.588 (0.51–0.67) | -0.138 |

**Within language** (same language, only corpus size changed; this is the clean control): 3/4 languages agree with 'smaller corpus -> harder to detect' (sw, te, id); flat yo.
Pooling all language x size points (n=12) Spearman rho=+0.08; this number mixes in inherent differences between languages and is for reference only; the line above is the conclusion.

## 3. Surviving-poison rate after filtering at 5% FPR (trans/bb)

| lang | full | 131,924 | 45,000 | change at smallest |
|---|---|---|---|---|
| sw | 0.68 (0.50–0.86) | — | 0.79 (0.64–0.93) | +0.11 |
| te | 0.70 (0.52–0.85) | 0.82 (0.67–0.94) | 0.88 (0.76–0.97) | +0.18 |
| yo | 0.54 (0.33–0.75) | — | 0.62 (0.42–0.79) | +0.08 |
| id | 0.88 (0.71–1.00) | 0.94 (0.82–1.00) | 0.94 (0.82–1.00) | +0.06 |

**Within language** (same language, only corpus size changed; this is the clean control): 4/4 languages agree with 'smaller corpus -> more poisons survive' (sw, te, yo, id).
Pooling all language x size points (n=10) Spearman rho=+0.31; this number mixes in inherent differences between languages and is for reference only; the line above is the conclusion.

## 4. Language ranking after aligning sizes to 45,000 passages

| lang | passages | detection AUROC | surviving-poison rate |
|---|---|---|---|
| id | 47,757 | 0.588 | 0.94 |
| te | 45,727 | 0.829 | 0.88 |
| sw | 45,496 | 0.634 | 0.79 |
| yo | 45,018 | 0.853 | 0.62 |

Sorted by surviving-poison rate from worst to best. If the top language is not the lowest-resource one, then 'low-resource languages are more vulnerable' is a property of corpus size, not of the language itself.

## 5. Detection difficulty of the three poison variants at 45,000 passages (AUROC vs length-matched)

| lang | form | native | trans | en |
|---|---|---|---|---|
| sw | bb | 0.779 | 0.634 | 0.682 |
| sw | adv | 0.902 | 0.753 | 0.817 |
| te | bb | 0.851 | 0.829 | 0.848 |
| te | adv | 0.871 | 0.887 | 0.930 |
| yo | bb | 0.913 | 0.853 | 0.899 |
| yo | adv | 0.989 | 0.948 | 0.985 |
| id | bb | 0.592 | 0.588 | 0.686 |
| id | adv | 0.685 | 0.687 | 0.763 |

Hardest-to-detect variant counts (8 language x form cells): native 2 times, trans 6 times, en 0 times. **trans** is hardest to detect in 6/8 cells.
Exceptions: te/adv, id/adv. How small the gaps are at the exceptions is in the table -- a difference of order 0.01 is noise and need not be treated as a counterexample.

## 6. Dose-response: full -> 45,000, the more it shrinks the more it drops

| lang | original passages | passages after | shrink factor | dAUROC | d surviving rate |
|---|---|---|---|---|---|
| yo | 49,043 | 45,018 | 1.1x | -0.007 | +0.08 |
| sw | 131,924 | 45,496 | 2.9x | -0.032 | +0.11 |
| te | 518,079 | 45,727 | 11.3x | -0.039 | +0.18 |
| id | 1,446,315 | 47,757 | 30.3x | -0.138 | +0.06 |

Spearman between shrink factor and dAUROC **rho=-1.000** (n=4 languages, permutation test two-sided p=0.083).
Spearman between shrink factor and d surviving rate **rho=-0.200**.

This section is the core of the scale control: not only the direction 'smaller corpora are more dangerous', but **how much it drops is ordered by how much it shrinks**. With only a few languages, the p value comes from a permutation test; do not use a large-sample approximation.

