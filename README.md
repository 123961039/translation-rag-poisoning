# Translation-Based Corpus Poisoning in Low-Resource RAG

Code, data and results for the anonymous submission

> **Detecting Translation-Based Corpus Poisoning in Low-Resource RAG at Ingestion Time**
> (authors and affiliations withheld for double-blind review)

We study an attacker who writes misleading passages in English and machine-translates them into Swahili (`sw`), Telugu (`te`) and Yoruba (`yo`), with Indonesian (`id`) as a higher-resource control, and we benchmark ingestion-time detectors (`knn10`, `rel_knn10` and nine baselines) on MIRACL with a BGE-M3 retriever and Qwen readers.

> **Content warning.** `results/miracl/*/poison*.jsonl` contain deliberately **false statements**, some of them about real people and organisations, generated for research. Use them only on local copies of public corpora. Do not upload them to any public wiki or production system.

---

## Repository layout

```
code/                 all experiment scripts (Python 3.12+)
  ml_*.py             MIRACL pipeline used in the paper
  run_final.sh, run_review.sh, run_review2.sh
                      orchestration scripts for the earlier experiment runs
  ml_novelty_lof.py, ml_ingestion_distinct.py
                      GPU scripts for revised Tables 4 and 6
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
  novelty_lof/       Table 4 score arrays and run logs
  ingestion_distinct/  Table 6 per-round GPU timing logs
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
# download this repository from the anonymous link and unpack it
cd translation-rag-poisoning
python3.12 -m venv .venv && . .venv/bin/activate
pip install -r requirements-cpu.txt

python verify_paper_numbers.py           # includes abstract counts and revised Tables 4 and 6
python annotation/analyze_annotation.py  # annotation statistics (Table 1), 36 checks

cd code
bash rejudge_cpu.sh                      # detection tables under the three judgment sets -> results/miracl/rejudge/  (native and robustness detection results)
python rejudge_compare.py                # robustness across judgment sets
python stats_final.py                    # paired McNemar + Holm (Table 7, Sec. 5.7)
python ml_baselines_summary.py           # detector benchmark (Table 3)
python evidence_combo.py                 # evidence-check ablation and OR-combination (Table 3)
python ml_paired_variants.py             # trans vs en vs native, paired (Table 2)
python scale_seeds_analyze.py            # size x sampling mode, five seeds (Fig. 3)
python density_analyze.py                # fixed-effects regression (Sec. 5.5)
python density_2x2_analyze.py            # controlled 2x2 construction (Fig. 4a)
python asr_scale_compare.py              # generation-level ASR, full vs 45k (Sec. 5.7)
python reader_compare.py                 # second reader (Sec. 5.1)
python ml_hnsw_used.py --phase summary   # Table 6 right block
cd ..
python figures/make_data_figs.py results/miracl figures/out    # Figs. 3, 4
```

The verifier reads the released files. The analysis commands regenerate outputs in `results/miracl/` from the released per-question files; on our machines the regenerated files are byte-identical to the released ones (`rejudge_cpu.sh` keeps timestamped backups of the previous files under `results/miracl/`). Two steps of `rejudge_cpu.sh` need the corpus texts and are skipped without them: `ml_prefix_detect.py` (Table 5) and `ml_querylog_detect.py` (supplementary). The released prefix summary remains available for Table 5.

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

`code/ml_download.py` downloads MIRACL (corpus, topics, qrels) and BGE-M3. `code/ml_fetch.sh` is an alternative downloader for these inputs. The main GPU experiments used an NVIDIA RTX 4080 SUPER (16 GB). The Table 4 comparison and Table 6 distinct-passage timing used an RTX 4080. The HNSW study ran on a 16-core CPU container. Random seeds are fixed in the scripts (downsampling seeds 0-4, benign samples seed 0).

