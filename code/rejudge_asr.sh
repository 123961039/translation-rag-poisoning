#!/usr/bin/env bash
# Rerun generation-level ASR with the new question judgments (GPU, vLLM + Qwen3-14B-AWQ).
# Why rerun everything rather than only the missing questions: the attacked condition puts the poisons of all kept questions into the corpus together,
# so another question's poison can enter a question's top-5; which questions are kept affects every result. Only a full rerun is consistent.
# Usage (in code/, with a GPU):
#     bash rejudge_asr.sh                  # both native and none, about 1.5 hours
#     SRCS=native bash rejudge_asr.sh      # only the native set, about 40 minutes
# The old set is not rerun: the existing asr_*_excl-bad.* are copied into rejudge/old/.
set -euo pipefail
shopt -s nullglob
export VLLM_CACHE_ROOT=${VLLM_CACHE_ROOT:-$HOME/.cache/vllm}
export TORCHINDUCTOR_CACHE_DIR=${TORCHINDUCTOR_CACHE_DIR:-$HOME/.cache/inductor}
PROJ=${PROJ:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}
R=$PROJ/results/miracl
SRCS=${SRCS:-"native none"}
STAMP=$(date +%Y%m%d_%H%M%S)
BK=$R/_backup_asr_$STAMP
FILES=(asr_summary_excl-bad.md asr_summary_excl-bad.json asr_answers_excl-bad.jsonl)

judg() {
  case $1 in
    native) echo "$R/review_judgments_native.json" ;;
    none)   echo "$R/review_judgments_empty.json" ;;
    *) echo "rejudge_asr.sh only runs native / none" >&2; exit 1 ;;
  esac
}
[ -f "$R/review_judgments_native.json" ] || { echo "missing $R/review_judgments_native.json"; exit 1; }
echo '{}' > "$R/review_judgments_empty.json"

mkdir -p "$BK" "$R/rejudge/old"
for f in "${FILES[@]}"; do
  [ -f "$R/$f" ] || { echo "missing $R/$f (ASR results of the old review set)"; exit 1; }
  cp -p "$R/$f" "$R/rejudge/old/"; mv "$R/$f" "$BK/"
done
restore() {
  for f in "${FILES[@]}"; do
    [ -f "$R/$f" ] && { mkdir -p "$R/rejudge/_incomplete_asr_$STAMP"; mv "$R/$f" "$R/rejudge/_incomplete_asr_$STAMP/"; }
    cp -p "$BK/$f" "$R/$f"
  done
  echo "original ASR files restored (backup kept in $BK)"
}
trap restore EXIT
cd "$PROJ/code"
nvidia-smi --query-gpu=memory.used,memory.total --format=csv

for s in $SRCS; do
  J=$(judg "$s"); OUTD=$R/rejudge/$s; mkdir -p "$OUTD"; LOG=$OUTD/asr_run.log
  echo "================ ASR $s: $J ================" | tee "$LOG"
  python ml_asr.py --exclude bad --judgments "$J" --gpu_util 0 --max_len 0 2>&1 | tee -a "$LOG"
  for f in "${FILES[@]}"; do mv "$R/$f" "$OUTD/"; done
  echo "-> $s done" | tee -a "$LOG"
done
echo "All done. Next step (CPU is enough): python rejudge_compare.py"
