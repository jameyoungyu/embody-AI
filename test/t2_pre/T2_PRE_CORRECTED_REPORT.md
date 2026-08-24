# T2-PRE 预试验报告（严格学术规范版）：公开基准动机分析、经验现象与受控识别方案

> **科学状态定性**：
> $$\boxed{\text{Pre-pilot = strong signal, not confirmatory evidence}}$$  
> **战略决策结论**：**Strong GO**（值得投入 GPU 正式实验；公开数据提供了强力研究动机，但核心科学结论必须由正式受控实验建立）  
> **核心研究切入命题**：
> $$\boxed{\textbf{Can robustness be fairly compared across robot policies with different nominal capability?}}$$
> **数据源版本冻结与访问声明**：
> 1. **LIBERO-Plus**：数据采用 **CVPR 2026 Camera-Ready Table 1 / arXiv:2510.13626 v1** 冻结版本（包含 10 个代表性模型在 7 个扰动轴上的评测）。注：官方 benchmark 包含 10,030 个扰动任务（1 trial/task），原始 clean 基线基于 40 个基础任务（50 trials/task）。
> 2. **EBench**：数据采用 **arXiv:2606.18239 v1 Table 2** 冻结版本（包含 4 个模型在 Val-Train 130 eps 与 Test 510 eps 上的 3 次运行均值与标准差）。

---

## 一、数据版本冻结与 Matched Clean–OOD 配对设计

### 1. 数据版本冻结规范
为避免混淆 arXiv v1、CVPR 2026 Camera-Ready 与 GitHub Leaderboard 之间可能存在的微调差异（例如 OpenVLA 在部分评测分支中的数值变动），本项目预分析严格冻结以 **CVPR 2026 Camera-Ready / arXiv:2510.13626 v1 Table 1** 为唯一比对基准。

### 2. 评测协议差异与宏观混合（Task Mixture）鸿沟
当前公开表格存在一个深层次的度量匹配问题：
- **Clean SR**：评测于原始 LIBERO 的 40 个 base tasks（各 task 50 trials，总计 2,000 trials）。
- **OOD SR**：评测于由 40 个 base tasks 派生出的 $10,030$ 个扰动变体（每个变体仅跑 1 trial）。各轴任务分布为：
  - Camera: 1599
  - Robot: 1550
  - Language: 1537
  - Light: 1142
  - Background: 1076
  - Noise: 1601
  - Layout: 1525

若不同 base task 在某一扰动轴下派生出的变体数量不均匀，则宏观公布的 $p_{\text{clean, overall}}$ 与 $p_{\text{OOD, axis}}$ 实际上对应了**不同的任务混合权重（Task Mixture）**。

因此，当前公开表格的分析在科学严谨度上定性为：
$$\text{Aggregate clean score} \quad\text{与}\quad \text{Aggregate OOD score} \quad\text{之间存在宏观结构关系}$$
它不能直接视为严格 matched 的 clean $\to$ OOD 演化。

### 3. 正式 T1 实验的 Seed-Level Matched Clean–OOD 方案
正式 T1 受控实验将不再使用宏观平均，而是实行严格的 **Episode-Level 配对观测（Paired Observation）**：
$$\boxed{\text{Same Task} + \text{Same Initial State} + \text{Same Random Seed} + \text{Only Perturbation Differs}}$$

对于同一模型 Checkpoint，在配对 episode $(Y^{\text{clean}}_{ij}, Y^{\text{OOD}}_{ij})$ 下直接构建 $2 \times 2$ 状态转移矩阵：

| Clean 结果 ($Y^{\text{clean}}$) | OOD 结果 ($Y^{\text{OOD}}$) | 状态分类 | 物理/策略意义 |
|:---:|:---:|:---:|---|
| **1** | **1** | **保持成功 (Retention)** | 策略具备有效抗扰能力 |
| **1** | **0** | **扰动导致失败 (Perturbation Failure)** | **模型本身会做，但被扰动破坏** |
| **0** | **1** | **异常改善 (Anomalous Gain)** | 噪声导致的偶发命中/探索成功 |
| **0** | **0** | **基线缺陷 (Baseline Incapacity)** | 模型在无扰动下即无法完成 |

