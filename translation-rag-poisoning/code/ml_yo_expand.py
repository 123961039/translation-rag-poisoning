"""
yo expansion (GPU, about 10-20 minutes): yo dev has only 119 questions; originally only 28 survived (8 judged valid by native speakers).
The main loss in the original pipeline was step 1 "answer extraction": JSON parsing failed for 63 questions, and only the first gold passage was tried, once.
Here only unused dev questions are processed, and:
  1. all gold passages of each question are tried (up to --max_gold); greedy decoding first, then several samples at temperature 0.7 on failure
  2. everything else reuses ml_gen_poison.py / ml_translate.py: same prompts, answer-type check, poison quality filter,
     5 per question, NLLB translation and target-answer flag (imported directly, not copied)
  3. generator: the original Qwen2.5-7B-Instruct (common.LLM_PATH) if present; otherwise the AWQ-quantised version of the same model
New questions are written separately to results/miracl/yo/poison_new.jsonl; the existing poison.jsonl is not touched.
After native-speaker annotation (annotation files from make_yo_annot.py) marks them valid, merge with merge_yo_new.py and rerun yo downstream.
    python ml_yo_expand.py
"""
import argparse, json, os, random, time

from vllm import LLM, SamplingParams        # before torch

from ml_gen_poison import (ANSWER_PROMPT, LANG_NAME, NATIVE_SUFFIX, POISON_PROMPT, TYPE_CHECK_PROMPT,
                           fetch_passages, fill, parse_json, quality_reason)
from ml_common import HF, load_qrels, load_topics, ml_results
from common import LLM_PATH

