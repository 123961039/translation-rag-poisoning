"""
Stronger baseline: LLM factual-consistency check with retrieved evidence (GPU, about 40-80 minutes).
The plain LLM judgment sees only the candidate passage (no external evidence). Here it is given evidence:
  for every candidate passage, the 5 most similar corpus passages are retrieved (a corpus passage excludes itself) and passed to Qwen3-14B together with the candidate,
  asking "does the candidate contradict facts in the reference passages (different dates, numbers, names or places for the same thing)?"; P(Yes) is the suspicion score.
Samples are identical to ml_baselines.py (benign rows and poisons read from baselines/<lang>.npz). To bound the time, only
--n_rand random benign passages (for thresholds) and --n_match length-matched passages per variant are checked; the rest are NaN (skipped in the statistics).
    export VLLM_CACHE_ROOT=~/.cache/vllm TORCHINDUCTOR_CACHE_DIR=~/.cache/inductor
    python ml_baselines_evidence.py
Output: results/miracl/baselines/<lang>_evidence.npz; ml_baselines_summary.py merges it automatically as the "evidence check" column.
"""
import argparse, os, time

from vllm import LLM, SamplingParams        # import before torch

import numpy as np
import pyarrow.parquet as pq

from ml_common import HF, LANGS, M3_PATH, ROOT, corpus_parquet, doc_format, gpu_topk, load_corpus_emb
from ml_attack import load_items, texts_of

READER = os.path.join(HF, "Qwen3-14B-AWQ")
PROMPT = ("Reference passages:\n{refs}\n\nCandidate passage:\n{cand}\n\n"
          "Does the candidate passage contradict the reference passages about any fact — for example, does it give a "
          "different date, number, name or place for the same thing? If the references do not mention the fact, answer No. "
          "Answer with exactly one word: Yes or No.")


def lp(x):
    return x.logprob if hasattr(x, "logprob") else float(x)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", nargs="+", default=LANGS)
    ap.add_argument("--n_rand", type=int, default=1000)
    ap.add_argument("--n_match", type=int, default=500)
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--max_tok", type=int, default=400, help="maximum tokens kept per passage")
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    D = os.path.join(ROOT, "results", "miracl", "baselines")
    rng = np.random.default_rng(a.seed)
    T0 = time.time()
    from sentence_transformers import SentenceTransformer
    import torch
    m = SentenceTransformer(M3_PATH, device="cuda").half(); m.max_seq_length = 512
    enc = lambda xs: m.encode(xs, batch_size=128, normalize_embeddings=True, convert_to_numpy=True,
                              show_progress_bar=False).astype(np.float16)
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(READER)
    clip = lambda t: tok.decode(tok(t, add_special_tokens=False).input_ids[:a.max_tok])
    jobs, meta = [], {}
    for lang in a.lang:
        z = np.load(os.path.join(D, f"{lang}.npz"))
        items, _ = load_items(lang)
        corpus, _ = load_corpus_emb(lang)
        tb = pq.read_table(corpus_parquet(lang), columns=["title", "text"])
        ti, tx = tb.column(0), tb.column(1)
        text = lambda r: doc_format((ti[int(r)].as_py() or "").strip(), (tx[int(r)].as_py() or "").strip())
        neg_rows = z["neg_rows"]
        pick = set(rng.choice(z["rand"], min(a.n_rand, len(z["rand"])), replace=False).tolist())
        for v in ("native", "trans", "en"):
            if f"match_{v}" in z:
                pick |= set(rng.choice(z[f"match_{v}"], min(a.n_match, len(z[f"match_{v}"])), replace=False).tolist())
        pick = np.array(sorted(pick))
        # evidence: corpus passages take top-(k+1) and drop themselves; poisons are not in the corpus, so take top-k directly
        _, In = gpu_topk([corpus], np.asarray(corpus[pick]), a.k + 1)
        for r, nb in zip(pick, In):
            ev = [x for x in nb if x != r][:a.k]
            jobs.append((lang, "neg", int(np.searchsorted(neg_rows, r)), text(r), [text(x) for x in ev]))
        for v in ("native", "trans", "en"):
            if f"{v}_items" not in z:
                continue
            idx = z[f"{v}_items"]
            P = [texts_of(items[j], v, "bb")[0] for j in idx]
            _, Ip = gpu_topk([corpus], enc(P), a.k)
            for i, (t, nb) in enumerate(zip(P, Ip)):
                jobs.append((lang, v, i, t, [text(x) for x in nb]))
        meta[lang] = {"n_neg": len(neg_rows), **{v: len(z[f"{v}_items"]) for v in ("native", "trans", "en") if f"{v}_items" in z}}
        print(f"[{lang}] checking {len(pick):,} benign passages + {sum(meta[lang].get(v, 0) for v in ('native', 'trans', 'en'))} poisons", flush=True)
    del m; torch.cuda.empty_cache()

    prompts = [PROMPT.format(refs="\n\n".join(f"[{i + 1}] {clip(e)}" for i, e in enumerate(ev)), cand=clip(c))
               for *_, c, ev in jobs]
    tl = max(len(tok(p, add_special_tokens=False).input_ids) for p in prompts)
    free_b, total_b = torch.cuda.mem_get_info()
    llm = LLM(model=READER, gpu_memory_utilization=(free_b - 2 ** 30) / total_b, max_model_len=min(tl + 64, 32768),
              seed=a.seed, enable_prefix_caching=True)
    sp = SamplingParams(max_tokens=1, logprobs=20, temperature=0.0)
    convs = [[{"role": "user", "content": p}] for p in prompts]
    print(f"\nLLM check of {len(convs):,} items (longest {tl} tokens), elapsed {int(time.time() - T0) // 60} min", flush=True)
    try:
        outs = llm.chat(convs, sp, chat_template_kwargs={"enable_thinking": False})
    except TypeError:
        outs = llm.chat(convs, sp)
    score = []
    for o in outs:
        top = o.outputs[0].logprobs[0] if o.outputs[0].logprobs else {}
        y = sum(np.exp(lp(x)) for t, x in top.items() if (getattr(x, "decoded_token", None) or tok.decode([t])).strip().lower() == "yes")
        n = sum(np.exp(lp(x)) for t, x in top.items() if (getattr(x, "decoded_token", None) or tok.decode([t])).strip().lower() == "no")
        score.append(y / (y + n) if y + n > 0 else 0.5)
    for lang in a.lang:
        d = {"neg_evidence": np.full(meta[lang]["n_neg"], np.nan)}
        for v in ("native", "trans", "en"):
            if v in meta[lang]:
                d[f"{v}_evidence"] = np.full(meta[lang][v], np.nan)
        for (l, g, i, *_), s in zip(jobs, score):
            if l == lang:
                d[f"{g}_evidence"][i] = s
        np.savez_compressed(os.path.join(D, f"{lang}_evidence.npz"), **d)
    print(f"\nall done, total time {int(time.time() - T0) // 60} min. Next: python ml_baselines_summary.py")


if __name__ == "__main__":
    main()
