"""
Decision gates G0-G8 and outcome routing (DECISION_GATE_CONCORDANCE.md; MSD v8.1 §12;
physical v7 §7; conditional-null v4.1 §7).

The primary coherent transport claim is SEPARATE from the cross-engine non-reproduction modifier:
  primary coherent  <=>  G0 & coherent-G1 & G2 & G3 & G4 & G6      (G5 NOT required)
  modifier          <=>  classical-G1 & G5
A G5 failure does NOT erase the coherent transport result. Any undefined-denominator route ->
mixed/undetectable. G7 is descriptive only (no threshold, no delta_cap comparison).
"""
from . import constants as C

UNDEFINED = "undefined"


def G0(t_bound_star):
    """Boundary gate: admissible iff t_bound* > 8 (strict). Else finite-size-limited."""
    return {"pass": t_bound_star > C.T_BOUND_STRICT,
            "state": "admissible" if t_bound_star > C.T_BOUND_STRICT else "finite-size-limited"}


def G1(median_r2):
    """Quality: pass iff median R^2_fit >= 0.90. A fail is descriptive; NEVER changes M9 membership."""
    return {"pass": median_r2 >= C.G1_R2_MIN}


def G2(qref):
    """Permutation stress: pass iff q_ref < 0.05 on M_perm,7 (extremeness, not significance)."""
    return {"pass": qref < C.G2_QREF_MAX}


def G3(m9_address, dcap):
    """Capacity: pass iff M9,address > delta_cap."""
    return {"pass": m9_address > dcap}


def G4(r_kill):
    """Shuffle-kill: r_kill is None (any undefined required reduction) -> mixed; else pass iff >=0.70."""
    if r_kill is None:
        return {"pass": False, "route": "mixed/undetectable"}
    return {"pass": r_kill >= C.G4_RKILL_MIN}


def G5(classical_m9_address, coherent_m9_address, dcap):
    """Cross-engine non-reproduction (NOT 'coherence-specific'). Denominator undefined if coherent
    <= delta_cap or <= 0 -> mixed. Else pass iff classical <= 0.2 * coherent."""
    if coherent_m9_address <= dcap or coherent_m9_address <= 0:
        return {"pass": False, "route": "mixed/undetectable", "denominator": UNDEFINED}
    return {"pass": classical_m9_address <= C.G5_CLASSICAL_FRAC * coherent_m9_address}


def G6(m9_resid, dcap):
    """Residual-orthogonal null 'survives': deterministic M9 of dR2_resid > delta_cap (lower bound)."""
    return {"pass": m9_resid > dcap}


def G7(m9_address, m9_parity):
    """Address vs parity: DESCRIPTIVE ONLY. No threshold, no comparison to delta_cap, no pass/fail."""
    dap = m9_address - m9_parity
    return {"descriptive": True, "M9_address": m9_address, "M9_parity": m9_parity, "Delta_ap": dap,
            "note": "qualitative only; small Delta_ap ~ 'compatible with representation collapse', "
                    "never proof of equality"}


def G8(qtilde_7):
    """Config-specific secondary: Westfall-Young q-tilde over the 7 feasible cells. Secondary only."""
    return {"secondary": True, "qtilde": qtilde_7}


def primary_coherent_transport(g0, g1_coherent, g2, g3, g4, g6):
    """G0 & coherent-G1 & G2 & G3 & G4 & G6 (G5 excluded)."""
    return all(g["pass"] for g in (g0, g1_coherent, g2, g3, g4, g6))


def cross_engine_modifier(g1_classical, g5):
    """classical-G1 & G5. Withheld on failure; does NOT erase the primary coherent result."""
    return g1_classical["pass"] and g5["pass"]


def route_physical_outcome(m9_addr2, m9_addr16, dcap, sign6_r2, m9_resid16, qref7,
                           feasible, m9_parity16=None):
    """Exhaustive routing by named frozen gates (physical v7 §7; conditional-null v4.1 §7):
    feasibility -> compression / survives-controls where exact criteria pass -> else mixed.
    Parity reported descriptively alongside (never a routing branch)."""
    from .aggregation import sign_support
    if not feasible:
        return "infeasible"
    # compression: exact criteria
    rho_defined = (m9_addr2 > 0) and (m9_addr2 > dcap) and sign_support(sign6_r2)
    if rho_defined:
        rho = m9_addr16 / m9_addr2
        if (m9_addr16 < dcap) and (rho < C.RHO_STAR):
            return "compression"
    # survives-the-frozen-stress-controls: exact criteria (G3 & G6 & G2)
    if (m9_addr16 > dcap) and (m9_resid16 > dcap) and (qref7 < C.G2_QREF_MAX):
        return "survives-stress-controls"
    return "mixed/undetectable"
