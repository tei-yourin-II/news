---
id: world_model
title: "世界模型(World Model / World Action Model / Physical AI)分支基线"
date: 2026-06-03
confidence: high
author: robot-intel-agent
version: 1.0
tags: [world-model, physical-AI, latent-dynamics, video-prediction, embodied-AI, Dreamer, Genie, Cosmos]
---

# 世界模型 (World Model) — 现状基线

> 本文档为「人形机器人/具身智能情报系统」的世界模型分支**现状基线**，建立于 2026-06-03。
> 后续每日增量情报将基于本文档叠加更新。
> 声明可核查；不确定处标注「**[未证实]**」；事实与判断明确区分。

---

## 1. 分支定义与边界

### 1.1 世界模型核心定义

世界模型（World Model）是指**学习环境动力学的预测性表示**，即给定当前状态与动作，预测未来状态（可为像素、潜在向量、语义特征等形式）。其最早系统化表述来自 Schmidhuber（1990）和 Ha & Schmidhuber《World Models》（2018, arXiv:1803.10122），近年随大规模生成式模型崛起而爆发。

**核心能力三角**：
- **预测（Prediction）**：前向仿真未来观测 / 状态
- **规划（Planning）**：在想象中搜索动作序列
- **评估（Evaluation）**：对策略 / 动作进行虚拟评分

### 1.2 与相邻概念的关系与边界

| 概念 | 与世界模型的关系 | 重叠区域 |
|------|----------------|---------|
| **VLA（Vision-Language-Action）** | 纯反应式策略，给定观测→输出动作，不显式建模未来 | WAM（World Action Model）既预测未来又输出动作，跨越两者 |
| **视频生成模型** | 世界模型的超集视角：高质量视频生成≠世界模型，需满足物理一致性和动作可控性 | Action-conditioned 视频预测（如 Cosmos、GAIA）具备世界模型属性 |
| **神经仿真器（Neural Simulator）** | 替代传统物理仿真器的角色，支持闭环 RL 训练 | UniSim、World-Env 等直接扮演仿真器角色 |
| **模型增强 RL（MBRL）** | 世界模型用于策略优化的经典范式（Dreamer 系） | Dreamer/DayDreamer 系为典型 MBRL |

**关键区分**（来源：arXiv:2605.12090 WAM Survey）：
- VLA：P(action | observation) — 反应式映射
- World Model：P(future_state | current_state, action) — 动力学预测
- WAM：P(future_state, action | current_state) — 联合分布，兼具两者

**判断（非事实）**：2025-2026 年三条边界正在快速模糊，"动作可控视频生成 + 策略解码"模式（UniPi→DreamZero 路线）实际上将三者合并为一个端到端框架。

---

## 2. 主要技术路线

### 2.1 隐空间动力学模型（Latent Dynamics）—— Dreamer 系

**核心思想**：在压缩的隐空间（latent space）中学习动力学，避免像素级预测的高维代价；策略在"想象"的隐状态序列中训练（Imagination-based Policy Optimization）。

**架构核心**：RSSM（Recurrent State-Space Model）= 确定性 GRU + 随机潜变量，支持随机预测和确定性记忆。

**技术演进**：
- **DreamerV1**（Hafner 等，2020, arXiv:1912.01603）：RSSM + 潜想象训练，奠定范式
- **DreamerV2**（Hafner 等，2020, arXiv:2010.02193）：引入离散类别隐变量，大幅提升 Atari 性能
- **DreamerV3**（Hafner 等，2023, arXiv:2301.04104）：**里程碑**，单一超参数跨 150+ 任务 SOTA，首次无课程从像素自主挖 Minecraft 钻石
- **DayDreamer**（Wu 等，2022, arXiv:2206.14176）：将 DreamerV3 移植到真实机器人（四足 + 机械臂 + 轮式），1 小时内学会站立/行走

**代表衍生**（2024-2025）：
- DreamerNav：多模态感知 + 课程训练，室内导航
- DREAMer-VXS：LiDAR 高维观测的 AGV 探索
- IRIS（Micheli 等，2022, arXiv:2209.00588）：以 VQ-VAE + Transformer 替代 RSSM，Atari 100k 超越人类 10/26 款

### 2.2 视频预测式世界模型（Video Prediction World Models）

**核心思想**：直接在像素/视频帧空间学习前向预测，保留空间细节；生成的视频可直接用于可视化、策略监督、合成数据。

