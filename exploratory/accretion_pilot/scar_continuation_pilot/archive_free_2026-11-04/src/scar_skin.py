#!/usr/bin/env python3
"""
scar_skin.py -- the archive-free scar worker and the lockstep comparator.

The worker is the FROZEN `active_skin_engine.ActiveSkin` (radius-2 hollow band with
an explicit true-frontier boundary that pruning never pollutes). The scheduler is
the AUDITED full-patch `scar_continuation.patient_scar`, reused verbatim: it drives
`P` only through `P.frontier()` / `D.candidates` / `P.legal` / `P.add`, all of
which ActiveSkin overrides or inherits, so the identical scheduler runs on the band.

The evaluator runs the same scheduler on the FULL patch (the audited baseline) and
compares every step: candidate inventories, outcomes, placements, frontier
identities, scars, and PRNG state. First divergence and cause are recorded.
"""
from __future__ import annotations
import random
import af_common as AF
from af_common import E, L, D, S, PC, dk

# the audited full-patch scar scheduler, reused verbatim for BOTH substrates
import sys
from pathlib import Path
_PILOT = str(Path(__file__).resolve().parents[3] / "scar_continuation_pilot" / "src")
if _PILOT not in sys.path:
    sys.path.insert(0, _PILOT)
import scar_continuation as SCN     # noqa: E402  patient_scar (audited)


def inventory(P):
    """Frozen E.inventory: per true-frontier edge, its id and sorted candidate
    decorated-key ids. This is the candidate-set evidence compared across substrates."""
    return E.inventory(P)


def run_lockstep(world, si, steps=44):
    """Replay from the fork seed with the audited scar scheduler on BOTH the full
    patch (evaluator) and the radius-2 ActiveSkin (archive-free worker), in lockstep
    from the same stream. Record per-step comparison and the first divergence."""
    forks = AF.RD.load_forks()
    Sstar = forks[world]["Sstar"]; cs = forks[world]["cs"]; B = cs[1]
    stream = PC.streams_for(world)[si]

    full = L.Patch(list(Sstar)); full.add(B)
    skin = E.ActiveSkin(list(Sstar) + [B], radius=2)
    rng_e = random.Random(stream); rng_w = random.Random(stream)
    scars_e = set(); scars_w = set()

    rows = []
    first_div = None
    jam_step = None
    illegal_worker = 0
    for s in range(1, steps + 1):
        inv_e = inventory(full)
        inv_w = inventory(skin)
        n0e = len(full.tris)
        st_e, n_e, k_e, new_e, il_e = SCN.patient_scar(full, rng_e, scars_e, verify_legal=True)
        placed_e = [dk(t) for t in full.tris[n0e:]]
        skin.additions = []
        st_w, n_w, k_w, new_w, il_w = SCN.patient_scar(skin, rng_w, scars_w, verify_legal=True)
        placed_w = [dk(t) for t in skin.additions]
        illegal_worker += il_w
        dropped = skin.prune()

        fr_e = [AF.frontier_id(e) for e in full.frontier()]
        fr_w = [AF.frontier_id(e) for e in skin.frontier()]
        if (new_e or new_w) and jam_step is None:
            jam_step = s

        # distinct mismatch classes (checked in a fixed order)
        causes = []
        if inv_w != inv_e:
            # separate frontier-set/order difference from candidate-set difference
            fe = [x[0] for x in inv_e]; fw = [x[0] for x in inv_w]
            if fw != fe:
                causes.append("frontier_identity_or_order")
            else:
                causes.append("candidate_set")
        if (st_w, n_w, k_w) != (st_e, n_e, k_e):
            causes.append("forced_free_or_outcome")
        if sorted(placed_w) != sorted(placed_e):
            causes.append("placement")
        if rng_w.getstate() != rng_e.getstate():
            causes.append("prng_state")
        if fr_w != fr_e:
            if "frontier_identity_or_order" not in causes:
                causes.append("frontier_after_step")
        if sorted(scars_w) != sorted(scars_e):
            causes.append("scar_set")

        if causes and first_div is None:
            first_div = dict(step=s, causes=causes,
                             eval_outcome=[st_e, n_e, k_e], worker_outcome=[st_w, n_w, k_w],
                             n_eval_frontier=len(fr_e), n_worker_frontier=len(fr_w),
                             n_eval_candidates_edges=len(inv_e), n_worker_candidates_edges=len(inv_w))

        rows.append(dict(step=s, agree=(not causes),
                         status=st_e, mode=k_e, placed=n_e,
                         worker_status=st_w, worker_placed=n_w,
                         frontier=len(fr_e), worker_frontier=len(fr_w),
                         full_tiles=len(full.tris), worker_retained=len(skin.tris),
                         dropped=dropped, scars=len(scars_e), worker_scars=len(scars_w),
                         newly_pinned=len(new_e)))
        if st_e == "total_arrest" or st_w == "total_arrest":
            break

    final_step = rows[-1]["step"] if rows else 0
    reached_44 = (final_step == steps and rows[-1]["status"] != "total_arrest"
                  and rows[-1]["worker_status"] != "total_arrest")
    all_agree = all(r["agree"] for r in rows)
    return dict(world=world, si=si, stream=stream, jam_step=jam_step,
                final_step=final_step, reached_44=reached_44,
                exact_equivalence=all_agree and first_div is None,
                first_divergence=first_div, illegal_worker=illegal_worker,
                full=list(full.tris), worker_band=list(skin.tris),
                worker_boundary={k: v for k, v in skin.boundary.items()},
                worker_scars=sorted([sorted(list(ek)) for ek in scars_w]),
                rows=rows)


