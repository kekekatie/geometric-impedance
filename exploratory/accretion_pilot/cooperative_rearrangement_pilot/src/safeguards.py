#!/usr/bin/env python3
"""
safeguards.py -- the maintained pilot's validation safeguards.

These are the independently-audited, tested implementations from the 3 November
2026 Codex audit (`audit_2026-11-03/audit_tools.py`, audit branch
`audit/cooperative-rearrangement-2026-11-03`, commit
`e7ff8ffdc1a746a4622a91c3cbe934999c15609f`). Per the integration brief, the pilot
REUSES them as the single source of truth (no re-implementation, no silent
substitution of a different method). This module is a thin, documented re-export
shim; the tested code lives in the preserved audit directory.

Adopted functions:
  * classify_region(band_constraints, region, full_verdict)
        -- the no-change shortcut now PROPAGATES the established full-band verdict
           (including 'unresolved'); it never assumes infeasibility after an LP
           failure. (Supersedes the hard-coded 'infeasible' shortcut in the
           historical part3_necessary.main.)
  * completed_replacement_legal(exterior, region, fill)
        -- explicit template-membership, footprint-coverage, non-overlap (general
           polygon intersection area, not the point-containment heuristic),
           boundary/interface preservation, and all affected old/new vertex-star
           checks against the FULL exterior. Empty or incomplete fillings FAIL.
           (Supersedes coop_common.completed_replacement_legal, which ignored the
           region, skipped coverage/template checks, and accepted empty fillings.)
  * true_frontier_counts(state, band)
        -- counts candidates only on the SAVED true-frontier edges, verifying edge
           ownership and excluding pruning-exposed inner-boundary edges.
           (Supersedes part5_score.frontier_candidate_counts, which counted the
           combined skin boundary.)

Also re-exported: area, intersection, overlap, boundary, template_ok (the audit's
convex-polygon geometry helpers used by the validator).
"""
from __future__ import annotations
import sys
from pathlib import Path

# the preserved, independently-audited artifact directory (single source of truth)
_AUDIT_DIR = Path(__file__).resolve().parents[1] / "audit_2026-11-03"
if not (_AUDIT_DIR / "audit_tools.py").is_file():
    raise RuntimeError(f"audited safeguards not found at {_AUDIT_DIR}/audit_tools.py")
if str(_AUDIT_DIR) not in sys.path:
    sys.path.insert(0, str(_AUDIT_DIR))

from audit_tools import (  # noqa: E402,F401
    classify_region,
    completed_replacement_legal,
    true_frontier_counts,
    area,
    intersection,
    overlap,
    boundary,
    template_ok,
)

AUDIT_COMMIT = "e7ff8ffdc1a746a4622a91c3cbe934999c15609f"
__all__ = ["classify_region", "completed_replacement_legal", "true_frontier_counts",
           "area", "intersection", "overlap", "boundary", "template_ok", "AUDIT_COMMIT"]
