# Stage 1-C：进入 Novelty Audit 的 5 个候选问题

> ⚠️ **本文件是 Stage 1 的初判，已被 Stage 2 审计部分推翻。**
> 阅读前请先看 [`06_stage2_audit_result.md`](06_stage2_audit_result.md)：
> - **C1 由 D 降为 C**，且原 claim（「无人控制干净性能」）**错误**——PDR 指标已存在，必须换 claim；
> - **C2 已淘汰**——被 Science Robotics 的 LBM 论文与 STEP 占据；
> - C1 的 Pilot 每条件 100 episodes **统计功效不足**，设计已在 Stage 2 重写。

> 说明：本阶段只完成了 **Novelty Audit 的 Layer 1–2**（直接检索 + 同义词检索）。
> Layer 3–6（机制检索、跨领域检索、引文图、最新预印本）留给 Stage 2，计划见 `04_stage2_audit_plan.md`。
> 因此下面的 Novelty Level 都标为 **preliminary**，不得直接写进论文。

---

# Candidate C1 — 机器人策略的鲁棒性比较是否被"干净成功率"混杂？

## 1. Observation

2025–2026 出现了大量"鲁棒 VLA"论文，比较方式清一色是：
在扰动集上比谁的成功率高。但这些模型的**干净成功率本身就不同**。

同时，LIBERO-Plus 报告了一个被顺带提到、却没人展开的现象：
π0.5（更强的架构 + 更广的训练数据）在物体位移扰动下能撑到 0.4 单位才崩，
而 OpenVLA 和 π0 在 0.2 就归零。
——这正是"鲁棒性差异可能只是能力差异的投影"的直接迹象。

图像分类领域早在 2020 年就解决了这个测量问题：
Taori et al.（NeurIPS 2020）证明 OOD 精度与 ID 精度沿一条几乎确定的曲线分布，
只有偏离该曲线的部分才叫 **effective robustness**；
绝大多数号称提升鲁棒性的方法，effective robustness 为零。

**在本次检索覆盖范围内，没有发现任何机器人/具身智能论文使用或检验过这一方法学。**

## 2. Scientific Question

> **Type A + Type B：**
> 在闭环机器人策略中，扰动条件下的 episode 成功率是否是干净成功率的（近似）确定性函数？
> 若是，其函数形式是什么，为什么闭环控制的形式应当不同于分类任务的线性律？
> 在控制干净性能之后，2025–2026 提出的"鲁棒性方法"还剩多少 effective robustness？

## 3. Origin

| 论文 | 场合 | 年份 | ID |
|---|---|---|---|
| LIBERO-Plus: In-depth Robustness Analysis of VLA Models | arXiv → CVPR 2026 | 2025/2026 | 2510.13626 |
| What Are We Actually Benchmarking in Robot Manipulation? | arXiv | 2026 | 2606.04233 |
| Measuring Robustness to Natural Distribution Shifts in Image Classification | NeurIPS | 2020 | 2007.00644 |
| STRONG-VLA / StableVLA（鲁棒性方法代表） | arXiv | 2026 | 2604.10055 / 2605.18287 |

## 4. Evidence

- LIBERO-Plus：7 轴扰动下 95% → <30%；不同模型崩溃阈值不同（0.2 vs 0.4）。
- 2606.04233：LIBERO 上仅 19.8% 的 SOTA 声明可证统计显著 → 说明该领域的比较基线本就脆弱。
- Taori et al.：在视觉领域，"超出线性趋势的模型极其罕见"。

## 5. Closest Literature（各自做了什么 / 没做什么）

