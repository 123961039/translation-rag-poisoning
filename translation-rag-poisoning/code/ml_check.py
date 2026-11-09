"""
Runs on a CPU-only instance: checks the MIRACL data before spending GPU time on encoding, and precomputes the length arrays used later.
    python ml_check.py                  # sw te yo id
    python ml_check.py --no_tok         # do not load the bge-m3 tokenizer (if the model is not downloaded yet)
Checks
  - corpus: number of passages, unique docids, empty passages, word-count distribution (cached as corpus_len_words.npy, aligned with corpus.parquet /
    embedding rows, used later for length matching)
  - queries and qrels: queries per split, queries with positives, positives per query, whether every qrels docid is in the corpus (must be 100%)
  - tokenization: sample 5000 passages with the bge-m3 tokenizer: token counts, share truncated above 512, tokens per word
    (low-resource languages are tokenized more finely; this number is itself a language difference worth reporting)
  - estimated size of the encoded vectors
Output: results/miracl/data_check.json
"""
import argparse, json, os, time

import numpy as np
import pyarrow.parquet as pq

from ml_common import (LANGS, M3_PATH, ROOT, corpus_parquet, doc_format, load_qrels, load_topics,
                       ml_data, query_splits)


def check_lang(lang, args, tok):
    t0 = time.time()
    cp = corpus_parquet(lang)
    assert os.path.exists(cp), f"{cp} missing; run ml_fetch.sh and ml_download.py --no_fetch first"
    pf = pq.ParquetFile(cp)
    N = pf.metadata.num_rows
    out = {"lang": lang, "passages": N}

    # corpus: docids, empty passages, word counts (read in batches, low memory)
    len_path = os.path.join(ml_data(lang), "corpus_len_words.npy")
    L = np.empty(N, dtype=np.int32)
    ids, empty, pos = set(), 0, 0
    dup = 0
    for b in pf.iter_batches(batch_size=50_000, columns=["docid", "title", "text"]):
        d = b.to_pydict()
        for i, (did, ti, tx) in enumerate(zip(d["docid"], d["title"], d["text"])):
            if did in ids:
                dup += 1
            ids.add(did)
            tx = (tx or "").strip()
            if not tx:
                empty += 1
            L[pos + i] = len(doc_format((ti or "").strip(), tx).split())
        pos += b.num_rows
    np.save(len_path, L)
    out.update({"dup_docids": dup, "empty_text": empty,
                "words_median": float(np.median(L)), "words_p95": float(np.percentile(L, 95)),
                "words_mean": float(L.mean())})

    # queries and qrels
    out["splits"] = {}
    for s in query_splits(lang):
        topics = load_topics(lang, s)
        row = {"queries": len(topics)}
        try:
            qrels = load_qrels(lang, s)
        except AssertionError:
            qrels = None
        if qrels is not None:
            pos_docs = [d for q in qrels for d in qrels[q]]
            row.update({"queries_with_pos": sum(q in topics for q in qrels),
                        "pos_per_query": float(np.mean([len(v) for v in qrels.values()])) if qrels else 0.0,
                        "qrels_docs_in_corpus": float(np.mean([d in ids for d in pos_docs])) if pos_docs else None})
        out["splits"][s] = row
    del ids

    # tokenization sample
    if tok is not None:
        rng = np.random.default_rng(0)
        pick = np.sort(rng.choice(N, size=min(args.tok_sample, N), replace=False))
        t = pq.read_table(cp, columns=["title", "text"]).take(pick).to_pydict()
        texts = [doc_format((a or "").strip(), (b or "").strip()) for a, b in zip(t["title"], t["text"])]
        n_tok = np.array([len(x) for x in tok(texts, add_special_tokens=True)["input_ids"]])
        n_w = np.maximum(L[pick], 1)
        out.update({"tokens_median": float(np.median(n_tok)), "tokens_p95": float(np.percentile(n_tok, 95)),
                    "truncated_512": float(np.mean(n_tok > 512)),
                    "tokens_per_word": float(np.median(n_tok / n_w))})

    out["emb_gb_fp16_1024d"] = N * 1024 * 2 / 2**30
    out["seconds"] = time.time() - t0
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--langs", nargs="+", default=LANGS)
    ap.add_argument("--no_tok", action="store_true")
    ap.add_argument("--tok_sample", type=int, default=5000)
    args = ap.parse_args()

    tok = None
    if not args.no_tok:
        if os.path.exists(os.path.join(M3_PATH, "tokenizer.json")) or os.path.exists(os.path.join(M3_PATH, "tokenizer_config.json")):
            from transformers import AutoTokenizer
            tok = AutoTokenizer.from_pretrained(M3_PATH)
        else:
            print(f"(no tokenizer files under {M3_PATH}; skipping tokenization statistics)")

    res = []
    for lang in args.langs:
        print(f"checking {lang} ...", flush=True)
        res.append(check_lang(lang, args, tok))

    print(f"\n{'lang':4s} {'passages':>10s} {'dup id':>6s} {'empty':>6s} {'words med/P95':>12s} {'tokens med/P95':>13s} "
          f"{'trunc>512':>8s} {'tok/word':>8s} {'vec GB':>6s}")
    for r in res:
        tk = f"{r['tokens_median']:.0f}/{r['tokens_p95']:.0f}" if "tokens_median" in r else "-"
        tr = f"{r['truncated_512']:.1%}" if "truncated_512" in r else "-"
        tw = f"{r['tokens_per_word']:.2f}" if "tokens_per_word" in r else "-"
        print(f"{r['lang']:4s} {r['passages']:>10,} {r['dup_docids']:>6d} {r['empty_text']:>6d} "
              f"{r['words_median']:>5.0f}/{r['words_p95']:<6.0f} {tk:>13s} {tr:>8s} {tw:>8s} {r['emb_gb_fp16_1024d']:6.2f}")
    print(f"\n{'lang':4s} {'split':7s} {'queries':>6s} {'w/ pos':>6s} {'pos/q':>7s} {'qrels in corpus':>12s}")
    bad = []
    for r in res:
        for s, v in r["splits"].items():
            cov = v.get("qrels_docs_in_corpus")
            print(f"{r['lang']:4s} {s:7s} {v['queries']:>6,} {v.get('queries_with_pos', '-')!s:>6s} "
                  f"{v.get('pos_per_query', float('nan')):>7.2f} {('-' if cov is None else f'{cov:.1%}'):>12s}")
            if cov is not None and cov < 1:
                bad.append(f"{r['lang']}/{s}")
        if r["dup_docids"]:
            bad.append(f"{r['lang']} has duplicate docids")
    total_gb = sum(r["emb_gb_fp16_1024d"] for r in res)
    print(f"\nencoded vectors total about {total_gb:.1f} GB (fp16, 1024 dimensions)")
    print("Needs attention: " + "; ".join(bad) if bad else "OK: docids unique, all qrels passages are in the corpus")
    os.makedirs(os.path.join(ROOT, "results", "miracl"), exist_ok=True)
    p = os.path.join(ROOT, "results", "miracl", "data_check.json")
    json.dump(res, open(p, "w"), indent=2, ensure_ascii=False)
    print("saved", p)
    os.system(f"df -h {ROOT}")


if __name__ == "__main__":
    main()
