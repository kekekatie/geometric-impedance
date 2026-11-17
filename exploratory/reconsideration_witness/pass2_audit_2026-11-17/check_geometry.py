"""Independent syndrome/parity checks for every minimum crossing representative."""
import audit

s = audit.nd_surface.Surface(5)
out = {}
for sector in ('X', 'Z'):
    weight, reps = audit.logical_reps(s, sector)
    old = audit.pass2.crossing_reps(s, sector)[1]
    bad = 0
    for tag, qs in old:
        dz, dx, zl, xl = s.simulate(*audit.nd_run.compose([(tag, q, 1) for q in qs]))
        bad += bool(any(dz.values()) or any(dx.values()))
    for qs in reps:
        for onset in (1, 2):
            dz, dx, zl, xl = s.simulate(*audit.nd_run.compose([(sector, q, onset) for q in qs]))
            assert not any(dz.values()) and not any(dx.values())
            assert (zl if sector == 'X' else xl) == 1
    out[sector] = dict(min_weight=weight, count=len(reps), correct_syndrome_and_parity_checks=2*len(reps),
                       old_representatives_with_nonzero_syndrome=bad)
audit.save('geometry_validation.json', out)
print(out)
