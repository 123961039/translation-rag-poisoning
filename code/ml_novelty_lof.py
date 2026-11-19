"""Table 4 GPU benchmark with a shared held-out reference corpus."""
import argparse
import json
import os
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from sentence_transformers import SentenceTransformer
from sklearn.metrics import roc_auc_score
from ml_common import LANGS, M3_PATH, ROOT
from second_encoder import load_items, texts_of


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lang", choices=LANGS)
    parser.add_argument("--model", default=M3_PATH)
    parser.add_argument("--output-dir", type=Path, default=Path(ROOT) / "results/miracl/novelty_lof")
    parser.add_argument("--yoruba-reference", type=Path,
                        default=Path(ROOT) / "results/miracl/novelty_lof/yo_sklearn.npz")
    args = parser.parse_args()
    lang = args.lang
    root = Path(ROOT)
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    res = root / "results/miracl"
    expected = {"yo": 26, "sw": 47, "te": 52, "id": 28}
    k = 10

    torch.set_grad_enabled(False)
    torch.set_float32_matmul_precision("highest")
    torch.backends.cuda.matmul.allow_tf32 = False

    emb = np.load(root / f"emb/miracl/{lang}/bge-m3/corpus_emb_fp16.npy",
                  mmap_mode="r", allow_pickle=False)
    with np.load(res / f"baselines/{lang}.npz", allow_pickle=False) as z:
        rand = z["rand"].astype(int)
        match = z["match_trans"].astype(int)
        candidates = z["trans_items"].astype(int)

    items = load_items(lang)
    labels = json.loads((res / "review_judgments_native.json").read_text())[lang]
    valid = [i for i in candidates if labels[str(items[i]["qid"])]["label"] != "bad"]
    qids = np.array([str(items[i]["qid"]) for i in valid])
    assert len(valid) == len(np.unique(qids)) == expected[lang]
    held = np.union1d(rand, match)
    assert 0 <= held.min() and held.max() < len(emb)
    keep = np.ones(len(emb), dtype=bool)
    keep[held] = False
    print(f"SETUP {lang=} corpus={len(emb)} reference={keep.sum()} "
          f"heldout={len(held)} valid={len(valid)}", flush=True)

    model = SentenceTransformer(args.model,
                                device="cuda").half().eval()
    model.max_seq_length = 512
    texts = [texts_of(items[i], "trans", "bb")[0] for i in valid]
    positive = model.encode(texts, normalize_embeddings=True, batch_size=32,
                            convert_to_numpy=True, show_progress_bar=False)
    del model
    torch.cuda.empty_cache()

    def unit(x):
        return F.normalize(torch.as_tensor(x, device="cuda", dtype=torch.float32),
                           dim=1)

    ref = unit(emb[keep])
    query = unit(np.concatenate([emb[held], positive]))
    print(f"{lang}: reference and candidates ready", flush=True)

    # Exact cosine top-k with self-exclusion for reference points.
    def lookup(vectors, rowids=None):
        distances, indices = [], []
        for start in range(0, len(vectors), 128):
            q = vectors[start:start + 128]
            sim = q @ ref.T
            if rowids is not None:
                rows = rowids[start:start + len(q)]
                sim[torch.arange(len(q), device="cuda"), rows] = -torch.inf
            vals, idx = sim.topk(k, dim=1)
            distances.append((1 - vals).clamp_min(0))
            indices.append(idx)
        return torch.cat(distances), torch.cat(indices)

    # LOF needs the query neighbors’ reachability densities and the next layer’s k-distances.
    d0, n0 = lookup(query)
    u1, inv0 = torch.unique(n0, return_inverse=True)
    inv0 = inv0.reshape_as(n0)
    d1, n1 = lookup(ref[u1], u1)

    u2, inv1 = torch.unique(n1, return_inverse=True)
    inv1 = inv1.reshape_as(n1)
    print(f"{lang}: first-layer unique={len(u1)}, second-layer unique={len(u2)}",
          flush=True)
    kdist2 = torch.empty(len(u2), device="cuda")
    for start in range(0, len(u2), 1024):
        rows = u2[start:start + 1024]
        d, _ = lookup(ref[rows], rows)
        kdist2[start:start + len(rows)] = d[:, -1]
        if start % 16384 == 0:
            print(f"{lang}: second layer {start + len(rows)}/{len(u2)}", flush=True)

    # Match the 1e-10 stabilizer in sklearn’s local reachability density.
    lrd1 = 1 / (torch.maximum(d1, kdist2[inv1]).mean(1) + 1e-10)
    reach0 = torch.maximum(d0, d1[:, -1][inv0]).mean(1)
    own_dist = d0.mean(1)
    neighbor_dist = d1.mean(1)[inv0].mean(1)
    scores = {
        "standard_LOF": lrd1[inv0].mean(1) * (reach0 + 1e-10),
        "knn10": own_dist,
        "rel_knn10": own_dist - neighbor_dist,
        "knn_distance_ratio": -neighbor_dist / (own_dist + 1e-6),
    }
    scores = {name: value.cpu().numpy() for name, value in scores.items()}
    ri, mi = np.searchsorted(held, rand), np.searchsorted(held, match)

    def metrics(score):
        assert np.isfinite(score).all()
        pos = score[len(held):]
        neg = score[mi]
        auc = roc_auc_score(np.r_[np.ones(len(pos)), np.zeros(len(neg))],
                            np.r_[pos, neg])
        t1, t5 = np.quantile(score[ri], [0.99, 0.95])
        return float(auc), int((pos > t1).sum()), int((pos > t5).sum())

    if lang == "yo":
        with np.load(args.yoruba_reference, allow_pickle=False) as old:
            for key, value in (("held_rows", held), ("rand_rows", rand),
                               ("match_rows", match), ("qids", qids)):
                np.testing.assert_array_equal(old[key], value)
            for name, score in scores.items():
                ref_auc, ref_h1, ref_h5 = metrics(old[name])
                auc, h1, h5 = metrics(score)
                print(f"CHECK {name} sklearn={(round(ref_auc,5),ref_h1,ref_h5)} "
                      f"gpu={(round(auc,5),h1,h5)}", flush=True)
                if abs(ref_auc - auc) > 0.001 or (ref_h1, ref_h5) != (h1, h5):
                    raise RuntimeError(f"Yoruba validation mismatch: {name}")

    for name, score in scores.items():
        auc, h1, h5 = metrics(score)
        print(f"RESULT lang={lang} method={name} AUROC={auc:.4f} "
              f"TPR@1%={h1}/{len(valid)} TPR@5%={h5}/{len(valid)}", flush=True)

    tmp = out / f"{lang}.tmp.npz"
    np.savez_compressed(tmp, held_rows=held, rand_rows=rand, match_rows=match,
                        qids=qids, **scores)
    os.replace(tmp, out / f"{lang}.npz")


if __name__ == "__main__":
    main()
