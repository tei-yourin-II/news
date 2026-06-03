---
id: dexterous_manipulation
date: 2026-06-03
version: baseline-v1
confidence: high (核心事实来自 arXiv 论文页、官方博客、产业报告；趋势判断标注置信度)
sources_checked: 2026-06-03
---

# 灵巧操作（Dexterous Manipulation）现状基线

> 本文档为「人形机器人/具身智能情报系统」灵巧操作分支的**初始基线**，后续新进展长在其上。  
> 覆盖重点：2025–2026 年中最新进展，兼收奠基性工作。  
> 未经充分核实的信息标注「未证实」。

---

## 1. 分支定义与边界

**灵巧操作**（dexterous manipulation）指机器人用多指手或双臂实现类人级别接触、力控与物体重定向的能力。本情报分支覆盖以下子领域：

| 子领域 | 关键词 |
|---|---|
| 多指灵巧手 | multi-finger dexterous hand, in-hand manipulation, finger-gaiting |
| 抓取 | grasping, 6-DoF grasp, functional grasp |
| 双手协同 | bimanual manipulation, two-arm coordination |
| 触觉感知 | tactile sensing, visuotactile, GelSight/DenseTact 系列 |
| 低成本遥操作 | ALOHA 系, UMI, teleoperation data collection |
| 模仿学习灵巧操作 | ACT, Diffusion Policy, behavior cloning |
| RL+sim2real 灵巧手 | RL dexterous hand, domain randomization, sim-to-real |
| VLA 融合 | VLA dexterous, language-conditioned dexterous manipulation |

**边界**：本分支不含纯移动导航（navigation），不含纯抓取无接触操作的工业夹爪（平行夹爪工业 pick-and-place），不含软体机器人（soft robotics）主赛道。与「人形机器人整机」「VLA 基础模型」分支存在交叉，以灵巧手/接触丰富操作为主轴划定归属。

---

## 2. 当前 SOTA 方法

### 2.1 模仿学习系：ACT / Diffusion Policy

**ACT（Action Chunking with Transformers）**
- 由 Stanford Tony Z. Zhao 等提出（arXiv 2304.13705，RSS 2023）。
- 核心：CVAE + Transformer，预测动作 chunk（一组连续关节目标）而非单步动作，配合时间集成（temporal ensembling）消抖。
- 平台：ALOHA 双臂低成本遥操作系统；50 条演示可达 80–90% 成功率于细粒度任务（充电线插接、翻转电池等）。
- 状态：2024–2025 年仍是许多灵巧手研究的基线；在执行速度敏感任务上仍优于 Diffusion Policy。

**Diffusion Policy**
- 由 Columbia Cheng Chi 等提出（arXiv 2303.04137，RSS 2023 / IJRR 2024）。
- 核心：将机器人策略建模为条件去噪扩散过程，支持多模态动作分布；在 12 项任务中平均比当时 SOTA 高 46.9%。
- 2025 状态：成为 ALOHA Unleashed（arXiv 2410.13126）、RDT-1B、π0 等工作的核心动作头。适合接触丰富/变形物体任务；推理延迟高于 ACT（需多步去噪）。
- 最新扩展：3D Diffusion Policy（点云输入）、Reactive Diffusion Policy（融合触觉快慢回路，arXiv 2503.02881，RSS 2025）。

**ALOHA Unleashed**（arXiv 2410.13126，2024）
- Google DeepMind + Stanford；在 ALOHA 2 平台大规模采集数据 + Diffusion Policy，攻克双臂变形物体（折叠衣物、打蝴蝶结等）及复杂接触操作。评估 5 个真实 + 3 个仿真任务。

**RDT-1B**（arXiv 2410.07864，ICLR 2025）
- 1B 参数 Diffusion Transformer，预训练于 100 万+多机器人 episode；支持双臂灵巧任务；1–5 条演示即可泛化到新技能。

**π0（Physical Intelligence）**（arXiv 2410.24164，2024）
- Flow matching（扩散变体）+ PaliGemma VLM 骨干；在 7 平台 68 任务训练；已完成折叠衣物、整理桌面等高灵巧演示。
- π0.7（2025，未证实具体发布日期）：泛化能力大幅提升，在陌生家庭环境完成整屋整理任务。

