"""
Policy Internal State & Buffer Manager (Dual-State Management)
==============================================================
Manages ACT action chunking queues, temporal ensembling buffers, observation history,
and policy inference RNG states to guarantee pi_0^{clean} == pi_0^{OOD}.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
import copy
import numpy as np


@dataclass
class PolicyStateSnapshot:
    """Snapshot of policy model internal state before episode execution."""
    action_chunk_buffer: List[np.ndarray] = field(default_factory=list)
    temporal_ensemble_step: int = 0
    observation_history: List[Dict[str, Any]] = field(default_factory=list)
    rng_state: Optional[Any] = None
    inference_step_count: int = 0


class PolicyStateManager:
    """Manages policy state resets and snapshots for clean/OOD paired isolation."""

    @staticmethod
    def reset_policy(policy: Any) -> None:
        """Reset all temporal buffers and internal action queues to initial state."""
        if hasattr(policy, "reset"):
            policy.reset()
        if hasattr(policy, "action_buffer"):
            policy.action_buffer.clear()
        if hasattr(policy, "temporal_ensemble_step"):
            policy.temporal_ensemble_step = 0
        if hasattr(policy, "obs_history"):
            policy.obs_history.clear()
        if hasattr(policy, "step_count"):
            policy.step_count = 0

    @staticmethod
    def capture_policy_state(policy: Any) -> PolicyStateSnapshot:
        """Capture current policy internal buffers."""
        act_buf = copy.deepcopy(getattr(policy, "action_buffer", []))
        te_step = getattr(policy, "temporal_ensemble_step", 0)
        obs_hist = copy.deepcopy(getattr(policy, "obs_history", []))
        rng = getattr(policy, "rng", None)
        rng_state = rng.get_state() if rng is not None else None
        steps = getattr(policy, "step_count", 0)
        
        return PolicyStateSnapshot(
            action_chunk_buffer=act_buf,
            temporal_ensemble_step=te_step,
            observation_history=obs_hist,
            rng_state=rng_state,
            inference_step_count=steps
        )

    @staticmethod
    def restore_policy_state(policy: Any, snapshot: PolicyStateSnapshot) -> None:
        """Restore policy buffers to a captured snapshot."""
        if hasattr(policy, "action_buffer"):
            policy.action_buffer = copy.deepcopy(snapshot.action_chunk_buffer)
        if hasattr(policy, "temporal_ensemble_step"):
            policy.temporal_ensemble_step = snapshot.temporal_ensemble_step
        if hasattr(policy, "obs_history"):
            policy.obs_history = copy.deepcopy(snapshot.observation_history)
        if hasattr(policy, "rng") and snapshot.rng_state is not None:
            policy.rng.set_state(snapshot.rng_state)
        if hasattr(policy, "step_count"):
            policy.step_count = snapshot.inference_step_count
