"""Stage 2, component 1: rotated-surface-code geometry + pre-flag retention accounting.

Built on the 2D pre-registration (commit 3213f62). numpy-only, exact where possible.

This is the FIRST of two 2D components. It tests the predictions that do not need a
full decoder:
  * the geometry: a bulk data qubit's star is 4 checks (2 X + 2 Z), edge 3, corner 2
    -- the spatial witness bracket, and the basis of D4;
  * the Shredder-resolution accounting (D1b): over background syndrome activity, the
    sparse activity-triggered scar archive costs ~ p_eff * N * L, far below the thick
    window's / dense lip-plane's N * L, with the saving growing as the physical error
    rate p -> 0; the post-flag local-diamond query is O(1), independent of distance.

The SECOND component (re-judgment accuracy: thin-alone fails where thin+archive and
thick succeed -- D1/D2/D3) needs a full 2D sliding-window MWPM erasure decoder and is
a separate build; this file does not claim it.
"""

import json
import numpy as np


# ---- rotated surface-code geometry -----------------------------------------
def build_code(d):
    """Rotated surface code, distance d. Data qubits at integer (x,y), 0<=x,y<d.

    Stabilizers at half-integer centres; bulk weight-4, boundary weight-2. X-type
    rough boundaries on top/bottom, Z-type on left/right (standard rotated layout).
    Returns (data, stabs) where stabs[k] = {'type','support'(frozenset of data),'c'}.
    """
    data = [(x, y) for x in range(d) for y in range(d)]
    dataset = set(data)
    stabs = []
    for i in range(-1, d):
        for j in range(-1, d):
            c = (i + 0.5, j + 0.5)
            corners = [(i, j), (i + 1, j), (i, j + 1), (i + 1, j + 1)]
            support = [q for q in corners if q in dataset]
            if len(support) == 0:
                continue
            typ = 'X' if (i + j) % 2 == 0 else 'Z'
            if len(support) == 4:
                stabs.append({'type': typ, 'support': frozenset(support), 'c': c})
            elif len(support) == 2:
                (x0, y0), (x1, y1) = sorted(support)
                horizontal = (y0 == y1)      # the two data share a row -> top/bottom edge
                # keep X weight-2 on top/bottom (horizontal pairs); Z on left/right
                if (typ == 'X' and horizontal) or (typ == 'Z' and not horizontal):
                    stabs.append({'type': typ, 'support': frozenset(support), 'c': c})
            # weight-1 (corner-only) plaquettes are dropped
    # star of each data qubit = stabilizers touching it
    star = {q: [k for k, s in enumerate(stabs) if q in s['support']] for q in data}
    return data, stabs, star


def classify(d, q):
    x, y = q
    edge = (x in (0, d - 1)) + (y in (0, d - 1))
    return {0: 'bulk', 1: 'edge', 2: 'corner'}[edge]


# ---- background syndrome activity (phenomenological) ------------------------
def simulate_detectors(d, stabs, T, p, rng):
    """Phenomenological noise: each round, each data qubit gets an X error w.p. p and
    a Z error w.p. p; each stabilizer measurement flips w.p. p. X errors are seen by
    Z-stabilizers, Z errors by X-stabilizers. Returns detector array D[N, T] (0/1)."""
    data = [(x, y) for x in range(d) for y in range(d)]
    didx = {q: i for i, q in enumerate(data)}
    N = len(stabs)
    xacc = np.zeros(len(data), dtype=np.uint8)   # cumulative X per data qubit
    zacc = np.zeros(len(data), dtype=np.uint8)
    prev = np.zeros(N, dtype=np.uint8)
    D = np.zeros((N, T), dtype=np.uint8)
    for t in range(T):
        xacc ^= (rng.random(len(data)) < p).astype(np.uint8)
        zacc ^= (rng.random(len(data)) < p).astype(np.uint8)
        synd = np.zeros(N, dtype=np.uint8)
        for k, s in enumerate(stabs):
            acc = zacc if s['type'] == 'X' else xacc   # X-stab sees Z errors, etc.
            v = 0
            for q in s['support']:
                v ^= int(acc[didx[q]])
            if rng.random() < p:
                v ^= 1
            synd[k] = v
        D[:, t] = synd ^ prev
        prev = synd
    return D


