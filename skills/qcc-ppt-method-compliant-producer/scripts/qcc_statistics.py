#!/usr/bin/env python3
"""Self-contained statistical tests for QCC effect confirmation.

No scipy dependency: the chi-square upper tail uses the regularized upper
incomplete gamma function and the Welch t-test uses the regularized incomplete
beta function (both implemented with standard series/continued-fraction
expansions).
"""
from __future__ import annotations

import math
from typing import Any


def _gammln(xx: float) -> float:
    cof = (
        76.18009172947146, -86.50532032941677, 24.01409824083091,
        -1.231739572450155, 0.1208650973866179e-2, -0.5395239384953e-5,
    )
    x = xx
    y = xx
    tmp = x + 5.5
    tmp -= (x + 0.5) * math.log(tmp)
    ser = 1.000000000190015
    for index in range(6):
        y += 1.0
        ser += cof[index] / y
    return -tmp + math.log(2.5066282746310005 * ser / x)


def _gser(a: float, x: float) -> float:
    itmax, eps = 200, 3e-12
    ap = a
    total = 1.0 / a
    delta = total
    for _ in range(1, itmax + 1):
        ap += 1.0
        delta *= x / ap
        total += delta
        if abs(delta) < abs(total) * eps:
            break
    return total * math.exp(-x + a * math.log(x) - _gammln(a))


def _gcf(a: float, x: float) -> float:
    itmax, eps, fpmin = 200, 3e-12, 1e-300
    b = x + 1.0 - a
    c = 1.0 / fpmin
    d = 1.0 / b
    h = d
    for index in range(1, itmax + 1):
        an = -index * (index - a)
        b += 2.0
        d = an * d + b
        if abs(d) < fpmin:
            d = fpmin
        c = b + an / c
        if abs(c) < fpmin:
            c = fpmin
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            break
    return math.exp(-x + a * math.log(x) - _gammln(a)) * h


def gammq(a: float, x: float) -> float:
    """Regularized upper incomplete gamma function Q(a, x)."""
    if a <= 0 or x < 0:
        raise ValueError("gammq domain error")
    if x == 0.0:
        return 1.0
    if x < a + 1.0:
        return 1.0 - _gser(a, x)
    return _gcf(a, x)


def _betacf(a: float, b: float, x: float) -> float:
    itmax, eps, fpmin = 200, 3e-12, 1e-300
    qab = a + b
    qap = a + 1.0
    qam = a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < fpmin:
        d = fpmin
    d = 1.0 / d
    h = d
    for m in range(1, itmax + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < fpmin:
            d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin:
            c = fpmin
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < fpmin:
            d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin:
            c = fpmin
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            break
    return h


def betai(a: float, b: float, x: float) -> float:
    """Regularized incomplete beta function I_x(a, b)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    bt = math.exp(
        _gammln(a + b) - _gammln(a) - _gammln(b) + a * math.log(x) + b * math.log(1.0 - x)
    )
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1.0 - x) / b


def chi_square_2x2(a: int, b: int, c: int, d: int, yates: bool = True) -> dict[str, Any]:
    """Two-proportion chi-square test on a 2x2 table."""
    total = a + b + c + d
    denominator = (a + b) * (c + d) * (a + c) * (b + d)
    if denominator == 0:
        raise ValueError("chi-square table has an empty margin")
    if yates:
        statistic = total * (abs(a * d - b * c) - total / 2.0) ** 2 / denominator
    else:
        statistic = total * (a * d - b * c) ** 2 / denominator
    statistic = max(statistic, 0.0)
    return {
        "test": "chi-square",
        "statistic": statistic,
        "df": 1,
        "p": gammq(0.5, statistic / 2.0),
        "yates": yates,
    }


def welch_t(m1: float, s1: float, n1: int, m2: float, s2: float, n2: int) -> dict[str, Any]:
    """Welch's unequal-variance t-test for two independent means."""
    if n1 < 2 or n2 < 2:
        raise ValueError("t-test requires n >= 2 per group")
    se2 = s1 * s1 / n1 + s2 * s2 / n2
    if se2 <= 0:
        raise ValueError("t-test requires non-zero variance")
    statistic = (m1 - m2) / math.sqrt(se2)
    df = se2**2 / ((s1 * s1 / n1) ** 2 / (n1 - 1) + (s2 * s2 / n2) ** 2 / (n2 - 1))
    return {
        "test": "welch-t",
        "statistic": statistic,
        "df": df,
        "p": betai(df / 2.0, 0.5, df / (df + statistic * statistic)),
    }


def evaluate_dataset(data: dict[str, Any]) -> dict[str, Any]:
    """Run the appropriate test for a QCC before/after dataset."""
    before = data.get("before") or {}
    after = data.get("after") or {}
    direction = str(data.get("direction", "lower"))
    metric = str(data.get("metric", "指标"))

    if {"defects", "total"} <= set(before) and {"defects", "total"} <= set(after):
        a, b = int(before["defects"]), int(before["total"]) - int(before["defects"])
        c, d = int(after["defects"]), int(after["total"]) - int(after["defects"])
        if min(a, b, c, d) < 0:
            raise ValueError("defects must be between 0 and total")
        result = chi_square_2x2(a, b, c, d)
        rate_before = 100.0 * a / (a + b)
        rate_after = 100.0 * c / (c + d)
        result.update(
            {
                "metric": metric,
                "direction": direction,
                "before_rate": rate_before,
                "after_rate": rate_after,
                "improved": rate_after < rate_before if direction == "lower" else rate_after > rate_before,
            }
        )
    elif {"mean", "sd", "n"} <= set(before) and {"mean", "sd", "n"} <= set(after):
        result = welch_t(
            float(before["mean"]), float(before["sd"]), int(before["n"]),
            float(after["mean"]), float(after["sd"]), int(after["n"]),
        )
        result.update(
            {
                "metric": metric,
                "direction": direction,
                "before_mean": float(before["mean"]),
                "after_mean": float(after["mean"]),
                "improved": (
                    float(after["mean"]) < float(before["mean"])
                    if direction == "lower"
                    else float(after["mean"]) > float(before["mean"])
                ),
            }
        )
    else:
        raise ValueError(
            "dataset must provide before/after as {defects,total} or {mean,sd,n}"
        )

    result["significant_05"] = float(result["p"]) < 0.05
    result["conclusion"] = "差异显著（p < 0.05）" if result["significant_05"] else "差异不显著（p ≥ 0.05）"
    return result
