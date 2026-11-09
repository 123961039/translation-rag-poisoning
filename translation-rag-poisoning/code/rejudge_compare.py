"""
Put the results of the three question-judgment sets (native speakers / old first-pass review / none = no exclusion) side by side to see which conclusions change. CPU only.
Input:  results/miracl/rejudge/<set>/   (output of rejudge_cpu.sh, rejudge_asr.sh)
Output: results/miracl/rejudge/compare.md
    python rejudge_compare.py
Also a self-check: AUROCs of the rerun old set should match the original files (in _backup_cpu_*); a mismatch means the environment or code changed.
"""
import glob, itertools, json, os, sys

PROJ = os.environ.get("PROJ", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
R = os.path.join(PROJ, "results", "miracl")
RJ = os.path.join(R, "rejudge")
SETS = ["native", "old", "none"]
NAME = {"native": "native", "old": "old review", "none": "no exclusion"}
LANGS = ["sw", "te", "yo", "id"]
SIZES = [("", "full"), ("_sub131924", "131,924"), ("_sub45000", "45,000")]
FEATS = ["rel_knn10", "knn10"]
V, F = "trans", "bb"          # main comparison


def load_analysis(d, feat, feats):
    """Locate by the args recorded inside the file, not by its name"""
    for p in sorted(glob.glob(os.path.join(d, "analysis_excl-bad*.json"))):
        try:
            J = json.load(open(p))
        except Exception:
            continue
        a = J.get("args", {})
        if a.get("feat", "rel_knn10") == feat and a.get("feats", "") == feats:
            return J
    return None


def row(rows, lang, v=V, f=F):
    for r in rows or []:
        if r["lang"] == lang and r["variant"] == v and r["form"] == f:
            return r
    return None


def f3(x):
    return "—" if x is None else f"{x:.3f}"


def f2ci(m):
    return "—" if m is None else f"{m[0]:.2f} ({m[1][0]:.2f}–{m[1][1]:.2f})"


def rank(x):
    o = sorted(range(len(x)), key=lambda i: x[i]); r = [0.0] * len(x); i = 0
    while i < len(o):
        j = i
        while j + 1 < len(o) and x[o[j + 1]] == x[o[i]]:
            j += 1
        for k in range(i, j + 1):
            r[o[k]] = (i + j) / 2
        i = j + 1
    return r


def spearman(x, y):
    a, b = rank(x), rank(y); n = len(a); ma, mb = sum(a) / n, sum(b) / n
    c = sum((p - ma) * (q - mb) for p, q in zip(a, b))
    s = (sum((p - ma) ** 2 for p in a) * sum((q - mb) ** 2 for q in b)) ** 0.5
    return c / s if s else float("nan")


def perm_p(x, y):
    """Exact permutation test, two-sided"""
    r0 = abs(spearman(x, y)); ps = list(itertools.permutations(y))
    return sum(abs(spearman(x, list(p))) >= r0 - 1e-12 for p in ps) / len(ps)


def main():
    have = [s for s in SETS if os.path.isdir(os.path.join(RJ, s))]
    if not have:
        sys.exit(f"no native / old / none directory under {RJ}; run rejudge_cpu.sh first")
    A = {(s, ft, sz): load_analysis(os.path.join(RJ, s), ft, sz) for s in have for ft in FEATS for sz, _ in SIZES}
    L = [f"# Results under three question-judgment sets ({', '.join(NAME[s] for s in have)})", "",
         f"Main comparison {V}/{F}. All analyses use --exclude bad; 'no exclusion' = empty judgment file.", ""]

    # ---- 0. question counts
    L += ["## 0. Questions kept by each judgment set (detection table B, trans/bb)", "", "| judgments | " + " | ".join(LANGS) + " |",
          "|---|" + "---|" * len(LANGS)]
    for s in have:
        rs = (A[(s, "rel_knn10", "")] or {}).get("B")
        L.append(f"| {NAME[s]} | " + " | ".join(str((row(rs, l) or {}).get("n", "—")) for l in LANGS) + " |")

    # ---- 1. scale control AUROC
    corpus = {}
    for s in have:
        for ft in FEATS:
            p = os.path.join(RJ, s, f"scale_control_{ft}.json")
            if os.path.exists(p) and not corpus:
                corpus = json.load(open(p)).get("corpus", {})
    for ft in FEATS:
        L += ["", f"## 1. Scale control: AUROC (vs length-matched), feature {ft}", "",
              "| lang | judgments | " + " | ".join(n for _, n in SIZES) + " | d(45k-full) |", "|---|---|" + "---|" * (len(SIZES) + 1)]
        for l in LANGS:
            for s in have:
                v = [(row((A[(s, ft, sz)] or {}).get("B"), l) or {}).get("auc_lenmatch", [None])[0] for sz, _ in SIZES]
                d = None if None in (v[0], v[-1]) else v[-1] - v[0]
                L.append(f"| {l} | {NAME[s]} | " + " | ".join(f3(x) for x in v) + f" | {f3(d)} |")
        if corpus:
            L += ["", "Spearman rho between endpoint dAUROC and shrink factor (full / 45k actual passages) (n=4, exact permutation two-sided p):", ""]
            for s in have:
                xs, ys = [], []
                for l in LANGS:
                    a0 = (row((A[(s, ft, "")] or {}).get("B"), l) or {}).get("auc_lenmatch", [None])[0]
                    a1 = (row((A[(s, ft, "_sub45000")] or {}).get("B"), l) or {}).get("auc_lenmatch", [None])[0]
                    if a0 is None or a1 is None:
                        continue
                    xs.append(corpus[""][l] / corpus["_sub45000"][l]); ys.append(a1 - a0)
                if len(xs) == 4:
                    L.append(f"- {NAME[s]}: rho = {spearman(xs, ys):+.3f}, p = {perm_p(xs, ys):.3f}")

    # ---- 2. surviving-poison rate after filtering
    for ft in FEATS:
        L += ["", f"## 2. Surviving-poison rate after filtering at 5% FPR, feature {ft}", "",
              "| lang | judgments | shared questions | full | 45,000 |", "|---|---|---|---|---|"]
        for l in LANGS:
            for s in have:
                c0 = row((A[(s, ft, "")] or {}).get("C"), l)
                c1 = row((A[(s, ft, "_sub45000")] or {}).get("C"), l)
                L.append(f"| {l} | {NAME[s]} | {(c0 or {}).get('n_common', '—')} | "
                         f"{f2ci((c0 or {}).get('hit_and_unflagged'))} | {f2ci((c1 or {}).get('hit_and_unflagged'))} |")
        L += ["", "Ranking at 45k (higher = more dangerous):", ""]
        for s in have:
            vals = [(l, (row((A[(s, ft, "_sub45000")] or {}).get("C"), l) or {}).get("hit_and_unflagged", [None])[0]) for l in LANGS]
            vals = [x for x in vals if x[1] is not None]
            L.append(f"- {NAME[s]}: " + " > ".join(f"{l} {v:.2f}" for l, v in sorted(vals, key=lambda t: -t[1])))

    # ---- 3. feature preference
    L += ["", "## 3. Feature preference: rows where rel_knn10 AUROC exceeds knn10 (3 variants x 2 forms per language)", "",
          "| size | judgments | " + " | ".join(LANGS) + " |", "|---|---|" + "---|" * len(LANGS)]
    for sz, nm in [("", "full"), ("_sub45000", "45,000")]:
        for s in have:
            cells = []
            for l in LANGS:
                ra, rb = (A[(s, "rel_knn10", sz)] or {}).get("B"), (A[(s, "knn10", sz)] or {}).get("B")
                pairs = [(row(ra, l, v, f), row(rb, l, v, f)) for v in ("native", "trans", "en") for f in ("bb", "adv")]
                pairs = [(a, b) for a, b in pairs if a and b]
                win = sum(a["auc_lenmatch"][0] > b["auc_lenmatch"][0] for a, b in pairs)
                cells.append(f"{win}/{len(pairs)}" if pairs else "—")
            L.append(f"| {nm} | {NAME[s]} | " + " | ".join(cells) + " |")

    # ---- 4. ASR
    asr = {}
    for s in have:
        p = os.path.join(RJ, s, "asr_summary_excl-bad.json")
        if os.path.exists(p):
            asr[s] = {(r["lang"], r["cond"], r["variant"], r["form"]): r for r in json.load(open(p))["rows"]}
    if asr:
        L += ["", "## 4. Generation-level ASR", ""]
        for v in ("trans", "en", "native"):
            L += [f"### {v}/{F}", "", "| lang | judgments | questions | clean accuracy | attacked ASR | defended ASR (realistic) | recovered |",
                  "|---|---|---|---|---|---|---|"]
            for l in LANGS:
                for s in asr:
                    c, a, d = (asr[s].get((l, "clean", "-", "-")), asr[s].get((l, "attacked", v, F)),
                               asr[s].get((l, "defended", v, F)))
                    if not a:
                        continue
                    rec = "—" if not d or a["ASR"][0] == 0 else f"{1 - d['ASR'][0] / a['ASR'][0]:.0%}"
                    L.append(f"| {l} | {NAME[s]} | {a['n']} | {f2ci(c['acc']) if c else '—'} | {f2ci(a['ASR'])} | "
                             f"{f2ci(d['ASR']) if d else '—'} | {rec} |")
            L.append("")
        fp = {s: json.load(open(os.path.join(RJ, s, "asr_summary_excl-bad.json"))).get("fp_stats", {}) for s in asr}
        L += ["### Cost of false alarms (gold wrongly removed)", "", "| lang | " + " | ".join(NAME[s] for s in asr) + " |",
              "|---|" + "---|" * len(asr)]
        for l in LANGS:
            L.append(f"| {l} | " + " | ".join(
                f"{fp[s][l]['gold_flagged']}/{fp[s][l]['gold_in_topk']}" if l in fp[s] else "—" for s in asr) + " |")
    else:
        L += ["", "## 4. Generation-level ASR", "", "(no ASR results yet: run rejudge_asr.sh, then this script)"]

    # ---- 5. self-check: rerun old set vs original files
    bks = sorted(glob.glob(os.path.join(R, "_backup_cpu_*")))
    if "old" in have and bks:
        worst, n = 0.0, 0
        for ft in FEATS:
            for sz, _ in SIZES:
                new = A[("old", ft, sz)]; orig = load_analysis(bks[0], ft, sz)
                if not (new and orig):
                    continue
                for r in orig["B"]:
                    m = row(new["B"], r["lang"], r["variant"], r["form"])
                    if m:
                        worst = max(worst, abs(m["auc_lenmatch"][0] - r["auc_lenmatch"][0])); n += 1
        ok = "consistent" if worst < 1e-9 else "WARNING: inconsistent, investigate before using the new results"
        L += ["", "## 5. Self-check", "", f"old review set rerun vs original files ({os.path.basename(bks[0])}): {n} AUROC rows compared, "
              f"max difference {worst:.2e} -> {ok}"]

    L += ["", "Other outputs (metric_gap, rel_diag, prefix, querylog) are in each set's directory with the original file names; "
          "scale_control is split by feature into scale_control_rel_knn10.* / scale_control_knn10.*."]
    out = os.path.join(RJ, "compare.md")
    open(out, "w").write("\n".join(L) + "\n")
    print("\n".join(L)); print(f"\nsaved {out}")


if __name__ == "__main__":
    main()
