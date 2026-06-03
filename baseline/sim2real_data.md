---
id: sim2real_data
date: 2026-06-03
confidence: medium-high
sources: web search + official papers/docs, 2025-2026
branch: sim2real_data
---

# Sim2Real / 数据 / 仿真 分支现状基线

> 建立日期：2026-06-03 | 分析员：情报系统 AI 助手  
> 置信度说明：有 arXiv ID 或官方来源支撑的事实标为事实；来自行业报告/博客且未经同行评审的数据标为【未证实】；带有"据悉""预计"等字样的为判断推断。

---

## 1. 分支定义与边界

**Sim2Real / 数据 / 仿真** 是为 VLA（Vision-Language-Action）模型、操作策略和运动控制器提供「数据与仿真基础设施」的一层，覆盖：

- **仿真器**：物理引擎、渲染器、并行化框架（用于 RL 训练和数据生成）
- **真机数据集**：遥操作/人工演示采集形成的现实世界轨迹库
- **合成数据生成**：仿真 + domain randomization，或世界模型/生成式模型造数据
- **Sim2Real 迁移方法**：弥合仿真与真实之间的物理/视觉差距
- **数据格式与工具链**：RLDS、LeRobot 等格式，标注、管理工具
- **跨机体（Cross-Embodiment）数据**：聚合异质机器人数据、研究数据规模化律

**边界**：不包含 VLA 模型架构本身（归 VLA/Policy 分支），不包含最终的机器人硬件（归 机器人本体分支），但与两者均强耦合。

---

## 2. 当前主要方向

### 2.1 大规模真机数据集

目标是汇聚跨机构、跨机体、跨任务的真实机器人轨迹，形成类比 NLP 的 web 数据规模库。

**代表作**：

| 数据集 | 规模 | 机器人 / 场景 | 特点 |
|-------|------|--------------|------|
| Open X-Embodiment (OXE / RT-X) | ~100 万轨迹，22 种机体 | 全球多机构联合 | 首个大规模跨机体聚合，提出 RT-1/RT-X 模型 |
| DROID | 76k 轨迹 / 350 小时 | 564 场景，50 名采集员 | In-the-wild Franka Panda，3 相机，遥操作 |
| AgiBot World (Colosseo) | 100 万+ 轨迹（Beta: ~44 TB） | 100+ 真实场景，双臂人形 | 中国最大开源人形机械臂数据集；IROS 2025 最佳论文候选 |
| π0 训练集（Physical Intelligence） | 10,000+ 小时 | 7 种机体，68 任务 | 未公开，含 OXE + 自采 |

### 2.2 遥操作数据采集系统

低成本遥操作系统是采集演示数据的主流途径，2023-2025 年涌现大量工具。

**代表作**：

- **ALOHA / ALOHA 2**（Stanford ACT，赵子龙等）：低成本双臂遥操作，~1000 美元级硬件，50 条演示学会复杂任务
- **Mobile ALOHA**（arXiv 2401.02117，CoRL 2024）：在 ALOHA 上加移动底座，整体遥操作；与静态数据协同训练，成功率提升 30-50%
- **UMI（Universal Manipulation Interface）**（X Square Robot 等）：手持夹持器 + GoPro，无机器人即可采集
- **Genie Sim 3.0**（AgiBot，arXiv 2601.02078）：LLM 驱动场景生成 + 自动演示采集，含 >10,000 小时仿真演示
- **DexSkills / Mecka AI Egoverse**：分布式可穿戴设备采集人类第一视角行为数据（2026年 Mecka AI 宣布 6000 万美元 A 轮，【未证实】ARR $1亿）

### 2.3 仿真合成数据 + Sim2Real

**核心方法**：Domain Randomization（DR）——在仿真中随机化光照/纹理/质量/摩擦等参数，使策略对真实环境变化鲁棒。

**最新方向**（2025）：

