# T1-mini-real: 真实 ACT + 真实 LIBERO 集成冒烟实验规范与准入规程

> **状态**：**已冻结（Protocol Frozen）**  
> **定位**：从 Synthetic Smoke 测试桩跨越到真实 ACT 权重与 LIBERO 物理仿真的**集成准入阶段（Integration Qualification）**  
> **核心原则**：**在通过真实状态恢复、真实观测扰动、真实 Checkpoint 能力跨度和非退化严重度验收之前，严禁访问 Frozen Test，严禁启动 3×7 T1-A 全量实验。**

---

## 一、三阶段项目执行全景（Three-Phase Progression）

```
┌────────────────────────────────────────────────────────┐
│ Phase 1: Synthetic Engineering Pipeline (已通过 ✓)     │
│ • 状态序列化与双重恢复逻辑自检                         │
│ • Perturbation Bank 跨 Checkpoint 冻结接口             │
│ • 20 字段 Provenance CSV 落盘与代数恒等式自检          │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│ Phase 2: T1-mini-real (真实 ACT + LIBERO 集成冒烟)     │
│ • 规模：1 Seed × 5 Checkpoints × 2 Tasks × 2 Axes      │
│ • 每 Cell 30~50 Paired States (总计 ~600 Rollouts)     │
│ • 目标：通过 5 项物理/感知/模型级集成门检              │
└───────────────────────────┬────────────────────────────┘
                            │ (全部 5 项 PASS 后)
                            ▼
┌────────────────────────────────────────────────────────┐
│ Phase 3: Formal T1-A 受控实验 (正式论文数据产出)       │
│ • 规模：3 Seeds × 7 Capability Bins × 4 Tasks × 3 Axes │
│ • 执行：独立脚本 run_t1_a_formal.py                    │
│ • 访问：首次且仅一次加载 Frozen Test Set (200 eps/cell)│
└────────────────────────────────────────────────────────┘
```

---

## 二、T1-mini-real 必须通过的 5 大集成门检（Five Integration Gates）

| 门检项 | 核验目标 | 判据与容差 |
|---|---|---|
| **Gate 1: Replay Stability** | 真实 MuJoCo $S_0$ 状态恢复稳定性 | 相同 $S_0$ 下重复 3 次 Clean Rollout，动作轨迹与终止结果 100% 确定性一致 |
| **Gate 2: Camera Obs Shift** | 真实相机外参扰动产生纯感知偏移 | 渲染 RGB 图像发生显著差异（$\|I_{\text{clean}} - I_{\text{camera}}\|_1 > 0$），而物理状态严格不变（$\|qpos\|_{\infty}=0, \|x_{\text{obj}}\|_{\infty}=0$） |
| **Gate 3: Object Pose Isolation** | 目标物体扰动隔离性与四元数乘法 | 仅指定目标物体发生位姿变换（$q_{\text{new}} = q_\Delta \otimes q_{\text{base}}$），机械臂与其他物体物理位姿差异为 0 |
| **Gate 4: Severity Non-Degeneracy** | 真实环境扰动严重度非极端化 | 在所测 Checkpoint 下，$p_{\text{OOD}}$ 既不全量坍塌至 0%（地板），也不与 Clean 完全相等（天花板），处于 $[5\%, 85\%]$ 有效区间 |
| **Gate 5: Capability Span** | 真实 ACT Checkpoint 具有有效能力跨度 | 选取的一组真实训练 Checkpoint 在 Validation 集上的 Clean SR 跨度 $\ge 35\%$ |

---

## 三、关键实现与坐标/四元数规范

### 1. 多任务与物体映射字典（Task-to-Target Mapping）
```python
TASK_TARGET_OBJECTS = {
    "libero_spatial_pick_up_the_black_bowl": "black_bowl",
    "libero_spatial_push_the_plate_to_the_front": "plate",
    "libero_object_pick_up_the_alphabet_soup": "alphabet_soup",
    "libero_goal_open_the_middle_drawer": "middle_drawer"
}
```

### 2. 四元数复合运算规范（Quaternion Composition: $q_{\text{new}} = q_\Delta \otimes q_{\text{base}}$）
针对 Robosuite 使用的 $[x, y, z, w]$ 格式，偏航角（Yaw）旋转 $\Delta \theta$ 算子为：
$$q_\Delta = \left[0, 0, \sin\left(\frac{\Delta \theta}{2}\right), \cos\left(\frac{\Delta \theta}{2}\right)\right]$$
复合公式（Hamilton 乘法）：
$$w_{\text{new}} = w_1 w_2 - x_1 x_2 - y_1 y_2 - z_1 z_2$$
$$x_{\text{new}} = w_1 x_2 + x_1 w_2 + y_1 z_2 - z_1 y_2$$
$$y_{\text{new}} = w_1 y_2 - x_1 z_2 + y_1 w_2 + z_1 x_2$$
$$z_{\text{new}} = w_1 z_2 + x_1 y_2 - y_1 x_2 + z_1 w_2$$
严禁直接覆盖原物体的 orientation 四元数。

### 3. 协议级隔离设计（Protocol-Level Isolation）
- `SplitManager` 在初始化时不生成 `frozen_test_snapshots`（`self.frozen_test_snapshots = None`）；
- `run_t1_mini_real.py` 专用冒烟运行器，根本不包含任何加载 Frozen Test 的代码；
- `run_t1_a_formal.py` 专用正式运行器，仅在所有门检通过后由研究员手动触发。
