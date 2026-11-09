"""
Reader diagnostic (GPU, a few minutes): Qwen2.5-7B answered almost all clean questions with unknown (id 28/28); check whether the prompt causes it.
Only the clean condition (clean top-5, no poison), questions kept by native-speaker judgments; the same contexts with three prompt wordings:
  orig        identical to ml_asr.py
  no_unknown  without the sentence "answer unknown if the context does not answer"
  soft        keeps the unknown option but explicitly requires answering when the context contains the answer
Each reader is run separately (one vLLM process loads one model):
    python ml_reader_probe.py --reader $HF_MODELS/Qwen2.5-7B-Instruct-AWQ --tag qwen25_7b
    python ml_reader_probe.py --reader $HF_MODELS/Qwen3-14B-AWQ --tag qwen3_14b
Output: results/miracl/reader_probe_<tag>.md / .jsonl
"""
import argparse, json, os, re

from vllm import LLM, SamplingParams

import numpy as np

import ml_asr
from ml_asr import RAG_PROMPT, appears, corpus_text_fn, norm, strip_think
from ml_common import ROOT, gpu_topk, load_corpus_emb, load_keep, load_query_emb
from ml_attack import load_items

PROMPTS = {
    "orig": RAG_PROMPT,
    "no_unknown": RAG_PROMPT.replace(" If the context does not answer it, reply exactly: unknown", ""),
    "soft": RAG_PROMPT.replace(
        "If the context does not answer it, reply exactly: unknown",
        "The answer is usually in the context, so read every passage carefully and answer whenever any passage "
        "contains it. Reply exactly: unknown only if none of the passages contains the answer."),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reader", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--lang", nargs="+", default=["sw", "te", "yo", "id"])
    ap.add_argument("--judgments", default=os.path.join(ROOT, "results", "miracl", "review_judgments_native.json"))
    args = ap.parse_args()
    assert PROMPTS["no_unknown"] != RAG_PROMPT and PROMPTS["soft"] != RAG_PROMPT, "RAG_PROMPT text changed; the replacement did not apply"

    jobs = []
    for lang in args.lang:
        items, _ = load_items(lang)
        keep, _ = load_keep(lang, items, "bad", args.judgments)
        corpus, _ = load_corpus_emb(lang)
        qemb, qid2row = load_query_emb(lang)
        ctext = corpus_text_fn(lang)
        js = [j for j in range(len(items)) if keep[j]]
        Q = qemb[[qid2row[items[j]["qid"]] for j in js]]
        _, I = gpu_topk([corpus], Q, 5)
        for k, j in enumerate(js):
            it = items[j]
            ctx = "\n\n".join(f"[{i + 1}] {ctext(int(r))}" for i, r in enumerate(I[k]))
            for pv, tmpl in PROMPTS.items():
                jobs.append({"lang": lang, "qid": it["qid"], "prompt_variant": pv,
                             "prompt": tmpl.format(ctx=ctx, q=it["question"]),
                             "correct": it["correct"], "correct_en": it.get("correct_en", "")})
        print(f"[{lang}] {len(js)} questions", flush=True)

    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(args.reader)
    tl = [len(tok(j["prompt"], add_special_tokens=False).input_ids) for j in jobs]
    import torch
    free_b, total_b = torch.cuda.mem_get_info()
    llm = LLM(model=args.reader, gpu_memory_utilization=(free_b - 2**30) / total_b,
              max_model_len=min(max(tl) + 300, 32768), seed=0, enable_prefix_caching=True)
    sp = SamplingParams(temperature=0.0, max_tokens=64)
    convs = [[{"role": "user", "content": j["prompt"]}] for j in jobs]
    try:
        outs = llm.chat(convs, sp, chat_template_kwargs={"enable_thinking": False})
    except TypeError:
        outs = llm.chat(convs, sp)
    for j, o in zip(jobs, outs):
        a = strip_think(o.outputs[0].text).strip()
        j["answer"] = a
        j["unknown"] = norm(a).startswith("unknown")
        j["hit_correct"] = bool(appears(j["correct"], a) or (j["correct_en"] and appears(j["correct_en"], a)))

    out = os.path.join(ROOT, "results", "miracl")
    L = [f"# Reader diagnostic: {args.tag} ({args.reader}), clean condition, native-validated questions", "",
         "| lang | questions | " + " | ".join(f"{p} accuracy / unknown" for p in PROMPTS) + " |", "|---|---|" + "---|" * len(PROMPTS)]
    for lang in args.lang:
        cells, n = [], 0
        for p in PROMPTS:
            g = [j for j in jobs if j["lang"] == lang and j["prompt_variant"] == p]
            n = len(g)
            cells.append(f"{np.mean([j['hit_correct'] for j in g]):.2f} / {np.mean([j['unknown'] for j in g]):.2f}")
        L.append(f"| {lang} | {n} | " + " | ".join(cells) + " |")
    L += ["", "## First 3 answers per language (orig)", ""]
    for lang in args.lang:
        for j in [j for j in jobs if j["lang"] == lang and j["prompt_variant"] == "orig"][:3]:
            L.append(f"- {lang} {j['qid']}: {j['answer'][:80]!r} (correct answer {j['correct']})")
    open(os.path.join(out, f"reader_probe_{args.tag}.md"), "w").write("\n".join(L) + "\n")
    with open(os.path.join(out, f"reader_probe_{args.tag}.jsonl"), "w") as fo:
        for j in jobs:
            fo.write(json.dumps({k: j[k] for k in ("lang", "qid", "prompt_variant", "answer", "unknown", "hit_correct")},
                                ensure_ascii=False) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
