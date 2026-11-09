"""
CPU-only analysis (a few tens of seconds): reads saved result files, loads no model and uses no GPU.
    python ml_analyze.py
    python ml_analyze.py --feat rel_knn10 --boot 2000
Inputs (outputs of ml_translate / ml_attack / ml_detect)
    results/miracl/<lang>/poison.jsonl, attack_detail.jsonl, detect_feats.npz
Three tables
  A. Attack (paired): hit@5 of native / trans / en on the questions shared by all three variants,
     differences (trans-en, native-trans) with paired bootstrap 95% CI
  B. Detection: main feature fixed in advance as rel_knn10 (--feat to change); AUROC (vs length-matched / random) with CI;
     deployment metrics: thresholds at the 99% / 95% quantile of random benign scores (FPR 1% / 5%), share of poisons flagged (TPR)
  C. Attack and defense together: share of questions whose poison is in the top-5 and not flagged at ingestion = surviving-poison rate (FPR 5%)
Output: results/miracl/analysis[_excl-bad|_excl-unsure].md / .json (no suffix with --exclude none)
"""
import argparse, json, os

import numpy as np

from ml_common import LANGS, ROOT, load_keep, ml_results

VARIANTS = ["native", "trans", "en"]
DEFAULT_FEAT = "rel_knn10"      # with another main feature, its name is added to the output file name to avoid overwriting


def auc(pos, neg):
    """pos/neg are suspicion scores; AUROC from rank statistics (ties included)"""
    neg = np.sort(neg)
    lo = np.searchsorted(neg, pos, "left")
    hi = np.searchsorted(neg, pos, "right")
    return float(np.mean((lo + (hi - lo) / 2) / len(neg)))


def ci(vals):
    return [float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))]


def boot_mean(x, B, rng):
    x = np.asarray(x, float)
    return float(x.mean()), ci([x[rng.integers(0, len(x), len(x))].mean() for _ in range(B)])


def boot_auc(pos, neg, B, rng):
    return auc(pos, neg), ci([auc(pos[rng.integers(0, len(pos), len(pos))], neg[rng.integers(0, len(neg), len(neg))])
                              for _ in range(B)])


