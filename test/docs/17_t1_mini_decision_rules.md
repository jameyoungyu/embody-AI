# T1-mini: 实验决策规则与预设门槛（Pre-Execution Decision Rules）

> **状态**：**已冻结（Frozen before execution）**  
> **核心原则**：在观测 T1-mini 实际运行数据之前写死判定规则，杜绝后验调参或因结果不及预期而主观“拯救假设”。

---

## 一、三条预设决策分支（Decision Gates）

```
                               ┌─────────────────────────────────────────┐
                               │           T1-mini 冒烟排查数据产出        │
                               └────────────────────┬────────────────────┘
                                                    │
                 ┌──────────────────────────────────┼──────────────────────────────────┐
                 ▼                                  ▼                                  ▼
   ┌───────────────────────────┐      ┌───────────────────────────┐      ┌───────────────────────────┐
   │ 决策 A: 进入全量 T1-A      │      │ 决策 B: 校准扰动强度后重测 │      │ 决策 C: 暂缓 / 证伪 C1    │
   ├───────────────────────────┤      ├───────────────────────────┤      ├───────────────────────────┤
   │ • 干净能力跨度 ≥ 40%      │      │ • 绝大多数 Checkpoint 的   │      │ • 在宽能力跨度下，两个    │
   │ • 状态还原 100% 可复现     │      │   OOD SR < 5% (近地板)    │      │   扰动轴的 R 均保持恒定   │
   │ • 至少一轴呈现系统性能力   │      │   或 OOD SR > 95% (天花板)│      │ • 配对破坏率 D 无系统变化 │
   │   耦合 (非单点拉扯驱动)    │      │ • 调整扰动幅度重新冒烟    │      │ • 正式接受证伪，不硬保假说│
   └───────────────────────────┘      └───────────────────────────┘      └───────────────────────────┘
```

### 决策 A：通过并正式启动 T1-A（$3 \text{ seeds} \times 7 \text{ capability bins}$）
- **触发条件**：
  1. 5 个 Checkpoint 的 Clean Validation SR 成功拉开 $\ge 40$ 个百分点跨度；
  2. 显式初始状态序列化与还原（$S_{0,j}^{\text{clean}} = S_{0,j}^{\text{OOD}}$）验证无损复现；
  3. 至少一个扰动轴（感知轴或状态轴）上，保持率 $R = p_{\text{OOD}} / p_{\text{clean}}$ 或配对破坏率 $D = P(Y_{\text{OOD}}=0 \mid Y_{\text{clean}}=1)$ 随基线能力演化呈现明确的系统性变化，且该趋势并非由极端近地板/天花板的单点驱动。

### 决策 B：校准扰动幅度并复测 T1-mini
- **触发条件**：
  - 扰动过强（多数 Checkpoint OOD SR $< 5\%$，全量跌入地板）或扰动过弱（多数 Checkpoint OOD SR $> 95\%$，无法造成有效干扰）。
- **行动**：调整物理扰动参数区间（如相机偏移角从 $\pm 15^\circ$ 微调至 $\pm 8^\circ$，或物块位姿扰动半径从 $5\text{cm}$ 调整至 $2\text{cm}$），仅重跑 T1-mini，不进入 T1-A。

### 决策 C：暂缓 C1 / 准备止损转向
- **触发条件**：
  - 在有效拉开 $\ge 40\%$ 的 Clean 能力跨度且扰动未落入地板/天花板的前提下，两个扰动轴上的保持率 $R$ 均保持水平恒定，且配对破坏率 $D$ 无任何系统性变化。
- **行动**：客观接受族内受控环境下 $H_0: \text{Proportional Retention}$ 成立的实证结果，启动预注册止损流程，不进行后验曲解。

---

## 二、逐 Episode 粒度原始数据记录规范（Episode-Level Raw Schema）

所有评测结果严禁仅保存百分比汇总值，必须实时持久化为 CSV / Parquet 格式的单行记录：

| 字段名 (Field) | 类型 | 含义 / 示例 |
|---|:---:|---|
| `model_family` | `str` | 策略模型族（如 `"ACT"`） |
| `seed` | `int` | 训练随机种子（如 `42`） |
| `checkpoint` | `str` | Checkpoint 标识（如 `"epoch_20"` / `"step_20000"`） |
| `clean_val_sr` | `float` | 选点用的 Validation 集 Clean 成功率（如 `0.648`） |
| `test_episode_id`| `str` | 独立 Frozen Test 集的 Episode 唯一标识（如 `"test_ep_0142"`） |
| `task_id` | `str` | 任务名称（如 `"libero_spatial_pick_up_the_black_bowl"`） |
| `initial_state_id`| `str` | 物理初始状态快照 Hash / ID（如 `"init_state_a7b8c9"`） |
| `perturbation_axis`| `str` | 扰动维度（`"camera_viewpoint"` / `"object_initial_pose"`） |
| `severity` | `float` | 扰动强度参数（如 `1.0` / `5.0_deg`） |
| `clean_success` | `int` | Clean Baseline 结果（`1` 或 `0`） |
| `ood_success` | `int` | 配对 OOD 条件下的结果（`1` 或 `0`） |

---

## 三、T1-mini 四大核心观察指标定义

1. **$p_{\text{OOD}} \text{ vs } p_{\text{clean}}$ 结构响应**：观测散点是否呈现偏离固定常数比例的系统性轨迹。
2. **名义保持率演化 $R(p_{\text{clean}})$**：$R = p_{\text{OOD}} / p_{\text{clean}}$ 是否随能力上升/下降而产生单调或非线性漂移。
3. **配对破坏率 (Paired Disruption Rate)**：
   $$D = P(Y_{\text{OOD}} = 0 \mid Y_{\text{clean}} = 1) = \frac{\sum_j \mathbb{I}(Y^{\text{clean}}_j = 1, Y^{\text{OOD}}_j = 0)}{\sum_j \mathbb{I}(Y^{\text{clean}}_j = 1)}$$
   *（在同一起始状态下，原本能完成的任务被扰动破坏的条件概率）*
4. **度量判定分歧检查 (Metric Inconsistency Check)**：
   - 检查是否存在特定 Checkpoint：其 PDR（或 $R$）显得较为鲁棒，但在更细粒度的配对破坏率 $D$ 上反而表现更差。
