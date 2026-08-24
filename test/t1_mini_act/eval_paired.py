"""
Multi-Task Paired Clean/OOD Evaluator with Dual Environment & Policy Reset
==========================================================================
Orchestrates:
1. Multi-Task Validation Set Clean Rollouts: Checkpoint capability selection per task;
2. Multi-Task Calibration / Smoke Set Paired Rollouts: Evaluates Clean (S_{0,j}) and OOD (T_d(S_{0,j}))
   with full dual reset: StateManager.restore_to_env() + ACTPolicyAdapter.reset().
3. Uses PerturbationBank for 100% identical frozen realizations delta_{j,d} across all checkpoints.
"""

from typing import List, Dict, Any, Tuple, Optional
import numpy as np
import time
import copy

from config import ExperimentConfig
from state_manager import InitialStateSnapshot, StateManager
from policy_state_manager import PolicyStateManager
from perturbations import PerturbationBank, PerturbationRealization
from logger import GranularLogger, GranularEpisodeRecord
from split_manager import SplitManager
from adapters.libero_adapter import LiberoEnvAdapter
from adapters.act_adapter import ACTPolicyAdapter


class PairedEvaluator:
    """
    Executes Multi-Task Four-Set isolated evaluation with complete dual environment and policy resets.
    """

    def __init__(self, config: ExperimentConfig, logger: GranularLogger):
        self.config = config
        self.logger = logger
        
        # Instantiate environment adapters per task
        self.envs: Dict[str, LiberoEnvAdapter] = {
            t: LiberoEnvAdapter(task_id=t, seed=config.default_seed)
            for t in config.tasks
        }
        
        self.split_mgr = SplitManager(config=config)
        self.pert_bank = PerturbationBank(master_seed=config.default_seed)

    def evaluate_checkpoint_clean_val(self, policy: ACTPolicyAdapter, task_id: str) -> float:
        """Evaluate Clean SR on independent Validation Set for a specific task."""
        env = self.envs[task_id]
        val_snaps = self.split_mgr.get_validation_snapshots(task_id=task_id, env=env)
        successes = 0
        
        for idx, snapshot in enumerate(val_snaps):
            StateManager.restore_to_env(env, snapshot)
            ep_seed = int(self.config.default_seed * 10000 + idx)
            policy.reset(episode_seed=ep_seed)
            res, _ = policy.rollout(env, is_perturbed=False)
            successes += res
            
        return float(successes / len(val_snaps))

    def evaluate_smoke_set_paired(
        self,
        policy: ACTPolicyAdapter,
        task_id: str,
        clean_val_sr: float,
        perturbation_axis: str,
        severity: str = "medium"
    ) -> Dict[str, Any]:
        """
        Execute paired evaluation on Calibration / Smoke Set for (task_id, perturbation_axis).
        Retrieves identical perturbation realization delta_{j,d} from PerturbationBank.
        """
        env = self.envs[task_id]
        smoke_snaps = self.split_mgr.get_smoke_snapshots(task_id=task_id, env=env)
        n_episodes = len(smoke_snaps)
        
        y_clean_list = []
        y_ood_list = []
        
        t0 = time.time()
        for idx, snapshot in enumerate(smoke_snaps):
            # Shared paired episode ID across all checkpoints
            paired_ep_id = f"{task_id}_{snapshot.snapshot_id}_{perturbation_axis}_{severity}"
            ep_seed = int(self.config.default_seed * 50000 + idx)
            
            # Step 1: Clean Rollout from S_{0,j}
            StateManager.restore_to_env(env, snapshot)
            policy.reset(episode_seed=ep_seed)
            y_clean, len_clean = policy.rollout(env, is_perturbed=False)
            
            # Step 2: Retrieve frozen perturbation realization from Bank
            realization: PerturbationRealization = self.pert_bank.get_realization(
                snapshot=snapshot,
                env_context=env.current_context,
                axis_name=perturbation_axis,
                severity=severity
            )
            
            # Step 3: Restore perturbed state, reset policy with identical ep_seed, and rollout
            StateManager.restore_to_env(env, realization.perturbed_snapshot)
            env.current_context = copy.deepcopy(realization.perturbed_env_context)
            policy.reset(episode_seed=ep_seed)
            
            y_ood, len_ood = policy.rollout(
                env,
                is_perturbed=True,
                perturbation_axis=perturbation_axis,
                severity=severity
            )
            
            y_clean_list.append(y_clean)
            y_ood_list.append(y_ood)
            
            # Log full 20-field record
            record = GranularEpisodeRecord(
                model_family=self.config.model_family,
                training_seed=self.config.default_seed,
                checkpoint_id=policy.checkpoint_name,
                checkpoint_hash=policy.checkpoint_hash,
                clean_val_sr=clean_val_sr,
                split_id="calibration_smoke",
                paired_episode_id=paired_ep_id,
                task_id=task_id,
                initial_state_id=snapshot.snapshot_id,
                initial_state_hash=snapshot.compute_hash(),
                perturbation_axis=perturbation_axis,
                perturbation_severity=severity,
                perturbation_params=realization.applied_params,
                perturbation_seed=realization.actual_seed,
                clean_success=y_clean,
                ood_success=y_ood,
                clean_episode_length=len_clean,
                ood_episode_length=len_ood,
                env_version=self.config.env_version,
                policy_version=self.config.policy_version
            )
            self.logger.log_episode(record)
            
        elapsed_sec = time.time() - t0
        return {
            "task_id": task_id,
            "checkpoint": policy.checkpoint_name,
            "perturbation_axis": perturbation_axis,
            "y_clean": np.array(y_clean_list),
            "y_ood": np.array(y_ood_list),
            "wallclock_sec": elapsed_sec,
            "sec_per_episode": elapsed_sec / (2 * n_episodes)
        }
