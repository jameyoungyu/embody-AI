"""
Expanded Granular Episode-Level Logger (20-Field Comprehensive Schema)
======================================================================
Records complete execution provenance:
- model_family, training_seed, checkpoint_id, checkpoint_hash, clean_val_sr;
- split_id, paired_episode_id (shared across checkpoints!), task_id, initial_state_id, initial_state_hash;
- perturbation_axis, perturbation_severity, perturbation_params (exact numeric values), perturbation_seed (actual seed);
- clean_success, ood_success, clean_episode_length, ood_episode_length;
- env_version, policy_version.
"""

from dataclasses import dataclass, asdict
import os
import csv
import json
from typing import List, Dict, Any, Optional


@dataclass
class GranularEpisodeRecord:
    """Full 20-field single paired test episode observation row."""
    model_family: str
    training_seed: int
    checkpoint_id: str
    checkpoint_hash: str
    clean_val_sr: float
    split_id: str
    paired_episode_id: str
    task_id: str
    initial_state_id: str
    initial_state_hash: str
    perturbation_axis: str
    perturbation_severity: str
    perturbation_params: Dict[str, Any]
    perturbation_seed: int
    clean_success: int
    ood_success: int
    clean_episode_length: int
    ood_episode_length: int
    env_version: str
    policy_version: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class GranularLogger:
    """Manages CSV logging with full audit provenance."""

    HEADER = [
        "model_family", "training_seed", "checkpoint_id", "checkpoint_hash", "clean_val_sr",
        "split_id", "paired_episode_id", "task_id", "initial_state_id", "initial_state_hash",
        "perturbation_axis", "perturbation_severity", "perturbation_params", "perturbation_seed",
        "clean_success", "ood_success", "clean_episode_length", "ood_episode_length",
        "env_version", "policy_version"
    ]

    def __init__(self, output_path: str):
        self.output_path = output_path
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        self.records: List[GranularEpisodeRecord] = []
        
        # Initialize CSV header if not present
        if not os.path.exists(self.output_path):
            with open(self.output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(self.HEADER)

    def log_episode(self, record: GranularEpisodeRecord) -> None:
        """Append a single paired episode record."""
        self.records.append(record)
        with open(self.output_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                record.model_family,
                record.training_seed,
                record.checkpoint_id,
                record.checkpoint_hash,
                f"{record.clean_val_sr:.4f}",
                record.split_id,
                record.paired_episode_id,
                record.task_id,
                record.initial_state_id,
                record.initial_state_hash,
                record.perturbation_axis,
                record.perturbation_severity,
                json.dumps(record.perturbation_params, sort_keys=True),
                record.perturbation_seed,
                record.clean_success,
                record.ood_success,
                record.clean_episode_length,
                record.ood_episode_length,
                record.env_version,
                record.policy_version
            ])

    def get_records(self) -> List[GranularEpisodeRecord]:
        return self.records

    @classmethod
    def load_from_csv(cls, csv_path: str) -> List[GranularEpisodeRecord]:
        """Load records from existing CSV file."""
        records = []
        if not os.path.exists(csv_path):
            return records
            
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(GranularEpisodeRecord(
                    model_family=row.get("model_family", "ACT"),
                    training_seed=int(row.get("training_seed", 42)),
                    checkpoint_id=row["checkpoint_id"],
                    checkpoint_hash=row["checkpoint_hash"],
                    clean_val_sr=float(row["clean_val_sr"]),
                    split_id=row.get("split_id", row.get("eval_split", "calibration_smoke")),
                    paired_episode_id=row["paired_episode_id"],
                    task_id=row["task_id"],
                    initial_state_id=row.get("initial_state_id", row["paired_episode_id"].split("_")[3] if len(row["paired_episode_id"].split("_")) > 3 else "s0"),
                    initial_state_hash=row["initial_state_hash"],
                    perturbation_axis=row["perturbation_axis"],
                    perturbation_severity=row.get("perturbation_severity", row.get("severity", "medium")),
                    perturbation_params=json.loads(row["perturbation_params"]) if row.get("perturbation_params") else {},
                    perturbation_seed=int(row.get("perturbation_seed", 42)),
                    clean_success=int(row["clean_success"]),
                    ood_success=int(row["ood_success"]),
                    clean_episode_length=int(row.get("clean_episode_length", row.get("clean_step_count", 0))),
                    ood_episode_length=int(row.get("ood_episode_length", row.get("ood_step_count", 0))),
                    env_version=row.get("env_version", "libero_mujoco_2.3.7"),
                    policy_version=row.get("policy_version", "act_pytorch_cuda")
                ))
        return records
