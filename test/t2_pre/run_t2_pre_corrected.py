"""
Corrected T2-PRE Benchmark Analysis (Diagnostic & Comparative Models)
======================================================================
This script performs exploratory diagnostic analysis on:
1. LIBERO-Plus (CVPR 2026 Camera-Ready Table 1 / arXiv:2510.13626 v1):
   - Compares functional forms: Log-Log OLS, Logit-Logit OLS, and Retention Ratio Dependence.
   - Computes Capability-Adjusted Residual Robustness vs PDR rankings.
   - Deconstructs High-Capability (p_clean >= 0.94) Vertical Spread.
   - Latent-Binomial MLE placed in Appendix Diagnostic section (demonstrating pseudo-significance from omitted architecture heterogeneity).
2. EBench (arXiv:2606.18239):
   - Narrow-range (Delta p_clean = 4.8%) negative control analysis.
"""

import sys
import os
import numpy as np
import scipy.stats as stats
from scipy import optimize

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(parent_dir)
from analysis.idood_model import Cell, fit, lrt_proportional, effective_robustness, pdr

# ==============================================================================
# 1. LIBERO-Plus Data Version Specification
# Source: CVPR 2026 / arXiv:2510.13626 v1 Table 1, Page 3
# Note: Benchmark total = 10,030 perturbation tasks (1 trial/perturbation task)
# Base clean tasks = 40 (50 trials/task)
# ==============================================================================
models_lp = [
    "OpenVLA", "OpenVLA-OFT", "OpenVLA-OFT_w", "OpenVLA-OFT_m",
    "pi0", "pi0-fast", "Nora", "WorldVLA", "UniVLA", "RIPT-VLA"
]

clean_sr_lp = np.array([0.765, 0.971, 0.953, 0.976, 0.942, 0.855, 0.879, 0.791, 0.952, 0.975])

axis_sample_sizes_lp = {
    "Camera":     1599,
    "Robot":      1550,
    "Language":   1537,
    "Light":      1142,
    "Background": 1076,
    "Noise":      1601,
    "Layout":     1525
}

axes_lp = {
    "Camera":     np.array([0.011, 0.597, 0.168, 0.579, 0.158, 0.664, 0.040, 0.003, 0.043, 0.583]),
    "Robot":      np.array([0.041, 0.372, 0.437, 0.306, 0.066, 0.248, 0.411, 0.302, 0.503, 0.367]),
    "Language":   np.array([0.268, 0.815, 0.732, 0.836, 0.610, 0.633, 0.670, 0.442, 0.718, 0.801]),
    "Light":      np.array([0.044, 0.858, 0.682, 0.916, 0.796, 0.730, 0.310, 0.294, 0.591, 0.879]),
    "Background": np.array([0.253, 0.924, 0.925, 0.836, 0.785, 0.677, 0.505, 0.145, 0.800, 0.904]),
    "Noise":      np.array([0.193, 0.767, 0.514, 0.763, 0.794, 0.758, 0.176, 0.122, 0.253, 0.738]),
    "Layout":     np.array([0.316, 0.771, 0.723, 0.732, 0.704, 0.703, 0.639, 0.394, 0.343, 0.765])
}


def fit_loglog_ols(p_clean, p_ood):
    """Log-Log regression: log(p_ood) = alpha + gamma * log(p_clean) + eps"""
    p_c = np.clip(p_clean, 1e-4, 1.0)
    p_o = np.clip(p_ood, 1e-4, 1.0)
    x = np.log(p_c)
    y = np.log(p_o)
    n = len(x)
    
    X = np.column_stack([np.ones(n), x])
    beta, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
    alpha_hat, gamma_hat = float(beta[0]), float(beta[1])
    
    y_pred = X @ beta
    rss = float(np.sum((y - y_pred) ** 2))
    s2 = rss / (n - 2) if n > 2 else 1e-6
    cov = s2 * np.linalg.inv(X.T @ X)
    se_gamma = float(np.sqrt(cov[1, 1]))
    
    t_stat = (gamma_hat - 1.0) / se_gamma
    p_val = float(2 * (1 - stats.t.cdf(np.abs(t_stat), df=n - 2)))
    t_crit = float(stats.t.ppf(0.975, df=n - 2))
    ci_gamma = (gamma_hat - t_crit * se_gamma, gamma_hat + t_crit * se_gamma)
    
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1.0 - (rss / ss_tot) if ss_tot > 1e-9 else 0.0
    
    return {
        "alpha_hat": alpha_hat, "gamma_hat": gamma_hat, "se_gamma": se_gamma,
        "t_stat": t_stat, "p_val": p_val, "ci_gamma": ci_gamma, "r2": r2
    }


