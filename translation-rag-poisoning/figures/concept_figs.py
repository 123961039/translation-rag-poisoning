"""Concept figures 2-4 for the ICDE paper (drawn at final print size).

Fig. 2  knn10 vs rel_knn10 (single column)
Fig. 3  two opposing effects of uniform downsampling (single column)
Fig. 4  2x2 controlled intervention: corpus size x local density (single column)

Usage: python concept_figs.py [outdir]   -> fig2_knn_vs_rel.pdf/.png, fig3_downsampling.pdf/.png, fig4_2x2_design.pdf/.png
"""
import sys
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from matplotlib.lines import Line2D

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))

BLUE = "#0072B2"      # benign / unrelated passage
LBLUE = "#56B4E9"     # same-topic passage
VERM = "#D55E00"      # poison
GREEN = "#009E73"     # easier / defense
GRAY = "#666666"
LGRAY = "#BBBBBB"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Liberation Sans", "DejaVu Sans"],
    "font.size": 7.5,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "axes.linewidth": 0.6,
})

DOT = 14      # marker area for passages
STAR = 90     # marker area for poison


def blank(ax, xlim, ylim, frame=True):
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect("equal")
    for s in ax.spines.values():
        s.set_visible(frame)
        s.set_color(LGRAY)


def spaced(rng, n, sampler, min_d, existing=None, max_tries=20000):
    """Sample n points with sampler() keeping at least min_d from each other and from `existing`."""
    pts = [] if existing is None else [tuple(p) for p in existing]
    out = []
    tries = 0
    while len(out) < n and tries < max_tries:
        tries += 1
        p = sampler()
        if all(np.hypot(p[0] - q[0], p[1] - q[1]) >= min_d for q in pts):
            pts.append(tuple(p))
            out.append(p)
    if len(out) < n:
        raise RuntimeError("could not place points; relax min_d")
    return np.array(out)


def save(fig, name):
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(OUT, f"{name}.{ext}"), bbox_inches="tight", pad_inches=0.02, dpi=300)
    plt.close(fig)


# ---------------------------------------------------------------- Fig. 2
def fig2():
    rng = np.random.default_rng(3)
    dense = spaced(rng, 16, lambda: rng.normal([-2.3, 0.0], 0.42), 0.22)
    sparse = spaced(rng, 14, lambda: rng.normal([1.4, -0.1], 1.0), 0.55)
    star = np.array([2.85, 1.35])           # at the edge of the sparse cluster
    benign = np.vstack([dense, sparse])
    k = 10

    def knn(i_pt, pts, exclude=()):
        d = np.hypot(*(pts - i_pt).T)
        order = [j for j in np.argsort(d) if j not in exclude and d[j] > 1e-9]
        return order[:k]

    nn_star = knn(star, benign)
    # a benign point at the rim of the sparse cluster: also "isolated" in absolute terms
    sp_idx = np.arange(len(dense), len(benign))
    iso = [np.sort(np.hypot(*(benign - benign[i]).T))[1:k + 1].mean() for i in sp_idx]
    rim = sp_idx[int(np.argmax(iso))]          # most isolated benign passage

    fig, axes = plt.subplots(1, 2, figsize=(3.5, 1.95))
    xlim, ylim = (-3.7, 4.1), (-2.7, 2.4)
    for ax, mode in zip(axes, ("a", "b")):
        blank(ax, xlim, ylim)
        if mode == "b":
            # second layer: neighbors' own neighbors (dashed, light)
            for j in nn_star[:6]:
                for m in knn(benign[j], benign, exclude=(j,))[:3]:
                    ax.plot(*zip(benign[j], benign[m]), ls=(0, (2, 1.2)), lw=0.55, color="#999999", zorder=1)
        for j in nn_star:
            ax.plot(*zip(star, benign[j]), lw=0.55, color=GRAY, zorder=2)
        ax.scatter(*benign.T, s=DOT, color=BLUE, lw=0, zorder=3)
        ax.scatter(*star, s=STAR, marker="*", color=VERM, lw=0, zorder=4)
        ax.text(-3.3, 1.55, "dense", ha="left", va="bottom", fontsize=6.5, color=GRAY)
        ax.text(1.0, -2.55, "sparse", ha="center", va="bottom", fontsize=6.5, color=GRAY)

    axes[0].set_title("(a) knn10 (absolute)", fontsize=7.5, pad=3)
    axes[1].set_title("(b) rel_knn10 (relative)", fontsize=7.5, pad=3)
    axes[0].annotate("benign, also\nlooks isolated", xy=benign[rim], xytext=(-2.0, -2.55),
                     fontsize=6.3, ha="center", va="bottom",
                     arrowprops=dict(arrowstyle="-|>", lw=0.5, color="k", mutation_scale=6,
                                     shrinkA=1, shrinkB=3))
    axes[1].plot([-3.4, -2.8], [-2.05, -2.05], ls=(0, (2, 1.2)), lw=0.7, color="#999999")
    axes[1].text(-2.7, -2.05, "neighbors'\nown kNN", fontsize=6.3, ha="left", va="center")
    axes[0].text(0.5, -0.06, r"$s(x)=\mathrm{knn}(x)$", transform=axes[0].transAxes,
                 ha="center", va="top", fontsize=7.5)
    axes[1].text(0.5, -0.06, r"$s(x)=\mathrm{knn}(x)-\mathrm{mean}_{n\in N(x)}\,\mathrm{knn}(n)$",
                 transform=axes[1].transAxes, ha="center", va="top", fontsize=7.5)
    fig.subplots_adjust(wspace=0.06)
    save(fig, "fig2_knn_vs_rel")


