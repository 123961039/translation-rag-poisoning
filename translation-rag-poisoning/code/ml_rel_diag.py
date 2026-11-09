"""Does the two-layer relative feature help or hurt? (CPU only, seconds without a GPU)

rel_knn10 = knn10 - c, where c is "the mean knn10 of the neighbours". c need not be recomputed -- it equals
knn10 - rel_knn10, and both are stored in detect_feats.npz.

Subtracting c has two opposing effects, which this script separates:

  signal cancellation   S_c / S_k   if the neighbours of a poison are also isolated, subtracting c removes signal too
  noise change          sd_rel/sd_k  <1 means c moves together with knn10 and subtracting it cleans up; >1 means c is extra noise

  net effect  d'_rel / d'_k = (1 - S_c/S_k) / (sd_rel/sd_k)

S = "mean over length-matched benign passages - mean over poisons" (poison more isolated -> smaller knn10 -> S > 0).

    python ml_rel_diag.py
    python ml_rel_diag.py --feats _sub45000
    python ml_rel_diag.py --lang yo --feats _sub45000

Input: results/miracl/<lang>/detect_feats[<suffix>].npz, poison.jsonl
Output: results/miracl/rel_diag[<suffix>].md / .json
"""
import argparse, json, os

import numpy as np

from ml_common import LANGS, ROOT, load_keep, ml_results

