#!/usr/bin/env python3
"""
Defect-Holonomy v3 -- PHASE 0 pre-registration (owned by Claude Code).

Registers, BEFORE any construction, the ideal-perp holonomy quanta pi_perp(M)
of the rational-approximant period sublattices, and the predicted geometric
shrink ratios across the convergent sequence. These numbers go on record here;
E1-v3/E2-v3 later measure against them untouched.

Conventions (protocol v3): edges are classified against the approximant's own
(rationalised) star vectors, but the perp INCREMENT is the IDEAL e_perp from the
ideal projection. Therefore the registered quantum for a period vector M is the
IDEAL pi_perp(M): the approximant sends M to zero in its own (rationalised) perp,
so the residual ideal-perp displacement is the frozen phason strain a winding
loop accumulates.

AB  (Z^4, silver ratio delta = 1+sqrt2): convergents p/q of sqrt2.
Penrose (Z^5, golden ratio phi): Fibonacci convergents, via the inflation
Phi e_j = -(e_{j+2}+e_{j+3}) (mult by phi in parallel, phi'=-1/phi in perp).
"""

import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "reverse_loop_test"))
import numpy as np
from geometry import star_vectors, SUBSTRATES

OUT = Path(__file__).parent / "phase0_registration.json"
SQRT2 = np.sqrt(2.0)
PHI = (1 + np.sqrt(5.0)) / 2


def perp(m, perp_star):
    return np.asarray(m, float) @ perp_star


def par(m, par_star):
    return np.asarray(m, float) @ par_star


# --------------------------------------------------------------------------- #
# Ammann-Beenker: closed-form period sublattice
# --------------------------------------------------------------------------- #
def ab_registration():
    cfg = SUBSTRATES["ammann_beenker"]
    par_star, perp_star = star_vectors(cfg["N"], cfg["par_step"], cfg["perp_step"])
    convergents = [(1, 1), (3, 2), (7, 5), (17, 12), (41, 29)]  # p/q -> sqrt2
    rows = []
    prev = None
    for k, (p, q) in enumerate(convergents, start=1):
        # period generators (derived): pi_perp'(M)=0 with sqrt2 -> p/q
        M_a = np.array([p, q, 0, -q])
        M_b = np.array([0, q, p, q])
        qa = perp(M_a, perp_star)   # ideal quantum, = (p - q*sqrt2, 0)
        qb = perp(M_b, perp_star)   # = (0, q*sqrt2 - p)
        na, nb = float(np.linalg.norm(qa)), float(np.linalg.norm(qb))
        ratio = (na / prev) if prev else None
        rows.append(dict(order=k, convergent=f"{p}/{q}",
                         M_a=M_a.tolist(), M_b=M_b.tolist(),
                         perp_par_check=[float(np.linalg.norm(par(M_a, par_star))),
                                         float(np.linalg.norm(par(M_b, par_star)))],
                         quantum_pi_perp_M_a=np.round(qa, 12).tolist(),
                         quantum_pi_perp_M_b=np.round(qb, 12).tolist(),
                         quantum_norm_a=na, quantum_norm_b=nb,
                         shrink_ratio_vs_prev=ratio))
        prev = na
    return dict(substrate="ammann_beenker",
                asymptotic_shrink_ratio_derived=float(SQRT2 - 1),
                asymptotic_shrink_ratio_note=(
                    "sqrt2 - 1 = 1/delta_silver ~ 0.41421 per consecutive "
                    "convergent (NOT delta^-2 = 3-2sqrt2 ~ 0.1716; the guessed "
                    "constant was one power too high -- derived here)."),
                orders=rows)


# --------------------------------------------------------------------------- #
# Penrose: inflation-generated period sublattice
# --------------------------------------------------------------------------- #
def penrose_inflation():
    """Phi e_j = -(e_{j+2}+e_{j+3}) mod 5 : mult by phi in parallel space."""
    N = 5
    Phi = np.zeros((N, N), int)
    for j in range(N):
        Phi[(j + 2) % N, j] -= 1
        Phi[(j + 3) % N, j] -= 1
    return Phi


