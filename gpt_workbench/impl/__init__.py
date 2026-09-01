"""
Production implementation of the SEALED radius-saturation protocol suite (design seal 4ec0536).

Modular, independently-testable components. The sealed manifests remain authoritative; if this code
and a sealed manifest disagree, the manifest wins. This package runs NO scientific study: it provides
the pipeline; the confirmatory run on the nine sealed study configurations is NOT authorized here.
"""
from . import (constants, seeds, substrate, features, matching, engines,
               aggregation, regression, gates, workflows, msd)

__all__ = ["constants", "seeds", "substrate", "features", "matching", "engines",
           "aggregation", "regression", "gates", "workflows", "msd"]
