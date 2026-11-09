"""
yo expansion step 4 (GPU, about 30-40 minutes): after merging new questions into poison.jsonl, rerun all yo downstream steps.
Problem: when ml_attack / ml_detect / ml_asr run for a single language, they overwrite the global summary files (attack_summary.json,
detect_summary*.json, asr_summary_excl-bad.json, asr_answers_excl-bad.jsonl) with yo only.
Approach: back up these files before each step, then replace the yo rows in the backup with the new ones, keep other languages unchanged, and write back.
Per-language files (attack_detail.jsonl, detect_feats*.npz) are already separated by language and are updated directly.
Steps
  1. ml_attack.py --lang yo --sizes full 131924 45000
  2. ml_detect.py --lang yo --boot 0 (features for full, _sub131924, _sub45000)
  3. ml_asr.py --lang yo, once with native judgments and once without exclusion, merged into rejudge/native, rejudge/none
     (the global asr_* use the old review and are left unchanged)
  4. scale robustness (scale_seeds.py --lang yo, old yo results deleted first)
  5. defense baselines (ml_baselines.py --lang yo)
Completed steps are recorded in results/miracl/yo/rerun_done.json and skipped on rerun after interruption.
    python yo_rerun.py
Afterwards (CPU is enough): bash rejudge_cpu.sh, python rejudge_compare.py, python scale_seeds_analyze.py,
python density_analyze.py, python ml_baselines_summary.py, python ml_paired_variants.py (printed as a reminder)
"""
import json, os, shutil, subprocess, sys, time

