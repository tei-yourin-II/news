---
id: whole_body_control
title: 全身控制 / 人形运动控制 — 现状基线
date: 2026-06-03
confidence: high（结构化部分）/ medium（近期趋势，部分来自预印本）
tags: [whole-body-control, humanoid, locomotion, teleoperation, sim-to-real, loco-manipulation]
---

# 全身控制 / 人形运动控制 — 现状基线

> 撰写日期：2026-06-03  
> 覆盖时段：重点 2024–2026 年中，含奠基作  
> 置信度说明：有 arXiv ID 或正式会议引用的标 ✓；未找到一手来源的标 **[未证实]**

---

## 1. 分支定义与边界

### 1.1 全身控制（Whole-Body Control, WBC）核心定义

全身控制指在单一策略或协调框架下，**同时驱动人形机器人的腿部（locomotion）与上肢（arm/hand manipulation）**，使机器人能在移动的同时完成操作任务，且保持整体动态平衡。

与相邻分支的边界：

| 分支 | 与全身控制的关系 |
|------|-----------------|
| **纯 locomotion** | 仅关注腿部/平衡；上肢固定或不受控 |
| **纯 manipulation（tabletop）** | 机器人固定底座；不涉及步行、平衡 |
| **全身控制（本分支）** | 两者融合：行走 + 手臂动作同时优化 |
| **遥操作 / 动作模仿** | 数据采集手段；最终目标也是全身控制 |
| **Avatar / 角色动画** | 视觉保真优先；物理可行性约束较弱 |

### 1.2 子方向

1. **Loco-Manipulation**：行走 + 操作的联合控制（最难，也最有应用价值）
2. **全身遥操作（Teleoperation）**：人类实时驱动机器人全身
3. **动作模仿（Motion Imitation）**：从人类视频/动捕数据学习全身动作
4. **平衡/跌倒恢复（Fall Recovery）**：应对扰动的鲁棒反应
5. **敏捷运动（Agile Locomotion）**：跑步、跳跃、跑酷、高动态技能

---

## 2. 当前 SOTA 方法

### 2.1 RL 控制器 + Sim-to-Real

**主流范式**：在 IsaacGym / IsaacLab / Genesis 中用大规模并行 RL 训练策略，再通过域随机化（Domain Randomization）实现零样本迁移到真实机器人。

**关键技术组合**：

- **教师-学生蒸馏（Teacher-Student Distillation）**：教师策略访问特权信息（精确接触力、地形地图），学生策略只用传感器可观测量，蒸馏后部署真机。这是当前最主流的 sim-to-real 路径之一（H2O、OmniH2O 均用此方法）。
- **域随机化（Domain Randomization）**：随机化电机参数、质量分布、地面摩擦、延迟等，迫使策略学习鲁棒表示。
- **Delta Action Model（增量动作模型）**：ASAP (2502.01143) 的核心贡献，用少量真实数据训练动作修正网络，减少仿真-现实动力学差距，无需重新训练主策略。
- **多仿真器随机化（Multi-Simulator DR）**：PolySim (2510.01708) 跨多个仿真引擎随机化，减少单一仿真器偏差。

**SOTA 代表作**：

| 方法 | 贡献 | 硬件 |
|------|------|------|
| H2O (2403.04436) | 首个基于 RL 的实时全身遥操作 | Unitree H1 |
| OmniH2O (2406.08858) | 统一姿态接口，支持 VR/语音/RGB 多模驱动 | Unitree H1 |
| ASAP (2502.01143) | Delta Action 模型大幅降低 sim-to-real gap | Unitree H1/H1-2 |
| Humanoid Locomotion as Next Token Prediction (2402.19469) | Transformer 自回归策略，多模态数据融合 | Digit (Agility) |
| ExBody2 (2412.13196) | 通才+专家蒸馏，数据自动筛选，AMASS 动捕驱动 | Unitree H1 |
| ALMI（adversarial loco-mani，2025.09）| 上下体对抗训练，下体 locomotion + 上体跟踪 | - |

