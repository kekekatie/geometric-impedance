# Archive-free post-prune retrodiction verification

Post-review check dated 27 October 2026. Source commit:
`a96c88b83a1d80f915dc29e0ffa193a6164f6e77`.
See PROTOCOL_2026-10-27.md for tolerances fixed before the pilot.
Historical closure files are not modified.

## What the reader receives
JSON on stdin containing only:
- surviving decorated skin triangles and their current physical coordinates;
- rhombus edge length;
- a common pre-fork physical origin, representing lift coordinate zero;
- the common four-consecutive-layer to window-rank map;
- fixed window normals and offsets;
- both historical hypothesis regions as half-plane constraints.

The origin and layer map are shared conventions established before A/B commitment.
The origin may refer to a position whose tile has since been deleted: its two
coordinates are retained as a reference frame, not a historical tile or lift map.
This check does not recover that historical origin from an unanchored skin.
The candidate hypotheses also remain supplied historical information. Thus the
test is anchored, global retrodiction, not blind/local decoding or history-free inference.

The reader receives no full patch, deleted tiles, per-vertex lift labels, true
option, random stream, case name, original scores or answer-dependent alignment.
The controller's case envelopes contain both a payload and a separate reference;
only the payload goes across the subprocess stdin boundary.

## How coordinates are recovered
Each present connected component is lifted using only its own rhombus-length edges.
For one vertex per component, the reader inverts its physical displacement from
the common origin. With five pentagonal directions, the integer kernel is the
all-ones vector. The numerical inverse searches normalized coefficients
`|k_j-k_4| <= 128` exhaustively with a meet-in-the-middle lookup. It accepts
exactly one solution within `1e-7` edge units.

The all-ones/layer shift must put the whole component into the supplied common
four-layer slab. A missing or nonunique alignment is unreconstructible, not a
guessed label or censoring. All vertices are checked against the coefficient
bound and physical projection. Components are not joined through deleted tiles.

This is a bounded numerical reconstruction, not a proof of uniqueness over
unbounded noisy integer coordinates. Out-of-slab components fail explicitly;
the reader does not silently drop vertices to improve the fit.

Constraints are computed from reconstructed coordinates. Independent half-plane
clipping yields region polygons, area and intersection with each supplied
hypothesis. Selection uses the original `1e-9` area threshold. Both compatible
hypotheses or neither yield an ambiguous index.

## Isolation
`skin_reader.py` uses only Python's standard library. The driver invokes it in
a fresh interpreter with `-I -S`, in an empty temporary directory, sending JSON
through stdin. After standard-library imports the reader installs an audit hook
that rejects file opens and network/subprocess calls. It does not import the
engine, reference tiling, verifier or source results. This is an auditable
process/data separation, not an OS security sandbox.

The full-history controller reconstructs only the previously selected cases.
It checks original patch sizes, streams, run lengths, guess steps, departure
brackets and saved areas. Full-patch lifts appear only in analyst references for
comparison, never in reader input.

## Reproduction
From this directory, with the parent requirements installed:

```sh
python verify_reader.py --pilot
python test_reader.py
python verify_reader.py
```

Once the committed case envelopes are present, no growth engine or third-party
packages are needed for a fresh readout comparison:

```sh
python verify_reader.py --verify-only
python test_reader.py
```

To regenerate rather than reuse cached cases, use a disposable checkout and move
`results/cases/` aside before running `verify_reader.py`. Regeneration uses
the original closure world IDs and streams, not a new sampling campaign.

For a direct reader invocation, extract one case's `payload` as a JSON object
and pipe it to `python -I -S skin_reader.py`. Never pass the case envelope itself.

## Files
- `skin_reader.py`: archive-free implementation.
- `verify_reader.py`: preparation/reference controller and process comparisons.
- `test_reader.py`: invalid-input, isolation, disconnected-skin and invariance checks.
- `results/cases/`: exact surviving-skin payloads plus separate analyst references.
- `results/reader-output/`: independent reader results, reconstructed coordinates and polygons.
- `results/comparisons.json`, `summary.json`: full comparison.
- `results/pilot_*.json`: initial three-case comparison.
- `results/checks.json`: meaningful checks.
- `VERIFICATION_2026-10-27.md`: scientific findings and scope.

A consistent nontrivial lift-gauge change and a swap of hypothesis ordering are
tested on every compared continuation. Raw residuals are retained; 'zero' is
always interpreted through the declared numerical threshold.
