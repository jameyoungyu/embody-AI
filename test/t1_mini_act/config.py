"""
Global Configuration for T1-mini ACT Experiment
================================================
Frozen specifications with explicit parameter distributions, collision rejection criteria,
and Four-Set physical isolation (Train / Validation / Calibration-Smoke / Frozen-Test).
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple
import numpy as np


# ==============================================================================
# 1. Capability Bins for Checkpoint Selection (Pre-frozen)
# Selection is strictly on Validation Clean SR BEFORE touching OOD.
# ==============================================================================
CAPABILITY_BINS_FULL: List[Tuple[float, float]] = [
    (0.25, 0.35),
    (0.40, 0.50),
    (0.55, 0.65),
    (0.68, 0.76),
    (0.78, 0.86),
    (0.88, 0.92),
    (0.93, 0.98),
]

T1_MINI_TARGET_CLEAN_SR: List[float] = [0.25, 0.45, 0.65, 0.80, 0.95]


# ==============================================================================
# 2. Perturbation Distribution & Operator Specifications (T_d)
# ==============================================================================
@dataclass
class CameraPerturbationDist:
    """Explicit distribution for perception-side camera viewpoint shift."""
    azimuth_range_deg: Tuple[float, float] = (-10.0, 10.0)      # U(-10, 10) deg
    elevation_range_deg: Tuple[float, float] = (-5.0, 5.0)       # U(-5, 5) deg
    pos_shift_range: Tuple[float, float] = (-0.03, 0.03)         # U(-3cm, 3cm) per axis


@dataclass
class LightingPerturbationDist:
    """Explicit distribution for lighting intensity scale."""
    intensity_scale_range: Tuple[float, float] = (0.4, 0.8)      # U(0.4, 0.8)


@dataclass
class ObjectPosePerturbationDist:
    """
    Explicit distribution for state-side object initial pose displacement.
    Includes workspace boundaries and collision rejection bounds.
    """
    dx_range: Tuple[float, float] = (-0.03, 0.03)                # U(-3cm, 3cm)
    dy_range: Tuple[float, float] = (-0.03, 0.03)                # U(-3cm, 3cm)
    dtheta_range_deg: Tuple[float, float] = (-20.0, 20.0)        # U(-20, 20) deg
    
    # Workspace validity boundaries [xmin, xmax, ymin, ymax]
    workspace_bounds: Tuple[float, float, float, float] = (0.05, 0.35, -0.25, 0.15)
    min_dist_to_obstacles: float = 0.04                          # Rejection threshold for collision


# ==============================================================================
# 3. Experiment Quotas & Four-Set Split Configuration
# ==============================================================================
@dataclass
class ExperimentConfig:
    model_family: str = "ACT"
    default_seed: int = 42
    env_version: str = "libero_v1.0"
    policy_version: str = "act_chunksize_10_v1"
    
    # Task definition
    task_suite_name: str = "LIBERO_Spatial"
    tasks: List[str] = field(default_factory=lambda: [
        "libero_spatial_pick_up_the_black_bowl",
        "libero_spatial_push_the_plate_to_the_front",
    ])
    
    # Four-Set Quotas (Strict physical isolation)
    val_episodes_per_checkpoint: int = 50          # Validation set (Checkpoint selection ONLY)
    smoke_episodes_per_cell: int = 100             # Calibration / Smoke set (T1-mini ONLY)
    frozen_test_episodes_per_cell: int = 200       # Frozen Test set (Untouched until T1-A)
    
    # Selected perturbation axes for T1-mini
    t1_mini_axes: List[str] = field(default_factory=lambda: [
        "camera_viewpoint",    # Perception-side
        "object_initial_pose"  # State-side
    ])
    t1_mini_severity: str = "medium"
    
    # Bootstrap CI config
    bootstrap_samples: int = 1000
    bootstrap_confidence: float = 0.95
    
    # Output paths
    output_dir: str = "experiments/t1_mini_act/results"
    log_csv_filename: str = "t1_mini_raw_episodes.csv"
    summary_report_filename: str = "T1_MINI_AUDIT_REPORT.md"
