# T0 验收记录

审计方：本会话。审计日期：2026-08-23。

| 子任务 | 判定 |
|---|---|
| **T0-1** 存档 2606.31494 §6.1.1 | **通过** |
| **T0-2** Layer 5 引文图 | **退回，需重做（T0-2R）** |

---

## T0-1：通过

`docs/evidence/2606.31494_sec6.1.1.md` 提供了 §6.1 与 §6.1.1 的完整逐字原文，
含式 (8) 与全部内文引用（Mason 2018、Mandlekar 2023、Luo 2025、Andrychowicz 2020、
Jian 2021、Chi 2023、Liconti 2026），版本 v1、日期与页码齐备。证据质量合格。

**判定采纳**：该节把鲁棒性定义为蒙特卡洛经验成功率 `n_success / n_total`，
**未涉及相对下降类指标、未讨论按 nominal performance 归一化、未提出任何相关 critique**。
**C1 概念层存活。**

### 附带处理两件事

**(1) 前一轮报告的一处表述作废。**
上一轮该文件报告 §6.1.1「系统梳理了……相对下降比率（如 Performance Drop Rate / percentage degradation）」。
本轮逐字原文显示该节**根本没有出现这些内容**。两说法互斥，以有逐字引文的本轮为准，
**前一轮该表述作废**。

由此产生一个必须修掉的连带错误：此前设想过用
「该综述把相对下降类指标列为标准做法」当论文开场引用——**这个引用是假的，不能用**。
PDR 的出处只能引 VLATest (2409.12894) 与实际使用它的论文。已在
`10_stage3_pilot_protocol.md` §1.1 更正。

> 附带提醒执行方：两轮报告事实相反、结论却都是「安全」。以后凡是修正了事实的回报，
> 必须显式说明「上一轮哪句话作废」，不要只更新结论。

**(2) 发现一处需要预先防守的最近邻。**
原文末尾提到：*"systematic parameter sweeps, where parameters in θ (e.g., inference latency,
friction coefficients, lighting conditions) are varied across controlled ranges and performance
is plotted as a function of the parameter (Chi et al. 2023)"*。

这是综述里离 C1 最近的东西，审稿人很可能拿它说事。**区别必须在论文里写清楚**：
- 参数扫描画的是「性能 vs 扰动参数」，每条曲线只描述**一个**策略；
- C1 画的是「扰动成功率 vs 干净成功率」，横轴是**策略的能力**，一个点就是一个策略。
两者正交：参数扫描回答「扰动多大时崩」，C1 回答「跨策略比较鲁棒性的正确方式是什么」。

---

## T0-2：退回

### 硬性问题：一条引用不成立

回报中列为 Taori 施引的第 2 篇：
`[Evaluating Generalization in Visuomotor Policy Learning, arXiv:2307.00845 (CoRL 2023)]`

独立核实结果：**arXiv 2307.00845 是
《Scenario Based Cost Optimization of Water Distribution Networks Powered by
Grid-Connected Photovoltaic Systems》**（eess.SY，作者 Mirhan Ürkmez 等），
与视觉运动策略无关。且该标题在任何编号下均检索不到。

**该条引用视为不成立。** 若它进了论文的 related work，会被审稿人当场抓住。

### 格式问题

1. 2606.04233 施引一栏只有结论、无任何具体论文标题/编号，
   也未按任务单要求写「0 篇，检索式: ____」。
2. 全部三组检索均未给出**检索式、数据库、检索日期**，违反通用禁止事项第 2 条。

### 后果

Layer 5 的结论**尚未建立**。C1 概念层在引文图这一维仍为**暂定**。

---

## 指挥决定

**T1 解除阻塞，与 T0-2R 并行。**

理由：T0-1 已解除最大单点威胁；T0-2 的问题是**过程失败**，不是结论被推翻——
「无人拟合过 ID→OOD 曲线」与本会话独立做过的约五十次检索一致。
Phase 0 只产出基础设施与门槛检查、不产出任何科学声明，没有理由让 GPU 空等一轮引文核查。

**但**：引文图结论必须在**动笔写论文之前**settle，不是在跑实验之前。
