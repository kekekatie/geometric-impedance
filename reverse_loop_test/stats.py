#!/usr/bin/env python3
"""
Reverse-Loop Test -- equivalence statistics.

Implements the protocol's statistical requirements (Sec. 4):
  * Cohen's d with bootstrap CI (effect sizes everywhere, no bare p-values).
  * TOST (two one-sided tests) for equivalence, with pre-registered bounds
    +-0.05 * d_zone expressed in Cohen's d units.
  * Two-sample KS test (distribution shape).
  * Benjamini-Hochberg FDR across the comparison grid (raw + adjusted).
"""

import numpy as np
from scipy import stats


def cohen_d(a, b):
    """Cohen's d for independent samples (b is the reference, e.g. C0)."""
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    na, nb = len(a), len(b)
    va, vb = a.var(ddof=1), b.var(ddof=1)
    sp = np.sqrt(((na - 1) * va + (nb - 1) * vb) / (na + nb - 2))
    if sp == 0:
        return 0.0
    return (a.mean() - b.mean()) / sp


def cohen_d_ci(a, b, n_boot=2000, seed=0, alpha=0.05):
    """Bootstrap percentile CI for Cohen's d."""
    rng = np.random.default_rng(seed)
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    d0 = cohen_d(a, b)
    boots = np.empty(n_boot)
    for i in range(n_boot):
        aa = a[rng.integers(0, len(a), len(a))]
        bb = b[rng.integers(0, len(b), len(b))]
        boots[i] = cohen_d(aa, bb)
    lo, hi = np.quantile(boots, [alpha / 2, 1 - alpha / 2])
    return d0, float(lo), float(hi)


def tost(a, b, low_d, high_d, alpha=0.05):
    """
    Two one-sided tests for equivalence of means of `a` and `b`.
    Bounds low_d, high_d are in Cohen's d units; converted to raw units with the
    pooled SD. Returns dict with the two one-sided p-values, combined p,
    the 90% CI of the mean difference, and an `equivalent` flag.
    """
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    na, nb = len(a), len(b)
    va, vb = a.var(ddof=1), b.var(ddof=1)
    sp = np.sqrt(((na - 1) * va + (nb - 1) * vb) / (na + nb - 2))
    diff = a.mean() - b.mean()
    se = np.sqrt(va / na + vb / nb)
    df = (va / na + vb / nb) ** 2 / (
        (va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1)
    ) if se > 0 else na + nb - 2
    low_raw = low_d * sp
    high_raw = high_d * sp
    if se == 0:
        equiv = (low_raw <= diff <= high_raw)
        return dict(diff=float(diff), se=0.0, low_raw=float(low_raw),
                    high_raw=float(high_raw), p_lower=0.0 if equiv else 1.0,
                    p_upper=0.0 if equiv else 1.0,
                    p_tost=0.0 if equiv else 1.0, equivalent=bool(equiv),
                    ci90_lo=float(diff), ci90_hi=float(diff))
    t_lower = (diff - low_raw) / se       # H0: diff <= low  -> upper tail
    t_upper = (diff - high_raw) / se      # H0: diff >= high -> lower tail
    p_lower = stats.t.sf(t_lower, df)
    p_upper = stats.t.cdf(t_upper, df)
    p_tost = max(p_lower, p_upper)
    tcrit = stats.t.ppf(1 - alpha, df)
    ci_lo = diff - tcrit_se(tcrit=tcrit_val(alpha, df), se=se)
    ci_hi = diff + tcrit_se(tcrit=tcrit_val(alpha, df), se=se)
    return dict(diff=float(diff), se=float(se), df=float(df),
                low_raw=float(low_raw), high_raw=float(high_raw),
                p_lower=float(p_lower), p_upper=float(p_upper),
                p_tost=float(p_tost), equivalent=bool(p_tost < alpha),
                ci90_lo=float(ci_lo), ci90_hi=float(ci_hi))


def tcrit_val(alpha, df):
    return stats.t.ppf(1 - alpha, df)


def tcrit_se(tcrit, se):
    return tcrit * se


def tost_one_sample(x, low_raw, high_raw, alpha=0.05):
    """
    One-sample / paired equivalence: is the mean of `x` within [low_raw,
    high_raw] (raw units)? Used for matched-set paired differences (Exp 1) and
    for loop holonomy vs 0 (Exp 2). Returns the two one-sided p-values, combined
    p, the (1-2*alpha) CI of the mean, and an `equivalent` flag.
    """
    x = np.asarray(x, float)
    n = len(x)
    mean = float(x.mean())
    sd = float(x.std(ddof=1)) if n > 1 else 0.0
    se = sd / np.sqrt(n) if n > 0 else 0.0
    if se == 0:
        equiv = (low_raw <= mean <= high_raw)
        p = 0.0 if equiv else 1.0
        return dict(mean=mean, se=0.0, p_lower=p, p_upper=p, p_tost=p,
                    equivalent=bool(equiv), ci_lo=mean, ci_hi=mean)
    df = n - 1
    t_lower = (mean - low_raw) / se
    t_upper = (mean - high_raw) / se
    p_lower = stats.t.sf(t_lower, df)
    p_upper = stats.t.cdf(t_upper, df)
    p_tost = max(p_lower, p_upper)
    tcrit = stats.t.ppf(1 - alpha, df)
    return dict(mean=mean, se=float(se), p_lower=float(p_lower),
                p_upper=float(p_upper), p_tost=float(p_tost),
                equivalent=bool(p_tost < alpha),
                ci_lo=float(mean - tcrit * se), ci_hi=float(mean + tcrit * se))


def ks_test(a, b):
    """Two-sample Kolmogorov-Smirnov test."""
    s, p = stats.ks_2samp(np.asarray(a, float), np.asarray(b, float))
    return dict(ks_stat=float(s), ks_p=float(p))


def benjamini_hochberg(pvals):
    """BH-adjusted p-values (q-values). Returns array aligned to input order."""
    p = np.asarray(pvals, float)
    n = len(p)
    order = np.argsort(p)
    ranked = p[order]
    q = ranked * n / (np.arange(1, n + 1))
    q = np.minimum.accumulate(q[::-1])[::-1]
    q = np.clip(q, 0, 1)
    out = np.empty(n)
    out[order] = q
    return out


def welch_t(a, b):
    """Welch's t-test p-value (for the sensitivity control)."""
    t, p = stats.ttest_ind(np.asarray(a, float), np.asarray(b, float),
                           equal_var=False)
    return float(t), float(p)
