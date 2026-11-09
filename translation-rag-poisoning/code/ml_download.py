"""
Download the MIRACL corpus, queries, qrels and the bge-m3 model (via the HF_ENDPOINT mirror if set).
    python ml_download.py                       # default sw te yo id + bge-m3
    python ml_download.py --langs sw --no_model # Swahili data only
    python ml_download.py --no_fetch            # files already fetched with ml_fetch.sh; only convert formats
The corpus docs-*.jsonl.gz is converted to corpus.parquet (docid, title, text, original order) and the gz files are deleted to save space.
"""
import argparse, glob, gzip, json, os, shutil, time

import pyarrow as pa
import pyarrow.parquet as pq

from ml_common import LANGS, M3_PATH, corpus_parquet, ml_data, query_splits


def to_parquet(gz_files, out_path, batch=20_000):   # small batches, fits in 2 GB RAM
    schema = pa.schema([("docid", pa.string()), ("title", pa.string()), ("text", pa.string())])
    w = pq.ParquetWriter(out_path + ".tmp", schema, compression="zstd")
    n, buf = 0, {"docid": [], "title": [], "text": []}

    def flush():
        w.write_table(pa.table(buf, schema=schema))
        for v in buf.values():
            v.clear()

    for gz in gz_files:                      # docs-0, docs-1, ... sorted by number for a stable order
        with gzip.open(gz, "rt", encoding="utf-8") as f:
            for line in f:
                d = json.loads(line)
                buf["docid"].append(str(d["docid"]))
                buf["title"].append(d.get("title") or "")
                buf["text"].append(d.get("text") or "")
                n += 1
                if len(buf["docid"]) >= batch:
                    flush()
    if buf["docid"]:
        flush()
    w.close()
    os.replace(out_path + ".tmp", out_path)
    return n


def gz_key(p):
    b = os.path.basename(p)                  # docs-12.jsonl.gz → 12
    try:
        return int(b.split("-")[1].split(".")[0])
    except Exception:
        return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--langs", nargs="+", default=LANGS)
    ap.add_argument("--no_model", action="store_true")
    ap.add_argument("--keep_gz", action="store_true", help="keep the original jsonl.gz after conversion")
    ap.add_argument("--no_fetch", action="store_true", help="offline: only convert already downloaded files (with ml_fetch.sh)")
    args = ap.parse_args()
    if args.no_fetch:
        args.no_model = True
        snapshot_download = lambda *a, **k: None
    else:
        from huggingface_hub import snapshot_download

    for lang in args.langs:
        print(f"\n========== {lang} ==========", flush=True)
        d = ml_data(lang)
        os.makedirs(d, exist_ok=True)
        t0 = time.time()
        snapshot_download("miracl/miracl", repo_type="dataset", local_dir=os.path.join(d, "raw"),
                          allow_patterns=[f"miracl-v1.0-{lang}/*"])
        print("  query splits:", query_splits(lang))
        assert query_splits(lang), f"no query files for {lang}; check {os.path.join(d, 'raw')}"
        cp = corpus_parquet(lang)
        if os.path.exists(cp):
            print(f"  {cp} exists, skipping the corpus")
        else:
            cdir = os.path.join(d, "raw_corpus")
            snapshot_download("miracl/miracl-corpus", repo_type="dataset", local_dir=cdir,
                              allow_patterns=[f"miracl-corpus-v1.0-{lang}/*"])
            gz = sorted(glob.glob(os.path.join(cdir, f"miracl-corpus-v1.0-{lang}", "docs-*.jsonl.gz")), key=gz_key)
            assert gz, f"no docs-*.jsonl.gz for {lang}"
            n = to_parquet(gz, cp)
            print(f"  corpus {n:,} passages -> {cp} ({os.path.getsize(cp) / 2**20:.0f} MB)")
            if not args.keep_gz:
                shutil.rmtree(cdir)
        print(f"  time {time.time() - t0:.0f} s")

    if not args.no_model:
        print("\n========== bge-m3 ==========", flush=True)
        # skip onnx (about 2 GB) and images; only the pytorch_model.bin weights
        snapshot_download("BAAI/bge-m3", local_dir=M3_PATH,
                          ignore_patterns=["onnx/*", "*.onnx", "imgs/*", "*.onnx_data"])
        print("  →", M3_PATH)
    os.system(f"df -h {ROOT}")


if __name__ == "__main__":
    main()
