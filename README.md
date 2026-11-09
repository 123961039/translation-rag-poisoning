# Translation-Based Corpus Poisoning in Low-Resource RAG

Code, data and results for the ICDE 2027 EAB submission

> **[Experiment, Analysis, and Benchmark] Translation-Based Corpus Poisoning in Low-Resource RAG: Detectability, Corpus Geometry, and Evaluation Pitfalls**
> Shiwei Dong, Li Dai, MeiXiu Qin, Danzeng Quzhen, Zeguang Huang, Xi Cao, Nuo Qun, Nyima Tashi
> Xizang University · Minzu University of China

We study an attacker who writes misleading passages in English and machine-translates them into Swahili (`sw`), Telugu (`te`) and Yoruba (`yo`), with Indonesian (`id`) as a higher-resource control, and we benchmark ingestion-time detectors (`knn10`, `rel_knn10` and nine baselines) on MIRACL with a BGE-M3 retriever and Qwen readers.

> **Content warning.** `results/miracl/*/poison*.jsonl` contain deliberately **false statements**, some of them about real people and organisations, generated for research. Use them only on local copies of public corpora. Do not upload them to any public wiki or production system.

---

## Repository layout

```
code/                 all experiment scripts (Python 3.10+)
  ml_*.py             MIRACL pipeline used in the paper
  run_final.sh, run_review.sh, run_review2.sh
                      the exact orchestration used for the final results (step lists)
  common.py, ml_common.py   shared utilities and paths
  length_control.py, relative_isolation.py
                      preliminary English experiments (not reported in the paper);
                      kept because ml_detect.py, scale_seeds.py and density_2x2.py import
                      their length matching and leave-one-out neighbour search
results/miracl/       every result reported in the paper (see the mapping below)
  {sw,te,yo,id}/      poison sets, attack details, detector features (*.npz)
  rejudge/{native,none,old}/
                      main results under three question filters:
                      native = native-speaker validated (main), none = no filter,
                      old = first-pass review (robustness)
  scale_seeds/, density_2x2/, baselines/, asr_scale_sub45000/, reader_*/
  review_judgments_native.json   native-speaker validity judgments (Task A)
  run_logs/           status files of the final runs
annotation/
  protocols/          instructions given to annotators (Tasks A and B)
  results/            agreement and verification analyses (Tasks A–D)
figures/              scripts that regenerate the paper figures from results/
```

## Setup

```bash
git clone https://github.com/123961039/translation-rag-poisoning.git
cd translation-rag-poisoning
pip install -r requirements.txt

# optional: everything defaults to the repository root
export PROJ=$PWD                 # data/, emb/, results/ live here
export HF_MODELS=$PWD/models      # local model directory
```

Models (download into `$HF_MODELS`):

| role | model |
|---|---|
| retriever | `BAAI/bge-m3` (dense, fp16, max length 512) |
| poison generator | `Qwen/Qwen2.5-7B-Instruct` (Yoruba expansion: `Qwen/Qwen2.5-7B-Instruct-AWQ`) |
| machine translation | `facebook/nllb-200-distilled-600M` |
| reader 1 / judge / evidence check | `Qwen/Qwen3-14B-AWQ` (thinking disabled) |
| reader 2 | `Qwen/Qwen2.5-7B-Instruct-AWQ` |

`code/ml_download.py` downloads MIRACL (corpus, topics, qrels) and BGE-M3; `code/ml_fetch.sh` downloads the LLMs. All GPU experiments were run on one NVIDIA RTX 4080 SUPER (16 GB).

## Reproducing the paper

**Which files are final?** See `FINAL_RESULTS_MANIFEST.md`. Files directly under `results/miracl/` are mostly pre-validation intermediates; the paper uses `results/miracl/rejudge/native/` and the files listed in the manifest.

**Check the paper's numbers** (CPU, seconds):

```bash
python verify_paper_numbers.py   # recomputes ~66 reported numbers from the final files
```

### A. From the released results (CPU only, minutes)

All tables and figures can be regenerated from `results/` without a GPU:

```bash
cd code
python stats_final.py                    # paired McNemar + Holm, clean-correct subset, yo strata
python stats_final.py --set none
python ml_baselines_summary.py           # detector benchmark (Table II)
python evidence_combo.py                 # evidence check ablation and OR-combination
python ml_paired_variants.py             # trans vs en vs native (paired)
python ml_metric_gap.py                  # AUROC vs TPR@FPR disagreement
python scale_seeds_analyze.py            # corpus size x sampling mode, 5 seeds
python density_analyze.py                # fixed-effects regression on local density
python density_2x2_analyze.py            # controlled 2x2 intervention
python asr_scale_compare.py              # generation-level ASR, full vs 45k
python reader_compare.py                 # second reader
cd ..
python figures/make_data_figs.py results/miracl figures/out
python figures/concept_figs.py figures/out
```