1. **Taori et al. 2020 (2007.00644)** — 建立 effective robustness；**未涉及机器人/闭环控制**。
2. **Accuracy-on-the-line 系列 / Models Out of Line (NeurIPS 2022)** — 讨论线性律何时失效；**均为分类任务**。
3. **Effective Robustness across Training Data (2302.01381)** — 处理训练数据不同带来的偏差；**仍是分类**。
4. **LIBERO-Plus (2510.13626)** — 建立多轴扰动基准并做排行榜；**用绝对成功率比较，未控制干净性能**。
5. **LIBERO-PRO (2510.03827)** — 指出记忆化问题；**不涉及鲁棒性度量方法学**。
6. **2606.04233** — 对**干净**分数做显著性与捷径诊断；**未处理鲁棒性维度、未做 ID–OOD 关系建模**。
7. **STRONG-VLA (2604.10055) / StableVLA (2605.18287)** — 提出鲁棒性方法；**自报绝对提升，未做 clean-matched 比较**。
8. **RoboArena (2506.18123)** — 解决"评测排名可信度"，但是通过众包双盲；**不处理鲁棒性度量的混杂**。
9. **Hooker et al. (1911.05248)** — 压缩模型的长尾遗忘；**分类领域，与本问题互补**。
10. **NavTrust (2603.19229)** — 导航领域的多模态 corruption 基准；**同样使用绝对分数比较**。

## 6. Novelty Level（preliminary）

~~**D**~~ → **Stage 2 审计后为 C**。原判失效：VLATest (2409.12894) 已定义 PDR =
(SR_clean − SR_perturbed)/SR_clean，即已有按干净成功率归一化的指标。
存活的 claim 收窄为「PDR 的**比例假设**从未被检验」。详见 `06_stage2_audit_result.md`。

## 7. Novelty Boundary

- **Known**：(a) VLA 在多轴扰动下大幅退化；(b) 干净 benchmark 已饱和且捷径可解；
  (c) 分类任务中 OOD 精度可由 ID 精度线性预测，effective robustness 罕见。
- **Unknown**：(d) 闭环序贯决策任务中 ID–OOD 关系的**存在性与函数形式**；
  (e) 该关系是否随任务时域 H 系统变化；(f) 现有鲁棒性方法在 clean-matched 条件下是否还有增益。
- **Our possible claim**：只能 claim (d)(e)(f)。
  **不得** claim "我们首次发现 VLA 不鲁棒"——那是 LIBERO-Plus 的贡献。

## 8. Why Important

- **Scientific**：给出闭环策略的 OOD 预测律，并给出机制解释（逐步可靠性沿时域复合）。
  这是分类任务不存在的现象，属于机器人特有的科学问题。
- **Practical**：如果关系近似确定，那么"提升鲁棒性"的正确做法就是提升干净能力，
  整个"鲁棒模块"研究线的投入方式需要改变；同时给出一个可直接采用的报告规范。

## 9. Generality

模型：自回归 VLA（OpenVLA）、flow-matching VLA（SmolVLA/π0）、扩散策略（DP）、Transformer BC（ACT）。
任务：LIBERO 4 套 + SimplerEnv / RoboCasa。扰动：视角、初始位姿、光照、纹理、传感器噪声、物体布局。

## 10. Hypotheses

- **H1**：跨模型的 (clean SR, perturbed SR) 点对可由单参数曲线拟合，R² ≥ 0.85。
- **H2**：在 logit/log 尺度上，斜率随任务时域 H 单调增大（扰动沿时域复合）。
- **H3**：宣称鲁棒性的方法，其相对拟合曲线的残差（= effective robustness）在 bootstrap 95% CI 内不显著大于 0。
- **证伪**：若 R² < 0.5，或残差显著为正且跨扰动轴一致 → H1/H3 被否定，转向"哪些因素制造 effective robustness"。

## 11. Cheapest Pilot（单张 4080）

| 项 | 设定 |
|---|---|
| Dataset | LIBERO（Spatial/Object/Goal/Long）作为 ID；LIBERO-Plus 扰动子集作为 OOD |
| Model | 先用 4 个即可：OpenVLA(4-bit, 7.0 GB)、SmolVLA-450M、自训 Diffusion Policy、自训 ACT |
| 独立变量 | 模型身份 × 扰动轴 × 扰动强度 |
| 控制变量 | 相同初始状态种子集合、相同 episode 预算、相同推理超参（action horizon / 去噪步数固定） |
| Metric | ID SR、OOD SR、拟合残差（effective robustness）、bootstrap CI |
| Expected signal | R² ≥ 0.85 且残差 CI 跨 0 → 支持 H1/H3；单点偏离 >10 个百分点才算真信号 |
| Compute | **F2（3–14 天）**。建议：每条件 100 episodes 起步，先用功效分析决定 episode 数 |

