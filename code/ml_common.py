"""Shared utilities for the multilingual (MIRACL) experiments. gpu_topk etc. come from common.py.
Layout:
    data/miracl/<lang>/corpus.parquet          docid, title, text (converted from docs-*.jsonl.gz)
    data/miracl/<lang>/raw/...                 raw topics / qrels tsv
    emb/miracl/<lang>/bge-m3/                  corpus_emb_fp16.npy, corpus_ids.txt, query_emb_fp16.npy, query_ids.txt
    results/miracl/<lang>/
"""
import glob, os

import numpy as np

# common is not imported here (it loads torch); download / check scripts on CPU-only instances need only these light helpers
ROOT = os.environ.get("PROJ", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HF = os.environ.get("HF_MODELS", os.path.join(ROOT, "models"))


def doc_format(title, text):
    """Same as common.doc_format (the format used to embed the corpus)"""
    return f"{title}. {text}" if title else text


def read_lines(path):
    with open(path) as f:
        return [l for l in f.read().split("\n") if l]


def gpu_topk(*args, **kwargs):
    from common import gpu_topk as _g   # torch is loaded only when needed
    return _g(*args, **kwargs)

M3_NAME = "bge-m3"
M3_PATH = os.path.join(HF, M3_NAME)
LANGS = ["sw", "te", "yo", "id"]          # low-resource: sw te yo; higher-resource control: id

# BGE-M3 paper, Table 1 (MIRACL dev, dense, nDCG@10), used only as an order-of-magnitude sanity check;
# the paper removes passages with the same id as the query and we do not, so our values may be slightly higher
REF_NDCG10 = {"sw": 78.7, "te": 86.2, "yo": 81.8, "id": 56.1}


def ml_data(lang):
    return os.path.join(ROOT, "data", "miracl", lang)


def ml_emb(lang):
    d = os.path.join(ROOT, "emb", "miracl", lang, M3_NAME)
    os.makedirs(d, exist_ok=True)
    return d


def ml_results(lang):
    d = os.path.join(ROOT, "results", "miracl", lang)
    os.makedirs(d, exist_ok=True)
    return d


def corpus_parquet(lang):
    return os.path.join(ml_data(lang), "corpus.parquet")


def _raw(lang, kind, split):
    pat = os.path.join(ml_data(lang), "raw", "**", f"{kind}.miracl-v1.0-{lang}-{split}.tsv")
    hits = sorted(glob.glob(pat, recursive=True))
    return hits[0] if hits else None


def query_splits(lang):
    """Which query splits exist for this language (dev / train / test-a / test-b)"""
    out = []
    for s in ("dev", "train", "test-a", "test-b"):
        if _raw(lang, "topics", s):
            out.append(s)
    return out


def load_topics(lang, split):
    p = _raw(lang, "topics", split)
    assert p, f"no {split} query file for {lang}"
    out = {}
    with open(p, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            qid, text = line.split("\t", 1)
            out[qid] = text
    return out


def load_qrels(lang, split):
    """TREC format: qid Q0 docid rel; keep only rel > 0"""
    p = _raw(lang, "qrels", split)
    assert p, f"no {split} qrels for {lang}"
    out = {}
    with open(p, encoding="utf-8") as f:
        for line in f:
            parts = line.split()
            if len(parts) != 4:
                continue
            qid, _, did, rel = parts
            if int(rel) > 0:
                out.setdefault(qid, {})[did] = int(rel)
    return out


def load_corpus_emb(lang):
    d = ml_emb(lang)
    emb = np.load(os.path.join(d, "corpus_emb_fp16.npy"), mmap_mode="r")
    ids = read_lines(os.path.join(d, "corpus_ids.txt"))
    assert len(ids) == emb.shape[0], f"{len(ids)} ids but {emb.shape[0]} vectors"
    return emb, ids


def load_query_emb(lang):
    d = ml_emb(lang)
    emb = np.load(os.path.join(d, "query_emb_fp16.npy"))
    ids = read_lines(os.path.join(d, "query_ids.txt"))
    return emb, {q: i for i, q in enumerate(ids)}


def load_keep(lang, items, level="bad", path=None):
    """Return, per question, whether it is kept according to human judgments (aligned with items).
    level: none = keep all; bad = drop bad; unsure = drop bad and unsure.
    Judgment file defaults to results/miracl/review_judgments.json, format {lang: {qid: {"label": ok/bad/unsure, ...}}};
    questions missing from the file are kept and counted."""
    import json
    keep = [True] * len(items)
    if level == "none":
        return keep, {"level": "none"}
    path = path or os.path.join(ROOT, "results", "miracl", "review_judgments.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"judgment file {path} missing; use --exclude none to keep all questions")
    J = json.load(open(path)).get(lang, {})
    drop = {"bad"} if level == "bad" else {"bad", "unsure"}
    stat = {"level": level, "judged": 0, "dropped": 0, "unjudged": 0}
    for j, it in enumerate(items):
        lab = J.get(it["qid"], {}).get("label")
        if lab is None:
            stat["unjudged"] += 1
            continue
        stat["judged"] += 1
        if lab in drop:
            keep[j] = False
            stat["dropped"] += 1
    return keep, stat
