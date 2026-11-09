# Task A — Is this test item valid?

## What you will do

Open the file for your native language (`taskA_validity_sw.tsv` = Swahili,
`te` = Telugu, `yo` = Yoruba, `id` = Indonesian) in Excel or any spreadsheet program.

Each row is one test item built automatically by a computer, and many of them are
faulty. Your job is to say **which ones are faulty and why**. Go down the rows and
fill in **four yes/no columns**. A row takes about 45 seconds.

Each row shows you five things:

| column | what it is |
|---|---|
| `question` | a real question in your language, from Wikipedia-based search data |
| `machine_english` | an English translation of that question, **made by a computer** — it is sometimes wrong |
| `correct_answer` | the answer a computer pulled out of the passage |
| `wrong_answer` | a false answer a computer invented on purpose |
| `passage` | the Wikipedia passage the question came from (cut off at about 300 characters) |

## The four columns

Write `y` or `n`. If you truly cannot decide, write `?`. Use `notes` freely —
short notes are very useful to us.

**`Q1_translation_same`** — Does `machine_english` ask the same thing as `question`?
Write `n` if the question word changed (*when* → *where*, *who* → *what*), if the
subject changed, or if it is about a different entity. Minor wording differences are fine → `y`.

**`Q2_passage_answers`** — Does `passage` directly answer `question`, and is
`correct_answer` really that answer? Write `n` if the passage is about something else,
or if `correct_answer` answers a different question than the one asked.

**`Q3_wrong_is_false`** — Is `wrong_answer` **clearly false**? Write `n` if it is in
fact true, or if it is just another way of saying the correct answer: an alternative
name or spelling, a rounded number, a synonym, or something partly true.

**`Q4_same_type`** — Are `correct_answer` and `wrong_answer` the **same kind of thing**?
Both years, both people, both places, both quantities in the same unit. Write `n` if
one is a year and the other a person, or one is an area and the other a number of houses.

## Worked examples

These are in English, to show you the four failure modes. The real rows are in your language.

**A good item — all four `y`:**

- question: *"What year was LL Cool J born?"* · machine_english: *"When was LL Cool J born?"*
- correct: *14 January 1968* · wrong: *15 February 1969*
- passage: *"James Todd Smith (born 14 January 1968) is a rapper and film actor from the United States…"*

`Q1` `y` (same question) · `Q2` `y` (passage states the birth date) ·
`Q3` `y` (1969 is false) · `Q4` `y` (both are dates)

**Four faulty items, one per column:**

| what is wrong | fill in |
|---|---|
| question asks *"what year did he die"*, machine_english says *"what year was he born"* | `Q1` = `n` |
| question asks about biology, but the passage is about bacteriology and does not answer it | `Q2` = `n` |
| correct = *Cape Town*, wrong = *Pretoria* — but Pretoria really is a capital of that country, so the "wrong" answer is true | `Q3` = `n` |
| question asks for an **area**; correct = *263 hectares*, wrong = *561 houses* — a count, not an area | `Q4` = `n` |

Please judge the four questions independently, one at a time, rather than first
forming an overall impression of the item. An item counts as usable to us only if
all four are `y`, and we need to know **which** of the four failed.

## When you are done

Do not reorder, add or delete rows, and do not edit the five columns you were given.
Save as TSV (tab-separated), UTF-8. In Excel: *Save As* → *Text (Tab delimited)*.
Rename the file with your own name in Latin letters, for example
`taskA_validity_sw__amina.tsv`.
