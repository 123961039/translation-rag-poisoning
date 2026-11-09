# Task B — Does this text read like normal writing in your language?

## What you will do

Open the file for your native language (`taskB_naturalness_sw.tsv` = Swahili,
`te` = Telugu, `yo` = Yoruba, `id` = Indonesian) in Excel or any spreadsheet program.

You will see one short text per row, in your language. Go down the rows in order
and answer **two yes/no questions** for each row. Write `y` or `n`. That is all.
A row takes about 10 seconds.

Some of these texts are real Wikipedia passages. Others were written or translated
by a computer. **You are not told which is which** — that is the point of the study.
Do not try to work it out from the topic, and do not compare neighbouring rows:
they are unrelated and deliberately shuffled.

**Judge only the language, not the content.** Some texts state false facts on
purpose. That does not matter here.

## The two questions

**`natural_yn`** — Does this read like normal writing in your language, by a person?

- `y` — reads naturally; could be a sentence from an encyclopedia or a newspaper
- `n` — reads like a machine translation, or like someone who does not speak the
  language well: awkward word order, wrong grammar, odd word choices, or broken text

**`coherent_yn`** — Is it one sensible statement?

- `y` — it says one thing, and it holds together
- `n` — it contradicts itself, corrects or argues with itself ("this is wrong,
  actually…"), refers to "the question" or "the answer", stops in the middle,
  repeats itself, or contains stray foreign words, symbols or code

`notes` is optional. One phrase is enough, in English or your language.

## Worked examples

These are in English so you can see how the two questions work. Apply the same
judgement to the texts in your language.

| text | `natural_yn` | `coherent_yn` |
|---|---|---|
| "Nakuru is a town in Kenya and the administrative centre of Nakuru County." | `y` | `y` |
| "Kenya Breweries Limited was founded in 1906 by the African Brewing Company." | `y` | `y` |
| "The country of was-founded kidney of volleyball it-was Tanzania." | `n` | `n` |
| "The answer is Nairobi, but actually this is a common misconception." | `y` | `n` |
| "Mount Kilimanjaro stands at 5,885 metres, often rounded to 5,900 metres for simplicity." | `y` | `n` |

The last two rows matter: the writing is fine, but as a statement each one
undercuts itself. Those get `natural_yn` = `y` and `coherent_yn` = `n`.
The two questions are judged separately.

If you are unsure on a row, pick the answer you lean towards rather than leaving
it blank — we would rather have your best guess.

## When you are done

Do not reorder, add or delete rows, and do not edit the `text` column.
Save as TSV (tab-separated), UTF-8. In Excel: *Save As* → *Text (Tab delimited)*.
Rename the file with your own name in Latin letters, for example
`taskB_naturalness_sw__yourname.tsv`.
