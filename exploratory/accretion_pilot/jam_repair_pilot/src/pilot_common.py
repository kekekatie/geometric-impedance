#!/usr/bin/env python3
"""
pilot_common.py -- shared, faithful replay helpers for the jam-repair pilot.

Everything here drives the FROZEN engine (via engine_bridge). No growth rule,
scheduler, legality test or window is reimplemented. The only new code is
bookkeeping: selecting the closure forks exactly as window_retrodiction.main
did, replaying arms, locating the dead (zero-candidate) frontier sites at a
jam, and extracting the retained active skin.

Determinism: common_state(k, centre) seeds its own RNG from SEED0+k; grow_arm
seeds from the stream value. Replay is therefore bit-identical across runs.
This is deterministic REPLAY of the original implementation, verified against
saved milestones -- it is NOT "zero new computation".
"""
from __future__ import annotations
import json
from pathlib import Path
import engine_bridge as EB

P, W, M = EB.P, EB.W, EB.M
L, D, SN, CD, Sl, S = EB.L, EB.D, EB.SN, EB.CD, EB.Sl, EB.S
dk = EB.dk

MAXWORLDS = 80          # window_retrodiction.main default --maxworlds
NSTREAMS = 2            # window_retrodiction.main default --nstreams
STEPS = 44             # window_retrodiction.main default --steps (the horizon)

# Saved closure records (the milestones we verify replay against).
SAVED_MEASUREMENTS = EB.PAIRED / "results" / "closure_measurements.json"
SAVED_REPORT = EB.PAIRED / "results" / "closure_report.txt"


def streams_for(k, nstreams=NSTREAMS):
    """window_retrodiction.main's stream formula, verbatim."""
    return [P.SEED0 * 1000 + k * 7919 + 101 * i for i in range(nstreams)]


def select_forks(maxworlds=MAXWORLDS, need=22):
    """Reproduce window_retrodiction.main's fork selection + dedup loop exactly.
    Returns an ordered list of dicts: {world, Sstar, edge, mid, cs, meta}."""
    seen = set()
    out = []
    centres = P.centres(maxworlds)
    for k in range(maxworlds):
        if len(out) >= need:
            break
        try:
            cs0 = P.common_state(k, centres[k])
        except Exception:
            continue
        if cs0 is None:
            continue
        Sstar, edge, mid, cs, meta = cs0
        key = W.fork_key(Sstar, mid)      # frozen CD.whole_key neighbourhood key
        if key in seen:
            continue
        seen.add(key)
        out.append(dict(world=k, Sstar=Sstar, edge=edge, mid=mid, cs=cs, meta=meta))
    return out


def grow(Sstar, c, stream, steps=STEPS):
    """Thin pass-through to the frozen grow_arm."""
    return P.grow_arm(Sstar, c, stream, steps)


def departure_step(arm, choice_tile):
    """First step at which the choice tile has left the retained skin (dep), else None.
    Mirrors window_retrodiction.retrodict_arm's dep computation exactly."""
    snaps = arm["snaps"]
    ck = dk(choice_tile)
    return next((s for s in range(1, len(snaps))
                 if ck not in {dk(t) for t in P.skin_of(snaps[s])[0]}), None)


def jam_step(arm):
    """Step index at which the jam was detected, else None. grow_arm appends the
    (unmutated) trigger state then breaks, so nsnaps == jam_step + 1."""
    return (len(arm["snaps"]) - 1) if arm["stop"] == "jam" else None


def dead_sites(full_tiles):
    """At a given full patch, return (frontier_edges, dead_edges, growable_count).
    A 'dead' edge is a frontier edge with zero legal candidates -- the engine jams
    the instant the patient scan reaches one (speed_of_now.patient)."""
    Pat = L.Patch(list(full_tiles))
    fr = Pat.frontier()
    dead = []
    growable = 0
    for e in fr:
        cs = D.candidates(Pat, *e[:3])
        if len(cs) == 0:
            dead.append(e)
        else:
            growable += 1
    return fr, dead, growable


def skin_of(full_tiles):
    """Retained active skin + true frontier, via the frozen prune rule."""
    return P.skin_of(full_tiles)


def ez(z):
    """Serialize a complex vertex."""
    return [z.real, z.imag]


def etile(t):
    """Serialize a decorated half-tile (c, A, B, C)."""
    return [int(t[0])] + [ez(z) for z in t[1:]]


def dtile(rec):
    """Deserialize a half-tile."""
    return (int(rec[0]),) + tuple(complex(x, y) for x, y in rec[1:])


def edge_repr(e):
    """Serialize a frontier edge (p, q, r, owner-tile)."""
    return dict(p=ez(e[0]), q=ez(e[1]), r=ez(e[2]), mid=ez((e[0] + e[1]) / 2))


def load_saved():
    return json.loads(SAVED_MEASUREMENTS.read_text())


def saved_arm(saved, world, opt, stream_idx):
    for r in saved:
        if r["world"] == world:
            for a in r["arms"]:
                if a["opt"] == opt and a["stream"] == stream_idx:
                    return a
    return None
