#!/usr/bin/env python3
"""
build_data.py -- compute the EXACT data for the mechanism walkthrough, straight from the
verified BUD/CONTACT implementation, and emit it as walkthrough_data.json for the interactive
page. No hand-typed numbers: every state, event, probability, sink and distribution here is
produced by the same code that backs the studies, and cross-checked against
pair_robustness.coast_limit. If anything disagrees, this script fails loudly (asserts +
nonzero exit) rather than shipping a wrong picture.

Two examples (both depth-3, both 4 active + 3 quiet, so both coast on 4-active-vertex
projections; chosen so the ONLY qualitative difference is the number of reachable sinks):
  * WASHOUT  = classes (22,25):  L = 0,  1 reachable sink   (expressed, then drains away)
  * DURABLE  = classes (0,1):    L = 7/50, 2 reachable sinks (expressed, splits the sinks)

Register: speculative exploration; exact rationals; a visual aid, not a new result. Isolated
under exploratory/accretion_pilot/mechanism_walkthrough/; earlier work untouched. Erasure
horizon H = 2 throughout (stated once, used everywhere).
"""
from __future__ import annotations
import os, sys, json, itertools
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "endogenous_present_width"))
sys.path.insert(0, os.path.join(HERE, "..", "endogenous_pair_robustness"))
import present_width as PW
import pair_robustness as PR
import depth3_criterion as D3

H = 2                      # erasure horizon, stated once
FAILS = []


def check(cond, msg):
    print(("[PASS] " if cond else "[FAIL] ") + msg)
    if not cond:
        FAILS.append(msg)


# ---------- human-readable labels for 4-active-vertex projection shapes ----------
SHAPE = {
    (0, (0, 0, 0, 0)): "four loose vertices",
    (1, (0, 0, 1, 1)): "one bond + two loose",
    (2, (0, 1, 1, 2)): "a chain of three + one loose",
    (2, (1, 1, 1, 1)): "two separate bonds",
    (3, (1, 1, 2, 2)): "a chain of four",
    (3, (1, 1, 1, 3)): "a star (one hub, three spokes)",
    (3, (0, 2, 2, 2)): "a triangle + one loose",
    (4, (1, 1, 2, 2)): "a chain of four + one chord (a 'kite' base)",
    (4, (2, 2, 2, 2)): "a four-cycle",
    (5, (2, 2, 2, 2)): "four-cycle + one chord",
    (6, (3, 3, 3, 3)): "the complete graph on four",
}


def shape_label(P):
    e = P.number_of_edges()
    deg = tuple(sorted(d for _, d in P.degree()))
    return SHAPE.get((e, deg), f"{e} bonds, degrees {list(deg)}")


def graph_json(G, active_only=False):
    nodes = [{"id": str(n), "label": G.nodes[n]["label"]} for n in G.nodes()]
    edges = [[str(u), str(v)] for u, v in G.edges()]
    return {"nodes": nodes, "edges": edges}


def proj_repr_json(P):
    """A 4-vertex active graph, with fixed square-corner coordinates for stable drawing."""
    ns = list(P.nodes())
    pos = [(0.25, 0.25), (0.75, 0.25), (0.75, 0.75), (0.25, 0.75)]
    idx = {n: i for i, n in enumerate(ns)}
    nodes = [{"id": str(n), "x": pos[idx[n]][0], "y": pos[idx[n]][1]} for n in ns]
    edges = [[str(u), str(v)] for u, v in P.edges()]
    return {"nodes": nodes, "edges": edges, "shape": shape_label(P), "n_edges": P.number_of_edges()}


def event_desc(G, ev):
    """Plain-language + technical description of a legal event and why it is allowed."""
    if ev[0] == "B":
        _, x, y = ev
        return {"kind": "BUD", "participants": [str(x), str(y)],
                "why": f"vertices {x} and {y} are both ACTIVE and joined by a bond, so a bud is "
                       f"legal here",
                "effect": f"{y} becomes QUIET; a fresh ACTIVE vertex appears, bonded to {x} "
                          f"and {y}"}
    if ev[0] == "C":
        _, pair, q = ev
        a, b = sorted(tuple(pair))
        return {"kind": "CONTACT", "participants": [str(a), str(b), str(q)],
                "why": f"quiet vertex {q} has two ACTIVE neighbours {a},{b} that are NOT yet "
                       f"bonded — so it can introduce them",
                "effect": f"a new bond {a}-{b} appears in the active layer (the archive vertex "
                          f"{q} is unchanged)"}
    raise ValueError(ev)


