# Active skin: exploratory protocol

Implement an engine whose mutable geometric state consists only of retained whole tiles and an explicit true-frontier map. Initialize once from the existing seed immediately after original choice B. Retain tiles with any vertex within 2*S of any true-frontier vertex; discard the rest after each complete scheduler step. Do not reconstruct frontier edges from the truncated tile patch: that would introduce artificial interior edges. Update the frontier by edge toggles as new tiles attach. Rebuild local vertex and overlap indexes only from retained tiles.

Run the skin engine in a separate process. Pass initial seed, random stream and optional slice-29 intervention once. Afterwards its only incoming message is STEP or STOP. It receives no corrections, archived tiles or reference decisions. This is programmatic separation, not an OS security sandbox.

The verifier independently retains and evolves the full patch using the historical rules and scheduler. Before every step compare decorated candidate sets on every original true-frontier edge; compare placements, status, kind, frontier and retained-tile membership afterwards. Abort and report any mismatch; never silently replenish from the archive.

Fixed initial scope: original B continuations 1 and 3, and continuation 1 with the other choice at slice 29. Horizon 120, stopping early on jam or mismatch. Radius 2*S is an engineering choice motivated by the earlier finite-state probe, not a measured thickness or established bound. No radius tuning after a failure without reporting the original failure.

Keep the global patient scheduler unchanged: forced placements have priority across the frontier and guesses use origin-distance order. This isolates present-state retention from scheduling locality. Fixed matching-rule templates are allowed; archived trajectories are not input to the worker.

Record retained tiles, discarded counts, frontier size, tested edge count and any mismatch. Render the retained skin against the verifier's archive in clearly labelled colours. The archived interior is visible only to the observer and is never returned to the worker.
