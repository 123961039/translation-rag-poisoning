"""
System cost of ingestion-time detection (GPU).
Measures what deployment actually costs, in three categories:
  offline, once  : encoding the corpus (speed measured on a sample, extrapolated), memory / GPU memory of the vectors,
                   threshold calibration (features for 10k random benign passages)
  online, per new document: encoding + isolation features. knn10 needs one neighbour layer; rel_knn10 also needs neighbours of neighbours (one more search)
                   batch throughput (1000 documents per batch) and single-document latency (one at a time)
  scaling with corpus size: the same language downsampled to 131,924 / 45,000 / 20,000 passages
Search keeps the corpus resident in GPU memory with exact inner-product top-k (no approximate index), as in the experiments;
features are checked against ml_detect.two_layer (the "check" column). A CPU-only (numpy) knn10 is also reported,
to show that small corpora work without a GPU.
    python ml_efficiency.py                    # four languages, all sizes
    python ml_efficiency.py --lang sw --reps 5
Output: results/miracl/efficiency.md / .json
"""
import argparse, json, os, time

import numpy as np
import pyarrow.parquet as pq
import torch

from ml_common import LANGS, M3_PATH, ROOT, corpus_parquet, doc_format, load_corpus_emb
from ml_eval_retrieval import subsample_rows
from ml_detect import two_layer
from ml_attack import load_items, texts_of