### 2.2 人形遥操作 / 动作模仿

**遥操作**：让人类通过外骨骼、VR、RGB 摄像头实时控制机器人全身，同时采集数据供后续学习。

**代表工作**：

- **H2O (2403.04436)**：仅 RGB 摄像头实时全身遥操作，首次 zero-shot 真机部署
- **OmniH2O (2406.08858)**：通用接口，首个人形全身控制数据集 OmniH2O-6（六任务）
- **Open-TeleVision (2407.01512)**：沉浸式视觉反馈遥操作，开源
- **HOMIE (2502.13013)**：同构外骨骼驾驶舱，单操作员控制完整机器人全身，含步行+蹲姿
- **MOSAIC (2602.08594)**：快速残差适应，提升遥操作动作跟踪的 sim-to-real 鲁棒性

**动作模仿（从人类数据学习）**：

- **HumanPlus (2406.10454)**：全身追随（shadowing）+ 从人类视角模仿，开源
- **ExBody (2402.16796)**：SMPL 动捕驱动，腿部速度跟踪+上身动作模仿解耦
- **ExBody2 (2412.13196)**：ExBody 升级版，通才-专家两阶段训练，更多高动态动作
- **EgoMimic (2410.24221)**：第一人称视频规模化模仿学习
- **SUGAR (2605.20373, 2026.05)**：自动从人类视频提取运动先验，无需任务特定奖励工程

### 2.3 全身 Loco-Manipulation 融合

这是当前最热门、难度最大的子方向。

**层次化控制（Hierarchical）**：上层策略输出速度命令 + 上肢目标，下层策略执行 locomotion；两者分别训练再组合。

**端到端 VLA（Vision-Language-Action）**：

- **WholeBodyVLA (2512.11047, ICLR 2026)**：从无动作标注的第一人称视频中学习潜在动作，LAM + LMO-RL 联合框架，在 AgiBot X2 验证，超出基线 21.3%
- **ULTRA (2603.03279, 2026.03)**：物理驱动神经重定向 + 统一多模控制器，支持稠密参考和稀疏任务规格，在 Unitree G1 部署
- **SUGAR (2605.20373, 2026.05)**：人类视频驱动，无奖励工程，三阶段框架（提取→过滤→训练）

**鲁棒全身控制框架**：

- **From Experts to Generalist (2506.12779, 2025.06)**：专家组合→通才策略，两个仿真器 + 真机验证
- **Behavior Foundation Model (2509.13780)**：大规模预训练行为基础模型，CVAE + 在线蒸馏，支持多控制模式零样本切换

---

## 3. 关键论文清单（详见末尾结构化表格）

以下按时间线列出奠基作和 2025-2026 突破，arXiv ID 可直接查验。

### 奠基作（2022-2024）

- `2402.19469` — Humanoid Locomotion as Next Token Prediction（UC Berkeley, 2024）
- `2402.16796` — Expressive Whole-Body Control / ExBody（UCSD, 2024）
- `2403.04436` — H2O: Learning Human-to-Humanoid Real-Time Whole-Body Teleoperation（CMU, IROS 2024）
- `2406.08858` — OmniH2O（CMU, CoRL 2024）
- `2406.10454` — HumanPlus: Humanoid Shadowing and Imitation from Humans（Stanford, 2024）
- `2403.10506` — HumanoidBench: Simulated Benchmark for Whole-Body Locomotion and Manipulation（2024）
- `2404.05695` — Humanoid-Gym: Zero-Shot Sim2Real for Humanoid Locomotion（2024）
- `2407.01512` — Open-TeleVision（2024）

### 2025 年突破

