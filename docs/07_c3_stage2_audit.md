# Stage 2：Candidate C3 完整六层查重与 Fast-Kill Pilot 方案

> **审计对象**：备选候选 **C3（6-DoF 抓取检测的系统性 Sensor Corruption 鲁棒性，以及 AP 与物理执行成功率的脱钩机制）**  
> **审计结论**：**Novelty 确定为 Level C**（邻近工作存在，核心问题收窄为：系统多轴传感器 corruption 扫描下 AP 与物理执行成功率的秩相关崩溃行为）。  
> **重要认知修正**：自动驾驶先例（Philion et al. 2020 / 2308.12779）表明离线检测指标与闭环下游通常存在中高度相关（~0.78），因此 C3 的“脱钩假设”面临较强的反向先验。**C3 Pilot 的定位变更为“快速证伪（Fast-Kill）”，而非高胜率备胎**。

---

## 一、六层查重执行细节（Layer 1–6）

### Layer 1 — Direct Search（直接检索）
- 检索式：`"grasp detection" ("corruption" OR "robustness benchmark" OR "sensor noise") "grasp success rate" OR "average precision"`
- 发现：GraspNet-1B（CVPR 2020 / IJRR 2023）、AnyGrasp、GSNet、FineGrasp 均在干净数据集或单一噪声条件下报告 $m\text{AP}$ 与仿真/真机抓取成功率。
- **缺口**：无标准化的类似 ImageNet-C / RoboDepth 的多轴物理传感器 corruption 退化谱基准。

### Layer 2 — Synonym Search（同义词检索）
- 检索词：6-DoF grasp pose estimation, depth missing holes, flying pixels, proxy metric misalignment, ranking inversion under sensor noise.
- 发现：社区存在“仿真/离线评测与实际物理抓取不一致”的定性讨论，但缺乏跨模型、多扰动轴的定量相关性研究。

### Layer 3 — Mechanism Search（抓取特异性脱钩机制）
C3 不能依赖通用先验，必须建立抓取特有的物理机制论证：
1. **几何容差 vs 力闭合敏感性（Tolerance Mismatch）**：AP 采用宏观距离/角度容差（如 $\Delta t < 2\text{cm}, \Delta R < 30^\circ$），而力闭合摩擦锥对接触法向量误差极度敏感（$<5^\circ$）。边缘散斑噪声轻微影响 AP，却直接破坏法向量导致打滑。
2. **Top-1 / Top-K 排序翻转（Ranking Inversion）**：AP 是全局 PR 曲线积分，而机器人执行只取 Top-1。深度传感器伪影极易产生“虚假高置信度”的不稳定抓取，使 Top-1 发生致命错误。
3. **碰撞裕度侵蚀**：深度量化与空洞导致物体几何残缺，使规划器误判接近轨迹。

### Layer 4 — Cross-Domain Search（跨领域先例纠偏）
- **事实纠偏**：
  - 自动驾驶中感知与下游控制指标研究的奠基工作是 **Philion et al. (arXiv:2004.08745, ECCV 2020, PKL)**，而非端到端架构（ST-P3/UniAD）。
  - **arXiv:2308.12779 (ICCVW 2023)** 实证表明：3D 目标检测指标（mAP / NDS）与闭环驾驶评分/碰撞数的相关性达 **0.77 ~ 0.78**。
- **先验警示**：邻近领域给出的实证先验是“指标与执行相关性尚可”，因此 C3 的假设 $H_2$（秩相关崩到 $<0.4$）失败概率上升。

### Layer 5 — Citation Graph（引文图）
- GraspNet-1B 施引文献（如 DexGraspNet 2.0、GraspGen、AO-Grasp）普遍同时报告 AP 与仿真抓取成功率，将物理仿真评测作为常规验证，但**未系统研究 corruption 下两者的相关性崩溃边界**。

### Layer 6 — 2025–2026 最新预印本
- GraspGen (2507.13097)、GraspGen-X (2606.00998) 仍采用标准干净 GraspNet AP + Isaac Gym clean rollout 评估，未触及传感器退化基准。

---

## 二、C3 的收窄定位与边界

- **禁止 Claim**：“我们首次提出在仿真中评测抓取物理成功率”（前人已做）。
- **可 Claim**：“我们在系统性传感器 Corruption 扫描下，首次量化了 6-DoF 抓取检测器 AP 与物理执行成功率的秩相关性，并揭示了 Top-1 排序翻转与接触法向畸变的解耦机制。”

---

## 三、4080 Fast-Kill Pilot 执行方案（防噪声与子采样设计）

为避免全量 90 场景 × 256 视角 × 120 条件带来的算力失控与采样噪声，Pilot 必须执行严格的分层子采样：

### 1. 实验子采样设计
- **场景与视角**：固定抽取 30 个场景（Seen: 10, Similar: 10, Novel: 10），每场景固定抽取 16 个均匀视角（共 480 个视点）。
- **基线前置检验（Sanity Check）**：**首先在 480 视点上检验干净条件下的模型排名是否与全量测试集一致**。若子采样改变了基线排名，则该子采样无效，需调整视点数。
- **扰动轴选择**：选择 4 种最具物理代表性的深度 corruption（高斯散斑噪声、边缘 Flying Pixels、量化条带、镜头水雾模糊），各设 3 个强度等级。

### 2. 评测指标与输出
- 分别计算：
  - $m\text{AP}$（数据集指标）
  - $\text{GSR}_{\text{Top-1}}$（真机最相关指标）
  - $\text{GSR}_{\text{Top-10}}$（多样性容错指标）
- 计算各扰动轴下的 Spearman 秩相关系数 $r_s(m\text{AP}, \text{GSR})$。

### 3. Fast-Kill 判定线（预注册）

| 实测结果 | 判定 | 后续行动 |
|---|---|---|
| **$r_s \ge 0.70$ 跨所有扰动轴** | AP 与执行保持强相关，假设不成立 | **立即杀死 C3**，彻底放弃该方向 |
| **仅 Top-1 脱钩，Top-10 仍强相关** | 属于单纯的置信度排序校准问题 | 降级为算法改善短文（Re-ranking） |
| **特定物理扰动（边缘噪声/空洞）下 $r_s < 0.40$** | 核心科学问题成立（法向量与几何容差机制起效） | 保留为有效成果，撰写基准与诊断论文 |
