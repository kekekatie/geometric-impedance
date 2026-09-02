# Weave-Feature Reconciliation v0.1

## The "discrepancy" is not a discrepancy

The old paper and the new pipeline use **identical weave features**:
  g_degree, g_neighbor_degree_mean, g_local_clustering, g_hop2_size

The difference is **which graph** the features come from:

| | Address source | Weave source | What it measures |
|-|----------------|--------------|------------------|
| Old paper ("identity persistence") | Native coords | **REWIRED** graph | Can you still identify vertices after corruption? |
| New pipeline ("native baseline") | Native coords | **NATIVE** graph | How strong is each channel in the unperturbed tiling? |

The old paper's "weave AUC = 0.740" means: "after scrambling the graph (5E rewiring),
weave features from the *scrambled* graph still predict native identity at 0.74."
This is SUPPOSED to be lower — that's the whole point of the perturbation experiment.

Our "weave AUC = 0.977" means: "native weave features predict native identity at 0.98."
This is the unperturbed baseline, not a perturbation result.

Comparing these two numbers is apples-to-oranges. There is no feature-definition discrepancy.

## Does "address-led" survive?

Using NATIVE (unperturbed) features — which is the fair comparison for "which channel is stronger":

| Substrate | Subset | Address AUC | Weave AUC | Stronger channel |
|-----------|--------|-------------|-----------|------------------|
| AB | full patch | ~0.84 | ~0.98 | WEAVE |
| AB | interior 75% | ~0.98 | ~1.00 | WEAVE (both near ceiling) |
| AB | boundary 25% | ~0.76 | ~0.94 | WEAVE |
| Penrose | full patch | ~0.62 | ~0.94 | WEAVE |
| Penrose | interior 75% | ~0.55 | ~0.91 | WEAVE |
| Penrose | boundary 25% | ~0.64 | ~0.95 | WEAVE |

**Weave wins everywhere, for both substrates, at every spatial scale.**

"AB is address-led" was never a correct reading of the data. The old paper showed that
address *survives perturbation* better than weave does on AB's full patch — which is true
(address 0.874 vs rewired-weave 0.740). But "survives perturbation better" ≠ "is stronger."
Address survives because rewiring doesn't touch it. Weave drops because rewiring IS the
weave perturbation. The asymmetry is built into the experimental design, not the substrate.

## The surviving distinction: redundancy, not leadership

The robust finding is the parachute/backup asymmetry:

> When weave is destroyed (rewired), AB's address catches the hybrid (~0.78 at boundary).
> Penrose's address can't (~0.64 at boundary). AB has redundancy. Penrose doesn't.

This does not require any "leadership" claim. Both substrates are weave-primary.
They differ in whether address provides a working backup.

## Verdict

1. The feature definitions are identical. No reconciliation needed.
2. The "discrepancy" was an apples-to-oranges comparison (native vs rewired features).
3. "Address-led" is dead. Weave is stronger for both substrates, everywhere.
4. The spine should be redundancy/parachute, not leadership.