- `2412.13196` — ExBody2: Advanced Expressive Humanoid Whole-Body Control（2024.12，影响延伸至 2025）
- `2502.01143` — ASAP: Aligning Simulation and Real-World Physics（PKU+Berkeley, 2025.02）
- `2502.13013` — HOMIE: Humanoid Loco-Manipulation with Isomorphic Exoskeleton Cockpit（2025.02）
- `2503.14734` — GR00T N1: Open Foundation Model for Generalist Humanoid Robots（NVIDIA, 2025.03）
- `2509.13780` — Behavior Foundation Model for Humanoid Robots（2025.09）
- `2510.01708` — PolySim: Multi-Simulator Dynamics Randomization（2025.10）
- `2510.25241` — One-shot Humanoid Whole-body Motion Learning（2025.10）
- `2511.04131` — BFM-Zero: Promptable BFM via Unsupervised RL（2025.11）
- `2512.11047` — WholeBodyVLA（ICLR 2026, 2025.12）

### 2026 年最新（截至 2026-06-03）

- `2502.20061` — HiFAR: Multi-Stage Curriculum for High-Dynamics Fall Recovery（2026.02）
- `2602.08594` — MOSAIC: Rapid Residual Adaptation for Motion Tracking（2026.02）
- `2603.03279` — ULTRA: Unified Multimodal Control for Autonomous Humanoid WBC（2026.03）
- `2603.08619` — Embedding Classical Balance Principles in RL for Humanoid Recovery（2026.03）
- `2506.12779` — From Experts to a Generalist: Toward General WBC（2026.06）
- `2506.12851` — KungfuBot: Physics-Based Humanoid WBC for Highly-Dynamic Skills（2026.06）
- `2506.20487` — Survey: Behavior Foundation Model for Next-Gen WBC（2026.06）
- `2605.20373` — SUGAR: Scalable Human-Video-Driven Humanoid Loco-Manipulation（PKU, 2026.05）

---

## 4. 关键玩家

### 4.1 硬件公司

| 公司 | 平台 | 全身控制现状 |
|------|------|-------------|
| **宇树科技 (Unitree)** | G1, H1, H1-2 | 2025年出货5500+台，全球第一；G1/H1是学术界主流实验平台；开源 Humanoid-Gym 基于 Isaac Gym |
| **智元机器人 (ZhiyuanAI)** | 远征 A2-W, A3 | 国内首个工业规模商业签单（富临精工）；2026 Q1 已下线1万台 A3 |
| **众擎机器人 (Zhongqing)** | SE01 | 170cm / 55kg / 32 DoF；自然步态，计划批量交付；目标售价 $20k-30k |
| **Figure AI** | Figure 03 | BMW 工厂40台商业部署；BotQ 工厂每90分钟产一台机器人 |
| **Tesla Optimus** | Optimus V2/V3 | 仅内部工厂测试；V3 预计 2026 年 7-8 月发布；2027 消费者销售 |
| **Boston Dynamics** | Atlas (electric) | 与 Toyota Research Institute 合作 Large Behavior Models；Hyundai 计划年产 30,000 台 |
| **Agility Robotics** | Digit | RoboFab 工厂量产；专注工厂物流 |
| **1X Technologies** | NEO Gamma | 家庭场景测试；**[未证实]** 截至 2026 商业化进展有限 |

### 4.2 科研机构

| 机构 | 代表工作 | 核心贡献方向 |
|------|---------|-------------|
| **CMU LeCAR Lab** | H2O, OmniH2O | 全身遥操作 + 动作模仿 |
| **UC Berkeley** | Humanoid Locomotion as NTP, ASAP | Transformer 策略，语言-动作对齐 |
| **UCSD（Xiaolong Wang 组）** | ExBody, ExBody2 | SMPL 驱动的表达性全身控制 |
| **Stanford** | HumanPlus | 第一视角模仿学习 |
| **NVIDIA** | GR00T N1, IsaacLab | 基础模型 + 仿真平台 |
| **PKU / Beihang** | SUGAR, ASAP | 人类视频驱动 loco-mani |
| **OpenDriveLab (上海 AI Lab)** | WholeBodyVLA | VLA for loco-manipulation |
| **上交大等中国高校** | KungfuBot | 高动态技能，RL 自适应课程 |