在此配对框架下，我们可以直接计算比宏观 PDR 更自然、更具物理意义的条件失效概率：
$$\boxed{P(Y_{\text{OOD}} = 0 \mid Y_{\text{clean}} = 1)}$$
即：**“模型本来能成功完成的 episode 中，有多少比例因为环境扰动而被破坏？”** 这将作为 T1 核心度量之一。

---

## 二、公开数据探索性诊断：三大核心经验现象（Three Observations）

公开基准数据虽然存在混杂，但同时展现出三个具有极高研究价值的物理现象：

### Observation 1 — Capability-associated structure（能力关联结构）
> **Clean 与 OOD performance 之间存在明显的结构性关联，且公开数据并不支持用一个简单的固定比例关系充分描述所有模型。**

为了探索不同函数形式的描述能力，我们考察两种基准形式并检验核心科学命题：
$$\boxed{\text{命题：性能保持率 } R = \frac{p_{OOD}}{p_{clean}} \text{ 是否系统性依赖于基线能力 } p_{clean} \text{？}}$$

#### 表 1：LIBERO-Plus 公开数据探索性回归诊断（M=10 模型）
| 扰动轴 (Axis) | 真实任务数 $N_d$ | Log-Log OLS $\hat{\gamma}$ | Log-Log 95% CI | Logit-Logit OLS $\hat{\beta}$ | Logit-Logit 95% CI | Spearman(PDR, -ER) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Camera** | 1599 | **15.744** | $[4.52, 26.97]$ | **1.694** | $[0.32, 3.07]$ | **-0.030** |
| **Robot** | 1550 | **4.719** | $[-1.89, 11.33]$ | **0.492** | $[-0.30, 1.29]$ | **0.382** |
| **Language** | 1537 | **3.533** | $[2.23, 4.83]$ | **0.775** | $[0.49, 1.06]$ | **0.236** |
| **Light** | 1142 | **8.718** | $[4.18, 13.26]$ | **1.494** | $[0.77, 2.22]$ | **-0.188** |
| **Background** | 1076 | **6.370** | $[3.98, 8.76]$ | **1.398** | $[0.85, 1.94]$ | **-0.042** |
| **Noise** | 1601 | **5.831** | $[1.10, 10.57]$ | **0.958** | $[0.11, 1.81]$ | **0.176** |
| **Layout** | 1525 | **2.602** | $[0.19, 5.01]$ | **0.533** | $[0.03, 1.04]$ | **0.115** |

> 📌 **方法论定性**：
> 1. **描述性诊断定位**：Camera 等轴存在部分模型接近地板（如 $0.3\%, 1.1\%$），导致对数回归对极小值敏感且存在异方差。此处的 OLS 结果严格定位为**探索性诊断（Exploratory Diagnostic）**，正式推断必须由受控实验完成。
> 2. **函数形式开放性**：正式实验将系统比对 Linear、Log-Log、Logit-Logit 与 Monotonic Spline/GAM，不预先假设真实世界必须服从单一幂律。

---

### Observation 2 — Large conditional heterogeneity（巨大的条件异质性）
> **即使在相近的高基线能力（$p_{clean} \approx 0.95 \sim 0.98$）下，不同模型的 OOD 表现仍然出现巨大的垂直离散（Vertical Spread：$4.3\% \sim 59.7\%$），表明 clean capability 并不能充分解释鲁棒性。**

