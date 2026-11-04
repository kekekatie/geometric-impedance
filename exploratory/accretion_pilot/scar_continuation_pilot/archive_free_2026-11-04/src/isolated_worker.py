#!/usr/bin/env python3
"""
isolated_worker.py -- serialization, cold-restart, and the spawned-process worker.

The archive-free worker must depend ONLY on the declared retained state (band
tiles + explicit true-frontier boundary + PRNG state + scar set). This module:
  * serializes that state (and nothing else — no full patch, no deleted tiles);
  * rebuilds an ActiveSkin from it (restoring the EXPLICIT boundary rather than
    re-deriving it from tiles, which would mistake the pruned cavity for frontier);
  * runs the worker in a SPAWNED process that receives only the serialized state
    and STEP/STOP, and sends back only band state.
"""
from __future__ import annotations
import random, multiprocessing as mp
import af_common as AF
from af_common import E, L, dk
import sys as _sys
from pathlib import Path as _Path
_PILOT = str(_Path(__file__).resolve().parents[3] / "scar_continuation_pilot" / "src")
if _PILOT not in _sys.path:
    _sys.path.insert(0, _PILOT)
import scar_continuation as SCN     # audited patient_scar


# ----------------------------- serialization -----------------------------
def etile(t):
    return [int(t[0])] + [[z.real, z.imag] for z in t[1:]]


def dtile(rec):
    return (int(rec[0]),) + tuple(complex(x, y) for x, y in rec[1:])


def ez(z):
    return [z.real, z.imag]


def serialize_state(skin, rng, scars):
    """The COMPLETE declared retained state. Audited to contain no full patch,
    deleted-tile list, archived lift, candidate menu, or hypothesis."""
    boundary = []
    for k, (p, q, r, owner) in skin.boundary.items():
        boundary.append(dict(p=ez(p), q=ez(q), r=ez(r),
                             owner=(etile(owner) if owner is not None else None)))
    return dict(schema="archive_free_retained_state/1",
                radius=skin.radius,
                tiles=[etile(t) for t in skin.tris],
                boundary=boundary,
                rng_state=list(rng.getstate()),
                scars=[sorted(list(ek)) for ek in scars],
                fields=["radius", "tiles", "boundary", "rng_state", "scars"])


def rebuild_skin(state):
    """Cold-start an ActiveSkin from the serialized retained state, restoring the
    EXPLICIT true-frontier boundary (not re-derived from tiles)."""
    tiles = [dtile(rec) for rec in state["tiles"]]
    P = E.ActiveSkin.__new__(E.ActiveSkin)
    P.boundary = {}; P.radius = state["radius"]; P.additions = []
    L.Patch.__init__(P, tiles)                 # builds tris/edges/V index (with cavity artefacts)
    bnd = {}
    for rec in state["boundary"]:
        p = complex(*rec["p"]); q = complex(*rec["q"]); r = complex(*rec["r"])
        owner = dtile(rec["owner"]) if rec.get("owner") else None
        bnd[AF.edge_id(p, q)] = (p, q, r, owner)
    P.boundary = bnd                           # override: the declared true frontier
    P.additions = []
    return P


def rebuild_rng(state):
    rng = random.Random()
    st = state["rng_state"]
    rng.setstate((st[0], tuple(st[1]), st[2]))
    return rng


def rebuild_scars(state):
    return {frozenset(tuple(v) for v in ek) for ek in state["scars"]}


# --------------------------- spawned-process worker ---------------------------
def _worker_proc(conn, state):
    """Runs in a SPAWNED process. Receives only the serialized retained state and
    STEP/STOP. Holds no full patch. Sends back only band state."""
    try:
        P = rebuild_skin(state); rng = rebuild_rng(state); scars = rebuild_scars(state)
        del state
        conn.send(dict(kind="ready",
                       frontier=[AF.frontier_id(e) for e in P.frontier()],
                       retained=len(P.tris)))
        while True:
            cmd = conn.recv()
            if cmd == "STOP":
                break
            if cmd != "STEP":
                raise ValueError("only STEP/STOP")
            before = E.inventory(P)
            P.additions = []
            st, n, kind, newly, illegal = SCN.patient_scar(P, rng, scars, verify_legal=True)
            placed = [dk(t) for t in P.additions]; P.additions = []
            dropped = P.prune()
            conn.send(dict(kind="step", status=st, mode=kind, n=n,
                           before=before, placed=placed, dropped=dropped,
                           frontier=[AF.frontier_id(e) for e in P.frontier()],
                           retained=len(P.tris), scars=len(scars), newly=len(newly),
                           illegal=illegal))
    except Exception:
        import traceback
        conn.send(dict(kind="error", traceback=traceback.format_exc()))
    finally:
        conn.close()


def run_spawned(state, n_steps):
    """Drive the spawned worker for n_steps, returning its per-step messages. The
    controller sends only STEP/STOP; it never sends geometry after the initial
    serialized state."""
    ctx = mp.get_context("spawn")
    parent, child = ctx.Pipe()
    proc = ctx.Process(target=_worker_proc, args=(child, state))
    proc.start(); child.close()
    out = []
    try:
        ready = parent.recv()
        if ready.get("kind") == "error":
            raise RuntimeError(ready["traceback"])
        out.append(ready)
        for _ in range(n_steps):
            parent.send("STEP")
            msg = parent.recv()
            if msg.get("kind") == "error":
                raise RuntimeError(msg["traceback"])
            out.append(msg)
            if msg.get("status") == "total_arrest":
                break
    finally:
        if proc.is_alive():
            parent.send("STOP")
        proc.join(timeout=10)
        if proc.is_alive():
            proc.terminate(); proc.join()
        parent.close()
    return out