PROJ = os.environ.get("PROJ", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
R = os.path.join(PROJ, "results", "miracl")
CODE = os.path.join(PROJ, "code")
DONE = os.path.join(R, "yo", "rerun_done.json")
J = os.path.join(R, "review_judgments_native.json")
ENV = dict(os.environ, VLLM_CACHE_ROOT=os.environ.get("VLLM_CACHE_ROOT", os.path.expanduser("~/.cache/vllm")),
           TORCHINDUCTOR_CACHE_DIR=os.environ.get("TORCHINDUCTOR_CACHE_DIR", os.path.expanduser("~/.cache/inductor")))


def run(cmd):
    print(f"\n+ {' '.join(cmd)}", flush=True)
    subprocess.run(cmd, cwd=CODE, env=ENV, check=True)


def merge_list_json(name, backup):
    """Global json files are lists of rows (each with lang): replace the yo rows in the backup with the new yo rows"""
    p = os.path.join(R, name)
    new = json.load(open(p))
    old = json.load(open(backup))
    merged = [r for r in old if r.get("lang") != "yo"] + [r for r in new if r.get("lang") == "yo"]
    json.dump(merged, open(p, "w"), indent=1, ensure_ascii=False)


def guarded(step, cmd, globals_):
    done = json.load(open(DONE)) if os.path.exists(DONE) else []
    if step in done:
        print(f"\n== {step}: already done, skipped", flush=True); return
    print(f"\n== {step} (elapsed {int(time.time() - T0) // 60} min)", flush=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    baks = {}
    for g in globals_:
        p = os.path.join(R, g)
        if os.path.exists(p):
            baks[g] = p + f".bak_yo_{stamp}"
            shutil.copy(p, baks[g])
    try:
        for c in cmd:
            run(c)
    except subprocess.CalledProcessError:
        for g, b in baks.items():            # on error: restore the global files
            shutil.copy(b, os.path.join(R, g))
        sys.exit(f"{step} failed; global summary files restored. Fix and rerun python yo_rerun.py")
    for g, b in baks.items():
        if g.endswith(".json") and g.startswith(("attack_summary", "detect_summary")):
            merge_list_json(g, b)
        elif g == "asr_summary_excl-bad.json":
            new, old = json.load(open(os.path.join(R, g))), json.load(open(b))
            old["rows"] = [r for r in old["rows"] if r["lang"] != "yo"] + [r for r in new["rows"] if r["lang"] == "yo"]
            old.setdefault("fp_stats", {})["yo"] = new.get("fp_stats", {}).get("yo")
            json.dump(old, open(os.path.join(R, g), "w"), indent=1, ensure_ascii=False)
        elif g == "asr_answers_excl-bad.jsonl":
            new = [l for l in open(os.path.join(R, g)) if json.loads(l)["lang"] == "yo"]
            old = [l for l in open(b) if json.loads(l)["lang"] != "yo"]
            open(os.path.join(R, g), "w").writelines(old + new)
        elif g.endswith(".md"):
            shutil.copy(b, os.path.join(R, g))  # md files are only human-readable tables; keep the old version so that not only yo remains; json is authoritative
    json.dump(done + [step], open(DONE, "w"))
    print(f"== {step} done (global summaries merged: other languages unchanged, yo replaced with new results)", flush=True)


ASR_FILES = ["asr_summary_excl-bad.json", "asr_summary_excl-bad.md", "asr_answers_excl-bad.jsonl"]


def asr_into(setname, judg):
    """Global asr_* are old-review results and must not change. After running yo, merge the yo rows into rejudge/<setname>/ and restore the global files"""
    step = f"3 generation-level ASR ({setname})"
    done = json.load(open(DONE)) if os.path.exists(DONE) else []
    if step in done:
        print(f"\n== {step}: already done, skipped", flush=True); return
    print(f"\n== {step} (elapsed {int(time.time() - T0) // 60} min)", flush=True)
    T = os.path.join(R, "rejudge", setname)
    if not os.path.exists(os.path.join(T, "asr_summary_excl-bad.json")):
        sys.exit(f"no ASR results under {T}; cannot merge")
    stamp = time.strftime("%Y%m%d_%H%M%S")
    baks = {}
    for g in ASR_FILES:
        p = os.path.join(R, g)
        if os.path.exists(p):
            baks[g] = p + f".bak_yo_{stamp}"; shutil.copy(p, baks[g])
        shutil.copy(os.path.join(T, g), os.path.join(T, g + f".bak_yo_{stamp}"))
    try:
        run([sys.executable, "ml_asr.py", "--lang", "yo", "--exclude", "bad", "--judgments", judg,
             "--gpu_util", "0", "--max_len", "0"])
        new = json.load(open(os.path.join(R, "asr_summary_excl-bad.json")))
        old = json.load(open(os.path.join(T, "asr_summary_excl-bad.json")))
        old["rows"] = [r for r in old["rows"] if r["lang"] != "yo"] + [r for r in new["rows"] if r["lang"] == "yo"]
        old.setdefault("fp_stats", {})["yo"] = new.get("fp_stats", {}).get("yo")
        json.dump(old, open(os.path.join(T, "asr_summary_excl-bad.json"), "w"), indent=1, ensure_ascii=False)
        keep = [l for l in open(os.path.join(T, "asr_answers_excl-bad.jsonl")) if json.loads(l)["lang"] != "yo"]
        add = [l for l in open(os.path.join(R, "asr_answers_excl-bad.jsonl")) if json.loads(l)["lang"] == "yo"]
        open(os.path.join(T, "asr_answers_excl-bad.jsonl"), "w").writelines(keep + add)
    except subprocess.CalledProcessError:
        sys.exit(f"{step} failed (global files are restored below)")
    finally:
        for g, b in baks.items():
            shutil.copy(b, os.path.join(R, g))
    json.dump(done + [step], open(DONE, "w"))
    print(f"== {step} done: new yo ASR merged into {T} (md table not updated, json is authoritative); global files restored", flush=True)


T0 = time.time()


def main():
    py = sys.executable
    n = sum(1 for _ in open(os.path.join(R, "yo", "poison.jsonl")))
    print(f"yo/poison.jsonl now has {n} questions", flush=True)
    guarded("1 attack", [[py, "ml_attack.py", "--lang", "yo", "--sizes", "full", "131924", "45000"]],
            ["attack_summary.json", "attack_summary.md"])
    guarded("2 detection features", [[py, "ml_detect.py", "--lang", "yo", "--boot", "0"],
                        [py, "ml_detect.py", "--lang", "yo", "--boot", "0", "--subsample", "131924"],
                        [py, "ml_detect.py", "--lang", "yo", "--boot", "0", "--subsample", "45000"]],
            [f"detect_summary{s}.{e}" for s in ("", "_sub131924", "_sub45000") for e in ("json", "md")])
    empty = os.path.join(R, "review_judgments_empty.json")
    if not os.path.exists(empty):
        open(empty, "w").write("{}")
    asr_into("native", J)          # main results (native judgments)
    asr_into("none", empty)        # robustness: no exclusion
    ss = os.path.join(R, "scale_seeds", "yo")
    if os.path.isdir(ss) and "4 scale robustness" not in (json.load(open(DONE)) if os.path.exists(DONE) else []):
        shutil.move(ss, ss + f"_old_{time.strftime('%Y%m%d_%H%M%S')}")
    guarded("4 scale robustness", [[py, "scale_seeds.py", "--lang", "yo"]], [])
    bp = os.path.join(R, "baselines", "yo.npz")
    if os.path.exists(bp) and "5 defense baselines" not in (json.load(open(DONE)) if os.path.exists(DONE) else []):
        shutil.move(bp, bp + f".old_{time.strftime('%Y%m%d_%H%M%S')}")
    guarded("5 defense baselines", [[py, "ml_baselines.py", "--lang", "yo"]], [])
    print(f"\nAll done, total time {int(time.time() - T0) // 60} min. Afterwards (CPU is enough) run in order:\n"
          "  bash rejudge_cpu.sh && python rejudge_compare.py\n"
          "  python scale_seeds_analyze.py && python density_analyze.py\n"
          "  python ml_baselines_summary.py && python ml_paired_variants.py")


if __name__ == "__main__":
    main()
