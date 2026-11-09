#!/usr/bin/env bash
# Rerun all CPU analyses with three question-judgment sets (native speakers / old first-pass review / none = no exclusion).
# Each set's results go to results/miracl/rejudge/<set>/ without overwriting the originals; the originals are restored afterwards.
# CPU only. Usage (in code/):
#     bash rejudge_cpu.sh                 # all three sets
#     SRCS=native bash rejudge_cpu.sh     # only the native set
set -euo pipefail
shopt -s nullglob
PROJ=${PROJ:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}
R=$PROJ/results/miracl
CODE=$PROJ/code
SRCS=${SRCS:-"native old none"}
STAMP=$(date +%Y%m%d_%H%M%S)
BK=$R/_backup_cpu_$STAMP
# these scripts write to the top level of results/miracl/ with file names that do not include the judgment source, so they overwrite each other
PAT=("analysis_excl-bad*" "scale_control.*" "scale_control_*" "metric_gap*" "rel_diag*"
     "prefix_summary_excl-bad.*" "querylog_summary_excl-bad.*")

judg() {   # set name -> judgment file
  case $1 in
    native) echo "$R/review_judgments_native.json" ;;
    old)    echo "$R/review_judgments.json" ;;
    none)   echo "$R/review_judgments_empty.json" ;;   # empty judgments + --exclude bad = nothing excluded
    *) echo "unknown set name $1" >&2; exit 1 ;;
  esac
}
for s in $SRCS; do J=$(judg "$s"); [ "$s" = none ] || [ -f "$J" ] || { echo "missing judgment file $J"; exit 1; }; done
# prevent two concurrent runs: the second one exits immediately
exec 9>"$R/.rejudge_cpu.lock"
flock -n 9 || { echo "another rejudge_cpu.sh is already running (check with ps -ef | grep rejudge); exiting"; exit 1; }
echo '{}' > "$R/review_judgments_empty.json"
for l in sw te yo id; do
  n=$(ls "$R/$l"/detect_feats*.npz 2>/dev/null | wc -l)
  [ "$n" -ge 3 ] || { echo "fewer than 3 detect_feats*.npz under $R/$l (full, _sub131924, _sub45000); check first"; exit 1; }
done

collect() {   # move all such top-level files into $1
  mkdir -p "$1"
  for p in "${PAT[@]}"; do for f in "$R"/$p; do [ -f "$f" ] && mv "$f" "$1/"; done; done
}
restore() {
  local left=("$R"/analysis_excl-bad* "$R"/rel_diag* "$R"/metric_gap*)
  if [ ${#left[@]} -gt 0 ]; then
    collect "$R/rejudge/_incomplete_$STAMP"
    echo "WARNING: exited early; unfinished outputs are in rejudge/_incomplete_$STAMP"
  fi
  for f in "$BK"/*; do b=$(basename "$f"); [ -e "$R/$b" ] || cp -p "$f" "$R/$b"; done
  echo "original files restored to results/miracl/ (backup kept in $BK)"
}

collect "$BK"                       # 1. move originals away (restored at the end)
trap restore EXIT
cd "$CODE"
NSETS=$(echo $SRCS | wc -w); TOTAL=$((NSETS * 15)); K=0; T0=$(date +%s)
mmss() { printf "%d:%02d" $(($1 / 60)) $(($1 % 60)); }
progress() {   # [k/total] progress bar, elapsed, estimated remaining
  local el=$(( $(date +%s) - T0 )) w=30 f=$((K * 30 / TOTAL)) eta="?"
  [ "$K" -gt 1 ] && eta=$(mmss $(( el * (TOTAL - K + 1) / (K - 1) )))
  printf "\n[%-${w}s] %d/%d  elapsed %s  remaining %s\n" "$(head -c $f /dev/zero | tr '\0' '#')" "$K" "$TOTAL" "$(mmss $el)" "$eta"
}

for s in $SRCS; do
  J=$(judg "$s"); OUTD=$R/rejudge/$s
  [ -d "$OUTD" ] && [ -n "$(ls -A "$OUTD")" ] && mv "$OUTD" "${OUTD}_old_$STAMP"
  mkdir -p "$OUTD"; LOG=$OUTD/run.log
  # ASR results (written by rejudge_asr.sh / yo_rerun.py) are not produced by this script; carry them over when moving the old directory
  for f in "${OUTD}_old_$STAMP"/asr_* "${OUTD}_old_$STAMP"/asr_run.log; do [ -f "$f" ] && cp -p "$f" "$OUTD/"; done
  echo "================ $s: $J ================" | tee "$LOG"
  run() {
    K=$((K + 1)); progress | tee -a "$LOG"
    echo "+ python $*" | tee -a "$LOG"
    local t=$(date +%s); python "$@" 2>&1 | tee -a "$LOG"
    echo "  (this step $(mmss $(( $(date +%s) - t ))))" | tee -a "$LOG"
  }

  run ml_analyze.py --exclude bad --judgments "$J"
  run ml_analyze.py --exclude bad --judgments "$J" --feat knn10
  for z in 131924 45000; do
    run ml_analyze.py --exclude bad --judgments "$J" --feats _sub$z --size sub$z
    run ml_analyze.py --exclude bad --judgments "$J" --feats _sub$z --size sub$z --feat knn10
  done
  # ml_scale.py writes scale_control.* for both features; rename right after each run
  run ml_scale.py;              for e in md json; do mv "$R/scale_control.$e" "$R/scale_control_rel_knn10.$e"; done
  run ml_scale.py --feat knn10; for e in md json; do mv "$R/scale_control.$e" "$R/scale_control_knn10.$e"; done
  run ml_metric_gap.py
  run ml_metric_gap.py --feats _sub45000
  run ml_rel_diag.py --exclude bad --judgments "$J"
  for z in 131924 45000; do run ml_rel_diag.py --exclude bad --judgments "$J" --feats _sub$z; done
  # these two read passage texts from data/miracl/<lang>/corpus.parquet (not shipped); skipped without it
  pq=("$PROJ"/data/miracl/*/corpus.parquet)   # nullglob is on: empty array when absent
  if [ ${#pq[@]} -gt 0 ]; then
    run ml_prefix_detect.py --exclude bad --judgments "$J"
    run ml_querylog_detect.py --exclude bad --judgments "$J"
  else
    echo "  (corpus texts not found: prefix / querylog steps skipped, released outputs kept)" | tee -a "$LOG"
    for f in "${OUTD}_old_$STAMP"/prefix_summary_* "${OUTD}_old_$STAMP"/querylog_summary_*; do [ -f "$f" ] && cp -p "$f" "$OUTD/"; done
  fi

  collect "$OUTD"
  python - "$OUTD" "$s" "$J" <<'PY'
import hashlib, json, sys, datetime, os
d, s, j = sys.argv[1:]
json.dump({"judgment_set": s, "judgments_file": j,
           "judgments_md5": hashlib.md5(open(j, "rb").read()).hexdigest(),
           "run_at": datetime.datetime.now().isoformat(timespec="seconds"),
           "note": "all analyses use --exclude bad; the none set uses an empty judgment file, i.e. nothing is excluded"},
          open(os.path.join(d, "meta.json"), "w"), ensure_ascii=False, indent=1)
PY
  echo "-> $s done, results in $OUTD" | tee -a "$LOG"
done
echo "All done, total time $(mmss $(( $(date +%s) - T0 ))). Next step: python rejudge_compare.py"
