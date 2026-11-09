"""
Retrieval-level effect of MIRACL poisoning: language x poison variant x question prefix x number injected x corpus size.
    python ml_attack.py                         # all languages; uses poison.jsonl if present (includes trans), else poison_gen.jsonl
    python ml_attack.py --sizes full 131924     # also test on the corpus downsampled to the sw size (scale comparison)
Method (saves time): the corpus is searched once for the top-k, then merged with the poison scores to take the top-5; this is exactly equivalent to inserting the poison into the corpus.
  variants native / trans / en; forms bb (question text + body) / adv (body only)
  injection multi (5 per question, all questions' poisons in the corpus at once) / single (only the first one per question)
  size full = original corpus; <n> = random n passages + all dev gold passages (same as ml_eval_retrieval.py --subsample)
Metrics: hit@5 (a poison of this question is in the top-5), avg@5 (number of this question's poisons in the top-5), top1, share of gold pushed out of the top-5
Output: results/miracl/attack_summary.json, attack_summary.md, and per-question details results/miracl/<lang>/attack_detail.jsonl
"""
import argparse, json, os, time

import numpy as np
import torch
from sentence_transformers import SentenceTransformer

from ml_common import (LANGS, M3_PATH, ROOT, gpu_topk, load_corpus_emb, load_qrels, load_query_emb,
                       ml_results)
from ml_eval_retrieval import subsample_rows

VARIANTS = ["native", "trans", "en"]


def load_items(lang):
    rd = ml_results(lang)
    for name in ("poison.jsonl", "poison_gen.jsonl"):
        p = os.path.join(rd, name)
        if os.path.exists(p):
            items = [json.loads(l) for l in open(p)]
            return items, name
    return [], None


def texts_of(it, variant, form):
    adv = it.get(f"{variant}_adv") or []
    return [f"{it['question']} {t}" for t in adv] if form == "bb" else list(adv)


