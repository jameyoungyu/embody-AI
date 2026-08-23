# Stage 2：Novelty Audit 执行计划（针对 Top-1 = C1）

本阶段目标：在写任何代码之前，确认 C1 的 novelty 是否成立。
**预算：1–2 天纯检索。若发现直接冲突，立即切换到 C3，不要沉没成本。**

---

## Layer 1 — Direct Search

在 Google Scholar / arXiv listing / OpenReview 上逐条执行，时间范围 2019–2026：

```
"effective robustness" robot policy
"effective robustness" manipulation
"accuracy on the line" robot
in-distribution out-of-distribution success rate correlation manipulation policy
clean success rate controls robustness comparison VLA
robustness normalized by clean performance robot policy
```

## Layer 2 — Synonym Search

为核心概念建立同义词组，交叉组合检索：

| 概念 | 同义词 |
|---|---|
| effective robustness | relative robustness、robustness beyond baseline、residual robustness、controlled comparison、matched-accuracy comparison |
| clean performance | nominal success rate、in-distribution performance、unperturbed success、baseline capability |
| perturbed performance | OOD success、robustness score、degradation、perturbation success rate、retention rate |
| 闭环复合 | error accumulation、compounding error、covariate shift in imitation learning、horizon-dependent failure |
| 关系形式 | linear trend、probit scale、scaling relation、predictive law、correlation structure |

## Layer 3 — Mechanism Search

针对"逐步误差沿时域复合"这一机制：

```
compounding error imitation learning horizon quadratic DAgger
per-step error episode success rate horizon relationship
error accumulation action chunk closed-loop policy degradation
horizon-dependent robustness manipulation policy
```
必读经典：Ross & Bagnell 的 DAgger / 复合误差界（这是本机制的理论祖宗，**必须引用并说明我们做的是实证律而不是重述理论界**）。

## Layer 4 — Application-Neutral Search

同一机制可能已在别的领域研究过，必须查：

```
effective robustness reinforcement learning
ID OOD correlation sequential decision making
robustness measurement autonomous driving planner
robustness metric confound clean accuracy medical imaging
robustness linear trend NLP / speech
```
**判定规则**：若某领域已有闭环任务的 ID–OOD 律，则本工作必须以"机器人操作特有的时域依赖 + 对现有 VLA 鲁棒性方法的重估"作为增量，否则 novelty 降为 B。

## Layer 5 — Citation Graph

对以下三篇做完整的引文图检查（References + Citing papers + 同作者后续）：
1. Taori et al. 2020（2007.00644）——**重点看 2024–2026 引用它的机器人论文**
2. LIBERO-Plus（2510.13626 / CVPR 2026）——看所有引用它的鲁棒性论文
3. 2606.04233 —— 看它的 related work 是否已提出本问题

## Layer 6 — Newest Work

```
site:arxiv.org 2606 2607 2608 VLA robustness evaluation methodology
OpenReview: ICLR 2027 / CoRL 2026 submissions, keyword = robustness evaluation manipulation
```
2026 年 6–8 月的预印本是最大威胁，必须逐周扫。

---

## 判定表

| 检索结果 | Novelty Level | 行动 |
|---|---|---|
| 找到已做 clean-controlled 的机器人鲁棒性分析 | A | **放弃 C1**，转 C3 |
| 找到 RL/驾驶领域的闭环 ID–OOD 律 | B–C | 保留，但必须强化时域依赖与重估部分 |
| 只找到分类领域的 effective robustness | C–D | **继续**，这是预期结果 |
| 完全没有相关工作 | D | 继续，但需额外做 Significance Audit（为什么以前没人做？） |

---

## Significance Audit（即使 Level D 也必须过）

问："为什么以前没人研究？"
- 原因 1（没人注意）→ 可接受：机器人领域的评测文化直到 2025 年才开始自省（2606.04233 是 2026 年的）。
- 原因 2（以前条件不成熟）→ 可接受：需要有足够多的公开 checkpoint 与多轴扰动基准，这在 2025 年底才具备。
- 原因 3（问题其实没影响）→ **淘汰**：若 clean SR 差异本来就很小，混杂就不存在。
  **Pilot 必须先检查候选模型的 clean SR 跨度是否足够大（建议 ≥30 个百分点）。**
- 原因 4（问题过于人工）→ **淘汰**。

## 至少满足 3 项的检查表（C1 逐条自查）

- [x] 多个模型受影响（所有做鲁棒性比较的论文）
- [x] 多个数据集受影响（LIBERO 系 + SimplerEnv + 导航的 NavTrust）
- [ ] 真实传感器会出现（不适用——这是测量问题）
- [x] benchmark 结果会因此改变（重估会改变排名解释）
- [x] 当前论文没有控制该变量（已确认 LIBERO-Plus / STRONG-VLA 用绝对分数）
- [x] 可以提出明确机制解释（时域复合）
- [x] 可以设计 clean ablation（同一评测代码 + 固定初始状态种子）

→ 满足 6 项，通过。

---

## Stage 3 Pilot 的预注册（写在动手之前，防止事后编故事）

**在跑实验之前就写死下面四条，任何一条命中就按规定执行，不许改口径：**

- Result A（方向成立）：R² ≥ 0.85 且鲁棒性方法的残差 CI 跨 0 → 进入 Full Experiment。
- Result B（效果太小）：clean SR 跨度 <15 个百分点，无法辨识关系 → 立即放弃。
- Result C（只对某模型成立）：曲线只在 VLA 族成立、DP/ACT 完全偏离 → 转为
  "架构族特异的鲁棒性结构"研究，或放弃。
- Result D（已有基线可解决）：若简单地报告相对下降率（retention rate）就完全等价于我的 effective robustness →
  贡献不足，**放弃**。（这一条尤其重要：必须在 Pilot 中显式证明 retention rate 与 effective robustness
  给出不同的方法排名，否则本工作没有独立价值。）
