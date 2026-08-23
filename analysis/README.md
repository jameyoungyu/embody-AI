# analysis

Statistical machinery for the C1 pilot. Pure numpy/scipy, no GPU, runs in seconds.

| file | what it is |
| --- | --- |
| `idood_model.py` | The ID→OOD model. `Cell` holds one (checkpoint, condition) observation; `fit` is the profile MLE over (alpha, gamma) with latent clean rates solved in closed form; `lrt_proportional` tests gamma == 1, the assumption PDR rests on; `effective_robustness` and `pdr` compute the two competing robustness measures. |
| `power_sim.py` | Reusable pieces: `simulate`, `rejection_rate`, `pdr_bias_demo`. |
| `run_power.py` | Driver that produces `power_results.txt`. |
| `power_results.txt` | Calibration, power, and the PDR capability-confound numbers quoted in `docs/10_stage3_pilot_protocol.md`. |

Real pilot data only needs to be shaped into `list[Cell]`:

```python
from idood_model import Cell, lrt_proportional
cells = [Cell(k_clean=98, n_clean=150, k_ood=41, n_ood=150), ...]
print(lrt_proportional(cells))
```

Do not fit observed rate against observed rate with ordinary least squares. Both
rates come from finite episode counts, and regressing one noisy estimate on
another attenuates the slope toward zero — manufacturing exactly the gamma < 1
the pilot is meant to test for. The latent-rate likelihood here exists to avoid
that.