# ---- the three retention schemes (pre-flag) --------------------------------
def retention(D, N, L):
    """Pre-flag retained state over the last L rounds, three ways.

    thick/dense are dense N*L (thick is an ACTIVE decoding graph, dense is passive
    storage). sparse keeps only fired detectors (coordinates)."""
    window = D[:, -L:]
    fired = int(window.sum())
    coord_bits = int(np.ceil(np.log2(max(N, 2)))) + int(np.ceil(np.log2(max(L, 2))))
    return {
        'thick_active_bits': N * L,
        'dense_lipplane_bits': N * L,
        'sparse_events': fired,
        'sparse_bits': fired * coord_bits,
        'empirical_fire_rate': fired / (N * L),
    }


def main():
    out = {'built_on': '3213f62', 'note': 'component 1 of 2 (geometry + accounting); '
           'the re-judgment decoder (D1/D2/D3) is a separate build'}

    # geometry: star sizes
    geo = {}
    for d in (3, 5, 7):
        data, stabs, star = build_code(d)
        sizes = {'bulk': set(), 'edge': set(), 'corner': set()}
        for q in data:
            sizes[classify(d, q)].add(len(star[q]))
        geo[d] = {'n_data': len(data), 'n_stabs': len(stabs),
                  'expected_n_stabs': d * d - 1,
                  'star_sizes': {k: sorted(v) for k, v in sizes.items()}}
    out['geometry'] = geo

    # the onset-lip query is O(1): star x onset interval
    out['postflag_query_size'] = {
        'bulk (4 checks) x 2-round onset': 4 * 2,
        'edge (3) x 2': 3 * 2, 'corner (2) x 2': 2 * 2,
        'note': 'independent of distance d -- the local diamond fed to the restorer'}

    # accounting sweep (D1b): sparse vs dense/thick across p and d
    L = 4
    T = 12
    rng = np.random.default_rng(0)
    sweep = []
    for d in (3, 5, 7):
        data, stabs, star = build_code(d)
        N = len(stabs)
        for p in (0.05, 0.02, 0.01, 0.005, 0.002, 0.001):
            # average over trials for a stable fire rate
            accs = [retention(simulate_detectors(d, stabs, T, p, rng), N, L)
                    for _ in range(40)]
            fire = float(np.mean([a['empirical_fire_rate'] for a in accs]))
            sp_bits = float(np.mean([a['sparse_bits'] for a in accs]))
            dense = N * L
            coord_bits = int(np.ceil(np.log2(max(N, 2)))) + int(np.ceil(np.log2(max(L, 2))))
            sweep.append({
                'd': d, 'N': N, 'p': p, 'L': L,
                'thick_dense_bits': dense,
                'sparse_bits_mean': round(sp_bits, 1),
                'fire_rate': round(fire, 4),
                'sparse_over_dense': round(sp_bits / dense, 4),
                'saving_factor_dense_over_sparse': round(dense / sp_bits, 1) if sp_bits else None,
                'coord_bits_per_event': coord_bits})
    out['accounting_sweep'] = sweep

    with open('stage2_accounting_handback.json', 'w') as f:
        json.dump(out, f, indent=2, default=str)
    _print(out)
    return out


def _print(out):
    print("=" * 76)
    print("STAGE 2 (component 1): surface-code geometry + pre-flag retention accounting")
    print("=" * 76)
    print("\n### geometry (star = the spatial witness diamond)")
    for d, g in out['geometry'].items():
        ok = "OK" if g['n_stabs'] == g['expected_n_stabs'] else "MISMATCH"
        print(f"  d={d}: {g['n_data']} data, {g['n_stabs']} stabs "
              f"(expect {g['expected_n_stabs']}) [{ok}]  star sizes: {g['star_sizes']}")
    print("\n### post-flag query size (O(1), distance-independent)")
    for k, v in out['postflag_query_size'].items():
        print(f"  {k}: {v}")
    print("\n### accounting sweep (D1b): sparse scar vs dense/thick N*L, L=4")
    print(f"  {'d':>2}{'N':>5}{'p':>8}{'fire':>8}{'dense':>8}{'sparse':>9}"
          f"{'sp/dense':>10}{'saving':>9}")
    for r in out['accounting_sweep']:
        print(f"  {r['d']:>2}{r['N']:>5}{r['p']:>8}{r['fire_rate']:>8}"
              f"{r['thick_dense_bits']:>8}{r['sparse_bits_mean']:>9}"
              f"{r['sparse_over_dense']:>10}{str(r['saving_factor_dense_over_sparse']):>9}")
    print("\n  Sparse scar cost tracks the firing rate (~ p); dense/thick is p-independent,")
    print("  so the sparse archive's saving over thick GROWS as the error rate falls.")


if __name__ == '__main__':
    main()
