"""ID->OOD success-rate model for closed-loop policy robustness.

Central question of candidate C1: the Performance Drop Rate used across the VLA
robustness literature,

    PDR = (p_clean - p_ood) / p_clean,

is only a well-defined comparison between policies if the perturbed success
rate is *proportional* to the clean success rate, i.e.

    p_ood = c * p_clean                                          (H0)

We embed that null in a power-law family,

    p_ood = exp(alpha) * p_clean ** gamma                        (H1)

so gamma == 1 recovers proportionality exactly. gamma is the quantity the
pilot estimates; rejecting gamma == 1 falsifies the assumption PDR rests on.

Both success rates are measured by running a finite number of episodes, so the
regressor is noisy. Regressing observed rate on observed rate attenuates the
slope toward zero and would manufacture the very effect we are testing for.
The clean rate of each checkpoint is therefore a latent parameter with its own
binomial likelihood, and alpha, gamma and the latent rates are fit jointly.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import optimize, stats

EPS = 1e-9


def _sigmoid(u: np.ndarray) -> np.ndarray:
    return 0.5 * (1.0 + np.tanh(0.5 * u))


def _logit(p: np.ndarray) -> np.ndarray:
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def _ood_rate(theta: np.ndarray, alpha: float, gamma: float) -> np.ndarray:
    """Perturbed success rate implied by the power-law family."""
    return np.clip(np.exp(alpha + gamma * np.log(np.clip(theta, EPS, 1.0))), EPS, 1 - EPS)


@dataclass
class Cell:
    """One (checkpoint, perturbation condition) observation.

    n_clean/n_ood are episode counts, k_clean/k_ood the successes. Clean and
    perturbed episodes should start from the same initial-state seeds; the
    likelihood below ignores that pairing, which makes every result here
    conservative relative to a paired analysis.
    """

    k_clean: int
    n_clean: int
    k_ood: int
    n_ood: int


def _profile_theta(alpha, gamma, k_c, n_c, k_o, n_o, iters=64):
    """Latent clean rate of every checkpoint, maximised for fixed (alpha, gamma).

    Profiling the latent rates out analytically leaves a two-parameter outer
    problem, which is what makes the power study below cheap enough to run.
    The score is monotone-crossing on (0, 1) -- it diverges to +inf at 0 and
    -inf at 1 -- so a vectorised bisection finds the maximiser without needing
    derivatives of the outer objective.
    """
    lo = np.full_like(k_c, 1e-6, dtype=float)
    hi = np.full_like(k_c, 1 - 1e-6, dtype=float)

    def score(th):
        p = np.clip(np.exp(alpha + gamma * np.log(th)), EPS, 1 - EPS)
        return (
            k_c / th
            - (n_c - k_c) / (1.0 - th)
            + gamma * k_o / th
            - gamma * p * (n_o - k_o) / (th * (1.0 - p))
        )

    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        go_right = score(mid) > 0
        lo = np.where(go_right, mid, lo)
        hi = np.where(go_right, hi, mid)
    return 0.5 * (lo + hi)


def _loglik_at(alpha, gamma, k_c, n_c, k_o, n_o):
    th = _profile_theta(alpha, gamma, k_c, n_c, k_o, n_o)
    p = np.clip(np.exp(alpha + gamma * np.log(th)), EPS, 1 - EPS)
    th = np.clip(th, EPS, 1 - EPS)
    return float(np.sum(
        k_c * np.log(th) + (n_c - k_c) * np.log1p(-th)
        + k_o * np.log(p) + (n_o - k_o) * np.log1p(-p)
    )), th


def _arrays(cells):
    return (
        np.array([c.k_clean for c in cells], dtype=float),
        np.array([c.n_clean for c in cells], dtype=float),
        np.array([c.k_ood for c in cells], dtype=float),
        np.array([c.n_ood for c in cells], dtype=float),
    )


@dataclass
class Fit:
    alpha: float
    gamma: float
    theta: np.ndarray
    loglik: float
    converged: bool


def fit(cells: list[Cell], fixed_gamma: float | None = None) -> Fit:
    """Profile MLE over (alpha, gamma), latent clean rates solved in closed form."""
    k_c, n_c, k_o, n_o = _arrays(cells)
    p_c0 = (k_c + 0.5) / (n_c + 1.0)
    p_o0 = (k_o + 0.5) / (n_o + 1.0)
    g0 = 1.0 if fixed_gamma is None else fixed_gamma
    a0 = float(np.mean(np.log(p_o0) - g0 * np.log(p_c0)))

    if fixed_gamma is None:
        obj = lambda x: -_loglik_at(x[0], x[1], k_c, n_c, k_o, n_o)[0]
        res = optimize.minimize(obj, np.array([a0, g0]), method="Nelder-Mead",
                                options={"xatol": 1e-7, "fatol": 1e-9, "maxiter": 4000})
        alpha, gamma = float(res.x[0]), float(res.x[1])
    else:
        obj = lambda a: -_loglik_at(a[0], fixed_gamma, k_c, n_c, k_o, n_o)[0]
        res = optimize.minimize(obj, np.array([a0]), method="Nelder-Mead",
                                options={"xatol": 1e-7, "fatol": 1e-9, "maxiter": 4000})
        alpha, gamma = float(res.x[0]), float(fixed_gamma)

    ll, theta = _loglik_at(alpha, gamma, k_c, n_c, k_o, n_o)
    return Fit(alpha, gamma, theta, ll, bool(res.success))


def lrt_proportional(cells: list[Cell]) -> dict:
    """Likelihood-ratio test of H0: gamma == 1 (PDR's implicit model).

    Returns the free and constrained fits, the LR statistic and its p-value
    against a chi-square with one degree of freedom.
    """
    free = fit(cells, fixed_gamma=None)
    null = fit(cells, fixed_gamma=1.0)
    stat = max(0.0, 2.0 * (free.loglik - null.loglik))
    return {
        "gamma_hat": free.gamma,
        "alpha_hat": free.alpha,
        "lr_stat": stat,
        "p_value": float(stats.chi2.sf(stat, df=1)),
        "converged": free.converged and null.converged,
    }


def effective_robustness(cells: list[Cell], reference: Fit) -> np.ndarray:
    """Residual of each cell above the fitted ID->OOD curve, in probability units.

    This is the robotics analogue of effective robustness in image
    classification: how much better a policy does under perturbation than its
    clean success rate alone predicts. Zero means the policy is exactly on the
    curve every other policy sits on.
    """
    theta_hat = np.array([(c.k_clean + 0.5) / (c.n_clean + 1.0) for c in cells])
    predicted = _ood_rate(theta_hat, reference.alpha, reference.gamma)
    observed = np.array([(c.k_ood + 0.5) / (c.n_ood + 1.0) for c in cells])
    return observed - predicted


def pdr(cells: list[Cell]) -> np.ndarray:
    """Performance Drop Rate as used in the VLA robustness literature."""
    p_c = np.array([(c.k_clean + 0.5) / (c.n_clean + 1.0) for c in cells])
    p_o = np.array([(c.k_ood + 0.5) / (c.n_ood + 1.0) for c in cells])
    return (p_c - p_o) / np.clip(p_c, EPS, None)
