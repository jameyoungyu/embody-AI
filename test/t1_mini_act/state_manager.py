"""
Explicit Initial Physical State Manager (S^{env}_0)
====================================================
Implements comprehensive physical state snapshot serialization and restoration.
Captures object poses, robot qpos/qvel, simulation time, actuator/controller state,
camera base parameters, task goal bounds, and environment RNG states.
"""

from dataclasses import dataclass, field, asdict
import json
import hashlib
from typing import Dict, Any, Optional, Tuple, List
import numpy as np
import copy


@dataclass
class InitialStateSnapshot:
    """
    Complete base physical state snapshot S_{0,j} of an environment before rollout.
    """
    snapshot_id: str
    task_id: str
    object_poses: Dict[str, list]               # object_name -> [x, y, z, qx, qy, qz, qw]
    robot_qpos: list                            # Robot joint positions
    robot_qvel: list                            # Robot joint velocities
    sim_time: float                             # Simulation time elapsed
    actuator_state: list                        # Actuator force / target values
    controller_state: Dict[str, Any]            # Controller internal parameters
    task_params: Dict[str, Any]                 # Goal / target layout parameters
    camera_base_params: Dict[str, Any]          # Base camera extrinsics & intrinsics
    instruction: str                            # Language prompt / instruction text
    env_metadata: Dict[str, Any] = field(default_factory=dict)
    env_rng_state: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # Drop non-serializable raw rng state in json export
        if "env_rng_state" in d and d["env_rng_state"] is not None:
            d["env_rng_state"] = None
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InitialStateSnapshot":
        return cls(**data)

    def compute_hash(self) -> str:
        """
        Compute a deterministic SHA-256 hash of the complete initial physical state.
        Includes joints, velocities, all object poses, actuators, controllers, camera, and RNG state.
        """
        rng_repr = str(self.env_rng_state[1][:10]) if (isinstance(self.env_rng_state, tuple) and len(self.env_rng_state) > 1) else str(self.env_rng_state)
        content = json.dumps({
            "task_id": self.task_id,
            "object_poses": {k: [round(x, 6) for x in v] for k, v in sorted(self.object_poses.items())},
            "robot_qpos": [round(x, 6) for x in self.robot_qpos],
            "robot_qvel": [round(x, 6) for x in self.robot_qvel],
            "sim_time": round(float(self.sim_time), 6),
            "actuator_state": [round(x, 6) for x in self.actuator_state],
            "controller_state": self.controller_state,
            "task_params": self.task_params,
            "camera_base_params": self.camera_base_params,
            "instruction": self.instruction,
            "env_rng_state": rng_repr
        }, sort_keys=True)
        return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


class StateManager:
    """Manages physical environment snapshot capture and restoration."""

    @staticmethod
    def capture_snapshot(
        task_id: str,
        object_poses: Dict[str, np.ndarray],
        robot_qpos: np.ndarray,
        robot_qvel: np.ndarray,
        sim_time: float,
        actuator_state: np.ndarray,
        controller_state: Dict[str, Any],
        task_params: Dict[str, Any],
        camera_base_params: Dict[str, Any],
        instruction: str,
        env_rng_state: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> InitialStateSnapshot:
        """Create a structured snapshot from current simulator state."""
        obj_dict = {k: np.asarray(v, dtype=float).tolist() for k, v in object_poses.items()}
        qpos_list = np.asarray(robot_qpos, dtype=float).tolist()
        qvel_list = np.asarray(robot_qvel, dtype=float).tolist()
        act_list = np.asarray(actuator_state, dtype=float).tolist()
        
        dummy = InitialStateSnapshot(
            snapshot_id="temp",
            task_id=task_id,
            object_poses=obj_dict,
            robot_qpos=qpos_list,
            robot_qvel=qvel_list,
            sim_time=float(sim_time),
            actuator_state=act_list,
            controller_state=copy.deepcopy(controller_state),
            task_params=copy.deepcopy(task_params),
            camera_base_params=copy.deepcopy(camera_base_params),
            instruction=instruction,
            env_metadata=metadata or {},
            env_rng_state=env_rng_state
        )
        snap_id = f"init_{dummy.compute_hash()}"
        dummy.snapshot_id = snap_id
        return dummy

    @staticmethod
    def restore_to_env(env: Any, snapshot: InitialStateSnapshot) -> bool:
        """Hard-restore a physical simulator environment to the exact snapshot state."""
        if hasattr(env, "set_state_snapshot"):
            env.set_state_snapshot(snapshot)
            return True
        elif hasattr(env, "reset_to_state"):
            env.reset_to_state(
                object_poses={k: np.array(v) for k, v in snapshot.object_poses.items()},
                robot_qpos=np.array(snapshot.robot_qpos),
                robot_qvel=np.array(snapshot.robot_qvel),
                task_params=snapshot.task_params
            )
            return True
        else:
            if hasattr(env, "robot_qpos"):
                env.robot_qpos = np.array(snapshot.robot_qpos, copy=True)
            if hasattr(env, "robot_qvel"):
                env.robot_qvel = np.array(snapshot.robot_qvel, copy=True)
            if hasattr(env, "sim_time"):
                env.sim_time = snapshot.sim_time
            if hasattr(env, "object_poses"):
                env.object_poses = {k: np.array(v, copy=True) for k, v in snapshot.object_poses.items()}
            return True
