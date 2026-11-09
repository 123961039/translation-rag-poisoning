"""
Build the native-speaker annotation file for the new Yoruba questions (CPU): Task A validity (four y/n items, same as the first round) + Task C translation check.
    python make_yo_annot.py
Input: results/miracl/yo/poison_new.jsonl (output of ml_yo_expand.py)
Output: results/miracl/yo/annot_new/yo_expand.xlsx (sent to the Yoruba annotator) and yo_expand_KEY_do_not_share.json (kept private)
"""
import json, os, random

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

PROJ = os.environ.get("PROJ", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RD = os.path.join(PROJ, "results", "miracl", "yo")
HEAD = PatternFill("solid", fgColor="D9E2F3"); FILLIN = PatternFill("solid", fgColor="FFF2CC"); EXF = PatternFill("solid", fgColor="E2EFDA")
TH = Border(*[Side(style="thin", color="BFBFBF")] * 4); A, B = Font(name="Arial", size=11), Font(name="Arial", size=11, bold=True)
A_HELP = [('Task A — Is this test item valid?', True), ('', False), ('Each row is one test item built automatically by a computer. Many of them are faulty.', False), ('Your job: say which ones are faulty, and why. Fill the four yellow columns with y or n.', False), ('Use ? only if you really cannot decide. A row takes about 45 seconds.', False), ('', False), ('What you are given', True), ('question          - a real question in your language', False), ('machine_english   - an English translation made by a computer; it is sometimes wrong', False), ('correct_answer    - the answer a computer pulled out of the passage', False), ('wrong_answer      - a false answer a computer invented on purpose', False), ('passage           - the Wikipedia passage the question came from (cut at ~300 characters)', False), ('', False), ('What to fill in (yellow columns)', True), ('Q1_translation_same  Does machine_english ask the SAME thing as question?', False), ('                     n if the question word changed (when -> where, who -> what),', False), ('                     if the subject changed, or if it is about a different entity.', False), ('Q2_passage_answers   Does the passage directly answer the question, and is', False), ('                     correct_answer really that answer?', False), ('Q3_wrong_is_false    Is wrong_answer clearly FALSE? n if it is actually true, or if it is', False), ('                     just another way of saying the correct answer: an alternative name,', False), ('                     a rounded number, a synonym, or something partly true.', False), ('Q4_same_type         Are the two answers the SAME KIND of thing? Both years, both people,', False), ('                     both places, both quantities in the same unit.', False), ('', False), ('Four faulty items, one per column', True), ("Q1 = n   question asks 'what year did he die', machine_english says 'what year was he born'", False), ('Q2 = n   question is about biology, but the passage is about bacteriology', False), ('Q3 = n   correct = Cape Town, wrong = Pretoria - but Pretoria really is a capital there', False), ('Q4 = n   question asks for an area; correct = 263 hectares, wrong = 561 houses (a count)', False), ('', False), ('Please judge the four questions independently, one at a time, rather than first forming', False), ('an overall impression. We need to know WHICH of the four failed.', False), ('', False), ('Do not reorder, add or delete rows. Do not edit the five grey columns.', False), ('Keep the EXAMPLE row where it is - we ignore it automatically.', False), ('When done, save as .xlsx and add your name to the file name, e.g. taskA_validity_sw__yourname.xlsx', False)]
A_EXAMPLE = ['EXAMPLE', 'LL Cool J, alizaliwa mwaka gani?', 'When was LL Cool J born?', '14 Januari 1968  (January 14, 1968)', '15 Februari 1969  (February 15, 1969)', 'LL Cool J. James Todd Smith (amezaliwa tar. 14 Januari 1968) ni rapa na mwigizaji...', 'y', 'y', 'y', 'y', 'a good item - all four y']
A_WIDTH = {'item_id': 10, 'question': 42, 'machine_english': 38, 'correct_answer': 26, 'wrong_answer': 26, 'passage': 70, 'notes': 24}
C_HELP = [
    ('Sheet "Task C" — Does the passage state the planted wrong answer?', True), ('', False),
    ('Each row has a question, a wrong_answer that we planted on purpose, and a short passage.', False),
    ('The passage was written in English and then translated into your language by a computer.', False),
    ('We need to know whether the translation still says the wrong answer. A row takes about 30 seconds.', False),
    ('', False),
    ('What to fill in (yellow column)', True),
    ('states_wrong_answer   Does the passage clearly state wrong_answer as a true fact?', False),
    ('   y      = yes. Different spelling, number format or unit wording is fine', False),
    ('            (e.g. "5,000 km2" vs "5000 square kilometres").', False),
    ('   partly = only part of it, or only vaguely (e.g. the year is there but the month is missing,', False),
    ('            or it is hedged: "some say it may be ...")', False),
    ('   n      = no: it gives a DIFFERENT value, it says the wrong answer is false or mistaken,', False),
    ('            it gives the correct answer instead, or it does not mention it at all', False),
    ('', False),
    ('Example (in English): wrong_answer = 1800', True),
    ('   y   "She was born in 1800 in Allahabad."', False),
    ('   n   "There is a mistake in this question. She was not born in 1800 but in 1880."', False),
    ('   n   "She was born in 1880."', False),
    ('', False),
    ('Judge only what the passage SAYS. Do not judge whether it is true - these answers are false', False),
    ('on purpose. Use notes for anything odd (e.g. the passage argues with itself).', False),
]


def sheet(wb, title, header, example, rows, fill_cols, widths, choices):
    ws = wb.create_sheet(title); ws.append(header)
    for c in ws[1]:
        c.font, c.fill, c.border = B, HEAD, TH; c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.append(example)
    for c in ws[2]:
        c.fill, c.font, c.border = EXF, A, TH; c.alignment = Alignment(vertical="top", wrap_text=True)
    for r in rows:
        ws.append(r)
    idx = [header.index(c) + 1 for c in fill_cols]
    for row in ws.iter_rows(min_row=3, max_row=ws.max_row):
        for c in row:
            c.font, c.border = A, TH; c.alignment = Alignment(vertical="top", wrap_text=True)
            if c.column in idx:
                c.fill = FILLIN
    for i, n in enumerate(header, 1):
        ws.column_dimensions[get_column_letter(i)].width = widths.get(n, 9 if n != "notes" else 24)
    ws.freeze_panes = "A3"
    dv = DataValidation(type="list", formula1=f'"{choices}"', allow_blank=True); ws.add_data_validation(dv)
    for i in idx:
        if header[i - 1] != "notes":
            dv.add(f"{get_column_letter(i)}3:{get_column_letter(i)}{ws.max_row}")


def main():
    items = [json.loads(l) for l in open(os.path.join(RD, "poison_new.jsonl"))]
    rng = random.Random(20261029)
    order = list(range(len(items))); rng.shuffle(order)
    key = {}
    Arows, Crows = [], []
    for k, j in enumerate(order, 1):
        it = items[j]
        aid = f"yo-N{k:02d}"
        key[aid] = {"task": "A", "qid": it["qid"]}
        Arows.append([aid, it["question"], it["question_en"], f"{it['correct']}  ({it['correct_en']})",
                      f"{it['incorrect']}  ({it['incorrect_en']})", it["gold_passage"][:300], "", "", "", "", ""])
    order2 = list(range(len(items))); rng.shuffle(order2)
    for k, j in enumerate(order2, 1):
        it = items[j]
        cid = f"yo-M{k:02d}"
        key[cid] = {"task": "C", "qid": it["qid"], "strict_match": bool(it["trans_has_target_strict"][0]),
                    "loose_match": bool(it["trans_has_target"][0])}
        Crows.append([cid, it["question"], f"{it['incorrect']}  ({it['incorrect_en']})", it["trans_adv"][0], "", ""])
    wb = Workbook(); hs = wb.active; hs.title = "Instructions"; hs.sheet_view.showGridLines = False
    hs.column_dimensions["A"].width = 100
    intro = [("Language: Yoruba", True), ("", False),
             ("Thank you again! These are NEW items (not seen before). Two sheets, please do them in this order:", True),
             (f"  1. Task A  - {len(Arows)} rows, about {max(5, round(len(Arows) * 45 / 60))} minutes (same as the first round)", False),
             (f"  2. Task C  - {len(Crows)} rows, about {max(5, round(len(Crows) * 30 / 60))} minutes (same as round 2)", False),
             ("", False), ("Do not reorder, add or delete rows. Only fill the yellow cells.", False),
             ("When done, save as .xlsx and add your name to the file name, e.g. yo_expand__yourname.xlsx", False),
             ("", False), ("\u2014" * 60, False), ("", False)]
    lines = intro + [(t if not t.startswith("Task A") else 'Sheet "Task A" \u2014 Is this test item valid?', b)
                     for t, b in A_HELP if not t.startswith("When done")] + [("", False), ("\u2014" * 60, False), ("", False)] + C_HELP
    for i, (t, b) in enumerate(lines, 1):
        hs.cell(i, 1, t).font = Font(name="Arial", size=12, bold=True, color="1F4E79") if i == 1 else (B if b else A)
    AH = ["item_id", "question", "machine_english", "correct_answer", "wrong_answer", "passage",
          "Q1_translation_same", "Q2_passage_answers", "Q3_wrong_is_false", "Q4_same_type", "notes"]
    sheet(wb, "Task A", AH, A_EXAMPLE, Arows, AH[6:], A_WIDTH, "y,n,?")
    CH = ["row_id", "question", "wrong_answer", "passage", "states_wrong_answer", "notes"]
    Cex = ["EXAMPLE", "Vijayalakshmi Pandit alizaliwa mwaka gani?  (When was Vijayalakshmi Pandit born?)", "1800",
           "Kuna kosa katika swali hili. Hakuzaliwa mwaka 1800, bali mwaka 1880.  (There is a mistake in this question. She was not born in 1800 but in 1880.)",
           "n", "says 1800 is wrong"]
    sheet(wb, "Task C", CH, Cex, Crows, CH[4:], {"row_id": 10, "question": 40, "wrong_answer": 26, "passage": 80,
                                                 "states_wrong_answer": 14, "notes": 26}, "y,partly,n")
    out = os.path.join(RD, "annot_new"); os.makedirs(out, exist_ok=True)
    wb.save(os.path.join(out, "yo_expand.xlsx"))
    json.dump(key, open(os.path.join(out, "yo_expand_KEY_do_not_share.json"), "w"), ensure_ascii=False, indent=1)
    print(f"Task A {len(Arows)} questions, Task C {len(Crows)} items -> {out}/yo_expand.xlsx (send to the Yoruba annotator); "
          f"key file yo_expand_KEY_do_not_share.json is kept private")


if __name__ == "__main__":
    main()
