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
code/                 all experiment scripts (Python 3.12+)
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
  data/               anonymized item-level labels of Tasks A-D and the retest
  protocols/          instructions given to annotators
  results/            recomputed statistics and the original analysis reports
  analyze_annotation.py   recomputes all annotation numbers of the paper
figures/              scripts that regenerate the paper figures from results/
```

## Reproduction levels

| level | what you do | needs | time |
|---|---|---|---|
| **1. Verify numbers** | recompute the paper's reported numbers, tables and figures from the frozen result files | CPU, Python >= 3.12, `requirements-cpu.txt` | ~10 min |
| **2. Rebuild key experiments** | recompute embeddings, retrieval, detector features and thresholds, scale/density experiments, HNSW | GPU (16 GB), MIRACL + BGE-M3, `requirements.txt` | ~1-2 days |
| **3. Full pipeline** | regenerate poisons, run readers / judge / evidence check, re-filter with the released judgments | as level 2 + vLLM and the LLMs below | ~3-4 days |

Which result files are final is listed in `FINAL_RESULTS_MANIFEST.md`; files directly under `results/miracl/` are partly pre-validation intermediates. The human annotation itself cannot be re-run; its item-level labels are released in `annotation/data/`, and levels 1-3 use the question filter derived from them (`results/miracl/review_judgments_native.json`).

### Level 1: the 10-minute path (CPU only)

```bash
git clone https://github.com/123961039/translation-rag-poisoning.git
cd translation-rag-poisoning
python3.12 -m venv .venv && . .venv/bin/activate
pip install -r requirements-cpu.txt

python verify_paper_numbers.py           # ~66 checks against the paper; prints ALL CHECKS PASSED
python annotation/analyze_annotation.py  # annotation statistics (Table II), 36 checks

