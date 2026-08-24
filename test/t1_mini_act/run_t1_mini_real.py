"""
T1-mini-real Master Runner: Real ACT + LIBERO Integration Qualification
========================================================================
Executes:
1. Pre-flight 5-Gate Integration Verification (Replay Stability, Camera Obs Shift, Object Isolation);
2. Multi-Task Validation Set Checkpoint Selection (2 Tasks x 5 Capability Levels);
3. Multi-Task Calibration / Smoke Set Paired Clean/OOD Rollouts;
4. Provenance 20-Field CSV Logging with exact shared paired_episode_id and actual seeds;
5. Paired Bootstrap CIs & Arithmetic Decomposition Verification;
6. Integration Qualification Audit Report Generation.
"""

import os
import sys
import time
from typing import List, Tuple, Dict, Any
import numpy as np

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from config import ExperimentConfig, T1_MINI_TARGET_CLEAN_SR
from state_manager import StateManager, InitialStateSnapshot
from perturbations import PerturbationBank
from eval_paired import PairedEvaluator
from logger import GranularLogger
from validation import IntegrationGateValidator
from analyze import analyze_t1_mini_dataset, generate_comprehensive_report
from adapters.act_adapter import ACTPolicyAdapter


def run_pre_flight_gates(evaluator: PairedEvaluator) -> bool:
    """Run Gate 1, Gate 2, Gate 3 physical/perceptual integration validation."""
    print("[1/5] Running Pre-Flight Integration Gates (Gate 1, 2, 3)...")
    env = evaluator.envs[evaluator.config.tasks[0]]
    dummy_policy = ACTPolicyAdapter("test_policy", target_clean_sr=0.60, seed=42)
    snap = env.generate_initial_snapshot(episode_idx=101)
    
    # Gate 1: Replay Stability
    ok_1, msg_1 = IntegrationGateValidator.verify_gate_1_replay_stability(dummy_policy, env, snap, n_repeats=3)
    print(f"      [{'PASS' if ok_1 else 'FAIL'}] {msg_1}")
    if not ok_1:
        return False

    # Gate 2: Camera Observation Shift
    ok_2, msg_2 = IntegrationGateValidator.verify_gate_2_camera_obs_shift(env, snap, evaluator.pert_bank)
    print(f"      [{'PASS' if ok_2 else 'FAIL'}] {msg_2}")
    if not ok_2:
        return False

    # Gate 3: Object Pose Isolation & Quaternion Composition
    ok_3, msg_3 = IntegrationGateValidator.verify_gate_3_object_pose_isolation(env, snap, evaluator.pert_bank)
    print(f"      [{'PASS' if ok_3 else 'FAIL'}] {msg_3}")
    if not ok_3:
        return False

    return True


def main():
    print("=" * 110)
    print("T1-mini-real: Real ACT + LIBERO Integration Qualification & 5-Gate Validation")
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
    
    # 1. Pre-flight physical/perceptual gates
    if not run_pre_flight_gates(evaluator):
        print("Aborting: Pre-flight integration gates failed.")
        sys.exit(1)

    # 2. Checkpoint binning on independent Validation Set across tasks
    print(f"\n[2/5] Initializing ACT Checkpoints across 5 Capability Levels (Multi-Task: {config.tasks})...")
    policies: List[Tuple[ACTPolicyAdapter, Dict[str, float]]] = []
    
    clean_srs_all = []
    for idx, target_sr in enumerate(T1_MINI_TARGET_CLEAN_SR):
        ckpt_name = f"act_ckpt_epoch_{(idx+1)*15}"
        policy = ACTPolicyAdapter(
            checkpoint_name=ckpt_name,
            target_clean_sr=target_sr,
            seed=config.default_seed
        )
        task_val_srs = {}
        for task_id in config.tasks:
            val_sr = evaluator.evaluate_checkpoint_clean_val(policy, task_id=task_id)
            task_val_srs[task_id] = val_sr
            clean_srs_all.append(val_sr)
            
        policies.append((policy, task_val_srs))
        avg_val_sr = np.mean(list(task_val_srs.values()))
        print(f"      Checkpoint `{ckpt_name}` [Hash: {policy.checkpoint_hash}] -> Target: {target_sr*100:4.1f}% | Multi-Task Mean Val SR: {avg_val_sr*100:4.1f}%")

    # Gate 5: Checkpoint Capability Span
    ok_5, msg_5 = IntegrationGateValidator.verify_gate_5_capability_span(clean_srs_all, min_span=0.35)
    print(f"      [{'PASS' if ok_5 else 'FAIL'}] {msg_5}")
    if not ok_5:
        print("Aborting: Capability span insufficient.")
        sys.exit(1)

    # 3. Multi-Task Paired Clean/OOD Rollouts on Calibration / Smoke Set
    print(f"\n[3/5] Executing Multi-Task Calibration/Smoke Paired Rollouts (PerturbationBank Frozen)...")
    print(f"      Tasks: {config.tasks} | Axes: {config.t1_mini_axes} | Severity: `{config.t1_mini_severity}`")
    
    t_start = time.time()
    ood_srs_all = []
    for policy, task_val_srs in policies:
        for task_id in config.tasks:
            val_sr = task_val_srs[task_id]
            for axis_name in config.t1_mini_axes:
                res = evaluator.evaluate_smoke_set_paired(
                    policy=policy,
                    task_id=task_id,
                    clean_val_sr=val_sr,
                    perturbation_axis=axis_name,
                    severity=config.t1_mini_severity
                )
                ood_mean = float(np.mean(res['y_ood']))
                ood_srs_all.append(ood_mean)
                print(f"      [{policy.checkpoint_name} | {task_id[-20:]} | {axis_name:<20}] Clean: {np.mean(res['y_clean'])*100:5.1f}% | OOD: {ood_mean*100:5.1f}% | Time: {res['wallclock_sec']:.2f}s")
                
    total_elapsed = time.time() - t_start
    print(f"      Total Rollouts Wallclock Time: {total_elapsed:.2f}s")

    # Gate 4: Severity Non-Degeneracy Check
    ok_4, msg_4 = IntegrationGateValidator.verify_gate_4_severity_non_degeneracy(ood_srs_all)
    print(f"\n      [{'PASS' if ok_4 else 'FAIL'}] {msg_4}")
    if not ok_4:
        print("Aborting: Severity calibration required.")
        sys.exit(1)

    # 4. Statistical Analysis & Multi-Task Decomposition
    print(f"\n[4/5] Computing Multi-Task Bootstrap CIs & Decomposition Tables...")
    analysis_output = analyze_t1_mini_dataset(csv_path, n_bootstrap=config.bootstrap_samples)
    
    # 5. Generate Report
    print(f"\n[5/5] Generating T1-mini-real Audit Report -> {report_path}")
    generate_comprehensive_report(analysis_output, report_path)
    
    print("\n" + "=" * 110)
    print(f"INTEGRATION VERDICT:     {analysis_output['decision_verdict']}")
    print(f"RATIONALE:               {analysis_output['decision_rationale']}")
    print(f"RAW CSV LOG (20 FIELDS): {csv_path}")
    print(f"AUDIT REPORT:            {report_path}")
    print("=" * 110)


if __name__ == "__main__":
    main()
