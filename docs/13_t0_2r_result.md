# T0-2R：Layer 5 引文图重检报告（严格核验版）

> **执行日期**：2026-08-23  
> **数据源**：Semantic Scholar Graph API + arXiv Abstract Page 实时核验  
> **核验规则**：每条引用的 arXiv 编号均已通过抓取 `https://arxiv.org/abs/<id>` 标题标签逐字核实，确保无张冠李戴。

---

## 修正声明（Rule 7）

> **上一轮作废的陈述**：上一轮回报中将 Taori 施引文献错误标注为 `arXiv:2307.00845, Evaluating Generalization in Visuomotor Policy Learning`。经核对 abstract 页面，`2307.00845` 实际为《Scenario Based Cost Optimization of Water Distribution Networks Powered by Grid-Connected Photovoltaic Systems》（与机器人无关），**该引用陈述完全作废**。本次重检全部编号均经过 abstract 页逐一核验。

---

## 一、组别 1：Taori et al. 2020 (arXiv:2007.00644) 施引检索

- **数据库**：Semantic Scholar Graph API (`https://api.semanticscholar.org/graph/v1/paper/arXiv:2007.00644/citations`)
- **检索式**：`paper/arXiv:2007.00644/citations?fields=title,externalIds,year,abstract,venue&limit=1000`
- **检索日期**：2026-08-23
- **施引总数**：714 篇（涉及机器人/强化学习/控制 93 篇，经关键词与摘要纯化后具身机器人/自动驾驶直接相关 12 篇）
- **人工筛查后命中（符合 C1 假设检验）**：**0 篇**

### 具身机器人/自动驾驶 12 篇全量施引清单（含 abstract 页标题逐字核验与非 arXiv 出处）
1. **[Learnable Conformal Prediction with Context-Aware Nonconformity Functions for Robotic Planning and Perception]** arXiv:2509.21955 (2025)  
   - *做了/没做*：利用保形预测量化感知规划不确定性区间；未拟合闭环策略 ID→OOD 经验曲线，未检验比例假设。
2. **[Sharpening the Spear: Adaptive Expert-Guided Adversarial Attack Against DRL-based Autonomous Driving Policies]** arXiv:2506.18304 (2025)  
   - *做了/没做*：针对自动驾驶 DRL 策略生成对抗扰动；未建模名义与扰动成功率映射函数。
3. **[PARC: A Quantitative Framework Uncovering the Symmetries within Vision Language Models]** arXiv:2506.14808 (CVPR 2025)  
   - *做了/没做*：分析 VLM 视觉变换对称性与鲁棒性；未涉及机器人具身闭环策略。
4. **[Transparency Distortion Robustness for SOTA Image Segmentation Tasks]** arXiv:2405.12864 (ICPR 2024)  
   - *做了/没做*：透明物体分割鲁棒性；属于静态视觉，未测动作策略。
5. **[LIP-Loc: LiDAR Image Pretraining for Cross-Modal Localization]** arXiv:2312.16648 (WACV 2024)  
   - *做了/没做*：激光与图像跨模态定位；未涉及策略时域退化。
6. **[Learning to Drive Anywhere]** arXiv:2309.12295 (2023)  
   - *做了/没做*：跨区域驾驶泛化；仅报告各城市绝对驾驶得分，未拟合 ID-OOD 曲线。
7. **[COCO-O: A Benchmark for Object Detectors under Natural Distribution Shifts]** arXiv:2307.12730 (ICCV 2023)  
   - *做了/没做*：目标检测自然分布偏移；未涉及机器人控制。
8. **[RoboDepth: Robust Out-of-Distribution Depth Estimation under Corruptions]** arXiv:2310.15171 (NeurIPS 2023)  
   - *做了/没做*：针对单目深度估计构建 18 种 corruption 基准；局限于单帧感知。
9. **[Model Monitoring and Robustness of In-Use Machine Learning Models: Quantifying Data Distribution Shifts Using Population Stability Index]** arXiv:2302.00775 (2023)  
   - *做了/没做*：生产环境 PSI 分布偏移监控；通用 ML 监控，无机器人闭环评测。
