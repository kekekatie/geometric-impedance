"""Machine-readable frozen registries and numerical constants."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Family = Literal["silver", "golden", "platinum"]
Tier = Literal["small", "medium", "large"]


@dataclass(frozen=True, order=True)
class Config:
    config_id: int
    family: Family
    tier: Tier
    extent: int
    rank: int

    @property
    def label(self) -> str:
        return f"{self.family}-e{self.extent}"


RADII = (2, 4, 8, 12, 16)
OFFSETS = ((0.13, 0.37), (0.29, 0.11), (0.41, 0.23),
           (0.05, 0.47), (0.19, 0.31), (0.37, 0.09))

# General arrays are tier-major.
CONFIGS = (
    Config(0, "silver", "small", 14, 8),
    Config(1, "golden", "small", 18, 10),
    Config(2, "platinum", "small", 16, 12),
    Config(3, "silver", "medium", 16, 8),
    Config(4, "golden", "medium", 20, 10),
    Config(5, "platinum", "medium", 18, 12),
    Config(6, "silver", "large", 18, 8),
    Config(7, "golden", "large", 22, 10),
    Config(8, "platinum", "large", 20, 12),
)
PERMUTATION_CONFIGS = tuple(CONFIGS[i] for i in (0, 1, 3, 4, 6, 7, 8))

# Capacity children are family-major, then tier, then offset-fast.
CAPACITY_CONFIGS = tuple(
    next(c for c in CONFIGS if c.family == family and c.tier == tier)
    for family in ("silver", "golden", "platinum")
    for tier in ("small", "medium", "large")
)
CAPACITY_PATCH_AXIS = tuple((c, oi) for c in CAPACITY_CONFIGS for oi in range(6))

BOUNDARY_TIMES = tuple(float(round(x, 4)) for x in __import__("numpy").linspace(0.0, 8.0, 161))
FIT_TIMES = (2.00,2.05,2.10,2.20,2.25,2.30,2.40,2.45,2.55,2.60,2.70,2.75,
             2.85,2.95,3.00,3.10,3.20,3.30,3.40,3.50,3.60,3.70,3.85,3.95,
             4.05,4.20,4.30,4.45,4.55,4.70,4.85,5.00,5.15,5.30,5.45,5.60,
             5.80,5.95,6.15,6.30,6.50,6.70,6.90,7.10,7.30,7.55,7.75,8.00)

GBT_PARAMS = dict(max_depth=3, max_iter=250, learning_rate=0.06,
                  l2_regularization=1.0, random_state=0)

COMMON_MIN = 400
SLAB_MIN = 100
LAUNCHES_PER_SLAB = 50
LAUNCHES_PER_PATCH = 200
ADDRESS_REPETITIONS = 1000
CAPACITY_DRAWS = 200


def validate_registries() -> None:
    if len(CONFIGS) != 9 or tuple(c.config_id for c in CONFIGS) != tuple(range(9)):
        raise RuntimeError("invalid general configuration registry")
    if len(PERMUTATION_CONFIGS) != 7 or len(CAPACITY_PATCH_AXIS) != 54:
        raise RuntimeError("invalid frozen membership")
    if len(FIT_TIMES) != 48 or len(set(FIT_TIMES)) != 48:
        raise RuntimeError("invalid fit-time registry")
    if not set(FIT_TIMES).issubset(set(BOUNDARY_TIMES)):
        raise RuntimeError("fit times are not boundary-grid members")


validate_registries()