**代表作**：

**UniPi**（Du 等，NeurIPS 2023, arXiv:2302.00111）：
- 将策略学习重新表述为"文本条件视频生成"，视频轨迹作为通用规划接口
- 逆动力学模型从生成视频中提取低级动作

**Navigation World Models / NWM**（Bar 等，CVPR 2025, arXiv:2412.03572）：
- 条件扩散 Transformer（CDiT），训练于人类+机器人的多样化第一人称视频
- 规模达 1B 参数，支持 MPC 框架规划导航轨迹，零样本迁移至物理机器人

**NVIDIA Cosmos 系列**（2025-2026）：
- Cosmos 1.0（arXiv:2501.03575）：首批开放权重物理 AI 世界基础模型，含 Predict / Transfer / Reason 子系统
- Cosmos-Predict2.5（2025-10）：统一 Text2World / Image2World / Video2World 于单模型，2B+14B 参数，基于 2 亿精选视频预训练 + RL 后训练
- **Cosmos 3**（2026-06-01）：混合专家 Transformer（MoT）架构，Nano(16B) + Super(64B)，**首个完全开放的全模态物理 AI 模型**，支持文本/图像/视频/音频/动作的理解与生成，"物理准确度领先"（NVIDIA 官方声明，未独立验证）

### 2.3 可交互生成环境（Interactive Generative Environments）—— Genie 系

**核心思想**：从无标注视频中学习可交互的虚拟世界，支持智能体在其中探索；用于具身智能 Agent 的训练与评测环境生成。

**技术演进**：

**Genie 1**（Bruce 等，ICML 2024 Best Paper, arXiv:2402.15391）：
- 从未标注的 2D 游戏视频学习可交互环境
- 三组件架构：视频 Tokenizer + SSM + Dynamics Model
- 意义：证明可从互联网视频无监督学习 latent action

**Genie 2**（Google DeepMind，2024-12，博客发布，无 arXiv）：
- 扩展至 3D 交互式世界；支持真实世界照片转可交互 3D 环境
- 局限：单次一致世界维持约 60 秒，分辨率 360p

**Genie 3**（Google DeepMind，2025-08，博客发布，无独立 arXiv）：
- 实时 24fps 720p 交互；世界一致性维持数分钟
- 2026-01-29 以「Project Genie」面向美国 AI Ultra 订阅用户开放

### 2.4 物理 AI 世界基础模型（Physical AI Foundation World Models）

重点覆盖 2025-2026 年新兴的大规模产业化模型：

**Wayve GAIA 系列**（自动驾驶，向机器人外溢）：
- GAIA-1（2023, arXiv:2309.17080）：首个为自动驾驶设计的生成式世界模型，视频+文本+动作输入，细粒度驾驶行为控制
- GAIA-2（2025-03）：多视角可控生成世界模型，arXiv 待查
- GAIA-3（2025-12）：150 亿参数，训练数据量约 GAIA-2 的 10 倍，跨大洲 / 车型 / 天气；定位"评估而非仅仿真"，闭环安全评测

**World Labs / Marble**（Fei-Fei Li，2025-11）：
- 首款商业产品 Marble：文本/图像/视频 Prompt 生成可探索 3D 世界，支持导出
- 定位"空间智能"（Spatial Intelligence），强调感知-想象-行动的统一
- **[未证实]**：与机器人策略的直接集成尚无公开技术细节

**Meta V-JEPA 2**（2025-06, arXiv:2506.09985）：
- 自监督视频预测，基于 100 万小时互联网视频预训练
- 后训练为 V-JEPA 2-AC（动作条件化）：仅用 62 小时无标注机器人视频
- 零样本部署于 Franka 机械臂：杯子抬取/移动成功率 80%（对比 Octo VLA: 15%）

### 2.5 用于机器人的世界模型（Robot-Specific World Models）

**World Action Models（WAM）**（新兴范式，2025-2026）：
- 正式命名来自 arXiv:2605.12090（WAM Survey，2026-05）
- 分类：Cascaded WAM（预测 + 动作解码解耦）vs Joint WAM（视频与动作联合生成）
- 代表作：DreamZero（Ye 等，arXiv:2602.15922）：联合视频-动作的 chunk-wise 去噪，7Hz 闭环控制，对 VLA 基线实现 2×+ 泛化提升；跨体型迁移，30 分钟数据迁移至新机器人