**OpenVLA-OFT**（arXiv 2502.19645，2025）
- 优化微调配方：25–50× 更快推理、支持双目多图输入；在 ALOHA 双臂任务上超越 π0、RDT-1B、Diffusion Policy 最多 15% 成功率。

### 2.2 RL + Sim2Real 灵巧手

**Sim-to-Real RL on Humanoids**（arXiv 2502.20396，CoRL 2025）
- Toru Lin, Jitendra Malik, Yuke Zhu 等；自动 real-to-sim 参数标定 + 分治策略蒸馏 + 混合物体表征；在人形机器人上实现抓取、箱子举起、双手递送的视觉驱动灵巧操作，高成功率于未见物体。

**Zero-Shot Sim-to-Real Force-Based Grasping**（arXiv 2601.02778，2026）
- 12-DoF 灵巧手；集成触觉+电机电流传感+高效仿真；无需微调实现可控抓取力追踪与掌内重定向。

**DexHandDiff**（arXiv 2411.18562，CVPR 2025）
- 交互感知扩散规划；双阶段（接触对齐 + 目标导向控制）；灵巧任务平均成功率 70.7%。

**DexMachina**（arXiv 2505.24853，2025）
- Columbia/NVIDIA；虚拟物体控制器逐步消退的课程方法，使策略从人手演示中学习功能性双手灵巧操作；发布仿真 benchmark，支持 Inspire、Allegro、XHand、Schunk 四种手型。

### 2.3 触觉融合

**Reactive Diffusion Policy (RDP)**（arXiv 2503.02881，RSS 2025）
- 慢快双层：慢层（Diffusion Policy，低频动作 chunk） + 快层（触觉闭环高频控制）；配套低成本 TactAR AR 遥操作系统；显著超越纯视觉基线于接触丰富任务。

**Sparsh-X / Tactile Beyond Pixels**（arXiv 2506.14754，2025，Meta FAIR）
- 四模态触觉融合（图像、音频、运动、压力）；Digit 360 传感器，100 万接触交互自监督训练；策略成功率提升 63%，物理属性识别准确率提升 48%，物体状态恢复鲁棒性提升 90%。

**Contact-Grounded Policy (CGP)**（arXiv 2603.05687，2026）
- 条件扩散模型预测多点接触轨迹 + 触觉反馈；学习的接触一致性映射转为顺应控制目标；在 Allegro V5 及五指手上超越视觉/触觉 Diffusion Policy 基线，涵盖掌内操作、精细抓取、工具使用。

**ManiFeel**（arXiv 2505.18472，2025）
- 系统性视触觉策略学习 benchmark；覆盖插入、齿轮装配、暗光操作等任务；揭示不同触觉模态的任务依赖优势。

**ManiSkill-ViTac 2025 Challenge**（arXiv 2411.12503）
- 三赛道竞赛：纯触觉操作、视触觉融合操作、触觉传感器结构设计；推动领域标准化评测。

### 2.4 双手协同

**Mobile ALOHA**（arXiv 2401.02117，2024，Stanford）
- 双臂 + 移动底盘；全身遥操作数据采集；协同模仿学习实现炒菜、清洁等全身任务。

**RDT-1B**（同上）兼支持双臂灵巧控制。

**DemoBot**（arXiv 2601.01651，2026）
- 从第三人称人类视频学习双臂灵巧操作，无需机器人演示。

**H-RDT**（arXiv 2507.23523，2025）
- 基于 EgoDex（338K+ 轨迹、194 任务）训练的双臂操作模型；覆盖人类操作策略与双手协调模式。

**BiCICLe（Bimanual Multi-Agent In-Context Learning）**（arXiv 2604.20348，2026）
- 首个无需微调让标准 LLM 执行少样本双臂操作的框架；leader-follower 分解动作空间。

### 2.5 遥操作数据采集驱动

