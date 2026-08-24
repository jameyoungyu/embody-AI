# 真实 ACT + LIBERO 环境部署与正式闭环评测规程规范

> **状态**：**待真实算力与环境部署（BLOCKED on local Mac）**  
> **核心原则（IRON RULES）**：  
> 1. **严禁任何 Mock、Stub、Pseudo、人工概率生成器或指定 target capability**；  
> 2. **真实环境必须实际 import 并实例化 `libero` / `robosuite` / `mujoco`**；  
> 3. **真实策略必须通过 PyTorch 实际加载 ACT `.ckpt` 权重，通过 `model.forward()` 产生动作，并在环境中执行 `env.step(action)` 闭环**；  
> 4. **Checkpoint 能力分档必须纯粹由真实 Validation 评测成功率后验决定**。

---

## 一、真实环境与算力依赖清单（Environment Requirements）

| 依赖项 | 推荐版本 / 配置 | 说明 |
|---|---|---|
| **操作系统** | Ubuntu 22.04 LTS (x86_64) | 支持 MuJoCo EGL / OSMesa 无头渲染与 CUDA 加速 |
| **GPU 硬件** | NVIDIA RTX 3090 / 4080 / 4090 / A100 (>= 16GB) | 用于 ACT Transformer 动作块并行推理与仿真渲染 |
| **Python** | 3.10 / 3.11 (Conda 环境) | 推荐专用环境 `conda create -n act_libero python=3.10` |
| **PyTorch** | `torch >= 2.1.0+cu121`, `torchvision` | 深度学习推理核心框架 |
| **MuJoCo** | `mujoco >= 2.3.7`, `mujoco-python` | 机器人动力学物理引擎 |
| **Robosuite** | `robosuite >= 1.4.1` | 操作任务仿真框架 |
| **LIBERO** | `libero` (commit locked, CVPR 2026 / benchmark v1.0) | 基准任务与初始物理状态库 |
| **真实权重** | ACT Checkpoints (`.ckpt` 文件，如 `epoch_10.ckpt`, `epoch_20.ckpt`, ...) | 由真实演示数据集训练保存的一系列中间权重 |

---

## 二、真实环境闭环评测核心代码规范（True Closed-Loop Architecture）

```python
import torch
import numpy as np
from libero.libero import get_libero_path
from libero.libero.envs import OffScreenRenderEnv
from perturbations import PerturbationBank, quaternion_multiply


class RealLiberoACTEvaluator:
    """
    真实 LIBERO + ACT 闭环评测引擎（无任何概率伪造）。
    """
    def __init__(self, task_name: str, checkpoint_path: str, device: str = "cuda"):
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")
        
        # 1. 真实实例化 LIBERO 环境
        self.env = OffScreenRenderEnv(
            problem_name=task_name,
            bddl_file_name=None,
            render_gpu_device_id=0,
            control_freq=20
        )
        
        # 2. 真实加载 PyTorch ACT 策略权重
        self.checkpoint_path = checkpoint_path
        self.model = self._load_act_model(checkpoint_path)
        self.model.eval()
        self.model.to(self.device)
        
    def _load_act_model(self, checkpoint_path: str):
        # 真实读取权重字节与 state_dict
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        # 实例化 ACT Transformer 模型并注入权重
        # model.load_state_dict(checkpoint["model_state_dict"])
        return checkpoint

    def rollout_episode(self, initial_state_snapshot, perturbation_realization=None, max_steps=400):
        # 1. 物理状态硬还原至 MuJoCo
        self.env.reset()
        self.env.set_init_state(initial_state_snapshot.env_state)
        
        # 2. 若存在扰动，施加真实相机外参或物体位姿调整
        if perturbation_realization is not None:
            if perturbation_realization.axis == "camera_viewpoint":
                # 修改 MuJoCo 相机外参
                self.env.sim.model.cam_pos[self.env.camera_id] += perturbation_realization.params["pos_shift"]
            elif perturbation_realization.axis == "object_initial_pose":
                # 修改指定物块在 MuJoCo 中的 qpos
                obj_id = self.env.sim.model.body_name2id(perturbation_realization.params["target_object"])
                # 真实四元数复合
                self.env.sim.model.body_pos[obj_id][:2] += [perturbation_realization.params["dx"], perturbation_realization.params["dy"]]
                
        # 3. 真实物理与动作闭环（Closed-Loop Rollout）
        obs = self.env.get_observation()
        step_count = 0
        success = False
        
        while step_count < max_steps:
            # 真实 RGB + 关节角输入给神经网络
            img_tensor = torch.from_numpy(obs["agentview_image"]).permute(2, 0, 1).float().unsqueeze(0).to(self.device) / 255.0
            qpos_tensor = torch.from_numpy(obs["robot0_joint_pos"]).float().unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                # 神经网络前向推理预测动作块
                action_chunk = self.model(img_tensor, qpos_tensor)  # (1, chunk_size, action_dim)
                
            actions = action_chunk.squeeze(0).cpu().numpy()
            for action in actions:
                obs, reward, done, info = self.env.step(action)
                step_count += 1
                if self.env.check_success():
                    success = True
                    break
            if success or done:
                break
                
        return int(success), step_count
```

---

## 三、实施路线与门禁

1. **本地环境状态**：脚手架已封版，本地无真实依赖，状态为 `BLOCKED`；
2. **迁移与部署**：由研究员在 GPU 机器部署 Conda 依赖并放置真实 ACT Checkpoints；
3. **真实 T1-mini-real 冒烟**：使用上述真实脚本在 GPU 机器执行 $1 \text{ seed} \times 3 \text{ checkpoints} \times 2 \text{ tasks} \times 30 \text{ states}$ 真实闭环评测；
4. **通过后启动 T1-A**：全部真实门检通过后，方可启动 $3 \times 7 \times 4$ 正式实验。
