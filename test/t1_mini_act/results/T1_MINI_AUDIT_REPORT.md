# T1-mini 合成工程测试桩（Synthetic Integration Harness）审计报告

> **执行时间**：2026-08-23  
> **数据性质定性**：$\boxed{\textbf{SYNTHETIC TEST HARNESS ONLY（代码工程脚手架测试数据，科学实验数据为 0）}}$  
> **真实模型与环境状态**：$\boxed{\textbf{REAL INTEGRATION: BLOCKED（本地环境缺失 PyTorch / LIBERO / MuJoCo 真实依赖与 ACT 权重）}}$  
> **正式 T1-A 状态**：$\boxed{\textbf{FORMAL T1-A: STRICTLY BLOCKED}}$  

---

## 一、重大工程事实与代码定性说明

本报告所载全部数据来自于本地 Python 环境（仅安装 NumPy / SciPy）中编写的**合成测试桩（Synthetic Engineering Scaffold）**。

### 明确澄清以下事实：
1. **无神经网络推理**：未加载 PyTorch，未导入 Transformer 架构，未读取真实的 ACT 权重文件（`.pt / .ckpt`）。
2. **无真实物理环境交互**：未调用 LIBERO、robosuite 或 MuJoCo 仿真器，未执行 `env.step(action)` 动力学闭环。
3. **能力跨度与扰动衰减系人工函数**：各 Checkpoint 的输出是由代码内预设的基线成功率与退化公式（$p^{2.05}, p^{1.85}$）计算的 Bernoulli 采样，**不可作为任何科学证据**。
4. **$G \equiv 0$ 的代数必然性**：由于在 Clean 与 OOD 采样前重置了相同的随机数种子 $u$，在 $p_o < p_c$ 的人工公式约束下必然导致 $u < p_o \implies u < p_c$，因此 $P(Y_o=1, Y_c=0) \equiv 0$ 是代码构造的代数结果，非物理现象。

---

## 二、合成脚手架（Synthetic Harness）验证通过的工程接口

虽然本测试不包含任何真实科学数据，但在软件工程层面上已验证以下数据接口与流程：
- [x] **多任务数据结构流转**（Multi-Task Data Flow）
- [x] **冻结扰动库实现**（`PerturbationBank` 保证跨 Checkpoint 物理参数 $\delta_{j,d}$ 100% 严格一致）
- [x] **20 字段完整 Provenance 日志格式**（`paired_episode_id` 统一，记录真实参数生成种子）
- [x] **测试集隔离逻辑**（`SplitManager` 懒加载，Frozen Test 保持 0 访问）
- [x] **保持率理论分解与 Bootstrap 置信区间计算链**（代数自检恒等式计算无 Bug）

---

## 三、真实 T1-mini-real 启动所需前置硬件与依赖清单

在将本管线迁移至 GPU 服务器执行真正的物理实验前，必须具备以下依赖：
1. **深度学习与物理引擎环境**：`torch >= 2.0`, `torchvision`, `mujoco >= 2.3`, `robosuite`, `libero`
2. **离线真实训练 Checkpoints**：基于真实演示数据训练的 ACT 系列权重（例如 `seed42_epoch15.ckpt`, `seed42_epoch30.ckpt`, ...）
3. **真实闭环 Rollout 逻辑**：
   ```python
   # 真实物理闭环架构（严禁任何概率生成器）
   obs = env.reset()
   while not done:
       action_chunk = act_model.predict(obs["rgb"], obs["qpos"])
       for action in action_chunk:
           obs, reward, done, info = env.step(action)
   ```
4. **无偏能力分档**：仅在真实 Validation 集 Rollout 统计得到的实际成功率进行 Checkpoint Bin 选取，彻底剔除 `target_clean_sr` / `nominal_capability` 等人工参数。