**ALOHA / ALOHA 2**（arXiv 2304.13705 / 2405.02292）
- Stanford + Google DeepMind；低成本双臂遥操作（<$20K 原始设计）；全球数十个实验室复现；ALOHA 2 改进人体工程学与鲁棒性，MuJoCo 系统辨识开源。

**UMI（Universal Manipulation Interface）**（arXiv 2402.10329，RSS 2024）
- 手持夹爪 + GoPro 随身采集；无需机器人即可在野外采集高质量演示；FastUMI（ICML 2025）提供 15,000+ 真实演示 24 任务开放数据集；UMI-3D（arXiv 2604.14089，2026）加入 LiDAR 实现 3D 感知。

**DexCap**（arXiv 2403.07788，2024）
- 便携手部动捕系统（SLAM + 电磁场）+ DexIL 模仿学习；6 个灵巧任务验证；支持野外动捕数据转机器人策略。

**EgoDex**（arXiv 2505.11709，ICLR 2026）
- Apple Vision Pro 采集；829 小时 egocentric 视频 + 3D 手指关节追踪；194 桌面任务；灵巧操作预训练新基准。

**EgoScale**（arXiv 2602.16710，2026，NVIDIA）
- 20,854 小时动作标注 egocentric 人类视频（20× 于前作）；VLA 两阶段迁移到 Unitree G1 + 7-DoF 三指手；成功率提升 54%；发现数据量与 validation loss 的对数线性 scaling law。

**DexMimicGen**（arXiv 2410.24185，ICRA 2025，NVIDIA）
- 60 条人类演示自动合成 21,000 条仿真演示；异步双臂执行策略 + 同步约束；real-to-sim-to-real 流水线，在人形机器人饮料罐分拣任务部署。

**GR-Dexter**（arXiv 2512.24210，ByteDance Seed，2025）
- ByteDexter V2 手（21-DoF，指尖压阻触觉传感）+ 直觉双手遥操作系统 + VLA 训练；在长时域家庭操作与泛化拾放任务强性能。后续 GR-RL 用 RL 微调将鞋带系结成功率从 45.7% 提升至 83.3%。

---

## 3. 关键论文清单（详见末节）

见本文末尾「## 关键论文（结构化）」部分，共列 **32 条**。

---

## 4. 关键玩家

### 学术机构

| 机构 | 代表工作 | 核心人物 |
|---|---|---|
| Stanford | ALOHA/ACT, Mobile ALOHA, ALOHA Unleashed | Tony Zhao, Chelsea Finn, Fei-Fei Li |
| Columbia | Diffusion Policy, DexMachina, UMI | Shuran Song, Cheng Chi |
| UC Berkeley | EgoScale, 多 VLA 工作 | Sergey Levine, Trevor Darrell, Pieter Abbeel |
| MIT | Diffusion Policy（合著）, 触觉相关 | Russ Tedrake, Alberto Rodriguez |
| CMU | 灵巧 RL, 接触建模 | David Held, Deepak Pathak |
| NVIDIA SRL | DexMimicGen, EgoScale, Isaac Lab | Yuke Zhu, Linxi Fan, Ajay Mandlekar |
| Google DeepMind | ALOHA 2, Gemini Robotics, RT-X | Pete Florence, Danny Driess |
| ByteDance Seed | GR-Dexter, GR-RL | 傅立叶（Hang Li 领导的机器人团队） |
| Physical Intelligence | π0, π0.7 | Sergey Levine, Chelsea Finn, Benjamin Burchfiel |

### 灵巧手硬件公司