工具：`allenai/vla-evaluation-harness`（"one framework to evaluate any VLA on any sim benchmark"）可省大量工程量。

## 12. Kill Criterion

- 发现 2026 年已有论文做了 clean-controlled 的 VLA 鲁棒性分析 → **立即停**。
- 4 个模型 × 3 扰动轴下 R² < 0.5 且无可解释结构 → 前提不成立，**停**，转 C2 或 C3。
- 评测噪声（同一模型不同 seed）本身就 > 模型间差异 → 该问题退化为 C2。

## 13. Full Experiment（若 Pilot 为正）

E1 现象：≥8 checkpoint × ≥4 扰动轴的 ID–OOD 曲线。
E2 跨模型：覆盖 4 个架构族。
E3 跨数据集：LIBERO + SimplerEnv/RoboCasa，检验曲线是否 benchmark 特异。
E4 机制：按任务时域 H 分层拟合；测量逐步动作误差并检验复合模型 SR ≈ p^H。
E5 压力测试：扰动强度扫描，定位崩溃阈值并与曲线预测对照。
E6 方法：提出 clean-matched 报告规范 + effective robustness 指标，重评已有鲁棒性方法。
E7 成本：无额外成本（纯评测）。
E8 真机：**Pilot 不需要**；Full Paper 若要 claim 真实部署，再申请机器人。

## 14. Resource

Pilot：单 4080 足够。Full：若想覆盖 π0/π0.5 全量与 RoboCasa，建议申请 1×A6000/A100 一个月。机器人：仅最终验证阶段需要。

## 15. Possible Method（发现问题之后）

- Solution 0：报告规范（同时报 clean SR、perturbed SR、effective robustness、CI）。
- Solution 1：clean-matched 比较协议（用早停/数据量把基线拉到同一 clean SR 再比）。
- Solution 2：把时域 H 纳入鲁棒性指标的归一化。
- Solution 3（只有前三个不够时才做）：针对复合机制的缓解方法（如按可靠性预算切分动作块）。

## 16. Reviewer 2

- *"这只是把视觉领域的分析搬过来"* → 反驳需要 **H2（时域依赖）**：闭环任务的函数形式与分类不同，这是新知识。
- *"没有真机实验"* → 需承认 claim 边界，只 claim 仿真评测方法学；并给出真机验证计划。
- *"只在 LIBERO 上成立"* → 必须做 E3 跨 benchmark。
- *"没有新方法"* → 用 E6 的重评结果 + 报告规范作为可操作贡献。

## 17. Publication Potential

MVA 🟡 / ICRA 🟢 / IROS 🟢 / RA-L 🟢 / CoRL 🟢（CoRL 偏爱这类实证研究）/ T-RO 🟡（需真机 + 更强 generality）/ NeurIPS D&B 🟡。

## 18. Overall Risk

**Medium**。主要风险是被 2026 年某篇论文抢先，其次是"缺新方法"的评审攻击。

---

# ~~Candidate C2~~ — 鲁棒性排名的测量可靠性（**Stage 2 已淘汰**）

> 淘汰原因：LBM（arXiv 2507.05331，**Science Robotics 2026**，1,800 真机 + 47,000 仿真 rollouts、盲测 A/B）
> 与 STEP（2503.10966，序贯检验策略比较）已占据该问题。降级为 C1 的实验设计约束。

## Observation
2606.04233 证明了 LIBERO 上只有 19.8% 的**干净** SOTA 声明统计显著。
但 2025–2026 的鲁棒性论文正在用同样脆弱的评测协议（常见 50 episodes/task、1–3 seeds、
经常不报标准差）做**更细的**多轴比较。

