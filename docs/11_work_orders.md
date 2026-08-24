# 任务单（执行方：本地 agent；验收方：本会话）

规则：
- 任务单只在本文件更新，执行方 pull 后照做。
- 每张单子有**前置门**、**禁止事项**、**回报格式**、**验收标准**四段。
- 前置门未过不得进入下一步；禁止事项不得自行放宽。
- 回报必须按指定格式，缺项视为未完成。

---

# T0（已验收，见 `12_t0_audit.md`）：补完两项 Stage 2 缺口

> **T0-1 通过。T0-2 退回 → 见下方 T0-2R。T1 已解除阻塞，与 T0-2R 并行。**

## 目标
把 C1 的 novelty 判定从「暂定」变成「已核」。

## 步骤

**T0-1　存档 2606.31494 §6.1.1 原文**
- 下载 PDF，记录 arXiv 版本号（v1/v2）与下载日期。
- 逐字摘录 Goal-Oriented Measures 一节中涉及 nominal performance、
  perturbed success rate、relative drop / percentage degradation 的**完整句子**。
- 存为 `docs/evidence/2606.31494_sec6.1.1.md`，含出处（节号、页码）。
- 同时确认该节**是否**出现下列任一意思的表述：
  「现有相对下降类指标未控制 nominal performance」/「该类指标不可跨能力水平比较」。

**T0-2　补 Layer 5 引文图**
用 Google Scholar 或 Semantic Scholar 查三组施引文献，各列**具体标题 + 编号**：
- Taori et al. 2020（arXiv 2007.00644）的施引中，是否有机器人/闭环控制论文；
- LIBERO-Plus（2510.13626）的施引；
- What Are We Actually Benchmarking（2606.04233）的施引。
筛选条件：是否有人拟合过 ID→OOD 成功率关系、或检验过相对下降类指标的比例假设。

## 禁止事项
- 禁止在没有逐字引文的情况下断言「该文没有提出某 critique」。
- 禁止只给结论不给论文标题/编号。
- 禁止把「检索没找到」写成「不存在」。

## 回报格式
```
T0-1  版本: v?   日期: ____
      原文摘录: （逐字，≥3 句）
      是否含 critique: 是 / 否   依据句: ____
T0-2  Taori 施引中的机器人论文: [标题, 编号] × N（无则写 "0 篇，检索式: ____"）
      LIBERO-Plus 施引命中: ...
      2606.04233 施引命中: ...
      结论: C1 概念层 存活 / 被抢先
```

## 验收标准
两项都有可核查的原始出处。**T0-1 若判定「含 critique」→ 停 C1，启动 T4（转 C3）。**

---

# T0-2R（**已验收通过**，见 `14_t0_2r_audit.md`）：重做 Layer 5 引文图

## 退回原因
见 `12_t0_audit.md`：一条引用（arXiv 2307.00845）经核实为配水管网光伏成本优化论文，
与视觉运动策略无关；另有两组检索未给出检索式与数据库。

## 本次额外要求
1. **每一条引用必须先打开 arXiv abstract 页核对标题**，回报时贴上该页显示的标题原文。
   编号与标题对不上的一律不得列入。
2. 每组检索必须给出：检索式、数据库（Google Scholar / Semantic Scholar / 其他）、检索日期、命中总数。
3. 没有命中就写「0 篇」并附上述四项，不要用叙述性结论替代。

## 回报格式
```
组别: Taori 2007.00644 施引 / LIBERO-Plus 施引 / 2606.04233 施引
  数据库: ____   检索式: ____   日期: ____   施引总数: ____
  人工筛查后命中: N 篇
    - [abstract 页标题原文] arXiv:____  ——  做了什么 / 没做什么
  （N=0 时写 "0 篇"）
```

## 验收标准
每条引用可被独立打开核对。任一编号与标题不符 → 整份退回。

---

# T2-PRE：零算力预试验（**新增，优先级高于 T1**）

## 为什么插在 T1 前面
γ 可以**不跑一个 episode**先估一遍。LIBERO-Plus、EBench、LIBERO-PRO、RoboDojo
都公开了「模型 × 扰动条件」的成功率表——那正是拟合 ID→OOD 关系所需的 (p_clean, p_ood) 点对。
半天之内就能知道 C1 是死是活，比先花几天搭 harness 划算得多。

## 步骤
1. 从**论文 PDF 正文与附录**抄录完整表格（不是二手摘要、不是本对话里出现过的散点数字）：
   - LIBERO-Plus `2510.13626` / CVPR 2026 版：7 个扰动轴 × 全部模型；
   - EBench `2606.18239`：4 个 generalization 维度 × π0 / π0.5 / XVLA / InternVLA-A1；
   - LIBERO-PRO `2510.03827`、RoboDojo `2607.04434` 若有同构表格一并抄。