| 公司 | 国家 | 代表产品 | 特点 |
|---|---|---|---|
| Shadow Robot | 英国 | DEX-EE / Dexterous Hand | 行业最早商业灵巧手；~$65K起；24-DoF |
| Wonik Robotics | 韩国 | Allegro Hand V4/V5 | 16-DoF；学术主流；<$25K；360° 指尖触觉（V5） |
| INSPIRE ROBOTS（因时机器人） | 中国 | RH系列 | 2025 年出货量破万；春晚亮相；行业规模第一（未证实全球占比） |
| LinkerBot（灵心巧手） | 中国 | 科研版42-DoF | 已完成红杉中国、蚂蚁集团等多轮融资（2025）；自称80%+全球高自由度灵巧手市占率（未证实） |
| 星动纪元（ROBOTERA） | 中国（清华孵化） | XHand 1（12-DoF） | 全栈自研；L7人形 |
| Unitree（宇树） | 中国 | Dex5（20-DoF，94触觉传感器）| 与 NVIDIA Isaac GR00T 平台集成 |
| ByteDance/ByteDexter | 中国 | ByteDexter V2（21-DoF）| 内部研发；指尖压阻触觉 |
| Fourier（傅里叶） | 中国 | GR-2 12-DoF手 + 6阵列触觉传感器 | 配套 GR-2 人形 |
| Sharpa（收购整合） | 美国 | Wave（22-DoF + 触觉）| 与 NVIDIA Isaac GR00T 参考人形集成（2026）|

---

## 5. 硬件 / 数据集 / Benchmark

### 5.1 灵巧手平台

| 平台 | DoF | 触觉 | 主要用途 |
|---|---|---|---|
| Shadow Dexterous Hand | 24 | 可选 BioTac | 科研高精度 |
| Allegro Hand V4 | 16 | 无（V5 有） | 学术灵巧 RL 主流平台 |
| Allegro Hand V5 | 16 | 360° 指尖 | 替换 V4 |
| Unitree Dex5 | 20 | 94 高精度传感器 | 人形机器人集成 |
| ByteDexter V2 | 21 | 压阻指尖 | VLA 双手任务 |
| LEAP Hand（CMU） | 16 | 无 | 低成本可打印 |

### 5.2 触觉传感器

| 传感器 | 类型 | 分辨率/特点 | 状态 |
|---|---|---|---|
| GelSight（MIT→GelSight Inc.） | 光学弹性体 | 高分辨率 3D 接触几何 | 成熟商用；2026 SBIR Phase II 军方合同 |
| DenseTact-mini | 光学 | 适合从平面拿取多尺度物体 | 学术实验室 |
| Digit（Meta）/ Digit 360 | 光学 | 四模态（Sparsh-X 使用）| 开放研究版 |
| XELA uSkin | 电容矩阵 | 柔性贴合 | 商用 |
| Fourier GR-2 指尖传感器 | 阵列式 | 6传感器/手 | 集成于人形 |
| BioTac（Syntouch，已停产）| 流体 | 多模态 | 历史参考 |

### 5.3 数据采集方案

| 方案 | 演示规模 | 特点 |
|---|---|---|
| ALOHA / ALOHA 2 | 50–数千条/任务 | 低成本双臂遥操作；全球最广复现 |
| UMI / FastUMI | 15,000+ 演示（FastUMI） | 随身夹爪；无机器人在场采集 |
| DexCap | 数百条/任务 | 手部动捕 + SLAM |
| DexMimicGen | 自动合成 21K 条 | 60 条人类演示生成 |
| EgoDex | 829 小时 | Apple Vision Pro；3D 关节追踪 |
| EgoScale | 20,854 小时 | MANUS 手套 + egocentric 视频 |
| MANUS 数据手套 | — | ByteDance Seed, NVIDIA 均使用 |
| TactAR（RSS 2025） | — | AR 实时触觉反馈遥操作 |

### 5.4 评测 Benchmark

| Benchmark | 覆盖范围 | 状态 |
|---|---|---|
| LIBERO | 生命周期学习双臂操作序列 | 广泛采用 |
| Bi-DexHands | 仿真双手大规模 RL benchmark | 学术参考 |
| DexArt | 关节物体灵巧操作泛化 | 仿真 |
| DexMachina Benchmark | 双手灵巧功能性重定向，4种手型 | 2025 新建 |
| ManiSkill-ViTac 2025 | 视触觉操作竞赛 | 竞赛形式 |
| ManiFeel | 系统性视触觉策略学习评测 | 2025 新建 |
| RoboEval | 双臂操作能力分层评测 | 2025 新建 |
| VTDexManip | 视触觉灵巧操作 RL benchmark | OpenReview 在审（未证实接受状态） |
| OakInk-v2 | 双手灵巧操作姿态 GT | DexMan 使用 |