def merge_top5(Sc, Ic, Sp, owner, k=5):
    """Sc/Ic: corpus top-k (rows >= 0); Sp: query x poison scores; owner: question index of each poison (poison rows encoded as -1-j)"""
    S = np.concatenate([Sc, Sp], 1)
    I = np.concatenate([Ic, -1 - np.arange(Sp.shape[1])[None, :].repeat(Sc.shape[0], 0)], 1)
    order = np.argsort(-S, 1, kind="stable")[:, :k]
    return np.take_along_axis(I, order, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", nargs="+", default=LANGS)
    ap.add_argument("--sizes", nargs="+", default=["full", "131924"],
                    help="full or a number of passages; sizes larger than the corpus are skipped")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    model = SentenceTransformer(M3_PATH, device="cuda").half()
    model.max_seq_length = 512
    enc = lambda xs: model.encode(xs, batch_size=128, normalize_embeddings=True,
                                  convert_to_numpy=True, show_progress_bar=False).astype(np.float16)
    rows, md = [], []

    for lang in args.lang:
        items, src = load_items(lang)
        if not items:
            print(f"[{lang}] no poison file, skipped")
            continue
        corpus, cids = load_corpus_emb(lang)
        N = corpus.shape[0]
        qemb, qid2row = load_query_emb(lang)
        qrels = load_qrels(lang, "dev")
        cid2row = {c: i for i, c in enumerate(cids)}
        Q = qemb[[qid2row[it["qid"]] for it in items]]
        gold_rows = [{cid2row[d] for d in it["gold_ids"] if d in cid2row} for it in items]
        all_dev_gold = np.array(sorted({cid2row[d] for q in qrels if q in qid2row for d in qrels[q] if d in cid2row}))
        print(f"\n[{lang}] {len(items)} questions ({src}), corpus {N:,}", flush=True)

        # encode all poison texts first
        P, owner = {}, {}
        for v in VARIANTS:
            for f in ("bb", "adv"):
                sel = [(j, t) for j, it in enumerate(items) for t in texts_of(it, v, f)]
                if sel:
                    P[(v, f)] = enc([t for _, t in sel])
                    owner[(v, f)] = np.array([j for j, _ in sel])
        n_has = {v: sum(bool(it.get(f"{v}_adv")) for it in items) for v in VARIANTS}

        detail = [{"qid": it["qid"]} for it in items]
        for size in args.sizes:
            if size == "full":
                blocks, rowmap, tag = [corpus], None, "full"
            else:
                n = int(size)
                if n >= N:
                    continue
                rowmap = subsample_rows(N, n, all_dev_gold, args.seed)
                blocks, tag = [np.asarray(corpus[rowmap])], f"sub{n}"
            t0 = time.time()
            Sc, Ic = gpu_topk(blocks, Q, 5)
            if rowmap is not None:
                Ic = rowmap[Ic]
            gold_before = np.array([bool(set(Ic[j]) & gold_rows[j]) for j in range(len(items))])
            for (v, f), Pv in P.items():
                own_all = owner[(v, f)]
                for mode in ("multi", "single"):
                    if mode == "single":     # keep only the first poison per question
                        first = np.array([np.flatnonzero(own_all == j)[0] for j in np.unique(own_all)])
                        Pm, own = Pv[first], own_all[first]
                    else:
                        Pm, own = Pv, own_all
                    Sp = (torch.from_numpy(Q.astype(np.float32)) @ torch.from_numpy(Pm.astype(np.float32)).T).numpy()
                    top = merge_top5(Sc, Ic, Sp, own)
                    qs = np.unique(own)      # questions that have a poison for this variant
                    hit, cnt, top1, gold_after = [], [], [], []
                    for j in qs:
                        mine = {-1 - p for p in np.flatnonzero(own == j)}
                        h = [int(x) in mine for x in top[j]]
                        hit.append(any(h)); cnt.append(sum(h)); top1.append(h[0])
                        gold_after.append(bool({int(x) for x in top[j] if x >= 0} & gold_rows[j]))
                        detail[j][f"{tag}/{v}/{f}/{mode}/hit5"] = bool(any(h))
                    r = {"lang": lang, "size": tag, "corpus": int(len(rowmap) if rowmap is not None else N),
                         "variant": v, "form": f, "mode": mode, "n_q": int(len(qs)),
                         "hit@5": float(np.mean(hit)), "avg@5": float(np.mean(cnt)), "top1": float(np.mean(top1)),
                         "gold@5_before": float(gold_before[qs].mean()), "gold@5_after": float(np.mean(gold_after))}
                    rows.append(r)
            print(f"  {tag}: {time.time() - t0:.1f} s", flush=True)
        with open(os.path.join(ml_results(lang), "attack_detail.jsonl"), "w") as fo:
            for d in detail:
                fo.write(json.dumps(d) + "\n")
        print(f"  questions with a poison per variant: {n_has}")

    out = os.path.join(ROOT, "results", "miracl")
    json.dump(rows, open(os.path.join(out, "attack_summary.json"), "w"), indent=1)
    head = f"| lang | corpus | variant | form | injection | questions | hit@5 | avg@5 | top1 | gold@5 before -> after |\n|---|---|---|---|---|---|---|---|---|---|"
    lines = [head] + [f"| {r['lang']} | {r['corpus']:,} | {r['variant']} | {r['form']} | {r['mode']} | {r['n_q']} | "
                      f"{r['hit@5']:.2f} | {r['avg@5']:.2f} | {r['top1']:.2f} | {r['gold@5_before']:.2f}→{r['gold@5_after']:.2f} |"
                      for r in rows]
    open(os.path.join(out, "attack_summary.md"), "w").write("\n".join(lines) + "\n")
    print("\n" + "\n".join(lines))
    print(f"\nsaved {out}/attack_summary.md / .json")


if __name__ == "__main__":
    main()