---

## 5. 仿真器 / Benchmark

### 5.1 仿真器

| 仿真器 | 特点 | 2025-2026 动态 |
|--------|------|---------------|
| **NVIDIA Isaac Gym** | GPU 并行 RL，人形 locomotion 主力 | 已迁移至 Isaac Lab；仍被大量论文使用 |
| **NVIDIA Isaac Lab** | Isaac Gym 升级版，模块化，支持多机器人 | 2024 正式发布；HumanoidVerse 等框架基于此 |
| **MuJoCo** | CPU/GPU，精确接触模拟 | MuJoCo-Warp（GPU 加速）：locomotion 最高 152x 加速；HumanoidBench 基础引擎 |
| **Genesis** | 开源，Python，430,000x 实时（RTX 4090）；统一 rigid/MPM/SPH/FEM | 2024.12 发布；HumanoidVerse 已支持 |
| **Humanoid-Gym** | 基于 Isaac Gym，专为人形 zero-shot sim2real | RobotEra 开源（2404.05695）|
| **HumanoidVerse** | 多仿真器（IsaacGym + Genesis + IsaacLab）统一训练 | LeCAR Lab 开源，2025.02 发布 |
| **Booster Gym** | 端到端人形 locomotion RL 框架，强化 DR | 2025.06（2506.15132）|

### 5.2 Benchmark

| Benchmark | 描述 |
|-----------|------|
| **HumanoidBench (2403.10506)** | MuJoCo 基础，28 DoF 人形机器人，覆盖 locomotion + manipulation 多任务；RL 难度高，层次方法表现更好 |
| **GRUtopia (2407.10943)** | 城市规模机器人仿真，大场景 loco-navigation |
| **ManiSkill3 (2410.00425)** | GPU 并行操作任务 benchmark，支持多种机器人 |
| **OmniH2O-6 dataset** | 首个全身控制数据集，6类日常任务的遥操作轨迹（随 OmniH2O 发布）|

---

## 6. 近 6-12 个月趋势（2025 下半年 – 2026 中）

### 6.1 Loco-Manipulation 端到端融合加速

最显著的趋势是从"分层控制（loco 策略 + mani 策略松耦合）"走向"端到端统一控制"。WholeBodyVLA（ICLR 2026）、ULTRA（2026.03）均在真机验证了端到端 loco-mani，成功率已超过分层基线。

### 6.2 人类视频作为免费数据源

SUGAR（2026.05）、EgoMimic、ExBody2 等工作证明可从海量 YouTube/动捕数据自动提取运动先验，**无需逐任务奖励工程或昂贵的遥操作采集**，大幅提升数据效率。

### 6.3 行为基础模型（Behavior Foundation Model）兴起

GR00T N1（NVIDIA, 2025.03）、BFM 系列（2509.13780, 2511.04131）、Survey（2506.20487）标志着社区开始探索"预训练一个大模型，零样本或少样本迁移到多任务"的范式转变。当前主要在 manipulation 任务验证，loco-mani 联合仍在攻关。

### 6.4 高动态技能突破

KungfuBot（2506.12851）等工作将 RL + 自适应课程学习推向功夫、舞蹈等高动态全身技能，并在 Unitree G1 真机验证。ASAP（2502.01143）等显著降低高动态动作的 sim-to-real gap。

### 6.5 跌倒恢复进入工程化阶段

HiFAR（2502.20061）、Embedding Classical Balance Principles（2603.08619）在 Unitree H1-2 上实现 93.4% 恢复率（随机初始姿态），无参考轨迹，单一策略覆盖踝策略→踏步→摔倒-站起全谱。

### 6.6 规模化真机部署

