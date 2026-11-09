"""
Review item P0-1: the ASR Markdown tables were not updated with the JSON (after the yo merge the md still had 8 questions). Regenerate the md from the JSON (CPU only).
    python regen_asr_md.py                 # rejudge/native, rejudge/none, the two reader directories, the asr_scale directory
asr_summary_excl-bad.md in each directory is first backed up as .md.bak_regen, then rewritten from the JSON; the header notes "rebuilt from JSON".
"""
import glob, json, os, shutil

PROJ = os.environ.get("PROJ", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
R = os.path.join(PROJ, "results", "miracl")
LANGS = ["sw", "te", "yo", "id"]
ORDER = {"clean": 0, "clean_defended": 1, "attacked": 2, "defended_ideal": 3, "defended": 4}


def fmt(m):
    return f"{m[0]:.2f} ({m[1][0]:.2f}–{m[1][1]:.2f})"


def regen(d):
    p = os.path.join(d, "asr_summary_excl-bad.json")
    if not os.path.exists(p):
        return False
    J = json.load(open(p))
    rows = sorted(J["rows"], key=lambda r: (LANGS.index(r["lang"]) if r["lang"] in LANGS else 9, r["variant"], r["form"], ORDER.get(r["cond"], 9)))
    reader = open(os.path.join(d, "READER.txt")).readline().strip() if os.path.exists(os.path.join(d, "READER.txt")) else "Qwen3-14B-AWQ"
    L = [f"# Generation-level attack success rate (reader {os.path.basename(reader)}, rebuilt from JSON; directory {os.path.relpath(d, R)})", "",
         "| lang | variant | form | condition | questions | ASR | ASR (loose) | accuracy | unknown |", "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['lang']} | {r['variant']} | {r['form']} | {r['cond']} | {r['n']} | {fmt(r['ASR'])} | "
                 f"{fmt(r['ASR_loose'])} | {fmt(r['acc'])} | {r['unknown']:.2f} |")
    fp = J.get("fp_stats") or {}
    if fp:
        L += ["", "## Actual cost of false alarms (without attack)", "", "| lang | retrieved benign passages flagged | gold wrongly removed |", "|---|---|---|"]
        for lg in LANGS:
            s = fp.get(lg)
            if s:
                L.append(f"| {lg} | {s['flag_rate_retrieved']:.1%} | {s['gold_flagged']}/{s['gold_in_topk']} |")
    md = os.path.join(d, "asr_summary_excl-bad.md")
    if os.path.exists(md):
        shutil.copy(md, md + ".bak_regen")
    open(md, "w").write("\n".join(L) + "\n")
    n_yo = {r["n"] for r in rows if r["lang"] == "yo" and r["cond"] == "clean"}
    print(f"{os.path.relpath(d, R)}: rebuilt (yo clean questions {n_yo})")
    return True


def main():
    for d in [os.path.join(R, "rejudge", s) for s in ("native", "none")] + sorted(glob.glob(os.path.join(R, "reader_*"))) \
             + sorted(glob.glob(os.path.join(R, "asr_scale_*"))):
        if os.path.isdir(d) and not d.endswith("_yo_no_unknown"):
            regen(d)


if __name__ == "__main__":
    main()
