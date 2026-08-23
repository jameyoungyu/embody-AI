import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))
from idood_model import Cell, fit, lrt_proportional, effective_robustness, pdr
import scipy.stats as stats
import numpy as np

# ==========================================
# Source 1: LIBERO-Plus Table 1 (arXiv:2510.13626 v1, Page 3)
# ==========================================
models_lp = [
    "OpenVLA", "OpenVLA-OFT", "OpenVLA-OFT_w", "OpenVLA-OFT_m",
    "pi0", "pi0-fast", "Nora", "WorldVLA", "UniVLA", "RIPT-VLA"
]

clean_sr_lp = [0.765, 0.971, 0.953, 0.976, 0.942, 0.855, 0.879, 0.791, 0.952, 0.975]

axes_lp = {
    "Camera":     [0.011, 0.597, 0.168, 0.579, 0.158, 0.664, 0.040, 0.003, 0.043, 0.583],
    "Robot":      [0.041, 0.372, 0.437, 0.306, 0.066, 0.248, 0.411, 0.302, 0.503, 0.367],
    "Language":   [0.268, 0.815, 0.732, 0.836, 0.610, 0.633, 0.670, 0.442, 0.718, 0.801],
    "Light":      [0.044, 0.858, 0.682, 0.916, 0.796, 0.730, 0.310, 0.294, 0.591, 0.879],
    "Background": [0.253, 0.924, 0.925, 0.836, 0.785, 0.677, 0.505, 0.145, 0.800, 0.904],
    "Noise":      [0.193, 0.767, 0.514, 0.763, 0.794, 0.758, 0.176, 0.122, 0.253, 0.738],
    "Layout":     [0.316, 0.771, 0.723, 0.732, 0.704, 0.703, 0.639, 0.394, 0.343, 0.765]
}

n_ep = 500  # Protocol-inferred: 50 trials x 10 tasks standard suite

print("==========================================================================================")
print("Source 1: LIBERO-Plus (arXiv:2510.13626 v1, Table 1, Page 3)")
print(f"Total models M={len(models_lp)}, Cells per axis={len(models_lp)}, n_ep={n_ep} (protocol-inferred)")
print("==========================================================================================")
print(f"{'Axis':<12} | {'M':<3} | {'gamma_hat':<9} | {'alpha_hat':<9} | {'LR stat':<8} | {'LRT p':<11} | {'Spearman(PDR, -Res)':<20} | {'Floor?'}")
print("-" * 105)

for axis_name, ood_sr in axes_lp.items():
    cells = []
    near_floor = any(s < 0.02 for s in ood_sr)
    for i in range(len(models_lp)):
        k_c = int(round(clean_sr_lp[i] * n_ep))
        k_o = int(round(ood_sr[i] * n_ep))
        k_c = max(1, min(n_ep - 1, k_c))
        k_o = max(1, min(n_ep - 1, k_o))
        cells.append(Cell(k_clean=k_c, n_clean=n_ep, k_ood=k_o, n_ood=n_ep))
    
    lrt_res = lrt_proportional(cells)
    fit_full = fit(cells, fixed_gamma=None)
    resids = effective_robustness(cells, fit_full)
    pdrs = pdr(cells)
    
    # Spearman rank correlation between PDR ranking and Effective Robustness (-residual) ranking
    corr, _ = stats.spearmanr(pdrs, -resids)
    
    print(f"{axis_name:<12} | {len(cells):<3} | {lrt_res['gamma_hat']:<9.3f} | {lrt_res['alpha_hat']:<9.3f} | {lrt_res['lr_stat']:<8.2f} | {lrt_res['p_value']:<11.4e} | {corr:<20.3f} | {str(near_floor)}")

# ==========================================
# Source 2: EBench (arXiv:2606.18239 v1, Table 2 / Table 3, Page 6)
# ==========================================
print("\n==========================================================================================")
print("Source 2: EBench (arXiv:2606.18239 v1, Table 2, Page 6)")
print("==========================================================================================")
# Models: pi0, pi0.5, XVLA, InternVLA-A1
models_eb = ["pi0", "pi0.5", "XVLA", "InternVLA-A1"]
clean_sr_eb = [0.305, 0.321, 0.283, 0.331] # Val-Train SR (%)
test_sr_eb = [0.244, 0.295, 0.247, 0.276]  # Test SR (%)
n_eb = 300 # 3 seeds x 100 trials

cells_eb = []
for i in range(len(models_eb)):
    k_c = int(round(clean_sr_eb[i] * n_eb))
    k_o = int(round(test_sr_eb[i] * n_eb))
    cells_eb.append(Cell(k_clean=k_c, n_clean=n_eb, k_ood=k_o, n_ood=n_eb))

lrt_eb = lrt_proportional(cells_eb)
fit_eb = fit(cells_eb, fixed_gamma=None)
resids_eb = effective_robustness(cells_eb, fit_eb)
pdrs_eb = pdr(cells_eb)
corr_eb, _ = stats.spearmanr(pdrs_eb, -resids_eb)

print(f"{'Split/Axis':<12} | {'M':<3} | {'gamma_hat':<9} | {'alpha_hat':<9} | {'LR stat':<8} | {'LRT p':<11} | {'Spearman(PDR, -Res)':<20} | {'Floor?'}")
print("-" * 105)
print(f"{'EBench-Test':<12} | {len(cells_eb):<3} | {lrt_eb['gamma_hat']:<9.3f} | {lrt_eb['alpha_hat']:<9.3f} | {lrt_eb['lr_stat']:<8.2f} | {lrt_eb['p_value']:<11.4e} | {corr_eb:<20.3f} | False")
