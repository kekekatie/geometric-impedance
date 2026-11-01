#!/usr/bin/env python3
"""Regenerate the 22 closure forks once and cache their S* states + candidates
to results/baseline/forks.pkl, so Phases 2-4 need not re-run the ~5 min frozen
dedup loop. Cache stores only decorated half-tiles (deterministic replay inputs);
it is a convenience, not a new result."""
from __future__ import annotations
import pickle
from pathlib import Path
import pilot_common as PC

OUT = Path(__file__).resolve().parent.parent / "results" / "baseline" / "forks.pkl"


def main():
    forks = PC.select_forks()
    data = {}
    for f in forks:
        data[f["world"]] = dict(
            Sstar=[tuple(t) for t in f["Sstar"]],
            cs=[tuple(c) for c in f["cs"]],
            edge=tuple(f["edge"]),
            mid=f["mid"],
            meta=f["meta"],
        )
    OUT.write_bytes(pickle.dumps(data))
    print(f"cached {len(data)} forks -> {OUT}")
    print("worlds:", sorted(data))


if __name__ == "__main__":
    main()