# ------------------- worker-only helpers (archive-free; no evaluator) -------------------
def new_worker(world, si):
    forks = AF.RD.load_forks()
    Sstar = forks[world]["Sstar"]; B = forks[world]["cs"][1]
    stream = PC.streams_for(world)[si]
    skin = E.ActiveSkin(list(Sstar) + [B], radius=2)
    rng = random.Random(stream); scars = set()
    return skin, rng, scars


def worker_step(skin, rng, scars):
    """One archive-free step on the band: inventory, scar-tolerant patient, prune."""
    before = E.inventory(skin)
    skin.additions = []
    st, n, kind, newly, illegal = SCN.patient_scar(skin, rng, scars, verify_legal=True)
    placed = [dk(t) for t in skin.additions]; skin.additions = []
    dropped = skin.prune()
    return dict(status=st, n=n, mode=kind, placed=placed, before=before,
                dropped=dropped, newly=len(newly), illegal=illegal,
                frontier=[AF.frontier_id(e) for e in skin.frontier()], retained=len(skin.tris))


def worker_trace(world, si, steps=44, stop_at=None, serialize_at=None):
    """Run ONLY the archive-free worker (no full patch anywhere). Optionally
    serialize the retained state at `serialize_at`. Returns per-step placed keys and
    the (optional) serialized state + live objects for cold-restart comparison."""
    import isolated_worker as IW
    skin, rng, scars = new_worker(world, si)
    trace = []; snapshot = None
    end = stop_at if stop_at is not None else steps
    for s in range(1, end + 1):
        if serialize_at is not None and s == serialize_at + 1:
            snapshot = IW.serialize_state(skin, rng, scars)
        m = worker_step(skin, rng, scars)
        trace.append(dict(step=s, placed=m["placed"], status=m["status"], retained=m["retained"],
                          frontier=len(m["frontier"]), scars=len(scars)))
        if m["status"] == "total_arrest":
            break
    if serialize_at is not None and snapshot is None:
        snapshot = IW.serialize_state(skin, rng, scars)
    return dict(trace=trace, snapshot=snapshot, skin=skin, rng=rng, scars=scars)