## Scientific Question
> Type D：在当前评测协议下，鲁棒性 benchmark 上的模型排名是否可复现？
> 微调 seed、checkpoint 选择、评测初始状态采样引入的方差，是否大于方法之间的差异？

## 关键近邻
2606.04233（干净分数显著性，未做鲁棒性）；LIBERO-Para（报告用 5 seeds，说明社区已意识到）；
通用 ML 的 seed 方差文献（2503.07329 等）。

## Novelty Level（preliminary）
**C**——邻近工作存在（干净分数版本），核心科学问题不同（鲁棒性维度 + checkpoint 选择偏差）。

## Hypotheses
H1：同一方法不同微调 seed 的扰动成功率标准差 ≥ 不同方法间报告差异的 50%。
H2：checkpoint 选择（best-of-N on test）能人为制造 ≥5 个百分点的"鲁棒性提升"。
H3：鲁棒性排名在 LIBERO-Plus 与另一 benchmark 之间发生翻转。

## Cheapest Pilot
只用 SmolVLA-450M（+ACT/DP）：3–5 seeds × LIBERO 4 套 × 4 扰动轴，记录每个 checkpoint 的完整曲线。
**F2**，纯小模型训练+评测，4080 完全够。

## Kill Criterion
若 seed 方差 < 2 个百分点而方法差异普遍 >10 个百分点 → 问题不重要，**停**。

## Risk
Medium-Low。风险在于结论"太可预期"（大家都知道方差大），需要用**排名翻转**这种硬结果撑住。

## Publication
ICRA 🟢 / IROS 🟢 / RA-L 🟡 / CoRL 🟢（可与 C1 合并成一篇更强的论文）。

---

# Candidate C3 — 抓取检测的系统性 corruption 鲁棒性，以及 AP 与执行成功率的脱钩

## Observation
自动驾驶领域早已有系统 corruption 基准（RoboDepth：18 种 corruption × 42 个深度模型；
Robo3D：8 种 corruption × 3 级 × 4 个数据集）。
**抓取检测领域没有对应工作**（本次检索未发现）。
同时多篇抓取论文提到"数据集/仿真/真机之间的差异妨碍准确分析"，
但没人系统量化 **AP 退化能否预测执行成功率退化**。

## Scientific Question
> Type C + Type A：在物理上合理的 RGB-D corruption 下，现代 6-DoF 抓取检测器如何退化？
> 数据集级指标（AP）的退化是否能预测执行级指标（抓取成功率）的退化？

## Origin
GraspNet-1B（CVPR 2020 / IJRR 2023 42(12)，标题即 "Robust grasping across diverse sensor qualities"）；
GraspGen（2507.13097）/ GraspGen-X（2606.00998）；RoboDepth（2310.15171, NeurIPS 2023）；Robo3D（ICCV 2023）。

## Novelty Level（preliminary）
**C**——方法学先例在自动驾驶已成熟（迁移本身不算贡献），
但 **"AP↔执行脱钩"** 这一问题是抓取领域特有的、且未被系统回答，构成独立科学问题。

## Novelty Boundary
- Known：深度洞可以补全；不同深度相机质量不同；抓取 AP 存在尺度偏置。
- Unknown：跨模型的 corruption 退化谱；AP 与执行成功率在扰动下的秩相关是否崩溃；
  哪一类 corruption 造成"AP 看着还行但抓不起来"。
- Possible claim：仅限后者。

## Hypotheses
H1：对若干 corruption（尤其无效像素模式、深度量化），AP 掉幅显著小于执行成功率掉幅。
H2：AP 与执行成功率的 Spearman 秩相关在干净条件下 >0.8，在特定 corruption 下 <0.4。
H3：该脱钩跨 ≥3 个检测器架构成立（点云 backbone / graspness / 扩散生成式）。

## Cheapest Pilot
- Model：GraspNet-baseline、GSNet(graspness)、Economic Grasp、GraspGen（均有公开权重，**只需推理**）。
- Data：GraspNet-1B 测试集（seen / similar / novel），RealSense 与 Kinect 双相机。
- 扰动：按 RoboDepth 风格构造深度侧 corruption（高斯/散粒噪声、无效像素掩码且模拟真实空洞形态、
  深度量化、运动模糊、离焦、光照、JPEG、点云稀疏化），每种 3 级强度。
