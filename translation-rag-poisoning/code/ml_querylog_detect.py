"""
Query-log overlap detection (CPU only, runs without a GPU, a few minutes): does a passage contain a verbatim "past user question"?
    python ml_querylog_detect.py
    python ml_querylog_detect.py --tau 0.7
Motivation: question-mark detection is bypassed by deleting one question mark; the prefix attack hits well precisely because it puts the user question verbatim in the passage.
  Compare against a query log: flag a passage if most words of some past question appear contiguously in it. Deleting punctuation does not evade this;
  the attacker must paraphrase the question, and paraphrasing weakens the retrieval advantage of the prefix.
Feature s = max_q longest common contiguous word run / number of words of q (q from the query log, at least 3 words; words split on whitespace, punctuation stripped, lowercased)
Two query-log settings (both must be reported, to avoid reporting only the optimistic one)
  full         queries of all MIRACL splits of the language (the attacker targets questions "asked before")
  excl_target  all attacked questions removed (the attacker targets new questions not in the log) -- the signal should then nearly fail
Flag rule: s >= tau (default 0.8, i.e. more than 80% of the words of some past question appear contiguously)
The false alarms of this rule are also reported on random benign and gold passages (gold passages often share many words with the question and are the most likely to be hurt)
Combined detection: query-log signal OR isolation (rel_knn10) above a threshold set from the remaining FPR budget (total FPR --fpr)
Attacker best response: pick whichever of with / without prefix gives the highest surviving rate (as in ml_prefix_detect.py)
Output: results/miracl/querylog_summary[_excl-bad|_excl-unsure].md / .json (no suffix with --exclude none)
"""
import argparse, json, os, unicodedata
from collections import Counter, defaultdict

import numpy as np

from ml_common import LANGS, ROOT, load_keep, ml_results, load_topics, query_splits
from ml_analyze import VARIANTS, boot_mean
from ml_prefix_detect import corpus_texts


def toks(text):
    """Split on whitespace + strip leading/trailing punctuation; \\w is not used, so Telugu vowel signs are not treated as separators"""
    out = []
    for w in text.lower().split():
        w = "".join(ch for ch in w if not unicodedata.category(ch).startswith("P"))
        if w:
            out.append(w)
    return out


def lcsubstr(a, b):
    """Length of the longest common contiguous run of two word sequences"""
    best, prev = 0, [0] * (len(b) + 1)
    for x in a:
        cur = [0] * (len(b) + 1)
        for j, y in enumerate(b, 1):
            if x == y:
                cur[j] = prev[j - 1] + 1
                if cur[j] > best:
                    best = cur[j]
        prev = cur
    return best