# ---------- exact BUD-only projection coast (kernel + reachable set) ----------
def build_coast(Gi, Gj):
    reps, buckets = [], {}

    def cidx(P):
        h = PW.wl(P)
        for k in buckets.get(h, ()):
            if PW.iso(P, reps[k]):
                return k
        reps.append(P); buckets.setdefault(h, []).append(len(reps) - 1)
        return len(reps) - 1

    def slice_dist(G):
        d = {}

        def rec(Gg, prob, s):
            key = cidx(PW.erase(Gg))
            if s == H:
                d[key] = d.get(key, Fr(0)) + prob; return
            evs = PW.events_ext(Gg); n = len(evs)
            if n == 0:
                d[key] = d.get(key, Fr(0)) + prob; return
            for e in evs:
                rec(PW.apply_ev(Gg, e), prob * Fr(1, n), s + 1)
        rec(G, Fr(1), 0)
        return d

    mu_i, mu_j = slice_dist(Gi), slice_dist(Gj)
    # kernel over reachable projection classes, recording underlying BUD events per transition
    T, evmap = {}, {}
    frontier = list(set(mu_i) | set(mu_j)); seen = set(frontier)
    while frontier:
        s = frontier.pop(); P = reps[s]; evs = PW.events_bud(P)
        row = {}; emap = {}
        if not evs:
            row = {s: Fr(1)}
        else:
            n = len(evs)
            for (_, x, y) in evs:
                s2 = cidx(PW.erase(PW.bud(P, x, y)))
                row[s2] = row.get(s2, Fr(0)) + Fr(1, n)
                emap.setdefault(s2, []).append(f"bud {x}→{y}")
        T[s] = row; evmap[s] = emap
        for s2 in row:
            if s2 not in seen:
                seen.add(s2); frontier.append(s2)
    for s in list(seen):                       # ensure every node has a row
        if s not in T:
            P = reps[s]; evs = PW.events_bud(P)
            if not evs:
                T[s] = {s: Fr(1)}; evmap[s] = {}
            else:
                n = len(evs); row = {}; emap = {}
                for (_, x, y) in evs:
                    s2 = cidx(PW.erase(PW.bud(P, x, y)))
                    row[s2] = row.get(s2, Fr(0)) + Fr(1, n)
                    emap.setdefault(s2, []).append(f"bud {x}→{y}")
                T[s] = row; evmap[s] = emap
    sinks = sorted(s for s in T if T[s] == {s: Fr(1)})
    return reps, mu_i, mu_j, T, evmap, sinks


def absorption(T, sinks, mu):
    trans = sorted(s for s in T if s not in sinks)
    idx = {s: k for k, s in enumerate(trans)}
    if trans:
        A = [[(Fr(1) if a == b else Fr(0)) - T[trans[a]].get(trans[b], Fr(0))
              for b in range(len(trans))] for a in range(len(trans))]
        R = [[T[trans[a]].get(c, Fr(0)) for c in sinks] for a in range(len(trans))]
        X = PR.solve(A, R)
    else:
        X = []
    a = {c: Fr(0) for c in sinks}
    for s, p in mu.items():
        if s in sinks:
            a[s] += p
        else:
            for ci, c in enumerate(sinks):
                a[c] += p * X[idx[s]][ci]
    return a


def apply_T(vec, T):
    out = {}
    for s, p in vec.items():
        for s2, q in T[s].items():
            out[s2] = out.get(s2, Fr(0)) + p * q
    return out


def tv(d1, d2):
    ks = set(d1) | set(d2)
    return sum(abs(d1.get(k, Fr(0)) - d2.get(k, Fr(0))) for k in ks) * Fr(1, 2)


def dist_json(d):
    return {str(k): str(v) for k, v in d.items()}


def dist_floats(d, keys):
    return {str(k): float(d.get(k, Fr(0))) for k in keys}


# ---------- event stepper: reachable full-state tree to horizon H ----------
def build_step_tree(G0):
    nodes = {}
    counter = [0]

    def add(G, depth):
        nid = f"n{counter[0]}"; counter[0] += 1
        evs = PW.events_ext(G)
        entry = {"id": nid, "depth": depth, "graph": graph_json(G),
                 "menu_size": len(PW.C_q(G, None) if False else []),  # placeholder, unused
                 "events": []}
        nodes[nid] = entry
        if depth < H:
            for e in evs:
                child = add(PW.apply_ev(G, e), depth + 1)
                d = event_desc(G, e); d["to"] = child
                entry["events"].append(d)
        return nid

    root = add(G0, 0)
    return root, nodes


