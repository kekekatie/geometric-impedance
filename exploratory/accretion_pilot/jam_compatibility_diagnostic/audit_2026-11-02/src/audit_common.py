#!/usr/bin/env python3
"""
audit_common.py -- shared wiring for the 2026-11-02 audit of the jam
compatibility diagnostic.

Read-only. Reuses the study's own modules (feas, part4_iis, study_common) and,
through them, the FROZEN engine (imported via engine_bridge from EFP_SNAPSHOT).
Nothing in the frozen engine, the frozen reader, the pilot, or the study's
committed results is modified. All audit outputs go under
`jam_compatibility_diagnostic/audit_2026-11-02/`.

Terminology: the study's "active skin" is the RETAINED BOUNDARY BAND of tiles
kept after enclosed interior tiles are pruned. Existing identifiers (skin_of,
F_skin, ActiveSkin, ...) are preserved verbatim; only new prose uses the longer
phrase.
"""
from __future__ import annotations
import os, sys
from pathlib import Path

# study src (feas.py, part4_iis.py, study_common.py); study_common adds the pilot src
# parents[2] == .../jam_compatibility_diagnostic
STUDY_SRC = (Path(__file__).resolve().parents[2] / "src")
if str(STUDY_SRC) not in sys.path:
    sys.path.insert(0, str(STUDY_SRC))

import study_common as SC          # noqa: E402  pulls the frozen engine (needs EFP_SNAPSHOT)
from study_common import Sl, PC, L, D, M, S, WIN  # noqa: E402
import feas                        # noqa: E402

AUDIT = Path(__file__).resolve().parents[1]        # .../audit_2026-11-02
RESULTS = AUDIT / "results"
FIGURES = AUDIT / "figures"

# The three recorded cases, with (world, stream_index, visible_jam, first_infeasible_step).
CASES = [(7, 0, 23, 9), (7, 1, 23, 9), (5, 0, 42, 17)]


def arm_of(world, si):
    """Deterministic frozen replay for (world, stream_index). Returns the arm dict."""
    forks = SC.P3.load_forks()
    Sstar = forks[world]["Sstar"]; B = forks[world]["cs"][1]
    stream = PC.streams_for(world)[si]
    return PC.grow(Sstar, B, stream, 44), forks


def jam_full_and_skin(world, si, js):
    arm, _ = arm_of(world, si)
    assert arm["stop"] == "jam" and len(arm["snaps"]) == js + 1, \
        f"replay mismatch w{world} s{si}: stop={arm['stop']} nsnaps={len(arm['snaps'])}"
    full = arm["snaps"][-1]
    skin, _ = PC.skin_of(full)
    return arm, full, skin
