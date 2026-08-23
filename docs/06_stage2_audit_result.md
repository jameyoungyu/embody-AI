# Stage 2：C1 的 Novelty Audit 结果

> 执行日期：2026-08-23。检索方式同 Stage 1（公开 Web 搜索；arXiv/OpenReview/CVF/Semantic Scholar 的 PDF 页面被网络出口拦截）。

## 结论先行

| 项 | Stage 1 初判 | Stage 2 审计后 |
|---|---|---|
| **C1** ID→OOD 关系 / effective robustness | **D**（未见直接研究） | **C**（邻近工作存在，核心科学问题仍未被回答）——**可以继续，但必须换 claim** |
| **C2** 鲁棒性测量可靠性 | C | **淘汰**——被 Science Robotics 论文 + STEP 占据 |
| **C3** 抓取 corruption / AP↔执行脱钩 | C（未审） | 初筛后仍为 **C**，未发现直接冲突 |

**一句话**：C1 原来的说法「没人控制干净性能」是**错的**，必须放弃；
但把 claim 收窄到「**现有的归一化方式（PDR）假设了一个错误的函数形式**」之后，问题依然成立，而且比原来更锋利。

---

## 一、审计推翻了什么

### 1.1 致命发现：PDR 已经是标准做法

**VLATest（arXiv 2409.12894）**已定义并使用：

```
PDR (Performance Drop Rate) = (SR_clean − SR_perturbed) / SR_clean × 100%
```

这就是一种**按干净成功率归一化的鲁棒性指标**，且已在 VLA 鲁棒性评测中流通。

**后果**：Stage 1 写的「无人控制干净性能这一混杂变量」**站不住**，任何以此为卖点的论文会被一句话打死。

**但是**——PDR 隐含了一个**从未被检验的假设**：

> SR_perturbed = (1 − PDR) · SR_clean
> 即扰动的作用是**乘性、成比例**的，与模型能力水平无关。

如果真实的 ID→OOD 关系不是过原点的比例关系（有截距、有曲率、或随任务时域变化），
那么 PDR 会**系统性地错排模型**。这个假设是否成立，本次检索**未发现任何检验**。

### 1.2 最大未解威胁：2026 年的鲁棒性综述

**Robustness of Robotic Manipulation: Foundations and Frontiers**
arXiv **2606.31494**，2026-06-30 提交。
作者：Yifei Dong, Zhanyi Sun, Lujie Yang, Manuel Baum, Kei Ikemura, **Shuran Song**, Florian T. Pokorny, Xianyi Cheng
（Duke / KTH / Stanford / MIT / Organifarms）。

摘要明确写了：**"revisits existing metrics and evaluation methods for quantifying manipulation robustness"**，
并给出「概率视角与控制论视角的一般化鲁棒性形式化」。

**我读不到它的正文**（arXiv 被网关拦截，themoonlight / alphaxiv / Semantic Scholar 同样被拦）。

> ⚠️ **这是你必须亲自做的第一件事**：下载 2606.31494，直接翻到 metrics / evaluation 那一节，
> 检查它是否已经：(a) 指出 PDR 的比例假设有问题；(b) 提出按 nominal performance 归一化的度量；
> (c) 给出 ID→OOD 的函数形式。
> **若 (a)+(c) 都有 → C1 判 A 级，立刻放弃，转 C3。**
> 若只有定义与分类学、没有实证拟合 → C1 成立，且这篇综述反而是你最好的引用与动机来源。

### 1.3 社区正在往这个方向集结

**ICRA 2026 Workshop on Manipulation Robustness**
（manipulation-robustness.github.io/icra2026/），目标包含
"definitions, mechanisms, and **evaluation** of robustness"。

这是双刃剑：
- **坏**：说明有一批人正在盯同一个问题，被抢先的概率显著高于我 Stage 1 的估计。
- **好**：有现成的、饥渴的受众与投稿口。**建议先投这个 workshop 抢时间戳**，再扩成 RA-L/ICRA 全文。

---

## 二、审计淘汰了什么：C2 正式出局

**A careful examination of large behavior models for multitask dexterous manipulation**
arXiv **2507.05331**，已发表于 **Science Robotics (2026)**，TRI。

