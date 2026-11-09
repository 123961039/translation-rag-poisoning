set -e
cd "$(dirname "${BASH_SOURCE[0]}")"
python ml_translate.py > translate.log 2>&1
python ml_attack.py   > attack.log 2>&1
python ml_detect.py   > detect.log 2>&1
echo "ALL DONE $(date)" > run_all.done
