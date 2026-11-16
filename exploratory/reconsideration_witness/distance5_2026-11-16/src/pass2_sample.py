"""Frozen Pass 2 sampling: 25,000 distinct ordinary-fault triples, seed + hash.

The 370 ordinary-fault primitives are indexed in the canonical nd_run pool order
(data X/Z over 5 rounds, then MZ on Z-stabs, then MX on X-stabs). A triple is a
sorted tuple of 3 distinct indices. We draw 25,000 DISTINCT triples uniformly
without replacement under a frozen seed, sort them canonically, and hash them, so
the design is reproducible and auditable independent of any decode outcome.
"""
import hashlib, random, json, sys
import nd_surface

SEED = 20261116
N_TRIPLES = 25000


def primitives(d=5):
    s = nd_surface.Surface(d)
    P = [('X', q, t) for q in s.DATA for t in range(5) for _ in (0,)]  # placeholder
    P = []
    for q in s.DATA:
        for t in range(5):
            for tag in ('X', 'Z'):
                P.append((tag, q, t))
    P += [('MZ', k, t) for k in s.ZSTABS for t in range(5)]
    P += [('MX', k, t) for k in s.XSTABS for t in range(5)]
    return P


def draw(seed=SEED, n=N_TRIPLES, npool=370):
    rng = random.Random(seed)
    seen = set()
    while len(seen) < n:
        t = tuple(sorted(rng.sample(range(npool), 3)))
        seen.add(t)
    triples = sorted(seen)
    blob = ';'.join(f'{a},{b},{c}' for a, b, c in triples).encode()
    h = hashlib.sha256(blob).hexdigest()
    return triples, h


if __name__ == '__main__':
    P = primitives()
    assert len(P) == 370, len(P)
    triples, h = draw()
    print('n_triples', len(triples))
    print('seed', SEED)
    print('sha256', h)
    print('first3', triples[:3])
    print('last3', triples[-3:])
    # also a fixed 250-triple cap subset: the first 250 in canonical order
    cap = triples[:250]
    blob = ';'.join(f'{a},{b},{c}' for a, b, c in cap).encode()
    print('cap250_sha256', hashlib.sha256(blob).hexdigest())
