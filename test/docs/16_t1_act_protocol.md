# T1: 族内受控实验方案（ACT 优先路线与执行规范）

> **状态**：**已冻结（Protocol Frozen）**  
> **前置依赖**：T0 概念审计通过、T2-PRE 预试验完成归档（`test/`）  
> **核心模型族**：**ACT (Action Chunking with Transformers)**  
> **计算环境**：单卡 NVIDIA RTX 4080 (16GB)

---

## 一、三大正式实验细节冻结（Protocol Freezes）

### 1. 显式物理状态还原（Explicit Initial State Restoration: $S_{0,j}^{\text{clean}} = S_{0,j}^{\text{OOD}}$）
- **禁止事项**：严禁仅依赖 `seed_clean = seed_OOD`（由于环境内部在不同扰动下可能发生非对称的随机数消费，单纯 seed 无法保证物理等价）。
- **执行规范**：每个 episode 评测前必须显式序列化并还原以下完整初始物理状态快照 $S_{0,j}$：
  - `object_poses`（所有被操作物体与干扰物的位姿 $[x, y, z, q_w, q_x, q_y, q_z]$）
  - `robot_initial_joint_state`（机械臂与夹爪初始关节位置及速度）
  - `environment_state`（MuJoCo / PyBullet 内部仿真器状态快照）
  - `task_parameters`（桌面布局与目标区域定义）
  - `camera_parameters`（默认相机内参外参，扰动仅在 OOD 条件下施加偏移）
  - `language_instruction`（配对的文本指令）

### 2. 严格三集隔离与 Checkpoint 无偏预筛选（Triple-Set Isolation）
严格杜绝后验挑点（No Selection-on-Outcome）：
```
                 ┌─────────────────────────────────────────────────────────┐
                 │           严格三集物理隔离工作流 (Triple-Set Pipeline)    │
                 └───────────────────────────┬─────────────────────────────┘
                                             │
      ┌──────────────────────────────────────┼──────────────────────────────────────┐
      ▼                                      ▼                                      ▼
┌───────────────────────────┐  ┌───────────────────────────┐  ┌───────────────────────────┐
│ 1. Training Set           │  │ 2. Validation Set         │  │ 3. Frozen Test Set        │
│ (训练轨迹采集)             │  │ (能力分档选点专用)        │  │ (配对 Clean/OOD 评测)     │
├───────────────────────────┤  ├───────────────────────────┤  ├───────────────────────────┤
│ • 标准演示数据训练        │  │ • 独立初始状态集合        │  │ • 严格隔离的初始状态集合  │
│ • 密集保存中间 Checkpoints│  │ • 仅测 Clean SR           │  │ • 执行配对评测            │
│   (M_5k, M_10k, ... M_80k)│  │ • 严格按 7 个预设 Bin 选点│  │ • 不参与任何选点决策      │
└───────────────────────────┘  └───────────────────────────┘  └───────────────────────────┘
```
- **预设 7 个能力区间 Bin**：
  $$[0.25, 0.35), [0.40, 0.50), [0.55, 0.65), [0.68, 0.76), [0.78, 0.86), [0.88, 0.92), [0.93, 0.98)$$
- **选点规则**：在每个 Bin 中选取距离中心值最近的 Checkpoint。**严禁在观测 OOD 结果后挑选或替换 Checkpoint**。

### 3. 三维互补鲁棒性指标体系（Complementary Robustness Quantities）
论文统一报告三个层级的互补物理度量，回答*“不同度量随能力演化究竟测量了什么”*：
1. **绝对部署成功率**：$p_{\text{OOD}}$（评估下游真实任务完成率）
2. **名义保持率 (Retention Ratio)**：$R = \frac{p_{\text{OOD}}}{p_{\text{clean}}}$（对应传统 PDR $= 1 - R$ 体系）
3. **配对破坏率 (Paired Disruption Rate)**：
   $$D = P(Y_{\text{OOD}} = 0 \mid Y_{\text{clean}} = 1) = \frac{\sum_j \mathbb{I}(Y^{\text{clean}}_j = 1, Y^{\text{OOD}}_j = 0)}{\sum_j \mathbb{I}(Y^{\text{clean}}_j = 1)}$$
   *（直接刻画原本能完成的任务中，有多少被环境扰动破坏）*

---

## 二、第一阶段执行策略：T1-mini 冒烟排查跑（Sanity Run）

在启动 full $3 \times 7$ 矩阵前，必须先执行 **T1-mini 冒烟实验**以校验整个软硬件与评测管线。

### T1-mini 规格配置：
- **模型**：ACT (1 training seed)
- **Checkpoint 采样**：5 个能力梯度（$p_{\text{clean}} \approx [0.35, 0.50, 0.65, 0.80, 0.92]$）
- **扰动轴（2 轴）**：
  1. **视觉轴 (Visual)**：Camera Viewpoint / Lighting Jitter
  2. **状态轴 (Physical/State)**：Initial Object Pose Perturbation
- **样本规模**：每个 Checkpoint 评测 $100 \sim 150$ 组严格配对 episodes

### T1-mini 验收清单（Pass Criteria）：
- [ ] **状态还原一致性**：验证 clean 与 OOD 的初始状态在物理引擎中 $100\%$ 无缝复现；
- [ ] **能力跨度有效性**：验证 Checkpoint 池成功拉出 $\ge 50$ 个百分点的 clean 梯度；
- [ ] **扰动强度适中性**：验证 OOD 成功率未发生全量跌 0（近地板）或全量无损（天花板）；
- [ ] **单 episode 吞吐实测**：获取 RTX 4080 下 ACT 推理的精确秒级墙钟时间，锁定后续全量排期。

---

## 三、后续推进梯队

1. **T1-A (主识别实验)**：ACT ($3 \text{ seeds} \times 7 \text{ capability bins} = 21 \text{ points}$)
2. **T1-B (跨族复现)**：Diffusion Policy ($3 \text{ seeds} \times 5 \text{ capability bins} = 15 \text{ points}$)
3. **T2 (大模型与干预验证)**：VLA 架构 (SmolVLA / OpenVLA) + Held-out Robust Interventions