# ---------------------------------------------------------------- Fig. 3
def fig3():
    rng = np.random.default_rng(7)
    W, H = 10.0, 3.0
    star = np.array([6.6, 1.5])
    gold = spaced(rng, 8, lambda: star + rng.normal(0, 0.55, 2), 0.32, existing=[star + [0, 0]] )
    gold = gold[np.hypot(*(gold - star).T) > 0.3]
    other = spaced(rng, 46, lambda: rng.uniform([0.3, 0.3], [W - 0.3, H - 0.3]), 0.5,
                   existing=np.vstack([gold, star[None]]))

    # Effect 1: keep same-topic passages, thin everything else (global sparsity)
    e1_other = other[rng.choice(len(other), 14, replace=False)]
    e1_gold = gold
    # Effect 2: uniform thinning also removes most same-topic neighbors
    e2_other = e1_other
    e2_gold = gold[np.argsort(np.hypot(*(gold - star).T))[[3, 6]]]

    fig = plt.figure(figsize=(3.5, 2.3))
    ax0 = fig.add_axes([0.20, 0.66, 0.60, 0.274])
    ax1 = fig.add_axes([0.01, 0.28, 0.47, 0.213])
    ax2 = fig.add_axes([0.52, 0.28, 0.47, 0.213])

    def draw(ax, oth, gd, title=None, color="k"):
        blank(ax, (0, W), (0, H))
        ax.scatter(*oth.T, s=DOT, color=BLUE, lw=0, zorder=2)
        ax.scatter(*gd.T, s=DOT, color=LBLUE, lw=0, zorder=2)
        ax.scatter(*star, s=STAR, marker="*", color=VERM, lw=0, zorder=3)
        if title:
            ax.set_title(title, fontsize=7.5, color=color, pad=3)

    draw(ax0, other, gold, "Full corpus")
    draw(ax1, e1_other, e1_gold, "Effect 1: global sparsity")
    draw(ax2, e2_other, e2_gold, "Effect 2: fewer same-topic neighbors")
    ax0.annotate("same-topic passages\n(gold article)", xy=gold[np.argmax(gold[:, 0] + gold[:, 1])],
                 xytext=(W + 0.4, H * 0.95), fontsize=6.3, ha="left", va="top",
                 annotation_clip=False,
                 arrowprops=dict(arrowstyle="-|>", lw=0.5, color="k", mutation_scale=6, shrinkB=2))

    # branching arrows
    fig.text(0.5, 0.60, "uniform downsampling", ha="center", va="center", fontsize=6.8, zorder=5,
             bbox=dict(fc="white", ec="none", pad=0.6),
             style="italic", color=GRAY)
    for x_end in (0.245, 0.755):
        fig.add_artist(FancyArrowPatch((0.5, 0.645), (x_end, 0.555), transform=fig.transFigure,
                                       arrowstyle="-|>", mutation_scale=7, lw=0.7, color="k",
                                       connectionstyle="arc3,rad=0"))
    fig.text(0.245, 0.265, "↓ detection harder", ha="center", va="top", color=VERM,
             fontsize=7.5, weight="bold")
    fig.text(0.755, 0.265, "↑ detection easier", ha="center", va="top", color=GREEN,
             fontsize=7.5, weight="bold")
    fig.text(0.5, 0.19, "Net effect depends on whether relevant documents stay in the corpus.",
             ha="center", va="top", fontsize=6.8, color="k")
    save(fig, "fig3_downsampling")


