"""
Paired comparison of generation-level ASR, full corpus vs 45k (CPU only).
  full: results/miracl/rejudge/native/asr_answers_excl-bad.jsonl
  45k : results/miracl/asr_scale_sub45000/asr_answers_excl-bad.jsonl
Same questions paired, exact McNemar; additionally restricted to questions answered correctly (clean) at both sizes, to exclude questions that became unanswerable on the smaller corpus.
    python asr_scale_compare.py
Output: results/miracl/asr_scale_compare.md
"""
import json, math, os

import numpy as np

PROJ = os.environ.get("PROJ", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
R = os.path.join(PROJ, "results", "miracl")
LANGS = ["sw", "te", "yo", "id"]


def mcnemar(b, c):
    n = b + c
    return 1.0 if n == 0 else min(1.0, 2 * sum(math.comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n)


def load(p):
    return {(r["lang"], r["cond"], r["variant"], r["form"], r["qid"]): r for r in map(json.loads, open(p))}


def main():
    F = load(os.path.join(R, "rejudge", "native", "asr_answers_excl-bad.jsonl"))
    S = load(os.path.join(R, "asr_scale_sub45000", "asr_answers_excl-bad.jsonl"))
    asr = lambda r: bool(r["hit_target"]) and not r["hit_correct"]
    L = ["# Effect of corpus size on generation-level ASR (Qwen3-14B, native-speaker judgments, full vs 45k, paired by question)", "",
         "45k is identical to ml_detect --subsample 45000 (seed 0, all dev gold passages kept); defense features use the matching size.", "",
         "| lang | variant | condition | questions | full ASR | 45k ASR | 45k higher / lower (questions) | p | clean correct at both sizes: questions / full / 45k |",
         "|---|---|---|---|---|---|---|---|---|"]
    for v in ("trans", "native", "en"):
        for lg in LANGS:
            okF = {k[4] for k, r in F.items() if k[0] == lg and k[1] == "clean" and r["hit_correct"]}
            okS = {k[4] for k, r in S.items() if k[0] == lg and k[1] == "clean" and r["hit_correct"]}
            for cond in ("attacked", "defended"):
                ks = [k for k in F if k[0] == lg and k[1] == cond and k[2] == v and k[3] == "bb" and k in S]
                if not ks:
                    continue
                x = np.array([asr(F[k]) for k in ks]); y = np.array([asr(S[k]) for k in ks])
                b, c = int((y & ~x).sum()), int((x & ~y).sum())
                both = [k for k in ks if k[4] in okF and k[4] in okS]
                cb = f"{len(both)} / {np.mean([asr(F[k]) for k in both]):.2f} / {np.mean([asr(S[k]) for k in both]):.2f}" if both else "—"
                L.append(f"| {lg} | {v} | {cond} | {len(ks)} | {x.mean():.2f} | {y.mean():.2f} | {b} / {c} | {mcnemar(b, c):.3f} | {cb} |")
    L += ["", "## Clean accuracy (does shrinking the corpus make questions unanswerable?)", "", "| lang | full | 45k |", "|---|---|---|"]
    for lg in LANGS:
        cf = [r["hit_correct"] for k, r in F.items() if k[0] == lg and k[1] == "clean"]
        cs = [r["hit_correct"] for k, r in S.items() if k[0] == lg and k[1] == "clean"]
        if cf and cs:
            L.append(f"| {lg} | {np.mean(cf):.2f} | {np.mean(cs):.2f} |")
    L += ["", "Note: the 45k version keeps all dev gold passages (as in the scale experiments), so clean accuracy should not drop much;",
          "changes in ASR mainly reflect weaker detection (defended) and changed retrieval ranking (attacked)."]
    out = os.path.join(R, "asr_scale_compare.md")
    open(out, "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
