# Address codes under corruption: pre-registration

*Written and committed **before** any code for this study existed or ran. The results will be
reported against these predictions, whichever way they fall.*

## The question

The horizon note (`../../HORIZON_NOTE_machines_that_remember.md`) proposes that quasiperiodic,
cut-and-project style addresses make good memory addresses: self-locating, and robust when the
pointers rot. It also points out that transformer positional encodings are already quasiperiodic
addresses. This study checks both ideas in the smallest honest setting, against boring baselines.

## Part A: self-location from content (can you tell where you are by looking around?)

A track of `N = 2048` cells, each holding one of two symbols (L, S). A reader that has lost its
pointer sees a window of `w` consecutive cells and must work out where it is.

Tracks:
- **periodic**: a length-13 block repeated (the Fibonacci approximant, so it has the same local
  letter mix);
- **Fibonacci**: the golden Sturmian word, the 1-D quasicrystal;
- **random**: i.i.d. symbols with the same letter frequency (`1/φ` for L).

Predictions:
- **A1.** The shortest window `w*` that makes every position unique:
  - periodic: never;
  - Fibonacci: very long, `w* > 500` (Sturmian complexity: only `w + 1` distinct windows of
    length `w` exist, so they must repeat);
  - random: short, `15 ≤ w* ≤ 40`.
- **A2.** With 5% of symbols flipped and window `w = 64`, nearest-match localisation succeeds for
  **> 90%** of positions on the random track and **< 5%** on the Fibonacci track.

The reasoning behind A: the local indistinguishability that makes aperiodic tilings good error
correctors (Li–Boyle: a patch reveals nothing about where it is) should make them *bad*
self-addresses. If A holds, the horizon note's "self-addressing" idea needs rethinking.

## Part B: positional codes in an associative memory (the transformer question)

`N = 256` items are stored under keys that encode their position; `d = 64` dimensions (32
frequency pairs of cos and sin, unit-normalised), except for the random baseline. Retrieval
returns the stored key with the largest dot product with the query (hard attention: the
large-β limit of softmax attention and of a modern Hopfield network). Corruption:
- **(q)** Gaussian noise added to the query (norm ratio `σ`);
- **(m)** the same noise added once to every *stored* key (silent memory corruption).

`σ ∈ {0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5}`, 20 seeds.

Codes:

| code | frequencies `ω_k` (k = 1..32) |
|---|---|
| **periodic (aliased)** | `2πk/64`: a crystal with period 64 < N |
| **harmonic** | `2πk/N`: period N, only low harmonics |
| **RoPE-style** | `10000^(−(k−1)/32)` rad per position, as shipped in transformers |
| **golden** (quasiperiodic) | `2π·frac(k/φ)`: the Kronecker / cut-and-project sequence |
| **random frequencies** | uniform on `(0, 2π)`, redrawn per seed: **the control for golden** |
| **random keys** | i.i.d. Gaussian vectors, unit-normalised: the classic baseline |

Metrics: exact accuracy; **near-hit rate** (retrieved within ±2 of the true position); mean
error distance.

Predictions:
- **B0 (sanity).** At `σ = 0` every code is 100% exact except periodic (aliased), which is exactly
  25%: four identical keys per slot.
- **B1.** For `σ > 0`, random keys have the highest exact accuracy of all codes, at every noise
  level, under both corruptions.
- **B2.** At `σ ≥ 0.75`, golden and random-frequency codes have a higher near-hit rate than random
  keys: their errors land *near* the true position (graceful degradation). Random keys fail to
  anywhere.
- **B3.** RoPE-style has the lowest exact accuracy of the non-aliased sinusoidal codes. At
  `N = 256`, most of its frequencies barely rotate and so carry almost no information.
- **B4 (the real question, predicted null).** Golden versus random frequencies: exact accuracy
  within 2 percentage points at every `σ`, under both corruptions. The quasiperiodic choice gives
  no special advantage over random frequencies.
- **B5.** Stored-key corruption (m) gives the same ranking of codes as query corruption (q).

## What would surprise me

- Golden beating random frequencies by more than 2 points (B4 failing in our favour).
- Fibonacci self-locating well (A failing).

Either would be worth chasing.
