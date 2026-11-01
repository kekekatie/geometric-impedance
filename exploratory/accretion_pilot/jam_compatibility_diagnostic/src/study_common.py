#!/usr/bin/env python3
"""
study_common.py -- wiring for the compatibility diagnostic.

Reuses the *validated* jam-repair pilot code (committed at aa371d4, an ancestor
of this branch) rather than duplicating it: engine_bridge (which imports the
frozen engine from EFP_SNAPSHOT), pilot_common, hexflip, phase3_repair. Adds the
new feasibility certifier (feas.py). Nothing in the frozen engine or the pilot is
modified.
"""
from __future__ import annotations
import sys
from pathlib import Path

PILOT_SRC = (Path(__file__).resolve().parents[2] / "jam_repair_pilot" / "src")
if str(PILOT_SRC) not in sys.path:
    sys.path.insert(0, str(PILOT_SRC))

import engine_bridge as EB          # noqa: E402  pulls the frozen engine
import pilot_common as PC           # noqa: E402
import hexflip as HF                # noqa: E402
import phase3_repair as P3          # noqa: E402

Sl, CD, D, L, S, SN = EB.Sl, EB.CD, EB.D, EB.L, EB.S, EB.SN
WIN = EB.WIN
M = EB.M

__all__ = ["EB", "PC", "HF", "P3", "Sl", "CD", "D", "L", "S", "SN", "WIN", "M", "PILOT_SRC"]
