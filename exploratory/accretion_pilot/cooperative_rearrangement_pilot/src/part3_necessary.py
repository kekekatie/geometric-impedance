#!/usr/bin/env python3
"""
part3_necessary.py -- Part 3: necessary condition before searching.

For a connected region R, the exterior (band \\ R) is held fixed. Changing only R
can restore projection-window compatibility ONLY IF the constraints supplied by
the unchanged exterior are themselves feasible. We:

  (A) enumerate connected regions R (size <= 8, witness/dead-site seeded, capped),
      compute the exterior compatibility region under a consistent gauge and
      CAREFUL provenance (a vertex's constraint is dropped only if its ENTIRE
      incident-tile star is in R), and classify it box-independently
      (box-50 certifier AND box-free Phase-I LP). Reject R if the exterior is
      infeasible; permit it if feasible; otherwise unresolved.

  (B) compute, faithfully, the MINIMUM set of vertex-stars whose engulfment makes
      the band feasible (the real "how much must change, and how spread out is
      it"). A vertex is a removal candidate only if it is a top contributor on
      some facet. This bounds what ANY connected fixed-exterior region -- even
      beyond size 8 -- would have to engulf, and whether that footprint is
      connected and how large/wide it is.

Controls: R=empty (exterior = full band) must be infeasible; a synthetic feasible
constraint system must classify feasible.

Reads input/retained_state.json only (search-visible). Writes
results/part3_necessary.json.
"""
from __future__ import annotations
import json, itertools, collections
import coop_common as CC
from coop_common import Sl, L, M, S
import feas

MAX_REGION_SIZE = 8
REGION_CAP = 50000


def load_band():
    st = json.loads((CC.INPUT / "retained_state.json").read_text())
    band = [CC.dtile(t) for t in st["tiles"]]
    rank = {int(k): int(v) for k, v in st["rank"].items()}
    dead_vkeys = set()
    for ds in st["dead_sites"]:
        dead_vkeys.add(L.key(complex(*ds["p"]))); dead_vkeys.add(L.key(complex(*ds["q"])))
    witness_vkeys = {L.key(complex(*w["vertex"])) for w in st["compatibility_witness_vertices"]}
    return st, band, rank, dead_vkeys, witness_vkeys


def seeds_from(band, vkeys):
    """tiles incident to any vertex in vkeys."""
    out = set()
    for t in band:
        if any(L.key(z) in vkeys for z in t[1:]):
            out.add(CC.dk(t))
    return out


def region_footprint_stats(BC, vertex_set):
    """For a set of vertices to engulf: the union of their incident tiles (the
    minimum region that engulfs them), its size, connectivity, and the pairwise
    span of the vertices (in S)."""
    tiles = set()
    for v in vertex_set:
        tiles |= BC.vincident.get(v, set())
    # connectivity of that tile set
    tilemap = {CC.dk(t): t for t in BC.band}
    sub = [tilemap[d] for d in tiles if d in tilemap]
    comps = CC.connected_components(sub) if sub else []
    vs = [complex(*v) for v in vertex_set]
    span = max((abs(a - b) / S for a in vs for b in vs), default=0.0)
    return dict(n_tiles=len(tiles), n_components=len(comps), connected=(len(comps) <= 1),
                vertex_span_S=round(span, 2))


def _violations(BC, cmax, t):
    """Per-constraint violation c_i/|n| - (n/|n|).t at point t (unit-normalised),
    using the raw WIN normals for each key in cmax."""
    from coop_common import WIN
    out = []
    for key, c in cmax.items():
        rk, i = key
        n, h = WIN[rk]
        nx, ny = float(n[i][0]), float(n[i][1]); nn = (nx * nx + ny * ny) ** 0.5
        viol = c / nn - (nx * t[0] + ny * t[1]) / nn
        out.append((viol, key))
    out.sort(reverse=True)
    return out


def min_facet_drop(BC, max_drop=4):
    """Constraint-level LOWER bound: minimum number of facet-constraints to delete
    for feasibility (brute force over the <=20 keys). Dropping a whole facet is at
    least as easy as achieving it by engulfment, so this lower-bounds the real
    change needed."""
    keys = list(BC.full_cmax.keys())
    for s in range(1, max_drop + 1):
        for drop in itertools.combinations(keys, s):
            cm = {k: v for k, v in BC.full_cmax.items() if k not in drop}
            if CC.classify_exterior(cm)["verdict"] == "feasible":
                return dict(size=s, dropped=[list(k) for k in drop])
    return dict(size=None, searched_up_to=max_drop)


def greedy_engulfment(BC, max_remove=80):
    """Faithful greedy UPPER bound: engulf the argmax vertex of the most-violated
    constraint until the band is feasible (it must converge -- in the limit the
    exterior empties). Reports how many vertex-stars had to be engulfed and the
    spatial footprint, which bounds what any connected fixed-exterior region would
    need."""
    E = set(); steps = []
    for _ in range(max_remove + 1):
        cmax, _ = BC.exterior_cmax_from_vertices(E)
        cl = CC.classify_exterior(cmax)
        if cl["verdict"] == "feasible":
            return dict(converged=True, n_vertices=len(E),
                        vertices=[list(v) for v in sorted(E)],
                        footprint=region_footprint_stats(BC, set(E)),
                        n_greedy_steps=len(steps))
        tstar = feas.classify(cmax)["witness"] or [0.0, 0.0]
        viols = _violations(BC, cmax, tstar)
        added = None
        for viol, key in viols:
            for c, v in BC.by_key[key]:
                if v not in E:
                    added = v; break
            if added is not None:
                break
        if added is None:
            break
        E.add(added); steps.append(list(added))
    return dict(converged=False, searched_up_to=max_remove, n_vertices=len(E),
               footprint=region_footprint_stats(BC, set(E)))


