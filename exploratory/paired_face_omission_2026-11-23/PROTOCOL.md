# Paired-face omission: frozen comparisons, no directional prediction

Starting SHA: `6236920f087a223ca3c0d701640afbe2a89ce5e7`. New branch: `experiment/paired-face-omission-2026-11-23`. All sealed experiments stay unchanged. Original three-site reference outputs are copied byte-for-byte from `1922a7b7ff7e30f0ead0781ac6aaf3b924038783` into `inputs/`, with source path, Git blob and SHA256 manifest. The new cuts and corrected decoder come from the starting commit.

| Site | Face A | Face B |
|---|---|---|
| AB_1 e14 | Z3 hallway | Z6 corner ear |
| AB_bal e14 | Z3 middle yard | Z6 middle yard |
| Penrose_1 e14 | Z7 middle yard | Z1 middle yard |
| Penrose_2 e4 | Z1 middle yard | Z4 middle yard |
| Penrose_ear e13 | Z7 hallway | Z6 corner ear |

No directional prediction. Freeze the four coordinate sets per site in `results/arms.json` before new decoding. AB/A/B/0 name the Z-faces **kept**, not omitted. Every arm retains both endpoint X-checks' rounds 1 and 2, plus all live rounds, thin boundary parities and committed frame. Thus arm 0 still has four early endpoint readings; it is not thin. Omitted coordinates remain absent, not zero-filled. Use the same site-independent archive, corrected patch-aware incidence adapter, `(3,3)` caps, p=.001, fixed scored observable, shared-onset inference, original odds weighting and half-credit tie rule.

All five joint-omission arms evaluate the original exhaustive 385,648 histories/site. Reuse sealed per-configuration baseline contributions for AB_1/Penrose_1/Penrose_2: verify their SHA256 and exact credit totals against sealed JSON, and independently replay all eight variants of every 251st configuration, checking baseline per-configuration credits exactly. For AB_bal/Penrose_ear the sealed outputs lack per-configuration credits; replay thin, thick, intact and both face-single omissions in full and require equality to stored unrounded gains. All baseline checks must pass before interpretation. Do not rerun endpoint-single omissions.

For the new arm use the existing deterministic every-2,003rd-history full-scan validation, original unaccelerated marginal with an empty cache, independently restricted full observations, and explicit coordinate-presence assertions. Report checks, mismatches and maximum posterior difference. Save per-configuration joint and reused/replayed baseline credits, resumable completed-site JSON, and verify totals independently. Within each site all arms share identical histories. Stream hashes may differ across sites because their check-row allocations differ; verify each against its own sealed stream.

Calculate from unrounded gains over thin (pp): A loss with B = G_AB−G_B; A loss without B = G_A−G_0; B loss with A = G_AB−G_A; B loss without A = G_B−G_0; I = G_A+G_B−G_AB−G_0. Report signed values, all four gains and their percentages of full gain. Positive I supports partial substitution **on decoder accuracy**; negative I means greater contribution with the partner present; zero means additive costs on this score. G_0 and I answer different questions. No information-theoretic, family-wide, or causal explanation of the residual AB_bal ratio is inferred.

Audit the AB_1/AB_bal comparison independently of scores: align vertices by exact lift identities and confirm projected coordinates; compare tile supports, the lost physical edge, e-to-q mappings, incident-face physical supports, boundary assignments, face neighbours and all shortest X-logical supports through the loss. Distinguish renumbering from physical changes. Draw the shared edge and added tile. Record precisely what “put a finger back on the same edge after adding one tile” establishes, including accompanying code/boundary changes. Leave manuscript edits to Neon.
