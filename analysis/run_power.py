"""Driver: produces the calibration/power table quoted in the Stage 3 protocol."""
import numpy as np
import idood_model as M  # noqa: F401  (imported for side-effect-free availability check)
from power_sim import rejection_rate, pdr_bias_demo

ALPHA = float(np.log(0.55)); REPS = 150; SEED = 20260823
print("Calibration and power of the LRT for H0: gamma == 1")
print(f"alpha = log(0.55); {REPS} replicates per configuration; nominal level 0.05\n")
grid = [("wide (clean SR 0.20-0.90)", 0.20, 0.90,
         [(g, m, n) for g in (1.0, 1.25, 1.5, 2.0) for m, n in ((12, 50), (12, 150), (20, 150))]),
        ("narrow (clean SR 0.45-0.75)", 0.45, 0.75,
         [(g, 12, 150) for g in (1.0, 1.5)])]
hdr = f"{'gamma':>6} {'M':>4} {'N/cell':>7} {'episodes':>9} {'reject':>8}   gamma_hat"
for label, lo, hi, cfgs in grid:
    print(f"--- checkpoint spread: {label} ---"); print(hdr, flush=True)
    for g, m, n in cfgs:
        r, gm, gs = rejection_rate(REPS, m, n, g, ALPHA, lo, hi, SEED + int(g * 100) + m + n)
        tag = "   <- type I error" if g == 1.0 else ""
        print(f"{g:>6.2f} {m:>4} {n:>7} {2*m*n:>9} {r:>7.1%}   {gm:.3f} +/-{gs:.3f}{tag}", flush=True)
    print(flush=True)
print("Capability confound in PDR, for policies exactly ON the fitted curve")
print("(every one has zero effective robustness by construction)")
for g in (0.75, 1.0, 1.5, 2.0):
    p, d = pdr_bias_demo(ALPHA, g, 0.30, 0.90)
    print(f"gamma={g:>4.2f}   PDR at clean SR 0.30 -> 0.90: {d[0]:.3f} -> {d[-1]:.3f}"
          f"   spread = {(d.max()-d.min())*100:5.1f} points")
