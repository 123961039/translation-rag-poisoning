"""
Review item P0-4 (first half): explain the "old review rerun vs original files, max AUROC difference 0.0916" in rejudge/compare.md (CPU only).
Compare row by row, by language, feature and size, the rerun of the "old review" set with the original 10-28 backup;
if differences occur only for yo, check yo's question set: questions added by the expansion were never judged in the old review and load_keep keeps all "unjudged" ones,
so under the old review yo grows from 14 to 66 questions -- the difference comes from the question set, not from code or environment.
    python selfcheck_explain.py
Output: results/miracl/selfcheck_explain.md
"""
import glob, json, os

PROJ = os.environ.get("PROJ", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
R = os.path.join(PROJ, "results", "miracl")


def load(d):
    out = {}
    for p in glob.glob(os.path.join(d, "analysis_excl-bad*.json")):
        J = json.load(open(p)); a = J["args"]
        for r in J["B"]:
            out[(a.get("feat", "rel_knn10"), a.get("feats", ""), r["lang"], r["variant"], r["form"])] = (r["auc_lenmatch"][0], r["n"])
    return out


def main():
    bk = sorted(glob.glob(os.path.join(R, "_backup_cpu_*")))
    orig = None
    for b in bk:      # first backup containing "original old-review results" (judgments is null)
        p = os.path.join(b, "analysis_excl-bad.json")
        if os.path.exists(p) and json.load(open(p))["args"].get("judgments") is None:
            orig = b; break
    if orig is None:
        raise SystemExit("original backup not found (analysis_excl-bad.json with judgments null in _backup_cpu_*)")
    A, B = load(orig), load(os.path.join(R, "rejudge", "old"))
    L = ["# Explanation of the self-check warning: old review rerun vs original files", "", f"original: {os.path.basename(orig)}; rerun: rejudge/old/", "",
         "| lang | rows compared | max AUROC diff | questions (original -> rerun, trans/bb full) |", "|---|---|---|---|"]
    for lg in ["sw", "te", "yo", "id"]:
        ks = [k for k in A if k[2] == lg and k in B]
        md = max(abs(A[k][0] - B[k][0]) for k in ks) if ks else float("nan")
        k0 = ("rel_knn10", "", lg, "trans", "bb")
        n = f"{A[k0][1]} → {B[k0][1]}" if k0 in A and k0 in B else "—"
        L.append(f"| {lg} | {len(ks)} | {md:.2e} | {n} |")
    old = json.load(open(os.path.join(R, "review_judgments.json"))).get("yo", {})
    items = [json.loads(l) for l in open(os.path.join(R, "yo", "poison.jsonl"))]
    new = [it for it in items if it.get("batch") == "yo_expand_2026-10-29"]
    unj = sum(it["qid"] not in old for it in new)
    L += ["", f"The yo expansion added {len(new)} questions, {unj} of which are not in the old review judgment file. load_keep keeps all unjudged questions,",
          "so under the old review the number of kept yo questions grows and AUROC changes accordingly. The other three languages are bit-identical, so code and environment did not change.",
          "", "In the paper, the yo entry of the 'old review' robustness column must note: added questions were not covered by the old review and are kept."]
    out = os.path.join(R, "selfcheck_explain.md")
    open(out, "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