def main():
    st, band, rank, dead_vkeys, witness_vkeys = load_band()
    BC = CC.BandConstraints(band, rank=rank)

    # provide exterior_cmax directly from a vertex set (for part B)
    def exterior_cmax_from_vertices(E):
        cmax = {}
        for key, lst in BC.by_key.items():
            for c, v in lst:
                if v not in E:
                    cmax[key] = c; break
        return cmax, E
    BC.exterior_cmax_from_vertices = exterior_cmax_from_vertices

    # ---- controls ----
    ctrl_empty = CC.classify_exterior(BC.full_cmax)       # R=empty -> full band
    synth = {(0, 0): -1.0, (0, 1): -1.0}                  # trivially feasible pair
    ctrl_feas = CC.classify_exterior(synth)

    # ---- (A) connected-region enumeration ----
    seeds = seeds_from(band, dead_vkeys | witness_vkeys)
    regions = CC.connected_regions(band, seeds, MAX_REGION_SIZE, REGION_CAP)
    by_size = collections.Counter(len(r) for r in regions)
    truncated = len(regions) >= REGION_CAP
    counts = collections.Counter()
    engulfing = 0
    permitted = []
    unresolved = []
    for R in regions:
        cmax, E = BC.exterior_cmax(R)
        if not E:
            counts["infeasible(no engulfment)"] += 1
            continue
        engulfing += 1
        # if engulfment left the binding constraints unchanged, feasibility is
        # unchanged (still infeasible) -- skip the LP.
        if cmax == BC.full_cmax:
            counts["infeasible(no binding change)"] += 1
            continue
        cl = CC.classify_exterior(cmax)
        counts[cl["verdict"]] += 1
        if cl["verdict"] == "feasible":
            permitted.append(dict(region=sorted(R), engulfed=len(E), exterior=cl))
        elif cl["verdict"] == "unresolved":
            unresolved.append(dict(region=sorted(R), engulfed=len(E), exterior=cl))

    # ---- (B) obstruction characterization ----
    facet_drop = min_facet_drop(BC)        # constraint-level lower bound
    greedy = greedy_engulfment(BC)         # faithful vertex-engulfment upper bound

    # witness-vertex span (characterisation)
    wvs = [complex(*v) for v in witness_vkeys]
    wspan = max((abs(a - b) / S for a in wvs for b in wvs), default=0.0)
    star_sizes = {str(list(v)): len(BC.vincident.get(v, set())) for v in witness_vkeys}

    report = dict(
        case="w7-B-s0 jam@23", move_class="connected fixed-exterior region, size<=8",
        controls=dict(
            R_empty_full_band=dict(verdict=ctrl_empty["verdict"], box_r=ctrl_empty["box_r"]),
            synthetic_feasible=dict(verdict=ctrl_feas["verdict"]),
        ),
        region_enumeration=dict(
            max_region_size=MAX_REGION_SIZE, cap=REGION_CAP, truncated=truncated,
            n_regions=len(regions), by_size=dict(sorted(by_size.items())),
            n_engulfing_a_vertex=engulfing,
            verdict_counts=dict(counts),
            n_permitted=len(permitted), permitted=permitted[:20],
            n_unresolved=len(unresolved), unresolved=unresolved[:20],
        ),
        obstruction=dict(
            min_facet_drop=facet_drop,
            greedy_vertex_engulfment=greedy,
        ),
        characterisation=dict(
            witness_vertex_span_S=round(wspan, 2),
            witness_star_sizes=star_sizes,
            note=("A connected region must engulf a vertex's ENTIRE tile star to drop its constraint. "
                  "The minimum feasible-making engulfment (part B) and its footprint size/connectivity/span "
                  "bound what any connected fixed-exterior region would need."),
        ),
    )
    CC.RESULTS.mkdir(parents=True, exist_ok=True)
    (CC.RESULTS / "part3_necessary.json").write_text(json.dumps(report, indent=2, default=float))

    print(f"controls: R=empty -> {ctrl_empty['verdict']} (box_r={ctrl_empty['box_r']:.4e}); "
          f"synthetic -> {ctrl_feas['verdict']}")
    print(f"regions enumerated: {len(regions)} (truncated={truncated}); by size {dict(sorted(by_size.items()))}")
    print(f"  engulfing >=1 vertex: {engulfing}; verdicts: {dict(counts)}")
    print(f"  PERMITTED (feasible exterior): {len(permitted)}; unresolved: {len(unresolved)}")
    print(f"min facet-drop (constraint-level lower bound): {facet_drop.get('size')} facets {facet_drop.get('dropped')}")
    gf = greedy["footprint"]
    print(f"greedy vertex-engulfment (faithful upper bound): converged={greedy['converged']} "
          f"n_vertices={greedy['n_vertices']} -> footprint {gf['n_tiles']} tiles, "
          f"connected={gf['connected']}, span {gf['vertex_span_S']} S")
    print(f"witness-vertex span {round(wspan,2)} S; star sizes {star_sizes}")
    print("wrote results/part3_necessary.json")


if __name__ == "__main__":
    main()