class QueryLog:
    def __init__(self, queries, max_df=0.02, top=30):
        self.q = [t for t in (toks(x) for x in queries) if len(t) >= 3]
        df = Counter(w for t in self.q for w in set(t))
        lim = max(20, int(max_df * len(self.q)))
        self.post = defaultdict(list)
        for i, t in enumerate(self.q):
            for w in set(t):
                if df[w] <= lim:          # only rarer words are used for candidate recall; common function words are not indexed
                    self.post[w].append(i)
        self.top = top

    def score(self, text):
        p = toks(text)
        cnt = Counter(i for w in set(p) for i in self.post.get(w, ()))
        best = 0.0
        for i, _ in cnt.most_common(self.top):
            q = self.q[i]
            best = max(best, lcsubstr(q, p) / len(q))
            if best >= 1.0:
                break
        return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", nargs="+", default=LANGS)
    ap.add_argument("--feat", default="rel_knn10")
    ap.add_argument("--tau", type=float, default=0.8)
    ap.add_argument("--fpr", type=float, default=0.05)
    ap.add_argument("--size", default="full")
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--exclude", default="bad", choices=["none", "bad", "unsure"],
                    help="exclude bad questions by manual judgments: none = keep all; bad = drop bad; unsure = also drop unsure")
    ap.add_argument("--judgments", default=None, help="judgment file, default results/miracl/review_judgments.json")
    args = ap.parse_args()
    rng = np.random.default_rng(args.seed)
    S, BR = [], []

    for lang in args.lang:
        rd = ml_results(lang)
        paths = [os.path.join(rd, f) for f in ("poison.jsonl", "detect_feats.npz", "attack_detail.jsonl")]
        if not all(os.path.exists(p) for p in paths):
            print(f"[{lang}] missing result files, skipped")
            continue
        items = [json.loads(l) for l in open(paths[0])]
        z = np.load(paths[1])
        detail = [json.loads(l) for l in open(paths[2])]
        allq = {}
        for sp in query_splits(lang):
            allq.update(load_topics(lang, sp))
        keep, kst = load_keep(lang, items, args.exclude, args.judgments)
        # excl_target must remove all attacked questions (including bad ones) from the log; the same question often recurs under different qids
        # (e.g. yo questions 11/20, three sw questions on the height of Kilimanjaro), so removal is by qid and by tokenised text
        targets = {it["qid"] for it in items}
        target_txt = {tuple(toks(it["question"])) for it in items}
        excl = [t for q, t in allq.items() if q not in targets and tuple(toks(t)) not in target_txt]
        n_dup = sum(1 for q, t in allq.items() if q not in targets and tuple(toks(t)) in target_txt)
        logs = {"full": QueryLog(list(allq.values())), "excl_target": QueryLog(excl)}

        pos_clean = {r: i for i, r in enumerate(z["clean_rows"])}
        iso_r = -z[f"clean_{args.feat}"][[pos_clean[r] for r in z["rand"]]]
        rand_txt = corpus_texts(lang, z["rand"])
        gold_txt = corpus_texts(lang, z["gold"])
        print(f"[{lang}] query log {len(logs['full'].q)} entries ({len(logs['excl_target'].q)} after removing attack targets), "
              f"benign passages {len(rand_txt)}, gold {len(gold_txt)}; {n_dup} further duplicates removed by text; "
              f"exclusion {kst}, kept {sum(keep)}/{len(items)} questions", flush=True)

        for lg, log in logs.items():
            s_rand = np.array([log.score(t) for t in rand_txt])
            s_gold = np.array([log.score(t) for t in gold_txt])
            sig_r = s_rand >= args.tau
            base = float(sig_r.mean())
            budget = max(args.fpr - base, 0.0)
            thr_c = float(np.quantile(iso_r[~sig_r], 1 - budget / (~sig_r).mean())) if budget > 0 else np.inf
            fpr_c = float((sig_r | (iso_r > thr_c)).mean())
            thr_i = float(np.quantile(iso_r, 1 - max(args.fpr, fpr_c)))
            print(f"  [{lg}] s>={args.tau} false alarms: random benign {base:.3f}, gold {float((s_gold >= args.tau).mean()):.3f}; "
                  f"combined detector actual FPR {fpr_c:.3f}", flush=True)
            for v in VARIANTS:
                has_full = [j for j, it in enumerate(items) if it.get(f"{v}_adv")]   # aligned with the npz
                sel = [i for i, j in enumerate(has_full) if keep[j]]
                has = [has_full[i] for i in sel]
                if not has or f"{v}_bb_{args.feat}" not in z.files:
                    continue
                eff = {"none": {}, "iso": {}, "comb": {}}
                for form in ("bb", "adv"):
                    texts = [(f"{items[j]['question']} {items[j][f'{v}_adv'][0]}" if form == "bb" else items[j][f"{v}_adv"][0])
                             for j in has]
                    sp_ = np.array([log.score(t) for t in texts])
                    # attacker deletes the question mark: the feature strips punctuation so the score is unchanged; checked explicitly here
                    sp_noq = np.array([log.score(t.replace("?", "").replace("\uff1f", "")) for t in texts])
                    iso_p = -z[f"{v}_{form}_{args.feat}"][sel]
                    flag_q = sp_ >= args.tau
                    flag_c = flag_q | (iso_p > thr_c)
                    flag_i = iso_p > thr_i
                    hit = np.array([bool(detail[j][f"{args.size}/{v}/{form}/single/hit5"]) for j in has])
                    eff["none"][form] = hit.astype(float)
                    eff["iso"][form] = (hit & ~flag_i).astype(float)
                    eff["comb"][form] = (hit & ~flag_c).astype(float)
                    S.append({"lang": lang, "log": lg, "variant": v, "form": form, "n": len(has),
                              "s_mean": float(sp_.mean()), "flag_q": boot_mean(flag_q, args.boot, rng),
                              "flag_q_noqmark": float((sp_noq >= args.tau).mean()),
                              "fpr_rand": base, "fpr_gold": float((s_gold >= args.tau).mean()),
                              "flag_iso": boot_mean(flag_i, args.boot, rng), "flag_comb": boot_mean(flag_c, args.boot, rng),
                              "fpr_comb": fpr_c})
                n = len(has)

                def worst(e):
                    pt = max(e["bb"].mean(), e["adv"].mean())
                    bs = [max(e["bb"][idx].mean(), e["adv"][idx].mean()) for idx in
                          (rng.integers(0, n, n) for _ in range(args.boot))]
                    return float(pt), [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))], \
                        ("bb" if e["bb"].mean() >= e["adv"].mean() else "adv")
                BR.append({"lang": lang, "log": lg, "variant": v, "n": n, "fpr": fpr_c,
                           "none": worst(eff["none"]), "iso": worst(eff["iso"]), "comb": worst(eff["comb"])})

    f2 = lambda m: f"{m[0]:.2f} ({m[1][0]:.2f}–{m[1][1]:.2f})"
    L = [f"# Query-log overlap detection (s >= {args.tau}; isolation {args.feat}; target total FPR {args.fpr:.0%}; exclusion {args.exclude})", "",
         "## 1. The query-log signal itself", "",
         "| lang | log | variant | form | n | mean poison s | poison flagged | flagged after deleting ? | FPR: random benign | FPR: gold |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for r in S:
        L.append(f"| {r['lang']} | {r['log']} | {r['variant']} | {r['form']} | {r['n']} | {r['s_mean']:.2f} | {f2(r['flag_q'])} | "
                 f"{r['flag_q_noqmark']:.2f} | {r['fpr_rand']:.3f} | {r['fpr_gold']:.3f} |")
    L += ["", "Gold FPR = fraction of truly relevant passages that would be wrongly removed; this is the main cost of the signal.", "",
          "## 2. Surviving-poison rate under the attacker's best response (lower is better; outside brackets: attacker's best choice)", "",
          "| lang | log | variant | questions | actual FPR | no defense | isolation only | query log + isolation |", "|---|---|---|---|---|---|---|---|"]
    for r in BR:
        c = lambda x: f"{x[0]:.2f} ({x[1][0]:.2f}–{x[1][1]:.2f}) {x[2]}"
        L.append(f"| {r['lang']} | {r['log']} | {r['variant']} | {r['n']} | {r['fpr']:.3f} | {c(r['none'])} | {c(r['iso'])} | {c(r['comb'])} |")
    L += ["", "excl_target is the pessimistic setting: the attacked questions never appeared in the log. The gap between the two settings is what the attacker gains by targeting new questions."]
    out = os.path.join(ROOT, "results", "miracl")
    tag = "" if args.exclude == "none" else f"_excl-{args.exclude}"
    open(os.path.join(out, f"querylog_summary{tag}.md"), "w").write("\n".join(L) + "\n")
    json.dump({"signal": S, "best_response": BR, "args": vars(args)},
              open(os.path.join(out, f"querylog_summary{tag}.json"), "w"), indent=1, ensure_ascii=False)
    print("\n".join(L))
    print(f"\nsaved {out}/querylog_summary{tag}.md")


if __name__ == "__main__":
    main()