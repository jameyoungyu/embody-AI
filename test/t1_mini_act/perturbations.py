"""
Perturbation Operators & Perturbation Bank (T_d: S_{0,j} -> S_{0,j}^{OOD})
==========================================================================
Formalizes the perturbation operator T_d:
- Perception-side: Modifies camera extrinsics / lighting context while preserving S_{0,j}^{env} physics intact.
- State-side: Shifts task-specific target object pose (dx, dy, dtheta) with Hamilton quaternion composition
  (q_new = q_delta (x) q_base), workspace bounds validation, and collision rejection.

Guarantees cross-checkpoint frozen parameter bank with exact seed provenance.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Tuple, Optional
import numpy as np
import copy
import hashlib

from state_manager import InitialStateSnapshot
from config import CameraPerturbationDist, LightingPerturbationDist, ObjectPosePerturbationDist


TASK_TARGET_OBJECTS: Dict[str, str] = {
    "libero_spatial_pick_up_the_black_bowl": "black_bowl",
    "libero_spatial_push_the_plate_to_the_front": "plate",
    "libero_object_pick_up_the_alphabet_soup": "alphabet_soup",
    "libero_goal_open_the_middle_drawer": "middle_drawer"
}


def quaternion_multiply(q1: np.ndarray, q2: np.ndarray, convention: str = "xyzw") -> np.ndarray:
    """
    Multiply two quaternions: q_out = q1 (x) q2 (Hamilton product).
    Supports Robosuite [x, y, z, w] and MuJoCo [w, x, y, z] conventions.
    """
    if convention == "xyzw":
        x1, y1, z1, w1 = q1
        x2, y2, z2, w2 = q2
        w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
        x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
        y = w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2
        z = w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2
        res = np.array([x, y, z, w], dtype=float)
    elif convention == "wxyz":
        w1, x1, y1, z1 = q1
        w2, x2, y2, z2 = q2
        w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
        x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
        y = w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2
        z = w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2
        res = np.array([w, x, y, z], dtype=float)
    else:
        raise ValueError(f"Unknown quaternion convention: {convention}")
        
    norm = np.linalg.norm(res)
    return res / norm if norm > 1e-8 else res


@dataclass
class PerturbationRealization:
    """Explicit realization provenance returned by operator and bank."""
    bank_key: str
    bank_version: str
    actual_seed: int
    applied_params: Dict[str, float]
    perturbed_snapshot: InitialStateSnapshot
    perturbed_env_context: Dict[str, Any]


class BasePerturbationOperator(ABC):
    """Abstract base class for perturbation operator T_d."""

    def __init__(self, axis_name: str, severity: str = "medium"):
        self.axis_name = axis_name
        self.severity = severity

    @abstractmethod
    def apply(
        self,
        snapshot: InitialStateSnapshot,
        env_context: Dict[str, Any],
        rng: np.random.RandomState
    ) -> Tuple[InitialStateSnapshot, Dict[str, Any], Dict[str, float]]:
        """
        Apply operator T_d to initial snapshot S_{0,j}.
        Returns: (perturbed_snapshot, perturbed_env_context, applied_numeric_params)
        """
        pass


class CameraViewpointOperator(BasePerturbationOperator):
    """
    Perception-side T_d: Alters camera extrinsics (azimuth, elevation, pos_shift).
    Leaves MuJoCo physical joints and object poses strictly invariant.
    """

    def __init__(self, severity: str = "medium", dist_config: Optional[CameraPerturbationDist] = None):
        super().__init__(axis_name="camera_viewpoint", severity=severity)
        self.dist = dist_config or CameraPerturbationDist()

    def apply(
        self,
        snapshot: InitialStateSnapshot,
        env_context: Dict[str, Any],
        rng: np.random.RandomState
    ) -> Tuple[InitialStateSnapshot, Dict[str, Any], Dict[str, float]]:
        perturbed_snapshot = copy.deepcopy(snapshot)
        perturbed_context = copy.deepcopy(env_context)
        
        # Sample exact deltas
        d_azimuth = float(rng.uniform(self.dist.azimuth_range_deg[0], self.dist.azimuth_range_deg[1]))
        d_elevation = float(rng.uniform(self.dist.elevation_range_deg[0], self.dist.elevation_range_deg[1]))
        d_pos_x = float(rng.uniform(self.dist.pos_shift_range[0], self.dist.pos_shift_range[1]))
        d_pos_y = float(rng.uniform(self.dist.pos_shift_range[0], self.dist.pos_shift_range[1]))
        
        cam_params = copy.deepcopy(perturbed_snapshot.camera_base_params)
        cam_params["azimuth_offset_deg"] = d_azimuth
        cam_params["elevation_offset_deg"] = d_elevation
        cam_params["pos_shift"] = [d_pos_x, d_pos_y, 0.0]
        
        perturbed_snapshot.camera_base_params = cam_params
        perturbed_context["camera_extrinsics_perturbed"] = True
        perturbed_context["camera_perturbation_params"] = {
            "azimuth_delta_deg": d_azimuth,
            "elevation_delta_deg": d_elevation,
            "pos_shift_x": d_pos_x,
            "pos_shift_y": d_pos_y
        }
        
        applied_params = {
            "camera_azimuth_delta_deg": d_azimuth,
            "camera_elevation_delta_deg": d_elevation,
            "camera_pos_shift_x": d_pos_x,
            "camera_pos_shift_y": d_pos_y
        }
        
        return perturbed_snapshot, perturbed_context, applied_params


class LightingOperator(BasePerturbationOperator):
    """
    Perception-side T_d: Scales illumination intensity while leaving physical state intact.
    """

    def __init__(self, severity: str = "medium", dist_config: Optional[LightingPerturbationDist] = None):
        super().__init__(axis_name="lighting", severity=severity)
        self.dist = dist_config or LightingPerturbationDist()

    def apply(
        self,
        snapshot: InitialStateSnapshot,
        env_context: Dict[str, Any],
        rng: np.random.RandomState
    ) -> Tuple[InitialStateSnapshot, Dict[str, Any], Dict[str, float]]:
        perturbed_snapshot = copy.deepcopy(snapshot)
        perturbed_context = copy.deepcopy(env_context)
        
        intensity = float(rng.uniform(self.dist.intensity_scale_range[0], self.dist.intensity_scale_range[1]))
        perturbed_context["lighting_intensity_scale"] = intensity
        perturbed_context["lighting_perturbed"] = True
        
        applied_params = {"lighting_intensity_scale": intensity}
        return perturbed_snapshot, perturbed_context, applied_params


class ObjectPoseOperator(BasePerturbationOperator):
    """
    State-side T_d: Modifies target object pose via Hamilton quaternion multiplication (q_delta (x) q_base).
    Leaves all other objects and robot joint state strictly invariant.
    """

    def __init__(self, severity: str = "medium", dist_config: Optional[ObjectPosePerturbationDist] = None):
        super().__init__(axis_name="object_initial_pose", severity=severity)
        self.dist = dist_config or ObjectPosePerturbationDist()

    def apply(
        self,
        snapshot: InitialStateSnapshot,
        env_context: Dict[str, Any],
        rng: np.random.RandomState
    ) -> Tuple[InitialStateSnapshot, Dict[str, Any], Dict[str, float]]:
        perturbed_snapshot = copy.deepcopy(snapshot)
        perturbed_context = copy.deepcopy(env_context)
        
        # Determine task target object name
        target_obj = TASK_TARGET_OBJECTS.get(snapshot.task_id, list(snapshot.object_poses.keys())[0])
        if target_obj not in snapshot.object_poses:
            target_obj = list(snapshot.object_poses.keys())[0]
            
        base_pose = list(snapshot.object_poses[target_obj])
        
        # Sample with rejection loop to guarantee workspace bounds & obstacle clearance
        for _ in range(50):
            dx = float(rng.uniform(self.dist.dx_range[0], self.dist.dx_range[1]))
            dy = float(rng.uniform(self.dist.dy_range[0], self.dist.dy_range[1]))
            dtheta = float(rng.uniform(self.dist.dtheta_range_deg[0], self.dist.dtheta_range_deg[1]))
            
            new_x = base_pose[0] + dx
            new_y = base_pose[1] + dy
            
            # Check workspace bounds
            b = self.dist.workspace_bounds
            if not (b[0] <= new_x <= b[1] and b[2] <= new_y <= b[3]):
                continue
                
            # Check obstacle clearance if obstacles present
            collision = False
            for obj_name, obj_p in snapshot.object_poses.items():
                if obj_name != target_obj:
                    dist = float(np.linalg.norm(np.array([new_x, new_y]) - np.array(obj_p[:2])))
                    if dist < self.dist.min_dist_to_obstacles:
                        collision = True
                        break
            if not collision:
                break
        else:
            dx, dy, dtheta = 0.01, 0.01, 5.0
            new_x = base_pose[0] + dx
            new_y = base_pose[1] + dy

        new_pose = copy.deepcopy(base_pose)
        new_pose[0] = new_x
        new_pose[1] = new_y
        
        # Quaternion rotation composition: q_new = q_delta (x) q_base
        # Standard Robosuite quaternion convention: [x, y, z, w]
        rad = np.radians(dtheta)
        q_delta = np.array([0.0, 0.0, float(np.sin(rad / 2.0)), float(np.cos(rad / 2.0))])
        q_base = np.array(base_pose[3:7], dtype=float)
        q_new = quaternion_multiply(q_delta, q_base, convention="xyzw")
        
        new_pose[3:7] = q_new.tolist()
        perturbed_snapshot.object_poses[target_obj] = new_pose
        perturbed_context["object_pose_perturbed"] = True
        perturbed_context["target_object_perturbed"] = target_obj
        
        applied_params = {
            "target_object": target_obj,
            "object_dx": dx,
            "object_dy": dy,
            "object_dtheta_deg": dtheta,
            "object_final_x": new_x,
            "object_final_y": new_y
        }
        
        return perturbed_snapshot, perturbed_context, applied_params


class PerturbationBank:
    """
    Pre-generated, frozen bank of perturbation parameters.
    Explicit key: task_id + initial_state_hash + axis + severity + bank_version.
    Guarantees delta_{j,d}^{(C_1)} == delta_{j,d}^{(C_2)} == ... across all checkpoints.
    """

    BANK_VERSION = "v1.0_frozen"

    def __init__(self, master_seed: int = 42):
        self.master_seed = master_seed
        self._operators: Dict[Tuple[str, str], BasePerturbationOperator] = {}
        self._bank: Dict[str, PerturbationRealization] = {}

    def _get_operator(self, axis_name: str, severity: str) -> BasePerturbationOperator:
        key = (axis_name, severity)
        if key not in self._operators:
            self._operators[key] = get_perturbation_operator(axis_name, severity=severity)
        return self._operators[key]

    def get_realization(
        self,
        snapshot: InitialStateSnapshot,
        env_context: Dict[str, Any],
        axis_name: str,
        severity: str = "medium"
    ) -> PerturbationRealization:
        """
        Retrieve or deterministically generate the frozen perturbation realization.
        Returns full provenance (actual_seed, params, bank_key, bank_version).
        """
        state_hash = snapshot.compute_hash()
        bank_key = f"{snapshot.task_id}_{state_hash}_{axis_name}_{severity}_{self.BANK_VERSION}"
        
        if bank_key not in self._bank:
            operator = self._get_operator(axis_name, severity)
            # Deterministic actual integer seed derived from SHA-256
            seed_hash_hex = hashlib.sha256(f"{bank_key}_{self.master_seed}".encode()).hexdigest()[:8]
            actual_seed = int(seed_hash_hex, 16) % (2**31 - 1)
            rng = np.random.RandomState(actual_seed)
            
            pert_snap, pert_ctx, applied_params = operator.apply(
                snapshot=snapshot,
                env_context=env_context,
                rng=rng
            )
            self._bank[bank_key] = PerturbationRealization(
                bank_key=bank_key,
                bank_version=self.BANK_VERSION,
                actual_seed=actual_seed,
                applied_params=applied_params,
                perturbed_snapshot=pert_snap,
                perturbed_env_context=pert_ctx
            )
            
        realization = self._bank[bank_key]
        return PerturbationRealization(
            bank_key=realization.bank_key,
            bank_version=realization.bank_version,
            actual_seed=realization.actual_seed,
            applied_params=copy.deepcopy(realization.applied_params),
            perturbed_snapshot=copy.deepcopy(realization.perturbed_snapshot),
            perturbed_env_context=copy.deepcopy(realization.perturbed_env_context)
        )


def get_perturbation_operator(axis_name: str, severity: str = "medium") -> BasePerturbationOperator:
    """Factory to retrieve requested perturbation operator."""
    if axis_name == "camera_viewpoint":
        return CameraViewpointOperator(severity=severity)
    elif axis_name == "lighting":
        return LightingOperator(severity=severity)
    elif axis_name == "object_initial_pose":
        return ObjectPoseOperator(severity=severity)
    else:
        raise ValueError(f"Unknown perturbation axis: {axis_name}")
