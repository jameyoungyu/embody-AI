"""
Mathematical Metrics & Retention Decomposition Engine
======================================================
Implements:
1. 2x2 Paired Contingency Matrix: N_11 (Retained), N_10 (Disrupted), N_01 (Gained), N_00 (Incapable);
2. Key Operational Transition Quantities:
   - D = P(Y_OOD=0 | Y_clean=1) (Paired Disruption Rate)
   - G = P(Y_OOD=1 | Y_clean=0) (Paired Recovery / Gain Rate)
3. Fundamental Retention Decomposition Identity:
   R = (1 - D) + ((1 - p_c) / p_c) * G
4. Paired Episode-Level Bootstrap 95% Confidence Intervals.
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Tuple
import numpy as np


@dataclass
class PairedMetricsSummary:
    checkpoint: str
    perturbation_axis: str
    n_episodes: int
    
    # Primary success rates
    p_clean: float
    p_clean_ci: Tuple[float, float]
    p_ood: float
    p_ood_ci: Tuple[float, float]
    
    # Retention & PDR
    retention_r: float
    retention_r_ci: Tuple[float, float]
    pdr: float
    
    # Operational transition rates
    disruption_d: float
    disruption_d_ci: Tuple[float, float]
    gain_g: float
    gain_g_ci: Tuple[float, float]
    
    # Decomposition components: R = (1 - D) + ((1-p_c)/p_c)*G
    term_1_minus_d: float
    term_odds_gain: float
    decomposition_residual: float  # |R - ((1-D) + ((1-pc)/pc)*G)| (Verification check)
    
    # 2x2 Matrix
    n_11: int
    n_10: int
    n_01: int
    n_00: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def compute_paired_metrics(
    y_clean: np.ndarray,
    y_ood: np.ndarray,
    checkpoint: str,
    perturbation_axis: str,
    n_bootstrap: int = 1000,
    confidence: float = 0.95,
    seed: int = 42
) -> PairedMetricsSummary:
    """
    Compute structured paired metrics with bootstrap confidence intervals and decomposition.
    """
    y_c = np.asarray(y_clean, dtype=int)
    y_o = np.asarray(y_ood, dtype=int)
    n = len(y_c)
    if n == 0 or len(y_o) != n:
        raise ValueError(f"Invalid paired array lengths: clean={len(y_c)}, ood={len(y_o)}")

    # 2x2 counts
    n_11 = int(np.sum((y_c == 1) & (y_o == 1)))
    n_10 = int(np.sum((y_c == 1) & (y_o == 0)))
    n_01 = int(np.sum((y_c == 0) & (y_o == 1)))
    n_00 = int(np.sum((y_c == 0) & (y_o == 0)))

    # Point estimates
    p_c = float(np.mean(y_c))
    p_o = float(np.mean(y_o))
    r_val = p_o / p_c if p_c > 1e-6 else 0.0
    pdr_val = (p_c - p_o) / p_c if p_c > 1e-6 else 0.0
    
    d_val = n_10 / (n_11 + n_10) if (n_11 + n_10) > 0 else 0.0
    g_val = n_01 / (n_00 + n_01) if (n_00 + n_01) > 0 else 0.0

    # Decomposition: R = (1 - D) + ((1 - p_c)/p_c) * G
    term_1_minus_d = 1.0 - d_val
    odds_factor = (1.0 - p_c) / p_c if p_c > 1e-6 else 0.0
    term_odds_gain = odds_factor * g_val
    decomp_reconstructed_r = term_1_minus_d + term_odds_gain
    decomp_residual = abs(r_val - decomp_reconstructed_r)

    # Paired Bootstrap Confidence Intervals
    rng = np.random.RandomState(seed)
    boot_indices = rng.choice(n, size=(n_bootstrap, n), replace=True)
    
    b_y_c = y_c[boot_indices]
    b_y_o = y_o[boot_indices]
    
    b_p_c = np.mean(b_y_c, axis=1)
    b_p_o = np.mean(b_y_o, axis=1)
    
    b_n_11 = np.sum((b_y_c == 1) & (b_y_o == 1), axis=1)
    b_n_10 = np.sum((b_y_c == 1) & (b_y_o == 0), axis=1)
    b_n_01 = np.sum((b_y_c == 0) & (b_y_o == 1), axis=1)
    b_n_00 = np.sum((b_y_c == 0) & (b_y_o == 0), axis=1)
    
    # Safe bootstrap ratios without RuntimeWarning
    b_r = np.divide(b_p_o, b_p_c, out=np.zeros_like(b_p_o, dtype=float), where=b_p_c > 1e-6)
    denom_d = b_n_11 + b_n_10
    b_d = np.divide(b_n_10.astype(float), denom_d.astype(float), out=np.zeros_like(denom_d, dtype=float), where=denom_d > 0)
    denom_g = b_n_00 + b_n_01
    b_g = np.divide(b_n_01.astype(float), denom_g.astype(float), out=np.zeros_like(denom_g, dtype=float), where=denom_g > 0)

    alpha = 1.0 - confidence
    ci_p_c = (float(np.percentile(b_p_c, 100 * (alpha / 2))), float(np.percentile(b_p_c, 100 * (1 - alpha / 2))))
    ci_p_o = (float(np.percentile(b_p_o, 100 * (alpha / 2))), float(np.percentile(b_p_o, 100 * (1 - alpha / 2))))
    ci_r = (float(np.percentile(b_r, 100 * (alpha / 2))), float(np.percentile(b_r, 100 * (1 - alpha / 2))))
    ci_d = (float(np.percentile(b_d, 100 * (alpha / 2))), float(np.percentile(b_d, 100 * (1 - alpha / 2))))
    ci_g = (float(np.percentile(b_g, 100 * (alpha / 2))), float(np.percentile(b_g, 100 * (1 - alpha / 2))))

    return PairedMetricsSummary(
        checkpoint=checkpoint,
        perturbation_axis=perturbation_axis,
        n_episodes=n,
        p_clean=p_c,
        p_clean_ci=ci_p_c,
        p_ood=p_o,
        p_ood_ci=ci_p_o,
        retention_r=r_val,
        retention_r_ci=ci_r,
        pdr=pdr_val,
        disruption_d=d_val,
        disruption_d_ci=ci_d,
        gain_g=g_val,
        gain_g_ci=ci_g,
        term_1_minus_d=term_1_minus_d,
        term_odds_gain=term_odds_gain,
        decomposition_residual=decomp_residual,
        n_11=n_11,
        n_10=n_10,
        n_01=n_01,
        n_00=n_00
    )
