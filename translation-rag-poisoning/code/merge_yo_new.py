"""
Yoruba expansion, step 3 (CPU): run after receiving the annotator's yo_expand__<name>.xlsx.
  1. Task A: a question is valid only if all four items are y (same rule as the first round); written into the yo part of review_judgments_native.json
     (source = native_expand; existing judgments are left unchanged)
  2. Task C: does the translation still state the wrong answer; saved as yo/trans_check_expand.json (used later to correct trans ASR)
  3. append the new questions to yo/poison.jsonl (original backed up; old question order unchanged, so downstream alignment is unaffected)
    python merge_yo_new.py --xlsx /root/yo_expand__xxx.xlsx
Then, on a GPU instance: bash yo_rerun.sh to re-run the Yoruba downstream steps.
"""
import argparse, json, os, shutil, time

from openpyxl import load_workbook

PROJ = os.environ.get("PROJ", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
R = os.path.join(PROJ, "results", "miracl")
RD = os.path.join(R, "yo")


def rows_of(ws):
    it = ws.iter_rows(values_only=True)
    head = [str(h).strip() for h in next(it)]
    for r in it:
        d = dict(zip(head, r))
        k = str(d.get(head[0]) or "").strip()
        if k and k != "EXAMPLE":
            yield k, d


def yn(x):
    return str(x or "").strip().lower()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--xlsx", required=True)
    args = ap.parse_args()
    key = json.load(open(os.path.join(RD, "annot_new", "yo_expand_KEY_do_not_share.json")))
    wb = load_workbook(args.xlsx, data_only=True)

    # ---- 1. Task A -> judgments ----
    jp = os.path.join(R, "review_judgments_native.json")
    J = json.load(open(jp))
    cols = ["Q1_translation_same", "Q2_passage_answers", "Q3_wrong_is_false", "Q4_same_type"]
    n_ok = n_bad = n_blank = 0
    for k, d in rows_of(wb["Task A"]):
        q = key[k]["qid"]
        vals = [yn(d.get(c)) for c in cols]
        if any(v == "" for v in vals):
            n_blank += 1
        fails = [c for c, v in zip(cols, vals) if v != "y"]
        lab = "ok" if not fails else "bad"
        n_ok += lab == "ok"; n_bad += lab == "bad"
        J.setdefault("yo", {})[q] = {"label": lab, "source": "native_expand", "item": k, "fails": fails}
    shutil.copy(jp, jp + f".bak_{time.strftime('%Y%m%d_%H%M%S')}")
    json.dump(J, open(jp, "w"), ensure_ascii=False, indent=1)
    print(f"Task A: valid {n_ok}, invalid {n_bad} (of which {n_blank} with empty cells, treated as invalid) -> written to {jp}")

    # ---- 2. Task C ----
    tc = {}
    for k, d in rows_of(wb["Task C"]):
        tc[key[k]["qid"]] = {"states_wrong_answer": yn(d.get("states_wrong_answer")), "notes": d.get("notes"),
                             "auto_strict": key[k]["strict_match"], "auto_loose": key[k]["loose_match"]}
    json.dump(tc, open(os.path.join(RD, "trans_check_expand.json"), "w"), ensure_ascii=False, indent=1)
    from collections import Counter
    print(f"Task C: {dict(Counter(v['states_wrong_answer'] for v in tc.values()))}")

    # ---- 3. append new questions ----
    pp = os.path.join(RD, "poison.jsonl")
    old = [json.loads(l) for l in open(pp)]
    new = [json.loads(l) for l in open(os.path.join(RD, "poison_new.jsonl"))]
    have = {it["qid"] for it in old}
    add = [it for it in new if it["qid"] not in have]
    if not add:
        print("the new questions are already in poison.jsonl (merged before); not appending again")
    else:
        shutil.copy(pp, pp + f".bak_before_expand_{time.strftime('%Y%m%d_%H%M%S')}")
        with open(pp, "a") as f:
            for it in add:
                f.write(json.dumps(it, ensure_ascii=False) + "\n")
        print(f"poison.jsonl: {len(old)} old + {len(add)} new = {len(old) + len(add)} questions (original backed up)")
    n_valid = sum(v["label"] != "bad" for v in J["yo"].values())
    print(f"\nYoruba valid questions in total: {n_valid}. Next (GPU): bash yo_rerun.sh")


if __name__ == "__main__":
    main()
