"""
Ablation of the evidence-check baseline (GPU, about 45 minutes): is it strong because the retrieved evidence happens to contain the gold article?
In MIRACL every attacked question has gold passages in the corpus and the poison contradicts them by design, so the evidence check is in its most favourable setting.
Here passages from the "same article" are removed from the evidence and the check is repeated:
  poison: all passages of the question's gold article are removed from its evidence (simulating "no article in the corpus covers this fact");
  benign passage: all passages of its own article are removed from its evidence (symmetric treatment, otherwise benign passages would be favoured).
Benign samples are identical to ml_baselines_evidence.py (the non-NaN rows of the original evidence files).
Also recorded: share of poisons whose original top-5 evidence contains a gold-article passage; check throughput (passages/s).
    export VLLM_CACHE_ROOT=~/.cache/vllm TORCHINDUCTOR_CACHE_DIR=~/.cache/inductor
    python ml_evidence_ablation.py
Output: results/miracl/baselines/<lang>_evidence_noart.npz, baselines/evidence_cost.json
"""
import argparse, json, os, time

from vllm import LLM, SamplingParams        # import before torch

import numpy as np
import pyarrow.parquet as pq
from tqdm import tqdm

from ml_common import HF, LANGS, M3_PATH, ROOT, corpus_parquet, doc_format, gpu_topk, load_corpus_emb
from ml_attack import load_items, texts_of
from ml_baselines_evidence import PROMPT, READER, lp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", nargs="+", default=LANGS)
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--pool", type=int, default=100, help="neighbours retrieved before filtering")
    ap.add_argument("--max_tok", type=int, default=400)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    D = os.path.join(ROOT, "results", "miracl", "baselines")
    T0 = time.time()
    from sentence_transformers import SentenceTransformer
    import torch
    m = SentenceTransformer(M3_PATH, device="cuda").half(); m.max_seq_length = 512
    enc = lambda xs: m.encode(xs, batch_size=128, normalize_embeddings=True, convert_to_numpy=True,
                              show_progress_bar=False).astype(np.float16)
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(READER)
    clip = lambda t: tok.decode(tok(t, add_special_tokens=False).input_ids[:a.max_tok])
    jobs, meta, diag = [], {}, {}
    for lang in tqdm(a.lang, desc="preparing evidence"):
        z = np.load(os.path.join(D, f"{lang}.npz"))
        ze = np.load(os.path.join(D, f"{lang}_evidence.npz"))
        items, _ = load_items(lang)
        corpus, cids = load_corpus_emb(lang)
        _, art = np.unique(np.array([c.split("#")[0] for c in cids]), return_inverse=True)
        cid2row = {c: i for i, c in enumerate(cids)}
        tb = pq.read_table(corpus_parquet(lang), columns=["title", "text"])
        ti, tx = tb.column(0), tb.column(1)
        text = lambda r: doc_format((ti[int(r)].as_py() or "").strip(), (tx[int(r)].as_py() or "").strip())
        neg_rows = z["neg_rows"]
        pick = neg_rows[~np.isnan(ze["neg_evidence"])]
        _, In = gpu_topk([corpus], np.asarray(corpus[pick]), a.pool)
        short = 0
        for r, nb in zip(pick, In):
            ev = [int(x) for x in nb if x >= 0 and art[x] != art[r]][:a.k]
            short += len(ev) < a.k
            jobs.append((lang, "neg", int(np.searchsorted(neg_rows, r)), text(r), [text(x) for x in ev]))
        meta[lang] = {"n_neg": len(neg_rows)}
        diag[lang] = {"neg_short": int(short), "neg_n": int(len(pick))}
        for v in ("native", "trans", "en"):
            if f"{v}_items" not in z:
                continue
            idx = z[f"{v}_items"]
            meta[lang][v] = len(idx)
            P = [texts_of(items[j], v, "bb")[0] for j in idx]
            _, Ip = gpu_topk([corpus], enc(P), a.pool)
            had = np.zeros(len(idx), bool)
            for i, (j, t, nb) in enumerate(zip(idx, P, Ip)):
                ga = {art[cid2row[d]] for d in items[j]["gold_ids"] if d in cid2row}
                had[i] = any(art[x] in ga for x in nb[:a.k] if x >= 0)
                ev = [int(x) for x in nb if x >= 0 and art[x] not in ga][:a.k]
                jobs.append((lang, v, i, t, [text(x) for x in ev]))
            diag[lang][f"{v}_goldart_in_top{a.k}"] = had.tolist()
        tqdm.write(f"[{lang}] benign {len(pick):,} + poisons {sum(meta[lang].get(v, 0) for v in ('native', 'trans', 'en'))}")
    del m; torch.cuda.empty_cache()

    prompts = [PROMPT.format(refs="\n\n".join(f"[{i + 1}] {clip(e)}" for i, e in enumerate(ev)), cand=clip(c))
               for *_, c, ev in jobs]
    lens = [len(tok(p, add_special_tokens=False).input_ids) for p in prompts]
    free_b, total_b = torch.cuda.mem_get_info()
    llm = LLM(model=READER, gpu_memory_utilization=(free_b - 2 ** 30) / total_b, max_model_len=min(max(lens) + 64, 32768),
              seed=a.seed, enable_prefix_caching=False)
    sp = SamplingParams(max_tokens=1, logprobs=20, temperature=0.0)
    convs = [[{"role": "user", "content": p}] for p in prompts]
    print(f"\nLLM check of {len(convs):,} items (mean {np.mean(lens):.0f} tokens, longest {max(lens)}), elapsed {int(time.time() - T0) // 60} min", flush=True)
    t1 = time.time()
    try:
        outs = llm.chat(convs, sp, chat_template_kwargs={"enable_thinking": False}, use_tqdm=True)
    except TypeError:
        outs = llm.chat(convs, sp, use_tqdm=True)
    dt = time.time() - t1
    score = []
    for o in outs:
        top = o.outputs[0].logprobs[0] if o.outputs[0].logprobs else {}
        dec = lambda t, x: (getattr(x, "decoded_token", None) or tok.decode([t])).strip().lower()
        y = sum(np.exp(lp(x)) for t, x in top.items() if dec(t, x) == "yes")
        n = sum(np.exp(lp(x)) for t, x in top.items() if dec(t, x) == "no")
        score.append(y / (y + n) if y + n > 0 else 0.5)
    for lang in a.lang:
        d = {"neg_evidence_noart": np.full(meta[lang]["n_neg"], np.nan)}
        for v in ("native", "trans", "en"):
            if v in meta[lang]:
                d[f"{v}_evidence_noart"] = np.full(meta[lang][v], np.nan)
                d[f"{v}_goldart_in_ev"] = np.array(diag[lang][f"{v}_goldart_in_top{a.k}"])
        for (l, g, i, *_), s in zip(jobs, score):
            if l == lang:
                d[f"{g}_evidence_noart"][i] = s
        np.savez_compressed(os.path.join(D, f"{lang}_evidence_noart.npz"), **d)
    cost = {"n_prompts": len(convs), "llm_seconds": dt, "passages_per_sec": len(convs) / dt,
            "mean_prompt_tokens": float(np.mean(lens)), "gpu": torch.cuda.get_device_name(0), "reader": READER,
            "note": "excludes evidence retrieval and encoding time; prefix caching disabled, close to the real cost of passage-by-passage ingestion",
            "diag": {l: {k: v for k, v in dd.items() if not k.endswith(f"top{a.k}")} for l, dd in diag.items()},
            "goldart_rate": {l: {k.split("_")[0]: float(np.mean(v)) for k, v in dd.items() if k.endswith(f"top{a.k}")}
                             for l, dd in diag.items()}}
    json.dump(cost, open(os.path.join(D, "evidence_cost.json"), "w"), indent=1, ensure_ascii=False)
    print(json.dumps(cost, indent=1, ensure_ascii=False))
    print(f"\nall done, total time {int(time.time() - T0) // 60} min. Check throughput {len(convs) / dt:.1f} passages/s")


if __name__ == "__main__":
    main()