cd code
bash rejudge_cpu.sh                      # detection tables under the three judgment sets -> results/miracl/rejudge/  (Tables I, VI, XI; Fig. 8)
python rejudge_compare.py                # robustness across judgment sets
python stats_final.py                    # paired McNemar + Holm (Fig. 9, Sec. V-G)
python ml_baselines_summary.py           # detector benchmark (Tables V, VI)
python evidence_combo.py                 # evidence-check ablation and OR-combination (Table V)
python ml_paired_variants.py             # trans vs en vs native, paired (Table IV)
python scale_seeds_analyze.py            # size x sampling mode, five seeds (Fig. 4, Table IX)
python density_analyze.py                # fixed-effects regression (Table X)
python density_2x2_analyze.py            # controlled 2x2 construction (Fig. 7)
python asr_scale_compare.py              # generation-level ASR, full vs 45k (Sec. V-G)
python reader_compare.py                 # second reader (Table III)
python ml_hnsw_used.py --phase summary   # HNSW table (Table VIII)
cd ..
python figures/make_data_figs.py results/miracl figures/out    # Figs. 4, 7, 8, 9
```

Every command rewrites its outputs in `results/miracl/` from the released per-question files; on our machines the regenerated files are byte-identical to the released ones (`rejudge_cpu.sh` keeps timestamped backups of the previous files under `results/miracl/`). Two steps of `rejudge_cpu.sh` (`ml_prefix_detect.py`, `ml_querylog_detect.py`, not used in the paper) need the corpus texts and are skipped without them.

### Levels 2 and 3 (GPU)

```bash
pip install -r requirements.txt          # pinned versions of the experiment server (CUDA 13.0)
export PROJ=$PWD                         # data/, emb/, results/ live here (default: repository root)
export HF_MODELS=$PWD/models             # local model directory
```

Models (download into `$HF_MODELS`):

| role | model |
|---|---|
| retriever | `BAAI/bge-m3` (dense, fp16, max length 512) |
| poison generator | `Qwen/Qwen2.5-7B-Instruct` (Yoruba expansion: `Qwen/Qwen2.5-7B-Instruct-AWQ`) |
| machine translation | `facebook/nllb-200-distilled-600M` |
| reader 1 / judge / evidence check | `Qwen/Qwen3-14B-AWQ` (thinking disabled) |
| reader 2 | `Qwen/Qwen2.5-7B-Instruct-AWQ` |

`code/ml_download.py` downloads MIRACL (corpus, topics, qrels) and BGE-M3; `code/ml_fetch.sh` downloads the LLMs. All GPU experiments were run on one NVIDIA RTX 4080 SUPER (16 GB); the HNSW study ran on a 16-core CPU container. Random seeds are fixed in the scripts (downsampling seeds 0-4, benign samples seed 0).

| level | step | script |
|---|---|---|
| 2 | download data and encoder | `ml_download.py`, `ml_fetch.sh` |
| 2 | embed corpora and queries | `ml_embed.py` |
| 2 | retrieval attack (incl. downsampled corpora) | `ml_attack.py` |
| 2 | detector features `knn10`, `rel_knn10` | `ml_detect.py` (`--subsample N` for scale runs) |
| 2 | scale robustness (5 seeds, keep/nokeep/article) | `scale_seeds.py` |
| 2 | 2x2 density construction | `density_2x2.py` |
| 2 | HNSW sensitivity | `ml_hnsw_used.py --phase encode/run` |
| 2 | cost | `ml_efficiency.py` |
| 3 | generate English / native poison | `ml_gen_poison.py` (Yoruba expansion: `ml_yo_expand.py`, `merge_yo_new.py`) |
| 3 | machine translation, build variants | `ml_translate.py` |
| 3 | question review sheets / judgments | `ml_make_review.py`, `ml_review_to_json.py` |
| 3 | generation-level ASR | `ml_asr.py`, `ml_asr_reader.py` (second reader), `rejudge_asr.sh` |
| 3 | baselines, evidence check, ablation | `ml_baselines.py`, `ml_baselines_evidence.py`, `ml_evidence_ablation.py` |

`run_final.sh`, `run_review.sh` and `run_review2.sh` list the exact command sequence (with arguments) that produced the files in `results/`. Level 2 reuses the released poison sets (`results/miracl/*/poison.jsonl`), so its numbers are directly comparable to the paper.

## Where each result comes from

Table and figure numbers refer to the submitted paper.

| paper item | result file (`results/miracl/...`) | script |
|---|---|---|
| Table I (data, hit@5) | `review_judgments_native.json`, `baselines/summary.md` | `ml_review_to_json.py`, `ml_baselines_summary.py` |
| Table II (annotation) | `annotation/data/*.csv`, `annotation/results/recomputed.md`, `review_judgments_native.json` | `annotation/analyze_annotation.py` |
| Table III (two readers) | `reader_compare.md` | `ml_asr_reader.py`, `reader_compare.py` |
| Table IV (paired variants) | `paired_variants.md` | `ml_paired_variants.py` |
| Tables V, VI (detector benchmark) | `baselines/summary.md`, `baselines/evidence_combo.md` | `ml_baselines*.py`, `ml_baselines_summary.py`, `evidence_combo.py` |
| Table VII (cost) | `efficiency.md`, `baselines/evidence_cost.json` | `ml_efficiency.py`, `ml_evidence_ablation.py` |
| Table VIII (HNSW) | `hnsw/*.json`, `hnsw/summary.md` | `ml_hnsw_used.py` (see notes) |
| Fig. 4, Table IX (corpus size) | `scale_seeds/summary.{json,md}` | `scale_seeds.py`, `scale_seeds_analyze.py` |
| Table X (regression) | `scale_seeds/density.md` | `density_analyze.py` |
| Fig. 7 (2x2 density) | `density_2x2/summary.md` | `density_2x2.py`, `density_2x2_analyze.py` |
| Fig. 8, Table XI (AUROC vs TPR) | `rejudge/native/metric_gap*.{json,md}` | `ml_metric_gap.py` |
| Tables XII, XIII, Fig. 9 (end to end) | `rejudge/native/asr_summary_excl-bad.json`, `rejudge/native/asr_answers_excl-bad.jsonl`, `stats_final.md` | `ml_asr.py`, `stats_final.py` |
| ASR at 45k (Sec. V-G) | `asr_scale_compare.md` | `asr_scale.py`, `asr_scale_compare.py` |
| reproducibility, truncation | `feat_determinism.md`, `trunc_check.md` | `feat_determinism.py`, `trunc_check.py` |

## Notes

* `results/miracl/hnsw/` was produced by `code/ml_hnsw_used.py`, the exact script version that was run (its `--phase summary` regenerates `hnsw/summary.md` byte for byte). In that version the exact baseline for benign passages is read from the paper's GPU fp16 features (`detect_feats*.npz`), while exact search for poisons and all HNSW searches run in fp32 on the CPU. `code/ml_hnsw.py` is a later revision that recomputes all exact features on the GPU with the same arithmetic as `ml_detect.py`, removing this fp16/fp32 mix; its numbers can differ from the released ones by that small component (validation differences in `hnsw/summary.md`: knn10 ~1e-4, rel_knn10 <= 0.016).

* All code, comments and result summaries are in English. A few generated texts in `results/miracl/*/poison*.jsonl` and some reader answers in `asr_answers*.jsonl` contain Chinese characters: these are verbatim model outputs (the Qwen models occasionally code-switch into Chinese, e.g. writing a date with Chinese year/month/day characters) and are deliberately left unchanged, because the reported numbers are computed from them.
* Feature extraction is bit-for-bit reproducible on the same GPU; across GPUs fp16 ties at the neighbour boundary can change a few scores (see `results/miracl/feat_determinism.md`).
* Human annotation: anonymized item-level labels of all four tasks (including the Task B source key and the retest records), the annotation protocols, and a script that recomputes every annotation number in the paper are in `annotation/` (see `annotation/README.md`). Annotator identities and free-text notes are not released.
* MIRACL is distributed under Apache-2.0; please also follow its terms.

## License

Code: MIT (see `LICENSE`). Generated poison data and results: CC BY 4.0, for research use, subject to the content warning above.