#### 表 2：高基线能力模型（$p_{clean} \ge 94\%$）的 OOD 垂直离散
| 模型 | Clean SR | Camera OOD | Light OOD | Robot OOD | Noise OOD | 关键架构与配置特征 |
|---|:---:|:---:|:---:|:---:|:---:|---|
| **OpenVLA-OFT** | $97.1\%$ | **$59.7\%$** | $85.8\%$ | $37.2\%$ | $76.7\%$ | 配备 Wrist Camera |
| **OpenVLA-OFT_w** | $95.3\%$ | **$16.8\%$** | $68.2\%$ | $43.7\%$ | $51.4\%$ | 仅 Third-view（无 Wrist） |
| **OpenVLA-OFT_m** | $97.6\%$ | **$57.9\%$** | $91.6\%$ | $30.6\%$ | $76.3\%$ | 多模态微调策略 |
| **$\pi_0$** | $94.2\%$ | **$15.8\%$** | $79.6\%$ | $6.6\%$ | $79.4\%$ | 基础 Flow-matching VLA |
| **UniVLA** | $95.2\%$ | **$4.3\%$** | $59.1\%$ | $50.3\%$ | $25.3\%$ | 统一感知头架构 |
| **RIPT-VLA** | $97.5\%$ | **$58.3\%$** | $87.9\%$ | $36.7\%$ | $73.8\%$ | 鲁棒策略预训练 |

$$\boxed{p_{clean} \approx 95\% \implies p_{Camera\_OOD} \in [4.3\%, 59.7\%]}$$

**理论启发**：这指导我们将机器人策略的鲁棒性严格分解为两个正交分量：
1. **基础能力效应（Capability Effect）**：$E[p_{OOD} \mid p_{clean}]$；
2. **架构/训练特异性残差（Architecture/Training Residual）**：$ER = p_{OOD} - E[p_{OOD} \mid p_{clean}]$。

---

### Observation 3 — Metric-dependent ranking（度量依赖型排序不一致）
> **PDR 排序与基于能力校准的 reference ranking 呈现较大的排序不一致（$\rho_s \in [-0.188, 0.382]$）。**

- 在 7 个扰动轴上，PDR 排序与残差排序的相关性普遍很低，Camera（$\rho_s = -0.030$）与 Light（$\rho_s = -0.188$）甚至呈现负相关趋势。
- **验证 PDR 误导性的黄金标准**：不依赖小样本的相关系数，而是在 T2 中通过 **Held-Out Intervention Validation（留出干预验证）** 进行确证——即检验在相同 $p_{clean}$ 下具备物理鲁棒机制（如 Wrist Camera, Domain Randomization）的策略是否会在传统 PDR 榜单中被反常压低。

---

## 三、EBench 作为 Narrow-Range Negative Control 的指导价值

EBench（arXiv:2606.18239 Table 2）4 个模型的干净成功率聚集在 $28.3\% \sim 33.1\%$（$\Delta p_{clean} = 4.8\%$，极窄区间），拟合结果 $\hat{\gamma} = 1.006$（95% CI: $[-1.65, 3.66]$, $p = 0.993$）。

**方法论定位**：EBench 充当了完美的 **低功效反例（Negative Control）**。它证实：
$$\boxed{\text{如果 } p_{\text{clean}} \text{ 的动态范围太窄，capability dependence 在统计上根本不可识别}}$$

### 对正式 T1 Checkpoint 实验设计的预冻结约束：
1. **严格禁止后验挑选（No Cherry-Picking）**：
   - 必须**仅根据 Clean Validation 成功率预先选择 Checkpoint**，严禁在观测 OOD 结果后反向挑选权重。
   - 预设 7 个能力区间 Bin：
     $$[0.25, 0.35), [0.40, 0.50), [0.55, 0.65), [0.68, 0.76), [0.78, 0.86), [0.88, 0.92), [0.93, 0.98)$$
     在每个 Bin 中选取距离目标最近的 Checkpoint。
2. **多 Seed 训练覆盖**：
   - 采用 $3 \text{ training seeds} \times 7 \text{ capability levels} = 21$ 个受控点位，避免单条训练轨迹的随机偶然性。
3. **高能力子集分层报告**：
   - 除全量拟合外，单独报告 $p_{clean} \ge 0.70$ 的高能力子集，彻底消除“结论仅由低能力退化权重驱动”的审稿顾虑。

---

## 四、族内受控识别实验方案（T1 Controlled Within-Family Identification）

因 Checkpoint 推进不仅改变成功率，同时还会伴随表征质量、动作平滑度与校准特性的变化，故正式实验定性为 **Controlled Within-Family Identification（族内受控识别）**。

### 7 步实验推进阶梯（7-Step Execution Queue）

