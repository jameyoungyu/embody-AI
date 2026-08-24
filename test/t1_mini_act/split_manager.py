"""
Four-Set Physical Isolation Manager
====================================
Enforces strict separation across:
1. Validation Set: Used EXCLUSIVELY for checkpoint capability bin selection.
2. Calibration / Smoke Set: Used EXCLUSIVELY for T1-mini-real (integration smoke test & calibration).
3. Frozen Test Set: Strictly isolated and NOT instantiated during T1-mini, reserved for formal T1-A.
4. Train Set: Training trajectories and demonstrations.
"""

from typing import List, Dict, Any, Optional
import numpy as np
from state_manager import InitialStateSnapshot, StateManager
from config import ExperimentConfig


class SplitManager:
    """
    Manages generation, isolation, and access control for initial physical state sets across multiple tasks.
    Enforces protocol-level isolation: Frozen Test is NEVER instantiated during T1-mini initialization.
    """

    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.base_seed = config.default_seed

        # Task-indexed snapshot libraries (Validation and Smoke ONLY)
        self._val_snapshots: Dict[str, List[InitialStateSnapshot]] = {}
        self._smoke_snapshots: Dict[str, List[InitialStateSnapshot]] = {}
        
        # Frozen test set is strictly None on init (Protocol-level isolation)
        self._frozen_test_snapshots: Optional[Dict[str, List[InitialStateSnapshot]]] = None

    def _generate_task_split(self, env: Any, task_id: str, split_name: str, offset: int, n_episodes: int) -> List[InitialStateSnapshot]:
        """Generate deterministic physical state snapshots for a designated task and split."""
        snapshots = []
        for i in range(n_episodes):
            ep_idx = offset + i
            snap = env.generate_initial_snapshot(episode_idx=ep_idx)
            snap.task_id = task_id
            snap.env_metadata["split_id"] = split_name
            snap.env_metadata["split_episode_index"] = i
            snapshots.append(snap)
        return snapshots

    def get_validation_snapshots(self, task_id: str, env: Any) -> List[InitialStateSnapshot]:
        """Validation snapshots for checkpoint capability selection ONLY (per task)."""
        if task_id not in self._val_snapshots:
            self._val_snapshots[task_id] = self._generate_task_split(
                env=env,
                task_id=task_id,
                split_name="validation",
                offset=10000,
                n_episodes=self.config.val_episodes_per_checkpoint
            )
        return self._val_snapshots[task_id]

    def get_smoke_snapshots(self, task_id: str, env: Any) -> List[InitialStateSnapshot]:
        """Calibration / Smoke snapshots for T1-mini ONLY (per task)."""
        if task_id not in self._smoke_snapshots:
            self._smoke_snapshots[task_id] = self._generate_task_split(
                env=env,
                task_id=task_id,
                split_name="calibration_smoke",
                offset=20000,
                n_episodes=self.config.smoke_episodes_per_cell
            )
        return self._smoke_snapshots[task_id]

    def load_frozen_test_snapshots(self, task_id: str, env: Any, permission: str = "") -> List[InitialStateSnapshot]:
        """
        Frozen Test snapshots.
        Protected access: Strictly isolated; only callable during formal T1-A execution.
        """
        if permission != "FORMAL_T1_A_EXECUTION":
            raise PermissionError(
                "Access Denied: Frozen Test Set is strictly isolated and cannot be accessed "
                "during T1-mini calibration or checkpoint selection."
            )
        if self._frozen_test_snapshots is None:
            self._frozen_test_snapshots = {}
        if task_id not in self._frozen_test_snapshots:
            self._frozen_test_snapshots[task_id] = self._generate_task_split(
                env=env,
                task_id=task_id,
                split_name="frozen_test",
                offset=50000,
                n_episodes=self.config.frozen_test_episodes_per_cell
            )
        return self._frozen_test_snapshots[task_id]