- Metric：AP（数据集指标）+ 物理仿真中的执行成功率（PyBullet/Isaac + GraspNet 网格）。
- **F1–F2，纯推理，4080 非常舒服。**

## Kill Criterion
若所有 corruption 下 AP 与执行成功率秩相关都 >0.7 → 脱钩不存在，**停**（退回纯 benchmark 论文，价值不足）。
若发现已有论文做过抓取 corruption 基准 → 只保留"脱钩"部分，若也被做过则 **停**。

## Risk
**Low–Medium**。这是 5 个候选里最"安全可发"的：机器人相关性强、免训练、指标清晰。
上限低于 C1（不太可能进 T-RO/RSS），但 ICRA/IROS/RA-L 命中率高。

## Publication
MVA 🟢 / ICRA 🟢 / IROS 🟢 / RA-L 🟢 / CoRL 🟡 / T-RO 🔴。

---

# Candidate C4 — 鲁棒性能否跨扰动轴迁移？

## Scientific Question
> Type E：在扰动轴 A（如光照）上通过增广获得的鲁棒性，能否迁移到未见过的轴 B（如视角）？
> 还是说所谓"鲁棒方法"只是对被评测的那几个轴过拟合？

## 依据
视觉领域先例明确：对抗鲁棒性不跨攻击类型迁移；ImageNet-C 明确禁止在同类 corruption 上训练。
机器人领域：LIBERO-Plus 提供了 7 个可分离的轴，STRONG-VLA / StableVLA 等在做鲁棒性训练，
但**未见 held-out-axis 协议**。

## Novelty Level（preliminary）
**C**，但风险高于 C1/C3：这个想法比较"显然"，2026 年很可能已有论文。

## Cheapest Pilot
SmolVLA 上做 7 组增广训练（每组只用一个轴），交叉评测 7×7 矩阵。**F2**。

## Kill Criterion
若对角线与非对角线差异 <5 个百分点 → 鲁棒性其实是通用的，故事消失，**停**。

## Publication
ICRA 🟢 / IROS 🟢 / RA-L 🟡。

---

# Candidate C5 — 压缩是否在用鲁棒性换干净精度？

## Scientific Question
> Type A：量化/蒸馏在干净任务上"几乎无损"，是否在扰动条件下造成不成比例的退化？

## 依据与风险
视觉领域先例强（Hooker et al. 1911.05248：压缩不成比例地损害长尾样本）；
VLA 侧 DA-PTQ（2604.11572）已提出"时序误差累积/漂移"的概念 → **novelty 风险最高（B/C）**。
但它是 5 个里 **最便宜的**（完全不需要训练，PTQ + 评测即可，F0–F1）。

## 定位建议
**不要单独做**。把它作为 C1 的一个数据点：压缩模型在 ID–OOD 曲线上是落在线上还是线下？
若显著落在线下 → 这是 effective robustness **为负**的第一个实例，反而强化 C1 的故事。

---

# 量化打分（0–10）

| Candidate | Novelty | Significance | Generality | Feasibility(4080) | Exp. clarity | Robotics rel. | Publication | Risk(越低越好) | 总评 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|:--:|
| **C1** ID–OOD 关系 / effective robustness | ~~8~~ 6 | 9 | 9 | ~~8~~ 7 | 9 | 6 | 7 | ~~5~~ 6 | **A**（原 S，Stage 2 下调） |
| **C3** 抓取 corruption + AP↔执行脱钩 | 6 | 8 | 8 | 9 | 9 | 9 | 8 | 4 | **A** |
| ~~**C2**~~ 鲁棒性测量可靠性 | 2 | 8 | 8 | 7 | 9 | 6 | 3 | 8 | **D 淘汰** |
| **C5** 压缩 × 鲁棒性 | 4 | 7 | 7 | 10 | 9 | 8 | 6 | 6 | **B+**（并入 C1） |
| **C4** 跨扰动轴迁移 | 5 | 7 | 7 | 6 | 8 | 6 | 6 | 6 | **B** |

