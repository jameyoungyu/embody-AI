# Test Directory: Local Research Scaffold & Exploration Archive

> ⚠️ **重要声明 (Git & Data Isolation Notice)**：
> 1. 本目录作为工程脚手架、受控实验协议与本地探索归档；
> 2. **数据性质声明**：`test/t1_mini_act/` 中的评测结果为 **Synthetic Integration Scaffold Data（代码工程脚手架测试数据）**，不包含任何真实 PyTorch 神经网络推理与 MuJoCo 物理闭环，**正式科学实验数据为 0**；
> 3. **真实实验状态**：因本地 macOS 环境缺少 `torch` / `libero` / `robosuite` / `mujoco` 依赖及真实 ACT 权重文件，当前处于 **`BLOCKED`** 状态，**正式 T1-A 严禁启动**。

---

## 项目当前全局状态定位

$$\boxed{\textbf{C1 核心研究方向：Strong GO}}$$

$$\boxed{\textbf{Synthetic Engineering Scaffold（工程数据脚手架）：PASS（已封版）}}$$

$$\boxed{\textbf{Actual ACT + LIBERO Integration（真实物理集成）：BLOCKED（待 GPU 环境）}}$$

$$\boxed{\textbf{Scientific T1 Empirical Data（正式科学实验数据）：0 episodes}}$$

$$\boxed{\textbf{Formal T1-A（全量 3×7 矩阵）：STRICTLY BLOCKED}}$$

---

## 目录结构与文档索引

```
test/
├── README.md                                 # 本说明文档与状态总览
│
├── docs/                                     # 方案设计与真实部署规范
│   ├── 16_t1_act_protocol.md                 # T1 族内受控实验主协议
│   ├── 17_t1_mini_decision_rules.md          # 统计指标与决策准入规则
│   ├── 18_t1_mini_real_protocol.md           # 5 大物理集成门检规范
│   └── 19_real_act_libero_deployment_spec.md # 真实 GPU 环境部署与闭环 Rollout 规范
│
├── t2_pre/                                   # T2-PRE 公开基准探索性诊断（已冻结归档）
│   ├── run_t2_pre_corrected.py               # 修正样本量诊断脚本 (CVPR 2026 Table 1 冻结)
│   └── T2_PRE_CORRECTED_REPORT.md            # 修正版预试验分析报告
│
└── t1_mini_act/                              # T1-mini 合成脚手架工程包 (Synthetic Scaffold)
    ├── config.py                             # 显式参数分布与四集隔离配额
    ├── state_manager.py                      # S_0 快照抓取与恢复逻辑
    ├── policy_state_manager.py               # 策略动作缓存与 RNG 重置逻辑
    ├── perturbations.py                      # 冻结扰动库 (PerturbationBank) 与四元数复合
    ├── split_manager.py                      # 懒加载四集隔离管理器 (Frozen Test 0 访问)
    ├── eval_paired.py                        # 多任务配对评测控制引擎
    ├── logger.py                             # 20 字段完整 Provenance CSV 日志记录器
    ├── metrics.py                            # 保持率分解引擎与 95% Bootstrap 置信区间
    ├── validation.py                         # 5 大物理门检核验逻辑
    ├── analyze.py                            # 多任务聚合统计与报告生成
    ├── run_t1_mini_real.py                   # 脚手架冒烟测试运行器
    └── results/
        ├── T1_MINI_AUDIT_REPORT.md           # 脚手架测试审计报告
        └── t1_mini_raw_episodes.csv          # 2000 行脚手架测试 CSV 记录
```
