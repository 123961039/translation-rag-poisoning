"""
Convert the manually edited review_all_judged.txt into review_judgments.json read by the scripts (CPU only, a few seconds).
    python ml_review_to_json.py ../results/miracl/review_all_judged.txt
Judgment line format:  Verdict: <ok|bad|unsure>  <reason (optional)>  [<- recheck]
  - only the first word ok / bad / unsure is read (case-insensitive); the reason is free text
  - the "<- recheck" marker may be kept or removed; it does not affect the result
Output: results/miracl/review_judgments.json (backed up to .bak before overwriting); prints which questions changed relative to the old file
"""
import json, os, re, shutil, sys, collections

from ml_common import ROOT


def parse(path):
    out, lang, cur, bad_lines = {}, None, None, []
    for no, ln in enumerate(open(path, encoding="utf-8"), 1):
        ln = ln.rstrip("\n")
        m = re.match(r"^# (\w+) manual review", ln)
        if m:
            lang = m.group(1)
            out.setdefault(lang, {})
            continue
        m = re.match(r"^\[(\d+)/\d+\] qid=(\S+)", ln)
        if m:
            cur = (int(m.group(1)), m.group(2))
            continue
        if ln.startswith("Verdict:") and cur and lang:
            body = ln[len("Verdict:"):].replace("<- recheck", "").strip()
            m = re.match(r"^(ok|bad|unsure)\b\s*(.*)$", body, re.I)
            if not m:
                bad_lines.append((no, ln))
                continue
            out[lang][cur[1]] = {"idx": cur[0], "label": m.group(1).lower(), "reason": m.group(2).strip(),
                                 "recheck": "<- recheck" in ln}
            cur = None
    return out, bad_lines


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "results", "miracl", "review_all_judged.txt")
    J, bad_lines = parse(src)
    if bad_lines:
        print("Warning: these judgment lines lack ok / bad / unsure; fill them in and re-run:")
        for no, ln in bad_lines:
            print(f"   line {no}: {ln}")
        sys.exit(1)
    dst = os.path.join(ROOT, "results", "miracl", "review_judgments.json")
    old = json.load(open(dst)) if os.path.exists(dst) else {}
    if os.path.exists(dst):
        shutil.copy(dst, dst + ".bak")
    json.dump(J, open(dst, "w"), ensure_ascii=False, indent=1)
    for lang, d in J.items():
        c = collections.Counter(v["label"] for v in d.values())
        print(f"[{lang}] {len(d)} questions: ok {c['ok']}  bad {c['bad']}  unsure {c['unsure']}")
        for q, v in d.items():
            o = old.get(lang, {}).get(q, {}).get("label")
            if o and o != v["label"]:
                print(f"     question {v['idx']} {q}: {o} -> {v['label']}  {v['reason']}")
    print(f"written to {dst} (old file backed up as .bak)")


if __name__ == "__main__":
    main()
