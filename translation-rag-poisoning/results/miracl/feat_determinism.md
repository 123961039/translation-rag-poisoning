# Feature reproducibility diagnostic (trans_bb, full corpus)

## id (62 poisons, original file 62)

- Two consecutive runs on this machine: max embedding difference 0.0e+00; max rel_knn10 difference 0.0e+00
- This run vs original file (10-28, a different GPU): max difference 2.6e-02, items with difference > 1e-3: 2
- This run vs scale_seeds seed 0: max difference 0.0e+00

| poison | diff | similarity gap 10th/11th neighbour | similarity gap 50th/51st neighbour | identical neighbour vector pairs in top-10 |
|---|---|---|---|---|
| 4170 | 1.6e-03 | 0.0e+00 | 4.9e-04 | 0 |
| 1038 | 2.6e-02 | 4.9e-04 | 4.9e-04 | 0 |

- AUROC (all poisons, vs length-matched): original features 0.7915, this run 0.7910

## yo (80 poisons, original file 80)

- Two consecutive runs on this machine: max embedding difference 0.0e+00; max rel_knn10 difference 0.0e+00
- This run vs original file (10-28, a different GPU): max difference 0.0e+00, items with difference > 1e-3: 0
- This run vs scale_seeds seed 0: max difference 0.0e+00

- AUROC (all poisons, vs length-matched): original features 0.8022, this run 0.8022

Reading: if two runs on the same machine are bit-identical, differences appear only across GPUs, and the differing poisons have ties / near-duplicates at the neighbour boundary,
then the differences can be attributed to fp16 matmul rounding on different GPUs changing the neighbour set; the change in AUROC should be far smaller than the effects reported in the paper.
