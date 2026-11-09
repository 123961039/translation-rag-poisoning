"""
Generation-level ASR with a second reader (GPU).
ml_asr.py is not modified: this script only swaps its reader and calls it; the protocol (5 conditions, top-5, rel_knn10 defense at 5% FPR,
strict / loose ASR) is identical. Results go to a separate folder and do not overwrite the Qwen3 results.
    python ml_asr_reader.py --reader $HF_MODELS/<model dir> --tag llama31_8b
    python ml_asr_reader.py --reader ... --tag ... --prompt no_unknown    # alternative prompt (see below)
--prompt: orig = same as ml_asr.py (default); no_unknown = drop the sentence "answer unknown if the context does not answer the question".
  A diagnostic (ml_reader_probe.py) showed that Qwen2.5-7B answers unknown in 89-100% of clean questions with the original prompt (sw/yo/id)
  but answers normally without that sentence; Qwen3-14B gives nearly identical results with both prompts. Cross-reader comparisons use no_unknown for both.
    All other arguments are passed through to ml_asr.py (native-speaker judgments by default when --judgments is not given)
Output: results/miracl/reader_<tag>/asr_summary_excl-bad.md / .json, asr_answers_excl-bad.jsonl
"""
import os, shutil, sys, time

from vllm import LLM  # noqa: F401  import before torch (as in ml_asr.py)

import ml_asr
from ml_common import ROOT

FILES = ["asr_summary_excl-bad.md", "asr_summary_excl-bad.json", "asr_answers_excl-bad.jsonl"]


def main():
    argv = sys.argv[1:]
    def pop(flag):
        if flag not in argv:
            sys.exit(f"missing {flag}")
        i = argv.index(flag); v = argv[i + 1]; del argv[i:i + 2]; return v
    reader, tag = pop("--reader"), pop("--tag")
    prompt = pop("--prompt") if "--prompt" in argv else "orig"
    if prompt == "no_unknown":
        new = ml_asr.RAG_PROMPT.replace(" If the context does not answer it, reply exactly: unknown", "")
        assert new != ml_asr.RAG_PROMPT, "RAG_PROMPT text changed; the replacement did not apply"
        ml_asr.RAG_PROMPT = new
    elif prompt != "orig":
        sys.exit(f"unknown --prompt {prompt}")
    tag = tag if prompt == "orig" else f"{tag}_{prompt}"
    if not os.path.exists(os.path.join(reader, "config.json")):
        sys.exit(f"no config.json under {reader}; is the model fully downloaded?")
    R = os.path.join(ROOT, "results", "miracl")
    if "--judgments" not in argv:
        argv += ["--judgments", os.path.join(R, "review_judgments_native.json")]
    if "--exclude" not in argv:
        argv += ["--exclude", "bad"]
    outd = os.path.join(R, f"reader_{tag}")
    os.makedirs(outd, exist_ok=True)

    # ml_asr.py writes to fixed file names and would overwrite the Qwen3 results: move them aside and restore afterwards
    stamp = time.strftime("%Y%m%d_%H%M%S")
    bak = os.path.join(R, f"_backup_reader_{stamp}")
    os.makedirs(bak)
    for f in FILES:
        if os.path.exists(os.path.join(R, f)):
            shutil.move(os.path.join(R, f), os.path.join(bak, f))
    ml_asr.READER = reader
    sys.argv = ["ml_asr.py"] + argv
    print(f"reader: {reader}\nargs: {' '.join(argv)}\noutput dir: {outd}", flush=True)
    try:
        ml_asr.main()
        for f in FILES:
            if os.path.exists(os.path.join(R, f)):
                shutil.move(os.path.join(R, f), os.path.join(outd, f))
        open(os.path.join(outd, "READER.txt"), "w").write(f"{reader}\nprompt={prompt}\n" + " ".join(argv) + "\n")
        print(f"\nsaved to {outd}", flush=True)
    finally:
        for f in FILES:
            src = os.path.join(bak, f)
            if os.path.exists(src):
                if os.path.exists(os.path.join(R, f)):        # leftovers from an interrupted run
                    shutil.move(os.path.join(R, f), os.path.join(outd, f + ".incomplete"))
                shutil.move(src, os.path.join(R, f))
        os.rmdir(bak)
        print("original Qwen3 ASR files restored", flush=True)


if __name__ == "__main__":
    main()