def fmt_t(s):
    s = int(s)
    return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}" if s >= 3600 else f"{s // 60}:{s % 60:02d}"


def sync():
    torch.cuda.synchronize()


def timeit(fn, reps):
    """One warm-up run, then the median of reps runs (seconds)"""
    fn(); sync()
    ts = []
    for _ in range(reps):
        t = time.perf_counter(); fn(); sync(); ts.append(time.perf_counter() - t)
    return float(np.median(ts))


class Resident:
    """Exact search with the corpus resident in GPU memory; features identical to ml_detect.two_layer for new documents not in the corpus"""
    def __init__(self, corpus_np, chunk=2_000_000):
        self.C = torch.from_numpy(np.ascontiguousarray(corpus_np, dtype=np.float16)).cuda()
        self.chunk = chunk

    def topk(self, Q, k, qbatch=1024):
        out_s, out_i = [], []
        for a in range(0, Q.shape[0], qbatch):
            s, i = (Q[a:a + qbatch] @ self.C.T).topk(k, dim=1)
            out_s.append(s.float()); out_i.append(i)
        return torch.cat(out_s), torch.cat(out_i)

    def knn10(self, Q):
        S, _ = self.topk(Q, 10)
        return S.mean(1)

    def rel_knn10(self, Q, M=10):
        S, I = self.topk(Q, 10)
        knn = S.mean(1)
        U, inv = torch.unique(I[:, :M], return_inverse=True)
        Su, Iu = self.topk(self.C[U], 11)                      # a neighbour ranks itself first; drop it and keep 10
        keep = Iu != U[:, None]
        order = torch.argsort((~keep).to(torch.int8), dim=1, stable=True)[:, :10]
        ky = torch.gather(Su, 1, order).mean(1)
        return knn - ky[inv].mean(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", nargs="+", default=LANGS)
    ap.add_argument("--sizes", nargs="+", default=["full", "131924", "45000", "20000"])
    ap.add_argument("--n_encode", type=int, default=2000, help="passages used to measure encoding speed")
    ap.add_argument("--n_batch", type=int, default=1000, help="documents per batch for throughput")
    ap.add_argument("--n_single", type=int, default=100, help="documents for single-document latency")
    ap.add_argument("--n_calib", type=int, default=10000, help="benign passages for threshold calibration (as in ml_detect)")
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    out = os.path.join(ROOT, "results", "miracl")
    gpu = torch.cuda.get_device_name(0)
    print(f"GPU: {gpu}; CPU threads {torch.get_num_threads()}", flush=True)

    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(M3_PATH, device="cuda").half()
    model.max_seq_length = 512
    enc = lambda xs, bs=128: model.encode(xs, batch_size=bs, normalize_embeddings=True,
                                          convert_to_numpy=True, show_progress_bar=False).astype(np.float16)

    N_of = {l: load_corpus_emb(l)[0].shape[0] for l in args.lang}
    jobs = [(l, s) for l in args.lang for s in args.sizes if s == "full" or int(s) < N_of[l]]
    rows, T0 = [], time.time()
    rng = np.random.default_rng(args.seed)
    cache = None
    for k, (lang, size) in enumerate(jobs, 1):
        t0 = time.time()
        if cache != lang:
            corpus_full, _ = load_corpus_emb(lang)
            N = corpus_full.shape[0]
            # encoding speed: random real passages (title + body, same format as when building the index)
            tb = pq.read_table(corpus_parquet(lang), columns=["title", "text"])
            pick = np.sort(rng.choice(N, min(args.n_encode, N), replace=False))
            titles, texts = tb.column(0).to_pylist(), tb.column(1).to_pylist()
            sample = [doc_format((titles[i] or "").strip(), (texts[i] or "").strip()) for i in pick]
            del tb, titles, texts
            enc_s = timeit(lambda: enc(sample), 1)
            enc_rate = len(sample) / enc_s
            # new documents to screen: real poison texts, repeated to fill a batch if needed
            items, _ = load_items(lang)
            pois = [texts_of(it, "trans", "bb")[0] for it in items if it.get("trans_adv")]
            cand_txt = (pois * (args.n_batch // max(len(pois), 1) + 1))[:args.n_batch]
            Pc = enc(cand_txt)
            cache = lang

        if size == "full":
            corpus = np.asarray(corpus_full)
        else:
            corpus = np.asarray(corpus_full[subsample_rows(N, int(size), np.array([], dtype=np.int64), args.seed)])
        Ns = corpus.shape[0]
        torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats()
        t_load = time.perf_counter()
        R = Resident(corpus); sync()
        t_load = time.perf_counter() - t_load
        Q = torch.from_numpy(Pc).cuda()

            # check: the resident implementation matches ml_detect.two_layer
        F_ref = two_layer(corpus, Pc[:50], np.full(50, -1), 50, 10)
        d_knn = float(np.max(np.abs(R.knn10(Q[:50]).cpu().numpy() - F_ref["knn10"])))
        d_rel = float(np.max(np.abs(R.rel_knn10(Q[:50]).cpu().numpy() - F_ref["rel_knn10"])))

            # batch throughput (excluding encoding)
        tb_knn = timeit(lambda: R.knn10(Q), args.reps)
        tb_rel = timeit(lambda: R.rel_knn10(Q), args.reps)
            # single-document latency (including encoding: document arrives -> encode -> score)
        one = cand_txt[:args.n_single]
        def single(feat):
            for t in one:
                q = torch.from_numpy(enc([t], bs=1)).cuda()
                (R.knn10 if feat == "knn10" else R.rel_knn10)(q)
        ts_knn = timeit(lambda: single("knn10"), 1) / len(one)
        ts_rel = timeit(lambda: single("rel"), 1) / len(one)
            # threshold calibration: rel_knn10 for 10k benign corpus passages (offline, once)
        cal = np.sort(rng.choice(Ns, min(args.n_calib, Ns), replace=False))
        t_cal = timeit(lambda: R.rel_knn10(R.C[cal]), 1)        # corpus passages hit themselves; cost is of the same order as the real computation
        peak = torch.cuda.max_memory_allocated() / 2**30
        # CPU-only knn10 (small corpora only; multi-threaded numpy matmul)
        cpu_rate = None
        if Ns <= 150_000:
            Cf, Qf = corpus.astype(np.float32), Pc[:200].astype(np.float32)
            t = time.perf_counter()
            S = Qf @ Cf.T
            np.partition(-S, 10, axis=1)[:, :10]
            cpu_rate = 200 / (time.perf_counter() - t)
            del Cf
        del R, Q; torch.cuda.empty_cache()

        r = {"lang": lang, "size": size, "corpus": int(Ns), "emb_gb": Ns * corpus.shape[1] * 2 / 2**30,
             "encode_per_s": enc_rate, "encode_full_est_s": N / enc_rate if size == "full" else None,
             "gpu_load_s": t_load, "knn10_per_s": args.n_batch / tb_knn, "rel_per_s": args.n_batch / tb_rel,
             "lat_knn10_ms": ts_knn * 1000, "lat_rel_ms": ts_rel * 1000, "calib_s": t_cal,
             "gpu_peak_gb": peak, "cpu_knn10_per_s": cpu_rate, "check_knn10": d_knn, "check_rel": d_rel}
        rows.append(r)
        el = time.time() - T0
        bar = "#" * int(30 * k / len(jobs))
        print(f"[{bar:<30}] {k}/{len(jobs)}  elapsed {fmt_t(el)}  remaining {fmt_t(el / k * (len(jobs) - k))} | "
              f"{lang} {Ns:,} passages: rel_knn10 {r['rel_per_s']:,.0f} docs/s, single {r['lat_rel_ms']:.1f} ms, "
              f"GPU peak {peak:.1f} GB, check diff {max(d_knn, d_rel):.1e}, this step {fmt_t(time.time() - t0)}", flush=True)

    # ---------- output ----------
    L = [f"# System cost of ingestion-time detection ({gpu}, bge-m3 fp16, exact top-k with the corpus resident in GPU memory)", "",
         "## Online: detection cost per new document", "",
         "| lang | passages | vector memory | knn10 throughput (docs/s, excl. encoding) | rel_knn10 throughput | single-document latency knn10 / rel_knn10 (ms, incl. encoding) | GPU peak | CPU-only knn10 (docs/s) | check diff |",
         "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        cpu = f"{r['cpu_knn10_per_s']:,.0f}" if r["cpu_knn10_per_s"] else "- (not measured above 150k passages)"
        L.append(f"| {r['lang']} | {r['corpus']:,} | {r['emb_gb']:.2f} GB | {r['knn10_per_s']:,.0f} | {r['rel_per_s']:,.0f} | "
                 f"{r['lat_knn10_ms']:.1f} / {r['lat_rel_ms']:.1f} | {r['gpu_peak_gb']:.1f} GB | {cpu} | "
                 f"{max(r['check_knn10'], r['check_rel']):.1e} |")
    L += ["", "## Offline: one-time cost (full corpus)", "",
          "| lang | passages | encoding speed (passages/s) | full encoding (estimate) | load vectors to GPU | threshold calibration (10k) |", "|---|---|---|---|---|---|"]
    for r in rows:
        if r["size"] != "full":
            continue
        L.append(f"| {r['lang']} | {r['corpus']:,} | {r['encode_per_s']:,.0f} | {fmt_t(r['encode_full_est_s'])} | "
                 f"{r['gpu_load_s']:.1f} s | {r['calib_s']:.2f} s |")
    L += ["", "Notes",
          "- Throughput = a batch of 1000 documents scored together; single-document latency = documents arrive one by one, including bge-m3 encoding. Encoding usually dominates latency.",
          "- rel_knn10 needs one more search (neighbours of neighbours) than knn10, roughly twice the cost; both scale about linearly with corpus size (exact search).",
          "- No approximate index (HNSW / IVF) is used here; see ml_hnsw.py for the effect of HNSW on detection.",
          "- check diff = maximum feature difference between the resident implementation and ml_detect.two_layer used in the experiments; should be below 1e-3 (fp16 ties may reorder neighbours)."]
    open(os.path.join(out, "efficiency.md"), "w").write("\n".join(L) + "\n")
    json.dump({"gpu": gpu, "rows": rows, "args": vars(args)}, open(os.path.join(out, "efficiency.json"), "w"),
              indent=1, ensure_ascii=False)
    print("\n" + "\n".join(L))
    print(f"\nall done, total time {fmt_t(time.time() - T0)}. saved {out}/efficiency.md")


if __name__ == "__main__":
    main()
