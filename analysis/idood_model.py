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


# ---------------------------------------------------------------------------
# Hierarchical form: one clean observation per checkpoint, many perturbed ones
# ---------------------------------------------------------------------------
#
# The flat `Cell` above carries its own clean counts, which is correct only when
# a fit contains one perturbation condition. Pool several conditions out of
# `Cell`s and the same clean episodes enter the likelihood once per condition,
# shrinking the latent clean rate far below what the data support and inflating
# significance. Real pilots want the pooled fit -- sharing theta across
# conditions is what makes it precise -- so the pooled form has to be built
# properly rather than assembled from `Cell`s.
#
# Each condition j (a perturbation axis at one severity) gets its own intercept
# alpha_j, since camera shift and lighting have no reason to share one. gamma
# may be shared across conditions or estimated per condition; whether the
# capability-robustness coupling is perturbation-specific is itself a question
# worth asking of the data.


@dataclass
class OODObs:
    """Perturbed outcome of one checkpoint under one condition."""

    k: int
    n: int
    condition: int


@dataclass
class Checkpoint:
    """One policy checkpoint: a single clean observation, many perturbed ones."""

    k_clean: int
    n_clean: int
    ood: list[OODObs]


@dataclass
class HierFit:
    alpha: np.ndarray        # one intercept per condition
    gamma: np.ndarray        # one exponent per condition (identical when shared)
    theta: np.ndarray        # latent clean rate per checkpoint
    loglik: float
    n_conditions: int
    shared_gamma: bool
    converged: bool

    def predict(self, p_clean, condition: int) -> np.ndarray:
        """Perturbed rate this fit predicts for a given clean rate."""
        p = np.clip(np.asarray(p_clean, dtype=float), EPS, 1.0)
        return np.clip(np.exp(self.alpha[condition] + self.gamma[condition] * np.log(p)),
                       EPS, 1 - EPS)


def _hier_theta(alpha, gamma, cps, iters=64):
    """Latent clean rate per checkpoint, maximised for fixed (alpha, gamma).

    Same vectorised bisection as the flat case; the score now sums the pull
    from every perturbed observation attached to the checkpoint, while the
    clean observation contributes exactly once.
    """
    k_c = np.array([c.k_clean for c in cps], dtype=float)
    n_c = np.array([c.n_clean for c in cps], dtype=float)
    lo = np.full(len(cps), 1e-6)
    hi = np.full(len(cps), 1 - 1e-6)

    def score(th):
        s = k_c / th - (n_c - k_c) / (1.0 - th)
        for i, cp in enumerate(cps):
            for o in cp.ood:
                g = gamma[o.condition]
                p = min(max(np.exp(alpha[o.condition] + g * np.log(th[i])), EPS), 1 - EPS)
                s[i] += g * o.k / th[i] - g * p * (o.n - o.k) / (th[i] * (1.0 - p))
        return s

    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        right = score(mid) > 0
        lo = np.where(right, mid, lo)
        hi = np.where(right, hi, mid)
    return 0.5 * (lo + hi)


def _hier_loglik(alpha, gamma, cps):
    th = np.clip(_hier_theta(alpha, gamma, cps), EPS, 1 - EPS)
    ll = 0.0
    for i, cp in enumerate(cps):
        ll += cp.k_clean * np.log(th[i]) + (cp.n_clean - cp.k_clean) * np.log1p(-th[i])
        for o in cp.ood:
            p = float(np.clip(np.exp(alpha[o.condition] + gamma[o.condition] * np.log(th[i])),
                              EPS, 1 - EPS))
            ll += o.k * np.log(p) + (o.n - o.k) * np.log1p(-p)
    return ll, th


