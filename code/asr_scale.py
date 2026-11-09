"""
Does the reader accept poisoned answers more readily on a smaller corpus? (GPU, about 30-40 minutes)
ml_asr.py is not modified: its two corpus-loading functions are replaced by the downsampled corpus; everything else is identical
(5 conditions, top-5, rel_knn10 defense at 5% FPR, defense features from the matching detect_feats_sub45000.npz).
Downsampling is identical to ml_detect.py --subsample 45000 (seed 0, all dev gold passages kept), so defense features match the corpus row by row.
    python asr_scale.py                       # default 45000, native-speaker judgments, four languages
Output: results/miracl/asr_scale_sub45000/asr_summary_excl-bad.json / .md, asr_answers_excl-bad.jsonl
Then: python asr_scale_compare.py
"""
import os, shutil, sys, time

from vllm import LLM  # noqa: F401  import before torch

import numpy as np

import ml_asr
from ml_common import ROOT, load_qrels, load_query_emb
from ml_eval_retrieval import subsample_rows

FILES = ["asr_summary_excl-bad.md", "asr_summary_excl-bad.json", "asr_answers_excl-bad.jsonl"]


def main():
    size = 45000
    argv = sys.argv[1:]
    if "--size" in argv:
        i = argv.index("--size"); size = int(argv[i + 1]); del argv[i:i + 2]
    R = os.path.join(ROOT, "results", "miracl")
    outd = os.path.join(R, f"asr_scale_sub{size}")
    os.makedirs(outd, exist_ok=True)
    if "--judgments" not in argv:
        argv += ["--judgments", os.path.join(R, "review_judgments_native.json")]
    if "--exclude" not in argv:
        argv += ["--exclude", "bad"]
    argv += ["--feats", f"_sub{size}", "--gpu_util", "0", "--max_len", "0"]

    orig_load, orig_text = ml_asr.load_corpus_emb, ml_asr.corpus_text_fn
    rowmaps = {}

    def rowmap_of(lang):
        if lang not in rowmaps:
            emb, cids = orig_load(lang)
            N = emb.shape[0]
            if size >= N:
                rowmaps[lang] = None
            else:
                qrels = load_qrels(lang, "dev"); _, qid2row = load_query_emb(lang)
                c2r = {c: i for i, c in enumerate(cids)}
                must = np.array(sorted({c2r[d] for q in qrels if q in qid2row for d in qrels[q] if d in c2r}))
                rowmaps[lang] = subsample_rows(N, size, must, 0)       # identical to ml_detect.py --subsample
        return rowmaps[lang]

    def load_sub(lang):
        emb, cids = orig_load(lang)
        rm = rowmap_of(lang)
        if rm is None:
            return emb, cids
        print(f"  [{lang}] downsampled corpus: {len(rm):,} passages (seed 0, all dev gold passages kept)", flush=True)
        return np.asarray(emb[rm]), [cids[r] for r in rm]

    def text_sub(lang):
        f = orig_text(lang); rm = rowmap_of(lang)
        return f if rm is None else (lambda r: f(int(rm[r])))

    ml_asr.load_corpus_emb, ml_asr.corpus_text_fn = load_sub, text_sub
    stamp = time.strftime("%Y%m%d_%H%M%S")
    bak = os.path.join(R, f"_backup_asrscale_{stamp}"); os.makedirs(bak)
    for f in FILES:
        if os.path.exists(os.path.join(R, f)):
            shutil.move(os.path.join(R, f), os.path.join(bak, f))
    sys.argv = ["ml_asr.py"] + argv
    print(f"size {size}; args {' '.join(argv)}; output dir {outd}", flush=True)
    try:
        ml_asr.main()
        for f in FILES:
            if os.path.exists(os.path.join(R, f)):
                shutil.move(os.path.join(R, f), os.path.join(outd, f))
        print(f"\nsaved to {outd}", flush=True)
    finally:
        for f in FILES:
            if os.path.exists(os.path.join(bak, f)):
                if os.path.exists(os.path.join(R, f)):
                    shutil.move(os.path.join(R, f), os.path.join(outd, f + ".incomplete"))
                shutil.move(os.path.join(bak, f), os.path.join(R, f))
        os.rmdir(bak)
        print("global ASR files restored", flush=True)


if __name__ == "__main__":
    main()
