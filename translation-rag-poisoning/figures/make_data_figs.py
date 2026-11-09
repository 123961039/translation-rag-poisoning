"""Data figures for the ICDE paper. All numbers are read from the server result files.

python make_data_figs.py <results/miracl dir> <outdir>
"""
import sys, os, re, json, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker
from matplotlib.lines import Line2D

R = sys.argv[1]
OUT = sys.argv[2]
os.makedirs(OUT, exist_ok=True)

LANGS = ["sw", "te", "yo", "id"]
C_REL = "#0072B2"   # rel_knn10
C_KNN = "#E69F00"   # knn10
C_ATK = "#D55E00"   # attacked
C_DEF = "#009E73"   # defended
GRAY = "#777777"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Liberation Sans", "DejaVu Sans"],
    "font.size": 7.5, "axes.titlesize": 7.5, "axes.labelsize": 7.5,
    "xtick.labelsize": 6.8, "ytick.labelsize": 6.8, "legend.fontsize": 6.8,
    "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
    "axes.spines.top": False, "axes.spines.right": False,
    "pdf.fonttype": 42, "ps.fonttype": 42,
})


def save(fig, name):
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(OUT, f"{name}.{ext}"), bbox_inches="tight", pad_inches=0.02, dpi=300)
    plt.close(fig)


def md_tables(path):
    """Return list of (header, rows) for every markdown table in a file."""
    tabs, cur = [], None
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if cur is None:
                cur = [cells, []]
            elif set("".join(cells)) <= set("-: "):
                continue
            else:
                cur[1].append(cells)
        else:
            if cur:
                tabs.append(cur)
            cur = None
    if cur:
        tabs.append(cur)
    return tabs


num = lambda s: float(re.match(r"[-+]?\d*\.?\d+", s.replace("**", "").replace("−", "-")).group())


# ------------------------------------------------------------- Fig. scale x sampling
def fig_scale():
    j = json.load(open(os.path.join(R, "scale_seeds/summary.json")))
    fig, axes = plt.subplots(1, 4, figsize=(7.16, 1.75), sharey=False)
    for ax, lang in zip(axes, LANGS):
        full = [v for k, v in j.items() if k.startswith(lang + "|full|")]
        n_full = full[0]["corpus"]
        for feat, col in (("rel_knn10", C_REL), ("knn10", C_KNN)):
            fa = np.mean([v[feat]["auc"] for v in full])
            for mode, ls, mk in (("keep", "-", "o"), ("nokeep", "--", "s")):
                xs, ys, es = [], [], []
                for size in ("20000", "45000", "131924"):
                    vs = [v for k, v in j.items() if k.startswith(f"{lang}|{size}|{mode}|")]
                    if not vs or int(size) >= n_full:
                        continue
                    xs.append(np.mean([v["corpus"] for v in vs]))
                    a = [v[feat]["auc"] for v in vs]
                    ys.append(np.mean(a)); es.append(np.std(a))
                xs.append(n_full); ys.append(fa); es.append(0)
                ax.errorbar(xs, ys, yerr=es, color=col, ls=ls, marker=mk, ms=2.6, lw=1.0,
                            capsize=1.5, elinewidth=0.6, mfc="white" if mode == "nokeep" else col)
        ax.set_xscale("log")
        ax.set_title(f"{lang} (full = {n_full/1000:,.0f}k)" if n_full < 1e6 else f"{lang} (full = {n_full/1e6:.2f}M)", pad=2)
        ticks = {"sw": [2e4, 5e4, 1e5], "te": [2e4, 1e5, 5e5], "yo": [2e4, 4e4], "id": [2e4, 1e5, 1e6]}[lang]
        ax.set_xticks(ticks)
        ax.set_xticklabels([f"{t/1e6:g}M" if t >= 1e6 else f"{t/1e3:g}k" for t in ticks])
        ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
        ax.set_xlim(1.6e4, n_full * 1.35)
        ax.grid(axis="y", lw=0.3, color="#DDDDDD")
        if lang == "sw":
            ax.set_ylabel("AUROC")
    fig.supxlabel("corpus size (passages, log scale)", y=0.0, fontsize=7.5)
    handles = [Line2D([], [], color=C_REL, lw=1.0, label="rel_knn10"),
               Line2D([], [], color=C_KNN, lw=1.0, label="knn10"),
               Line2D([], [], color=GRAY, ls="-", marker="o", ms=2.6, lw=1.0, label="keep relevant docs"),
               Line2D([], [], color=GRAY, ls="--", marker="s", ms=2.6, mfc="white", lw=1.0,
                      label="uniform (no keep)")]
    fig.legend(handles=handles, loc="upper center", ncol=4, frameon=False, bbox_to_anchor=(0.5, 1.10))
    fig.subplots_adjust(wspace=0.32, bottom=0.2)
    save(fig, "fig_scale")


