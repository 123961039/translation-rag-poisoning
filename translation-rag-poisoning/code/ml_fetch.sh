#!/bin/bash
# Download MIRACL data and bge-m3 with hfd.sh (multi-threaded aria2c); same layout as ml_download.py.
#   bash ml_fetch.sh                 # default sw te yo id + bge-m3
#   bash ml_fetch.sh sw yo           # selected languages only (add NO_MODEL=1 to skip the model)
# Afterwards run: python ml_download.py --no_fetch   (converts the corpus jsonl.gz to parquet)
set -e
export HF_ENDPOINT=${HF_ENDPOINT:-https://hf-mirror.com}
ROOT=${PROJ:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}
HF=${HF_MODELS:-$PROJ/models}
LANGS=${@:-sw te yo id}

# locate hfd.sh: can be set with HFD=/path/to/hfd.sh
HFD=${HFD:-$(command -v hfd.sh || command -v hfd || ls /root/hfd.sh 2>/dev/null | head -1 || true)}
if [ -z "$HFD" ]; then
  echo "hfd.sh not found. The previous download command is recorded in:"; cat $HF/bge-base-en-v1.5/.hfd/last_download_command 2>/dev/null
  echo "set it with HFD=/path/to/hfd.sh bash ml_fetch.sh"; exit 1
fi
echo "using $HFD, mirror $HF_ENDPOINT"

for L in $LANGS; do
  D=$ROOT/data/miracl/$L
  mkdir -p $D
  echo "========== $L: queries and qrels =========="
  bash $HFD miracl/miracl --dataset --include "miracl-v1.0-$L/*" "miracl-v1.0-$L/*/*" --local-dir $D/raw -x 4 -j 5
  if [ -f $D/corpus.parquet ]; then
    echo "$D/corpus.parquet exists, skipping the corpus"
  else
    echo "========== $L: corpus =========="
    bash $HFD miracl/miracl-corpus --dataset --include "miracl-corpus-v1.0-$L/*" --local-dir $D/raw_corpus -x 8 -j 5
  fi
done

if [ -z "$NO_MODEL" ]; then
  echo "========== bge-m3 =========="
  # skip onnx (about 2 GB) and images
  bash $HFD BAAI/bge-m3 --exclude "onnx/*" "*.onnx" "*.onnx_data" "imgs/*" --local-dir $HF/bge-m3 -x 8
fi
df -h "$PROJ"
echo "next: python ml_download.py --no_fetch"