| level | step | script |
|---|---|---|
| 2 | download data and encoder | `ml_download.py`, `ml_fetch.sh` |
| 2 | embed corpora and queries | `ml_embed.py` |
| 2 | retrieval attack (incl. downsampled corpora) | `ml_attack.py` |
| 2 | detector features `knn10`, `rel_knn10` | `ml_detect.py` (`--subsample N` for scale runs) |
| 2 | scale robustness (5 seeds, keep/nokeep/article) | `scale_seeds.py` |
| 2 | 2x2 density construction | `density_2x2.py` |
| 2 | HNSW sensitivity | `ml_hnsw_used.py --phase encode/run` |
| 2 | shared-holdout novelty LOF | `ml_novelty_lof.py` |
| 2 | distinct-passage ingestion cost | `ml_ingestion_distinct.py` |
| 2 | second encoder (multilingual-E5-large; embedding-based detectors only) | `second_encoder.py` |
| 3 | generate English / native poison | `ml_gen_poison.py` (Yoruba expansion: `ml_yo_expand.py`, `merge_yo_new.py`) |
| 3 | machine translation, build variants | `ml_translate.py` |
| 3 | question review sheets / judgments | `ml_make_review.py`, `ml_review_to_json.py` |
| 3 | generation-level ASR | `ml_asr.py`, `ml_asr_reader.py` (second reader), `rejudge_asr.sh` |
| 3 | baselines, evidence check, ablation | `ml_baselines.py`, `ml_baselines_evidence.py`, `ml_evidence_ablation.py` |

`run_final.sh`, `run_review.sh` and `run_review2.sh` document the command sequence for the earlier experiment runs. Level 2 reuses the released poison sets (`results/miracl/*/poison.jsonl`), so its numbers are directly comparable to the paper.

### Detector protocols in Tables 3 and 4

- **Table 3** compares detectors on the full corpus across four languages and three poison variants in `bb` form. For a benign candidate, the kNN features exclude that candidate from both neighbor layers. The **kNN distance ratio** divides the neighbors' mean distance by the candidate's mean distance (with a stabilizer). The released baseline and second-encoder arrays keep the historical key `lof_knn10` for this score.
- **Table 4** compares standard novelty LOF, absolute kNN and relative kNN on the same BGE-M3 reference per language for `trans/bb`. The reference excludes the union of the 2,000 random calibration rows and 1,000 length-matched evaluation rows. Standard novelty LOF uses local reachability densities with exact cosine neighbors (`k=10`). In each score array the prefix follows `held_rows`, and the suffix follows `qids`. Look up `rand_rows` in the prefix for the 99th and 95th percentile thresholds and count positive scores strictly above them. Look up `match_rows` in the prefix for the AUROC negatives. The independent Yoruba sklearn run uses the same row and question order.

### Rerunning Tables 4 and 6 on GPU

Run from the repository root after downloading BGE-M3 and preparing the corpus Parquet files and fp16 embeddings. Table 4 also uses the released baseline sample IDs, poison records and native-speaker judgments. Both scripts use `PROJ` and `HF_MODELS` as above and accept `--model` to point to a local BGE-M3 model. These commands write to a separate directory for comparison with the released evidence.

```bash
mkdir -p rerun/novelty_lof rerun/ingestion_distinct
for lang in yo sw te id; do
    python code/ml_novelty_lof.py "$lang" --output-dir rerun/novelty_lof
done
for lang in sw te yo; do
    python code/ml_ingestion_distinct.py "$lang"
done > rerun/ingestion_distinct/sw_te_yo.log
python code/ml_ingestion_distinct.py id > rerun/ingestion_distinct/id.log
```

The Table 6 script uses seed `20261119` to select 1,000 unique formatted nonempty texts from a random draw of 5,000 rows per language. It removes the selected rows from the reference, warms up each batch configuration and alternates measurement order over six paired rounds. Each pair uses identical passages and CUDA synchronization around wall-clock timing. It reports the median of the six per-round overhead percentages, and batch-1,000 throughput as 1,000 divided by the median screened time. Screening includes uncached exact scoring and excludes index writes. The released logs cover batches of 1, 128 and 1,000 with encoding minibatches capped at 128. The earlier `ml_efficiency.py` timings include repeated texts and are historical.

## Where each result comes from

Table, figure and section numbers refer to the revised DASFAA paper.

