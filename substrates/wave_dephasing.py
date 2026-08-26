#!/usr/bin/env python3
"""
EXPLORATORY — the coherence ladder (first rung of the "why can coherent dynamics read
the address?" question). NOT a sealed test.

Mechanism hypothesis (directional, per GPT — no functional form assumed): if coherent
interference is what exposes the multiscale address, then destroying coherence should
reduce the address-predictiveness of transport.

Cheap first probe: three rungs of a per-vertex RETURN observable, decreasing coherence,
all in the sealed primary window |E| in [0.8,2.5], from the eigenstates alone (no noisy
simulation yet):

  1. coherent-return  P_coh(v)  = < |sum_{k in win} |phi_k(v)|^2 e^{-i E_k t}|^2 >_t
        -- full dynamical interference between window eigenstates (most coherent).
  2. diagonal-ensemble P_diag(v) = sum_{k in win} |phi_k(v)|^4
        -- infinite-time average: dynamical phases dephased, eigenstate structure kept.
  3. classical-return  (the sealed incoherent null, random-walk return e^{tL})
        -- no quantum structure at all (least coherent).

For each rung we measure the same M4-over-M3 address increment (held-out-offset CV) and
the stratified-shuffle control. If the increment falls monotonically 1 -> 2 -> 3, that is
the mechanism trend, and the smooth stochastic-dephasing sweep becomes worth its compute.
"""

import sys
import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from transport_run import (build_features, assemble, held_out_r2, OFFSETS,
                           WIN_PRIMARY, NAME)


def observables(f, times=(0.3, 0.6, 1.2)):
    ev, w2, n = f["evals"], f["w2"], f["n"]
    win = (np.abs(ev) >= WIN_PRIMARY[0]) & (np.abs(ev) <= WIN_PRIMARY[1])
    W = w2[:, win]; Ew = ev[win]
    Pcoh = np.zeros(n)
    for t in times:
        amp = (W * np.exp(-1j * Ew * t)[None, :]).sum(1)
        Pcoh += np.abs(amp) ** 2
    Pcoh /= len(times)
    Pdiag = (W ** 2).sum(1)
    return Pcoh, Pdiag


def ladder(N, extent=12, offs=None):
    offs = offs or OFFSETS[:4]
    feats = [build_features(N, o, extent=extent, return_dynamics=True) for o in offs]
    bulk = [f["bulk"] for f in feats]
    rng = np.random.default_rng(0)
    codebook = {}
    for f in feats:
        for k in f["motif_keys"]:
            codebook.setdefault(k, len(codebook))
    B = [assemble(f, codebook, rng) for f in feats]

    Pcoh, Pdiag, classical = [], [], []
    for f in feats:
        pc, pd = observables(f)
        Pcoh.append(pc); Pdiag.append(pd); classical.append(f["ret"][10])

    rungs = [("1 coherent-return (interference)", Pcoh),
             ("2 diagonal-ensemble (dephased)", Pdiag),
             ("3 classical-return (incoherent)", classical)]
    nb = sum(int(b.sum()) for b in bulk)
    print(f"\n{'='*70}\n{NAME[N]} (N={N})  extent={extent}  {len(offs)} offsets  "
          f"{nb} bulk vertices\n{'='*70}")
    print(f"  {'rung (coherence high -> low)':38s} {'M3':>7} {'M4':>7} "
          f"{'M4-M3':>8} {'shuffle':>8}")
    incs = []
    for name, y in rungs:
        m3 = held_out_r2(B, y, bulk, "M3")[0]
        m4 = held_out_r2(B, y, bulk, "M4")[0]
        m4s = held_out_r2(B, y, bulk, "M4shuf")[0]
        incs.append(m4 - m3)
        print(f"  {name:38s} {m3:7.4f} {m4:7.4f} {m4-m3:+8.4f} {m4s-m3:+8.4f}")
    trend = "DECREASING (mechanism trend)" if incs[0] > incs[1] > incs[2] else \
            "not monotone -- look closer"
    print(f"  --> address increment across the ladder: "
          f"{[round(i,4) for i in incs]}  → {trend}")
    return incs


if __name__ == "__main__":
    fams = tuple(int(x) for x in sys.argv[1:]) if len(sys.argv) > 1 else (10,)
    for N in fams:
        ladder(N)
