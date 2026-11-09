"""
Question-prefix detection + combined detector (CPU only, runs without a GPU, about 1 minute)
    python ml_prefix_detect.py                      # main signal: question mark (default)
    python ml_prefix_detect.py --qsignal prefix     # main signal: question mark or question word
Motivation: removing the question prefix lowers the attack hit rate and makes isolation detection easier; if we can recognise "a question embedded in a passage", both ends are covered.
Question features (text only, no embeddings needed)
  q_mark    contains a question mark
  q_word    a question word of the language within the first 12 words (whole-word match for Latin-script languages; prefix match for Telugu)
  q_prefix  q_mark or q_word
Combined detector: the question signal fires, or isolation (--feat) exceeds a threshold. The isolation threshold uses the remaining budget "total FPR - question-signal FPR";
  if the question signal alone already exceeds the budget, the isolation-only control is compared at the same actual FPR, for fairness.
Attacker best response: the attacker knows the detection rule and picks whichever of "with prefix bb / without prefix adv" is best for them;
  for each defense, compute per question the fraction "in top-5 and not flagged" and take the larger of the two forms = worst-case surviving-poison rate.
Output: results/miracl/prefix_summary[_excl-bad|_excl-unsure].md / .json (no suffix with --exclude none)
"""
import argparse, json, os, re

import numpy as np
import pyarrow.parquet as pq

from ml_common import LANGS, ROOT, corpus_parquet, doc_format, load_keep, ml_results
from ml_analyze import VARIANTS, boot_mean, fmt

QWORDS = {
    "sw": ["nani", "nini", "lini", "wapi", "vipi", "gani", "ngapi", "kwa nini"],
    "te": ["ఎంత", "ఎక్కడ", "ఎప్పుడు", "ఎవరు", "ఏమి", "ఏది", "ఎలా", "ఎందుకు", "ఎన్ని"],
    "yo": ["kí", "ki", "tani", "tí", "nígbà wo", "nigba wo", "ibo", "báwo", "bawo", "mélòó", "melo"],
    "id": ["apa", "apakah", "siapa", "kapan", "dimana", "di mana", "mengapa", "kenapa", "bagaimana", "berapa"],
}
QMARK = re.compile(r"[?\uff1f]")


def q_feats(text, lang):
    head_tokens = re.findall(r"\w+", text.lower())[:12]
    head = " ".join(head_tokens)
    mark = bool(QMARK.search(text))
    if lang == "te":   # Telugu question words often carry suffixes; match by word prefix
        word = any(tok.startswith(w) for tok in head_tokens for w in QWORDS[lang])
    else:              # whole-word (or whole-phrase) match, so that apa does not match apabila and je does not match jeshi
        word = any(re.search(rf"(?<!\w){re.escape(w)}(?!\w)", head) for w in QWORDS[lang])
    return {"q_mark": float(mark), "q_word": float(word), "q_prefix": float(mark or word)}