---

## 6. 近 6–12 个月趋势（2025 年初 – 2026 年中）

### 趋势 1：大规模人类数据驱动的预训练（★★★★★）

最显著趋势。EgoDex（829h Apple Vision Pro）、EgoScale（20,854h egocentric 视频，NVIDIA）均表明：人类数据可以作为灵巧操作的预训练来源，通过少量机器人数据对齐即可迁移。EgoScale 发现 log-linear scaling law：数据量与 validation loss 呈对数线性关系，成功率平均提升 54%。

### 趋势 2：VLA 与灵巧操作深度融合（★★★★★）

π0（flow matching + VLM），Gemini Robotics On-Device（2025.06），GR-Dexter（VLA + 21-DoF 双手），OpenVLA-OFT，GR-RL（RL 后训练推高 VLA 灵巧专业化）。VLA 已从通用抓取渗透到接触丰富的灵巧操作。Gemini Robotics On-Device 在 50–100 条演示下实现泛化，支持折叠、拉链等精细任务。

### 趋势 3：触觉从「可选」变「必需」（★★★★☆）

Reactive Diffusion Policy（慢快回路）、Contact-Grounded Policy、Sparsh-X（63% 成功率提升）、ManiFeel benchmark、ManiSkill-ViTac 竞赛均指向：纯视觉策略在精细接触任务上碰到天花板，触觉融合成刚需，但统一触觉表征（多传感器、多模态）仍是开放问题。

### 趋势 4：Sim2Real 越来越「可交付」（★★★★☆）

Zero-Shot Force-Based Grasping（arXiv 2601.02778）无需微调即部署 12-DoF 灵巧手力控；DexMimicGen 60→21K 自动数据扩增后 real-to-sim-to-real 在人形机器人上成功；DexMachina 课程方法跨多种手型泛化。仿真与真实物理（摩擦、软接触）差距仍存在，但正在被系统性缩小。

### 趋势 5：中国产业链全面崛起（★★★★☆）

因时机器人 2025 年交付破万；Unitree Dex5（20-DoF，94 触觉传感器）接入 NVIDIA GR00T；LinkerBot 完成亿元量级多轮融资（红杉中国、蚂蚁集团）；ByteDance Seed 开发 GR-RL 完成完整系鞋带（行业首次声明）；Zhiyuan Robot（智元机器人）将灵巧手业务独立剥离。竞争格局从学术研究快速转向产品化。

### 趋势 6：跨具身（Cross-Embodiment）迁移（★★★☆☆）

Scaling Cross-Embodiment World Models（arXiv 2511.01177）、DexFormer、One Hand to Rule Them All（arXiv 2602.16712）探索通用跨手型迁移。核心洞察：训练具身越多，对未见具身的泛化越强；3D 粒子表示可统一不同自由度的手型表达。目前仍在仿真验证阶段，真实硬件结果有限（未证实大规模真实硬件验证）。

---

## 7. 开放问题 / 下一步

1. **触觉统一表征**：市场上传感器异构（光学/电容/压阻），跨传感器迁移学习方案仍不成熟；UniTouch 等工作是第一步，但多手/多传感器同时训练仍是挑战。

2. **接触物理仿真精度**：摩擦、软体形变、多点接触的仿真依然不够精确，导致 sim2real gap 在极细粒度任务（如针线穿引、精密装配）依然显著。

3. **长时域灵巧任务**：多步骤灵巧任务（系完整鞋带、折叠任意衣物）虽已有 demo，但鲁棒性与泛化率不稳定；GR-RL 将鞋带成功率从 45.7% 提至 83.3% 仍有 17% 失败。

4. **数据效率**：EgoScale 需要 20,854 小时预训练数据；减少人类数据依赖（少样本/无监督）是核心开放问题。

5. **手型与任务的协同设计**：Cross-Embodiment Co-Design（arXiv 2512.03743）指出，手型设计与学习算法的联合优化尚未系统化。