- **MimicGen**（arXiv 2310.17596）：10 条人工演示自动扩增为 50k+ 条轨迹，大幅降低人工采集成本
- **Real2Render2Real（R2R2R）**（arXiv 2505.09601，CoRL 2025）：手机扫描物体 + 单条人类演示 → 大规模合成数据，与 150 条遥操作数据效果相当
- **DexScale**（ICML 2025 Poster）：自动化 Sim2Real 技能仿真扩增与 domain randomization，用于可部署操作策略
- **SplatSim**（arXiv 2409.10161）：3D Gaussian Splatting 替代传统 mesh → 高度真实感仿真，平均成功率 86.25%（真实数据训练 97.5%）
- **ReBot**（arXiv 2503.14526，IROS 2025）：Real-to-Sim-to-Real 视频合成，Octo 成功率 +17%，OpenVLA +20%

**当前共识**：视觉 sim2real gap（镜面/透明物体）仍是主要失效原因；3DGS + 物理引擎混合方案是当前最佳实践方向（事实，多实验室报告）。

### 2.4 生成模型 / 世界模型造数据

用视频世界模型生成机器人轨迹，是近 12 个月最热方向之一。

**代表作**：

- **DreamGen（GR00T-Dreams）**（arXiv 2505.12705，NVIDIA GEAR Lab）：用 Cosmos Predict2 视频世界模型，从 1 条 pick-and-place 遥操作 + 语言提示 → 22 种新行为；seen/unseen 环境成功率分别 43.2% / 28.5%（基线 GR00T N1 仅训练 pick-and-place = 0%）
- **GR00T N1 / N1.5**（arXiv 2503.14734，NVIDIA，2025-03）：人形机器人基础模型，混合真机轨迹 + 人类视频 + 合成数据训练；N1.5 借助 DreamGen 36 小时生成（否则需约 3 个月人工采集）
- **UniSim**（Google DeepMind）：视频世界模型用于合成训练片段 + 安全评估，已整合进部分 RT 系列训练（【未证实】具体版本细节）
- **Genie / Genie 2**（Google DeepMind）：互联网视频训练的生成式交互环境，Genie 2 支持 3D 控制；机器人方向：可在小量领域数据上微调代替从头训练（【未证实】大规模机器人部署数据）
- **RoboGen**（arXiv 2311.01455）：基于生成仿真的自动化机器人学习，LLM 生成任务 + 仿真数据

### 2.5 跨机体（Cross-Embodiment）数据

**关键问题**：如何让在 A 机器人上采集的数据帮助 B 机器人学习？

**进展**：

- OXE 数据覆盖 22 种机体；OXE-AugE（arXiv 2512.13100）进一步扩增 OXE 用于跨机体策略学习
- **Embodiment Scaling Laws**（arXiv 2505.05753，CoRL 2025）：扩大训练机体数（~1000 种程序生成机体）比扩大单机体数据量更能提升泛化，最优策略零样本迁移到 Unitree Go2 和 H1
- **Data Scaling Laws in Imitation Learning**（ICLR 2025 Oral + CoRL 2024 Best Workshop Paper）：在操作任务中研究数据规模化律，证明合适数据规模下单任务策略可零样本泛化到新物体/新场景
- **标准食谱**（2025 年行业共识，【未证实】具体数值）：OXE 预训练 → DROID 微调 → 任务演示微调，pi0、多家 2025 年人形策略采用此路线

---

## 3. 主流仿真器对比

| 仿真器 | 主导方 | GPU 并行 | 速度 | 渲染质量 | 可微分 | 适用场景 | arXiv/来源 |
|--------|--------|---------|------|---------|--------|---------|-----------|
| **Isaac Lab** | NVIDIA | 是（PhysX GPU） | ~82k-94k FPS（4096 env） | RTX 光追 | 计划（Newton 引擎） | 人形/四足运动，全身控制，大规模 RL | 2511.04831 |
| **Isaac Sim 5.0** | NVIDIA | 是 | 同上 | 光追级 | 否 | Isaac Lab 底座，2025 年开源 | NVIDIA 官方 |
| **Genesis** | Genesis AI（学术发起） | 是 | 10-80x 快于 Isaac Gym/MJX | Nyx 渲染器 | 是（Quadrants） | 多物理（刚/软/流体），触觉传感 | genesis-world.readthedocs.io |
| **MuJoCo / MJX** | DeepMind（开源） | MJX: JAX TPU，2.7M steps/s | 单环境快，多环境 MJX | 无（基础） | 是（MJX + JAX autodiff） | 学术操作研究，VLA 评估标准 | 官方文档 |
| **ManiSkill3** | UCSD/PKU（SAPIEN 基础） | 是 | 10-1000x vs 其他平台（30k+ FPS） | 较高 | 否 | 操作基准，GPU 并行 RL+IL | 2410.00425 |
| **SAPIEN** | 同上 | 部分 | 中 | 中 | 否 | ManiSkill 底座，关节物体支持好 | 开源 |
| **Genie Sim 3.0** | AgiBot | 是（Isaac Sim 集成） | 同 Isaac Sim | 光追级 | 否 | 人形，工业场景数字孪生 | 2601.02078 |
| **RoboVerse / MetaSim** | 学术联合（Malik/Abbeel等） | 是 | 多引擎抽象 | 多引擎 | 否 | 跨仿真器统一接口 | 2504.18904 |

