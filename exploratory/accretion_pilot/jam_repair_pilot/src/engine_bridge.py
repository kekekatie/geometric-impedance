#!/usr/bin/env python3
"""
engine_bridge.py -- import the *frozen* historical growth engine and closure
instrument, so this pilot replays the closure forks with the exact original
implementation (not a reimplementation).

The closure study was produced on branch `codex/manuscript-reconciliation`
at commit 84130b97f5044197392e72cd53e0e71f81b043f3, under
  exploratory/accretion_pilot/expansion_front_paper/

Reproduction (from repo root):
  git worktree add --detach <SNAPSHOT_DIR> 84130b97f5044197392e72cd53e0e71f81b043f3
  export EFP_SNAPSHOT=<SNAPSHOT_DIR>/exploratory/accretion_pilot/expansion_front_paper
  python <this pilot>/src/<script>.py

If EFP_SNAPSHOT is unset we fall back to a sibling worktree at
  ~/efp-snapshot/exploratory/accretion_pilot/expansion_front_paper

Nothing here mutates the snapshot; it is imported read-only.
"""
from __future__ import annotations
import os, sys
from pathlib import Path

SNAPSHOT_COMMIT = "84130b97f5044197392e72cd53e0e71f81b043f3"

def _efp() -> Path:
    env = os.environ.get("EFP_SNAPSHOT")
    if env:
        p = Path(env).expanduser().resolve()
        if p.is_dir():
            return p
        raise SystemExit(f"EFP_SNAPSHOT={env} is not a directory")
    for base in (Path.home(), Path("/home/user")):
        cand = base / "efp-snapshot" / "exploratory" / "accretion_pilot" / "expansion_front_paper"
        if cand.is_dir():
            return cand.resolve()
    raise SystemExit(
        "Frozen snapshot not found. Create it with:\n"
        f"  git worktree add --detach ~/efp-snapshot {SNAPSHOT_COMMIT}\n"
        "or set EFP_SNAPSHOT to <worktree>/exploratory/accretion_pilot/expansion_front_paper"
    )

EFP = _efp()
PAIRED = EFP / "paired-front"
CRC = EFP / "corner-response-catalogue"
for p in (str(PAIRED), str(EFP), str(CRC)):
    if p not in sys.path:
        sys.path.insert(0, p)

# Historical modules (frozen). figures reads argv at import, so neutralise it.
_argv = sys.argv[:]
try:
    sys.argv = sys.argv[:1]
    import figures as F            # noqa: E402  pulls settled_test -> CD,L,D,Sl,SN,S
    import paired_front as P       # noqa: E402  common_state, grow_arm, skin_of
    import perp_map as M           # noqa: E402  lift, perp, edge_dir
    import window_retrodiction as W # noqa: E402  F_in_gauge, fork selection, stream formula
finally:
    sys.argv = _argv

# Re-export the engine primitives everyone uses.
Sl, CD, D, L, S, SN = F.Sl, F.CD, F.D, F.L, F.S, F.SN
WIN = Sl.WIN
dk = P.dk

__all__ = ["F", "P", "M", "W", "Sl", "CD", "D", "L", "S", "SN", "WIN", "dk",
           "EFP", "PAIRED", "CRC", "SNAPSHOT_COMMIT"]