def build_example(name, ai, bi, d3, classification):
    Gi, Gj = d3[ai], d3[bi]
    check(PW.iso(PW.erase(Gi), PW.erase(Gj)) and not PW.iso(Gi, Gj),
          f"{name}: matched pair (iso active projection, different archive)")
    reps, mu_i, mu_j, T, evmap, sinks = build_coast(Gi, Gj)
    a_i, a_j = absorption(T, sinks, mu_i), absorption(T, sinks, mu_j)
    L = tv(a_i, a_j)
    Lref, shapes_ref, _ = PR.coast_limit(Gi, Gj)
    check(L == Lref, f"{name}: coast limit L={L} matches pair_robustness.coast_limit ({Lref})")
    check(len(sinks) == len(shapes_ref),
          f"{name}: #sinks={len(sinks)} matches ({len(shapes_ref)})")
    check(sum(mu_i.values()) == 1 and sum(mu_j.values()) == 1, f"{name}: mu distributions sum to 1")
    check((classification == "washout") == (L == 0 and tv(mu_i, mu_j) > 0),
          f"{name}: classification '{classification}' consistent with L and expression")

    # per-step coast distributions (floats for the divide animation; endpoints exact elsewhere)
    steps = []
    vi, vj = dict(mu_i), dict(mu_j); tv_series = []
    allkeys = sorted(set().union(*[set(T)], set(mu_i), set(mu_j)))
    for t in range(13):
        steps.append({"t": t, "i": dist_floats(vi, allkeys), "j": dist_floats(vj, allkeys)})
        tv_series.append(float(tv(vi, vj)))
        vi, vj = apply_T(vi, T), apply_T(vj, T)

    proj_classes = []
    for cid in sorted(set(T) | set(mu_i) | set(mu_j)):
        proj_classes.append({"id": cid, "is_sink": cid in sinks, **proj_repr_json(reps[cid])})
    transitions = []
    for s in sorted(T):
        for s2, p in sorted(T[s].items()):
            transitions.append({"from": s, "to": s2, "prob": str(p), "prob_f": float(p),
                                "events": evmap.get(s, {}).get(s2, ["(self-loop: no bond to "
                                                                    "bud)"] if s == s2 else [])})
    step_root_i, step_nodes_i = build_step_tree(Gi)
    step_root_j, step_nodes_j = build_step_tree(Gj)

    return {
        "name": name, "classification": classification, "classes": [ai, bi],
        "L": str(L), "L_float": float(L), "n_sinks": len(sinks),
        "lineages": {
            "i": {"class": ai, "full": graph_json(Gi), "proj": proj_repr_json(PW.erase(Gi))},
            "j": {"class": bi, "full": graph_json(Gj), "proj": proj_repr_json(PW.erase(Gj))},
        },
        "proj_classes": proj_classes,
        "transitions": transitions,
        "sinks": sinks,
        "mu_exact": {"i": dist_json(mu_i), "j": dist_json(mu_j)},
        "absorption_exact": {"i": dist_json(a_i), "j": dist_json(a_j)},
        "dist_steps": steps,
        "tv_series": tv_series,
        "step_tree": {"i": {"root": step_root_i, "nodes": step_nodes_i},
                      "j": {"root": step_root_j, "nodes": step_nodes_j}},
    }


def main():
    d3 = D3.depth3_classes()
    data = {
        "meta": {
            "commit_context": "a43ff0c",
            "horizon_H": H,
            "what_it_shows": "How local BUD/CONTACT events move the ACTIVE shape, and why a "
                             "historical difference between two archives can persist (durable) "
                             "or vanish (washout) after the archive is deleted.",
            "caveats": [
                "Everything here is EXACT (rational) and computed from the verified "
                "implementation; floats are shown only for drawing.",
                "'Two possible destinations' does NOT mean the system anticipates or chooses "
                "its future; outcomes follow the fixed local rules and event probabilities.",
                "Single-run stepping is an illustration; the distribution view is the exact "
                "ensemble claim. Keep them distinct.",
                "The fork rule (durable iff the coast can fork) is verified on the enumerated "
                "depth-2 and depth-3 sets, not proven in general.",
                "This is a toy model. No perpendicular-space coupling, no physical-world "
                "mechanism is claimed.",
            ],
        },
        "washout": build_example("washout", 22, 25, d3, "washout"),
        "durable": build_example("durable", 0, 1, d3, "durable"),
    }
    out = os.path.join(HERE, "walkthrough_data.json")
    with open(out, "w") as f:
        json.dump(data, f, separators=(",", ":"))
    size = os.path.getsize(out)
    print(f"\nwrote {out} ({size/1024:.1f} KB)")
    print(f"washout: L={data['washout']['L']} sinks={data['washout']['n_sinks']} "
          f"proj_classes={len(data['washout']['proj_classes'])}")
    print(f"durable: L={data['durable']['L']} sinks={data['durable']['n_sinks']} "
          f"proj_classes={len(data['durable']['proj_classes'])}")
    if FAILS:
        print(f"\nFAILED: {len(FAILS)} check(s)"); sys.exit(1)
    print("\nALL DATA CHECKS PASSED.")


if __name__ == "__main__":
    main()
