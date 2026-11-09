#!/usr/bin/env bash
# Final round: merge new yo questions -> rerun all yo experiments (GPU) -> recompute all statistics (CPU) -> package and back up -> shut down.
# One command after starting the GPU instance:
#   cd "$(dirname "${BASH_SOURCE[0]}")"
#   nohup bash run_final.sh > run_final.log 2>&1 &
# Optional environment variables:
#   XLSX=/root/yo_expand.xlsx   returned yo annotation file (default path)
#   SHUTDOWN=0                  do not shut down at the end (default 1 = shut down)
#   GPU_TIMEOUT=4h              maximum wait for the GPU part; on timeout it is killed (against hangs), and statistics, packaging and shutdown still run
# Success / failure of each step is recorded in run_final_status.txt; a failed step does not block later statistics and shutdown;
# failed steps and reasons are in the log, to be redone next time.
set -u
cd "$(dirname "$0")"
PROJ=${PROJ:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}; R=$PROJ/results/miracl
XLSX=${XLSX:-/root/yo_expand.xlsx}; SHUTDOWN=${SHUTDOWN:-1}; GPU_TIMEOUT=${GPU_TIMEOUT:-4h}
export VLLM_CACHE_ROOT=${VLLM_CACHE_ROOT:-$HOME/.cache/vllm} TORCHINDUCTOR_CACHE_DIR=${TORCHINDUCTOR_CACHE_DIR:-$HOME/.cache/inductor}
STATUS=$PWD/run_final_status.txt; : > "$STATUS"
T0=$(date +%s)
el() { echo "$(( ($(date +%s) - T0) / 60 )) min"; }
step() {   # name command...
  local name=$1; shift
  echo; echo "======== $name (elapsed $(el)) $(date '+%m-%d %T') ========"
  if "$@"; then echo "OK    $name" | tee -a "$STATUS"; else echo "FAIL  $name (exit code $?)" | tee -a "$STATUS"; fi
}

# ---- 0. checks ----
echo "start $(date '+%F %T')"
miss=0
for f in "$XLSX" "$R/yo/annot_new/yo_expand_KEY_do_not_share.json" "$R/yo/poison_new.jsonl" \
         merge_yo_new.py yo_rerun.py rejudge_cpu.sh rejudge_compare.py scale_seeds_analyze.py \
         density_analyze.py ml_baselines_summary.py ml_paired_variants.py; do
  [ -e "$f" ] || { echo "missing $f"; miss=1; }
done
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader || { echo "no GPU (CPU-only instance?)"; miss=1; }
if [ $miss = 1 ]; then echo "checks failed; not running, not shutting down"; exit 1; fi
df -h "${PROJ:-.}" | tail -1

# ---- 1. merge new yo questions (CPU, seconds) ----
step "1 merge new yo questions" python merge_yo_new.py --xlsx "$XLSX"

# ---- 2. rerun yo (GPU) ----
if grep -q "^OK    1 " "$STATUS"; then
  step "2 rerun yo attack / detection / ASR / scale / baselines" timeout --signal=TERM "$GPU_TIMEOUT" python yo_rerun.py
else
  echo "step 1 failed, skipping step 2" | tee -a "$STATUS"
fi

# ---- 3. recompute all statistics (CPU) ----
step "3a detection and scale analyses for the three judgment sets" bash rejudge_cpu.sh
step "3b comparison table of the three judgment sets" python rejudge_compare.py
step "3c scale robustness (native)" python scale_seeds_analyze.py
step "3d scale robustness (old review)" python scale_seeds_analyze.py --judgments "$R/review_judgments.json"
step "3e scale robustness (no exclusion)" python scale_seeds_analyze.py --judgments none
step "3f local density (native)" python density_analyze.py
step "3g local density (no exclusion)" python density_analyze.py --judgments none
step "3h defense baselines (native)" python ml_baselines_summary.py
step "3i defense baselines (no exclusion)" python ml_baselines_summary.py --judgments none
step "3j paired poison variants (native)" python ml_paired_variants.py
step "3k paired poison variants (no exclusion)" python ml_paired_variants.py --judgments none
step "3l paired poison variants (45k)" python ml_paired_variants.py --feats _sub45000

# ---- 4. package, back up ----
echo; echo "======== 4 package (elapsed $(el)) ========"
cp "$STATUS" run_final.log "$R/" 2>/dev/null
cd "$R"
tar czf /root/final_results.tar.gz --ignore-failed-read \
  rejudge/compare.md rejudge/*/*.md rejudge/*/*.json \
  scale_seeds/summary*.md scale_seeds/density*.md baselines/summary*.md paired_variants*.md \
  reader_compare.md efficiency.md yo/poison_new_stats.json yo/trans_check_expand.json \
  review_judgments_native.json run_final_status.txt run_final.log 2>/dev/null
ls -lh /root/final_results.tar.gz
if [ -d /root/autodl-fs ]; then cp /root/final_results.tar.gz /root/autodl-fs/ && echo "backed up to /root/autodl-fs/"; fi
sync
echo; echo "step results:"; cat "$STATUS"
echo; echo "All done, total time $(el). Result package /root/final_results.tar.gz"
if [ "$SHUTDOWN" = 1 ]; then echo "shutting down in 60 s"; sleep 60; shutdown -h now; else echo "(SHUTDOWN=0, not shutting down)"; fi
