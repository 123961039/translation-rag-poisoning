"""
Feature reproducibility check: id / yo poison features differed by more than 1e-3 from the original files in the scale_seeds self-check (GPU, a few minutes).
Three checks:
  1. compute ml_detect.two_layer twice on the same machine: is it bit-for-bit reproducible?
  2. compare poison by poison with the original detect_feats.npz and with scale_seeds seed 0; list poisons differing by > 1e-3
  3. for those poisons, check ties at the neighbour boundary: similarity gap between neighbours 10/11 and 50/51 (fp16 ties can swap neighbour sets),
     and whether identical vectors (near-duplicate passages) occur among the neighbours
Finally, the effect on AUROC (computed once with the original features and once with the recomputed features).
    python feat_determinism.py --lang id yo
Output: results/miracl/feat_determinism.md
"""
import argparse, json, os

import numpy as np

from ml_common import ROOT, gpu_topk, load_corpus_emb, ml_results
from ml_detect import two_layer
from ml_attack import load_items, texts_of


def auc(pos, neg):
    neg = np.sort(neg)
    lo, hi = np.searchsorted(neg, pos, "left"), np.searchsorted(neg, pos, "right")
    return float(np.mean((lo + (hi - lo) / 2) / len(neg)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", nargs="+", default=["id", "yo"])
    ap.add_argument("--variant", default="trans")
    ap.add_argument("--form", default="bb")
    a = ap.parse_args()
    from sentence_transformers import SentenceTransformer
    from ml_common import M3_PATH
    m = SentenceTransformer(M3_PATH, device="cuda").half(); m.max_seq_length = 512
    enc = lambda xs: m.encode(xs, batch_size=128, normalize_embeddings=True, convert_to_numpy=True,
                              show_progress_bar=False).astype(np.float16)
    key = f"{a.variant}_{a.form}"
    L = [f"# Feature reproducibility ({key}, full corpus)", ""]
    for lg in a.lang:
        items, _ = load_items(lg)
        idx = [j for j, it in enumerate(items) if it.get(f"{a.variant}_adv")]
        corpus, _ = load_corpus_emb(lg)
        P = enc([texts_of(items[j], a.variant, a.form)[0] for j in idx])
        P2 = enc([texts_of(items[j], a.variant, a.form)[0] for j in idx])
        F1 = two_layer(corpus, P, np.full(len(P), -1))
        F2 = two_layer(corpus, P2, np.full(len(P2), -1))
        z = np.load(os.path.join(ml_results(lg), "detect_feats.npz"))
        ref = z[f"{key}_rel_knn10"]
        ss = os.path.join(ROOT, "results", "miracl", "scale_seeds", lg, "full_full_s0.npz")
        s0 = np.load(ss)[f"{key}_pois_rel_knn10"] if os.path.exists(ss) else None
        d_self = np.abs(F1["rel_knn10"] - F2["rel_knn10"])
        d_enc = float(np.abs(P.astype(np.float32) - P2.astype(np.float32)).max())
        n = min(len(ref), len(F1["rel_knn10"]))
        d_ref = np.abs(F1["rel_knn10"][:n] - ref[:n])
        L += [f"## {lg} ({len(idx)} poisons, original file {len(ref)})", "",
              f"- two runs on this machine: max encoding difference {d_enc:.1e}; max rel_knn10 difference {d_self.max():.1e}",
              f"- this run vs original file (another GPU): max difference {d_ref.max():.1e}, {int((d_ref > 1e-3).sum())} poisons differ by > 1e-3"]
        if s0 is not None:
            L.append(f"- this run vs scale_seeds seed 0: max difference {np.abs(F1['rel_knn10'][:len(s0)] - s0).max():.1e}")
        bad = np.flatnonzero(d_ref > 1e-3)
        if len(bad):
            S, I = gpu_topk([corpus], P[bad], 52)
            L += ["", "| poison | difference | similarity gap neighbours 10/11 | similarity gap neighbours 50/51 | identical neighbour vector pairs in top-10 |", "|---|---|---|---|---|"]
            for k, b in enumerate(bad):
                nb = np.asarray(corpus[I[k, :10]], np.float32)
                dup = int(sum((np.abs(nb[i] - nb[j]).max() == 0) for i in range(10) for j in range(i + 1, 10)))
                L.append(f"| {items[idx[b]]['qid']} | {d_ref[b]:.1e} | {S[k, 9] - S[k, 10]:.1e} | {S[k, 49] - S[k, 50]:.1e} | {dup} |")
        # AUROC effect (length-matched negatives as in ml_analyze; negatives from the original file to avoid other differences)
        pos = {r: i for i, r in enumerate(z["clean_rows"])}
        sm = -z["clean_rel_knn10"][[pos[r] for r in z[f"{key}_match"]]]
        L += ["", f"- AUROC (all poisons, vs length-matched): original features {auc(-ref[:n], sm):.4f}, recomputed features {auc(-F1['rel_knn10'][:n], sm):.4f}", ""]
    L += ["Reading: if two runs on the same machine are identical, differences appear only across GPUs, and the differing poisons have ties / near-duplicates at the neighbour boundary,",
          "they are due to fp16 rounding on different GPUs swapping neighbours; the AUROC change should be far smaller than the effects reported in the paper."]
    out = os.path.join(ROOT, "results", "miracl", "feat_determinism.md")
    open(out, "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