2. 每个单元格记录：模型、轴、扰动成功率、**对应的干净成功率**、**每格 episode 数 n**。
   n 若论文未写，记录其声明的评测协议（LIBERO 惯例每任务 50 × 10 任务 = 500/套），
   并在表中标注 n 是「论文明确给出」还是「按协议推断」。
3. 用 `analysis/idood_model.py` 的 **`fit_hier()` / `lrt_hier()`** 拟合，报告 γ、95% CI、LRT p 值。
   **禁止用扁平 `Cell` 池化多个条件**——那会让 clean 观测被重复计入、凭空造出 γ≠1
   （实测真值 γ=1 时单次抽样即得 p=0.035）。CI 用 `paired_bootstrap_gamma()`。
4. 顺带算 PDR 排序 vs 残差排序的 Spearman——这是 H3 的免费预演。

## 禁止事项
- **禁止使用检索摘要里的数字。** 必须回原文表格。本会话中出现过的任何散点数字一律不得入表。
- 不同数据源（不同论文 / 不同 LIBERO 版本 / 不同评测协议）的点**不得混进同一次拟合**。
- OOD 成功率接近 0 的单元格要单独标注：近地板区对数拟合不稳定，必要时改报非参数结果。
- 干净成功率若是从别处凑来的（不是同一篇论文同一协议下测的），必须标注，并做敏感性分析。

## 回报格式
```
数据源: ____ (arXiv 编号, 表号, 版本)
单元格数: ____   n 明确给出 / 按协议推断: ____ / ____
按轴拟合: [轴, 点数 M, γ_hat, 95% CI, LRT p, 是否近地板]
H3 预演: 每轴 Spearman(PDR 排序, 残差排序) = ____
```

## 验收标准
至少两个独立数据源，每源至少一个轴上有 ≥5 个点对。
- **各源 γ 的 CI 都覆盖 1** → C1 提前死亡，转 T4，不必再跑 T1/T2。
- **γ 显著偏离 1** → C1 大幅提前，T1/T2 转为「用受控实验确认公开表格上看到的现象」。

---

# T6：Related Work 重定位（**在写论文之前必须完成**）

## 起因
外部评审指出并经本会话核实：**arXiv `2602.03344`
《Robustness as an Emergent Property of Task Performance》**（2026-02，cs.CL）
已经证明鲁棒性主要由 task competence 驱动，并建议减少对鲁棒性的独立投入。
**"发现能力混杂鲁棒性"这个概念命题已被发表**，不得再作为本工作的 headline。

## 步骤
1. 读 `2602.03344` 全文，重点看：它用了哪些相对下降指标、是否讨论过指标的可比性、
   附录里 PDR 与总体性能的趋势具体是什么形状。**逐字存档到 `docs/evidence/`。**
2. 读 `2603.11400`《Deployment-Time Reliability of Learned Robot Policies》
   （**Christopher Agia 的斯坦福博士学位论文**，不是会议论文，引用时文献类型要写对）,
   摘出其关于 compounding errors 的表述——H2 机制部分要引。
3. 按 `10_stage3_pilot_protocol.md` §1bis 的对照表重写定位段落。

## 禁止事项
- 禁止把 `2602.03344` 说成"只是 NLP、与我们无关"。它的**推论**直接冲击整个 robust-VLA 研究线，
  必须正面处理。
- 禁止沿用评审给的 "ROEP" 这个名字——查无此文，正确出处见上。

## 验收标准
两篇都有逐字存档；定位段落写成"检验其推论在闭环控制中是否成立"，而非"我们首次发现"。

---

# T5：常设 arXiv 监视（每周一次，长期）

## 为什么需要
T0-2R 用引文数据库做 Layer 5，但它对新预印本有索引延迟——
执行方自己的数据显示 **2606.04233 发布近两个月仍记录到 0 篇施引**。
引文图因此**系统性看不见最近 2–3 个月**，而那恰好是竞品最可能出现的窗口。
「0 命中」这个结论比它看上去的要弱，必须用前瞻监视补上。

## 步骤
每周扫 arXiv cs.RO + cs.LG 新投稿，关键词组：
```
robustness evaluation manipulation / effective robustness / performance drop rate
perturbation success rate / generalization gap policy / robustness metric robot
```
命中记入 `docs/watch_log.md`：日期、编号、**abstract 页标题原文**、是否构成冲突。

## 验收标准
每周一条记录（含「本周 0 命中」）。**发现冲突立刻上报，不要等下次汇报。**

---

# T1：Controlled Within-Family Experiment（ACT 优先路线，见 `16_t1_act_protocol.md`）

## 前置门
**T0 与 T2-PRE 预试验完成归档**（已通过）。

## 目标
在 ACT 策略族内执行受控能力扫描，利用三集隔离与 Seed-Level 配对评测，检验鲁棒性保持率 $R$ 及条件破坏率 $D$ 是否系统性随基线能力演化。