**GigaBrain-0 / GigaWorld-0**（arXiv:2510.19430 / arXiv:2511.19861）：
- 将世界模型作为 VLA 训练的数据引擎，生成视频/3D 增强数据

**WorldEval**（arXiv:2505.19017，2025-05）：
- 离线策略评估：世界模型替代真实环境，用于策略排名、检查点选择、安全检测
- Policy2Vec 将潜在动作编码注入视频生成，解决动作一致性问题

---

## 3. 关键玩家布局

### 3.1 NVIDIA — Cosmos 平台

| 产品 | 时间 | 规模 | 定位 |
|------|------|------|------|
| Cosmos 1.0 | 2025-01 (CES) | 多个模型变体 | 开放权重，物理 AI 基础平台 |
| Cosmos-Predict2.5 | 2025-10 | 2B / 14B | 统一多模态视频生成，机器人专用微调 |
| Cosmos-Transfer2.5 | 2025-10 | 2B | 多空间控制输入条件化仿真 |
| Cosmos 3 | 2026-06-01 | 16B(Nano) / 64B(Super) | 全模态 Omnimodel，MoT 架构，开放前沿 |

**机器人生态**：1X、Agility Robotics、Figure AI、Skild AI 等首批采用 Cosmos 生成训练数据。
**工具链**：NeMo Curator 支持 14 天处理 2000 万小时视频（vs CPU 需 3 年以上）。

### 3.2 Google DeepMind — Genie + SpatioTemporal Research

- Genie 1/2/3 路线（见 2.3 节）
- SIMA（Scalable Instructable Multiworld Agent）：跨多款 3D 游戏的具身 Agent，利用互动环境世界模型（arXiv:2512.04797 for SIMA 2）
- 策略评估与合成数据方向持续投入（判断，非独立公开信息）

### 3.3 Meta AI — V-JEPA 系列

- V-JEPA（2024）→ V-JEPA 2（arXiv:2506.09985，2025-06）
- 路线：自监督潜空间预测，不生成像素；强调数据效率与零样本机器人迁移
- 发布 Droid 数据集使用细节；引入物理推理新 Benchmark

### 3.4 Wayve — GAIA（自动驾驶方向）

- 专注自动驾驶仿真与安全评测，不直接面向机器人
- GAIA-3（2025-12）：将世界模型从"仿真工具"重新定位为"评估工具"，是方法论上的重要转变

### 3.5 World Labs — Marble（3D 空间智能）

- 创立者：Fei-Fei Li + Justin Johnson + Christoph Lassner + Ben Mildenhall
- Marble（2025-11）：首个多模态 Prompt 到可探索 / 可编辑 3D 世界的商业产品
- 定位与机器人关联：空间智能作为感知-想象-行动链路的基础层（创始人愿景）
- **[未证实]**：直接机器人应用尚无公开披露

### 3.6 机器人公司在世界模型上的布局

| 公司 | 布局方式 |
|------|---------|
| Physical Intelligence (π) | π0 / π0.5 VLA + World Model 后训练方向（WAM 化趋势） |
| Figure AI | Helix VLA；采用 Cosmos 生成合成数据 |
| 1X Technologies | 采用 Cosmos；NEO 机器人数据飞轮 |
| Agility Robotics | 采用 Cosmos；Digit 商业化 |
| Unitree | UnifoLM-VLA-0 开源（2026-03），世界模型集成 [未证实] |
| AgiBOT (智元机器人) | τ0-WM：统一视频-动作世界模型（arXiv 待查，finch.agibot.com） |
| Waabi | UniSim 神经仿真器（CVPR 2023），自动驾驶为主 |

---

## 4. 数据集 / Benchmark / 评测方式

### 4.1 主要训练数据集

| 数据集 | 规模 | 用途 |
|--------|------|------|
| **Open X-Embodiment** | ~100 万轨迹，22 种机器人 | 跨体型 VLA 预训练，世界模型数据引擎基础 |
| **BridgeData V2** | 60K+ 轨迹，厨房场景 | 机器人操作基础 |
| **Droid** | 76K 轨迹，多场景 | V-JEPA 2 后训练（仅 62 小时无标注视频） |
| **RH20T** | 110K+ 接触丰富操作序列 | 精细操作世界模型训练 |
| **Cosmos 预训练数据** | 2 亿高质量视频片段 | Cosmos-Predict2.5 预训练（NVIDIA 内部） |
| **互联网视频（V-JEPA 2）** | 100 万小时 | 自监督视频预测预训练 |