VARIANTS = ["native", "trans", "en"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", nargs="+", default=LANGS)
    ap.add_argument("--feats", default="", help='size suffix, e.g. "_sub45000"')
    ap.add_argument("--exclude", default="bad", choices=["none", "bad", "unsure"])
    ap.add_argument("--judgments", default=None)
    ap.add_argument("--dup", type=float, default=0.95, help="near-duplicate threshold (nn1 above it counts as near-duplicate)")
    args = ap.parse_args()

    rows, prof = [], []
    for lang in args.lang:
        rd = ml_results(lang)
        pz = os.path.join(rd, f"detect_feats{args.feats}.npz")
        pp = os.path.join(rd, "poison.jsonl")
        miss = [p for p in (pz, pp) if not os.path.exists(p)]
        if miss:
            print(f"[{lang}] missing the following files, skipped:\n    " + "\n    ".join(miss))
            continue
        z = np.load(pz)
        items = [json.loads(l) for l in open(pp)]
        keep, _ = load_keep(lang, items, args.exclude, args.judgments)
        has_full = {v: [j for j, it in enumerate(items) if it.get(f"{v}_adv")] for v in VARIANTS}
        pos_clean = {r: i for i, r in enumerate(z["clean_rows"])}

        ck, cr = z["clean_knn10"], z["clean_rel_knn10"]
        cc = ck - cr                                  # correction term c, not recomputed
        # corpus-side profile: near-duplicate fraction, correlation of c and knn10
        rand_i = [pos_clean[r] for r in z["rand"]]
        nn1r = z["clean_nn1"][rand_i]
        corr = float(np.corrcoef(ck[rand_i], cc[rand_i])[0, 1])
        prof.append({"lang": lang, "n_clean": len(z["clean_rows"]),
                     "dup_rate": float((nn1r > args.dup).mean()),
                     "nn1_med": float(np.median(nn1r)),
                     "knn10_med": float(np.median(ck[rand_i])),
                     "c_sd": float(cc[rand_i].std()), "knn10_sd": float(ck[rand_i].std()),
                     "corr_knn10_c": corr})

        for v in VARIANTS:
            for f in ("bb", "adv"):
                kk, rk = f"{v}_{f}_knn10", f"{v}_{f}_rel_knn10"
                if kk not in z or rk not in z:
                    continue
                sel = [i for i, j in enumerate(has_full[v]) if keep[j]]
                pk, pr = z[kk][sel], z[rk][sel]
                pc = pk - pr
                mi = [pos_clean[r] for r in z[f"{v}_{f}_match"]]
                mk, mr, mc = ck[mi], cr[mi], cc[mi]
                if len(pk) < 3:
                    continue

                S_k = float(mk.mean() - pk.mean())     # poison more isolated -> smaller knn10 -> S>0
                S_c = float(mc.mean() - pc.mean())
                S_r = float(mr.mean() - pr.mean())     # = S_k - S_c
                pooled = lambda a, b: float(np.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2))
                sd_k, sd_r = pooled(mk, pk), pooled(mr, pr)
                d_k = S_k / sd_k if sd_k > 0 else float("nan")
                d_r = S_r / sd_r if sd_r > 0 else float("nan")
                rows.append({"lang": lang, "variant": v, "form": f, "n": len(pk),
                             "S_k": S_k, "S_c": S_c, "S_r": S_r,
                             "cancel": S_c / S_k if S_k else float("nan"),
                             "sd_k": sd_k, "sd_r": sd_r,
                             "noise": sd_r / sd_k if sd_k > 0 else float("nan"),
                             "d_k": d_k, "d_r": d_r,
                             "net": d_r / d_k if d_k else float("nan")})

    if not rows:
        print("no data to analyse")
        return

    size = "full corpus" if not args.feats else args.feats.lstrip("_")
    L = [f"# Does the two-layer relative feature help or hurt ({size}, exclusion {args.exclude})", "",
         "`rel_knn10 = knn10 - c`, c = mean knn10 of the neighbours (solved from knn10 - rel_knn10, not recomputed).", "",
         "- **signal cancellation** `S_c/S_k`: whether the neighbours of a poison are also isolated. Near 1 = signal removed; "
         "negative = subtracting c amplifies the signal", "",
         "- **noise ratio** `sd_rel/sd_k`: <1 = c moves with knn10, subtracting is cleaner; >1 = c is extra noise", "",
         "- **net effect** `d'_rel/d'_k`: >1 relative feature better, <1 absolute feature better", "",
         "| lang | variant | form | n | S_k | S_c | cancellation | sd_k | sd_rel | noise ratio | d'_k | d'_rel | net effect |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['lang']} | {r['variant']} | {r['form']} | {r['n']} | "
                 f"{r['S_k']:+.4f} | {r['S_c']:+.4f} | {r['cancel']:+.2f} | "
                 f"{r['sd_k']:.4f} | {r['sd_r']:.4f} | {r['noise']:.2f} | "
                 f"{r['d_k']:.2f} | {r['d_r']:.2f} | **{r['net']:.2f}** |")

    # attribution by language. Note: the question is not "which term is larger in absolute value" but "on which term this language departs from the others" --
    # cancellation may be high for every language, in which case it cannot explain differences between languages.
    med = lambda x: float(np.median(x)) if len(x) else float("nan")
    per = {}
    for lang in dict.fromkeys(r["lang"] for r in rows):
        rs = [r for r in rows if r["lang"] == lang]
        per[lang] = {"net": med([r["net"] for r in rs]), "cancel": med([r["cancel"] for r in rs]),
                     "noise": med([r["noise"] for r in rs])}
    lg = lambda x: float(np.log(max(1e-6, x)))
    ref_c = med([lg(1 - p["cancel"]) for p in per.values()])      # cross-language reference
    ref_n = med([lg(p["noise"]) for p in per.values()])

    L += ["", "## Attribution by language", "",
          "net effect = (1 - cancellation) / noise ratio. The two 'deviation' columns are this language's deviation from the **cross-language median** "
          "on each term (log scale, additive); the term with the larger absolute value is why it differs from the other languages.", "",
          "| lang | median net effect | cancellation | noise ratio | cancellation deviation | noise deviation | difference mainly from |",
          "|---|---|---|---|---|---|---|"]
    for lang, p in per.items():
        dc = lg(1 - p["cancel"]) - ref_c
        dn = -(lg(p["noise"]) - ref_n)              # more noise -> smaller net effect; negated to align directions
        if abs(dc) < 0.05 and abs(dn) < 0.05:
            why = "(consistent with other languages)"
        else:
            why = ("**signal cancellation**" if abs(dc) > abs(dn) else "**noise ratio**") + \
                  (", more favourable" if (dc if abs(dc) > abs(dn) else dn) > 0 else ", less favourable")
        L.append(f"| {lang} | {p['net']:.2f} | {p['cancel']:+.2f} | {p['noise']:.2f} | "
                 f"{dc:+.2f} | {dn:+.2f} | {why} |")
    L += ["", "Absolute levels as well:", ""]
    for lang, p in per.items():
        v = ("relative feature better" if p["net"] > 1.05 else
             "absolute feature better" if p["net"] < 0.95 else "comparable")
        L.append(f"- {lang}: net effect {p['net']:.2f} -> {v}")
    L += [""]

    L += ["", "## Corpus profile (random benign passages)", "",
          "| lang | benign passages | median nn1 | near-duplicate rate | median knn10 | sd(knn10) | sd(c) | corr(knn10, c) |",
          "|---|---|---|---|---|---|---|---|"]
    for p in prof:
        L.append(f"| {p['lang']} | {p['n_clean']:,} | {p['nn1_med']:.3f} | {p['dup_rate']:.3f} | "
                 f"{p['knn10_med']:.3f} | {p['knn10_sd']:.4f} | {p['c_sd']:.4f} | {p['corr_knn10_c']:+.3f} |")
    L += ["", f"near-duplicate rate = fraction with nn1 > {args.dup}. The higher corr(knn10, c), the more common fluctuation subtracting c removes; "
              "the lower, the more c is mainly noise.", ""]

    out = os.path.join(ROOT, "results", "miracl")
    open(os.path.join(out, f"rel_diag{args.feats}.md"), "w").write("\n".join(L) + "\n")
    json.dump({"rows": rows, "profile": prof, "args": vars(args)},
              open(os.path.join(out, f"rel_diag{args.feats}.json"), "w"), indent=1, ensure_ascii=False)
    print("\n".join(L))
    print(f"\nsaved {out}/rel_diag{args.feats}.md")


if __name__ == "__main__":
    main()