def fmt(m, c, d=2):
    return f"{m:.{d}f} ({c[0]:.{d}f}–{c[1]:.{d}f})"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", nargs="+", default=LANGS)
    ap.add_argument("--feat", default=DEFAULT_FEAT, help="main feature fixed in advance (smaller = more isolated)")
    ap.add_argument("--size", default="full", help="corpus size of the attack results (full or sub131924)")
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--exclude", default="bad", choices=["none", "bad", "unsure"],
                    help="exclude questions by human judgment: none = keep all; bad = drop bad; unsure = also drop unsure")
    ap.add_argument("--judgments", default=None, help="judgment file, default results/miracl/review_judgments.json")
    ap.add_argument("--feats", default="", help='feature file suffix, e.g. "_sub131924" (with --size sub131924 for the scale comparison)')
    args = ap.parse_args()
    rng = np.random.default_rng(args.seed)
    A, Bt, C = [], [], []

    for lang in args.lang:
        rd = ml_results(lang)
        paths = {k: os.path.join(rd, k) for k in ("poison.jsonl", "attack_detail.jsonl")}
        paths["detect_feats.npz"] = os.path.join(rd, f"detect_feats{args.feats}.npz")
        miss = [p for p in paths.values() if not os.path.exists(p)]
        if miss:
            print(f"[{lang}] missing files, skipped:\n    " + "\n    ".join(miss))
            continue
        items = [json.loads(l) for l in open(paths["poison.jsonl"])]
        detail = [json.loads(l) for l in open(paths["attack_detail.jsonl"])]
        assert [d["qid"] for d in detail] == [it["qid"] for it in items], "attack_detail and poison.jsonl question order differ; re-run ml_attack.py"
        z = np.load(paths["detect_feats.npz"])
        keep, kst = load_keep(lang, items, args.exclude, args.judgments)
        has_full = {v: [j for j, it in enumerate(items) if it.get(f"{v}_adv")] for v in VARIANTS}  # aligned with the npz
        has = {v: [j for j in has_full[v] if keep[j]] for v in VARIANTS}
        common = sorted(set(has["native"]) & set(has["trans"]) & set(has["en"]))
        print(f"[{lang}] exclusion setting {kst}", flush=True)
        pos_clean = {r: i for i, r in enumerate(z["clean_rows"])}
        cf = z[f"clean_{args.feat}"]
        print(f"[{lang}] kept {sum(keep)}/{len(items)} questions, {len(common)} shared by all three variants", flush=True)

        # ---------- A. attack (paired) ----------
        for form in ("bb", "adv"):
            for mode in ("single", "multi"):
                key = lambda v: f"{args.size}/{v}/{form}/{mode}/hit5"
                if key("en") not in detail[0]:
                    continue
                h = {v: np.array([float(detail[j].get(key(v), np.nan)) for j in common]) for v in VARIANTS}
                row = {"lang": lang, "form": form, "mode": mode, "n_common": len(common)}
                for v in VARIANTS:
                    row[v] = boot_mean(h[v], args.boot, rng)
                for a, b in (("trans", "en"), ("native", "trans")):
                    d = h[a] - h[b]
                    row[f"{a}-{b}"] = boot_mean(d, args.boot, rng)
                A.append(row)

        # ---------- B. detection ----------
        neg_rand_all = cf[[pos_clean[r] for r in z["rand"]]]
        sr = -neg_rand_all                                   # suspicion
        thr = {fp: float(np.quantile(sr, 1 - fp)) for fp in (0.01, 0.05)}
        for v in VARIANTS:
            for form in ("bb", "adv"):
                k = f"{v}_{form}_{args.feat}"
                if k not in z:
                    continue
                sel = [i for i, j in enumerate(has_full[v]) if keep[j]]
                sp = -z[k][sel]                              # aligned with has[v] (after exclusion)
                sm = -cf[[pos_clean[r] for r in z[f"{v}_{form}_match"]]]
                row = {"lang": lang, "variant": v, "form": form, "n": len(sp),
                       "auc_lenmatch": boot_auc(sp, sm, args.boot, rng),
                       "auc_random": boot_auc(sp, sr, args.boot, rng),
                       "tpr@1%": boot_mean(sp > thr[0.01], args.boot, rng),
                       "tpr@5%": boot_mean(sp > thr[0.05], args.boot, rng)}
                # AUROC on shared questions (comparable across variants)
                where = {j: i for i, j in enumerate(has[v])}
                spc = np.array([sp[where[j]] for j in common])
                row["auc_lenmatch_common"] = boot_auc(spc, sm, args.boot, rng)
                Bt.append(row)

                # ---------- C. surviving-poison rate after filtering ----------
                hk = f"{args.size}/{v}/{form}/single/hit5"
                if hk in detail[0]:
                    hit = np.array([bool(detail[j][hk]) for j in common])
                    flag = spc > thr[0.05]
                    C.append({"lang": lang, "variant": v, "form": form, "n_common": len(common),
                              "hit@5": boot_mean(hit, args.boot, rng),
                              "flag@5%FPR": boot_mean(flag, args.boot, rng),
                              "hit_and_unflagged": boot_mean(hit & ~flag, args.boot, rng)})

    # ---------- output ----------
    L = [f"# MIRACL analysis (main feature {args.feat}, attack corpus {args.size}, exclusion {args.exclude}, {args.boot} bootstrap samples, 95% CI in brackets)", ""]
    L += ["## A. Attack: paired comparison on shared questions (hit@5)", "",
          "| lang | form | injected | shared questions | native | trans | en | trans-en | native-trans |", "|---|---|---|---|---|---|---|---|---|"]
    for r in A:
        L.append(f"| {r['lang']} | {r['form']} | {r['mode']} | {r['n_common']} | " +
                 " | ".join(fmt(*r[v]) for v in VARIANTS) + f" | {fmt(*r['trans-en'])} | {fmt(*r['native-trans'])} |")
    L += ["", "A difference is significant only if its CI excludes 0.", "",
          f"## B. Ingestion-time detection ({args.feat}, one injected passage per question)", "",
          "| lang | variant | form | questions | AUROC vs length-matched | same (shared questions) | AUROC vs random | TPR@1%FPR | TPR@5%FPR |",
          "|---|---|---|---|---|---|---|---|---|"]
    for r in Bt:
        L.append(f"| {r['lang']} | {r['variant']} | {r['form']} | {r['n']} | {fmt(*r['auc_lenmatch'], 3)} | "
                 f"{fmt(*r['auc_lenmatch_common'], 3)} | {fmt(*r['auc_random'], 3)} | {fmt(*r['tpr@1%'])} | {fmt(*r['tpr@5%'])} |")
    L += ["", "TPR: thresholds at the 99% / 95% quantile of random benign passages, i.e. 1% / 5% of benign passages are flagged at ingestion.", "",
          "## C. Attack and defense together: after ingestion filtering at 5% FPR (shared questions, one injected passage per question)", "",
          "| lang | variant | form | questions | hit@5 before filtering | share flagged | surviving-poison rate |", "|---|---|---|---|---|---|---|"]
    for r in C:
        L.append(f"| {r['lang']} | {r['variant']} | {r['form']} | {r['n_common']} | {fmt(*r['hit@5'])} | "
                 f"{fmt(*r['flag@5%FPR'])} | {fmt(*r['hit_and_unflagged'])} |")
    L += ["", "Surviving-poison rate = poison in the top-5 and not flagged (flagged poisons are blocked at ingestion)."]
    out = os.path.join(ROOT, "results", "miracl")
    tag = ("" if args.exclude == "none" else f"_excl-{args.exclude}") \
          + ("" if args.feat == DEFAULT_FEAT else f"_{args.feat}") + args.feats
    open(os.path.join(out, f"analysis{tag}.md"), "w").write("\n".join(L) + "\n")
    json.dump({"A": A, "B": Bt, "C": C, "args": vars(args)}, open(os.path.join(out, f"analysis{tag}.json"), "w"), indent=1)
    print("\n".join(L))
    print(f"\nsaved {out}/analysis{tag}.md")


if __name__ == "__main__":
    main()