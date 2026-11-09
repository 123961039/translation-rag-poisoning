"""
MIRACL poison generation step 2: machine-translate the English poison bodies into the target language with NLLB-200 and assemble the three variants.
    python ml_translate.py --lang sw
    python ml_translate.py                      # all of sw te yo id
Input: results/miracl/<lang>/poison_gen.jsonl (output of ml_gen_poison.py)
Output: results/miracl/<lang>/poison.jsonl; each question has three variants (injected separately during attacks):
    native  generated natively in the target language   -- the attacker knows the language
    trans   generated in English -> NLLB into the target language -- the attacker knows only English and uses MT
    en      English original, not translated              -- cross-lingual poisoning, relying on cross-lingual hits of a multilingual retriever
  Each variant has <v>_adv (body only) and <v>_poison (question verbatim + body, i.e. PoisonedRAG's S+I;
  the question is copied verbatim from the query, no knowledge of the language needed)
  Each trans item carries a trans_has_target flag: whether the translation still contains the target answer (MT may garble entities)
"""
import argparse, json, os

import re

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from transformers.utils import logging as hf_logging

hf_logging.set_verbosity_error()      # silence repeated max_length / max_new_tokens warnings

from ml_common import HF, LANGS, ml_results

NLLB_PATH = os.path.join(HF, "nllb-200-distilled-600M")
NLLB_CODE = {"sw": "swh_Latn", "te": "tel_Telu", "yo": "yor_Latn", "id": "ind_Latn"}


def keeps_target(t, it):
    """Whether the translation keeps the target answer. Strict: verbatim; loose: all digits of the answer appear, or (no digits) at least one answer word of >=4 characters appears.
    MT often renders "5,000 sq km" as "5,000 చదరపు కిలోమీటర్లు", which a strict match would misjudge"""
    tl = t.lower()
    strict = it["incorrect"].lower() in tl or it["incorrect_en"].lower() in tl
    nums = re.findall(r"\d[\d,.]*", it["incorrect_en"]) or re.findall(r"\d[\d,.]*", it["incorrect"])
    if nums:
        loose = all(n.strip(",.") in t for n in nums)
    else:
        words = [w for w in re.findall(r"\w+", it["incorrect"] + " " + it["incorrect_en"]) if len(w) >= 4]
        loose = any(w.lower() in tl for w in words)
    return strict, strict or loose


@torch.no_grad()
def translate(model, tok, texts, tgt, batch=32, beams=4):
    tok.src_lang = "eng_Latn"
    bos = tok.convert_tokens_to_ids(tgt)
    out = []
    for i in range(0, len(texts), batch):
        enc = tok(texts[i:i + batch], return_tensors="pt", padding=True, truncation=True, max_length=256).to(model.device)
        gen = model.generate(**enc, forced_bos_token_id=bos, num_beams=beams, max_new_tokens=300)
        out += tok.batch_decode(gen, skip_special_tokens=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", nargs="+", default=LANGS)
    ap.add_argument("--device", default="cuda")
    args = ap.parse_args()
    tok = AutoTokenizer.from_pretrained(NLLB_PATH)
    model = AutoModelForSeq2SeqLM.from_pretrained(NLLB_PATH, torch_dtype=torch.float16 if args.device == "cuda"
                                                  else torch.float32).to(args.device).eval()
    for lang in args.lang:
        rd = ml_results(lang)
        src = os.path.join(rd, "poison_gen.jsonl")
        if not os.path.exists(src):
            print(f"[{lang}] no {src}, skipped")
            continue
        items = [json.loads(l) for l in open(src)]
        flat = [t for it in items for t in it["en_adv"]]
        tr = translate(model, tok, flat, NLLB_CODE[lang])
        k, kept, kept_strict = 0, 0, 0
        for it in items:
            n = len(it["en_adv"])
            it["trans_adv"] = tr[k:k + n]
            k += n
            flags = [keeps_target(t, it) for t in it["trans_adv"]]
            it["trans_has_target_strict"] = [a for a, _ in flags]
            it["trans_has_target"] = [b for _, b in flags]
            kept += sum(it["trans_has_target"])
            kept_strict += sum(it["trans_has_target_strict"])
            for v in ("native", "trans", "en"):
                it[f"{v}_poison"] = [f"{it['question']} {t}" for t in it[f"{v}_adv"]]
        with open(os.path.join(rd, "poison.jsonl"), "w") as f:
            for it in items:
                f.write(json.dumps(it, ensure_ascii=False) + "\n")
        n = max(len(flat), 1)
        print(f"[{lang}] {len(items)} questions, {len(flat)} translated; translation keeps target answer: strict {kept_strict}/{len(flat)} "
              f"({kept_strict / n:.0%}), loose {kept}/{len(flat)} ({kept / n:.0%})", flush=True)
        if items:
            ex = items[0]
            print(f"  en:    {ex['en_adv'][0]}\n  trans: {ex['trans_adv'][0]}\n"
                  f"  native:{(ex['native_adv'] or ['(not filled)'])[0]}", flush=True)


if __name__ == "__main__":
    main()