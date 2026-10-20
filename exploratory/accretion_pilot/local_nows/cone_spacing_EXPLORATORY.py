#!/usr/bin/env python3
"""EXPLORATORY (after cone.py's registered run): was the failure of causally honest local nows due to SIMULTANEOUS
independent choices? Re-run CONE(H=24) with simultaneous choices forced at least 48 edges apart (the spacing the
faster-than-light R=24 rule had). That spacing is itself non-local coordination. Writes results/cone_spacing_EXPLORATORY.txt."""
import os, collections
from multiprocessing import Pool
import numpy as np
import cone as CO
import local_nows as LN


def job(k):
    CO.SPACING = 48.0
    return CO.run((k, 24))


if __name__ == "__main__":
    with Pool(4, maxtasksperchild=1) as p:
        out = p.map(job, range(LN.N_WORLDS))
    bad = sum(r["status"] == "JAM" or r["dead_at_end"] for r in out)
    lines = [f"EXPLORATORY CONE(H=24) with simultaneous choices >= 48 edges apart: bad {bad}/24; statuses "
             f"{dict(collections.Counter(r['status'] for r in out))}; choices in the slice of death "
             f"{dict(collections.Counter(r['died_choices'] for r in out if r['died'] is not None))}; tiles median {np.median([r['tiles'] for r in out]):.0f}"]
    print("\n".join(lines))
    open(os.path.join(LN.RES, "cone_spacing_EXPLORATORY.txt"), "w").write("\n".join(lines) + "\n")
