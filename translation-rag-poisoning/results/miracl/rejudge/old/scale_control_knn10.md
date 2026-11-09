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
| sw | 0.669 (0.60–0.74) | 0.669 (0.60–0.74) | 0.633 (0.56–0.70) | -0.036 |
| te | 0.861 (0.84–0.88) | 0.828 (0.81–0.85) | 0.806 (0.78–0.83) | -0.055 |
| yo | 0.860 (0.83–0.89) | 0.860 (0.83–0.89) | 0.855 (0.83–0.88) | -0.005 |
| id | 0.723 (0.67–0.78) | 0.602 (0.53–0.68) | 0.558 (0.49–0.64) | -0.165 |

**Within language** (same language, only corpus size changed; this is the clean control): 3/4 languages agree with 'smaller corpus -> harder to detect' (sw, te, id); flat yo.
Pooling all language x size points (n=12) Spearman rho=+0.08; this number mixes in inherent differences between languages and is for reference only; the line above is the conclusion.

## 3. Surviving-poison rate after filtering at 5% FPR (trans/bb)

| lang | full | 131,924 | 45,000 | change at smallest |
|---|---|---|---|---|
| sw | 0.74 (0.59–0.88) | — | 0.82 (0.68–0.94) | +0.09 |
| te | 0.72 (0.56–0.87) | 0.79 (0.67–0.92) | 0.87 (0.77–0.97) | +0.15 |
| yo | 0.52 (0.39–0.66) | — | 0.56 (0.43–0.67) | +0.03 |
| id | 0.85 (0.70–1.00) | 0.95 (0.85–1.00) | 0.95 (0.85–1.00) | +0.10 |

**Within language** (same language, only corpus size changed; this is the clean control): 4/4 languages agree with 'smaller corpus -> more poisons survive' (sw, te, yo, id).
Pooling all language x size points (n=10) Spearman rho=+0.13; this number mixes in inherent differences between languages and is for reference only; the line above is the conclusion.

## 4. Language ranking after aligning sizes to 45,000 passages

| lang | passages | detection AUROC | surviving-poison rate |
|---|---|---|---|
| id | 47,757 | 0.558 | 0.95 |
| te | 45,727 | 0.806 | 0.87 |
| sw | 45,496 | 0.633 | 0.82 |
| yo | 45,018 | 0.855 | 0.56 |

Sorted by surviving-poison rate from worst to best. If the top language is not the lowest-resource one, then 'low-resource languages are more vulnerable' is a property of corpus size, not of the language itself.

## 5. Detection difficulty of the three poison variants at 45,000 passages (AUROC vs length-matched)

| lang | form | native | trans | en |
|---|---|---|---|---|
| sw | bb | 0.740 | 0.633 | 0.687 |
| sw | adv | 0.885 | 0.744 | 0.818 |
| te | bb | 0.833 | 0.806 | 0.826 |
| te | adv | 0.851 | 0.869 | 0.924 |
| yo | bb | 0.928 | 0.855 | 0.926 |
| yo | adv | 0.989 | 0.947 | 0.987 |
| id | bb | 0.545 | 0.558 | 0.650 |
| id | adv | 0.645 | 0.661 | 0.735 |

Hardest-to-detect variant counts (8 language x form cells): native 3 times, trans 5 times, en 0 times. **trans** is hardest to detect in 5/8 cells.
Exceptions: te/adv, id/bb, id/adv. How small the gaps are at the exceptions is in the table -- a difference of order 0.01 is noise and need not be treated as a counterexample.

## 6. Dose-response: full -> 45,000, the more it shrinks the more it drops

| lang | original passages | passages after | shrink factor | dAUROC | d surviving rate |
|---|---|---|---|---|---|
| yo | 49,043 | 45,018 | 1.1x | -0.005 | +0.03 |
| sw | 131,924 | 45,496 | 2.9x | -0.036 | +0.09 |
| te | 518,079 | 45,727 | 11.3x | -0.055 | +0.15 |
| id | 1,446,315 | 47,757 | 30.3x | -0.165 | +0.10 |

Spearman between shrink factor and dAUROC **rho=-1.000** (n=4 languages, permutation test two-sided p=0.083).
Spearman between shrink factor and d surviving rate **rho=+0.800**.

This section is the core of the scale control: not only the direction 'smaller corpora are more dangerous', but **how much it drops is ordered by how much it shrinks**. With only a few languages, the p value comes from a permutation test; do not use a large-sample approximation.

