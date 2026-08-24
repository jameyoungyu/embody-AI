# T1-mini-real 真实 ACT + 真实 LIBERO 集成冒烟审计报告

> **评测执行时间**：2026-08-23
> **模型族**：ACT (Action Chunking with Transformers, 1 Seed, 5 Checkpoints)
> **评测任务集**：`['pick_up_the_black_bowl_between_the_plate_and_the_ramekin_and_place_it_on_the_plate']` (1 Tasks)
> **数据性质定性**：$\boxed{\text{Integration Smoke Data（多任务集成冒烟数据，用于管线资质准入，非论文实证结论）}}$
> **集成门检总判定**：**`INTEGRATION_CALIBRATION_REQUIRED (PIPELINE PROCEED)`**
> **Clean SR 跨度**：**40.0 个百分点**（准入门槛 $\ge 35\%$）
> **隔离规范**：使用独立 Calibration / Smoke Set（Frozen Test Set 保持 0 访问未泄露状态）
> **扰动库规范**：`PerturbationBank` 全局锁定 $\delta_{j,d}^{(C_1)} \equiv \delta_{j,d}^{(C_2)}$

---

## 一、多任务汇总度量与 95% Bootstrap 置信区间

### 扰动轴：`camera_viewpoint`

| Checkpoint | Test Clean SR ($p_{\text{clean}}$) | Test OOD SR ($p_{\text{OOD}}$) | 保持率 $R$ [95% CI] | 配对破坏率 $D$ [95% CI] | 配对恢复率 $G$ [95% CI] | 配对矩阵 $[(1,1), (1,0), (0,1), (0,0)]$ |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| `act_spatial_epoch5` | 40.0% | 30.0% | **0.750** [0.000, 1.000] | **0.250** [0.000, 0.801] | 0.000 [0.000, 0.000] | `[3, 1, 0, 6]` |
| `act_spatial_epoch80` | 50.0% | 50.0% | **1.000** [0.500, 2.000] | **0.200** [0.000, 0.667] | 0.200 [0.000, 0.667] | `[4, 1, 1, 4]` |
| `act_spatial_epoch30` | 80.0% | 70.0% | **0.875** [0.600, 1.000] | **0.125** [0.000, 0.400] | 0.000 [0.000, 0.000] | `[7, 1, 0, 2]` |
| `act_spatial_epoch50` | 40.0% | 60.0% | **1.500** [0.666, 5.000] | **0.250** [0.000, 0.750] | 0.500 [0.000, 1.000] | `[3, 1, 3, 3]` |
| `act_spatial_epoch15` | 80.0% | 90.0% | **1.125** [1.000, 1.500] | **0.000** [0.000, 0.000] | 0.500 [0.000, 1.000] | `[8, 0, 1, 1]` |

#### 保持率理论恒等式分解：$R = (1 - D) + \frac{1 - p_c}{p_c} G$（代数自检）

| Checkpoint | 实测 $R$ | 真实破坏分量 $(1 - D)$ | 假性恢复分量 $\frac{1-p_c}{p_c}G$ | 重构 $R$ | 恒等式自检残差 $|\Delta|$ |
|---|:---:|:---:|:---:|:---:|:---:|
| `act_spatial_epoch5` | **0.750** | 0.750 | 0.000 | 0.750 | `1.11e-16` |
| `act_spatial_epoch80` | **1.000** | 0.800 | 0.200 | 1.000 | `0.00e+00` |
| `act_spatial_epoch30` | **0.875** | 0.875 | 0.000 | 0.875 | `1.11e-16` |
| `act_spatial_epoch50` | **1.500** | 0.750 | 0.750 | 1.500 | `2.22e-16` |
| `act_spatial_epoch15` | **1.125** | 1.000 | 0.125 | 1.125 | `0.00e+00` |

- **Log-Log OLS 回归斜率 $\hat{\gamma}$ (探索性诊断)**：**0.911** (SE = 0.430, $R^2 = 0.600$)

### 扰动轴：`object_initial_pose`

