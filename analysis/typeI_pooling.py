"""Type I error of the two ways of pooling several perturbation conditions.

Under the null (gamma == 1) a correct test rejects 5% of the time. Assembling
flat Cells re-enters each checkpoint's clean episodes once per condition, so
the latent clean rate looks far better determined than the data allow.
"""
import numpy as np, idood_model as M

REPS, M_CP, N, J = 200, 12, 150, 3
ALPHA = np.array([np.log(0.55), np.log(0.35), np.log(0.75)])
theta = np.linspace(0.25, 0.90, M_CP)
rng = np.random.default_rng(20260823)
flat_rej = hier_rej = 0
for _ in range(REPS):
    kc = rng.binomial(N, theta)
    ko = np.array([[rng.binomial(N, float(np.clip(np.exp(ALPHA[j] + np.log(t)), 1e-9, 1-1e-9)))
                    for j in range(J)] for t in theta])
    cells = [M.Cell(int(kc[i]), N, int(ko[i, j]), N) for i in range(M_CP) for j in range(J)]
    if M.lrt_proportional(cells)["p_value"] < 0.05:
        flat_rej += 1
    cps = [M.Checkpoint(int(kc[i]), N, [M.OODObs(int(ko[i, j]), N, j) for j in range(J)])
           for i in range(M_CP)]
    if M.lrt_hier(cps, J, shared_gamma=True)["p_value"] < 0.05:
        hier_rej += 1
print(f"replicates={REPS}  conditions={J}  checkpoints={M_CP}  N/cell={N}  nominal level 5%")
print(f"  flat Cells pooled (clean counted {J}x): type I = {flat_rej/REPS:.1%}")
print(f"  hierarchical (clean counted once)     : type I = {hier_rej/REPS:.1%}")