## 阶段规划
1. **T1-mini 冒烟排查跑（Sanity Run）**：
   - 1 seed × 5 checkpoints（$p_{clean} \approx [0.35, 0.50, 0.65, 0.80, 0.92]$）
   - 2 扰动轴（Camera / Initial Object Pose）× 100~150 配对 episodes
   - 目的：验证显式状态还原 $S_{0,j}^{clean} = S_{0,j}^{OOD}$、排查地板/天花板效应、实测 RTX 4080 墙钟吞吐。
2. **T1-A 正式识别跑**：
   - ACT 架构：$3 \text{ training seeds} \times 7 \text{ capability bins} = 21$ 个评估点
   - 严格在 Validation 集选点后，进入独立 Frozen Test 集测 Clean 与 OOD 配对矩阵。
3. **T1-B 跨族复现跑**：
   - Diffusion Policy：$3 \text{ seeds} \times 5 \text{ capability bins} = 15$ 个评估点。

## 禁止事项
- **严禁在观测 OOD 后挑选 Checkpoint（No Cherry-Picking）**。
- **严禁仅用随机数种子代替显式物理状态还原**（必须保存并恢复完整状态快照）。
- 严禁将选点所用的 Validation 集混入最终 Test 集统计。

## 回报格式
```
T1-mini 冒烟结果:
- 状态还原复现性: 100% / 异常
- Checkpoint 干净能力梯度: [c1, c2, c3, c4, c5] (跨度: ____)
- OOD 响应区间: Camera [____], Object Pose [____] (有无地板/天花板)
- RTX 4080 单 episode 实测耗时: ____ 秒
- 全量 T1-A 预期耗时: ____ 小时
```

## 验收标准
T1-mini 状态还原无误差、能力跨度 $\ge 50$ 点且无全量地板效应 $\to$ 正式启动 T1-A。


---

# T2：Stage 3 Pilot Phase 1（决定生死的一张图）

## 前置门
T1 验收通过。

## 目标
拿到 γ 的第一个估计，判定 H1。

## 步骤
1. 选 1 个扰动轴（建议相机视角——LIBERO-Plus 报告它最致命，信号最强）。
2. 3 个强度 × 全部 checkpoint × 150 episodes，初始状态种子与 T1 干净基线**配对**。
3. 用 `analysis/idood_model.py`：构造 `list[Checkpoint]`（每个 checkpoint 一条 clean、
   多条 `OODObs`）→ `lrt_hier()`；CI 用 `paired_bootstrap_gamma()`。
   **禁止用扁平 `Cell` 池化多个条件。**
4. 曲线只在**参考总体**（标准训练策略）上拟合；鲁棒性方法作为 held-out，
   用 `effective_robustness_vs_reference()` 打分。见协议 §3.3bis。
4. 画 clean SR vs perturbed SR 散点 + 拟合曲线 + γ=1 参考线。

## 禁止事项
- **禁止用观测成功率对观测成功率做 OLS**（回归衰减会凭空造出 γ<1，正是我们要测的效应）。
  必须走 `idood_model.py` 的潜变量似然。
- 禁止把每格 episode 数压到 100 以下。
- 禁止看到结果后调整判据。

## 回报格式
```
每强度一行: [强度, γ_hat, γ 的 95% CI, LRT p 值, 是否收敛]
散点图: 附图
H3 检查: PDR 排序 vs 残差排序的 Spearman = ____
```

## 验收标准
按 `10_stage3_pilot_protocol.md` §6 的停止规则表判定。三种结局都要如实报，
**不允许出现「结果不理想但还能包装」这种回报**。

---

# T3：Phase 2 + Phase 3（仅在 T2 判定继续时启动）

4 轴 × 3 强度全量；随后按演示长度四分位分层重拟合，检验 α_H 关于 H 是否过原点线性。
回报格式沿用 T2，另加 α_H 对 H 的回归结果。

---

# T4：C3 Fast-Kill（仅在 C1 被判死时启动）

按 `07_c3_stage2_audit.md` 的子采样方案执行，目标是**尽快证伪 C3**：
若 r_s ≥ 0.70 跨扰动轴普遍成立 → 当场杀死 C3，不留念想。

---

# 通用禁止事项（对所有任务单生效）

1. 评级只能用 **A / B / C / D**，不得出现 B+ / C+ 之类。
2. 任何「某某没做过」的断言必须附检索式、数据库、时间范围、最近邻工作。
3. 报告成功率必须同时给 **n 与置信区间**，禁止裸报点估计。
4. 不得因为「已经写了代码 / 已经跑了实验」而放宽预注册判据。
5. 跨机器写同一文件前先 `git pull`，避免再次分叉。
6. **任何 arXiv 编号在写进回报前必须打开 abstract 页核对标题**，并贴上该页标题原文。
   已发生过一次编号张冠李戴（见 `12_t0_audit.md`）。
7. **修正了此前事实陈述时，必须显式写明「上一轮哪句话作废」**，不得只更新结论。
   已发生过一次两轮事实互斥而结论不变的情况。
