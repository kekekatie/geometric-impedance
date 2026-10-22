# Cold restart test

Scope: the same three active-skin histories, retaining radius 2*S and the original patient scheduler. Produce a checkpoint at slice 60 inside a fresh growth worker. The worker runs from its initial seed, prunes every step, emits its own state, and exits. Confirm that exit before launching the resumed process.

Serialize only retained tiles, explicit true frontier, retention radius, RNG state, current slice, intervention flag and format version. No archived geometry, original seed, replay log or verifier decisions are included. The resumed process receives only those serialized bytes and thereafter STEP/STOP commands.

Before restart, verify checkpoint tile order and frontier against the previously recorded skin at 60. Independently advance the original random stream using the historical recorded choice counts and compare its exact state with the checkpoint. These checks stay in the controller and never repair the checkpoint.

After restart, compare every frontier candidate set, ordered placement, status, RNG state and frontier against a full-archive reference held solely in the controller. Also compare per-step counts with the earlier uninterrupted run. Stop on a mismatch. Target slice 120, or the reference jam. The known original continuation-1 jam at 70 must be reproduced, not repaired.

This isolates persistence/restart correctness. It does not broaden the population, prove a geometric memory bound, or remove global scheduling. Do not start motif interpretation on the strength of this test alone.
