# Native-speaker annotation

One native speaker per language (Swahili, Telugu, Yoruba, Indonesian) annotated four tasks. Annotators were informed that the passages contain false statements created for research. Annotator identities, the free-text notes they added, and the passage texts shown to them are not included; texts can be recovered from the released result files through `qid`.

| task | question | released records | protocol |
|---|---|---|---|
| A | is the attacked question valid? (four y/n criteria) | `data/taskA_round1.csv` (278 items), `data/taskA_yo_expansion.csv` (52 new Yoruba questions) | `protocols/INSTRUCTIONS_taskA.md`, `protocols/INSTRUCTIONS_yo_expansion.md` |
| B | does a passage read as human-written? (blind; real / MT poison / LLM-written native poison mixed and shuffled) | `data/taskB_round1.csv` (720 rows, with the source of each row) | `protocols/INSTRUCTIONS_taskB.md` |
| retest | Tasks A and B repeated on a subset about one week later | `data/taskA_retest.csv`, `data/taskB_retest.csv` (linked to round 1 by `round1_item_id` / `round1_row_id`) | `protocols/INSTRUCTIONS_round2_retest_taskC.md` |
| C | does the translated poison still state the target answer? | `data/taskC_translation_check.csv` (with the automatic strict / loose string match) | same as retest |
| D | does the reader's answer state the target / the correct answer? (stratified sample) | `data/taskD_asr_check.csv` (with the automatic judgment and sampling stratum) | `protocols/INSTRUCTIONS_taskD.md` |

Labels: `y`, `n`, `?` (annotator could not decide), `partly` (Tasks C and D). The `source` column of Task B was hidden from the annotator; it is released now that the study is complete.

`first_pass_label` in `taskA_round1.csv` is the earlier non-native, LLM-assisted first-pass review (`results/miracl/review_judgments.json`, with its reasons), which the native-speaker judgments replace; it is kept to report their agreement and the robustness analyses under the old filter.

## Recompute

```bash
python annotation/analyze_annotation.py
```

This recomputes every annotation number reported in the paper (validity counts, naturalness shares, test-retest kappa, Task C preservation, Task D kappa and agreement), writes `results/recomputed.md`, checks them against the paper (36 checks), and checks that the question filter used by all experiments (`results/miracl/review_judgments_native.json`) follows from the Task A labels: round 1 ok = all four y, bad = any n, unsure otherwise; Yoruba expansion ok = all four y, bad otherwise (`code/merge_yo_new.py`).

`results/retest.md`, `results/taskd.md` and `results/transcheck_yo26.md` are the original analysis reports (more detailed breakdowns of the same data).