### 4.2 主要 Benchmark

| Benchmark | arXiv / 来源 | 评测维度 | 状态 |
|-----------|-------------|---------|------|
| **WorldArena** | 2602.08971 (2026-02) | 视频感知质量（16 指标）+ 具身功能性（合成数据/规划/评估）；EWMScore 综合指标 | 公开排行榜 worldarena.ai |
| **WorldArena 2.0** | 2605.17912 (2026-05) | 扩展至视觉触觉、RL 环境、真实机器人 | 最新版本 |
| **EWMBench** | 2505.09694 (2025-05) | 场景一致性 + 运动正确性 + 语义对齐 | 开源工具 |
| **RoboWM-Bench** | 2604.19092 (2026-04) | 操作任务的可执行动作序列评测，含 Veo3.1 / Wan2.6 / Cosmos 对比 | 含商业模型 |
| **WorldModelBench** | 2502.20694 (2025-02) | 物理一致性（质量守恒等）、常识合理性，6.7 万人工标注 | ICLR 2025 |
| **WBench** | 2605.25874 (2026-05) | 多轮交互式视频世界模型评测 | 最新 |
| **Target-Bench** | 2511.17792 (2025-11) | 无地图路径规划，语义目标接近性 + 方向一致性 | |

### 4.3 评测方式分类

1. **像素质量指标**：FID、FVD、PSNR、SSIM（必要但不充分）
2. **物理一致性指标**：质量守恒、碰撞合理性、接触点准确性（EWMBench、WorldModelBench 重点）
3. **任务功能性指标**：合成数据的下游 VLA 性能提升；规划成功率；策略排名相关性（WorldArena 重点）
4. **零样本机器人执行**：直接在物理机器人上执行（V-JEPA 2 采用此方式）

**核心发现**（WorldArena 2026-02）：高视觉质量与强具身功能性之间存在显著差距（"perception-functionality gap"），即生成视频好看不等于能指导机器人完成任务。

---

## 5. 近 6-12 个月趋势（2025-H2 至 2026-H1）

### 5.1 世界模型 → 机器人策略的四种耦合模式

根据 arXiv:2605.00080（World Model for Robot Learning Survey，2026-04）：

**模式一：合成数据引擎（Data Engine）**
- 世界模型生成多样化轨迹，扩充真实数据不足的长尾场景
- 代表：GigaBrain-0、GigaWorld-0、Cosmos Predict（用于 1X/Figure 等）
- 效果：GigaBrain-0 整合 Sim2Real/Real2Real/HumanTransfer 等多类合成数据

**模式二：RL 后训练环境（Learned Simulator for RL）**
- 世界模型替代真实环境，提供奖励信号 + 状态转移
- 代表：World-Env（2025）、WMPO（2026）、WoVR（2026 世界模型-策略协同进化）
- DreamerV3 系继承：VLA-RFT（2025）在世界模型中做强化微调

**模式三：规划器（Planning via Imagination）**
- 给定目标图像，在世界模型中搜索动作序列（MPC / 轨迹排名）
- 代表：NWM（CVPR 2025）、V-JEPA 2-AC（零样本，2025）
- 有效规划窗口约 20-50 步（2-5 秒 @ 10Hz），受 compounding error 限制

**模式四：策略评估器（Policy Evaluator / Safety Guard）**
- 离线测试策略，无需物理部署
- 代表：WorldEval（arXiv:2505.19017，2025-05）、WorldArena
- 用途：Checkpoint 选择、安全异常检测、OOD 鲁棒性测试

### 5.2 核心技术趋势

1. **WAM 化**：VLA 与世界模型融合产生 World Action Model；DreamZero 等实现端到端联合视频+动作预测，获超 VLA 2× 泛化能力
2. **隐空间 vs 像素的折中**：VLA-JEPA（2026）、WoG（2026）等采用紧凑隐状态预测，比像素生成快 30× 以上（判断，基于综述叙述）
3. **基础模型规模化**：Cosmos 系从数十亿到 2000 亿+参数；数据量从 GB 级到 2 亿视频片段
4. **闭环评测**：世界模型从"生成工具"向"评测平台"演进，降低对真实机器人的依赖
5. **物理一致性后训练**：Cosmos-Predict2.5 引入 RL 后训练提升物理准确性；Cosmos Reason 加入链式思维视频理解

