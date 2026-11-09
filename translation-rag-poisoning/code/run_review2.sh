#!/usr/bin/env bash
# Second supplementary round: fix C10 (45k ASR file names carried a _sub45000 suffix) + evidence-check ablation / combination / cost. About 1 hour, shuts down automatically.
#   cd "$(dirname "${BASH_SOURCE[0]}")"
#   nohup bash run_review2.sh > run_review2.log 2>&1 &
# Optional: SHUTDOWN=0 (do not shut down); SKIP="G1"
set -u
cd "$(dirname "$0")"
PROJ=${PROJ:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}; R=$PROJ/results/miracl
SHUTDOWN=${SHUTDOWN:-1}; SKIP=${SKIP:-}; GPU_TIMEOUT=${GPU_TIMEOUT:-2h}
export VLLM_CACHE_ROOT=${VLLM_CACHE_ROOT:-$HOME/.cache/vllm} TORCHINDUCTOR_CACHE_DIR=${TORCHINDUCTOR_CACHE_DIR:-$HOME/.cache/inductor}
STATUS=$PWD/run_review2_status.txt; : > "$STATUS"; T0=$(date +%s)
el() { echo "$(( ($(date +%s) - T0) / 60 )) min"; }
step() {
  local id=$1 name=$2; shift 2
  case " $SKIP " in *" $id "*) echo "SKIP  $id $name" | tee -a "$STATUS"; return;; esac
  echo; echo "======== $id $name (elapsed $(el)) $(date '+%m-%d %T') ========"
  if "$@"; then echo "OK    $id $name" | tee -a "$STATUS"; else echo "FAIL  $id $name (exit code $?)" | tee -a "$STATUS"; fi
}
fix_c10() {
  mkdir -p "$R/asr_scale_sub45000"
  local n=0
  for f in "$R"/asr_*_excl-bad_sub45000.*; do
    [ -e "$f" ] || continue
    b=$(basename "$f"); mv -f "$f" "$R/asr_scale_sub45000/${b/_sub45000/}"; echo "  moved $b"; n=$((n+1))
  done
  [ -f "$R/asr_scale_sub45000/asr_answers_excl-bad.jsonl" ] || { echo "per-answer file for 45k not found"; ls "$R" | grep -i 45000; return 1; }
  python asr_scale_compare.py
}

echo "start $(date '+%F %T')"
miss=0
for f in ml_evidence_ablation.py evidence_combo.py reader_compare.py asr_scale_compare.py ml_baselines_evidence.py; do
  [ -f "$f" ] || { echo "missing $f"; miss=1; }
done
for l in sw te yo id; do [ -f "$R/baselines/${l}_evidence.npz" ] || { echo "missing baselines/${l}_evidence.npz"; miss=1; }; done
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader || { echo "no GPU (needs a GPU instance)"; miss=1; }
[ $miss = 1 ] && { echo "checks failed; not running, not shutting down"; exit 1; }

step C0 "fix 45k ASR file locations + size x ASR comparison" fix_c10
step C1 "cross-model comparison table (yo note corrected)" python reader_compare.py
step G1 "evidence-check ablation: no same-article evidence + throughput" timeout --signal=TERM "$GPU_TIMEOUT" python ml_evidence_ablation.py
step C2 "evidence check vs rel_knn10: ablation and combination (native)" python evidence_combo.py
step C3 "same (no exclusion)" python evidence_combo.py --judgments none

echo; echo "======== package (elapsed $(el)) ========"
cp "$STATUS" run_review2.log "$R/" 2>/dev/null
cd "$R"
tar czf /root/review2_results.tar.gz --ignore-failed-read asr_scale_compare.md asr_scale_sub45000/asr_summary_excl-bad.* \
  reader_compare.md baselines/evidence_combo*.md baselines/evidence_cost.json run_review2_status.txt run_review2.log 2>/dev/null
ls -lh /root/review2_results.tar.gz
[ -d /root/autodl-fs ] && cp /root/review2_results.tar.gz /root/autodl-fs/ && echo "backed up to /root/autodl-fs/"
sync
echo; cat "$STATUS"; echo; echo "All done, total time $(el). Result package /root/review2_results.tar.gz"
if [ "$SHUTDOWN" = 1 ]; then echo "shutting down in 60 s"; sleep 60; shutdown -h now; else echo "(SHUTDOWN=0, not shutting down)"; fi