def corpus_texts(lang, rows):
    t = pq.read_table(corpus_parquet(lang), columns=["title", "text"]).take(np.asarray(rows)).to_pydict()
    return [doc_format((a or "").strip(), (b or "").strip()) for a, b in zip(t["title"], t["text"])]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", nargs="+", default=LANGS)
    ap.add_argument("--feat", default="rel_knn10")
    ap.add_argument("--qsignal", default="q_mark", choices=["q_mark", "q_prefix"])
    ap.add_argument("--fpr", type=float, default=0.05)
    ap.add_argument("--size", default="full", help="corpus size used for attack hits (same as ml_attack.py)")
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--exclude", default="bad", choices=["none", "bad", "unsure"],
                    help="exclude bad questions by manual judgments: none = keep all; bad = drop bad; unsure = also drop unsure")
    ap.add_argument("--judgments", default=None, help="judgment file, default results/miracl/review_judgments.json")
    args = ap.parse_args()
    rng = np.random.default_rng(args.seed)
    Fq, Cmb, BR = [], [], []

    for lang in args.lang:
        rd = ml_results(lang)
        paths = [os.path.join(rd, f) for f in ("poison.jsonl", "detect_feats.npz", "attack_detail.jsonl")]
        if not all(os.path.exists(p) for p in paths):
            print(f"[{lang}] missing result files, skipped")
            continue
        items = [json.loads(l) for l in open(paths[0])]
        z = np.load(paths[1])
        detail = [json.loads(l) for l in open(paths[2])]
        assert [d["qid"] for d in detail] == [it["qid"] for it in items], "attack_detail and poison.jsonl are in different order"
        pos_clean = {r: i for i, r in enumerate(z["clean_rows"])}
        iso_clean = -z[f"clean_{args.feat}"]
        keep, kst = load_keep(lang, items, args.exclude, args.judgments)
        print(f"[{lang}] exclusion {kst}, kept {sum(keep)}/{len(items)} questions", flush=True)

        rand_txt = corpus_texts(lang, z["rand"])
        rq = {k: np.array([q_feats(t, lang)[k] for t in rand_txt]) for k in ("q_mark", "q_word", "q_prefix")}
        iso_r = iso_clean[[pos_clean[r] for r in z["rand"]]]
        sig_r = rq[args.qsignal] > 0.5
        base = float(sig_r.mean())
        budget = max(args.fpr - base, 0.0)
        thr_c = (float(np.quantile(iso_r[~sig_r], 1 - budget / (~sig_r).mean())) if budget > 0 else np.inf)
        fpr_c = float((sig_r | (iso_r > thr_c)).mean())
        fpr_iso = max(args.fpr, fpr_c)                       # isolation-only control at the same actual FPR
        thr_i = float(np.quantile(iso_r, 1 - fpr_iso))
        print(f"[{lang}] false alarms on random benign passages: question mark {rq['q_mark'].mean():.3f}  question word {rq['q_word'].mean():.3f}  "
              f"either {rq['q_prefix'].mean():.3f} | combined detector actual FPR {fpr_c:.3f}" +
              (" (question signal alone exceeds the budget)" if base > args.fpr else ""), flush=True)

        for v in VARIANTS:
            has_full = [j for j, it in enumerate(items) if it.get(f"{v}_adv")]   # aligned with the npz
            sel = [i for i, j in enumerate(has_full) if keep[j]]
            has = [has_full[i] for i in sel]
            if not has or f"{v}_bb_{args.feat}" not in z.files:
                continue
            per_form = {}
            for form in ("bb", "adv"):
                texts = [(f"{items[j]['question']} {items[j][f'{v}_adv'][0]}" if form == "bb" else items[j][f"{v}_adv"][0])
                         for j in has]
                q = {k: np.array([q_feats(t, lang)[k] for t in texts]) for k in ("q_mark", "q_word", "q_prefix")}
                iso_p = -z[f"{v}_{form}_{args.feat}"][sel]
                flag_i = iso_p > thr_i
                flag_c = (q[args.qsignal] > 0.5) | (iso_p > thr_c)
                hit = np.array([bool(detail[j][f"{args.size}/{v}/{form}/single/hit5"]) for j in has])
                per_form[form] = {"hit": hit, "flag_i": flag_i, "flag_c": flag_c}
                Fq.append({"lang": lang, "variant": v, "form": form, "n": len(has),
                           **{f"poison_{k}": float(q[k].mean()) for k in q},
                           **{f"clean_{k}": float(rq[k].mean()) for k in rq}})
                Cmb.append({"lang": lang, "variant": v, "form": form, "n": len(has), "fpr": fpr_c,
                            "iso_only": boot_mean(flag_i, args.boot, rng),
                            "q_only": boot_mean(q[args.qsignal] > 0.5, args.boot, rng),
                            "combined": boot_mean(flag_c, args.boot, rng)})

            # attacker best response: bootstrap paired by question, each time taking the form with the larger surviving rate
            n = len(has)
            eff = {d: {f: (per_form[f]["hit"] & ~per_form[f][f"flag_{d}"]).astype(float) for f in ("bb", "adv")}
                   for d in ("i", "c")}
            none = {f: per_form[f]["hit"].astype(float) for f in ("bb", "adv")}
            def worst(e):
                pt = max(e["bb"].mean(), e["adv"].mean())
                bs = []
                for _ in range(args.boot):
                    idx = rng.integers(0, n, n)
                    bs.append(max(e["bb"][idx].mean(), e["adv"][idx].mean()))
                return float(pt), [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))], \
                    ("bb" if e["bb"].mean() >= e["adv"].mean() else "adv")
            BR.append({"lang": lang, "variant": v, "n": n, "fpr": fpr_c,
                       "no_defense": worst(none), "iso_only": worst(eff["i"]), "combined": worst(eff["c"])})

    L = [f"# Question prefix + isolation combined detection (question signal {args.qsignal}, isolation {args.feat}, target FPR {args.fpr:.0%}, exclusion {args.exclude})", "",
         "## 1. Firing rate of the question signal", "",
         "| lang | variant | form | n | poison: ? | poison: q-word | benign: ? | benign: q-word |", "|---|---|---|---|---|---|---|---|"]
    for r in Fq:
        L.append(f"| {r['lang']} | {r['variant']} | {r['form']} | {r['n']} | {r['poison_q_mark']:.2f} | {r['poison_q_word']:.2f} | "
                 f"{r['clean_q_mark']:.3f} | {r['clean_q_word']:.3f} |")
    L += ["", "Benign columns = FPR of that signal alone (random benign passages).", "",
          "## 2. Detection rate (at the same actual FPR)", "",
          "| lang | variant | form | n | actual FPR | isolation only | question signal only | combined |", "|---|---|---|---|---|---|---|---|"]
    for r in Cmb:
        L.append(f"| {r['lang']} | {r['variant']} | {r['form']} | {r['n']} | {r['fpr']:.3f} | {fmt(*r['iso_only'])} | "
                 f"{fmt(*r['q_only'])} | {fmt(*r['combined'])} |")
    L += ["", "## 3. Surviving-poison rate under the attacker's best response (lower is better)", "",
          "The attacker picks whichever of with / without prefix is best for them; surviving = in top-5 and not flagged (one poison per question). The bb/adv outside brackets is the attacker's best choice.", "",
          "| lang | variant | questions | actual FPR | no defense | isolation only | combined |", "|---|---|---|---|---|---|---|"]
    for r in BR:
        c = lambda x: f"{x[0]:.2f} ({x[1][0]:.2f}–{x[1][1]:.2f}) {x[2]}"
        L.append(f"| {r['lang']} | {r['variant']} | {r['n']} | {r['fpr']:.3f} | {c(r['no_defense'])} | {c(r['iso_only'])} | {c(r['combined'])} |")
    out = os.path.join(ROOT, "results", "miracl")
    tag = "" if args.exclude == "none" else f"_excl-{args.exclude}"
    open(os.path.join(out, f"prefix_summary{tag}.md"), "w").write("\n".join(L) + "\n")
    json.dump({"q": Fq, "combined": Cmb, "best_response": BR, "args": vars(args)},
              open(os.path.join(out, f"prefix_summary{tag}.json"), "w"), indent=1, ensure_ascii=False)
    print("\n".join(L))
    print(f"\nsaved {out}/prefix_summary{tag}.md")


if __name__ == "__main__":
    main()
