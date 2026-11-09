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
| sw | 0.738 (0.65–0.81) | 0.738 (0.66–0.81) | 0.642 (0.56–0.72) | -0.096 |
| te | 0.890 (0.85–0.93) | 0.823 (0.76–0.87) | 0.784 (0.72–0.84) | -0.106 |
| yo | 0.824 (0.75–0.89) | 0.824 (0.74–0.89) | 0.827 (0.75–0.89) | +0.003 |
| id | 0.820 (0.76–0.87) | 0.605 (0.50–0.71) | 0.622 (0.51–0.72) | -0.199 |

**Within language** (same language, only corpus size changed; this is the clean control): 3/4 languages agree with 'smaller corpus -> harder to detect' (sw, te, id); flat yo.
Pooling all language x size points (n=12) Spearman rho=+0.04; this number mixes in inherent differences between languages and is for reference only; the line above is the conclusion.

## 3. Surviving-poison rate after filtering at 5% FPR (trans/bb)

| lang | full | 131,924 | 45,000 | change at smallest |
|---|---|---|---|---|
| sw | 0.75 (0.57–0.89) | — | 0.89 (0.79–1.00) | +0.14 |
| te | 0.39 (0.24–0.55) | 0.48 (0.30–0.67) | 0.48 (0.30–0.64) | +0.09 |
| yo | 0.42 (0.21–0.62) | — | 0.46 (0.25–0.67) | +0.04 |
| id | 0.71 (0.47–0.94) | 0.94 (0.82–1.00) | 0.88 (0.71–1.00) | +0.18 |

**Within language** (same language, only corpus size changed; this is the clean control): 4/4 languages agree with 'smaller corpus -> more poisons survive' (sw, te, yo, id).
Pooling all language x size points (n=10) Spearman rho=-0.04; this number mixes in inherent differences between languages and is for reference only; the line above is the conclusion.

## 4. Language ranking after aligning sizes to 45,000 passages

| lang | passages | detection AUROC | surviving-poison rate |
|---|---|---|---|
| sw | 45,496 | 0.642 | 0.89 |
| id | 47,757 | 0.622 | 0.88 |
| te | 45,727 | 0.784 | 0.48 |
| yo | 45,018 | 0.827 | 0.46 |

Sorted by surviving-poison rate from worst to best. If the top language is not the lowest-resource one, then 'low-resource languages are more vulnerable' is a property of corpus size, not of the language itself.

## 5. Detection difficulty of the three poison variants at 45,000 passages (AUROC vs length-matched)

| lang | form | native | trans | en |
|---|---|---|---|---|
| sw | bb | 0.835 | 0.642 | 0.749 |
| sw | adv | 0.905 | 0.711 | 0.851 |
| te | bb | 0.863 | 0.784 | 0.839 |
| te | adv | 0.872 | 0.834 | 0.920 |
| yo | bb | 0.905 | 0.827 | 0.874 |
| yo | adv | 0.965 | 0.922 | 0.974 |
| id | bb | 0.663 | 0.622 | 0.749 |
| id | adv | 0.760 | 0.729 | 0.825 |

Hardest-to-detect variant counts (8 language x form cells): native 0 times, trans 8 times, en 0 times. **trans** is hardest to detect in 8/8 cells.

## 6. Dose-response: full -> 45,000, the more it shrinks the more it drops

| lang | original passages | passages after | shrink factor | dAUROC | d surviving rate |
|---|---|---|---|---|---|
| yo | 49,043 | 45,018 | 1.1x | +0.003 | +0.04 |
| sw | 131,924 | 45,496 | 2.9x | -0.096 | +0.14 |
| te | 518,079 | 45,727 | 11.3x | -0.106 | +0.09 |
| id | 1,446,315 | 47,757 | 30.3x | -0.199 | +0.18 |

Spearman between shrink factor and dAUROC **rho=-1.000** (n=4 languages, permutation test two-sided p=0.083).
Spearman between shrink factor and d surviving rate **rho=+0.800**.

This section is the core of the scale control: not only the direction 'smaller corpora are more dangerous', but **how much it drops is ordered by how much it shrinks**. With only a few languages, the p value comes from a permutation test; do not use a large-sample approximation.

