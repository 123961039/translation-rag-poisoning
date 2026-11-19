# Final results manifest

The paper reports **only** results filtered by native-speaker validity judgments
(`results/miracl/review_judgments_native.json`; valid questions: sw 47, te 52, yo 26, id 28).
Install `requirements-cpu.txt` in a clean Python 3.12+ environment and run
`python verify_paper_numbers.py` from the repository root. Table numbers follow the revised DASFAA paper.

## Final files used in the paper

| paper item | file (under `results/miracl/`) |
|---|---|
| Table 1 (questions, hit@5) | `review_judgments_native.json`, `baselines/summary.json` |
| Table 3 (BGE-M3 detectors) | `baselines/summary.json`, `baselines/evidence_combo.md`, `baselines/evidence_cost.json` |
| Table 7 (end to end), paired tests | `rejudge/native/asr_answers_excl-bad.jsonl`, `rejudge/native/asr_summary_excl-bad.json`, `stats_final.md` |
| Abstract and Sec. 5.1 (43 strict successes, 32 after a correct clean answer) | `rejudge/native/asr_answers_excl-bad.jsonl` (match attacked `trans/bb` to clean by language and question ID) |
| Table 3 (second encoder) | `encoder2/me5-large/summary.{json,md}` |
| Table 4 (shared holdout) | `novelty_lof/{yo,sw,te,id}.npz` and `novelty_lof/gpu.log`; independent Yoruba cross-check in `novelty_lof/yo_sklearn.{npz,log}` |
| Table 5 (prefix and attacker's best response) | `rejudge/native/prefix_summary_excl-bad.{json,md}` |
| detection by variant / form | `rejudge/native/analysis_excl-bad*.json` |
| Table 2 (paired variant comparison) | `paired_variants.json` (native) |
| Figure 3 (scale) | `scale_seeds/summary.json` |
| fixed-effects regression | `scale_seeds/density.md` |
| Figure 4a (density 2x2) | `density_2x2/summary.md` |
| Figure 4b (AUROC vs TPR) | `rejudge/native/metric_gap.json`, `rejudge/native/metric_gap_sub45000.json` |
| second reader | `reader_compare.md` |
| ASR at 45k | `asr_scale_compare.md` |
| Table 6 left (distinct-passage GPU timing) | `ingestion_distinct/id.log`, `ingestion_distinct/sw_te_yo.log` |
| Table 6 right (HNSW) | `hnsw/hnsw_<lang>_full.json`, `hnsw/summary.md` (45k robustness in `hnsw/hnsw_<lang>_45000.json`) |
| reproducibility, truncation | `feat_determinism.md`, `trunc_check.md` |
| human annotation | `../../annotation/data/*.csv`, `../../annotation/results/recomputed.md` (`annotation/analyze_annotation.py`) |

The CPU verifier recomputes Table 4 from scores and Table 6 overhead from the six
paired times per language and batch. Table 6 HNSW values come from the existing
index summaries. See the GPU commands in [README.md](README.md) for rerunning
the two new benchmarks. The logs retain experimental records with terminal weight
loading progress and machine lifecycle messages removed.

## Historical timing

`efficiency.{md,json}` and `code/ml_efficiency.py` document the earlier benchmark,
which used repeated texts to fill some batches.

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