# ---------------------------------------------------------------- Fig. 4
def fig4():
    rng = np.random.default_rng(11)
    W, H = 4.0, 3.0
    star = np.array([W / 2, H / 2])
    n_total = {"20k": 14, "45k": 26}
    n_swap = 6

    fig, axes = plt.subplots(2, 2, figsize=(3.5, 2.9))
    for c, size in enumerate(("20k", "45k")):
        n = n_total[size]
        # low density: 2 same-topic near the star, rest unrelated spread over the cell
        near = lambda: star + rng.normal(0, 0.45, 2)
        gold_low = spaced(rng, 2, near, 0.3, existing=[star])
        far = spaced(rng, n - 2, lambda: rng.uniform([0.2, 0.2], [W - 0.2, H - 0.2]), 0.36,
                     existing=np.vstack([gold_low, star[None]]))
        # keep unrelated passages away from the star so that density is carried by the light dots
        # high density: same cell, n_swap unrelated passages swapped for same-topic ones
        drop = rng.choice(len(far), n_swap, replace=False)
        far_high = np.delete(far, drop, axis=0)
        extra = spaced(rng, n_swap, near, 0.3,
                       existing=np.vstack([gold_low, star[None], far_high]))
        gold_high = np.vstack([gold_low, extra])
        for r, (oth, gd) in enumerate(((far, gold_low), (far_high, gold_high))):
            ax = axes[r, c]
            blank(ax, (0, W), (0, H))
            assert len(oth) + len(gd) == n
            ax.scatter(*oth.T, s=DOT, color=BLUE, lw=0, zorder=2)
            ax.scatter(*gd.T, s=DOT, color=LBLUE, lw=0, zorder=2)
            ax.scatter(*star, s=STAR, marker="*", color=VERM, lw=0, zorder=3)

    axes[0, 0].set_title("Corpus size 20k", fontsize=7.5, pad=3)
    axes[0, 1].set_title("Corpus size 45k", fontsize=7.5, pad=3)
    axes[0, 0].set_ylabel("Low local\ndensity", fontsize=7.5)
    axes[1, 0].set_ylabel("High local\ndensity", fontsize=7.5)
    fig.subplots_adjust(wspace=0.05, hspace=0.20, top=0.85)

    handles = [
        Line2D([], [], ls="", marker="o", ms=4, color=BLUE, label="unrelated passage"),
        Line2D([], [], ls="", marker="o", ms=4, color=LBLUE, label="same-topic passage"),
        Line2D([], [], ls="", marker="*", ms=8, color=VERM, label="poison"),
    ]
    fig.legend(handles=handles, loc="upper center", ncol=3, frameon=False, fontsize=6.8,
               bbox_to_anchor=(0.53, 1.0), handletextpad=0.2, columnspacing=1.0)
    # swap annotation between rows (left side of right column)
    fig.text(0.53, 0.487, "\u2193  swap %d unrelated for same-topic passages (total fixed)  \u2193" % n_swap,
             ha="center", va="center", fontsize=6.3, color=GRAY)
    save(fig, "fig4_2x2_design")


if __name__ == "__main__":
    fig2()
    fig3()
    fig4()
    print("written to", OUT)