---

## 6. 开放问题 / 下一步方向

### 6.1 技术瓶颈

1. **Compounding Error（最核心）**：自回归世界模型每步误差积累，有效预测视窗约 20-50 步。当前缓解方案：chunk-wise 解噪（DreamZero）、层次化技能预测、定期重锚点（perception re-anchoring）。尚无根本解决方案。

2. **物理一致性 vs 视觉质量失衡**：FVD/FID 高分≠物理正确。现有视频生成骨干（DiT/Flow Matching）未显式建模刚体动力学、接触力学。WorldArena 2026-02 实验证实"感知-功能差距"存在。

3. **动作可控性与精度**：动作条件化视频生成的动作跟随精度不足，尤其在精细操作（毫米级接触）场景。RoboWM-Bench（2026-04）指出空间推理错误、接触预测不稳定为常见失败模式。

4. **实时性约束**：像素级视频生成（Cosmos 量级）推理延迟远超机器人控制频率（10-50Hz）。DreamZero 用 14B 视频扩散模型实现 7Hz 闭环，接近下限。隐空间方法（V-JEPA 系）是当前速度最优路线。

5. **长程记忆与世界一致性**：Genie 2 约 60 秒、Genie 3 提升至数分钟；开放世界长期一致性仍未解决。

6. **跨体型迁移（Cross-Embodiment）**：世界模型学习人类视频能否迁移至不同运动学结构的机器人，理论框架尚不成熟。DreamZero 展示了有限跨体型迁移能力（arXiv:2602.15922）。

7. **评测标准碎片化**：多个 Benchmark 并存（WorldArena / EWMBench / RoboWM-Bench / WorldModelBench），互不兼容，社区共识尚未形成。

### 6.2 开放研究方向

- **世界模型 × RL 的 scalability**：在世界模型中做大规模 RL（类 Dreamer，但面向复杂操作任务）
- **多模态物理感知**：视觉-触觉-力觉联合世界模型（WorldArena 2.0 开始探索）
- **世界模型作为通用评测平台**：替代昂贵的真实机器人测试，成为 CI/CD 管道的一部分
- **神经+物理混合仿真**：将可微分物理引擎（Isaac Sim 类）与神经世界模型结合，解决 Reality Gap

---

## 参考文献索引（综述）

- arXiv:2605.00080 — World Model for Robot Learning: A Comprehensive Survey（2026-04）
- arXiv:2510.16732 — A Comprehensive Survey on World Models for Embodied AI（2025-10）
- arXiv:2605.12090 — World Action Models: The Next Frontier in Embodied AI（2026-05）
- arXiv:2507.00917 — Learning Embodied Intelligence from Physical Simulators and World Models（2025-07）
- arXiv:2506.22355 — Embodied AI Agents: Modeling the World（2026-05）

---

## 关键论文（结构化）

> 格式：`arxiv_id | 标题 | 年份 | 一句话贡献`
> 排序：先奠基作，后 2025-2026 重要进展，再工具/benchmark