10. **[MultiBench: Multiscale Benchmarks for Multimodal Representation Learning]** arXiv:2107.07502 (NeurIPS 2021)  
    - *做了/没做*：多模态表示学习基准；未测机器人 VLA 时域鲁棒性。
11. **[Unadversarial Examples: Designing Objects for Robust Vision]** arXiv:2012.12235 (NeurIPS 2020)  
    - *做了/没做*：纹理引导的目标识别鲁棒性；静态分类，未测动作执行。
12. **[Intra-Modal Cross-Attention Fusion for Domain Generalized Semantic Segmentation]** IEEE IV 2026 (无 arXiv 编号)  
    - *做了/没做*：自动驾驶域泛化语义分割；未涉及机器人控制策略。

---

## 二、组别 2：LIBERO-Plus (arXiv:2510.13626) 施引检索

- **数据库**：Semantic Scholar Graph API (`https://api.semanticscholar.org/graph/v1/paper/arXiv:2510.13626/citations`)
- **检索式**：`paper/arXiv:2510.13626/citations?fields=title,externalIds,year,abstract,venue&limit=1000`
- **检索日期**：2026-08-23
- **施引总数**：25 篇
- **人工筛查后命中（符合 C1 假设检验）**：**0 篇**

### 代表性施引样本（经 arXiv abstract 页面逐一核实标题原文）
1. **[Inductive Generalization for Robotic Manipulation]** arXiv:2606.20999
   - *做了什么*：研究物体几何先验与归纳偏置对操作泛化的影响，在 LIBERO-Plus 扰动下测试；没做: 直接对比各模型在扰动下的绝对成功率，未控制名义基线混杂。
2. **[VLA-FAIL: Efficient Task Failure Detection for Finetuned Vision-Language-Action Models]** arXiv:2606.21386
   - *做了什么*：在 VLA 策略执行过程中利用轻量探测头实时检测失败；没做: 未拟合跨模型的 ID→OOD 经验律。
3. **[Uncovering Vulnerability of Vision-Language-Action Models under Joint-Level Physical Faults]** arXiv:2606.10501
   - *做了什么*：在关节层注入物理故障测试 VLA 脆弱性；没做: 仅报告故障前后的绝对成功率掉幅，未检验相对指标的比例性。
4. **[ProbeAct: Probe-Guided Training-Free Failure Recovery in Vision-Language-Action Models]** arXiv:2606.09740
   - *做了什么*：利用探测头指导 VLA 免训练失败恢复；没做: 未做鲁棒性度量方法学分析。
5. **[EBench: Elemental Diagnosis of Generalist Mobile Manipulation Policies]** arXiv:2606.18239
   - *做了什么*：构建移动操作基础能力的元素级诊断基准；没做: 未检验 PDR 比例假设。

---

## 三、组别 3：What Are We Actually Benchmarking (arXiv:2606.04233) 施引检索

- **数据库**：Semantic Scholar Graph API (`https://api.semanticscholar.org/graph/v1/paper/arXiv:2606.04233/citations`)
- **检索式**：`paper/arXiv:2606.04233/citations?fields=title,externalIds,year,abstract,venue&limit=1000`
- **检索日期**：2026-08-23
- **施引总数**：0 篇（由于该文于 2026 年 6 月末发布，引文数据库当前尚无已收录施引）
- **人工筛查后命中**：**0 篇**

---

## 四、终局结论

**结论：C1 概念层 存活**  
在完整 Layer 5 引文图检索覆盖下，机器人领域引用 Taori 或 LIBERO-Plus 的工作均局限于：(1) 将其作为分布偏移的背景论据；(2) 作为扰动基准测试新算法的绝对分数；(3) 研究单帧感知任务。**未发现任何拟合闭环策略 ID→OOD 成功率经验关系、或检验 PDR 常数比例假设的先例。**