**选型参考**：
- 人形/四足运动 RL → **Isaac Lab**
- 操作基准/学术 → **MuJoCo** 或 **ManiSkill3**
- 多物理/可微 → **Genesis**
- 大规模合成数据 + 光追渲染 → **Isaac Sim / Genie Sim**

---

## 4. 主流数据格式

| 格式 | 来源 | 特点 | 兼容性 |
|------|------|------|--------|
| **RLDS**（Reinforcement Learning Datasets） | Google | TFRecord 存储，OXE 标准格式 | RT-2/OpenVLA/Octo |
| **LeRobot v3.0** | HuggingFace | Parquet（状态/动作）+ MP4（视觉），支持流式加载，HF Hub 托管 | 可转 RLDS；LeRobot 框架原生 |
| **HDF5（ACT/ALOHA）** | 学术/斯坦福 | 简单，快速读写 | 操作研究常用 |
| **Robo-DM**（arXiv 2505.15558） | 学术 | 大规模机器人数据管理框架，处理异质数据 | 中间层管理 |

**趋势**：LeRobot v3.0（2025 年下半年发布）正成为开源社区新标准；RLDS 仍是大型 VLA 训练的主流；两者已有转换工具互通。

---

## 5. 关键玩家

### 学术 / 开源
- **Google DeepMind**：Open X-Embodiment、RT-X、Octo、UniSim、Genie；主导数据格式（RLDS）
- **斯坦福（Levine/Finn/赵子龙）**：ALOHA/Mobile ALOHA、DROID、OXE 核心贡献
- **UC Berkeley（Abbeel/Malik）**：RoboVerse、Real2Render2Real、Octo 联合
- **CMU**：DROID 采集，操作 RL 研究
- **CMU/UW/MIT 联合**：Embodiment Scaling Laws

### 工业 / 商业
- **NVIDIA**：Isaac Sim/Lab、Cosmos 世界模型、GR00T N1/N1.5/DreamGen；最大仿真基础设施提供者
- **Physical Intelligence（π.ai）**：π0/π0.5/π0-FAST；私有大规模多机体数据；$600M 融资（2024）
- **AgiBot（智元机器人，中国）**：AgiBot World 数据集（最大开源人形操作数据）、Genie Sim 3.0；IROS 2025 最佳论文候选
- **HuggingFace**：LeRobot 框架 + 数据集托管平台
- **X Square Robot**：UMI 采集工具，$140M 融资（【未证实】确切年份）
- **Mecka AI**：Egoverse 人类行为数据，分布式可穿戴采集，$60M 融资（2025-2026）
- **Cortex AI（YC 孵化）**：工作场所机器人 + 第一视角真实数据集

---

## 6. 近 6-12 个月趋势（2025-2026 中）

### 6.1 数据瓶颈怎么破？

**Ken Goldberg（UC Berkeley）在 2025 NVIDIA GTC 指出**：机器人基础模型与 LLM 的数据差距高达 120,000 倍【未证实，引用自行业报告，需核实原始数据】。

**三条破局路径（均在同步推进）**：

