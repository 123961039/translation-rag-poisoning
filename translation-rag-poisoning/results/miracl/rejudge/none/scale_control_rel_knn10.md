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
| sw | 0.761 (0.71–0.81) | 0.761 (0.71–0.81) | 0.675 (0.62–0.73) | -0.085 |
| te | 0.899 (0.87–0.92) | 0.821 (0.78–0.86) | 0.778 (0.73–0.83) | -0.121 |
| yo | 0.802 (0.76–0.84) | 0.802 (0.76–0.84) | 0.801 (0.75–0.85) | -0.001 |
| id | 0.792 (0.75–0.83) | 0.577 (0.51–0.65) | 0.554 (0.49–0.63) | -0.238 |

**Within language** (same language, only corpus size changed; this is the clean control): 3/4 languages agree with 'smaller corpus -> harder to detect' (sw, te, id); flat yo.
Pooling all language x size points (n=12) Spearman rho=+0.25; this number mixes in inherent differences between languages and is for reference only; the line above is the conclusion.

## 3. Surviving-poison rate after filtering at 5% FPR (trans/bb)

| lang | full | 131,924 | 45,000 | change at smallest |
|---|---|---|---|---|
| sw | 0.70 (0.57–0.80) | — | 0.80 (0.70–0.91) | +0.11 |
| te | 0.37 (0.24–0.51) | 0.47 (0.33–0.61) | 0.49 (0.35–0.63) | +0.12 |
| yo | 0.54 (0.43–0.67) | — | 0.54 (0.43–0.66) | +0.00 |
| id | 0.72 (0.57–0.85) | 0.93 (0.85–1.00) | 0.95 (0.88–1.00) | +0.22 |

**Within language** (same language, only corpus size changed; this is the clean control): 3/4 languages agree with 'smaller corpus -> more poisons survive' (sw, te, id); flat yo.
Pooling all language x size points (n=10) Spearman rho=-0.12; this number mixes in inherent differences between languages and is for reference only; the line above is the conclusion.

## 4. Language ranking after aligning sizes to 45,000 passages

| lang | passages | detection AUROC | surviving-poison rate |
|---|---|---|---|
| id | 47,757 | 0.554 | 0.95 |
| sw | 45,496 | 0.675 | 0.80 |
| yo | 45,018 | 0.801 | 0.54 |
| te | 45,727 | 0.778 | 0.49 |

Sorted by surviving-poison rate from worst to best. If the top language is not the lowest-resource one, then 'low-resource languages are more vulnerable' is a property of corpus size, not of the language itself.

## 5. Detection difficulty of the three poison variants at 45,000 passages (AUROC vs length-matched)

| lang | form | native | trans | en |
|---|---|---|---|---|
| sw | bb | 0.863 | 0.675 | 0.768 |
| sw | adv | 0.918 | 0.729 | 0.863 |
| te | bb | 0.847 | 0.778 | 0.840 |
| te | adv | 0.853 | 0.838 | 0.929 |
| yo | bb | 0.915 | 0.801 | 0.887 |
| yo | adv | 0.964 | 0.904 | 0.969 |
| id | bb | 0.624 | 0.554 | 0.708 |
| id | adv | 0.717 | 0.699 | 0.815 |

Hardest-to-detect variant counts (8 language x form cells): native 0 times, trans 8 times, en 0 times. **trans** is hardest to detect in 8/8 cells.

## 6. Dose-response: full -> 45,000, the more it shrinks the more it drops

| lang | original passages | passages after | shrink factor | dAUROC | d surviving rate |
|---|---|---|---|---|---|
| yo | 49,043 | 45,018 | 1.1x | -0.001 | +0.00 |
| sw | 131,924 | 45,496 | 2.9x | -0.085 | +0.11 |
| te | 518,079 | 45,727 | 11.3x | -0.121 | +0.12 |
| id | 1,446,315 | 47,757 | 30.3x | -0.238 | +0.22 |

Spearman between shrink factor and dAUROC **rho=-1.000** (n=4 languages, permutation test two-sided p=0.083).
Spearman between shrink factor and d surviving rate **rho=+1.000**.

This section is the core of the scale control: not only the direction 'smaller corpora are more dangerous', but **how much it drops is ordered by how much it shrinks**. With only a few languages, the p value comes from a permutation test; do not use a large-sample approximation.