- 宇树（5500+ 台，2025 全年）、智元（1万台 A3，2026 Q1）已进入批量交付阶段
- Figure AI 40 台机器人商业部署于 BMW 工厂（$25/机器人-小时）
- Boston Dynamics 与 Hyundai 合作，计划年产 30,000 台 Atlas

---

## 7. 开放问题 / 下一步

1. **Sim-to-Real Gap（接触、变形体）**：现有 DR 对刚体系统效果好；柔性物体、液体、衣物等复杂接触场景 sim2real 仍是硬问题。Genesis/MuJoCo-Warp 等工具正在改善但未解决。

2. **长时程 Loco-Mani**：当前端到端模型（如 GR00T N1）还不能处理"走过去→抓取→移动→放置"的长链任务；WholeBodyVLA/ULTRA 正在攻克但场景仍局限。

3. **数据瓶颈**：高质量全身操作数据（手-臂-腿协同）远少于纯 manipulation 数据；SUGAR/EgoMimic 方向（视频→策略）是最有潜力的突破口。

4. **安全与人机协作**：量产后的安全边界（跌倒、碰撞、紧急停机）缺乏标准化 benchmark 和认证框架。**[未证实]** 是否有正式监管框架尚不明确。

5. **跨形态泛化**：当前大多数策略针对特定硬件训练；GR00T N1 等跨形态基础模型方向值得关注，但效果尚不稳定。

6. **能量效率**：高动态全身控制下的功耗/续航仍是工程瓶颈；Duke Humanoid（2409.19795）等工作开始关注能量效率优化。

7. **上肢灵巧操作 + 移动的深度融合**：灵巧手（5指）与移动底座的联合优化远难于 2-3 指夹爪；当前多数 loco-mani 工作用简化手型规避此问题。

---

## 关键论文（结构化）

