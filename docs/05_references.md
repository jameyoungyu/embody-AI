# 参考文献与核实状态

## ⚠️ 本次检索的已知局限（必须先读）

1. **无法直接打开 PDF**。本次会话的网络出口拦截了 `arxiv.org`、`openreview.net`、
   `proceedings.mlr.press`、`openaccess.thecvf.com`、`huggingface.co`、
   `api.semanticscholar.org` 等域名。所有论文事实来自**搜索引擎抓取并摘要的页面内容**，
   没有一篇是我逐段读过原文的。
2. 因此**所有条目在引用前必须自行核实**（标题、作者、会议、年份、数字）。
   尤其是数字（如 "19.8%"、"95%→<30%"）必须回原文确认。
3. 编号形如 `26xx.xxxxx` 的 arXiv 预印本超出我的训练知识（截至 2026-05），
   完全依赖检索结果，存在**页面本身错误或摘要失真**的可能。
4. 检索日期：**2026-08-23**。检索语言：英文。数据库：公开 Web 搜索
   （覆盖 arXiv listing、会议 proceedings 页、项目页、GitHub、期刊页）。

**核实等级标记：**
- `[V2]` 至少两条独立检索结果一致（标题 + ID + 结论）
- `[V1]` 仅单条结果支持
- `[NV]` 未核实 / 仅凭记忆，禁止直接引用

---

## VLA / 通用策略

| 文献 | ID / 出处 | 等级 |
|---|---|---|
| OpenVLA: An Open-Source Vision-Language-Action Model | 2406.09246, CoRL 2024 | `[V2]` |
| Octo: An Open-Source Generalist Robot Policy | RSS 2024 | `[V1]` |
| SmolVLA: A VLA Model for Affordable and Efficient Robotics | 2506.01844 | `[V2]` |
| SpatialVLA | 2501.15830 | `[V1]` |
| VLA Foundry (TRI-ML) | 2604.19728 | `[V2]` |
| VLANeXt: Recipes for Building Strong VLA Models | 2602.18532 | `[V1]` |

## 鲁棒性 benchmark / 评测批判

| 文献 | ID / 出处 | 关键结论 | 等级 |
|---|---|---|---|
| LIBERO-Plus: In-depth Robustness Analysis of VLA Models | 2510.13626；CVPR 2026 版题为 *A Progressive Robustness Benchmark for Visual-Language-Action Models* | 7 轴扰动；95%→<30%；模型倾向完全忽略语言；语言扰动平均降幅 −25.3（此数字**存疑，需核**） | `[V2]`（数字 `[V1]`） |
| LIBERO-PRO: Towards Robust and Fair Evaluation Beyond Memorization | 2510.03827 | 默认划分分布位移极小 → 死记硬背 | `[V2]` |
| LIBERO-X: Robustness Litmus for VLA Models | 2602.06556 | 多标签渐进扰动 | `[V1]` |
| LIBERO-Para: Paraphrase Robustness | 2603.28301 | 5 seeds × 每 task-paraphrase | `[V1]` |
| What Are We Actually Benchmarking in Robot Manipulation? | 2606.04233 | LIBERO/SimplerEnv 仅 19.8%/19.7% SOTA 声明显著；0.09B 探针≈SOTA；四种 benchmark 失效模式 | `[V2]` |
| VLATest: Testing and Evaluating VLA Models | — | 系统测试 VLA | `[V1]` |
| STRONG-VLA | 2604.10055 | 多模态扰动下的解耦鲁棒学习 | `[V1]` |
| StableVLA: Towards Robust VLA without Extra Data | 2605.18287 | — | `[V1]` |
| NavTrust: Benchmarking Trustworthiness for Embodied Navigation | 2603.19229 | 对 RGB/深度/指令做 corruption | `[V1]` |

## 评测基础设施

| 文献 | ID / 出处 | 等级 |
|---|---|---|
| RoboArena: Distributed Real-World Evaluation of Generalist Robot Policies | 2506.18123；CoRL 2025 (PMLR v305:336–364)；7 机构 / DROID / >600 对比 episode | `[V2]` |
| SIMPLER: Evaluating Real-World Robot Manipulation Policies in Simulation | CoRL 2024 | `[V2]` |
| AutoEval: Autonomous Evaluation of Generalist Robot Policies in the Real World | 2503.24278 | `[V1]` |
| RoboChallenge: Large-scale Real-robot Evaluation | 2510.17950 | `[V1]` |
| RobotArena∞: Scalable Robot Benchmarking via Real-to-Sim | 2510.23571；ICLR 2026 proceedings 链接 | `[V2]` |
| allenai/vla-evaluation-harness | GitHub | `[V1]` |

## 捷径学习 / 因果混淆

