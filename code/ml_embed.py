"""
Encode the MIRACL corpora and queries with bge-m3 (dense, fp16), resumable. Run on a GPU instance:
    python ml_embed.py                        # all of sw te yo id
    python ml_embed.py --langs sw --limit 20000   # small speed test, written to a _test folder
Documents use doc_format ("title. text"); bge-m3 queries have no instruction prefix.
At the start, the share of passages truncated above max_len is estimated on a sample (low-resource languages are tokenized more finely).
"""
import argparse, json, os, time

import numpy as np
import pyarrow.parquet as pq
import torch
from sentence_transformers import SentenceTransformer

from ml_common import LANGS, M3_PATH, corpus_parquet, doc_format, load_topics, ml_emb, query_splits


def doc_texts(batch):
    d = batch.to_pydict()
    return [doc_format((t or "").strip(), (x or "").strip()) for t, x in zip(d["title"], d["text"])]


def encode_lang(model, lang, args):
    out = ml_emb(lang) + (f"_test{args.limit}" if args.limit else "")
    os.makedirs(out, exist_ok=True)
    pf = pq.ParquetFile(corpus_parquet(lang))
    N = min(pf.metadata.num_rows, args.limit) if args.limit else pf.metadata.num_rows
    dim = model.get_sentence_embedding_dimension()
    print(f"\n== {lang}: {N:,} passages, {dim} dimensions, about {N * dim * 2 / 2**30:.2f} GB ==", flush=True)

    # truncation share on a sample
    first = next(pf.iter_batches(batch_size=2000, columns=["title", "text"]))
    toks = model.tokenizer(doc_texts(first), add_special_tokens=True)["input_ids"]
    lens = np.array([len(t) for t in toks])
    print(f"  token length (first 2000 passages) median {np.median(lens):.0f}, P95 {np.percentile(lens, 95):.0f}, "
          f"truncated above {args.max_len}: {np.mean(lens > args.max_len):.1%}", flush=True)

    emb_path = os.path.join(out, "corpus_emb_fp16.npy")
    prog_path = os.path.join(out, "progress.json")
    ids_path = os.path.join(out, "corpus_ids.txt")
    done = json.load(open(prog_path))["done"] if os.path.exists(prog_path) else 0
    mode = "r+" if os.path.exists(emb_path) and done > 0 else "w+"
    emb = np.lib.format.open_memmap(emb_path, mode=mode, dtype=np.float16, shape=(N, dim))

    if not os.path.exists(ids_path):
        with open(ids_path, "w") as f:
            w = 0
            for b in pf.iter_batches(batch_size=500_000, columns=["docid"]):
                ids = b.column(0).to_pylist()[: N - w]
                f.write("\n".join(ids) + "\n")
                w += len(ids)
                if w >= N:
                    break

    if done >= N:
        print("  corpus already encoded, skipping")
    else:
        print(f"  resuming from passage {done:,}", flush=True)
        pos, t0, done0 = 0, time.time(), done
        for batch in pf.iter_batches(batch_size=args.chunk, columns=["title", "text"]):
            if pos >= N:
                break
            if pos + batch.num_rows > N:
                batch = batch.slice(0, N - pos)
            n = batch.num_rows
            if pos + n <= done:
                pos += n
                continue
            texts = doc_texts(batch)
            start = max(done - pos, 0)
            vec = model.encode(texts[start:], batch_size=args.batch, normalize_embeddings=True,
                               convert_to_numpy=True, show_progress_bar=False)
            emb[pos + start: pos + n] = vec.astype(np.float16)
            emb.flush()
            pos += n
            done = pos
            json.dump({"done": done, "total": N}, open(prog_path, "w"))
            rate = (done - done0) / (time.time() - t0 + 1e-9)
            print(f"  {done:,}/{N:,} ({done / N:.1%})  {rate:.0f} passages/s  about {(N - done) / max(rate, 1e-9) / 60:.0f} min left  "
                  f"GPU peak {torch.cuda.max_memory_allocated() / 2**30:.1f} GB", flush=True)
        if args.limit:
            full = pq.ParquetFile(corpus_parquet(lang)).metadata.num_rows
            print(f"  >> at this speed, the full {full:,} passages take about {full / max(rate, 1e-9) / 60:.0f} min")
    del emb

    # queries: all splits with files are merged (dev for evaluation, train as possible attack targets)
    qids, qtexts = [], []
    for s in query_splits(lang):
        for q, t in load_topics(lang, s).items():
            qids.append(q)
            qtexts.append(t)
    assert len(set(qids)) == len(qids), "duplicate query ids across splits"
    qv = model.encode(qtexts, batch_size=args.batch, normalize_embeddings=True, convert_to_numpy=True,
                      show_progress_bar=False)
    np.save(os.path.join(out, "query_emb_fp16.npy"), qv.astype(np.float16))
    open(os.path.join(out, "query_ids.txt"), "w").write("\n".join(qids) + "\n")
    print(f"  {len(qids):,} queries ({', '.join(query_splits(lang))}) encoded -> {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--langs", nargs="+", default=LANGS)
    ap.add_argument("--batch", type=int, default=256)
    ap.add_argument("--chunk", type=int, default=50_000)
    ap.add_argument("--max_len", type=int, default=512)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--device", default="cuda")
    args = ap.parse_args()
    model = SentenceTransformer(M3_PATH, device=args.device)
    if args.device == "cuda":
        model.half()
    model.max_seq_length = args.max_len
    for lang in args.langs:
        encode_lang(model, lang, args)
    os.system(f"df -h {ROOT}")


if __name__ == "__main__":
    main()
