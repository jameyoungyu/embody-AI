# Stage 1-A：2022–2026 Embodied AI Research Landscape

> 检索时间：2026-08-23。检索方式与局限见 `05_references.md` 顶部。
> 论文编号形如 `2606.xxxxx` 表示 2026 年 6 月 arXiv 预印本——这些**超出我的训练知识**，
> 完全来自本次检索抓取的页面，引用前必须自行核实。

---

## 0. 先回答三个问题

### Q1：2024–2026 年社区到底在解决什么？

分四波，时间顺序很清楚：

**第一波（2022–2024）：造模型。**
RT-1/RT-2 → Octo（RSS 2024）→ OpenVLA（CoRL 2024）→ π0 / π0.5 → SpatialVLA / SmolVLA / Qwen-VLA。
主线是"用互联网预训练的 VLM 当 backbone + 动作头"，加上 Open X-Embodiment 做跨本体数据聚合。
Diffusion Policy（RSS 2023 / IJRR 2025）与 ACT 成为默认的小模型基线。

**第二波（2024–2025）：造 benchmark 与评测基础设施。**
LIBERO / CALVIN / RoboCasa / RoboTwin / COLOSSEUM → SIMPLER（CoRL 2024，仿真里评真机策略）
→ AutoEval（真机自动评测）→ RoboArena（CoRL 2025，分布式双盲众包评测）
→ RoboChallenge / RobotArena∞ / RoboDojo → 世界模型当评测器（WorldGym / dWorldEval / RoboWorld / GE-Sim）。
驱动力是一句话："**评测已经成为 robot learning 的瓶颈**"。

**第三波（2025–2026）：拆 benchmark。**
LIBERO-Plus（CVPR 2026）/ LIBERO-PRO / LIBERO-X / LIBERO-Para / VLATest / STRONG-VLA / NavTrust。
结论集中而尖锐：干净 benchmark 已饱和、存在捷径可解性、扰动一加就崩、
"SOTA 提升"大多不具统计显著性。

**第四波（2026 至今）：效率化 + 世界模型 + 人形。**
量化 / 蒸馏 / 小 VLA（QuantVLA、ActQuant、DA-PTQ、SmolVLA、ActDistill），
World-Action Model，人形全身操作与无机器人数据采集（HuMI、SUGAR）。

### Q2：哪些方向已经过度拥挤？

按拥挤度从高到低（🔴 = 半年内 5 篇以上直接竞品）：

1. 🔴 **给 VLA 加一个模态/模块**（加 depth、加 3D、加 flow、加 CoT、加 memory）——2026 年这是灌水重灾区。
2. 🔴 **VLA 鲁棒性 benchmark**（LIBERO-* 家族已经至少 4 个变体）。
3. 🔴 **VLA 量化/蒸馏/加速**（半年内 ≥6 篇）。
4. 🔴 **世界模型做策略评测器**（半年内 ≥6 篇）。
5. 🟠 **失败检测 / 运行时监控**（RSS 2025 + NeurIPS 2025 已占坑，后续跟进密集）。
6. 🟠 **视角/相机鲁棒性**（外参条件化、免标定、视角增广，2025-10 至 2026-07 至少 5 篇）。
7. 🟠 **触觉跨传感器不变表征**（ICLR 2025 之后被快速填满）。
8. 🟠 **语言 grounding 失效与修复**（"VLA 无视语言"已被反复报道并已有多种解法）。

### Q3：哪里还有明显 gap？

**不在"再做一个 benchmark"或"再提一个鲁棒模块"，而在测量层面：**

- **G1（最大空隙）**：所有鲁棒性论文都在比"扰动下的成功率"，但没人控制**干净成功率**这个混杂变量。
  图像分类领域早在 2020 年就确立了 `effective robustness` 方法学（Taori et al., NeurIPS 2020），
  机器人领域**在本次检索范围内未见任何应用**。
- **G2**：闭环控制特有的机制问题——每步扰动如何沿任务时域复合成 episode 级失败？
  这决定了 ID→OOD 关系的函数形式，而分类领域的线性律**不应该**直接成立。
- **G3**：鲁棒性排名的**测量可靠性**——benchmark 之间、seed 之间、checkpoint 之间是否会翻转？
  已有工作（2606.04233）做了干净分数的显著性检验，但没做鲁棒性维度。
- **G4**：抓取检测这类"成熟感知任务"缺一个 ImageNet-C 式的系统性 corruption 鲁棒性研究；
  自动驾驶领域早已有 RoboDepth / Robo3D，抓取领域**本次检索未发现对应工作**。
- **G5**：检测器级指标（AP）与执行级指标（抓取成功率）在扰动下是否同步退化——无人系统性检验。

---

## 1. Research Landscape 主表

拥挤度：🔴 过热 / 🟠 拥挤 / 🟡 适中 / 🟢 有空隙
4080 适配：✅ 可做 / ⚠️ 需裁剪 / ❌ 不可行