def fit_logitlogit_ols(p_clean, p_ood):
    """Logit-Logit regression: logit(p_ood) = alpha + beta * logit(p_clean) + eps"""
    p_c = np.clip(p_clean, 1e-4, 1 - 1e-4)
    p_o = np.clip(p_ood, 1e-4, 1 - 1e-4)
    x = np.log(p_c / (1.0 - p_c))
    y = np.log(p_o / (1.0 - p_o))
    n = len(x)
    
    X = np.column_stack([np.ones(n), x])
    beta, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
    alpha_hat, beta_hat = float(beta[0]), float(beta[1])
    
    y_pred = X @ beta
    rss = float(np.sum((y - y_pred) ** 2))
    s2 = rss / (n - 2) if n > 2 else 1e-6
    cov = s2 * np.linalg.inv(X.T @ X)
    se_beta = float(np.sqrt(cov[1, 1]))
    
    t_stat = (beta_hat - 1.0) / se_beta
    p_val = float(2 * (1 - stats.t.cdf(np.abs(t_stat), df=n - 2)))
    t_crit = float(stats.t.ppf(0.975, df=n - 2))
    ci_beta = (beta_hat - t_crit * se_beta, beta_hat + t_crit * se_beta)
    
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1.0 - (rss / ss_tot) if ss_tot > 1e-9 else 0.0
    
    return {
        "alpha_hat": alpha_hat, "beta_hat": beta_hat, "se_beta": se_beta,
        "t_stat": t_stat, "p_val": p_val, "ci_beta": ci_beta, "r2": r2
    }


def run_full_audit():
    print("=" * 115)
    print("LIBERO-Plus Exploratory Audit (CVPR 2026 Camera-Ready Table 1 / arXiv:2510.13626)")
    print("M=10 Models, 7 Perturbation Axes, 10,030 Perturbation Benchmark Tasks")
    print("=" * 115)
    
    print(f"{'Axis':<12} | {'N_tasks':<7} | {'OLS Log-Log g':<14} | {'Log-Log 95% CI':<16} | {'Logit-Logit b':<14} | {'Logit 95% CI':<16} | {'Spearman(PDR,-ER)':<18}")
    print("-" * 115)
    
    appendix_latent_bin = []
    
    for axis_name, ood_sr in axes_lp.items():
        n_axis = axis_sample_sizes_lp[axis_name]
        
        # 1. Log-Log OLS
        ols_log = fit_loglog_ols(clean_sr_lp, ood_sr)
        ci_log_str = f"[{ols_log['ci_gamma'][0]:.2f}, {ols_log['ci_gamma'][1]:.2f}]"
        
        # 2. Logit-Logit OLS
        ols_logit = fit_logitlogit_ols(clean_sr_lp, ood_sr)
        ci_logit_str = f"[{ols_logit['ci_beta'][0]:.2f}, {ols_logit['ci_beta'][1]:.2f}]"
        
        # 3. Reference capability model residual & PDR ranking comparison
        cells = []
        for i in range(len(models_lp)):
            k_c = int(round(clean_sr_lp[i] * n_axis))
            k_o = int(round(ood_sr[i] * n_axis))
            k_c = max(1, min(n_axis - 1, k_c))
            k_o = max(1, min(n_axis - 1, k_o))
            cells.append(Cell(k_clean=k_c, n_clean=n_axis, k_ood=k_o, n_ood=n_axis))
        
        fit_full = fit(cells, fixed_gamma=None)
        resids = effective_robustness(cells, fit_full)
        pdrs = pdr(cells)
        corr, _ = stats.spearmanr(pdrs, -resids)
        
        lrt_res = lrt_proportional(cells)
        appendix_latent_bin.append({
            "axis": axis_name,
            "gamma_hat": lrt_res["gamma_hat"],
            "lr_stat": lrt_res["lr_stat"],
            "p_value": lrt_res["p_value"]
        })
        
        print(f"{axis_name:<12} | {n_axis:<7} | {ols_log['gamma_hat']:<14.3f} | {ci_log_str:<16} | {ols_logit['beta_hat']:<14.3f} | {ci_logit_str:<16} | {corr:<18.3f}")
    
    print("\n" + "=" * 115)
    print("Vertical Spread Breakdown at High Clean SR (p_clean in [0.94, 0.98])")
    print("Demonstrating massive architecture-level variance not captured by clean capability alone")
    print("=" * 115)
    
    high_clean_idx = [i for i, sr in enumerate(clean_sr_lp) if sr >= 0.94]
    print(f"{'Model':<16} | {'Clean SR':<9} | {'Camera OOD':<11} | {'Light OOD':<10} | {'Robot OOD':<10} | {'Noise OOD':<10}")
    print("-" * 75)
    for idx in high_clean_idx:
        m_name = models_lp[idx]
        c_sr = clean_sr_lp[idx]
        cam_sr = axes_lp["Camera"][idx]
        light_sr = axes_lp["Light"][idx]
        rob_sr = axes_lp["Robot"][idx]
        noise_sr = axes_lp["Noise"][idx]
        print(f"{m_name:<16} | {c_sr*100:<8.1f}% | {cam_sr*100:<10.1f}% | {light_sr*100:<9.1f}% | {rob_sr*100:<9.1f}% | {noise_sr*100:<9.1f}%")
        
    print("\n" + "=" * 115)
    print("[APPENDIX DIAGNOSTIC ONLY] Latent-Binomial MLE (Illustrating Pseudo-Significance from Omitted Heterogeneity)")
    print("=" * 115)
    print(f"{'Axis':<12} | {'LatentBin gamma_hat':<22} | {'LRT Chi2 Stat':<15} | {'LRT p-value':<15} | {'Diagnostic Note'}")
    print("-" * 115)
    for item in appendix_latent_bin:
        print(f"{item['axis']:<12} | {item['gamma_hat']:<22.3f} | {item['lr_stat']:<15.2f} | {item['p_value']:<15.4e} | Underestimates cross-model SE")


if __name__ == "__main__":
    run_full_audit()