6. **灵巧手耐用性与成本**：Shadow（~$65K）、Unitree Dex5 在工业场景的磨损、可维护性尚无系统性报告（未证实）。中国低成本方案（因时、LinkerBot）的长期可靠性数据有限。

7. **安全接触力控**：与人共存场景下，灵巧手的力边界控制与安全停止策略仍属研究早期。

---

## 关键论文（结构化）

> 格式：`- arxiv_id | 标题 | 年份 | 一句话贡献`  
> 无 arXiv 号的重要工作标注 [非arXiv]

### 奠基性工作

- 2304.13705 | Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware (ALOHA/ACT) | 2023 | 提出 ALOHA 双臂低成本遥操作平台与 ACT 动作分块 Transformer，50 条演示达 80–90% 成功率
- 2303.04137 | Diffusion Policy: Visuomotor Policy Learning via Action Diffusion | 2023 | 将机器人策略建模为条件扩散过程，12 任务平均超 SOTA 46.9%
- 2402.10329 | Universal Manipulation Interface: In-The-Wild Robot Teaching Without In-The-Wild Robots | 2024 | 手持夹爪随身采集系统，无需机器人即可在野外获取高质量双手演示
- 2403.07788 | DexCap: Scalable and Portable Mocap Data Collection System for Dexterous Manipulation | 2024 | SLAM+电磁场便携手部动捕系统，配套 DexIL 将野外动捕数据转机器人策略

### 数据规模化 / 预训练

- 2505.11709 | EgoDex: Learning Dexterous Manipulation from Large-Scale Egocentric Video | 2025 | Apple Vision Pro 采集 829 小时 egocentric 视频 + 精准 3D 手指追踪，194 任务，ICLR 2026
- 2602.16710 | EgoScale: Scaling Dexterous Manipulation with Diverse Egocentric Human Data | 2026 | 20,854 小时人类数据预训练 VLA 后迁移到灵巧手，发现 log-linear scaling law，成功率平均提升 54%
- 2410.24185 | DexMimicGen: Automated Data Generation for Bimanual Dexterous Manipulation via Imitation Learning | 2024 | 60 条人类演示自动合成 21,000 条仿真轨迹，ICRA 2025，human-to-sim-to-real 流水线
- 2310.08864 | Open X-Embodiment: Robotic Learning Datasets and RT-X Models | 2023 | 22 机器人 527 技能开放数据集，跨具身预训练基础

### 双手 / 灵巧 VLA 系

- 2410.13126 | ALOHA Unleashed: A Simple Recipe for Robot Dexterity | 2024 | ALOHA 2 大规模采集 + Diffusion Policy 攻克变形物体双臂操作
- 2410.07864 | RDT-1B: a Diffusion Foundation Model for Bimanual Manipulation | 2024 | 1B 参数 Diffusion Transformer，1M+ 多机器人 episode 预训练，1–5 条演示可学新技能，ICLR 2025
- 2410.24164 | π0: A Vision-Language-Action Flow Model for General Robot Control | 2024 | Flow Matching + PaliGemma VLM，7 平台 68 任务训练，最强通用灵巧策略之一
- 2502.19645 | Fine-Tuning Vision-Language-Action Models: Optimizing Speed and Success (OpenVLA-OFT) | 2025 | 优化 VLA 微调配方，25–50× 更快推理，双臂任务超 π0/RDT-1B 最多 15%
- 2512.24210 | GR-Dexter Technical Report (ByteDance Seed) | 2025 | 21-DoF 双手 + VLA 训练框架，首个在鞋带任务 RL 后训练突破 83% 成功率（GR-RL 配套工作）
- 2604.20348 | Bimanual Robot Manipulation via Multi-Agent In-Context Learning (BiCICLe) | 2026 | 首个无微调 LLM few-shot 双臂操作框架，leader-follower 分解动作空间

### RL + Sim2Real

