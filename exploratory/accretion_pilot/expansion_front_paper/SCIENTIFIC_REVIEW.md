# Scientific review for the manuscript pass

16 October 2026; source baseline `d4e00c5d4396c38bd69b265907b5f3d6c5bc030a`.

## What was checked

Read the two registrations, implementations, saved results, corrected-binning script,
derivation note, growth-rule background, scheduler, candidate generator, decoration-aware
tile identity, rounded configuration key, lift and compatibility-region construction.
The saved-data audit reproduces the reported numbers; it does not certify global completeness
of the candidate generator or existence of infinite completions.

`geometry_checks.py` compares the actual four-pentagon facet normals with the five indexed
internal-space directions, recomputes the observed family/normal alignment, checks the
conditional angle arithmetic, and records registration/implementation addition commits.
Git history puts both registrations before the corresponding implementation; it cannot establish
the absence of earlier private exploration.

## Conditional forcing argument

Assume the chosen finite patch has a valid complete extension. At each exposed site, assume
candidate enumeration includes every tile that can occupy that site in a valid extension,
and the geometry and legality checks are correct. If enumeration returns a unique candidate,
every completion contains it. Reapply the argument after each addition to obtain the forced sequence.
This does not prove that nonempty computed F guarantees an extension, or that the implemented
candidate generator is complete. Simultaneous forced slices still require compatible additions.

The code's F is an intersection of vertex/window half-plane constraints. Its nonemptiness is
not, by itself, a proof supplied here of complete extendability of the decorated patch.
The cut measurement is after the first forced slice. A conditionally fixed future sequence may
be computed in advance without any physical propagation ahead of the constructed boundary.

## Geometry and interpretation

The physical indexed edge directions are 18 + 72j degrees. The internal star directions are
144j degrees. Given the measured dominant-family correspondence and perpendicular strip
direction, elementary arithmetic yields 108 - 2 times cut direction modulo 180 degrees.
The indexed direction correspondence is exact arithmetic; finite-strip alignment and the
family correspondence are empirical inputs. Arbitrary physical vector angles are not generally doubled.
No branch-difference theorem or completeness proof was produced in this pass.

P4 tests only two eligible configurations. Its failure limits the extension of the forced-burst
guarantee to the later changed region; it does not prove all earlier constraints cease at a new choice.
F summarizes current compatibility constraints and need not encode the complete ordering of history.
The placement-time fit is not a speed limit, and forced duration is not spatial width.

## Targeted literature verification

- George Y. Onoda, Paul J. Steinhardt, David P. DiVincenzo and Joshua E. S. Socolar,
  *Growing Perfect Quasicrystals*, Physical Review Letters 60, 2653-2656 (1988).
  [Publisher record](https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.60.2653).
  Local-rule growth of Penrose tilings is prior work; do not claim priority for that principle.
- Connor Hann, Joshua E. S. Socolar and Paul J. Steinhardt,
  *Local growth of icosahedral quasicrystalline tilings*, Physical Review B 94, 014113 (2016).
  [Author manuscript](https://arxiv.org/html/1604.02479v1), Sections II and IV.A;
  [bibliographic record](https://arxiv.org/abs/1604.02479).
  Section II defines six star vectors; IV.A states fifteen possible worm-plane normal vectors.
  A six-edge-family extension of the present correspondence therefore needs a separate argument.

This was a targeted check of the two growth references and the 3D distinction, not a complete
literature survey or final bibliography audit. The manuscript and acknowledgements remain deferred.
