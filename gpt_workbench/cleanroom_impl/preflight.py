from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Mapping

from .constants import CONFIGS, PERMUTATION_CONFIGS
from .errors import GeometryPreflightFailure

Role=Literal["HardFeasibility","FrozenMembership","ExactIdentityCheck","ProvenanceOnly"]


@dataclass(frozen=True)
class GeometryReferenceSource:
    path: str
    git_blob: str
    section: str
    scope: str
    quantity: str
    units: str
    value_status: str
    role: Role


PREFLIGHT_SOURCE=GeometryReferenceSource("gpt_workbench/PREFLIGHT_GEOMETRY_REPORT_V2.md","1c2995cc16bb5b8c0b8777550a461d4593966b48","§1–§6","family×extent","geometry provenance","mixed","RoundedExpectation","ProvenanceOnly")
AUDIT_SOURCE=GeometryReferenceSource("gpt_workbench/SIX_OFFSET_AUDIT_REPORT.md","2470997bf70c16c1ee6af6f13784b4212d56a291","per-patch/Appendix","9×6","r16/singletons","vertices","ExactDiscrete","ExactIdentityCheck")

EXACT_PATCH_REGISTRY={
"silver-e14":((668,655,653,653,671,658),(8,8,7,5,2,2)),
"silver-e16":((1120,1120,1120,1102,1120,1120),(4,4,4,4,4,4)),
"silver-e18":((1698,1718,1698,1723,1723,1723),(3,0,2,3,2,1)),
"golden-e18":((581,597,600,590,585,596),(18,24,14,15,18,25)),
"golden-e20":((1025,1013,1012,1020,1024,1027),(19,16,11,13,10,18)),
"golden-e22":((1535,1545,1559,1537,1547,1539),(18,9,14,12,15,9)),
"platinum-e16":((726,727,730,728,725,735),(65,67,66,66,70,72)),
"platinum-e18":((1170,1168,1171,1165,1167,1170),(60,61,68,61,65,73)),
"platinum-e20":((1719,1719,1704,1716,1704,1718),(51,58,61,58,71,65)),
}

ROUNDED_MORPHOLOGY={
"silver": {"extent":(18,20,22),"n":(5463,6719,8100),"hull_area":(4478,5522,6667),"diameter":(78.8,87.4,96.1),"usable_r16_area":(1370,1976,2690)},
"golden": {"extent":(18,20,22),"n":(3999,4913,5920),"hull_area":(3272,4032,4840),"diameter":(95.9,106.5,116.7),"usable_r16_area":(452,794,1210)},
"platinum": {"extent":(18,20,22),"n":(4604,5660,6806),"hull_area":(3726,4554,5489),"diameter":(88.6,99.9,108.3),"usable_r16_area":(921,1345,1879)},
}


def validate_exact_patch_registry(observed: Mapping[str,tuple[tuple[int,...],tuple[int,...]]]) -> dict[str,tuple[bool,...]]:
    if dict(observed)!=EXACT_PATCH_REGISTRY:
        raise GeometryPreflightFailure("exact 54-patch geometry registry mismatch")
    availability={}
    for label,(r16,singletons) in EXACT_PATCH_REGISTRY.items():
        availability[label]=tuple(s/r <= .05 for s,r in zip(singletons,r16))
    expected={c.label for c in PERMUTATION_CONFIGS}
    actual={k for k,v in availability.items() if all(v)}
    if actual!=expected or {c.label for c in CONFIGS}!=set(EXACT_PATCH_REGISTRY):
        raise GeometryPreflightFailure("frozen M9/M_perm membership mismatch")
    return availability


def report_rounded_expectations(observed: Mapping[str,object]) -> dict[str,object]:
    """Side-by-side provenance only; deliberately performs no equality/gate operation."""
    return {"observed":dict(observed),"rounded_expectation":ROUNDED_MORPHOLOGY,"role":"ProvenanceOnly"}
