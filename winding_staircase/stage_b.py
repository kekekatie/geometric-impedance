#!/usr/bin/env python3
"""
Stage B (winding staircase) — instrument CALIBRATION. Control, never a finding.

Build the standard sine circle map and confirm the code reproduces the two
universal numbers of the critical devil's staircase:

    x_{n+1} = x_n + Omega - (K / 2pi) sin(2pi x_n)          (lift; rho = winding)

  * D  ~ 0.8700 +- 0.01   -- fractal (box-counting) dimension of the mode-locking
                             structure at criticality K = 1 (Jensen, Bak, Bohr).
  * delta ~ 3.0 +- 0.3    -- mode-locked step width scales as  Delta(p/q) ~ q^-delta.

Per the sealed pre-registration (rule C): these are properties of ANY critical
circle map; reproducing them calibrates the instrument and is *never* a finding.
"Do not proceed [to Stage D] if it fails." A miss means our map / rotation-number
code is broken, and we fix it before anything with real content runs.
"""
import json
import numpy as np

K_CRIT = 1.0
TWO_PI = 2.0 * np.pi


def rotation_number(Omega, K, n_trans=3000, n_avg=12000, x0=0.0):
    """Winding number rho of the lift map, vectorized over an array Omega."""
    x = np.full_like(np.asarray(Omega, dtype=float), x0)
    Om = np.asarray(Omega, dtype=float)
    for _ in range(n_trans):
        x += Om - (K / TWO_PI) * np.sin(TWO_PI * x)
    x_start = x.copy()
    for _ in range(n_avg):
        x += Om - (K / TWO_PI) * np.sin(TWO_PI * x)
    return (x - x_start) / n_avg


def critical_sweep(K=K_CRIT, M=400000, n_trans=6000, n_avg=40000):
    """High-convergence rotation-number sweep across Omega in [0,1]."""
    Omega = (np.arange(M) + 0.5) / M
    rho = rotation_number(Omega, K, n_trans=n_trans, n_avg=n_avg)
    return Omega, rho


def step_width_for_rho(Omega, rho, target, eps):
    """Width of the mode-locked step at rotation number `target`, located by
    inverting the (monotone) rho(Omega) -- NOT assumed to sit at Omega=target
    (the huge rho=0 tongue shifts the small-q steps well off the diagonal)."""
    dO = Omega[1] - Omega[0]
    idx = np.where(np.abs(rho - target) < eps)[0]
    if idx.size == 0:
        return 0.0
    # longest contiguous run of locked samples = the step
    runs = np.split(idx, np.where(np.diff(idx) > 1)[0] + 1)
    longest = max(runs, key=len)
    return len(longest) * dO


def measure_delta(Omega, rho, eps=1.2e-4, qmax=26):
    """delta from the principal 1/q steps, Delta(1/q) ~ q^-delta, located by
    rho-inversion. The finite-q effective exponent rises slowly toward the
    asymptotic delta (= 3 for the cubic-inflection sine map), so we EXTRAPOLATE:
    fit the 3-point effective exponent delta_eff(q) linearly in 1/q and read the
    intercept (q -> infinity). Returns (delta_infinity, data, raw_tail_slope)."""
    data = []
    for q in range(2, qmax + 1):
        w = step_width_for_rho(Omega, rho, 1.0 / q, eps)
        if w > 8 * (Omega[1] - Omega[0]):           # comfortably above resolution
            data.append((q, w))
    q_arr = np.array([q for q, _ in data], float)
    w_arr = np.array([w for _, w in data], float)
    raw = -np.polyfit(np.log(q_arr[q_arr >= 7]), np.log(w_arr[q_arr >= 7]), 1)[0]
    # centred 3-point effective exponent
    lq, lw = np.log(q_arr), np.log(w_arr)
    qmid = q_arr[1:-1]
    deff = -(lw[2:] - lw[:-2]) / (lq[2:] - lq[:-2])
    msk = (qmid >= 5) & (qmid <= qmax - 3)          # avoid the noisy top edge
    slope, delta_inf = np.polyfit(1.0 / qmid[msk], deff[msk], 1)
    return float(delta_inf), data, float(raw)


