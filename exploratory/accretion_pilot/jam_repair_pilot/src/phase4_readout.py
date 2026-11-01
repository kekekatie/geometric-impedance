#!/usr/bin/env python3
"""
phase4_readout.py -- Phase 4: A/B readout after (attempted) repair.

Uses the ORIGINAL historical A/B candidate regions, reference convention, reader
and tolerances. Runs the FROZEN standalone reader (archive-free-reader/
skin_reader.py) in an isolated subprocess on a fresh serialization of surviving
geometry:

  * PRE-REPAIR readout: the jam-trigger retained skin (the final usable
    checkpoint for a jammed arm);
  * POST-REPAIR readout: the resumed skin, only for cases Phase 3 actually
    repaired (if any).

Choice-tile fate is tracked separately (departed under pruning / removed or
altered by the repair / still retained). Outcomes are reported in the five
categories: correct, wrong, ambiguous, empty/incompatible, unreconstructible.
The reader's scientific decision rule is unchanged; only a neutral payload
adapter is new.

Outputs under ../results/phase4/: per-case reader output + phase4_report.txt.
"""
from __future__ import annotations
import json, pickle, subprocess, sys, tempfile
from pathlib import Path
import pilot_common as PC
from pilot_common import Sl, CD, L, S
import engine_bridge as EB
WIN = EB.WIN

OUT = Path(__file__).resolve().parent.parent / "results" / "phase4"
FORKS = Path(__file__).resolve().parent.parent / "results" / "baseline" / "forks.pkl"
JAMDIR = Path(__file__).resolve().parent.parent / "results" / "baseline" / "jam_cases"
P3DIR = Path(__file__).resolve().parent.parent / "results" / "phase3"
READER = EB.EFP / "archive-free-reader" / "skin_reader.py"

B_JAMS = [(5, 0), (7, 0), (7, 1), (15, 0), (19, 0), (19, 1), (21, 0), (21, 1), (28, 0), (28, 1), (29, 1)]


def load_forks():
    data = pickle.loads(FORKS.read_bytes())
    return {w: dict(Sstar=[(int(t[0]),) + tuple(t[1:]) for t in d["Sstar"]],
                    cs=[(int(c[0]),) + tuple(c[1:]) for c in d["cs"]]) for w, d in data.items()}


def cm_rows(cm):
    return [[int(r), int(i), float(v)] for (r, i), v in sorted(cm.items())]


def run_reader(payload):
    """Invoke the frozen reader exactly as verify_reader does: fresh -I -S process,
    empty cwd, JSON on stdin."""
    with tempfile.TemporaryDirectory(prefix="reader-") as cwd:
        p = subprocess.run([sys.executable, "-I", "-S", str(READER)],
                           input=json.dumps(payload), text=True, capture_output=True,
                           cwd=cwd, timeout=120)
    if p.returncode:
        return dict(status="process_error", stderr=p.stderr[-500:])
    return json.loads(p.stdout)


def build_payload(Sstar, cs, skin_tiles):
    rank = Sl.rank_of(Sstar)
    origin = next(p for t in Sstar for p, q in ((t[1], t[2]), (t[2], t[3]), (t[3], t[1]))
                  if abs(abs(q - p) - S) < 1e-4 * S)
    hypotheses = [CD.after_first(Sstar, c, rank) for c in cs]   # C^A, C^B (original)
    windows = [dict(normals=n.tolist(), h=float(h)) for n, h in WIN]
    payload = dict(schema=1,
                   tiles=[[t[0]] + [[z.real, z.imag] for z in t[1:]] for t in skin_tiles],
                   edge_length=float(S), origin=[origin.real, origin.imag],
                   rank={str(k): int(v) for k, v in rank.items()},
                   windows=windows, hypotheses=[cm_rows(c) for c in hypotheses])
    return payload