- 2402.19469 | Humanoid Locomotion as Next Token Prediction | 2024 | 将人形控制建模为自回归 Token 预测，Transformer 策略在 Digit 上 zero-shot 真机行走
- 2402.16796 | Expressive Whole-Body Control for Humanoid Robots (ExBody) | 2024 | SMPL 动捕驱动上身模仿+腿部速度跟踪解耦，首个表达性全身控制 sim2real
- 2403.04436 | Learning Human-to-Humanoid Real-Time Whole-Body Teleoperation (H2O) | 2024 | 仅 RGB 相机实现首个 RL-based 实时全身遥操作（IROS 2024）
- 2406.08858 | OmniH2O: Universal and Dexterous Human-to-Humanoid Whole-Body Teleoperation | 2024 | 统一姿态接口支持 VR/语音/RGB 多模驱动，发布首个全身控制数据集 OmniH2O-6（CoRL 2024）
- 2406.10454 | HumanPlus: Humanoid Shadowing and Imitation from Humans | 2024 | 全身影随+第一视角模仿学习，Stanford 开源
- 2403.10506 | HumanoidBench: Simulated Humanoid Benchmark for Whole-Body Locomotion and Manipulation | 2024 | 覆盖 locomotion + manipulation 的标准 benchmark，MuJoCo 基础
- 2404.05695 | Humanoid-Gym: RL for Humanoid Robot with Zero-Shot Sim2Real Transfer | 2024 | Isaac Gym 框架 + sim2sim 验证，专为人形 zero-shot sim2real
- 2407.01512 | Open-TeleVision: Teleoperation with Immersive Visual Feedback | 2024 | 沉浸式视觉反馈遥操作系统，开源
- 2408.07295 | Learning Multi-Modal Whole-Body Control for Real-World Humanoid Robots (MHC) | 2024 | 多模式全身跟踪控制器，RL 训练 + sim2real
- 2410.24221 | EgoMimic: Scaling Imitation Learning via Egocentric Video | 2024 | 第一人称视频规模化模仿学习
- 2412.13196 | ExBody2: Advanced Expressive Humanoid Whole-Body Control | 2024 | 通才+专家两阶段训练，AMASS 动捕自动筛选，高动态动作 sim2real
- 2501.02116 | Humanoid Locomotion and Manipulation: Current Progress and Challenges | 2025 | 综述：模型-based 与学习-based 方法对比，含战术感知融合展望
- 2502.01143 | ASAP: Aligning Simulation and Real-World Physics for Learning Agile Humanoid Whole-Body Skills | 2025 | Delta Action Model 用少量真实数据修正 sim 策略，首次实现高度敏捷动作 sim2real（PKU+Berkeley）
- 2502.13013 | HOMIE: Humanoid Loco-Manipulation with Isomorphic Exoskeleton Cockpit | 2025 | 同构外骨骼驾驶舱，单操作员全身控制，RL 策略支持任意上身姿态+行走+蹲姿
- 2502.20061 | HiFAR: Multi-Stage Curriculum Learning for High-Dynamics Humanoid Fall Recovery | 2025 | 多阶段课程 RL 实现高动态跌倒恢复
- 2503.14734 | GR00T N1: An Open Foundation Model for Generalist Humanoid Robots | 2025 | NVIDIA 发布首个开源人形机器人基础模型，VLA 双系统架构，50k H100 GPU-hrs 训练
- 2504.11054 | Zero-Shot Whole-Body Humanoid Control via Behavioral Foundation Models | 2025 | BFM 实现零样本全身控制
- 2506.12779 | From Experts to a Generalist: Toward General Whole-Body Control for Humanoid Robots | 2025 | 专家策略组合蒸馏为通才策略，双仿真器+真机验证
- 2509.13780 | Behavior Foundation Model for Humanoid Robots | 2025 | CVAE + 在线蒸馏预训练行为基础模型，零样本多控制模式切换
- 2510.01708 | PolySim: Bridging the Sim-to-Real Gap via Multi-Simulator Dynamics Randomization | 2025 | 跨仿真器域随机化降低单一仿真器偏差
- 2510.25241 | One-shot Humanoid Whole-body Motion Learning | 2025 | 单示例全身动作学习
- 2511.04131 | BFM-Zero: A Promptable Behavioral Foundation Model via Unsupervised RL | 2025 | 无监督 RL 可提示行为基础模型
- 2512.11047 | WholeBodyVLA: Towards Unified Latent VLA for Whole-Body Loco-Manipulation Control | 2025 | LAM 从无动作标注视频学潜在动作 + LMO-RL，AgiBot X2 验证超基线 21.3%（ICLR 2026）
- 2602.08594 | MOSAIC: Bridging the Sim-to-Real Gap in Generalist Humanoid Motion Tracking and Teleoperation with Rapid Residual Adaptation | 2026 | 快速残差适应提升遥操作 sim2real 鲁棒性
- 2603.03279 | ULTRA: Unified Multimodal Control for Autonomous Humanoid Whole-Body Loco-Manipulation | 2026 | 物理神经重定向 + 统一控制器，Unitree G1 真机自主 loco-mani
- 2603.08619 | Embedding Classical Balance Control Principles in Reinforcement Learning for Humanoid Recovery | 2026 | 嵌入质心/捕获点等经典平衡量，单策略跨踝/踏步/跌倒恢复，93.4% 成功率
- 2506.12851 | KungfuBot: Physics-Based Humanoid Whole-Body Control for Learning Highly-Dynamic Skills | 2026 | 自适应双层优化课程，功夫/舞蹈动作 Unitree G1 真机部署
- 2506.20487 | A Survey of Behavior Foundation Model: Next-Generation Whole-Body Control System of Humanoid Robots | 2026 | BFM for WBC 综述，覆盖预训练管线、真机应用与未来挑战
- 2605.20373 | SUGAR: A Scalable Human-Video-Driven Generalizable Humanoid Loco-Manipulation Learning Framework | 2026 | 自动从人类视频提取运动先验，无奖励工程，三阶段 loco-mani 框架（PKU+Beihang）