1. **真机数据规模化（工厂模式）**：AgiBot World 100 万轨迹（2025），Physical Intelligence 千人级数据团队，AgiBot/Figure/1X 等部署工厂机器人采集。
2. **合成数据质量突破**：DreamGen（NVIDIA）将单条演示扩增为 22 种行为；Real2Render2Real（CoRL 2025）单条人手演示 ≈ 150 条遥操作；Genie Sim 3.0 提供 10,000+ 小时仿真数据。
3. **世界模型 / 视频生成器作为「仿真器」**：Cosmos + DreamGen 已证明视频世界模型可直接生成有效策略数据；但泛化到未见环境的成功率（28.5%）仍远低于真实数据训练。

### 6.2 合成数据够用吗？

**结论（综合多实验室 2025 证据，判断）**：
- 合成数据已能有效**补充**真实数据，尤其在任务初期探索和场景多样化上；
- 对于**简单抓取**和**视觉导航**等任务，零样本 Sim2Real 已工程可用；
- 对于**接触丰富的精密操作**（装配、布料、透明物体），合成数据单独训练成功率仍显著低于真机数据（差距 15-30%，【未证实】具体数字来自行业分析）；
- **混合方案**（合成预训练 + 少量真实微调）是 2025 年主流实践，可达真实数据训练效果的 92-97%（【未证实】，需核实原始论文）。

### 6.3 Gaussian Splatting 进入仿真流水线

3DGS 正从纯渲染技术进入机器人仿真主流：SplatSim（arXiv 2409.10161）、RoboSimGS（Real2Sim2Real 框架）、多个 2025 仿真数据生成工作均采用 3DGS 重建真实场景后在其中生成轨迹，显著缩小视觉 domain gap。

### 6.4 数据格式标准化加速

LeRobot v3.0 + HuggingFace Hub 正成为开源数据集的事实标准；Robo-DM（arXiv 2505.15558）提出大规模机器人数据管理框架解决异质数据管理问题；AgiBot World 已部分对齐 LeRobot 格式。

---

## 7. 开放问题 / 下一步

1. **接触丰富操作的 Sim2Real**：软体/织物/透明物体的物理仿真精度仍不足；触觉传感数据的 sim2real 几乎未被解决。
2. **世界模型数据的可靠性上限**：DreamGen 在未见环境 28.5% 成功率是否可扩展？视频模型生成的数据是否有系统偏差（如物理不一致性）尚待研究。
3. **数据质量 vs 数量**：RoboCurate（arXiv 2602.18742）等工作开始研究数据质量筛选；大规模低质数据是否伤害性能是开放问题。
4. **跨机体动作空间对齐**：不同机体的关节空间、末端执行器语义不同，如何学习通用表征仍是核心挑战。
5. **长程任务数据稀缺**：现有数据集大多覆盖 10-30 秒操作；π0.5 的 10-15 分钟厨房任务数据是罕见例外。
6. **评估基准标准化**：SimplerEnv、ManiSkill3、RoboVerse 各有覆盖，缺乏社区统一 benchmark（类比 ImageNet 之于视觉）。
7. **数据飞轮**：工厂部署机器人是否能自动回采高质量数据，形成「部署 → 数据 → 训练」闭环，仍待验证。

---

## 关键论文（结构化）