### B. Full pipeline (GPU)

| step | script |
|---|---|
| download data and encoder | `ml_download.py`, `ml_fetch.sh` |
| embed corpora and queries | `ml_embed.py` |
| generate English / native poison | `ml_gen_poison.py` (Yoruba expansion: `ml_yo_expand.py`, `merge_yo_new.py`) |
| machine translation, build variants | `ml_translate.py` |
| retrieval attack (incl. downsampled corpora) | `ml_attack.py` |
| detector features `knn10`, `rel_knn10` | `ml_detect.py` (`--subsample N` for scale runs) |
| question review sheets / judgments | `ml_make_review.py`, `ml_review_to_json.py` |
| generation-level ASR | `ml_asr.py`, `ml_asr_reader.py` (second reader) |
| scale robustness (5 seeds, keep/nokeep/article) | `scale_seeds.py` |
| baselines, evidence check, ablation | `ml_baselines.py`, `ml_baselines_evidence.py`, `ml_evidence_ablation.py` |
| 2x2 density intervention | `density_2x2.py` |
| cost | `ml_efficiency.py` |
| re-filter with native judgments | `rejudge_cpu.sh`, `rejudge_asr.sh` |

`run_final.sh`, `run_review.sh` and `run_review2.sh` list the exact command sequence (with arguments) that produced the files in `results/`.

## Where each result comes from

| paper item | result file (`results/miracl/...`) | script |
|---|---|---|
| Table I (questions, hit@5) | `review_judgments_native.json`, `baselines/summary.md` | `ml_review_to_json.py`, `ml_baselines_summary.py` |
| Table II (detectors) | `baselines/summary.md`, `baselines/evidence_combo.md`, `baselines/evidence_cost.json` | `ml_baselines_summary.py`, `evidence_combo.py` |
| Table III, Fig. ASR | `rejudge/native/asr_summary_excl-bad.json`, `rejudge/native/asr_answers_excl-bad.jsonl`, `stats_final.md` | `ml_asr.py`, `stats_final.py` |
| Fig. scale | `scale_seeds/summary.json`, `scale_seeds/summary.md` | `scale_seeds.py`, `scale_seeds_analyze.py` |
| fixed-effects regression | `scale_seeds/density.md` | `density_analyze.py` |
| Fig. density (2x2) | `density_2x2/summary.md` | `density_2x2.py`, `density_2x2_analyze.py` |
| Fig. AUROC vs TPR | `rejudge/native/metric_gap*.json` | `ml_metric_gap.py` |
| paired variants | `paired_variants*.md` | `ml_paired_variants.py` |
| HNSW sensitivity | `hnsw/*.json`, `hnsw/summary.md` | `ml_hnsw_used.py` (see note below) |
| cost | `efficiency.md` | `ml_efficiency.py` |
| second reader | `reader_compare.md` | `ml_asr_reader.py`, `reader_compare.py` |
| ASR at 45k | `asr_scale_compare.md` | `asr_scale.py`, `asr_scale_compare.py` |
| reproducibility, truncation | `feat_determinism.md`, `trunc_check.md` | `feat_determinism.py`, `trunc_check.py` |
| human annotation (Tasks A–D) | `annotation/results/*.md` | — |

## Notes

* `results/miracl/hnsw/` was produced by `code/ml_hnsw_used.py`, the exact script version that was run (its `--phase summary` regenerates `hnsw/summary.md` byte for byte). In that version the exact baseline for benign passages is read from the paper's GPU fp16 features (`detect_feats*.npz`), while exact search for poisons and all HNSW searches run in fp32 on the CPU. `code/ml_hnsw.py` is a later revision that recomputes all exact features on the GPU with the same arithmetic as `ml_detect.py`, removing this fp16/fp32 mix; its numbers can differ from the released ones by that small component (validation differences in `hnsw/summary.md`: knn10 ~1e-4, rel_knn10 <= 0.016).

* All code, comments and result summaries are in English. A few generated texts in `results/miracl/*/poison*.jsonl` and some reader answers in `asr_answers*.jsonl` contain Chinese characters: these are verbatim model outputs (the Qwen models occasionally code-switch into Chinese, e.g. writing a date with Chinese year/month/day characters) and are deliberately left unchanged, because the reported numbers are computed from them.
* Feature extraction is bit-for-bit reproducible on the same GPU; across GPUs fp16 ties at the neighbour boundary can change a few scores (see `results/miracl/feat_determinism.md`).
* Annotation answer keys (which item is real / MT / LLM-written in the blind Task B) and the raw annotation sheets are not released; aggregated results are in `annotation/results/`.
* MIRACL is distributed under Apache-2.0; please also follow its terms.

## License

Code: MIT (see `LICENSE`). Generated poison data and results: CC BY 4.0, for research use, subject to the content warning above.