- 1,800+ 真机 rollouts、47,000 仿真 rollouts；
- **盲测 + 随机化 A/B**，严格控制初始条件；
- 关键数字：**用 50 次 rollout，成功率的置信区间宽度通常是 20–30 个百分点绝对值**，
  这意味着除最大的效应外，其它差异根本测不出来。

加上 **STEP（Is Your Imitation Learning Policy Better than Mine? arXiv 2503.10966）**
提出的序贯检验框架（解决小样本下的策略比较与 p-hacking）。

→ **C2「评测统计可靠性」这个坑已经被顶刊和专门方法论论文填了**。
不要单独做。它降级为 C1 的**实验设计约束**，不是贡献。

---

## 三、审计给出的最重要的实操教训：我的 Pilot 预算错了

Stage 1 我写的是「每条件 100 episodes 起步」。用二项分布算一下（p≈0.5 最坏情况，95% CI）：

| 每条件 episodes | 半宽（百分点） |
|---:|---:|
| 50 | ±14 |
| 100 | ±10 |
| 200 | ±7 |
| 500 | ±4.4 |

而我要检测的 effective robustness 残差量级是 5–10 个百分点。
**按原计划，单点噪声比我要测的信号还大。** LBM 那篇的数字（50 次 → 20–30 点 CI）正是这个意思。

### 修正后的实验设计

**不要**「少数条件 × 大量 episodes」，而要「**大量条件 × 中等 episodes + 显式建模观测噪声**」：

- 单元格 = (模型 × 扰动轴 × 强度)。目标 ≥60 个单元格。
- 每单元格 150 episodes（半宽约 ±8，可接受）。
- 拟合时**不能用朴素 OLS + R²**——每个点自带二项噪声，会造成回归稀释（attenuation），R² 被系统低估。
  改用**分层二项回归 / 测量误差模型**（贝叶斯或 GLM），把每格的 n 显式写进似然。
- 报告的是**曲率参数的后验**，不是一个 R² 数字。

**两个可预注册的统计检验：**

1. **比例性检验**：拟合 `SR_ood = c · SR_clean`（PDR 隐含模型）vs `SR_ood = f(SR_clean; 截距, 曲率)`。
   后者是否显著更好？→ 若显著，PDR 的假设被证伪，这就是论文的核心结果。
2. **时域依赖检验**：按任务时域 H 分层拟合。

> ⚠️ **本条已被 `10_stage3_pilot_protocol.md` §1.3 修正。** 这里原写的是「log 尺度斜率随 H 增大」。
> 把逐步复合模型算完整之后这是错的：设单步能力 q、单步保持率 r，则
> `p_clean = q^H`、`p_ood = (rq)^H = r^H · p_clean`——
> **随 H 变化的是截距 α = H·log r，斜率 γ 反而与 H 无关**（γ = 1 + dlog r/dlog q）。
> 正确的 H2 是「α_H 关于 H 过原点线性」。以协议文件为准。

**算力估计**（需自行标定，属 `[估计值]`）：60 单元格 × 150 ep ≈ 9,000 episodes。
小模型（SmolVLA / DP / ACT）单 episode 数十秒量级；OpenVLA-7B 明显更慢，
建议 7B 只覆盖单元格的一个子集。整体仍在 **F2（3–14 天）**，但没有余量，不要再加模型。

---

## 四、C1 的修订版 Novelty Boundary

- **Known**
  (a) VLA 在多轴扰动下大幅退化（LIBERO-Plus 等 4 个基准）；
  (b) 已有按干净成功率归一化的指标 **PDR**（VLATest）；
  (c) 强模型在某些轴上退化更少（LIBERO-Plus 的 π0.5 vs OpenVLA 观察）；
  (d) 「相对保持率高但原本成功率就低、没有下降空间」这一天花板效应已被<em>顺带提及</em>（2506.06196）；
  (e) 策略评测的统计可靠性问题（LBM / Science Robotics、STEP）；
  (f) 分类任务中 OOD 精度可由 ID 精度线性预测（Taori et al., NeurIPS 2020）；
  (g) 闭环复合误差的**理论**界（DAgger 谱系；2503.09722）。

- **Unknown**（我能 claim 的全部）
  (h) 闭环操作任务中 ID→OOD 成功率关系的**实证函数形式**；
  (i) **PDR 的比例假设是否成立**，不成立时它错排了哪些模型；
  (j) 该关系是否随**任务时域 H** 系统变化，即复合误差理论在 episode 级成功率上的**实证对应**。

