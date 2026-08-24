# Embodied AI 研究选题挖掘项目

本仓库记录一次系统性的具身智能（Embodied AI / Robot Learning / Robot Manipulation）
研究方向挖掘过程。目标不是"想出几个看起来新颖的模块"，而是找到**真实存在、尚未被解决、
可被证伪、单张 RTX 4080 可完成 Pilot 验证**的研究问题。

## 方法论（Stage 流程）

```
Stage 1  Literature Mining（已完成）
Stage 2  Novelty Audit（已完成：C1 边界重塑与假设证伪，C3 全量查重与交叉验证）  ← 当前阶段
Stage 3  4080 Pilot（验证现象是否存在）
Stage 4  Mechanism（研究成因）
Stage 5  Generalization（跨模型 / 跨数据集）
Stage 6  Method（最小必要解法）
Stage 7  Resource Escalation（申请 GPU / 机器人）
Stage 8  Paper
```

核心纪律：**Cheap discovery → Strong evidence → Resource escalation**。
在问题本身尚未被证明存在之前，不投入昂贵资源。

## 文档

| 文件 | 内容 |
| --- | --- |
| [docs/01_landscape.md](docs/01_landscape.md) | 2022–2026 研究地图：15 个子方向的主流方法 / 已解决 / 未解决 / 拥挤度 |
| [docs/02_failure_modes.md](docs/02_failure_modes.md) | Failure Mode 矿藏清单 + **淘汰清单**（哪些方向已经死了） |
| [docs/03_candidates.md](docs/03_candidates.md) | 5 个进入 Novelty Audit 的候选问题 + 量化打分 + Top-1 推荐 |
| [docs/04_stage2_audit_plan.md](docs/04_stage2_audit_plan.md) | Stage 2 六层查重的具体执行计划 |
| [docs/05_references.md](docs/05_references.md) | 参考文献 + **逐条核实状态标注** |
| [docs/06_stage2_audit_result.md](docs/06_stage2_audit_result.md) | **Stage 2 查重结果**：C1 降级为 C 并换 claim，C2 淘汰，Pilot 统计设计重写 |
| [docs/07_c3_stage2_audit.md](docs/07_c3_stage2_audit.md) | **Candidate C3 全量查重**：抓取 Corruption 基准与 AP-执行脱钩机制审计 |
| [docs/08_cross_check_notes.md](docs/08_cross_check_notes.md) | **对外部审计报告的交叉核实**：一处判定逻辑不成立、一处文献事实纠正、C3 风险重估 |
| [docs/09_venue_timeline.md](docs/09_venue_timeline.md) | **投稿窗口核实**：ICRA 2026 workshop 与 CoRL 2026 均已关闭，路线改为 arXiv 预印本 + RA-L |
| [docs/10_stage3_pilot_protocol.md](docs/10_stage3_pilot_protocol.md) | **Stage 3 Pilot 预注册协议**：统计模型、功效分析、执行阶段、停止规则 |
| [docs/11_work_orders.md](docs/11_work_orders.md) | **任务单**：分工、禁止事项、回报格式、验收标准 |
| [docs/13_t0_2r_result.md](docs/13_t0_2r_result.md) | **T0-2R 严格核验**：Layer 5 引文图重检与 12 篇全量施引核实 |
| [docs/14_t0_2r_audit.md](docs/14_t0_2r_audit.md) | **T0-2R 验收**：通过，新增常设监视与零算力预试验 |
| [docs/15_external_review_audit.md](docs/15_external_review_audit.md) | **外部评审验收**：2602.03344 核实属实并改写定位；层次似然修复（一类错误 73%→4%） |
| [docs/21_t2_pre_t1mini_audit.md](docs/21_t2_pre_t1mini_audit.md) | **T2-PRE / T1-mini 验收**：公开表格 γ̂ 不可信；主假设换为「匹配能力下跨架构离散 14 倍」 |
| [docs/15_t2_pre_result.md](docs/15_t2_pre_result.md) | **T2-PRE 预试验报告**：公开基准数据实证拟合，7 轴全量证伪 PDR 比例假设 |
| [docs/watch_log.md](docs/watch_log.md) | **T5 前瞻监视日志**：每周 cs.RO / cs.LG 新提交追踪 |

## Stage 1 一句话结论

> 2025–2026 年，"给 VLA 做鲁棒性 benchmark"和"提出一个更鲁棒的模块"这两条路已经过热；
> 真正还空着的是**测量层面**的问题——**鲁棒性提升到底是真的，还是干净性能的副产物**，
> 以及**闭环控制中扰动如何随任务时域复合**。这正好是单张 4080 用别人已发布的
> checkpoint 就能回答的问题。

详见 [docs/03_candidates.md](docs/03_candidates.md) 的 Top-1 推荐——
但**该结论已被 Stage 2 修订**：「无人按干净性能归一化」是错的（PDR 已存在），
存活的问题收窄为「PDR 的比例假设从未被检验」。见 [docs/06_stage2_audit_result.md](docs/06_stage2_audit_result.md)。

## 证据纪律

- 所有事实必须能追溯到原始论文（proceedings / publisher / OpenReview / arXiv）。
- 不确定的信息标注 `[NOT VERIFIED]`，不猜测。
- 禁止写 "No one has studied this"，只能写"在本次检索覆盖范围内未发现"，并附检索式。
- 本次检索的**已知局限**见 [docs/05_references.md](docs/05_references.md) 顶部。
