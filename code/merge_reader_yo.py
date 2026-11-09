"""
After re-running ml_asr_reader.py for Yoruba only (26 questions), merge the Yoruba rows
into the result folders of both readers (CPU only).
    python merge_reader_yo.py
  reader_qwen3_14b_yo_no_unknown/                  → reader_qwen3_14b_no_unknown/
  reader_qwen2_5_7b_instruct_awq_yo_no_unknown/    → reader_qwen2_5_7b_instruct_awq_no_unknown/
Original files are backed up (*.bak_yo26). Then run python reader_compare.py to rebuild the comparison table.
"""
import json, os, shutil

PROJ = os.environ.get("PROJ", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
R = os.path.join(PROJ, "results", "miracl")
PAIRS = [("reader_qwen3_14b_yo_no_unknown", "reader_qwen3_14b_no_unknown"),
         ("reader_qwen2_5_7b_instruct_awq_yo_no_unknown", "reader_qwen2_5_7b_instruct_awq_no_unknown")]


def main():
    for src, dst in PAIRS:
        S, D = os.path.join(R, src), os.path.join(R, dst)
        if not os.path.exists(os.path.join(S, "asr_summary_excl-bad.json")):
            print(f"skip: no results under {S}"); continue
        for f in ("asr_summary_excl-bad.json", "asr_answers_excl-bad.jsonl"):
            shutil.copy(os.path.join(D, f), os.path.join(D, f + ".bak_yo26"))
        new, old = json.load(open(os.path.join(S, "asr_summary_excl-bad.json"))), json.load(open(os.path.join(D, "asr_summary_excl-bad.json")))
        old["rows"] = [r for r in old["rows"] if r["lang"] != "yo"] + [r for r in new["rows"] if r["lang"] == "yo"]
        old.setdefault("fp_stats", {})["yo"] = new.get("fp_stats", {}).get("yo")
        json.dump(old, open(os.path.join(D, "asr_summary_excl-bad.json"), "w"), indent=1, ensure_ascii=False)
        keep = [l for l in open(os.path.join(D, "asr_answers_excl-bad.jsonl")) if json.loads(l)["lang"] != "yo"]
        add = [l for l in open(os.path.join(S, "asr_answers_excl-bad.jsonl")) if json.loads(l)["lang"] == "yo"]
        open(os.path.join(D, "asr_answers_excl-bad.jsonl"), "w").writelines(keep + add)
        n = len({json.loads(l)["qid"] for l in add})
        print(f"{dst}: yo replaced by the new results for {n} questions")


if __name__ == "__main__":
    main()
