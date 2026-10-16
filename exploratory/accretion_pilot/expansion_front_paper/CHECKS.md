# Saved-data checks - 16 October 2026

New descriptive reanalysis of saved data; not an independent growth-engine replication. Configuration keys retain the existing rounded, translation-normalized definition. First occurrence per key is retained.

| Check | Recomputed result |
|---|---|
| date | "2026-10-16" |
| base_commit | "d4e00c5d4396c38bd69b265907b5f3d6c5bc030a" |
| unique | [45, 45] |
| overlap | 13 |
| new_configurations | 32 |
| new_P1 | 32 |
| later_guess | [13, 14] |
| no_later_guess | [31, 31] |
| followup_families | {"0": 16, "1": 0, "2": 13, "3": 6, "4": 10} |
| new_families | {"0": 11, "2": 9, "3": 5, "4": 7} |
| elongated | 41 |
| maximum_angle_deviation | 2.593516733412116 |
| placement_fit | {"n": 4331, "intercept": 2.4418750822528477, "slope": 1.0873221430838396} |
| registered_C1 | [44, 45] |
| registered_C2 | [17, 17] |
| registered_C3 | {"directions": 4, "families": 4} |
| registered_C4 | [41, 41] |
| corrected_bins | {"90": {"0": 22}, "54": {"1": 1}, "162": {"3": 3}, "18": {"2": 11}, "126": {"4": 8}} |
| P1 | [45, 45] |
| P2 | {"passing": 90, "n": 90, "median": 0.6695402298850575, "quartiles": [0.6619718309859155, 0.6857142857142857]} |
| P3 | [44, 45] |
| P4 | {"passing": 1, "n": 2, "identical": 44, "covered": 92} |
| burst_status | {"stalled": 24, "cap": 66} |
| guesses | {"0": 380, "1": 70} |
| noncore_control | {"identical": 1208, "covered": 2242} |
| choice_tile_only_cut | {"found": 14, "total": 45, "same_direction": 14} |

P4 counts covered tile-comparison instances across ordered continuation pairs, not independent tiles or trials. Forty slices is a censoring cap, not a measured stopping time or width. The fit is a pooled placement-time association, not a propagation speed.

## Figure selection
{
  "criterion": "Among first occurrences with ratio >= 3, minimize absolute distance of n_strip from the eligible median; break ties lexicographically by key.",
  "eligible": 41,
  "median_n_strip": 84.0,
  "key": "2a3cfb2c41f77386",
  "world": 19,
  "slice": 31,
  "n_strip": 84,
  "ratio": 8.007729915172416
}

## Provenance
{
  "cut_direction\\results\\worlds.json": "0b88c2f13bc1706a9d9b4a682b1d9be92e68547a4db9f03e585e43f2f7d7a1cb",
  "settled_test\\results\\results.json": "c6b157d6de7e8e4e74d72fd97a16335c1b560d8991201490dd6c376c860f31a9"
}