| 文献 | ID | 等级 |
|---|---|---|
| Do You Need Proprioceptive States in Visuomotor Policies?（State-free Policy） | 2509.18644 | `[V2]` |
| Shortcut Learning in Generalist Robot Policies: Dataset Diversity and Fragmentation | 2508.06426 | `[V2]` |
| Adapt Your Body: Mitigating Proprioception Shifts in Imitation Learning | 2506.23944 | `[V1]` |
| Do You Know Where Your Camera Is? View-Invariant Policy Learning with Camera Conditioning | 2510.02268 | `[V2]` |
| Learning Long-Context Diffusion Policies via Past-Token Prediction | 2505.09561 | `[V2]` |
| Fighting Copycat Agents in Behavioral Cloning from Observation Histories | NeurIPS 2020 | `[V2]` |

## 抓取

| 文献 | ID / 出处 | 等级 |
|---|---|---|
| GraspNet-1Billion: A Large-Scale Benchmark for General Object Grasping | CVPR 2020 | `[V2]` |
| Robust grasping across diverse sensor qualities: The GraspNet-1Billion dataset | IJRR 2023, 42(12) | `[V2]` |
| Generalizing 6-DoF Grasp Detection via Domain Prior Knowledge | CVPR 2024, pp.18102–18111；2404.01727 | `[V2]` |
| An Economic Framework for 6-DoF Grasp Detection | 2407.08366 | `[V1]` |
| GraspGen: A Diffusion-based Framework for 6-DOF Grasping | 2507.13097（NVIDIA，53M 仿真抓取，真机 81.3%） | `[V2]` |
| GraspGen-X: Cross-Embodiment 6-DOF Diffusion-based Grasping | 2606.00998 | `[V1]` |
| GraspClutter6D | 2504.06866 | `[V1]` |
| Depth Hole Filling based on Deep Learning for Robust Grasp Detection | IEEE (2021) | `[V1]` |

## 鲁棒性度量方法学（跨领域先例，C1 的理论基础）

| 文献 | ID / 出处 | 等级 |
|---|---|---|
| Measuring Robustness to Natural Distribution Shifts in Image Classification（effective robustness） | NeurIPS 2020；2007.00644 | `[V2]` |
| Models Out of Line: A Fourier Lens on Distribution Shift Robustness | NeurIPS 2022 | `[V1]` |
| Effective Robustness against Natural Distribution Shifts for Models with Different Training Data | 2302.01381 | `[V1]` |
| What Do Compressed Deep Neural Networks Forget? | 1911.05248 | `[V2]` |
| RoboDepth: Robust OOD Depth Estimation under Corruptions | 2310.15171；NeurIPS 2023；18 corruption × 42 模型 | `[V2]` |
| Robo3D: Towards Robust and Reliable 3D Perception against Corruptions | ICCV 2023；8 corruption × 3 级 × 4 数据集 | `[V2]` |
| Accuracy on the Line (Miller et al., ICML 2021) | — | `[NV]` 概念在检索中出现，原文未核实 |

## 失败检测 / 部署

| 文献 | ID / 出处 | 等级 |
|---|---|---|
| FAIL-Detect | RSS 2025 (rss21/p073) | `[V1]` |
| Failure Prediction at Runtime for Generative Robot Policies (FIPER) | 2510.09459；NeurIPS 2025 | `[V2]` |
| DA-PTQ: Drift-Aware Post-Training Quantization for VLA | 2604.11572 | `[V1]` |
| QuantVLA / ActQuant / EaqVLA / QAIL | 2602.20309 / 2605.24011 / 2505.21567 / 2412.01034 | `[V1]` |
| Same Weights, Different Robot: A Deployment Safety View of VLA Policies | 2606.03724 | `[V1]` |

## 数据 / 其他

| 文献 | ID / 出处 | 等级 |
|---|---|---|
| Data Scaling Laws in Imitation Learning for Robotic Manipulation | 2410.18647；ICLR 2025 | `[V2]` |
| Sensor-Invariant Tactile Representation (SITR) | 2502.19638；ICLR 2025 | `[V2]` |
| Toward Reliable RGB-D Semantic Segmentation: Condition Dropout | 2607.20326 | `[V1]` |
| EquiForm: Noise-Robust SE(3)-Equivariant Policy Learning from Point Clouds | 2601.17486 | `[V1]` |
| NaviTrace: Evaluating Embodied Navigation of VLMs | 2510.26909 | `[V1]` |

## `[NV]` 凭印象提到、本次未核实（禁止引用，需自查）

- Bidirectional Decoding（动作块 consistency vs reactivity 权衡）
- Real-Time Chunking（π 系列的实时动作块执行）
- THE COLOSSEUM（RSS 2024，14 轴扰动泛化基准）
- Diffusion Policy（RSS 2023 / IJRR 2025）、ACT / ALOHA
- DP3 / iDP3 的具体编号
- Ross & Bagnell 的复合误差理论界