- 1803.10122 | World Models | 2018 | Ha & Schmidhuber 奠定"世界模型 = 编码器 + 隐动力学 + 策略"三组件范式
- 1912.01603 | Dream to Control: Learning Behaviors by Latent Imagination (DreamerV1) | 2020 | RSSM + 隐想象策略优化，奠定 Dreamer 系基础
- 2010.02193 | Mastering Atari with Discrete World Models (DreamerV2) | 2021 | 离散类别隐变量使 Dreamer 在 Atari 达人类水平
- 2301.04104 | Mastering Diverse Domains through World Models (DreamerV3) | 2023 | 单一超参数跨 150+ 任务 SOTA，首次无辅助从像素挖 Minecraft 钻石
- 2209.00588 | Transformers are Sample-Efficient World Models (IRIS) | 2023 | VQ-VAE + Transformer 世界模型，Atari 100k 超越人类 10/26 款
- 2302.00111 | Learning Universal Policies via Text-Guided Video Generation (UniPi) | 2023 | 将策略学习重表述为文本条件视频生成 + 逆动力学，打通视频生成与策略路线
- 2206.14176 | DayDreamer: World Models for Physical Robot Learning | 2022 | DreamerV3 移植至真实机器人，四足 1 小时学会站立行走，无仿真器
- 2309.17080 | GAIA-1: A Generative World Model for Autonomous Driving | 2023 | Wayve 首个面向自动驾驶的生成式世界模型，视频+文本+动作输入
- 2402.15391 | Genie: Generative Interactive Environments | 2024 | ICML 2024 Best Paper，从无标注视频无监督学习可交互潜在动作环境
- 2501.03575 | Cosmos World Foundation Model Platform for Physical AI | 2025 | NVIDIA 首批开放权重物理 AI 世界基础模型平台，含多子系统
- 2412.03572 | Navigation World Models (NWM) | 2024 | 条件扩散 Transformer 1B 参数，训练于多样化第一人称视频，MPC 框架导航规划，CVPR 2025
- 2506.09985 | V-JEPA 2: Self-Supervised Video Models Enable Understanding, Prediction and Planning | 2025 | Meta 自监督视频世界模型 100 万小时预训练，62 小时机器人数据后训练，零样本 80% 成功率
- 2605.00080 | World Model for Robot Learning: A Comprehensive Survey | 2026 | 43 页综述，系统梳理机器人学习中世界模型的策略耦合、仿真、视频生成三大范式
- 2510.16732 | A Comprehensive Survey on World Models for Embodied AI | 2025 | 三轴分类体系（功能性/时间建模/空间表示），跨机器人/自动驾驶/通用视频
- 2605.12090 | World Action Models: The Next Frontier in Embodied AI | 2026 | 首个 WAM 综述，建立 WAM vs VLA 的正式区分框架与 Cascaded/Joint 分类
- 2602.15922 | World Action Models are Zero-shot Policies (DreamZero) | 2026 | 联合视频-动作 chunk-wise 生成，7Hz 闭环，对 VLA 基线 2× 以上泛化提升
- 2511.19861 | GigaWorld-0: World Models as Data Engine to Empower Embodied AI | 2025 | 视频+3D 双引擎世界模型作为 VLA 训练数据工厂，含 Sim2Real/Real2Real 等多类合成数据
- 2602.08971 | WorldArena: A Unified Benchmark for Evaluating Perception and Functional Utility of Embodied World Models | 2026 | 首个兼顾视频感知质量与具身功能性的统一评测框架，揭示"感知-功能差距"
- 2502.20694 | WorldModelBench: Judging Video Generation Models As World Models | 2025 | 6.7 万人工标注，评测物理守恒/常识合理性，14 个前沿模型对比
- 2604.19092 | RoboWM-Bench: A Benchmark for Evaluating World Models in Robotic Manipulation | 2026 | 操作任务可执行性评测，将生成视频转化为机器人动作序列验证
- 2505.19017 | WorldEval: World Model as Real-World Robot Policies Evaluator | 2025 | 离线策略评估管道，Policy2Vec 编码潜在动作，替代真实机器人测试进行策略排名与安全检测
- 2505.09694 | EWMBench: Evaluating Scene, Motion, and Semantic Quality in Embodied World Models | 2025 | 场景一致性+运动正确性+语义对齐三维度评测，含开源工具
- 2511.00062 | World Simulation with Video Foundation Models for Physical AI | 2025 | NVIDIA Cosmos-Predict2.5 技术报告，统一多模态世界仿真与 RL 后训练
- 2510.19430 | GigaBrain-0: A World Model-Powered Vision-Language-Action Model | 2025 | 世界模型生成多类合成数据（Sim2Real/Real2Real/Human-transfer）驱动 VLA 训练
- 2507.00917 | A Survey: Learning Embodied Intelligence from Physical Simulators and World Models | 2025 | 分析机器人控制算法、仿真器、世界模型三者交互关系，2018-2025 综述
- 2506.22355 | Embodied AI Agents: Modeling the World | 2026 | 具身 AI Agent 世界建模方法综述
- 2605.17912 | WorldArena 2.0: Extending Embodied World Model Benchmarking | 2026 | 扩展至视觉触觉模态、RL 优化环境评测与真实机器人多体型测试
- 2605.25874 | WBench: A Comprehensive Multi-turn Benchmark for Interactive Video World Model Evaluation | 2026 | 多轮交互式视频世界模型评测 Benchmark
- 2511.17792 | Target-Bench: Can Video World Models Achieve Mapless Path Planning with Semantic Targets? | 2025 | 语义目标驱动的无地图路径规划评测，含接近性与方向一致性指标
