# Final results manifest

The paper reports **only** results filtered by native-speaker validity judgments
(`results/miracl/review_judgments_native.json`; valid questions: sw 47, te 52, yo 26, id 28).
Run `python verify_paper_numbers.py` to recompute the key numbers from the files below.

## Final files used in the paper

| paper item | file (under `results/miracl/`) |
|---|---|
| Table I (questions, hit@5) | `review_judgments_native.json`, `baselines/summary.json` |
| Table II (detectors) | `baselines/summary.json`, `baselines/evidence_combo.md`, `baselines/evidence_cost.json` |
| Table III, Fig. ASR, paired tests | `rejudge/native/asr_answers_excl-bad.jsonl`, `rejudge/native/asr_summary_excl-bad.json`, `stats_final.md` |
| detection by variant / form | `rejudge/native/analysis_excl-bad*.json` |
| paired variant comparison | `paired_variants.json` (native) |
| Fig. scale | `scale_seeds/summary.json` |
| fixed-effects regression | `scale_seeds/density.md` |
| Fig. density (2x2) | `density_2x2/summary.md` |
| Fig. AUROC vs TPR | `rejudge/native/metric_gap.json`, `rejudge/native/metric_gap_sub45000.json` |
| second reader | `reader_compare.md` |
| ASR at 45k | `asr_scale_compare.md` |
| approximate index (HNSW) | `hnsw/hnsw_<lang>_<full|45000>.json`, `hnsw/summary.md` |
| cost | `efficiency.md` |
| reproducibility, truncation | `feat_determinism.md`, `trunc_check.md` |
| human annotation | `../../annotation/results/*.md` |

## Robustness variants (not the main numbers)

* `rejudge/none/` – no question filter
* `rejudge/old/` – first-pass (non-native) review; new Yoruba questions were never reviewed and are kept
* `*_none.md` / `*_none.json` – same analyses without filtering

## NOT final – do not cite

The following files in `results/miracl/` are **intermediate outputs from before native-speaker
validation** (they use the first-pass review, e.g. te has 78 questions). They are kept because the
re-filtering scripts (`code/rejudge_cpu.sh`, `code/rejudge_asr.sh`) read the raw answers from them.

* `asr_answers_excl-bad.jsonl` – raw reader answers for all questions (input to re-filtering)
* `asr_summary_excl-bad.{json,md}`
* `attack_summary.*`, `detect_summary*.{json,md}`, `prefix_summary.*`, `querylog_summary.*`
* `review_judgments.json` (first-pass review), `review_judgments_empty.json`
