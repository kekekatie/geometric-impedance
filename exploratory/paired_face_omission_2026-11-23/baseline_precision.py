"""Distinguish a score change from last-bit binary-float output differences."""
import math
from fractions import Fraction

def verify(credits,counts,gains,reference,site):
    expected={'thick':reference['full_archive_gain_pp'],'AB':reference['intact_gain_pp'],
        'A':next(x['gain_over_thin_pp'] for x in reference['omissions'] if x['omitted']==site['B']),
        'B':next(x['gain_over_thin_pp'] for x in reference['omissions'] if x['omitted']==site['A'])}
    # p/(1-p)=1/999 mathematically. Every doubled credit total is an integer.
    denominator=sum(c*999**(2-k) for k,c in enumerate(counts))
    numerator={a:sum(int(2*c)*999**(2-k) for k,c in enumerate(cs)) for a,cs in credits.items()}
    quantum=Fraction(50,denominator) # one half-credit weighted by a two-fault history, in pp
    comparisons={}
    for a,published in expected.items():
        units=numerator[a]-numerator['thin']
        inferred_units=round(published/float(quantum))
        exact=units*quantum
        assert inferred_units==units,(site['name'],a,'different exact score lattice point')
        # Four absolute score ulps is a conservative bound for subtraction/report rounding.
        bound=400*math.ulp(1.0)
        assert abs(published-float(exact))<=bound and abs(gains[a]-float(exact))<=bound
        assert bound<float(quantum)/1000000
        comparisons[a]=dict(sealed_gain_pp=published,replayed_gain_pp=gains[a],difference_pp=gains[a]-published,
            literal_float_equal=gains[a]==published,exact_gain_fraction=str(exact),doubled_weighted_credit_difference=units)
    return dict(method='unique exact weighted half-credit lattice point; last-bit float differences disclosed',
                score_quantum_pp=float(quantum),comparisons=comparisons)