# ------------------------------------------------------------- Fig. 2x2 density
def fig_density():
    tabs = md_tables(os.path.join(R, "density_2x2/summary.md"))
    # tables with header starting "lang | low@20k"
    auc = {}
    order = []
    for hdr, rows in tabs:
        if len(hdr) > 4 and hdr[1].startswith("low@20k"):
            order.append(rows)
    feats = ["rel_knn10", "knn10"]  # file order: rel first, knn second
    for feat, rows in zip(feats, order):
        for r in rows:
            if r[0] in LANGS:
                auc[(feat, r[0])] = [num(c) for c in r[1:5]]  # low20 high20 low45 high45
    fig, axes = plt.subplots(1, 2, figsize=(3.5, 1.9), sharey=True)
    for ax, feat, col in zip(axes, ["knn10", "rel_knn10"], [C_KNN, C_REL]):
        for i, lang in enumerate(LANGS):
            v = auc[(feat, lang)]
            for k, (lo, hi, off, size) in enumerate(((v[0], v[1], -0.17, "20k"), (v[2], v[3], 0.17, "45k"))):
                x = i + off
                ax.annotate("", xy=(x, hi), xytext=(x, lo),
                            arrowprops=dict(arrowstyle="-|>", color=col, lw=1.0, mutation_scale=6,
                                            shrinkA=0, shrinkB=0, alpha=1.0 if size == "45k" else 0.55))
                ax.plot(x, lo, "o", ms=2.8, color=col, mfc="white", mew=0.8, alpha=1.0 if size == "45k" else 0.55)
        ax.set_xticks(range(4))
        ax.set_xticklabels(LANGS)
        ax.set_title(feat, pad=2, color=col)
        ax.grid(axis="y", lw=0.3, color="#DDDDDD")
        ax.set_xlim(-0.5, 3.5)
        ax.set_ylim(0.36, 0.92)
    axes[0].set_ylabel("AUROC")
    fig.text(0.53, 1.0, "circle = low density, arrow head = high density; faded = 20k, solid = 45k",
             ha="center", va="bottom", fontsize=6.5)
    fig.subplots_adjust(wspace=0.08)
    save(fig, "fig_density")
    return auc