def fit_hier(cps: list[Checkpoint], n_conditions: int, shared_gamma: bool = True,
             fixed_gamma: float | None = None) -> HierFit:
    """Profile MLE with one clean observation per checkpoint.

    shared_gamma=True estimates a single exponent across conditions;
    False gives each condition its own. fixed_gamma pins every exponent, which
    is the null used by `lrt_hier`.
    """
    p_c = np.array([(c.k_clean + 0.5) / (c.n_clean + 1.0) for c in cps])
    a0 = np.zeros(n_conditions)
    for j in range(n_conditions):
        vals = [(np.log((o.k + 0.5) / (o.n + 1.0)) - np.log(p_c[i]))
                for i, c in enumerate(cps) for o in c.ood if o.condition == j]
        a0[j] = float(np.mean(vals)) if vals else -0.6

    if fixed_gamma is not None:
        gam = np.full(n_conditions, float(fixed_gamma))
        obj = lambda x: -_hier_loglik(x, gam, cps)[0]
        res = optimize.minimize(obj, a0, method="L-BFGS-B",
                                options={"maxiter": 8000, "ftol": 1e-12})
        alpha, gamma = res.x, gam
    elif shared_gamma:
        obj = lambda x: -_hier_loglik(x[:-1], np.full(n_conditions, x[-1]), cps)[0]
        res = optimize.minimize(obj, np.append(a0, 1.0), method="L-BFGS-B",
                                options={"maxiter": 8000, "ftol": 1e-12})
        alpha, gamma = res.x[:-1], np.full(n_conditions, res.x[-1])
    else:
        obj = lambda x: -_hier_loglik(x[:n_conditions], x[n_conditions:], cps)[0]
        res = optimize.minimize(obj, np.concatenate([a0, np.ones(n_conditions)]),
                                method="L-BFGS-B", options={"maxiter": 12000, "ftol": 1e-12})
        alpha, gamma = res.x[:n_conditions], res.x[n_conditions:]

    ll, th = _hier_loglik(alpha, gamma, cps)
    return HierFit(alpha, gamma, th, ll, n_conditions, shared_gamma, bool(res.success))


def lrt_hier(cps: list[Checkpoint], n_conditions: int, shared_gamma: bool = True) -> dict:
    """Test H0: every exponent equals 1, i.e. drop is proportional to clean rate.

    Rejecting it says relative drop cannot be compared across policies of
    different capability without first accounting for the curve.
    """
    free = fit_hier(cps, n_conditions, shared_gamma=shared_gamma)
    null = fit_hier(cps, n_conditions, fixed_gamma=1.0)
    df = 1 if shared_gamma else n_conditions
    stat = max(0.0, 2.0 * (free.loglik - null.loglik))
    return {
        "gamma_hat": free.gamma.copy(),
        "alpha_hat": free.alpha.copy(),
        "lr_stat": stat,
        "df": df,
        "p_value": float(stats.chi2.sf(stat, df=df)),
        "converged": free.converged and null.converged,
        "fit": free,
    }


def effective_robustness_vs_reference(reference: HierFit, held_out: list[Checkpoint]) -> list[dict]:
    """Residual of held-out policies above a curve fitted on a reference population.

    Fitting the curve on the same policies you are judging lets a genuinely
    robust method drag the curve up and erase its own residual. Following
    Taori et al., the curve is fitted on standard policies only, and robustness
    interventions are scored against it as held-out points.
    """
    out = []
    for cp in held_out:
        p_clean = (cp.k_clean + 0.5) / (cp.n_clean + 1.0)
        for o in cp.ood:
            observed = (o.k + 0.5) / (o.n + 1.0)
            predicted = float(reference.predict(p_clean, o.condition))
            out.append({
                "condition": o.condition,
                "p_clean": p_clean,
                "p_ood": observed,
                "predicted": predicted,
                "effective_robustness": observed - predicted,
                "pdr": (p_clean - observed) / max(p_clean, EPS),
            })
    return out


def paired_bootstrap_gamma(cps: list[Checkpoint], n_conditions: int, n_boot: int = 400,
                           seed: int = 0, shared_gamma: bool = True) -> dict:
    """Checkpoint-level bootstrap CI for gamma.

    The likelihood treats clean and perturbed outcomes as independent even
    though they share initial-state seeds. That is not automatically
    conservative, so the interval reported alongside the LRT is resampled over
    checkpoints rather than assumed.
    """
    rng = np.random.default_rng(seed)
    idx = np.arange(len(cps))
    draws = []
    for _ in range(n_boot):
        pick = rng.choice(idx, size=len(cps), replace=True)
        try:
            f = fit_hier([cps[i] for i in pick], n_conditions, shared_gamma=shared_gamma)
            draws.append(f.gamma.copy())
        except Exception:
            continue
    if not draws:
        return {"lo": None, "hi": None, "n_boot": 0}
    d = np.array(draws)
    return {"lo": np.percentile(d, 2.5, axis=0), "hi": np.percentile(d, 97.5, axis=0),
            "n_boot": len(draws)}