评级含义：S=立即做 Pilot；A=强候选；B=备选；C=风险大；D=放弃。

---

# Top-1 Direction

## 选择：**C1 —— 闭环机器人策略的 ID→OOD 成功率关系，与 effective robustness 审计**
（把 **C5 作为 C1 的一个实验条件**，把 **C2 作为 C1 的可靠性附录**；
若 Stage 2 查重发现 C1 被抢先，立即切换到 **C3**。）

### 1. 为什么它最值得投入？
因为它是唯一一个**我的资源结构反而是优势**的方向：
不需要训练大模型、不需要机器人、用别人已发布的 checkpoint 就能回答一个别人没问的问题。
同时它站在一个已经过热的赛道（VLA 鲁棒性）的**测量层**——赛道热意味着有大量可复用的
checkpoint、benchmark 和待重估的论文，而测量层几乎空着。

### 2. 真正的新知识是什么？
**不是**"提出了一个新模块"。而是：
> 在闭环序贯决策中，扰动下的 episode 成功率与干净成功率之间是否存在一条可预测的曲线；
> 这条曲线的函数形式由"逐步可靠性沿任务时域复合"决定，因而**应当随任务时域系统变化**——
> 这是分类任务不存在、机器人特有的现象。
> 以及：在控制干净性能之后，2025–2026 的"鲁棒性提升"还剩多少。

### 3. 为什么其他机器人研究者会关心？
因为它直接决定他们该怎么写实验表格。如果 ID→OOD 关系接近确定性，
那么"我的方法在扰动集上高 5 个点"就不再是证据，审稿标准会改变；
如果关系随时域变化，那么长时域任务的鲁棒性必须用不同的方式归一化后才能比较。

### 4. 为什么不是 dataset trick？
因为验证要求跨 ≥2 个 benchmark（LIBERO + SimplerEnv/RoboCasa）与 ≥4 个架构族。
若结论只在 LIBERO 成立，那本身就是 E3 的结论（"benchmark 特异性"），仍然是关于测量的真结果。

### 5. 为什么不是 implementation detail？
因为控制变量是**模型身份**，不是某个实现选项；所有模型共享同一评测代码、同一初始状态种子、
同一推理超参。若差异来自实现细节，会在残差结构里表现为随机而非系统偏离。

### 6. 最便宜的第一步实验是什么？
4 个模型（OpenVLA-4bit / SmolVLA / Diffusion Policy / ACT）× 3 个扰动轴 × 3 个强度 × 100 episodes，
画一张 clean-SR vs perturbed-SR 散点图并拟合。**一张图就能决定这个方向生死。**

### 7. 用 RTX 4080 是否能完成？
能。OpenVLA 4-bit 约 7.0 GB；SmolVLA-450M 可训可推；DP/ACT 在 LIBERO 上单卡可训。
LIBERO 仿真本身很轻。属于 **F2（3–14 天）**，需要的是耐心而不是显存。

### 8. 什么时候需要向导师申请额外资源？
满足全部三条时才开口：
(a) Pilot 的 R² ≥ 0.85 或出现清晰的时域依赖结构；
(b) Stage 2 六层查重通过（Novelty ≥ C）；
(c) 已能在两个 benchmark 上重现。
届时申请 1×A100/A6000（跑 π0/π0.5 与 RoboCasa 全量）+ 后期真机验证。

### 9. 什么结果出现应立即停止？
- 查重发现已有 clean-controlled 的机器人鲁棒性分析 → **停**。
- R² < 0.5 且残差无可解释结构 → **停**，转 C3。
- 同一模型不同 seed 的方差 ≥ 模型间差异 → 该问题退化为 C2，按 C2 重写而不是硬撑 C1。
- 拟合曲线在两个 benchmark 上完全不同且无法用时域解释 → 说明是 benchmark artifact，价值大跌，**停**。
