#!/usr/bin/env python3
"""
scar_common.py -- shared wiring for the scar-continuation pilot (2026-11-03).

Read-only w.r.t. the frozen engine, the frozen reader, and all prior pilot/audit
directories. Reuses the jam-repair pilot's faithful replay helpers (engine_bridge,
pilot_common, phase4_readout) and the FROZEN standalone reader (skin_reader.py).
Nothing historical is modified.

Terminology: "retained boundary band" / "active ring" is the study's active skin.
"""
from __future__ import annotations
import sys
from pathlib import Path

PILOT_SRC = (Path(__file__).resolve().parents[2] / "jam_repair_pilot" / "src")
if str(PILOT_SRC) not in sys.path:
    sys.path.insert(0, str(PILOT_SRC))

import engine_bridge as EB          # noqa: E402  frozen engine (needs EFP_SNAPSHOT)
import pilot_common as PC           # noqa: E402  faithful replay helpers
import phase4_readout as RD         # noqa: E402  frozen-reader adapter (build_payload/run_reader/classify)

Sl, L, D, S = EB.Sl, EB.L, EB.D, EB.S
SN = EB.SN                          # frozen patient scheduler module (speed_of_now)
ordered = SN.ordered                # deterministic candidate ordering (frozen)
WIN = EB.WIN
dk = PC.dk

# frozen standalone reader, imported read-only for direct lift diagnostics/tests
READER_DIR = EB.EFP / "archive-free-reader"
if str(READER_DIR) not in sys.path:
    sys.path.insert(0, str(READER_DIR))
import skin_reader as SR            # noqa: E402

HERE = Path(__file__).resolve().parents[1]     # scar_continuation_pilot
RESULTS = HERE / "results"
FIGURES = HERE / "figures"

# the 11 recorded B-jams (world, stream_index), from phase4_readout
B_JAMS = list(RD.B_JAMS)


def ekey(p, q):
    return frozenset((L.key(p), L.key(q)))


def jam_state(world, si):
    """Deterministic frozen replay to the recorded jam. Returns a dict with the
    full jam patch, the retained boundary band (active ring), the true-frontier
    dead sites, the fork S*, A/B options, stream, and jam step."""
    forks = RD.load_forks()
    Sstar = forks[world]["Sstar"]; cs = forks[world]["cs"]; B = cs[1]
    stream = PC.streams_for(world)[si]
    arm = PC.grow(Sstar, B, stream, 44)
    assert arm["stop"] == "jam", f"w{world}-s{si}: expected jam, got {arm['stop']}"
    jam_step = len(arm["snaps"]) - 1
    full = arm["snaps"][-1]
    band, frontier = PC.skin_of(full)
    fr, dead, growable = PC.dead_sites(full)
    return dict(world=world, si=si, stream=stream, jam_step=jam_step,
                Sstar=Sstar, cs=cs, B=B, full=full, band=band,
                true_frontier=fr, dead=dead, n_growable=growable)


def read_patch(Sstar, cs, tiles):
    """Run the FROZEN reader on a patch (or connected sub-arc) under the fork gauge
    and A/B hypotheses. Returns (outcome, detail, raw) via the frozen adapter."""
    payload = RD.build_payload(Sstar, cs, list(tiles))
    raw = RD.run_reader(payload)
    outcome, detail = RD.classify(raw)
    return outcome, detail, raw
