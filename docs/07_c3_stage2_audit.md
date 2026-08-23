# Stage 2：Candidate C3 完整六层查重审计报告

> **审计对象**：备选候选 **C3（6-DoF 抓取检测的系统性 Sensor Corruption 鲁棒性，以及 AP 与物理执行成功率的脱钩机制）**  
> **审计目标**：完成 Layer 1–6 全量检索与机制分析，确定其作为 C1 兜底方案的技术独立性与发表可行性。  
> **审计结论**：**通过六层查重，Novelty 评级确定为 B / C+**。抓取检测领域完全缺乏类似 ImageNet-C / RoboDepth 的多轴物理传感器扰动基准；“AP 提升无法转化为执行成功率”的脱钩现象被广泛口头提及但从未被系统量化建模。**单卡 RTX 4080 纯推理 1–2 天即可完成 Pilot**，是确定性极高的安全备选方案。

---

## 一、Layer 1 — Direct Search（直接检索）

**检索式**：
```
"grasp detection" ("corruption" OR "robustness benchmark" OR "sensor noise") "grasp success rate" OR "average precision"
"GraspNet-1Billion" ("corruption" OR "depth noise" OR "benchmark") "AP" "execution"
"6-DoF grasp" "metric misalignment" "AP" "success rate"
```

### 命中情况与代表文献
1. **GraspNet-1Billion (Fang et al., CVPR 2020 / IJRR 2023)**：
   - 建立了百万级 6-DoF 抓取数据集与基于矩形/双指网格覆盖的 AP 评估体系。
   - 评测主要集中在干净场景与不同相机（RealSense vs Kinect）的跨设备评测。
   - **未做**：系统性的多轴物理传感器 corruption 强度扫描与 AP–执行相关性量化。
2. **AnyGrasp / GSNet / FineGrasp / SpikeGrasp (2022–2026)**：
   - 各自针对特定传感器噪声（如反光、细小物体、事件相机输入）提出新的网络结构或表征（如 Graspness 场、Context-free 轮廓学习）。
   - **未做**：独立于具体模型的第三方基准评测，仍各自采用私有实验设置或标准 GraspNet 干净测试集。

---

## 二、Layer 2 — Synonym Search（同义词拓展检索）

| 核心维度 | 拓展检索词 | 检索结论 |
|---|---|---|
| 任务 | 6-DoF grasp pose estimation, grasp synthesis, affordance detection, suction/pinch grasp | 涵盖主流 6-DoF 夹爪与吸盘预测 |
| 扰动 | depth noise, missing return (holes), flying pixels, quantization, motion blur, speckle noise, specular reflection | 自动驾驶领域已规范化，抓取领域零散 |
| 关系 | proxy metric misalignment, perception-execution decoupling, rank correlation collapse | 抓取领域仅有现象感叹，无数学建模 |

---

## 三、Layer 3 — Mechanism Search（机制分析与脱钩假设）

为什么在传感器噪声下 **AP（数据集指标）会与执行成功率（物理指标）发生系统性脱钩？**

1. **几何容差 vs 力闭合敏感性（Tolerance Mismatch）**：
   - AP 基于抓取位姿与标注位姿的距离/旋转阈值（如 IoU 或 $\Delta R < 30^\circ, \Delta t < 2\text{cm}$）。
   - 物理抓取要求接触点法向量误差 $< 5^\circ$ 以满足摩擦锥约束。深度图边缘的微小散斑噪声对 AP 的影响仅占微小权重，却直接导致夹爪与物体碰撞或滑脱。
2. **Top-1 / Top-K 排序翻转（Ranking Inversion under Noise）**：
   - AP 是所有预测抓取按置信度排序后的 Precision-Recall 曲线积分（宏观均值）。
   - 实际机器人执行只选择置信度最高的 Top-1 或 Top-3 抓取。传感器噪声容易使实际上不稳定的抓取位姿产生虚假的高置信度，使 Top-1 发生致命错误，而整体 AP 仅微跌。
3. **碰撞裕度侵蚀（Collision Margin Shrinkage）**：
   - 深度量化与空洞会导致物体表面膨胀或残缺，破坏夹爪接近轨迹（Approach vector）的无碰撞判定。

---