LANG = "yo"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--llm", default=None, help="generator model directory; default the original Qwen2.5-7B-Instruct, else the AWQ version")
    ap.add_argument("--max_gold", type=int, default=3)
    ap.add_argument("--retries", type=int, default=6, help="after greedy failure, how many more samples per passage")
    ap.add_argument("--per_q", type=int, default=5)
    ap.add_argument("--words", type=int, default=30)
    ap.add_argument("--rounds", type=int, default=12)
    ap.add_argument("--gpu_util", type=float, default=0.6)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    T0 = time.time()
    llm_path = args.llm or (LLM_PATH if os.path.exists(os.path.join(LLM_PATH, "config.json"))
                            else os.path.join(HF, "Qwen2.5-7B-Instruct-AWQ"))
    rd = ml_results(LANG)
    used = {json.loads(l)["qid"] for l in open(os.path.join(rd, "poison.jsonl"))}
    qrels, topics = load_qrels(LANG, "dev"), load_topics(LANG, "dev")
    pool = sorted(q for q in qrels if q in topics and q not in used)
    random.Random(args.seed).shuffle(pool)
    golds = {q: sorted(qrels[q])[: args.max_gold] for q in pool}
    passages = fetch_passages(LANG, {g for gs in golds.values() for g in gs})
    print(f"[yo] dev {len([q for q in qrels if q in topics])} questions, {len(used)} already used, {len(pool)} candidates this run; "
          f"generator {llm_path}", flush=True)

    llm = LLM(model=llm_path, gpu_memory_utilization=args.gpu_util, max_model_len=4096, seed=args.seed,
              enable_prefix_caching=True)
    stat = {"candidates": len(pool), "parse_fail": 0, "correct_not_in_passage": 0, "type_mismatch": 0}

    # ---- 1. answer extraction: greedy per gold passage first, sampling on failure ----
    got = {}
    for attempt, sp in [("greedy", SamplingParams(temperature=0.0, max_tokens=400)),
                        ("sample", SamplingParams(n=args.retries, temperature=0.7, top_p=0.95, max_tokens=400, seed=args.seed))]:
        jobs = [(q, g) for q in pool if q not in got for g in golds[q] if passages.get(g)]
        if not jobs:
            break
        outs = llm.chat([[{"role": "user", "content": ANSWER_PROMPT.format(
            lang=LANG_NAME[LANG], passage=passages[g][:2000], question=topics[q])}] for q, g in jobs],
            sp)
        for (q, g), o in zip(jobs, outs):
            if q in got:
                continue
            for c in o.outputs:
                d = parse_json(c.text)
                if d and d["correct"].lower() in passages[g].lower():
                    got[q] = (g, d)
                    break
        print(f"  after answer extraction ({attempt}): {len(got)}/{len(pool)} succeeded", flush=True)
    stat["answers_parsed"] = len(got)

    items = [{"lang": LANG, "qid": q, "question": topics[q], "gold_ids": sorted(qrels[q]), "gold_first": g,
              "gold_passage": passages[g][:400], **d, "native_adv": [], "en_adv": [], "batch": "yo_expand_2026-10-29"}
             for q, (g, d) in got.items()]
    outs = llm.chat([[{"role": "user", "content": TYPE_CHECK_PROMPT.format(
        q=it["question_en"], c=it["correct_en"], w=it["incorrect_en"])}] for it in items],
        SamplingParams(temperature=0.0, max_tokens=3))
    keep = [it for it, o in zip(items, outs) if o.outputs[0].text.strip().lower().startswith("yes")]
    stat["type_mismatch"] = len(items) - len(keep)
    items = keep
    print(f"  {len(items)} questions after answer-type check", flush=True)

    # ---- 2. poison bodies (same prompts and filters as ml_gen_poison.py) ----
    sp = SamplingParams(n=args.per_q, temperature=1.0, top_p=0.95, max_tokens=200)
    rej_n = fill(llm, sp, items, "native_adv",
                 lambda it: POISON_PROMPT.format(q=it["question"], a=it["incorrect"], v=args.words)
                 + NATIVE_SUFFIX.format(lang=LANG_NAME[LANG]),
                 lambda it, t: quality_reason(t, it, args.words, "incorrect", "correct", "question", LANG),
                 args.per_q, args.rounds)
    rej_e = fill(llm, sp, items, "en_adv",
                 lambda it: POISON_PROMPT.format(q=it["question_en"], a=it["incorrect_en"], v=args.words),
                 lambda it, t: quality_reason(t, it, args.words, "incorrect_en", "correct_en", "question_en"),
                 args.per_q, args.rounds)
    full = [it for it in items if len(it["en_adv"]) == args.per_q]
    for it in full:
        it["native_ok"] = len(it["native_adv"]) == args.per_q
        if not it["native_ok"]:
            it["native_adv"] = []
    del llm
    import gc, torch
    gc.collect(); torch.cuda.empty_cache()

    # ---- 3. machine translation (same as ml_translate.py) ----
    from ml_translate import NLLB_CODE, NLLB_PATH, keeps_target, translate
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(NLLB_PATH)
    mt = AutoModelForSeq2SeqLM.from_pretrained(NLLB_PATH, torch_dtype=torch.float16).to("cuda").eval()
    flat = [t for it in full for t in it["en_adv"]]
    tr = translate(mt, tok, flat, NLLB_CODE[LANG]) if flat else []
    k = 0
    for it in full:
        n = len(it["en_adv"])
        it["trans_adv"] = tr[k:k + n]; k += n
        flags = [keeps_target(t, it) for t in it["trans_adv"]]
        it["trans_has_target_strict"] = [a for a, _ in flags]
        it["trans_has_target"] = [b for _, b in flags]
        for v in ("native", "trans", "en"):
            it[f"{v}_poison"] = [f"{it['question']} {t}" for t in it[f"{v}_adv"]]

    with open(os.path.join(rd, "poison_new.jsonl"), "w") as f:
        for it in full:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    stat.update({"kept": len(full), "native_ok": sum(it["native_ok"] for it in full),
                 "trans_target_loose": f"{sum(sum(it['trans_has_target']) for it in full)}/{len(flat)}",
                 "native_rejected": rej_n.get(LANG, {}), "en_rejected": rej_e.get(LANG, {}), "llm": llm_path})
    json.dump(stat, open(os.path.join(rd, "poison_new_stats.json"), "w"), indent=1, ensure_ascii=False)
    print(f"\nyo: {len(full)} new questions (native also filled for {stat['native_ok']}), took {int(time.time() - T0) // 60} min"
          f"\n   -> {rd}/poison_new.jsonl\n   stats {stat}\nNext step (CPU): python make_yo_annot.py", flush=True)


if __name__ == "__main__":
    main()