def penrose_registration():
    cfg = SUBSTRATES["penrose"]
    par_star, perp_star = star_vectors(cfg["N"], cfg["par_step"], cfg["perp_step"])
    Phi = penrose_inflation()
    # base periods (order 0): search short integer vectors (mod all-ones) with
    # small ideal perp and independent parallel images.
    ones = np.ones(5, int)
    cand = []
    rng = range(-2, 3)
    import itertools
    for m in itertools.product(rng, repeat=5):
        m = np.array(m)
        if np.all(m == 0):
            continue
        pnorm = np.linalg.norm(perp(m, perp_star))
        parnorm = np.linalg.norm(par(m, par_star))
        if parnorm > 1e-6:
            cand.append((pnorm, parnorm, m))
    cand.sort(key=lambda t: t[0])
    # pick the shortest-perp vector, then the shortest independent (in parallel)
    M0a = cand[0][2]
    pa = par(M0a, par_star)
    M0b = None
    for _, _, m in cand:
        pm = par(m, par_star)
        if abs(pa[0] * pm[1] - pa[1] * pm[0]) > 1e-6:   # parallel-independent
            M0b = m
            break
    rows = []
    prev = None
    fib = [(1, 1), (2, 1), (3, 2), (5, 3), (8, 5)]      # convergent labels
    Ma, Mb = M0a.copy(), M0b.copy()
    for k, (fnum, fden) in enumerate(fib, start=1):
        qa, qb = perp(Ma, perp_star), perp(Mb, perp_star)
        na, nb = float(np.linalg.norm(qa)), float(np.linalg.norm(qb))
        ratio = (na / prev) if prev else None
        rows.append(dict(order=k, convergent=f"{fnum}/{fden}",
                         M_a=Ma.tolist(), M_b=Mb.tolist(),
                         parallel_period_norms=[float(np.linalg.norm(par(Ma, par_star))),
                                                float(np.linalg.norm(par(Mb, par_star)))],
                         quantum_pi_perp_M_a=np.round(qa, 12).tolist(),
                         quantum_pi_perp_M_b=np.round(qb, 12).tolist(),
                         quantum_norm_a=na, quantum_norm_b=nb,
                         shrink_ratio_vs_prev=ratio))
        prev = na
        Ma = Phi @ Ma
        Mb = Phi @ Mb
    return dict(substrate="penrose",
                inflation_matrix=Phi.tolist(),
                asymptotic_shrink_ratio_derived=float(1 / PHI),
                asymptotic_shrink_ratio_note=(
                    "1/phi = phi - 1 ~ 0.61803 per inflation/consecutive "
                    "Fibonacci convergent (NOT phi^-2 ~ 0.3820; guessed constant "
                    "was one power too high -- derived here via perp eigenvalue "
                    "phi' = -1/phi of the inflation)."),
                base_periods=dict(M0_a=M0a.tolist(), M0_b=M0b.tolist()),
                orders=rows)


def main():
    reg = dict(
        note=("PHASE 0 pre-registration for defect-holonomy v3. Quanta = ideal "
              "pi_perp of approximant period vectors; measured E1/E2 must hit "
              "these before construction is tuned. Registered by Claude Code."),
        ammann_beenker=ab_registration(),
        penrose=penrose_registration())
    OUT.write_text(json.dumps(reg, indent=2, default=str))

    for sub in ["ammann_beenker", "penrose"]:
        r = reg[sub]
        print(f"\n=== {sub} ===")
        print(f"  asymptotic shrink ratio (derived): "
              f"{r['asymptotic_shrink_ratio_derived']:.5f}")
        print(f"  {r['asymptotic_shrink_ratio_note']}")
        print("  order  convergent   |pi_perp(M_a)|   ratio")
        for row in r["orders"]:
            rr = row["shrink_ratio_vs_prev"]
            print(f"    {row['order']}     {row['convergent']:>5}      "
                  f"{row['quantum_norm_a']:.6f}     "
                  f"{('%.5f' % rr) if rr else '  --'}")
    print(f"\nregistered -> {OUT.name}")


if __name__ == "__main__":
    main()