---

## 本次使用的检索式（供复现与 Stage 2 扩展）

检索日期 2026-08-23，全部经由公开 Web 搜索：

```
vision-language-action model failure modes robustness evaluation 2025 arxiv
LIBERO-Plus robustness analysis vision-language-action models perturbation
imitation learning policy over-reliance proprioception state input shortcut visual generalization robot
robot learning evaluation protocol flaws seed variance checkpoint selection reproducibility CoRL 2025
6-DoF grasp detection depth sensor noise missing depth robustness benchmark GraspNet real-world failure
"real-to-sim" OR "simulation evaluation" correlation real robot success rate policy ranking 2025 2026
RoboArena distributed real-world evaluation generalist robot policies 2025
Open X-Embodiment data quality curation noisy demonstrations negative transfer cross-embodiment 2025
camera viewpoint generalization manipulation policy calibration extrinsics robustness 2025 2026
missing modality robustness RGB-D manipulation policy depth dropout modality collapse fusion
LIBERO benchmark saturation train test overlap leakage manipulation benchmark criticism
action normalization statistics vision-language-action policy dataset-specific quantile denormalization effect
tactile sensor cross-sensor generalization representation transfer GelSight DIGIT 2025 2026
failure detection uncertainty out-of-distribution detection robot manipulation policy runtime monitoring 2025
grasp detection cross-sensor generalization RealSense Kinect GraspNet-1Billion train one camera test another
does depth help vision-language-action model 3D input ablation RGB-only manipulation policy
vision-language navigation failure modes analysis 2026 embodied navigation generalization gap real world
quantized VLA robustness distribution shift INT4 quantization degrades generalization robot policy evaluation
observation history hurts imitation learning policy causal confusion copycat diffusion policy 2024 2025
"VLA Foundry" unified framework training vision-language-action controlled study findings design choices
"What Are We Actually Benchmarking in Robot Manipulation" LIBERO significance probe 0.09B
3D diffusion policy point cloud depth noise real sensor robustness DP3 simulation clean point cloud gap
VLA language grounding evaluation instruction following distractor objects policy ignores instruction wrong object
grasp detection benchmark AP metric correlation with real robot grasp success rate criticism evaluation
depth hole filling inpainting preprocessing effect grasp detection performance invalid depth zero pixels
robustness ranking unstable across random seeds fine-tuning variance robustness evaluation deep learning benchmark
"effective robustness" OR "accuracy on the line" distribution shift linear trend clean accuracy robot policy manipulation
data augmentation random crop preprocessing dominates vision-language-action fine-tuning ablation more than architecture
robustness metric relative drop retention rate normalize clean success rate confound comparing models robustness
in-distribution out-of-distribution success rate correlation across robot policies linear relationship generalization measurement manipulation
"What Do Compressed Deep Neural Networks Forget" pruning quantization disparate impact robustness long tail
inference hyperparameters action horizon temporal ensembling sampling steps confound comparison manipulation policy evaluation unfair
data scaling laws imitation learning robotic manipulation environment object diversity demonstrations power law
world model policy evaluation robot manipulation video prediction 2026 trend generative simulator
SmolVLA efficient vision-language-action model consumer GPU single GPU training LeRobot 450M
stronger VLA models more robust or less robust clean success rate correlates perturbation drop LIBERO-Plus leaderboard finding
"Generalizing 6-DoF Grasp Detection via Domain Prior Knowledge" CVPR 2024 cross-camera Kinect RealSense experiment
"Robust grasping across diverse sensor qualities" GraspNet-1Billion IJRR 2023 cross-sensor analysis findings
GraspGen grasp foundation model 2025 2026 generalizable grasping diffusion sim data NVIDIA
"reality check" OR "sober look" OR "rethinking" fair re-evaluation vision-language-action robot manipulation matched training comparison 2026
VLA evaluation variance number of evaluation episodes error bars random seeds LIBERO statistical power robot policy
robustness trained on one perturbation type does not transfer held-out corruption augmentation overfitting robot policy
OpenVLA LoRA fine-tuning GPU memory requirement 24GB single GPU inference 4-bit quantization
corruption robustness benchmark grasp detection RGB-D like ImageNet-C common corruptions robotic grasping evaluation
Robo3D RoboDepth robustness benchmark corruptions point cloud depth estimation autonomous driving out-of-distribution
dexterous manipulation humanoid whole-body learning 2026 trends bimanual sim-to-real open challenges
```

**"没人做过"的正确表述**（本报告统一采用）：

> 在本次检索覆盖的数据库（公开 Web 搜索，含 arXiv listing / 会议 proceedings 页 / 项目页 / GitHub）、
> 上列关键词与同义词、时间范围 2019–2026-08 内，未发现直接解决该问题的论文。
> 最近邻工作见各候选的 "Closest Literature"。