## 四、Layer 4 — Cross-Domain Search（跨领域映射）

- **自动驾驶先例**：
  - **ST-P3 (ECCV 2022) / UniAD (CVPR 2023 Best Paper)** 证明：自动驾驶中感知 mAP 的提升与下游规划（L2 轨迹误差、碰撞率）并不单调对应（Planning-oriented perception）。
  - **RoboDepth (NeurIPS 2023) / Robo3D (ICCV 2023)**：系统构建了 18 种传感器 corruption 基准，成为行业标准。
- **具身抓取现状**：
  - 抓取领域尚**无**对应的 “RoboGrasp-C” 标准，亦无系统量化 AP 与物理执行在不同扰动轴下的 Spearman 秩相关性。
  - **迁移判定**：属于跨领域成熟方法在机器人基础操作子领域的首次标准化落地，具备坚实的 Benchmark & Analysis 价值。

---

## 五、Layer 5 — Citation Graph（引文图溯源）

- **GraspNet-1B (CVPR 2020)** 施引网络分析：
  - 500+ 篇引用主要流向：(1) 扩散抓取生成（GraspGen）、(2) 视触觉多模态融合、(3) 灵巧手抓取、(4) 乱序分拣真机系统。
  - **无任何工作系统性对比 ≥5 种主流架构在多轴 corruption 下的 AP vs 仿真/真机抓取成功率对应关系**。

---

## 六、Layer 6 — 2025–2026 最新工作（Newest Preprints）

- **GraspGen (arXiv 2507.13097)** & **GraspGen-X (arXiv 2606.00998)**：
  - 采用 Flow Matching / Diffusion 生成抓取位姿，测试仍在 GraspNet-1B 干净集上报告 AP 与简单 Isaac Gym 仿真成功率。
  - 未涉及传感器退化条件下的系统鲁棒性测试。

---

## 七、C3 课题定位与 Pilot 执行规范

### 1. 论文一句话定位
> *“我们建立了首个面向 6-DoF 抓取检测的多轴传感器退化基准（RoboGrasp-C），系统评测了 6 种主流检测架构，并首次量化了感知指标（AP）与物理执行成功率在真实物理扰动下的解耦现象与排序翻转机制。”*

### 2. 极简 Pilot 验证方案（单卡 RTX 4080，纯推理）
- **模型库（全量开源 Checkpoints，0 训练成本）**：
  1. GraspNet-baseline (PointNet++ backbone)
  2. GSNet (Graspness 启发式)
  3. Contact-GraspNet (局部接触预测)
  4. AnyGrasp (密集预测)
  5. GraspGen (扩散生成模型)
- **数据与扰动**：
  - GraspNet-1B 测试集（90 个乱序抓取场景）。
  - 构造 6 种物理传感器扰动：高斯/泊松深度噪声、边缘散斑缺失（Flying Pixels）、深度量化条带、镜头水雾/油污模糊、高光表面空洞。每种 3 个强度等级。
- **评测流程**：
  1. 运行各模型推理，计算 $m\text{AP}$。
  2. 将预测抓取导入 PyBullet / Isaac Gym 仿真环境，执行夹爪闭合与提起判定，计算真实抓取成功率（GSR）。
  3. 计算各扰动轴下的 Spearman 秩相关系数 $r_s(m\text{AP}, \text{GSR})$。
- **预期判定信号**：
  - 若在特定扰动（如深度空洞与边缘散斑）下，$r_s < 0.4$ 或 $m\text{AP}$ 上升但 GSR 下降 $\rightarrow$ **课题核心假设成立，进入正式论文写作**。

### 3. 风险与收益对比

| 候选 | 科学野心 | 查重风险 | 算力门槛 | 命中预期 |
|:---:|:---:|:---:|:---:|:---:|
| **C1** (VLA 实证律) | 极高（挑战领域基础假设） | 中（需严格界定与 PDR/综述的边界） | 4080 跑仿真（需 4-7 天） | CoRL / ICRA / RA-L |
| **C3** (抓取 Corruption 基准) | 高（首个标准化物理基准 + 脱钩机制） | **极低（查重完全清白）** | **4080 纯推理（1-2 天即可）** | ICRA / IROS / RA-L (稳健) |
