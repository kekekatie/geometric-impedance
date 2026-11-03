#!/usr/bin/env python3
"""
af_common.py -- shared wiring for the archive-free scar-continuation experiment
(2026-11-04).

Read-only w.r.t. the frozen engine, the frozen reader, the frozen hollow-band
ActiveSkin engine, the original scar pilot, and Astra's audit. Reuses:
  * the frozen ActiveSkin hollow-band engine (active_skin_engine, radius-2 band
    with an EXPLICIT true-frontier boundary that pruning never pollutes);
  * the jam-repair pilot replay helpers (pilot_common) and frozen reader adapter
    (phase4_readout);
  * the frozen patient scheduler primitives (speed_of_now via figures).

Terminology: "retained boundary band" / "active ring" is the study's active skin.
"""
from __future__ import annotations
import sys, pickle, random
from pathlib import Path

PILOT_SRC = (Path(__file__).resolve().parents[3] / "jam_repair_pilot" / "src")
if str(PILOT_SRC) not in sys.path:
    sys.path.insert(0, str(PILOT_SRC))

import engine_bridge as EB          # noqa: E402  frozen engine (needs EFP_SNAPSHOT); adds EFP to sys.path
import pilot_common as PC           # noqa: E402  faithful replay helpers
import phase4_readout as RD         # noqa: E402  frozen-reader adapter
import active_skin_engine as E      # noqa: E402  FROZEN hollow-band worker engine
import figures as F                 # noqa: E402  gives SN (patient scheduler) + ordered

L, D, S = EB.L, EB.D, EB.S
SN = F.SN
ordered = SN.ordered
dk = PC.dk

HERE = Path(__file__).resolve().parents[1]     # archive_free_2026-11-04
RESULTS = HERE / "results"
FIGURES = HERE / "figures"
INPUT = HERE / "input"

B_JAMS = list(RD.B_JAMS)


def edge_id(p, q):
    return frozenset((L.key(p), L.key(q)))


def frontier_id(e):
    return repr(sorted(edge_id(e[0], e[1])))


def jam_prep(world, si):
    """REPLAY (preparation, clearly labelled): deterministic frozen full-patch
    replay to the recorded jam. Returns the fork, options, stream, jam step, the
    full jam patch, and the retained band derived by the frozen prune rule. This
    is used only to prepare/compare; the worker never consults the full patch."""
    forks = RD.load_forks()
    Sstar = forks[world]["Sstar"]; cs = forks[world]["cs"]; B = cs[1]
    stream = PC.streams_for(world)[si]
    arm = PC.grow(Sstar, B, stream, 44)
    assert arm["stop"] == "jam", f"w{world}-s{si}: expected jam, got {arm['stop']}"
    jam_step = len(arm["snaps"]) - 1
    full_jam = arm["snaps"][jam_step]
    band, _ = PC.skin_of(full_jam)
    return dict(world=world, si=si, Sstar=Sstar, cs=cs, B=B, stream=stream,
                jam_step=jam_step, full_jam=full_jam, band=band)