# ------------------------------------------------------------- Fig. paired ASR
def mcnemar_exact(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    p = sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n
    return min(1.0, 2 * p)


def holm(ps):
    idx = sorted(range(len(ps)), key=lambda i: ps[i])
    out, run = [0] * len(ps), 0
    for r, i in enumerate(idx):
        run = max(run, min(1, (len(ps) - r) * ps[i]))
        out[i] = run
    return out


def paired_asr():
    ans = {}
    for l in open(os.path.join(R, "rejudge/native/asr_answers_excl-bad.jsonl")):
        r = json.loads(l)
        if r["form"] not in ("bb", "-"):
            continue
        succ = bool(r["hit_target"]) and not bool(r["hit_correct"])
        ans[(r["lang"], r["variant"], r["cond"], r["qid"])] = succ
    rows = []
    for v in ("trans", "native", "en"):
        for lang in LANGS:
            qs = sorted({k[3] for k in ans if k[0] == lang and k[1] == v and k[2] == "attacked"})
            a = [ans[(lang, v, "attacked", q)] for q in qs]
            d = [ans[(lang, v, "defended", q)] for q in qs]
            b = sum(1 for x, y in zip(a, d) if x and not y)
            c = sum(1 for x, y in zip(a, d) if y and not x)
            rows.append(dict(lang=lang, variant=v, n=len(qs), att=np.mean(a), dfd=np.mean(d), b=b, c=c,
                             p=mcnemar_exact(b, c)))
    prim = [r for r in rows if r["variant"] == "trans"]
    for r, hp in zip(prim, holm([r["p"] for r in prim])):
        r["holm_primary"] = hp
    for r, hp in zip(rows, holm([r["p"] for r in rows])):
        r["holm_all"] = hp
    return rows


def fig_asr(rows):
    fig, ax = plt.subplots(figsize=(3.5, 2.7))
    y = 0
    yt, yl = [], []
    for v, vname in (("trans", "MT-translated poison (trans)"), ("native", "target-language poison (native)"),
                     ("en", "English poison (en)")):
        ax.text(0.005, y - 0.15, vname, ha="left", va="bottom", fontsize=6.5, style="italic", color=GRAY)
        y += 0.75
        for lang in LANGS:
            r = next(r for r in rows if r["lang"] == lang and r["variant"] == v)
            ax.plot([r["dfd"], r["att"]], [y, y], color="#BBBBBB", lw=1.6, solid_capstyle="round", zorder=1)
            ax.plot(r["att"], y, "o", color=C_ATK, ms=4, zorder=2)
            ax.plot(r["dfd"], y, "o", color=C_DEF, ms=4, zorder=3)
            sig = (r.get("holm_primary", 1) < 0.05) if v == "trans" else (r["holm_all"] < 0.05)
            ax.text(1.01, y, f"{r['b']}/{r['c']}" + ("*" if sig else ""), va="center", ha="left",
                    fontsize=6.3, transform=ax.get_yaxis_transform(), color="k" if sig else GRAY,
                    weight="bold" if sig else "normal")
            yt.append(y); yl.append(f"{lang} ({r['n']})")
            y += 1
        y += 0.15
    ax.set_yticks(yt)
    ax.set_yticklabels(yl, fontsize=6.5)
    ax.tick_params(axis="y", length=0, pad=2)
    ax.set_ylim(y - 0.3, -0.6)
    ax.set_xlim(0, 0.92)
    ax.set_xlabel("attack success rate (strict)")
    ax.grid(axis="x", lw=0.3, color="#DDDDDD")
    ax.text(1.01, -0.5, "b/c", ha="left", va="center", fontsize=6.3, transform=ax.get_yaxis_transform(),
            color=GRAY)
    handles = [Line2D([], [], marker="o", ls="", color=C_ATK, ms=4, label="attacked"),
               Line2D([], [], marker="o", ls="", color=C_DEF, ms=4, label="defended (rel_knn10 @ 5% FPR)")]
    fig.legend(handles=handles, loc="upper center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 1.04),
               handletextpad=0.2)
    save(fig, "fig_asr")


# ------------------------------------------------------------- Fig. metric gap
def fig_metric_gap():
    fig, axes = plt.subplots(1, 2, figsize=(3.5, 1.75), sharey=True)
    for ax, fn, title in zip(axes, ("metric_gap.json", "metric_gap_sub45000.json"), ("full corpus", "45k passages")):
        j = json.load(open(os.path.join(R, "rejudge/native", fn)))
        bad = 0
        for r in j["rows"]:
            disagree = r["verdict"]["5"] != "yes"
            bad += disagree
            ax.plot(r["d_auc"], r["d_tpr5"], "o" if not disagree else "D",
                    ms=2.8 if not disagree else 3.6,
                    color=GRAY if not disagree else C_ATK, mfc="white" if not disagree else C_ATK, mew=0.7,
                    zorder=3 if disagree else 2)
        ax.axhline(0, color="k", lw=0.5)
        ax.axvline(0, color="k", lw=0.5)
        lim = 0.13
        ax.set_xlim(-lim, lim)
        ax.set_ylim(-0.42, 0.42)
        ax.fill_between([-lim, 0], 0, 0.42, color="#FBE3D6", zorder=0)
        ax.fill_between([0, lim], -0.42, 0, color="#FBE3D6", zorder=0)
        ax.set_title(f"{title}: {bad}/{len(j['rows'])} disagree", pad=2)
        ax.set_xlabel(r"$\Delta$AUROC (rel $-$ knn)")
        ax.set_xticks([-0.1, 0, 0.1])
    axes[0].set_ylabel(r"$\Delta$TPR@5% (rel $-$ knn)")
    fig.subplots_adjust(wspace=0.08)
    save(fig, "fig_metric_gap")


if __name__ == "__main__":
    fig_scale()
    auc = fig_density()
    rows = paired_asr()
    fig_asr(rows)
    fig_metric_gap()
    json.dump(rows, open(os.path.join(OUT, "paired_asr_recomputed.json"), "w"), indent=1, default=float)
    for r in rows:
        print(r["lang"], r["variant"], r["n"], f"{r['att']:.2f}->{r['dfd']:.2f}", r["b"], r["c"],
              f"p={r['p']:.4f}", f"holm1={r.get('holm_primary', float('nan')):.4f}", f"holm12={r['holm_all']:.4f}")
