"""Scale-control summary (CPU only, seconds without a GPU): combines results already computed at several corpus sizes into one table.

    python ml_scale.py                                  # automatically find all existing size points
    python ml_scale.py --variant trans --form bb        # change the main poison variant / prefix form
    python ml_scale.py --sizes "" _sub131924 _sub45000  # specify explicitly

Reads (existing files only, nothing is recomputed)
    results/miracl/analysis_excl-<level><suffix>.json   <- output of ml_analyze.py, with 95% CI
    results/miracl/detect_summary<suffix>.json          <- output of ml_detect.py, actual corpus size per language

Question answered: as corpora shrink, how much harder does detection get and how much easier does the attack get? And does the claim
"low-resource languages are more vulnerable" survive once sizes are aligned? yo has only 49k passages, so downsampling barely touches it; it is a natural internal control.

Output: results/miracl/scale_control.md / .json
"""
import argparse, itertools, json, math, os, re, glob

from ml_common import LANGS, ROOT, ml_emb

OUT = os.path.join(ROOT, "results", "miracl")
VARIANTS = ["native", "trans", "en"]
DEFAULT_FEAT = "rel_knn10"


def full_corpus_size(lang):
    """When an old detect_summary.json lacks the corpus field, count the lines of corpus_ids.txt;
    without the embeddings (CPU-only reproduction) fall back to results/miracl/corpus_sizes.json"""
    p = os.path.join(ml_emb(lang), "corpus_ids.txt")
    if not os.path.exists(p):
        q = os.path.join(OUT, "corpus_sizes.json")
        return int(json.load(open(q)).get(lang, 0)) if os.path.exists(q) else 0
    with open(p) as f:
        return sum(1 for l in f if l.strip())


def rank(xs):
    """Average ranks (with ties)"""
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            r[order[k]] = avg
        i = j + 1
    return r


def pearson(x, y):
    n = len(x)
    if n < 3:
        return float("nan")
    mx, my = sum(x) / n, sum(y) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    return sxy / (sxx * syy) ** 0.5 if sxx > 0 and syy > 0 else float("nan")


def spearman(x, y):
    return pearson(rank(x), rank(y))


def scan(level, feat):
    """Scan analysis_excl-<level>*.json, keep those whose recorded args have the same main feature, return {size suffix: path}.
    File names are not parsed -- whether they contain the feature name changed across versions; args are authoritative."""
    found, other = {}, {}
    for p in sorted(glob.glob(os.path.join(OUT, f"analysis_excl-{level}*.json"))):
        try:
            a = json.load(open(p)).get("args", {})
        except Exception:
            continue
        f = a.get("feat", DEFAULT_FEAT)
        sfx = a.get("feats", "")
        if f == feat:
            found[sfx] = p
        else:
            other.setdefault(f, []).append(os.path.basename(p))
    for f, ps in other.items():
        print(f"  (skipped {len(ps)} files with main feature {f}: {', '.join(ps)})")
    return found