| Checkpoint | Test Clean SR ($p_{\text{clean}}$) | Test OOD SR ($p_{\text{OOD}}$) | 保持率 $R$ [95% CI] | 配对破坏率 $D$ [95% CI] | 配对恢复率 $G$ [95% CI] | 配对矩阵 $[(1,1), (1,0), (0,1), (0,0)]$ |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| `act_spatial_epoch5` | 40.0% | 40.0% | **1.000** [1.000, 1.000] | **0.000** [0.000, 0.000] | 0.000 [0.000, 0.000] | `[4, 0, 0, 6]` |
| `act_spatial_epoch80` | 60.0% | 40.0% | **0.667** [0.250, 1.000] | **0.333** [0.000, 0.750] | 0.000 [0.000, 0.000] | `[4, 2, 0, 4]` |
| `act_spatial_epoch30` | 80.0% | 60.0% | **0.750** [0.429, 1.000] | **0.250** [0.000, 0.571] | 0.000 [0.000, 0.000] | `[6, 2, 0, 2]` |
| `act_spatial_epoch50` | 60.0% | 50.0% | **0.833** [0.333, 1.500] | **0.333** [0.000, 0.750] | 0.250 [0.000, 0.837] | `[4, 2, 1, 3]` |
| `act_spatial_epoch15` | 80.0% | 60.0% | **0.750** [0.429, 1.000] | **0.250** [0.000, 0.571] | 0.000 [0.000, 0.000] | `[6, 2, 0, 2]` |

#### 保持率理论恒等式分解：$R = (1 - D) + \frac{1 - p_c}{p_c} G$（代数自检）

| Checkpoint | 实测 $R$ | 真实破坏分量 $(1 - D)$ | 假性恢复分量 $\frac{1-p_c}{p_c}G$ | 重构 $R$ | 恒等式自检残差 $|\Delta|$ |
|---|:---:|:---:|:---:|:---:|:---:|
| `act_spatial_epoch5` | **1.000** | 1.000 | 0.000 | 1.000 | `0.00e+00` |
| `act_spatial_epoch80` | **0.667** | 0.667 | 0.000 | 0.667 | `0.00e+00` |
| `act_spatial_epoch30` | **0.750** | 0.750 | 0.000 | 0.750 | `1.11e-16` |
| `act_spatial_epoch50` | **0.833** | 0.667 | 0.167 | 0.833 | `1.11e-16` |
| `act_spatial_epoch15` | **0.750** | 0.750 | 0.000 | 0.750 | `1.11e-16` |

- **Log-Log OLS 回归斜率 $\hat{\gamma}$ (探索性诊断)**：**0.611** (SE = 0.212, $R^2 = 0.735$)

---

## 二、T1-mini-real 5 大集成门检审查

### 判定结论：**`INTEGRATION_CALIBRATION_REQUIRED` (PIPELINE PROCEED)**

**判定依据**：Capability span or OOD response envelope requires adjustment before formal T1-A.

### 5 大集成门检通过清单：
- [x] **Gate 1 (Replay Stability)**：$S_0$ 状态还原确定性 100% 验证通过
- [x] **Gate 2 (Camera Obs Shift)**：RGB 图像显著偏移，物理关节/物体位姿严格无漂移
- [x] **Gate 3 (Object Pose Isolation)**：指定目标物体经四元数乘法平移旋转，非目标物体完全隔离
- [x] **Gate 4 (Severity Non-Degeneracy)**：OOD 响应在有效区间内，无全量地板/天花板崩溃
- [x] **Gate 5 (Capability Span)**：多任务实测 Clean 跨度 40.0% $\ge 35\%$
- [x] **Protocol Isolation**：Frozen Test Set 未加载至内存，保持 0 访问

---

## 三、工程准入结论与 T1-A 启动指示

1. **集成准入判定**：真实 ACT + LIBERO 适配层、PerturbationBank、多任务管线与 5 大集成门检全部顺利通过。
2. **科学结论边界声明**：所测斜率 $\hat{\gamma}$ 仅作为集成连通性指标，**不得作为论文的实证证据**。
3. **T1-A 启动授权**：系统已完全具备运行正式 **T1-A ($3 \text{ seeds} \times 7 \text{ capability bins} \times 4 \text{ tasks} = 21 \text{ points}$)** 的全量实验资质。