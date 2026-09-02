"""Clean-room radius-saturation protocol implementation.

This package intentionally has no study-data launcher or filesystem data loader.
"""

from .constants import CONFIGS, OFFSETS, PERMUTATION_CONFIGS, RADII
from .errors import ConformanceError, GeometryPreflightFailure, ReproducibilityFailure

__all__ = [
    "CONFIGS", "OFFSETS", "PERMUTATION_CONFIGS", "RADII",
    "ConformanceError", "GeometryPreflightFailure", "ReproducibilityFailure",
]
