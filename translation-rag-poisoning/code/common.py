"""Shared utilities: paths, data loading, chunked exact top-k search on the GPU. Imported by the other scripts."""
import glob
import os

import numpy as np
import pyarrow.parquet as pq
import torch

ROOT = os.environ.get("PROJ", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HF = os.environ.get("HF_MODELS", os.path.join(ROOT, "models"))
EMB_MODEL = os.path.join(HF, "bge-base-en-v1.5")
EMB_NAME = "bge-base-en-v1.5"
LLM_PATH = os.path.join(HF, "Qwen2.5-7B-Instruct")
QUERY_INSTRUCTION = "Represent this sentence for searching relevant passages: "


def data_dir(ds):
    return os.path.join(ROOT, "data", ds)


def emb_dir(ds):
    return os.path.join(ROOT, "emb", ds, EMB_NAME)


def results_dir(ds):
    d = os.path.join(ROOT, "results", ds)
    os.makedirs(d, exist_ok=True)
    return d


def default_split(ds):
    # BEIR convention: MS MARCO is evaluated on dev, the others on test
    return "dev" if ds == "msmarco" else "test"


def read_lines(path):
    with open(path) as f:
        return [l for l in f.read().split("\n") if l]


def corpus_parquet(ds):
    return sorted(glob.glob(os.path.join(data_dir(ds), "raw", "**", "*corpus*.parquet"), recursive=True))[0]


def load_corpus_emb(ds):
    emb = np.load(os.path.join(emb_dir(ds), "corpus_emb_fp16.npy"), mmap_mode="r")
    ids = read_lines(os.path.join(emb_dir(ds), "corpus_ids.txt"))
    assert len(ids) == emb.shape[0], f"{len(ids)} ids but {emb.shape[0]} vectors"
    return emb, ids


def load_query_emb(ds):
    emb = np.load(os.path.join(emb_dir(ds), "query_emb_fp16.npy"))
    ids = read_lines(os.path.join(emb_dir(ds), "query_ids.txt"))
    return emb, {q: i for i, q in enumerate(ids)}


def load_query_text(ds):
    p = sorted(glob.glob(os.path.join(data_dir(ds), "raw", "**", "*queries*.parquet"), recursive=True))[0]
    t = pq.read_table(p, columns=["_id", "text"]).to_pydict()
    return dict(zip(map(str, t["_id"]), t["text"]))


def load_qrels(ds, split=None):
    split = split or default_split(ds)
    hits = sorted(glob.glob(os.path.join(data_dir(ds), "qrels", "**", f"{split}.tsv"), recursive=True))
    assert hits, f"{split}.tsv not found"
    qrels = {}
    with open(hits[0]) as f:
        next(f)  # header
        for line in f:
            qid, did, score = line.rstrip("\n").split("\t")
            if int(score) > 0:
                qrels.setdefault(qid, {})[did] = int(score)
    return qrels


def fetch_docs(ds, doc_ids):
    """Read corpus text by id; returns {id: (title, text)}"""
    t = pq.read_table(corpus_parquet(ds), columns=["_id", "title", "text"],
                      filters=[("_id", "in", list(doc_ids))]).to_pydict()
    return {str(i): ((ti or "").strip(), (tx or "").strip())
            for i, ti, tx in zip(t["_id"], t["title"], t["text"])}


def doc_format(title, text):
    """Document format used for embedding the corpus (must match the stored embeddings)"""
    return f"{title}. {text}" if title else text


@torch.no_grad()
def gpu_topk(blocks, queries, k, qbatch=1024, chunk=1_000_000, device="cuda"):
    """Exact inner-product top-k over several vector blocks (concatenated in order, global ids contiguous).
    The corpus is moved to the GPU chunk by chunk, so GPU memory does not grow with corpus size."""
    q = torch.from_numpy(np.ascontiguousarray(queries, dtype=np.float16)).to(device)
    m = q.shape[0]
    best_s = torch.full((m, k), -1e4, device=device, dtype=torch.float32)
    best_i = torch.full((m, k), -1, device=device, dtype=torch.int64)
    off = 0
    for blk in blocks:
        n = blk.shape[0]
        for s in range(0, n, chunk):
            c = torch.from_numpy(np.ascontiguousarray(blk[s:s + chunk], dtype=np.float16)).to(device)
            kk = min(k, c.shape[0])
            for a in range(0, m, qbatch):
                ts, ti = (q[a:a + qbatch] @ c.T).topk(kk, dim=1)
                cs = torch.cat([best_s[a:a + qbatch], ts.float()], 1)
                ci = torch.cat([best_i[a:a + qbatch], ti + (off + s)], 1)
                bs, bi = cs.topk(k, dim=1)
                best_s[a:a + qbatch] = bs
                best_i[a:a + qbatch] = ci.gather(1, bi)
            del c
        off += n
    return best_s.cpu().numpy(), best_i.cpu().numpy()