- **禁止 claim**：「我们首次发现 VLA 不鲁棒」「我们首次提出按干净性能归一化」——两者都已有人做。

**修订后的论文一句话**：
> 现有 VLA 鲁棒性比较使用的 Performance Drop Rate 隐含了一个未经检验的比例假设；
> 我们在多个架构族与多个 benchmark 上拟合闭环策略的 ID→OOD 成功率关系，
> 证明它是非比例且随任务时域变化的，并给出由此导致的模型错排与修正后的报告方式。

---

## 五、C3 初筛（尚未做完整六层）

| 检查 | 结果 |
|---|---|
| 抓取检测的 ImageNet-C 式 corruption 基准 | 未发现直接对应工作 |
| 最近邻 | **A Benchmarking Study of Vision-based Robotic Grasping Algorithms（2503.11163）**——系统改变背景纹理与光照评估真实鲁棒性，但不是 corruption 谱系，也未做跨模型退化曲线 |
| AP ↔ 执行成功率系统相关性研究 | 未发现；只见到零散的「仿真执行比真机更严格/数据集与真机有差异」的定性表述 |
| 结论 | 仍为 **C**，无直接冲突。但 Layer 3–6 未做，不能当定论 |

---

## 六、修订后的行动建议

**推荐路线：C1 继续，但按下面的顺序做，不要跳步。**

1. **（半天，阻塞性）** 亲自读 2606.31494 的 metrics 章节。这一步的结论决定后面所有事。
   - 若它已给出 ID→OOD 实证关系 → **停 C1，转 C3**。
   - 否则继续。
2. **（半天）** 读 VLATest（2409.12894）确认 PDR 定义与使用方式；读 LIBERO-Plus 正文，
   确认它是否在附录画过 clean-vs-perturbed 散点。
3. **（1 天）** 补做我做不了的 **Layer 5 引文图**：用 Google Scholar / Semantic Scholar 查
   Taori (2007.00644) 的引用中是否有机器人论文；查 LIBERO-Plus 与 2606.04233 的施引文献。
   我的网络访问被拦截，这一层是**空的**，必须你来补。
4. **（1–2 周）** 按第三节的修订设计跑 Pilot，先只做「比例性检验」。
5. **（时间戳）** 结果一出来就投 **ICRA 2026 manipulation robustness workshop**，再扩全文。

**预注册的停止规则（在修订设计下重写）**

| 结果 | 行动 |
|---|---|
| 2606.31494 已含实证 ID→OOD 关系 | **停 C1**，转 C3 |
| 比例模型与带曲率模型的拟合无显著差异（贝叶斯因子不支持） | PDR 假设成立，**核心 claim 死亡**，停 |
| 曲率显著但不导致任何模型排名变化 | 只是数学细节，无实践意义，**停** |
| 曲率显著且改变排名，但 α_H 与 H 无结构 | 仍可发，但机制故事减半，降级为方法学短文 |
| 曲率显著、改变排名、且 α_H 关于 H 线性 | **全部成立**，按 Full Experiment 推进并申请资源 |

---

## 七、本次审计的覆盖与缺口（诚实记录）

**已完成**
- Layer 1 直接检索：6 组检索式，均无「机器人 effective robustness」直接命中。
- Layer 2 同义词：命中 PDR、相对保持率、天花板效应的零散表述。
- Layer 3 机制：命中复合误差理论谱系与长时域退化的定性描述；**未发现 episode 级成功率与时域的实证拟合**。
- Layer 4 跨领域：RL / 自动驾驶均未见 effective robustness 的应用。
- Layer 6 最新：命中 2606.31494 综述、ICRA 2026 workshop、VLA-Arena (2512.22539)、
  RobustVLA (2511.01331)、Inductive Generalization (2606.20999)、LBM Science Robotics (2507.05331)。

**未完成（缺口，必须由你补）**
- **Layer 5 引文图完全没做成**：Semantic Scholar / OpenReview / Google Scholar 均被网络出口拦截。
- **2606.31494 正文未读**：这是最大的单点风险。
- 所有 26xx 编号预印本仅见摘要级信息，未读正文。
