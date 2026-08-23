"""Power and calibration study for the C1 pilot design.

Answers the question the pilot budget turns on: with M checkpoints spread over
a given clean-success-rate range and N episodes per cell, how often does the
likelihood-ratio test correctly reject proportionality (gamma == 1)?

The LBM evaluation study reports that 50 rollouts leave a 20-30 point
confidence interval on a single success rate, which is why per-cell precision
is the wrong thing to budget for. The regression pools every checkpoint, so
what matters is total episodes and the spread of clean rates. This script
quantifies that trade-off instead of asserting it.
"""

from __future__ import annotations

import argparse
import numpy as np

import idood_model as M


def simulate(rng, m, n, gamma, alpha, lo, hi):
    theta = np.linspace(lo, hi, m)
    cells = []
    for t in theta:
        p_ood = float(np.clip(np.exp(alpha + gamma * np.log(t)), 1e-6, 1 - 1e-6))
        cells.append(M.Cell(int(rng.binomial(n, t)), n, int(rng.binomial(n, p_ood)), n))
    return cells


def rejection_rate(reps, m, n, gamma, alpha, lo, hi, seed):
    rng = np.random.default_rng(seed)
    rejects = 0
    gammas = []
    for _ in range(reps):
        cells = simulate(rng, m, n, gamma, alpha, lo, hi)
        out = M.lrt_proportional(cells)
        if not out["converged"]:
            continue
        gammas.append(out["gamma_hat"])
        if out["p_value"] < 0.05:
            rejects += 1
    return rejects / reps, float(np.mean(gammas)), float(np.std(gammas))


def pdr_bias_demo(alpha, gamma, lo, hi):
    """PDR of policies that lie exactly on the fitted curve.

    Every policy here has zero effective robustness by construction: none is
    more robust than its clean success rate predicts. Any spread in PDR is
    therefore pure capability confound.
    """
    p = np.linspace(lo, hi, 7)
    pdr = 1.0 - np.exp(alpha) * p ** (gamma - 1.0)
    return p, pdr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=400)
    ap.add_argument("--seed", type=int, default=20260823)
    args = ap.parse_args()

    alpha = float(np.log(0.55))
    print("=" * 78)
    print("Calibration and power of the LRT for H0: gamma == 1")
    print(f"alpha = log(0.55); {args.reps} replicates per configuration; nominal level 0.05")
    print("=" * 78)

    spreads = {"wide (clean SR 0.20-0.90)": (0.20, 0.90),
               "narrow (clean SR 0.45-0.75)": (0.45, 0.75)}
    header = f"{'gamma':>6} {'M':>4} {'N/cell':>7} {'episodes':>9} {'reject':>8} {'gamma_hat':>18}"
    for label, (lo, hi) in spreads.items():
        print(f"\n--- checkpoint spread: {label} ---")
        print(header)
        for gamma in (1.0, 1.25, 1.5, 2.0):
            for m, n in ((12, 50), (12, 150), (20, 150)):
                rate, gm, gs = rejection_rate(
                    args.reps, m, n, gamma, alpha, lo, hi, args.seed + int(gamma * 100) + m + n
                )
                tag = "  <- type I" if gamma == 1.0 else ""
                print(f"{gamma:>6.2f} {m:>4} {n:>7} {2*m*n:>9} {rate:>7.1%} "
                      f"{gm:>10.3f} +/-{gs:<5.3f}{tag}")

    print("\n" + "=" * 78)
    print("Capability confound in PDR, for policies exactly on the curve")
    print("=" * 78)
    for gamma in (0.75, 1.0, 1.5, 2.0):
        p, d = pdr_bias_demo(alpha, gamma, 0.30, 0.90)
        span = (d.max() - d.min()) * 100
        print(f"gamma={gamma:>4.2f}  PDR at clean SR 0.30 -> 0.90: "
              f"{d[0]:.3f} -> {d[-1]:.3f}   spread = {span:5.1f} points")


if __name__ == "__main__":
    main()
