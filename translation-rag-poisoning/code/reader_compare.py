"""
Generation-level ASR across reader models (CPU only). Reads asr_summary_excl-bad.json of each ASR run and lays them out side by side.
    python reader_compare.py
Three runs are compared by default (only those present are listed):
  Qwen3-14B, original prompt          results/miracl/rejudge/native/        (main results)
  Qwen3-14B, unknown sentence removed  results/miracl/reader_qwen3_14b_no_unknown/
  Qwen2.5-7B, unknown sentence removed results/miracl/reader_qwen2_5_7b_instruct_awq_no_unknown/
Cross-model conclusions use the last two runs (same prompt); the difference between the first and second = effect of changing only the prompt.
Output: results/miracl/reader_compare.md
"""
import json, os

PROJ = os.environ.get("PROJ", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
R = os.path.join(PROJ, "results", "miracl")
RUNS = [("Qwen3-14B, orig prompt", os.path.join(R, "rejudge", "native")),
        ("Qwen3-14B, no-unknown", os.path.join(R, "reader_qwen3_14b_no_unknown")),
        ("Qwen2.5-7B, no-unknown", os.path.join(R, "reader_qwen2_5_7b_instruct_awq_no_unknown"))]
LANGS = ["sw", "te", "yo", "id"]


def main():
    data = {}
    for name, d in RUNS:
        p = os.path.join(d, "asr_summary_excl-bad.json")
        if os.path.exists(p):
            J = json.load(open(p))
            data[name] = ({(r["lang"], r["cond"], r["variant"], r["form"]): r for r in J["rows"]}, J.get("fp_stats", {}))
    if not data:
        raise SystemExit("no results found")
    names = list(data)
    f2 = lambda m: f"{m[0]:.2f}"
    L = [f"# Generation-level ASR across reader models (native-validated questions, top-5, defense rel_knn10 @ 5% FPR)", "",
         "Each cell: models in order " + "; ".join(names) + ". Cross-model conclusions use only the two runs with the same prompt.", "",
         "## clean: accuracy / unknown rate", "", "| lang | questions | " + " | ".join(names) + " |", "|---|---|" + "---|" * len(names)]
    for l in LANGS:
        cells, n = [], "—"
        for nm in names:
            r = data[nm][0].get((l, "clean", "-", "-"))
            cells.append(f"{f2(r['acc'])} / {r['unknown']:.2f}" if r else "—")
            n = r["n"] if r else n
        L.append(f"| {l} | {n} | " + " | ".join(cells) + " |")
    for v in ("trans", "en", "native"):
        L += ["", f"## {v}/bb: attacked ASR -> ASR under realistic defense (fraction recovered)", "", "| lang | questions | " + " | ".join(names) + " |",
              "|---|---|" + "---|" * len(names)]
        for l in LANGS:
            cells, n = [], "—"
            for nm in names:
                a = data[nm][0].get((l, "attacked", v, "bb")); d = data[nm][0].get((l, "defended", v, "bb"))
                if not (a and d):
                    cells.append("—"); continue
                n = a["n"]
                rec = "—" if a["ASR"][0] == 0 else f"{1 - d['ASR'][0] / a['ASR'][0]:.0%}"
                cells.append(f"{a['ASR'][0]:.2f} ({a['ASR'][1][0]:.2f}-{a['ASR'][1][1]:.2f}) -> {d['ASR'][0]:.2f} ({rec})")
            L.append(f"| {l} | {n} | " + " | ".join(cells) + " |")
    L += ["", "## Utility cost of the defense: clean accuracy -> clean_defended accuracy", "", "| lang | " + " | ".join(names) + " |",
          "|---|" + "---|" * len(names)]
    for l in LANGS:
        cells = []
        for nm in names:
            c = data[nm][0].get((l, "clean", "-", "-")); cd = data[nm][0].get((l, "clean_defended", "-", "-"))
            cells.append(f"{f2(c['acc'])} → {f2(cd['acc'])}" if c and cd else "—")
        L.append(f"| {l} | " + " | ".join(cells) + " |")
    L += ["", "Note: which passages the defense removes depends only on retrieval and isolation features, not on the reader, so 'false alarms / gold wrongly removed' are identical across models.",
          "yo has 26 questions (including the expansion); CIs are wide, do not interpret differences within 0.1."]
    out = os.path.join(R, "reader_compare.md")
    open(out, "w").write("\n".join(L) + "\n")
    print("\n".join(L)); print(f"\nsaved {out}")


if __name__ == "__main__":
    main()
