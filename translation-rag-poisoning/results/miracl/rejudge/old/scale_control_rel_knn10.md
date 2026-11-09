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
| sw | 0.727 (0.65–0.79) | 0.727 (0.65–0.79) | 0.624 (0.54–0.70) | -0.103 |
| te | 0.908 (0.88–0.93) | 0.844 (0.79–0.89) | 0.798 (0.74–0.85) | -0.110 |
| yo | 0.824 (0.78–0.87) | 0.824 (0.77–0.87) | 0.826 (0.78–0.87) | +0.002 |
| id | 0.773 (0.71–0.83) | 0.576 (0.48–0.68) | 0.573 (0.47–0.67) | -0.200 |

**Within language** (same language, only corpus size changed; this is the clean control): 3/4 languages agree with 'smaller corpus -> harder to detect' (sw, te, id); flat yo.
Pooling all language x size points (n=12) Spearman rho=+0.13; this number mixes in inherent differences between languages and is for reference only; the line above is the conclusion.

## 3. Surviving-poison rate after filtering at 5% FPR (trans/bb)

| lang | full | 131,924 | 45,000 | change at smallest |
|---|---|---|---|---|
| sw | 0.79 (0.65–0.91) | — | 0.91 (0.82–1.00) | +0.12 |
| te | 0.33 (0.18–0.46) | 0.38 (0.23–0.51) | 0.44 (0.28–0.59) | +0.10 |
| yo | 0.49 (0.36–0.62) | — | 0.49 (0.36–0.62) | +0.00 |
| id | 0.70 (0.50–0.90) | 0.95 (0.85–1.00) | 0.90 (0.75–1.00) | +0.20 |

**Within language** (same language, only corpus size changed; this is the clean control): 3/4 languages agree with 'smaller corpus -> more poisons survive' (sw, te, id); flat yo.
Pooling all language x size points (n=10) Spearman rho=-0.14; this number mixes in inherent differences between languages and is for reference only; the line above is the conclusion.

## 4. Language ranking after aligning sizes to 45,000 passages

| lang | passages | detection AUROC | surviving-poison rate |
|---|---|---|---|
| sw | 45,496 | 0.624 | 0.91 |
| id | 47,757 | 0.573 | 0.90 |
| yo | 45,018 | 0.826 | 0.49 |
| te | 45,727 | 0.798 | 0.44 |

Sorted by surviving-poison rate from worst to best. If the top language is not the lowest-resource one, then 'low-resource languages are more vulnerable' is a property of corpus size, not of the language itself.

## 5. Detection difficulty of the three poison variants at 45,000 passages (AUROC vs length-matched)

| lang | form | native | trans | en |
|---|---|---|---|---|
| sw | bb | 0.812 | 0.624 | 0.739 |
| sw | adv | 0.895 | 0.690 | 0.849 |
| te | bb | 0.856 | 0.798 | 0.850 |
| te | adv | 0.859 | 0.849 | 0.931 |
| yo | bb | 0.921 | 0.826 | 0.894 |
| yo | adv | 0.967 | 0.904 | 0.968 |
| id | bb | 0.607 | 0.573 | 0.709 |
| id | adv | 0.698 | 0.708 | 0.810 |

Hardest-to-detect variant counts (8 language x form cells): native 1 times, trans 7 times, en 0 times. **trans** is hardest to detect in 7/8 cells.
Exceptions: id/adv. How small the gaps are at the exceptions is in the table -- a difference of order 0.01 is noise and need not be treated as a counterexample.

## 6. Dose-response: full -> 45,000, the more it shrinks the more it drops

| lang | original passages | passages after | shrink factor | dAUROC | d surviving rate |
|---|---|---|---|---|---|
| yo | 49,043 | 45,018 | 1.1x | +0.002 | +0.00 |
| sw | 131,924 | 45,496 | 2.9x | -0.103 | +0.12 |
| te | 518,079 | 45,727 | 11.3x | -0.110 | +0.10 |
| id | 1,446,315 | 47,757 | 30.3x | -0.200 | +0.20 |

Spearman between shrink factor and dAUROC **rho=-1.000** (n=4 languages, permutation test two-sided p=0.083).
Spearman between shrink factor and d surviving rate **rho=+0.800**.

This section is the core of the scale control: not only the direction 'smaller corpora are more dangerous', but **how much it drops is ordered by how much it shrinks**. With only a few languages, the p value comes from a permutation test; do not use a large-sample approximation.

