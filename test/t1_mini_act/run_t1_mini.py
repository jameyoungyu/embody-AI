"""
Master T1-mini ACT Pipeline Runner & Smoke Test
================================================
Executes:
1. Level A/B/C Reproducibility Verification (Physics, Observation, Rollout);
2. Four-Set Physical Isolation Verification;
3. Validation Set Checkpoint Capability Binning (5 levels);
4. Calibration / Smoke Set Paired Clean/OOD Rollouts;
5. Granular 20-Field CSV Logging;
6. Paired Bootstrap CI & Retention Decomposition Analysis;
7. Decision Gate Audit Report Generation.
"""

import os
import sys
import time
from typing import List, Tuple, Dict, Any
import numpy as np

# Add local path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from config import ExperimentConfig, T1_MINI_TARGET_CLEAN_SR
from state_manager import StateManager, InitialStateSnapshot
from policy_state_manager import PolicyStateManager
from eval_paired import MockLiberoEnv, ACTCheckpointPolicy, PairedEvaluator
from logger import GranularLogger
from validation import ProtocolValidator
from analyze import analyze_t1_mini_dataset, generate_comprehensive_report


def run_pre_flight_checks(evaluator: PairedEvaluator) -> bool:
    """Run Level A, Level B, Level C reproducibility checks and split isolation."""
    print("[1/5] Running Level A/B/C Reproducibility & Protocol Isolation Checks...")
    env = evaluator.env
    dummy_policy = ACTCheckpointPolicy("check_policy", target_clean_sr=0.60)
    snap = env.generate_initial_snapshot(episode_idx=99)
    
    # Level A: Physics restore
    ok_a, msg_a = ProtocolValidator.verify_level_a_physics_restore(env, snap)
    print(f"      [{'PASS' if ok_a else 'FAIL'}] Level A: {msg_a}")
    if not ok_a:
        return False

    # Level B: Observation restore
    ok_b, msg_b = ProtocolValidator.verify_level_b_observation_restore(env, snap)
    print(f"      [{'PASS' if ok_b else 'FAIL'}] Level B: {msg_b}")
    if not ok_b:
        return False

    # Level C: Rollout reproducibility
    ok_c, msg_c = ProtocolValidator.verify_level_c_rollout_reproducibility(dummy_policy, env, snap, n_repeats=3)
    print(f"      [{'PASS' if ok_c else 'FAIL'}] Level C: {msg_c}")
    if not ok_c:
        return False

    # Four-Set Isolation
    val_snaps = evaluator.split_mgr.get_validation_snapshots()
    smoke_snaps = evaluator.split_mgr.get_smoke_snapshots()
    ok_iso, msg_iso = ProtocolValidator.verify_split_isolation(val_snaps, smoke_snaps)
    print(f"      [{'PASS' if ok_iso else 'FAIL'}] Four-Set Isolation: {msg_iso}")
    if not ok_iso:
        return False

    return True


def main():
    print("=" * 110)
    print("T1-mini ACT Pipeline Smoke Run: Paired Disruption (D) & Gain (G) Decomposition")
    print("=" * 110)
    
    config = ExperimentConfig()
    results_dir = os.path.join(current_dir, "results")
    os.makedirs(results_dir, exist_ok=True)
    
    csv_path = os.path.join(results_dir, config.log_csv_filename)
    report_path = os.path.join(results_dir, config.summary_report_filename)
    
    # Clean previous run
    if os.path.exists(csv_path):
        os.remove(csv_path)
        
    logger = GranularLogger(output_path=csv_path)
    evaluator = PairedEvaluator(config=config, logger=logger)
    
    # 1. Pre-flight reproducibility checks
    if not run_pre_flight_checks(evaluator):
        print("Aborting: Pre-flight protocol checks failed.")
        sys.exit(1)

    # 2. Checkpoint binning on independent Validation Set
    print(f"\n[2/5] Initializing ACT Checkpoints across 5 Capability Levels...")
    policies: List[Tuple[ACTCheckpointPolicy, float]] = []
    
    for idx, target_sr in enumerate(T1_MINI_TARGET_CLEAN_SR):
        ckpt_name = f"act_ckpt_epoch_{(idx+1)*15}"
        policy = ACTCheckpointPolicy(
            checkpoint_name=ckpt_name,
            target_clean_sr=target_sr,
            seed=config.default_seed
        )
        val_clean_sr = evaluator.evaluate_checkpoint_clean_val(policy)
        policies.append((policy, val_clean_sr))
        print(f"      Checkpoint `{ckpt_name}` -> Target: {target_sr*100:4.1f}% | Validation Clean SR: {val_clean_sr*100:4.1f}%")

    # 3. Paired Clean/OOD Rollouts on Calibration / Smoke Set
    print(f"\n[3/5] Executing Calibration/Smoke Paired Rollouts (Dual S_0 & Policy Reset)...")
    print(f"      Axes: {config.t1_mini_axes} | Severity: `{config.t1_mini_severity}` | Quota: {config.smoke_episodes_per_cell} pairs/cell")
    
    t_start = time.time()
    for policy, val_clean_sr in policies:
        for axis_name in config.t1_mini_axes:
            res = evaluator.evaluate_smoke_set_paired(
                policy=policy,
                clean_val_sr=val_clean_sr,
                perturbation_axis=axis_name,
                severity=config.t1_mini_severity
            )
            print(f"      [{policy.checkpoint_name} | {axis_name:<20}] Clean: {np.mean(res['y_clean'])*100:5.1f}% | OOD: {np.mean(res['y_ood'])*100:5.1f}% | Wallclock: {res['wallclock_sec']:.2f}s")
            
    total_elapsed = time.time() - t_start
    print(f"      Total Test Rollouts Time: {total_elapsed:.2f}s ({total_elapsed/len(policies):.2f}s per checkpoint)")

    # 4. Statistical Analysis & Decomposition
    print(f"\n[4/5] Computing Paired Bootstrap CIs & Retention Decomposition (R = 1 - D + ((1-pc)/pc)*G)...")
    analysis_output = analyze_t1_mini_dataset(csv_path, n_bootstrap=config.bootstrap_samples)
    
    # 5. Generate Report
    print(f"\n[5/5] Generating Audit Report -> {report_path}")
    generate_comprehensive_report(analysis_output, report_path)
    
    print("\n" + "=" * 110)
    print(f"DECISION RECOMMENDATION: {analysis_output['decision_verdict']}")
    print(f"RATIONALE:               {analysis_output['decision_rationale']}")
    print(f"RAW CSV LOG (20 FIELDS): {csv_path}")
    print(f"AUDIT REPORT:            {report_path}")
    print("=" * 110)


if __name__ == "__main__":
    main()
