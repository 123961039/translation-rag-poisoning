"""
Review item P1-7 (side check): BGE-M3 uses max_seq_length=512; check the truncation rate (CPU only, tokenizer only, a few minutes).
Fraction of poison texts (three variants x bb/adv, first per question) and 5000 random corpus passages longer than 512 tokens (including special tokens).
    python trunc_check.py
Output: results/miracl/trunc_check.md
"""
import os

import numpy as np
import pyarrow.parquet as pq
from transformers import AutoTokenizer

from ml_common import LANGS, M3_PATH, ROOT, corpus_parquet, doc_format
from ml_attack import load_items, texts_of


def main():
    tok = AutoTokenizer.from_pretrained(M3_PATH)
    n_tok = lambda xs: np.array([len(tok(x, add_special_tokens=True).input_ids) for x in xs])
    L = ["# BGE-M3 truncation rate (max_seq_length = 512)", "",
         "| lang | text | n | median tokens | 95th percentile | fraction > 512 |", "|---|---|---|---|---|---|"]
    rng = np.random.default_rng(0)
    for lg in LANGS:
        items, _ = load_items(lg)
        for v in ("native", "trans", "en"):
            for f in ("bb", "adv"):
                xs = [texts_of(it, v, f)[0] for it in items if it.get(f"{v}_adv")]
                if xs:
                    t = n_tok(xs)
                    L.append(f"| {lg} | poison {v}/{f} | {len(t)} | {int(np.median(t))} | {int(np.percentile(t, 95))} | {np.mean(t > 512):.1%} |")
        tb = pq.read_table(corpus_parquet(lg), columns=["title", "text"])
        pick = rng.choice(tb.num_rows, min(5000, tb.num_rows), replace=False)
        ti, tx = tb.column(0), tb.column(1)
        xs = [doc_format((ti[int(i)].as_py() or "").strip(), (tx[int(i)].as_py() or "").strip()) for i in pick]
        t = n_tok(xs)
        L.append(f"| {lg} | corpus passages (random) | {len(t)} | {int(np.median(t))} | {int(np.percentile(t, 95))} | {np.mean(t > 512):.1%} |")
        print(f"[{lg}] done", flush=True)
    L += ["", "Truncation affects only texts longer than 512 tokens; when the fraction is near 0, truncation does not affect the comparison of detectors."]
    out = os.path.join(ROOT, "results", "miracl", "trunc_check.md")
    open(out, "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
