"""
Export a manual review sheet (CPU only, a few seconds).
    python ml_make_review.py --lang yo              # all 28 Yoruba questions
    python ml_make_review.py --lang sw te id --n 20 # 20 questions for each other language
One block per question: original question, Qwen's English translation, correct answer, target answer, gold passage, and one poison text per variant.
Fill in ok or bad after "Verdict:" for each question (wrong translation / answer does not fit the question) and save the file under the same name;
ml_review_to_json.py converts the sheet into a judgment file that the analyses use to exclude bad questions (--exclude).
Output: results/miracl/<lang>/review.txt
"""
import argparse, json, os

from ml_common import LANGS, ml_results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", nargs="+", default=LANGS)
    ap.add_argument("--n", type=int, default=0, help="export the first n questions per language, 0 = all")
    args = ap.parse_args()
    for lang in args.lang:
        rd = ml_results(lang)
        p = os.path.join(rd, "poison.jsonl")
        if not os.path.exists(p):
            print(f"[{lang}] {p} missing, skipped")
            continue
        items = [json.loads(l) for l in open(p)]
        if args.n:
            items = items[: args.n]
        out = os.path.join(rd, "review.txt")
        with open(out, "w") as f:
            f.write(f"# {lang} manual review: {len(items)} questions\n"
                    "# Fill in ok or bad after 'Verdict:' (bad = the English translation does not match the question, or the answer does not answer this question)\n"
                    "# A short reason after bad helps the write-up\n\n")
            for i, it in enumerate(items, 1):
                f.write(f"{'=' * 70}\n[{i}/{len(items)}] qid={it['qid']}\nVerdict: \n"
                        f"  question      : {it['question']}\n"
                        f"  English       : {it['question_en']}\n"
                        f"  correct answer: {it['correct']}   ({it.get('correct_en', '')})\n"
                        f"  target answer : {it['incorrect']}   ({it.get('incorrect_en', '')})\n"
                        f"  gold passage  : {it.get('gold_passage', '')[:300]}\n")
                for v in ("native", "trans", "en"):
                    adv = it.get(f"{v}_adv") or []
                    f.write(f"  {v:6s}: {adv[0] if adv else '(not filled)'}\n")
        print(f"[{lang}] {len(items)} questions -> {out}")


if __name__ == "__main__":
    main()
