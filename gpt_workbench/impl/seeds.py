"""
Stable, keyed seed registry (conditional-null v4.1 §5; locality repair item 1).

Every RNG is addressed by an explicit key tuple and seeded by blake2b(ROOT | key) -> int, which is
reproducible across processes and machines. Python's process-salted built-in hash() is used NOWHERE.
Three roots are frozen:
  - address-permutation:  SEED_ADDRESS_PERM_ROOT (20260829)  -> children indexed by rep b
  - capacity:             SEED_CAPACITY_ROOT     (20260830)  -> children indexed 0..199
  - locality-ladder:      SEED_LOCALITY_ROOT     (20260829)  -> keyed substreams (design diagnostic)
Parity has NO seed (it is deterministic).
"""
import hashlib
import numpy as np
from . import constants as C


def _seed_int(root, *key):
    payload = "|".join(repr(x) for x in (root, *key)).encode()
    return int.from_bytes(hashlib.blake2b(payload, digest_size=16).digest(), "big")


def rng(root, *key):
    """Deterministic numpy Generator addressed by (root, *key). Order-stable, process-independent."""
    return np.random.default_rng(_seed_int(root, *key))


def address_perm_rng(*key):
    """Address-permutation substream (root 20260829). Key with stable identifiers, e.g.
    (family, tier, offset, motif_key, b)."""
    return rng(C.SEED_ADDRESS_PERM_ROOT, *key)


def capacity_rng(draw_index):
    """Capacity substream (root 20260830), child index 0..199."""
    assert 0 <= draw_index < C.CAPACITY_DRAWS
    return rng(C.SEED_CAPACITY_ROOT, "capacity", int(draw_index))


def locality_rng(*key):
    """Locality-ladder design-diagnostic substream (root 20260829, blake2b keyed)."""
    return rng(C.SEED_LOCALITY_ROOT, *key)