def measure_D_boxcount(Omega, rho, tol=1.0e-4):
    """Box-counting dimension: N(r) = boxes where rho rises (covers the mode-locking
    Cantor set) ~ r^-D. Fit the clean scaling window."""
    M = len(rho)
    ns, Ns = [], []
    for n in [50, 75, 110, 165, 250, 375, 560, 840, 1260, 1900, 2850]:
        per = M // n
        r = rho[: n * per].reshape(n, per)
        occ = int(np.count_nonzero((r.max(axis=1) - r.min(axis=1)) > tol))
        ns.append(n); Ns.append(occ)
    ns, Ns = np.array(ns, float), np.array(Ns, float)
    m = (Ns > 5) & (Ns < 0.9 * ns)
    slope, _ = np.polyfit(np.log(ns[m]), np.log(Ns[m]), 1)
    return slope, list(zip(ns.astype(int).tolist(), Ns.astype(int).tolist()))


def main():
    print("Stage B — sine circle map calibration (K = 1). Control, never a finding.\n")
    Omega, rho = critical_sweep()

    D, boxes = measure_D_boxcount(Omega, rho)
    D_ok = abs(D - 0.8700) <= 0.01
    print(f"[D]  box-counting dimension at criticality = {D:.4f}   "
          f"target 0.8700 +- 0.01 -> {'PASS' if D_ok else 'CHECK'}")
    print(f"     box counts (n, N): {boxes}")

    delta, tongues, raw = measure_delta(Omega, rho)
    d_ok = abs(delta - 3.0) <= 0.3
    print(f"\n[delta]  Delta(1/q) ~ q^-delta   q->inf extrapolation = {delta:.3f}   "
          f"(raw finite-q fit {raw:.3f})   target 3.0 +- 0.3 -> {'PASS' if d_ok else 'CHECK'}")
    for q, w in tongues:
        print(f"     1/{q}: width = {w:.6f}")

    passed = bool(D_ok and d_ok)
    report = {
        "stage": "B", "role": "calibration (never a finding)", "K": K_CRIT,
        "D_measured": float(D), "D_target": 0.8700, "D_tol": 0.01, "D_pass": bool(D_ok),
        "delta_measured": float(delta), "delta_raw_finite_q": float(raw),
        "delta_target": 3.0, "delta_tol": 0.3, "delta_pass": bool(d_ok),
        "tongue_widths_by_q": {str(q): float(w) for q, w in tongues},
        "box_counts": {str(n): int(N) for n, N in boxes},
        "calibration_passed": passed,
        "note": ("D and delta are universal properties of any critical circle map "
                 "(sealed rule C); reproducing them verifies the instrument, and is "
                 "never a finding. Proceed to Stage C/D only if PASS."),
    }
    json.dump(report, open("stage_b_results.json", "w"), indent=2)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(7, 6))
        ax.plot(Omega, rho, ".", ms=1, color="#0072B2")
        ax.set_xlabel(r"$\Omega$ (bare frequency)")
        ax.set_ylabel(r"$\rho$ (winding number)")
        ax.set_title(f"Critical sine-circle-map devil's staircase (K=1)\n"
                     f"D = {D:.3f} (target 0.870), delta = {delta:.2f} (target 3.0)")
        fig.tight_layout(); fig.savefig("stage_b_staircase.png", dpi=140)
        print("\n-> stage_b_staircase.png")
    except Exception as e:
        print("  (figure skipped:", e, ")")

    print(f"\nStage B calibration PASSED: {passed}")
    print("-> stage_b_results.json")
    return passed


if __name__ == "__main__":
    main()