- 2502.20396 | Sim-to-Real Reinforcement Learning for Vision-Based Dexterous Manipulation on Humanoids | 2025 | 自动 real-to-sim 标定 + 分治蒸馏，人形机器人视觉灵巧 RL 高成功率，CoRL 2025
- 2601.02778 | Closing the Reality Gap: Zero-Shot Sim-to-Real Deployment for Dexterous Force-Based Grasping | 2026 | 12-DoF 灵巧手，触觉+电流传感+仿真，无微调零样本部署力控抓取与掌内重定向
- 2411.18562 | DexHandDiff: Interaction-aware Diffusion Planning for Adaptive Dexterous Manipulation | 2024 | 双阶段扩散规划（接触对齐 + 目标导向），灵巧任务平均 70.7% 成功率，CVPR 2025

### 跨具身 / 功能重定向

- 2505.24853 | DexMachina: Functional Retargeting for Bimanual Dexterous Manipulation | 2025 | 虚拟物体控制器课程法，从人手演示学功能性双手灵巧，支持 4 种手型 benchmark
- 2511.01177 | Scaling Cross-Embodiment World Models for Dexterous Manipulation | 2025 | 3D 粒子表示统一多具身，世界模型规模化改善对未见手型的泛化
- 2602.16712 | One Hand to Rule Them All: Canonical Representations for Unified Dexterous Manipulation | 2026 | 规范表示统一多手型灵巧策略迁移

### 触觉 / 视触觉

- 2506.14754 | Tactile Beyond Pixels: Multisensory Touch Representations for Robot Manipulation (Sparsh-X) | 2025 | 四模态触觉统一表示，100 万接触交互训练，策略成功率提升 63%
- 2503.02881 | Reactive Diffusion Policy: Slow-Fast Visual-Tactile Policy Learning for Contact-Rich Manipulation | 2025 | 慢快双层视触觉策略（Diffusion + 触觉闭环），配套 TactAR 低成本遥操作，RSS 2025
- 2603.05687 | Contact-Grounded Policy: Dexterous Visuotactile Policy with Generative Contact Grounding | 2026 | 扩散模型预测接触轨迹+触觉，接触一致性映射转顺应控制，超视觉/触觉 Diffusion Policy 基线
- 2505.18472 | ManiFeel: Benchmarking and Understanding Visuotactile Manipulation Policy Learning | 2025 | 首个系统性视触觉操作策略学习 benchmark，揭示触觉模态任务依赖优势
- 2401.18084 | Binding Touch to Everything: Learning Unified Multimodal Tactile Representations (UniTouch) | 2024 | 对齐触觉嵌入到视觉/语言/声音，首个跨传感器触觉多模态统一模型
- 2411.12503 | ManiSkill-ViTac 2025: Challenge on Manipulation Skill Learning with Vision and Tactile Sensing | 2024 | 三赛道视触觉操作竞赛，推动触觉操作标准化评测

### 抓取

- [非arXiv] AnyDexGrasp | AnyDexGrasp: Learning General Dexterous Grasping for Any Hands | 2025 | 40 物体训练即泛化，100 次尝试内收敛，展示 scaling 维度选择关键性（来源：graspnet.net）

### 数据采集 / 遥操作

- 2405.02292 | ALOHA 2: An Enhanced Low-Cost Hardware for Bimanual Teleoperation | 2024 | ALOHA 改进版，更好人体工程学与鲁棒性，MuJoCo 模型开源
- 2601.01651 | DemoBot: Learning Bimanual Manipulation with Dexterous Hands From Third-Person Human Videos | 2026 | 从第三人称人类视频无需机器人演示学习双手灵巧操作
- 2604.14089 | UMI-3D: Extending Universal Manipulation Interface from Vision-Limited to 3D Spatial Perception | 2026 | UMI 扩展：腕部 LiDAR 加入 3D 空间感知
- 2509.23829 | DexFlyWheel: A Scalable and Self-improving Data Generation Framework for Dexterous Manipulation | 2025 | 自改进循环持续丰富数据多样性的灵巧操作数据生成框架

---

*文档生成时间：2026-06-03 | 作者：具身智能情报系统（Claude Sonnet 4.6）*  
*置信度说明：论文级事实（arXiv 可查）= 高置信；产业数字（市占率、融资金额等）= 中等置信（信息源为新闻报道）；趋势判断 = 分析性结论，标注「未证实」的需进一步核实*