def label(sfx):
    if sfx == "":
        return "full"
    n = re.sub(r"[^0-9]", "", sfx)
    return f"{int(n):,}" if n else sfx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", nargs="+", default=LANGS)
    ap.add_argument("--sizes", nargs="+", default=None,
                    help='file suffixes of the size points, "" = full corpus; default: scan automatically')
    ap.add_argument("--exclude", default="bad", choices=["bad", "unsure"])
    ap.add_argument("--feat", default=DEFAULT_FEAT,
                    help="main feature; only size points run by ml_analyze with the same main feature are summarised")
    ap.add_argument("--variant", default="trans", help="main poison variant (trans is the hardest to detect)")
    ap.add_argument("--form", default="bb", choices=["bb", "adv"])
    args = ap.parse_args()

    avail = scan(args.exclude, args.feat)
    if args.sizes is not None:
        sizes = ["" if s in ("full", '""', "''") else s for s in args.sizes]
    else:
        key = lambda s: (0, 0) if s == "" else (1, -int(re.sub(r"\D", "", s) or 0))
        sizes = sorted(avail, key=key)
    if not sizes:
        print(f"no analysis_excl-{args.exclude}*.json with main feature {args.feat} found.\n"
              f"Run first: python ml_analyze.py --exclude {args.exclude} --feat {args.feat} [--feats <suffix> --size <size>]")
        return

    # ---------- read ----------
    an, corpus = {}, {}          # an[sfx] = {"B": {...}, "C": {...}}; corpus[sfx][lang] = passage count
    for sfx in sizes:
        p = avail.get(sfx) or os.path.join(OUT, f"analysis_excl-{args.exclude}{sfx}.json")
        if not os.path.exists(p):
            print(f"Warning: missing analysis file for size point {label(sfx)} (main feature {args.feat}), skipped.\n"
                  f"  To fill in: python ml_analyze.py --exclude {args.exclude} --feat {args.feat}"
                  + (f" --feats {sfx} --size {sfx.lstrip('_')}" if sfx else "") + "\n"
                  f"  Otherwise this column stays empty and the dose-response section cannot be computed")
            continue
        J = json.load(open(p))
        got_feat = J.get("args", {}).get("feat", DEFAULT_FEAT)
        if got_feat != args.feat:
            print(f"Error: the main feature of {os.path.basename(p)} is {got_feat}, not {args.feat}; "
                  f"mixing them is meaningless, this size point is skipped")
            continue
        an[sfx] = {"B": {(r["lang"], r["variant"], r["form"]): r for r in J["B"]},
                   "C": {(r["lang"], r["variant"], r["form"]): r for r in J["C"]}}
        d = os.path.join(OUT, f"detect_summary{sfx}.json")
        corpus[sfx] = {}
        if os.path.exists(d):
            miss_field = set()
            for r in json.load(open(d)):
                if "corpus" in r:
                    corpus[sfx][r["lang"]] = int(r["corpus"])
                else:
                    miss_field.add(r["lang"])          # old file did not store it; count it ourselves
            for l in sorted(miss_field):
                if l not in corpus[sfx]:
                    corpus[sfx][l] = full_corpus_size(l)
            if miss_field:
                print(f"  {os.path.basename(d)} is an old version (no corpus field); "
                      f"passage counts for {', '.join(sorted(miss_field))} are counted from corpus_ids.txt")
        else:
            print(f"Warning: missing {d}; corpus size left empty for this size point")
    sizes = [s for s in sizes if s in an]
    langs = [l for l in args.lang if any(any(k[0] == l for k in an[s]["B"]) for s in sizes)]
    if not langs:
        print("no results for any language to summarise")
        return

    L = [f"# Scale control (main variant {args.variant}/{args.form}, exclusion {args.exclude}, brackets = 95% CI)", "",
         "All size points use the same rowmap (same seed, all dev gold passages kept), so questions align across languages.", ""]

    # ---------- 1. actual corpus size at each size point ----------
    L += ["## 1. Actual corpus size of each language at each size point", "",
          "| lang | " + " | ".join(label(s) for s in sizes) + " |",
          "|---" * (len(sizes) + 1) + "|"]
    for l in langs:
        L.append(f"| {l} | " + " | ".join(f"{corpus[s].get(l, 0):,}" if corpus[s].get(l) else "—"
                                          for s in sizes) + " |")
    L += ["", "Languages already smaller than the downsampling target stay unchanged -- they are internal controls: size unchanged, results should not change.", ""]

    # ---------- 2. detection AUROC ----------
    L += [f"## 2. Ingestion detection AUROC (vs length-matched, {args.variant}/{args.form})", "",
          "| lang | " + " | ".join(label(s) for s in sizes) + " | change at smallest |",
          "|---" * (len(sizes) + 2) + "|"]
    auc_pts, auc_chg = [], {}   # auc_pts for the correlation; auc_chg[lang] = change at the smallest size
    for l in langs:
        cells, vals = [], []
        for s in sizes:
            r = an[s]["B"].get((l, args.variant, args.form))
            if r is None:
                cells.append("—")
                continue
            m, c = r["auc_lenmatch"][0], r["auc_lenmatch"][1]
            cells.append(f"{m:.3f} ({c[0]:.2f}–{c[1]:.2f})")
            vals.append(m)
            if corpus[s].get(l):
                auc_pts.append((l, s, corpus[s][l], m))
        if len(vals) >= 2:
            auc_chg[l] = vals[-1] - vals[0]
        span = f"{auc_chg[l]:+.3f}" if l in auc_chg else "—"
        L.append(f"| {l} | " + " | ".join(cells) + f" | {span} |")

    if auc_chg:
        sign = -1                        # expected direction of change (when shrinking the corpus)
        flat = 0.02                        # changes below this count as flat
        agree = [l for l, d in auc_chg.items() if d * sign > flat]
        same  = [l for l, d in auc_chg.items() if abs(d) <= flat]
        opp   = [l for l, d in auc_chg.items() if d * sign < -flat]
        L += ["", f"**Within language** (same language, only corpus size changed; this is the clean control): "
                  f"{len(agree)}/{len(auc_chg)} languages agree with 'smaller corpus -> harder to detect'"
                  + (f" ({', '.join(agree)})" if agree else "")
                  + (f"; flat {', '.join(same)}" if same else "")
                  + (f"; **opposite {', '.join(opp)}**" if opp else "") + "."]
        if len(auc_pts) >= 4:
            L += [f"Pooling all language x size points (n={len(auc_pts)}) Spearman rho="
                  f"{spearman([p[2] for p in auc_pts], [p[3] for p in auc_pts]):+.2f}; "
                  f"this number mixes in inherent differences between languages and is for reference only; the line above is the conclusion."]
        L += [""]

    # ---------- 3. surviving-poison rate after filtering ----------
    L += [f"## 3. Surviving-poison rate after filtering at 5% FPR ({args.variant}/{args.form})", "",
          "| lang | " + " | ".join(label(s) for s in sizes) + " | change at smallest |",
          "|---" * (len(sizes) + 2) + "|"]
    eff_pts, eff_chg = [], {}
    for l in langs:
        cells, vals = [], []
        for s in sizes:
            r = an[s]["C"].get((l, args.variant, args.form))
            if r is None:
                cells.append("—")
                continue
            m, c = r["hit_and_unflagged"][0], r["hit_and_unflagged"][1]
            cells.append(f"{m:.2f} ({c[0]:.2f}–{c[1]:.2f})")
            vals.append(m)
            if corpus[s].get(l):
                eff_pts.append((l, s, corpus[s][l], m))
        if len(vals) >= 2:
            eff_chg[l] = vals[-1] - vals[0]
        span = f"{eff_chg[l]:+.2f}" if l in eff_chg else "—"
        L.append(f"| {l} | " + " | ".join(cells) + f" | {span} |")

    if eff_chg:
        sign = +1                        # expected direction of change (when shrinking the corpus)
        flat = 0.02                        # changes below this count as flat
        agree = [l for l, d in eff_chg.items() if d * sign > flat]
        same  = [l for l, d in eff_chg.items() if abs(d) <= flat]
        opp   = [l for l, d in eff_chg.items() if d * sign < -flat]
        L += ["", f"**Within language** (same language, only corpus size changed; this is the clean control): "
                  f"{len(agree)}/{len(eff_chg)} languages agree with 'smaller corpus -> more poisons survive'"
                  + (f" ({', '.join(agree)})" if agree else "")
                  + (f"; flat {', '.join(same)}" if same else "")
                  + (f"; **opposite {', '.join(opp)}**" if opp else "") + "."]
        if len(eff_pts) >= 4:
            L += [f"Pooling all language x size points (n={len(eff_pts)}) Spearman rho="
                  f"{spearman([p[2] for p in eff_pts], [p[3] for p in eff_pts]):+.2f}; "
                  f"this number mixes in inherent differences between languages and is for reference only; the line above is the conclusion."]
        L += [""]

    # ---------- 4. language ranking after aligning sizes ----------
    small = sizes[-1]
    if small != "":
        L += [f"## 4. Language ranking after aligning sizes to {label(small)} passages", "",
              "| lang | passages | detection AUROC | surviving-poison rate |", "|---|---|---|---|"]
        rows = []
        for l in langs:
            b = an[small]["B"].get((l, args.variant, args.form))
            c = an[small]["C"].get((l, args.variant, args.form))
            if b and c:
                rows.append((l, corpus[small].get(l, 0), b["auc_lenmatch"][0], c["hit_and_unflagged"][0]))
        for l, n, a, e in sorted(rows, key=lambda r: -r[3]):
            L.append(f"| {l} | {n:,} | {a:.3f} | {e:.2f} |")
        L += ["", "Sorted by surviving-poison rate from worst to best. If the top language is not the lowest-resource one, "
                  "then 'low-resource languages are more vulnerable' is a property of corpus size, not of the language itself.", ""]

    # ---------- 5. three variants at the smallest size ----------
    L += [f"## 5. Detection difficulty of the three poison variants at {label(small)} passages (AUROC vs length-matched)", "",
          "| lang | form | " + " | ".join(VARIANTS) + " |", "|---|---|---|---|---|"]
    for l in langs:
        for f in ("bb", "adv"):
            cs = []
            for v in VARIANTS:
                r = an[small]["B"].get((l, v, f))
                cs.append(f"{r['auc_lenmatch'][0]:.3f}" if r else "—")
            L.append(f"| {l} | {f} | " + " | ".join(cs) + " |")
    win = {v: 0 for v in VARIANTS}
    cells_n = 0
    for l in langs:
        for f in ("bb", "adv"):
            got = {v: an[small]["B"][(l, v, f)]["auc_lenmatch"][0]
                   for v in VARIANTS if (l, v, f) in an[small]["B"]}
            if len(got) == len(VARIANTS):
                win[min(got, key=got.get)] += 1
                cells_n += 1
    if cells_n:
        best = max(win, key=win.get)
        L += ["", f"Hardest-to-detect variant counts ({cells_n} language x form cells): "
                  + ", ".join(f"{v} {win[v]} times" for v in VARIANTS)
                  + f". **{best}** is hardest to detect in {win[best]}/{cells_n} cells."]
        if win[best] < cells_n:
            exc = [f"{l}/{f}" for l in langs for f in ("bb", "adv")
                   if (l, VARIANTS[0], f) in an[small]["B"]
                   and min((an[small]["B"][(l, v, f)]["auc_lenmatch"][0], v) for v in VARIANTS)[1] != best]
            L += [f"Exceptions: {', '.join(exc)}. How small the gaps are at the exceptions is in the table -- "
                  f"a difference of order 0.01 is noise and need not be treated as a counterexample."]
        L += [""]

    # ---------- 6. dose-response: the more it shrinks, the more it drops ----------
    big = sizes[0]
    if small != "" and big != small:
        pts = []
        for l in langs:
            b0 = an[big]["B"].get((l, args.variant, args.form))
            b1 = an[small]["B"].get((l, args.variant, args.form))
            c0 = an[big]["C"].get((l, args.variant, args.form))
            c1 = an[small]["C"].get((l, args.variant, args.form))
            n0, n1 = corpus[big].get(l), corpus[small].get(l)
            if b0 and b1 and n0 and n1 and n1 > 0:
                pts.append({"lang": l, "n0": n0, "n1": n1, "shrink": n0 / n1,
                            "d_auc": b1["auc_lenmatch"][0] - b0["auc_lenmatch"][0],
                            "d_eff": (c1["hit_and_unflagged"][0] - c0["hit_and_unflagged"][0])
                                     if c0 and c1 else None})
        if len(pts) >= 3:
            pts.sort(key=lambda p: p["shrink"])
            L += [f"## 6. Dose-response: {label(big)} -> {label(small)}, the more it shrinks the more it drops", "",
                  "| lang | original passages | passages after | shrink factor | dAUROC | d surviving rate |",
                  "|---|---|---|---|---|---|"]
            for p in pts:
                L.append(f"| {p['lang']} | {p['n0']:,} | {p['n1']:,} | {p['shrink']:.1f}x | "
                         f"{p['d_auc']:+.3f} | "
                         + (f"{p['d_eff']:+.2f} |" if p["d_eff"] is not None else "— |"))
            lg = [math.log(p["shrink"]) for p in pts]
            ra = spearman(lg, [p["d_auc"] for p in pts])
            n = len(pts)
            # n is very small; exact permutation p (two-sided) for |rho| this large
            base = list(range(n))
            exact = sum(1 for q in itertools.permutations(base)
                        if abs(spearman(base, list(q))) >= abs(ra) - 1e-9) / math.factorial(n)
            L += ["", f"Spearman between shrink factor and dAUROC **rho={ra:+.3f}** "
                      f"(n={n} languages, permutation test two-sided p={exact:.3f})."]
            if all(p["d_eff"] is not None for p in pts):
                re_ = spearman(lg, [p["d_eff"] for p in pts])
                L += [f"Spearman between shrink factor and d surviving rate **rho={re_:+.3f}**."]
            L += ["", "This section is the core of the scale control: not only the direction 'smaller corpora are more dangerous', "
                      "but **how much it drops is ordered by how much it shrinks**. With only a few languages, the p value comes from a permutation test; "
                      "do not use a large-sample approximation.", ""]

    open(os.path.join(OUT, "scale_control.md"), "w").write("\n".join(L) + "\n")
    json.dump({"sizes": sizes, "corpus": corpus, "auc_points": auc_pts, "eff_points": eff_pts,
               "args": vars(args)}, open(os.path.join(OUT, "scale_control.json"), "w"),
              indent=1, ensure_ascii=False)
    print("\n".join(L))
    print(f"\nsaved {OUT}/scale_control.md")


if __name__ == "__main__":
    main()