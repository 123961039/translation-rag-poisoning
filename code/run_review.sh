#!/usr/bin/env bash
# One-shot run addressing the internal review: GPU experiments -> CPU statistics -> package and back up -> shut down. About 2.5-3 hours.
#   cd "$(dirname "${BASH_SOURCE[0]}")"
#   nohup bash run_review.sh > run_review.log 2>&1 &
# Optional: SHUTDOWN=0 (do not shut down); GPU_TIMEOUT=2h (maximum time per GPU step); SKIP="G5" (skip steps, space-separated)
# Success / failure of each step is recorded in run_review_status.txt; a failed step does not block later ones; packaging and shutdown run as usual.
set -u
cd "$(dirname "$0")"
PROJ=${PROJ:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}; R=$PROJ/results/miracl; H=${HF_MODELS:-$PROJ/models}
SHUTDOWN=${SHUTDOWN:-1}; GPU_TIMEOUT=${GPU_TIMEOUT:-2h}; SKIP=${SKIP:-}
export VLLM_CACHE_ROOT=${VLLM_CACHE_ROOT:-$HOME/.cache/vllm} TORCHINDUCTOR_CACHE_DIR=${TORCHINDUCTOR_CACHE_DIR:-$HOME/.cache/inductor}
STATUS=$PWD/run_review_status.txt; : > "$STATUS"; T0=$(date +%s)
el() { echo "$(( ($(date +%s) - T0) / 60 )) min"; }
step() {   # id name command...
  local id=$1 name=$2; shift 2
  case " $SKIP " in *" $id "*) echo "SKIP  $id $name" | tee -a "$STATUS"; return;; esac
  echo; echo "======== $id $name (elapsed $(el)) $(date '+%m-%d %T') ========"
  if "$@"; then echo "OK    $id $name" | tee -a "$STATUS"; else echo "FAIL  $id $name (exit code $?)" | tee -a "$STATUS"; fi
}
gpu() { timeout --signal=TERM "$GPU_TIMEOUT" "$@"; }

echo "start $(date '+%F %T')"
miss=0
for f in stats_final.py selfcheck_explain.py feat_determinism.py density_2x2.py density_2x2_analyze.py asr_scale.py \
         asr_scale_compare.py merge_reader_yo.py regen_asr_md.py trunc_check.py ml_baselines_evidence.py \
         ml_baselines_summary.py ml_asr_reader.py reader_compare.py; do
  [ -f "$f" ] || { echo "missing $f"; miss=1; }
done
python -c "import openpyxl" 2>/dev/null || pip install -q openpyxl
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader || { echo "no GPU"; miss=1; }
[ $miss = 1 ] && { echo "checks failed; not running, not shutting down"; exit 1; }
df -h "${PROJ:-.}" | tail -1

# ---- GPU ----
step G1 "feature reproducibility diagnostic (id / yo)" gpu python feat_determinism.py --lang id yo
step G2 "second reader: rerun yo 26 questions (Qwen3)" gpu python ml_asr_reader.py --reader $H/Qwen3-14B-AWQ --tag qwen3_14b_yo \
     --prompt no_unknown --lang yo --gpu_util 0 --max_len 0
step G3 "second reader: rerun yo 26 questions (Qwen2.5)" gpu python ml_asr_reader.py --reader $H/Qwen2.5-7B-Instruct-AWQ \
     --tag qwen2_5_7b_instruct_awq_yo --prompt no_unknown --lang yo --gpu_util 0 --max_len 0
step G4 "size x local density 2x2 intervention" gpu python density_2x2.py
step G5 "generation-level ASR on the 45k corpus" gpu python asr_scale.py
step G6 "evidence-check baseline" gpu python ml_baselines_evidence.py

# ---- CPU ----
step C1 "merge second-reader yo" python merge_reader_yo.py
step C2 "cross-model comparison table" python reader_compare.py
step C3 "rebuild ASR tables from JSON" python regen_asr_md.py
step C4 "paired tests / clean subset / yo strata (native)" python stats_final.py
step C5 "same (no exclusion)" python stats_final.py --set none
step C6 "self-check warning explanation" python selfcheck_explain.py
step C7 "truncation rate" python trunc_check.py
step C8 "2x2 statistics (native)" python density_2x2_analyze.py
step C9 "2x2 statistics (no exclusion)" python density_2x2_analyze.py --judgments none
step C10 "size x generation-level ASR comparison" python asr_scale_compare.py
step C11 "baseline comparison (native, incl. evidence check and TPR@1%)" python ml_baselines_summary.py
step C12 "baseline comparison (no exclusion)" python ml_baselines_summary.py --judgments none

# ---- package ----
echo; echo "======== package (elapsed $(el)) ========"
cp "$STATUS" run_review.log "$R/" 2>/dev/null
cd "$R"
tar czf /root/review_results.tar.gz --ignore-failed-read \
  stats_final*.md selfcheck_explain.md feat_determinism.md trunc_check.md asr_scale_compare.md \
  density_2x2/summary*.md baselines/summary*.md reader_compare.md \
  rejudge/native/asr_summary_excl-bad.* rejudge/native/asr_answers_excl-bad.jsonl \
  rejudge/none/asr_summary_excl-bad.* reader_*_no_unknown/asr_summary_excl-bad.* \
  asr_scale_sub45000/asr_summary_excl-bad.* asr_scale_sub45000/asr_answers_excl-bad.jsonl \
  yo/poison.jsonl run_review_status.txt run_review.log 2>/dev/null
ls -lh /root/review_results.tar.gz
[ -d /root/autodl-fs ] && cp /root/review_results.tar.gz /root/autodl-fs/ && echo "backed up to /root/autodl-fs/"
sync
echo; cat "$STATUS"; echo; echo "All done, total time $(el). Result package /root/review_results.tar.gz"
if [ "$SHUTDOWN" = 1 ]; then echo "shutting down in 60 s"; sleep 60; shutdown -h now; else echo "(SHUTDOWN=0, not shutting down)"; fi