```
Step 1: 族内多 Checkpoint 宽幅采样 (Within-family Checkpoint Identification)
   │    • 单一模型架构固定 (如 Diffusion Policy / ACT)
   ▼    • 3 Seeds × 7 Bins 覆盖 25% ~ 95% Clean SR 宽动态范围
Step 2: 严格 Seed-Level Matched Clean-OOD 配对评测
   │    • 同一 Initial Seed、同一 Task，计算 P(Y_OOD=0 | Y_clean=1)
   ▼
Step 3: 多函数形式对比拟合 (Functional Form Comparison)
   │    • 对比 Linear, Log-Log, Logit-Logit, Monotonic Spline/GAM
   ▼
Step 4: 任务/Checkpoint 分层随机效应模型与 Cluster Bootstrap
   │    • 建立分层模型，给出稳健标准误与置信区间
   ▼
Step 5: 预先冻结主要假设与排除标准 (Pre-registered Hypotheses)
   │    • 锁定主度量与 floor 剔除阈值（如 p < 0.02）
   ▼
Step 6: 跨架构泛化验证 (Cross-Architecture Validation)
   │    • 拓展至 ACT, Diffusion Policy, OpenVLA, SmolVLA, π0 类模型
   ▼
Step 7: 留出鲁棒干预验证与闭环 Horizon 机制解释
        • 验证 Held-out Intervention 下的 PDR 排名逆转
        • 建立闭环误差自回归累积的 Horizon collapse 物理模型
```

---

## 五、项目状态评估与目标定位

| 评估维度 | 当前客观状态判断 |
|---|---|
| **继续推进必要性** | **非常有必要（Strong GO）** |
| **立项与动机数据** | **充分且极具说服力（三大 Observation 支撑）** |
| **核心结论状态** | **假说已明确，待受控实验确证** |
| **公开表格再挖掘价值** | **极低（已完成动机使命，不再多轮重复挖掘）** |
| **主要研究风险** | **受控实验中能力依赖效应弱于预期**（已通过宽幅 Bin 与多 Seed 控制） |
| **最大潜在突破** | **族内受控关系确立 + 真实具身策略 Ranking Reversal** |
| **主投目标会议** | **ICRA / IROS / RA-L** |
| **高阶冲击目标** | **CoRL**（若 Horizon 机制与干预排名逆转高度扎实） |

---

## 附录：潜变量二项似然模型探索性诊断（Appendix Diagnostic Only）

> ⚠️ **方法论批注**：本附录保留潜变量二项似然模型（Latent-Binomial Profile MLE）的估计结果，仅用于**方法论诊断演示**：若在统计推断中忽略跨模型架构异质性方差（$u_{arch}, u_{train}$），纯二项抽样方差会导致推断输出极端非物理的超低 $p$ 值。此模型不作为主文推断依据。

| 扰动轴 (Axis) | 真实任务数 $N_d$ | 潜变量二项 $\hat{\gamma}$ | 似然比检验 $\chi^2$ 统计量 | LRT $p$ 值 | 诊断备注 |
|---|:---:|:---:|:---:|:---:|---|
| **Camera** | 1599 | **36.928** | $5173.56$ | $< 10^{-300}$ | 忽略跨模型架构方差，SE 严重低估 |
| **Robot** | 1550 | **11.577** | $846.43$ | $4.34 \times 10^{-186}$ | 忽略跨模型架构方差，SE 严重低估 |
| **Language** | 1537 | **3.551** | $636.69$ | $1.75 \times 10^{-140}$ | 忽略跨模型架构方差，SE 严重低估 |
| **Light** | 1142 | **9.218** | $2183.20$ | $< 10^{-300}$ | 忽略跨模型架构方差，SE 严重低估 |
| **Background** | 1076 | **6.428** | $1527.24$ | $< 10^{-300}$ | 忽略跨模型架构方差，SE 严重低估 |
| **Noise** | 1601 | **12.076** | $3245.30$ | $< 10^{-300}$ | 忽略跨模型架构方差，SE 严重低估 |
| **Layout** | 1525 | **4.222** | $703.78$ | $4.51 \times 10^{-155}$ | 忽略跨模型架构方差，SE 严重低估 |