def classify(result):
    """Map the frozen reader output to the five Phase-4 categories.
    true index for B is 1; A is 0."""
    if result.get("status") != "reconstructed":
        return "unreconstructible", result.get("reason") or result.get("status")
    sel = result.get("selected")
    if sel == 1:
        return "correct", None            # B retrodicted
    if sel == 0:
        return "wrong", None              # A retrodicted
    # selected is None: distinguish ambiguous vs empty/incompatible
    area = result.get("area", 0.0)
    ints = result.get("intersections", [])
    ncompat = sum(1 for v in ints if v > 1e-9)
    if area <= 1e-12 or ncompat == 0:
        return "empty_incompatible", f"area={area:.3e} ncompat={ncompat}"
    return "ambiguous", f"ncompat={ncompat}"


def dtile(rec):
    return (int(rec[0]),) + tuple(complex(x, y) for x, y in rec[1:])


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    forks = load_forks()
    rows = []
    for (w, si) in B_JAMS:
        tag = f"w{w}-B-s{si}"
        case = json.loads((JAMDIR / f"{tag}.json").read_text())
        skin = [dtile(t) for t in case["repair_worker_input"]["retained_skin"]]
        Sstar = forks[w]["Sstar"]; cs = forks[w]["cs"]
        B = cs[1]; Bk = PC.dk(B)
        b_in_skin = case["choice_tile"]["present_in_retained_skin"]
        fate = "retained_in_skin" if b_in_skin else "departed_under_pruning"

        payload = build_payload(Sstar, cs, skin)
        result = run_reader(payload)
        outcome, detail = classify(result)
        (OUT / f"{tag}-pre.json").write_text(json.dumps(
            dict(reader=result, outcome=outcome, detail=detail), indent=2, default=float))

        # post-repair readout only if Phase 3 repaired this case
        post = None
        p3f = P3DIR / f"{tag}.json"
        if p3f.exists():
            p3 = json.loads(p3f.read_text())
            if p3.get("repair") and p3["repair"].get("unjammed_local"):
                post = dict(note="Phase 3 repaired this case; post-repair readout would apply",
                            outcome_p3=p3.get("outcome"))
        rows.append(dict(case=tag, choice_tile_fate=fate,
                         pre_repair_outcome=outcome, pre_detail=detail,
                         reader_status=result.get("status"),
                         reader_selected=result.get("selected"),
                         reader_area=result.get("area"),
                         reader_intersections=result.get("intersections"),
                         post=post))

    (OUT / "phase4_results.json").write_text(json.dumps(rows, indent=2, default=float))

    from collections import Counter
    oc = Counter(r["pre_repair_outcome"] for r in rows)
    fates = Counter(r["choice_tile_fate"] for r in rows)
    lines = []
    lines.append("Phase 4 -- A/B readout on surviving geometry at the jam-trigger checkpoint (pre-repair)")
    lines.append("Frozen reader (archive-free-reader/skin_reader.py), original gauge, hypotheses C^A,C^B.")
    lines.append(f"reader: {READER}")
    lines.append("")
    lines.append(f"{'case':>12} {'fate':>22} {'outcome':>18} {'selected':>8} {'area':>10}  detail")
    for r in rows:
        ar = r["reader_area"]
        lines.append(f"{r['case']:>12} {r['choice_tile_fate']:>22} {r['pre_repair_outcome']:>18} "
                     f"{str(r['reader_selected']):>8} {('%.3e'%ar) if isinstance(ar,(int,float)) else str(ar):>10}  {r['pre_detail'] or ''}")
    lines.append("")
    lines.append("outcome tally (B is the committed/true option; correct = reader selects B):")
    for k, v in sorted(oc.items()):
        lines.append(f"  {k}: {v}")
    lines.append("choice-tile fate tally:")
    for k, v in sorted(fates.items()):
        lines.append(f"  {k}: {v}")
    lines.append("")
    lines.append("Note: an empty F or unreconstructible readout at a jammed checkpoint is NOT by itself")
    lines.append("proof that historical information has vanished (the jam gives F(full)=0 globally, and the")
    lines.append("4-layer slab has a horizon as the front advances). Reported as its own category.")
    txt = "\n".join(lines)
    (OUT / "phase4_report.txt").write_text(txt + "\n")
    print(txt)


if __name__ == "__main__":
    main()