| paper item | result file (`results/miracl/...`) | script |
|---|---|---|
| Table 1 (corpora, validation, annotation) | `review_judgments_native.json`, `baselines/summary.md`, `annotation/data/*.csv`, `annotation/results/recomputed.md` | `ml_review_to_json.py`, `ml_baselines_summary.py`, `annotation/analyze_annotation.py` |
| Table 2 (paired variants) | `paired_variants.md` | `ml_paired_variants.py` |
| Table 3, BGE-M3 block (detectors) | `baselines/summary.md`, `baselines/evidence_combo.md` | `ml_baselines*.py`, `ml_baselines_summary.py`, `evidence_combo.py` |
| Table 3, second encoder | `encoder2/me5-large/summary.md` (`encoder2/bge-m3/summary.md` reproduces the BGE-M3 block with the same script) | `second_encoder.py` |
| Table 4 (shared-holdout novelty LOF) | `novelty_lof/{yo,sw,te,id}.npz`, `novelty_lof/yo_sklearn.npz` | `ml_novelty_lof.py`, `verify_paper_numbers.py` |
| Table 5 (question prefix, attacker's best response) | `rejudge/native/prefix_summary_excl-bad.md` | `ml_prefix_detect.py` |
| Table 7 (end to end), paired tests | `rejudge/native/asr_summary_excl-bad.json`, `rejudge/native/asr_answers_excl-bad.jsonl`, `stats_final.md` | `ml_asr.py`, `stats_final.py` |
| Abstract and Sec. 5.1 (strict ASR and clean-to-target flips) | `rejudge/native/asr_answers_excl-bad.jsonl` | `verify_paper_numbers.py` |
| Fig. 3 (corpus size) | `scale_seeds/summary.{json,md}` | `scale_seeds.py`, `scale_seeds_analyze.py` |
| Fig. 4a (2x2 density) | `density_2x2/summary.md` | `density_2x2.py`, `density_2x2_analyze.py` |
| Fig. 4b (AUROC vs TPR) | `rejudge/native/metric_gap*.{json,md}` | `ml_metric_gap.py` |
| Sec. 5.1 (two readers) | `reader_compare.md` | `ml_asr_reader.py`, `reader_compare.py` |
| Sec. 5.3 (evidence-check cost) | `baselines/evidence_cost.json` | `ml_evidence_ablation.py` |
| Table 6 left (GPU screening) | `ingestion_distinct/id.log`, `ingestion_distinct/sw_te_yo.log` | `ml_ingestion_distinct.py`, `verify_paper_numbers.py` |
| Table 6 right (HNSW) | `hnsw/hnsw_<lang>_full.json`, `hnsw/summary.md` | `ml_hnsw_used.py` (see notes) |
| Sec. 5.5 (regression) | `scale_seeds/density.md` | `density_analyze.py` |
| Sec. 5.7 (ASR at 45k) | `asr_scale_compare.md` | `asr_scale.py`, `asr_scale_compare.py` |
| reproducibility, truncation | `feat_determinism.md`, `trunc_check.md` | `feat_determinism.py`, `trunc_check.py` |

## Notes

* `results/miracl/hnsw/` was produced by `code/ml_hnsw_used.py`, the exact script version that was run (its `--phase summary` regenerates `hnsw/summary.md` byte for byte). In that version the exact baseline for benign passages is read from the paper's GPU fp16 features (`detect_feats*.npz`), while exact search for poisons and all HNSW searches run in fp32 on the CPU. `code/ml_hnsw.py` is a later revision that recomputes all exact features on the GPU with the same arithmetic as `ml_detect.py`, removing this fp16/fp32 mix; its numbers can differ from the released ones by that small component (validation differences in `hnsw/summary.md`: knn10 ~1e-4, rel_knn10 <= 0.016).

* All code, comments and result summaries are in English. A few generated texts in `results/miracl/*/poison*.jsonl` and some reader answers in `asr_answers*.jsonl` contain Chinese characters: these are verbatim model outputs (the Qwen models occasionally code-switch into Chinese, e.g. writing a date with Chinese year/month/day characters) and are deliberately left unchanged, because the reported numbers are computed from them.
* Feature extraction is bit-for-bit reproducible on the same GPU; across GPUs fp16 ties at the neighbour boundary can change a few scores (see `results/miracl/feat_determinism.md`).
* Human annotation: anonymized item-level labels of all four tasks (including the Task B source key and the retest records), the annotation protocols, and a script that recomputes every annotation number in the paper are in `annotation/` (see `annotation/README.md`). Annotator identities and free-text notes are not released.
* MIRACL is distributed under Apache-2.0; please also follow its terms.

## License

Code: MIT (see `LICENSE`). Generated poison data and results: CC BY 4.0, for research use, subject to the content warning above.
