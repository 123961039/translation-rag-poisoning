"""Table 6 GPU benchmark for distinct held-out passages."""
import argparse
import time
from pathlib import Path
from statistics import median

import numpy as np
import pyarrow.parquet as pq
import torch
from sentence_transformers import SentenceTransformer

from ml_common import LANGS, M3_PATH, ROOT, doc_format
from ml_efficiency import Resident


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lang", choices=LANGS)
    parser.add_argument("--model", default=M3_PATH)
    args = parser.parse_args()
    lang = args.lang
    root = Path(ROOT)
    rng = np.random.default_rng(20261119)
    torch.set_grad_enabled(False)

    emb = np.load(root / f"emb/miracl/{lang}/bge-m3/corpus_emb_fp16.npy",
                  mmap_mode="r", allow_pickle=False)
    table = pq.read_table(root / f"data/miracl/{lang}/corpus.parquet",
                          columns=["title", "text"])
    assert len(table) == len(emb), (lang, len(table), len(emb))
    print("GPU:", torch.cuda.get_device_name(), "torch:", torch.__version__)
    print("Corpus:", lang, emb.shape, emb.dtype)

    ids, texts, seen = [], [], set()
    for idx in rng.choice(len(emb), size=5000, replace=False):
        i = int(idx)
        title = (table["title"][i].as_py() or "").strip()
        body = (table["text"][i].as_py() or "").strip()
        if not body:
            continue
        text = doc_format(title, body)
        if text in seen:
            continue
        seen.add(text)
        ids.append(i)
        texts.append(text)
        if len(ids) == 1000:
            break
    assert len(ids) == 1000, (lang, len(ids))
    del table

    keep = np.ones(len(emb), dtype=bool)
    keep[ids] = False
    index = Resident(emb[keep])
    model = SentenceTransformer(args.model,
                                device="cuda").half().eval()
    model.max_seq_length = 512
    print("Reference rows:", int(keep.sum()), "held-out unique texts:", len(texts))

    def encode(batch):
        return model.encode(batch, batch_size=min(128, len(batch)),
                            normalize_embeddings=True, convert_to_tensor=True,
                            show_progress_bar=False).to(device="cuda", dtype=torch.float16)

    def elapsed(batches, screen):
        torch.cuda.synchronize()
        start = time.perf_counter()
        for batch in batches:
            q = encode(batch)
            if screen:
                index.rel_knn10(q)
        torch.cuda.synchronize()
        return time.perf_counter() - start

    for batch_size, n in ((1, 64), (128, 896), (1000, 1000)):
        batches = [texts[i:i + batch_size] for i in range(0, n, batch_size)]
        unique_counts = []
        for batch in batches:
            q = encode(batch)
            _, neighbors = index.topk(q, 10)
            unique_counts.append(torch.unique(neighbors).numel())
            index.rel_knn10(q)
        torch.cuda.synchronize()

        baseline, screened, overhead = [], [], []
        for rep in range(6):
            times = {}
            for mode in ((False, True) if rep % 2 == 0 else (True, False)):
                times[mode] = elapsed(batches, mode)
            base, full = times[False], times[True]
            baseline.append(base)
            screened.append(full)
            overhead.append(100 * (full / base - 1))
            print(f"rep={rep+1} lang={lang} batch={batch_size} encode_s={base:.4f} "
                  f"encode_screen_s={full:.4f} overhead_pct={overhead[-1]:.2f}")

        print(f"RESULT lang={lang} batch={batch_size} n={n} "
              f"encode_docs_s={n/median(baseline):.1f} "
              f"screened_docs_s={n/median(screened):.1f} "
              f"paired_overhead_pct={median(overhead):.2f} "
              f"mean_U={np.mean(unique_counts):.1f} "
              f"U_fraction={np.mean(unique_counts)/(10*batch_size):.3f}")


if __name__ == "__main__":
    main()