| # | 方向 | 代表工作 | 当前主流方法 | 已解决 | 仍存在问题 | 4080 | 拥挤度 | 创新机会 |
|---|------|---------|------------|-------|-----------|------|-------|---------|
| 1 | VLA 通用策略 | OpenVLA (2406.09246, CoRL'24)；Octo (RSS'24)；π0/π0.5；SpatialVLA (2501.15830)；SmolVLA (2506.01844)；VLANeXt (2602.18532) | VLM backbone + 离散/flow 动作头 + OXE 预训练 + 下游 LoRA | 多任务单臂桌面操作在仿真上接近饱和 | 真正的跨环境泛化未解决；"通才"实为"训练环境专才" | ⚠️ 仅推理/LoRA | 🔴 | 极低——不要碰架构 |
| 2 | VLA 效率化 | QuantVLA (2602.20309)；ActQuant (2605.24011)；DA-PTQ (2604.11572)；EaqVLA (2505.21567)；QAIL (2412.01034)；ActDistill (2511.18082) | PTQ / QAT / 蒸馏 / 小 backbone | W8A8 基本无损；边缘部署可行 | 压缩对**扰动下**行为的影响缺系统结论；时序误差累积 | ✅ 纯推理 | 🔴 方法侧 / 🟡 分析侧 | 中——只在"压缩×鲁棒性"分析侧 |
| 3 | VLA 鲁棒性 benchmark | LIBERO-Plus (2510.13626, CVPR'26)；LIBERO-PRO (2510.03827)；LIBERO-X (2602.06556)；LIBERO-Para (2603.28301)；VLATest；NavTrust (2603.19229) | 7 轴受控扰动 + 分级 + 排行榜 | 已确认：视角/初始位姿最致命（95%→<30%）；语言基本被无视 | **测量方法学空白**：无人控制干净性能这一混杂变量 | ✅ | 🔴 造 benchmark / 🟢 测量方法学 | **高——见 G1/G2** |
| 4 | Benchmark 有效性 / 统计方法学 | What Are We Actually Benchmarking in Robot Manipulation? (2606.04233) | 显著性检验 + 捷径探针 + 跨 benchmark 一致性 | LIBERO/SimplerEnv 仅 ~19.8%/19.7% 的 SOTA 声明可证显著；0.09B 探针接近 SOTA | 只覆盖**干净**分数；鲁棒性声明的可靠性未查 | ✅ | 🟡 | **高——G3** |
| 5 | 真机/大规模评测 | RoboArena (2506.18123, CoRL'25)；AutoEval (2503.24278)；RoboChallenge (2510.17950)；RobotArena∞ (2510.23571, ICLR'26) | 众包双盲 / 真机自动化 / real-to-sim | 排名可信度显著优于集中式评测 | 需要真机或大规模基建 | ❌ | 🟠 | 低（资源门槛） |
| 6 | 世界模型评测器 | WorldGym (2506.00613)；dWorldEval (2604.22152)；RoboWorld (2607.01060)；GE-Sim 2.0 (2605.27491) | 视频世界模型 rollout + 与真机相关性 | 报告 Pearson r 达 0.9–0.95 | 相关性是否在**扰动条件**下仍成立？未见检验 | ❌ 训练 / ⚠️ 用现成 | 🔴 | 中（但依赖他人模型） |
| 7 | 6-DoF 抓取检测 | GraspNet-1B (CVPR'20 / IJRR'23 42(12))；AnyGrasp；Economic Grasp (2407.08366)；GraspGen (2507.13097)；GraspGen-X (2606.00998)；GraspClutter6D (2504.06866) | 点云 backbone + 抓取采样/打分；扩散式生成 + 判别器 | 杂乱场景通用抓取工程上可用（真机 ~81%） | 无 ImageNet-C 式系统 corruption 研究；AP↔真实成功率脱节被反复提及但未系统量化 | ✅ 推理免训练 | 🟡 | **高——G4/G5** |
| 8 | RGB-D 感知 / 深度质量 | Depth Hole Filling for Robust Grasp Detection (IEEE'21)；DREDS；TransCG；SpikeGrasp (2510.10602) | 深度补全 / inpainting / 最近非零像素填充 | 深度洞的**修补方法**已成熟 | 无效深度的**分布效应**（归一化统计漂移）无跨模型量化 | ✅ | 🟡 | 中（significance 需谨慎） |
| 9 | 3D 点云策略 | DP3 (2403.03954 系)；iDP3 (2410.10803)；EquiForm (2601.17486)；Twin-DP3 | 稀疏点云编码 + 扩散策略 | 几何输入对视觉扰动更稳 | 仿真点云"过于干净"，真实传感器噪声下的系统退化缺跨模型证据 | ✅ | 🟡 | 中 |
| 10 | 触觉 / 多模态融合 | SITR (2502.19638, ICLR'25)；T3 (2406.13640)；AnyTouch 2 (2602.09617)；UniTac (2606.31451)；FTP-1 (2606.13102) | 跨传感器不变表征 + 大规模触觉预训练 | 跨 GelSight 家族迁移基本可做 | 需要真实触觉硬件才能验证 | ❌ 无硬件 | 🟠 | 低（硬件门槛） |
| 11 | 模仿学习 shortcut / 因果混淆 | Do You Need Proprioceptive States? (2509.18644)；Shortcut Learning in Generalist Robot Policies (2508.06426)；Adapt Your Body (2506.23944)；Past-Token Prediction (2505.09561)；Fighting Copycat (NeurIPS'20) | 去 state 输入 / 数据多样性 / 过去 token 预测 | 本体感受捷径、copycat、静态背景推相机位姿捷径均已被指认 | 新捷径的**发现**仍可能有空间，但主要几条已被占 | ✅ | 🟠 | 低–中 |
| 12 | 失败检测 / 运行时监控 | FAIL-Detect (RSS'25)；FIPER (2510.09459, NeurIPS'25)；ActProbe (2606.08508)；Foresight (2606.23085) | OOD 分数 + 动作熵 + conformal prediction | 无需失败数据即可预测失败 | 与鲁棒性研究的接口（扰动下监控器是否也失效）未打通 | ✅ | 🟠 | 中 |
| 13 | 数据 / scaling law | Data Scaling Laws in IL (2410.18647, ICLR'25)；OXE；co-training 研究 (2602.01067, 2606.06627) | 环境×物体多样性幂律；质量加权采样 | 多样性 > 数量已成共识 | 需要大规模采集才能推进 | ❌ | 🟡 | 低（数据门槛） |
| 14 | 跨本体 / 人形 / 灵巧手 | HuMI (2602.06643)；SUGAR (2605.20373)；Sim-to-Real Dexterous (2502.20396)；AnyBody (2505.14986) | 人类视频 → 人形技能；RL sim-to-real | 部分单任务灵巧技能可零样本迁移 | 双臂接触丰富任务、奖励设计仍开放 | ❌ | 🟠 | 低（硬件门槛） |
| 15 | 具身导航 VLN | NaviTrace (2510.26909)；NavBench；NavTrust (2603.19229)；VLN 真机评测综述 (2607.09792) | VLM 零样本导航 + 轨迹评测 | 目标定位是主导失败模式已被指认 | sim→real 退化机制（光照/运动模糊）缺跨模型量化 | ✅ 仿真 | 🟡 | 中 |

---

## 2. 关键"已被解决/已被占坑"的事实（防止重复造轮子）

以下都是**别人已经做完**的，写进任何 proposal 前请先确认自己没有在重复：

| 你可能想做的 | 已有工作 | 状态 |
|---|---|---|
| "VLA 对相机视角很敏感" | LIBERO-Plus (2510.13626) 已量化：视角是最致命扰动轴 | ❌ 已占 |
| "VLA 其实没在听指令" | LIBERO-Plus 明确报告"模型倾向于完全忽略语言指令"；CAST (2508.13446)、2603.06001 已提解法 | ❌ 已占 |
| "本体感受输入让策略走捷径" | Do You Need Proprioceptive States? (2509.18644) 提出 State-free Policy | ❌ 已占 |
| "策略用静态背景反推相机位姿" | Do You Know Where Your Camera Is? (2510.02268) 已指认此捷径 | ❌ 已占 |
| "LIBERO 训练/测试太像，已经饱和" | LIBERO-PRO (2510.03827)、2606.04233（0.09B 探针接近 SOTA） | ❌ 已占 |
| "机器人论文的 SOTA 提升不显著" | 2606.04233：LIBERO 仅 19.8% 声明可证显著 | ❌ 已占（干净分数部分） |
| "触觉传感器换一个就失效" | SITR (ICLR'25)、T3、AnyTouch 2、UniTac | ❌ 已占 |
| "缺模态时多模态策略会崩" | ConD (2607.20326)、2606.15514、DisDP | ❌ 已占 |
| "深度图有洞会影响抓取" | Depth Hole Filling for Robust Grasp Detection (IEEE'21)；最近非零填充已是工程惯例 | ⚠️ 解法已占，机制量化未占 |
| "量化会掉点" | QuantVLA / ActQuant / DA-PTQ / EaqVLA / QAIL | ⚠️ 方法已占，分析未占 |
| "压缩模型会遗忘长尾" | Hooker et al. (1911.05248) 在视觉领域已确立 | ⚠️ 跨领域先例，迁移需额外贡献 |

---

## 3. 对我的条件（单张 RTX 4080 / 16 GB）的可行性结论

**可以做的：**
- 用已发布 checkpoint 做**推理级**大规模评测：OpenVLA-7B 4-bit 约 7.0 GB 显存，bf16 约 16 GB（勉强）；
  SmolVLA-450M、Octo-small、Diffusion Policy、ACT 都轻松。
- LIBERO / SimplerEnv / ManiSkill 仿真评测。
- 抓取检测：GraspNet 系模型推理 + 单模型微调（单卡可完成）。
- 小模型（≤1B）的多 seed 微调对照实验。

**不能做的：**
- 7B 级 VLA 的全量微调、任何预训练。
- 需要真机的 claim（触觉、人形、真实抓取成功率）——Pilot 阶段必须绕开。
- 世界模型训练。

**结论：** 我的资源结构天然适合**"用别人的模型回答别人没问的问题"**，
即评测/测量/机制类研究，而不是造模型类研究。这一约束应当主导选题，而不是被视为劣势。