- 2310.08864 | Open X-Embodiment: Robotic Learning Datasets and RT-X Models | 2023 | 汇聚 22 种机体 100 万真实轨迹，证明跨机体数据提升泛化，提出 RT-X 系列模型
- 2403.12945 | DROID: A Large-Scale In-The-Wild Robot Manipulation Dataset | 2024 | 76k 轨迹/350 小时，564 场景 Franka Panda In-the-Wild 数据集，三相机+遥操作
- 2401.02117 | Mobile ALOHA: Learning Bimanual Mobile Manipulation with Low-Cost Whole-Body Teleoperation | 2024 | 低成本移动双臂遥操作系统，协同静态数据训练成功率提升 30-50%
- 2405.12213 | Octo: An Open-Source Generalist Robot Policy | 2024 | 800k 轨迹训练的开源跨机体通用策略，支持 9 种机器人平台微调
- 2410.24164 | π0: A Vision-Language-Action Flow Model for General Robot Control | 2024 | 混合 7 机体 68 任务 10000+ 小时数据训练的 VLA flow 模型，Physical Intelligence
- 2310.17596 | MimicGen: A Data Generation System for Scalable Robot Learning using Human Demonstrations | 2023 | 10 条人工演示自动生成 50k+ 轨迹，大幅降低操作数据采集成本
- 2410.00425 | ManiSkill3: GPU Parallelized Robotics Simulation and Rendering for Generalizable Embodied AI | 2024 | GPU 并行仿真 10-1000x 加速，统一操作基准框架，SAPIEN 底座
- 2406.02523 | RoboCasa: Large-Scale Simulation of Everyday Tasks for Generalist Robots | 2024 | 厨房场景大规模仿真框架，联合 MimicGen 自动生成演示
- 2503.14734 | GR00T N1: An Open Foundation Model for Generalist Humanoid Robots | 2025 | NVIDIA 首个开源人形基础模型，混合真机/人类视频/合成数据训练，含逆动力学伪动作标注
- 2505.12705 | DreamGen: Unlocking Generalization in Robot Learning through Video World Models | 2025 | 视频世界模型（Cosmos）从单条演示扩增为 22 新行为，未见环境成功率 28.5%
- 2504.18904 | RoboVerse: Towards a Unified Platform, Dataset and Benchmark for Scalable and Generalizable Robot Learning | 2025 | 跨仿真器统一接口（MetaSim）+ 合成数据集 + 统一基准，支持 IL/RL/世界模型/Sim2Real
- 2503.14526 | ReBot: Scaling Robot Learning with Real-to-Sim-to-Real Robotic Video Synthesis | 2025 | Real2Sim2Real 视频合成流水线，Octo 成功率+17%，OpenVLA+20%
- 2505.09601 | Real2Render2Real: Scaling Robot Data Without Dynamics Simulation or Robot Hardware | 2025 | 手机扫描+单条演示生成大规模合成数据，效果≈150条遥操作；CoRL 2025
- 2505.05753 | Towards Embodiment Scaling Laws in Robot Locomotion | 2025 | 1000 种程序生成机体训练，证明扩机体数>扩数据量，零样本迁移 Unitree Go2/H1；CoRL 2025
- 2512.13100 | OXE-AugE: A Large-Scale Robot Augmentation of OXE for Scaling Cross-Embodiment Policy Learning | 2024 | 大规模扩增 OXE 用于跨机体策略学习
- 2511.04831 | Isaac Lab: A GPU-Accelerated Simulation Framework for Multi-Modal Robot Learning | 2025 | NVIDIA Isaac Lab 正式论文，GPU 并行 PhysX + RTX 渲染，统一 RL+IL 框架
- 2504.16054 | π0.5: a Vision-Language-Action Model with Open-World Generalization | 2025 | π0 升级版，移动操作 10-15 分钟复杂任务，新家庭场景零样本泛化
- 2503.06669 | AgiBot World Colosseo: A Large-scale Manipulation Platform for Scalable and Intelligent Embodied Systems | 2025 | 100 万+ 轨迹开源人形操作数据集，IROS 2025 最佳论文候选
- 2601.02078 | Genie Sim 3.0: A High-Fidelity Comprehensive Simulation Platform for Humanoid Robot | 2026 | AgiBot 开源人形仿真平台，LLM 场景生成 + 200 任务/10000+ 小时仿真数据，CES 2026 发布
- 2409.10161 | SplatSim: Zero-Shot Sim2Real Transfer of RGB Manipulation Policies Using Gaussian Splatting | 2024 | 3DGS 替代 mesh 实现高真实感仿真，零样本 Sim2Real 平均成功率 86.25%
- 2311.01455 | RoboGen: Towards Unleashing Infinite Data for Automated Robot Learning via Generative Simulation | 2023 | LLM 自动生成任务 + 仿真数据，开启生成式仿真数据流水线
- 2505.15558 | Robo-DM: Data Management For Large Robot Datasets | 2025 | 大规模异质机器人数据高效管理框架
- 2501.09747 | FAST: Efficient Action Tokenization for Vision-Language-Action Models | 2025 | 高效动作 tokenization，π0.5 采用，使 VLA 可处理高频动作序列
- 2603.04356 | RoboCasa365: A Large-Scale Simulation Framework for Training and Benchmarking Generalist Robots | 2026 | RoboCasa 扩展至 365 任务/2500 厨房场景，600+ 小时人工演示 + 1600 小时合成演示
