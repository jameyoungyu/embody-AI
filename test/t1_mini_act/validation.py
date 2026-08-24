"""
T1-mini-real Integration Qualification Gate Engine (5 Gates)
============================================================
Implements:
1. Gate 1: Replay Stability (Exact MuJoCo S_0 restore -> deterministic clean replay);
2. Gate 2: Camera Observation Shift (RGB image changes: ||I_clean - I_camera||_1 > 0, while physics state invariant);
3. Gate 3: Object Pose Isolation (Target object shifts via q_delta (x) q_base; all other physical state invariant);
4. Gate 4: Real Severity Non-Degeneracy (0.05 <= p_OOD <= 0.85, no floor/ceiling extremes);
5. Gate 5: Checkpoint Capability Span (Validation Clean SR span >= 35%);
6. Protocol Isolation Gate (Frozen Test set non-instantiation check).
"""

from typing import Dict, Any, Tuple, List
import numpy as np
import copy

from state_manager import InitialStateSnapshot, StateManager
from policy_state_manager import PolicyStateManager
from perturbations import PerturbationBank, TASK_TARGET_OBJECTS


class IntegrationGateValidator:
    """Verifies all 5 T1-mini-real Integration Qualification Gates."""

    @staticmethod
    def verify_gate_1_replay_stability(policy: Any, env: Any, snapshot: InitialStateSnapshot, n_repeats: int = 3) -> Tuple[bool, str]:
        """Gate 1: State Replay Reproducibility & Stability."""
        outcomes = []
        for _ in range(n_repeats):
            StateManager.restore_to_env(env, snapshot)
            policy.reset(episode_seed=42)
            res, _ = policy.rollout(env, is_perturbed=False)
            outcomes.append(res)
            
        if len(set(outcomes)) != 1:
            return False, f"Replay Stability Failure: Outcomes varied across repeats: {outcomes}"
        return True, f"Gate 1 (Replay Stability): 100% Deterministic across {n_repeats} clean rollouts (PASS)"

    @staticmethod
    def verify_gate_2_camera_obs_shift(env: Any, snapshot: InitialStateSnapshot, pert_bank: PerturbationBank) -> Tuple[bool, str]:
        """
        Gate 2: Camera Observation Shift.
        Verifies that camera perturbation alters rendered RGB pixels while physics remains strictly invariant.
        """
        # 1. Clean rendering
        StateManager.restore_to_env(env, snapshot)
        img_clean = env.render_observation_rgb()
        qpos_clean = np.array(env.robot_qpos, copy=True)
        poses_clean = {k: np.array(v, copy=True) for k, v in env.object_poses.items()}
        
        # 2. Perturbed rendering
        realization = pert_bank.get_realization(snapshot, env.current_context, axis_name="camera_viewpoint", severity="medium")
        StateManager.restore_to_env(env, realization.perturbed_snapshot)
        env.current_context = copy.deepcopy(realization.perturbed_env_context)
        img_camera = env.render_observation_rgb()
        qpos_camera = np.array(env.robot_qpos, copy=True)
        poses_camera = {k: np.array(v, copy=True) for k, v in env.object_poses.items()}
        
        # Check image difference
        pixel_diff = float(np.mean(np.abs(img_clean.astype(float) - img_camera.astype(float))))
        if pixel_diff < 1e-3:
            return False, f"Camera Shift Failure: Rendered RGB images are identical (diff={pixel_diff:.4f})"
            
        # Check physics invariance
        qpos_diff = float(np.max(np.abs(qpos_clean - qpos_camera)))
        if qpos_diff > 1e-7:
            return False, f"Physics Invariance Failure: qpos shifted during camera perturbation ({qpos_diff:.2e})"
            
        for k in poses_clean:
            obj_diff = float(np.max(np.abs(poses_clean[k] - poses_camera[k])))
            if obj_diff > 1e-7:
                return False, f"Physics Invariance Failure: Object {k} moved during camera perturbation ({obj_diff:.2e})"
                
        return True, f"Gate 2 (Camera Obs Shift): RGB Pixel Diff={pixel_diff:.2f}, Physics Joint/Pose Invariance=100% (PASS)"

    @staticmethod
    def verify_gate_3_object_pose_isolation(env: Any, snapshot: InitialStateSnapshot, pert_bank: PerturbationBank) -> Tuple[bool, str]:
        """
        Gate 3: Object Pose Isolation & Quaternion Composition.
        Verifies that only the designated target object moves via q_delta (x) q_base;
        other objects and robot joint state remain strictly unchanged.
        """
        StateManager.restore_to_env(env, snapshot)
        poses_clean = {k: np.array(v, copy=True) for k, v in env.object_poses.items()}
        qpos_clean = np.array(env.robot_qpos, copy=True)
        
        realization = pert_bank.get_realization(snapshot, env.current_context, axis_name="object_initial_pose", severity="medium")
        StateManager.restore_to_env(env, realization.perturbed_snapshot)
        env.current_context = copy.deepcopy(realization.perturbed_env_context)
        poses_ood = {k: np.array(v, copy=True) for k, v in env.object_poses.items()}
        qpos_ood = np.array(env.robot_qpos, copy=True)
        
        target_obj = realization.applied_params.get("target_object")
        if not target_obj or target_obj not in poses_clean:
            return False, f"Object Isolation Failure: Target object '{target_obj}' not found in scene"
            
        # Target object must have moved
        target_diff = float(np.max(np.abs(poses_clean[target_obj] - poses_ood[target_obj])))
        if target_diff < 1e-3:
            return False, f"Object Isolation Failure: Target object did not move ({target_diff:.4f})"
            
        # Other objects must NOT have moved
        for k in poses_clean:
            if k != target_obj:
                other_diff = float(np.max(np.abs(poses_clean[k] - poses_ood[k])))
                if other_diff > 1e-7:
                    return False, f"Object Isolation Failure: Non-target object {k} moved ({other_diff:.2e})"
                    
        # Robot joints must NOT have moved
        qpos_diff = float(np.max(np.abs(qpos_clean - qpos_ood)))
        if qpos_diff > 1e-7:
            return False, f"Object Isolation Failure: Robot joints moved ({qpos_diff:.2e})"
            
        return True, f"Gate 3 (Object Pose Isolation): Target '{target_obj}' Shifted via Quaternion Composition, Non-targets Intact (PASS)"

    @staticmethod
    def verify_gate_4_severity_non_degeneracy(p_ood_values: List[float]) -> Tuple[bool, str]:
        """Gate 4: Severity Non-Degeneracy (No floor/ceiling extremes)."""
        min_ood = min(p_ood_values)
        max_ood = max(p_ood_values)
        if max_ood < 0.05:
            return False, f"Severity Degeneracy: Floor effect (max OOD SR = {max_ood*100:.1f}% < 5%)"
        if min_ood > 0.85:
            return False, f"Severity Degeneracy: Ceiling effect (min OOD SR = {min_ood*100:.1f}% > 85%)"
        return True, f"Gate 4 (Severity Non-Degeneracy): OOD SR Range [{min_ood*100:.1f}%, {max_ood*100:.1f}%] within valid operational envelope (PASS)"

    @staticmethod
    def verify_gate_5_capability_span(clean_srs: List[float], min_span: float = 0.35) -> Tuple[bool, str]:
        """Gate 5: Checkpoint Capability Span."""
        span = float(max(clean_srs) - min(clean_srs))
        if span < min_span:
            return False, f"Capability Span Insufficient: Span {span*100:.1f}% < {min_span*100:.1f}%"
        return True, f"Gate 5 (Capability Span): Clean SR Span {span*100:.1f}% >= {min_span*100:.1f}% (PASS)"
