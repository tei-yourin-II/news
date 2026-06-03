---
branch_id: vla
branch_name: "Vision-Language-Action (VLA) 视觉-语言-动作模型"
generated_date: "2026-06-03"
confidence_note: |
  本报告基于截至 2026-06-03 的公开文献、arXiv 预印本、实验室博客及新闻报道。
  标注「[未证实]」的条目来自非同行评审来源或尚未独立核实的声明。
  模型性能数字来自各团队自报，存在评测条件不统一的问题，需谨慎对比。
  中国团队的技术细节多来自公司公告，独立核实程度较低。
author: "具身智能情报系统 自动生成"
version: "1.0"
---

# VLA（视觉-语言-动作模型）现状基线

> **用途**：作为人形机器人/具身智能情报系统的 VLA 分支种子节点，后续每日新论文以此为基准增量更新。
> **时间范围**：重点覆盖 2025 年至 2026 年 6 月；奠基性工作追溯至 2023 年。

---

## 1. 分支定义与边界

### 1.1 什么是 VLA

Vision-Language-Action（VLA）模型是一类将**视觉感知、自然语言理解、机器人动作生成**三者统一在单一神经网络（或紧耦合双系统）中的机器人策略模型。其核心特征是：

- **输入**：RGB 图像（单/多摄像头）+ 自然语言指令（可选：机器人状态、触觉、深度）
- **输出**：连续或离散动作序列（末端执行器姿态、关节角度等），可跨任务、跨机器人泛化
- **基础**：依赖大规模预训练的视觉-语言模型（VLM）作为主干，迁移互联网规模知识

### 1.2 与邻近领域的区分

| 概念 | 与 VLA 的关系 |
|------|--------------|
| **World Model（世界模型）** | 学习环境动态（预测下一帧/状态）；VLA 直接预测动作。两者开始融合：VLA+WM 联合训练（如 GigaBrain-0、VLAW），但核心目标不同 |
| **纯操作策略（Manipulation Policy）** | 如 ACT、Diffusion Policy：不使用预训练 VLM，任务范围窄，泛化能力弱；VLA 以 VLM 为骨干，具备语言泛化 |
| **LLM/VLM 用于规划（Task Planning）** | 如 SayCan：语言模型作高层规划器，底层由单独策略执行；VLA 是端到端的，语言理解与动作生成耦合 |
| **具身导航（Embodied Navigation）** | 任务空间是移动/探索而非操作；部分工作（CrossFormer）尝试统一，但 VLA 主要聚焦操作 |

### 1.3 定义边界的共识与争议

- **共识**：需要 VLM 骨干 + 机器人数据微调 + 产生可执行动作 = VLA
- **争议**：双系统架构（如 Helix、GR00T N1）中 VLM 只做高层规划、动作由独立模块生成，是否算"纯 VLA"存在分歧。本报告将其列为 **VLA 变体（Dual-System VLA）**

---

## 2. 当前 SOTA 方法与代表模型

### 2.1 架构范式总览

当前 VLA 领域已收敛出三大主要范式，以及两类混合/扩展路线：

```
┌─────────────────────────────────────────────────────────────────────┐
│  范式一：自回归 Token（Autoregressive Token）                        │
│  代表：RT-2, OpenVLA, UniVLA                                        │
│  原理：将动作离散化为 token，插入语言模型 next-token 预测流程        │
│  优点：直接继承 VLM 推理能力，训练简单                              │
│  缺点：离散化损失精度；自回归推理延迟高；难以建模多模态动作分布     │
├─────────────────────────────────────────────────────────────────────┤
│  范式二：扩散解码器（Diffusion Decoder / Diffusion Head）           │
│  代表：RDT-1B, GR00T N1 (System 1), Octo                          │
│  原理：VLM 提取语义特征，扩散模型迭代去噪生成连续动作              │
│  优点：精准连续动作，天然建模多模态分布                             │
│  缺点：扩散头与 VLM 主干分离，推理慢（DDPM），语言推理弱           │
├─────────────────────────────────────────────────────────────────────┤
│  范式三：流匹配（Flow Matching）                                    │
│  代表：π0, π0.5, GraspVLA                                         │
│  原理：学习从噪声到动作的确定性流，兼顾精度与速度                  │
│  优点：比 DDPM 快；可训练大规模跨体态数据；保留 VLM 推理           │
│  缺点：仍比自回归慢；训练比扩散复杂                                │
├─────────────────────────────────────────────────────────────────────┤
│  扩展路线 A：双系统架构（Dual-System / System 1 + System 2）       │
│  代表：GR00T N1, Figure Helix                                      │
│  原理：VLM（慢，~10Hz）做场景理解，扩散/轻量策略（快，~120-200Hz）做精细控制 │
├─────────────────────────────────────────────────────────────────────┤
│  扩展路线 B：混合（Hybrid）：单模型内同时有自回归+扩散             │
│  代表：HybridVLA, DiffusionVLA                                     │
│  原理：共享 LLM 骨干，同时预测语言推理链（AR）和连续动作（扩散）   │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 代表模型详表

#### 奠基性模型（2023-2024）

| 模型 | 机构 | 年份 | 参数量 | 架构范式 | 核心贡献 | 来源 |
|------|------|------|--------|----------|---------|------|
| **RT-2** | Google DeepMind | 2023 | 55B | 自回归（PaLM-E/PaLI-X骨干） | 首个大规模 VLA：将机器人动作表示为语言 token，与视觉问答联合训练，展示 emergent 泛化 | [arXiv:2307.15818](https://arxiv.org/abs/2307.15818) |
| **Octo** | 伯克利等 | 2024 | 27M/93M | Transformer + 扩散头 | 首个全开源跨体态机器人策略；训练于 OXE 800k 轨迹；可在消费级 GPU 几小时微调 | [arXiv:2405.12213](https://arxiv.org/abs/2405.12213) |
| **OpenVLA** | Stanford等 | 2024 | 7B | 自回归（Llama2+DINOv2+SigLIP） | 开源 7B VLA；29 任务上以 7B 参数超越 RT-2-X (55B) 16.5%；支持 LoRA 微调 | [arXiv:2406.09246](https://arxiv.org/abs/2406.09246) |
| **RDT-1B** | 清华大学 | 2024 | 1.2B | 扩散 Transformer | 最大规模扩散基础模型（双臂操作）；统一动作空间；46 数据集 100 万+轨迹预训练；1-5 样本 zero-shot 泛化 | [arXiv:2410.07864](https://arxiv.org/abs/2410.07864) |
| **π0（Pi Zero）** | Physical Intelligence | 2024 | ~3B | 流匹配（PaliGemma骨干） | 首个流匹配 VLA；跨多种机器人平台（单臂/双臂/移动）；展示叠衣、装箱等复杂技能；RSS 2025 发表 | [arXiv:2410.24164](https://arxiv.org/abs/2410.24164) |
| **Diffusion Policy** | Columbia | 2023 | 中小型 | 扩散（DDPM/DDIM） | 奠基性扩散策略工作；非 VLA 但为后续扩散 VLA 铺路 | [arXiv:2303.04137](https://arxiv.org/abs/2303.04137) |

#### 2025 年关键模型

| 模型 | 机构 | 时间 | 架构范式 | 核心贡献 |
|------|------|------|----------|---------|
| **GR00T N1** | NVIDIA | 2025-03 | 双系统（VLM S2 + 扩散 Transformer S1） | 首个开源人形机器人基础模型；S2@10Hz 推理 + S1@120Hz 动作；真实+人类视频+合成数据混合训练 |
| **π0.5** | Physical Intelligence | 2025-04 | 流匹配（扩展 π0） | 开放世界泛化：在**全新家庭环境**完成厨房/卧室清洁长时域任务；多机器人+语义子任务联合训练 |
| **OpenVLA-OFT** | Stanford等 | 2025-02 | 自回归（优化微调配方） | LIBERO 上平均成功率从 76.5% 升至 97.1%；推理速度提升 26x；并行解码+动作分块+连续表示 |
| **FAST / π0-FAST** | Physical Intelligence | 2025-01 | 自回归（DCT token化） | 频域动作 token 化；基于 FAST 的自回归 VLA 在 10k 小时数据上训练，匹配扩散 VLA 性能，训练时间减少 5x |
| **HybridVLA** | 北京大学 | 2025-03 | 混合（AR+扩散共享 LLM） | 单 LLM 内协同自回归推理链 + 扩散动作生成；仿真和真实任务上超前 SOTA 14%/19% |
| **GR00T N1.5** | NVIDIA | 2025-05（[未证实]具体月份） | 双系统（改进版） | 用 GR00T-Dreams 合成数据在 36 小时内完成训练（手工收集需~3个月）；更好环境/工作空间适应性 |
| **GR00T N1.7** | NVIDIA | 2026-04（Early Access） | 双系统（新 VLM 骨干） | 新 VLM 骨干；引入 20k 小时 EgoScale 人类视频预训练；泛化性和语言跟随能力改善 |
| **SpatialVLA** | 多机构 | 2025-01 | 自回归（Ego3D 位置编码） | 空间感知 VLA；Ego3D 位置编码提升空间理解和精细操作 |
| **GraspVLA** | Galbot/北大等 | 2025-05 | 流匹配+自回归（CoT） | 10 亿帧合成数据预训练；直接 sim-to-real 零样本迁移；多类别 ~90% 成功率 |
| **AgiBot GO-1（ViLLA）** | 智元机器人 | 2025-03 | ViLLA（VLM+MoE 专家） | 新框架：Latent Planner（跨体态通用动作理解）+ Action Expert（高频精细操作） |
| **DiffusionVLA** | 多机构 | 2024-12/2025 | 混合（AR 推理+扩散动作） | AR 任务分解引导扩散动作预测；2B→72B 体现泛化缩放 |
| **UniVLA** | 多机构 | 2025 | 全自回归（编码器自由，DCT离散化） | 所有模态统一离散 token；World Modeling 后训练增强因果动态理解 |
| **VLA-RL** | 多机构 | 2025-05 | 自回归+在线 RL 后训练 | 在线 RL 提升 OOD 泛化；OpenVLA-7B 在 LIBERO 40 任务超越强微调基线 4.5%，逼近 π0-FAST |

#### GR00T N2（预告）

NVIDIA CEO 黄仁勋预告 GR00T N2，基于 DreamZero 研究，采用「World Action Model」架构，[未证实]声称比现有 VLA 模型成功率高 2x 以上，计划 2026 年内发布。目前在 MolmoSpaces 和 RoboArena 排名第一（[未证实]来源：NVIDIA 官方新闻稿，未经独立验证）。

---

## 3. 关键玩家

### 3.1 国际实验室与公司

| 机构 | 代表工作 | 定位与策略 |
|------|---------|-----------|
| **Physical Intelligence (π.ai)** | π0, π0.5, FAST | 全栈 VLA 研究+部署；开源 openpi 推理框架；专注泛化操作 |
| **Google DeepMind** | RT-2, RT-X, AutoRT, SARA-RT | 大规模数据（OXE 贡献者），探索从 VLM 到 VLA 的迁移学习路线 |
| **NVIDIA** | GR00T N1/N1.5/N1.7/N2, Isaac Sim | 开源策略+闭源数据+模拟平台全栈；合成数据大规模生成（Cosmos WFM）；硬件生态驱动 |
| **Figure AI** | Helix (System 1+2) | 闭源双系统 VLA；~500 小时高质量人类示教数据；专注人形机器人全身控制 |
| **UC Berkeley（Levine组等）** | Octo, OpenVLA, HybridVLA 合作 | 开源生态建设；跨体态训练；标准化评测 |
| **Stanford IPRL** | OpenVLA, OpenVLA-OFT, MiniVLA | 开源方向、微调效率优化 |
| **Hugging Face / LeRobot** | SmolVLA, LeRobot 框架, X-VLA | 民主化工具链；LeRobotDataset v3 标准数据格式；社区数据收集 |
| **清华大学（ml group）** | RDT-1B | 扩散基础模型；双臂操作领域 SOTA |

### 3.2 中国团队

| 机构 | 代表工作 | 现状 |
|------|---------|------|
| **智元机器人（AgiBot）** | GO-1（ViLLA 框架） | 2025-03 发布；ViLLA = VLM + MoE 专家系统；已有量产计划；2025 年多篇顶会（含 NeurIPS 6 篇）[未证实数字] |
| **银河通用（Galbot）** | GraspVLA（arXiv:2505.03233） | 与北京大学合作；10 亿帧合成数据；CoRL 2025 接收；考虑 IPO |
| **星海图（Galaxea AI）** | G0 模型（2025-08），G0 Plus（2026-01）；支持蚂蚁开源 LingBot-VLA | 2026-02 融资 1 亿美元+；R1 Pro 机器人；演示布料折叠/装配等 |
| **北京大学 EPIC 组** | GraspVLA（合作），具身操作研究 | 产学结合；与 Galbot 深度合作 |
| **知乎/国内学术整理** | 2025-2026 VLA 论文整理（知乎专栏）| 中文社区综述，非一手来源 |

**背景**：2026 年 2 月中国发布首个人形机器人与具身智能国家标准体系；"十五五"规划（2026-2030）将具身智能列为核心增长引擎。腾讯投资智元/宇树，阿里投资源码资本机器人方向，蚂蚁参与星海图多轮融资。

---

## 4. 数据集与 Benchmark

### 4.1 主要训练数据集

| 数据集 | 规模 | 说明 |
|--------|------|------|
| **Open X-Embodiment (OXE)** | ~100 万轨迹，22 种机器人，22 机构联合 | 当前最大开源真实机器人数据；OXE v2 持续更新 |
| **DROID** | ~76k 轨迹，7 DoF Franka | 多样场景单臂操作 |
| **Bridge Data V2** | ~60k 轨迹 | WidowX 机器人家庭操作 |
| **SynGrasp-1B（GraspVLA）** | 10 亿帧 | 光照真实渲染 + 大量域随机化；合成数据 |
| **LeRobot Community Datasets** | 持续增长 | HuggingFace Hub 标准化格式；v3.0 支持流式加载 |
| **NVIDIA Omniverse 合成数据** | [未证实规模] | 用于 GR00T N1.5 训练；Cosmos WFM 生成 |
| **EgoScale** | 2 万小时人类视频 | 用于 GR00T N1.7 预训练；[未证实]独立验证 |

### 4.2 主要 Benchmark 评测套件

| Benchmark | 类型 | 说明 |
|-----------|------|------|
| **LIBERO** | 仿真（4 个任务套件，130+ 任务） | 当前最广泛引用的 VLA 仿真评测标准；LIBERO-PRO 版本（2025）针对"记忆化"问题改进 |
| **Open X-Embodiment（评测集）** | 真实机器人 | 多体态迁移评测 |
| **SIMPLER** | 仿真（MuJoCo）| 真实机器人任务的仿真镜像，用于快速迭代 |
| **VLABench（OpenMOSS）** | 仿真+多维度 | 多维度泛化评测（语言、视觉、物体类别）；2025 |
| **RoboArena** | 社区排行榜 | [未证实] GR00T N2 声称榜首；独立核实困难 |
| **MolmoSpaces** | 社区排行榜 | [未证实] 同上 |
| **LIBERO-PRO** | 仿真（改进版） | 2025-10 arXiv:2510.03827；针对 VLA 记忆化评测盲区 |

**评测重要注意**：各论文自选评测集，跨论文数字对比意义有限。标准化的盲测或竞赛式评测（类似 LLM leaderboard）在机器人领域仍付之阙如。

---

## 5. 近 6-12 个月的趋势与突破（2025 年初 至 2026 年 6 月）

### 5.1 已确立的变化

**① 流匹配成为主流替代**

π0（2024-10）确立流匹配作为扩散的竞争者：精度接近、速度更快、更易跨体态扩展。2025 年多个工作跟进采用或对比流匹配。

**② 合成数据规模化成为关键杠杆**

NVIDIA 用 Cosmos 世界模型合成数据将 GR00T N1.5 的"三个月数据收集"压缩到 36 小时。GraspVLA 用 10 亿帧合成数据做预训练，实现直接 sim-to-real 零样本迁移。合成数据从"辅助"变为"主要数据来源"是 2025 年最重要的结构性转变之一。

**③ 双系统架构广泛采用**

GR00T N1（NVIDIA）和 Helix（Figure AI）均采用"慢 VLM 推理 + 快扩散/策略执行"的双系统设计，这一架构在 2025 年形成行业共识，解决了单一 VLA 推理速度与精度的矛盾。

**④ 在线 RL 后训练开始兴起**

2025 年下半年涌现多篇 RL post-training 工作（VLA-RL, SimpleVLA-RL, RobustVLA），弥补模仿学习在 OOD 场景的不足。π0-FAST 在 RL 训练后性能提升显著。这是 LLM 后训练路线（RLHF/GRPO）向机器人领域迁移的信号。

**⑤ 效率与轻量化并行发展**

TinyVLA、SmolVLA（SmolLM 骨干，<1B）、EfficientVLA（训练无关加速，1.93x）等工作针对实际部署的延迟和成本约束。

**⑥ 中国团队加速追赶并开始输出原创架构**

ViLLA（AgiBot）、GraspVLA（Galbot/北大）已在国际会议发表，而非仅工程复现。国家政策+大额融资+制造业数据优势形成独特赛道，但具体技术细节独立核实程度仍低。

**⑦ 世界模型与 VLA 融合加速**

2025 年下半年出现明确的 VLA+WM 联合训练工作（VLAW, GigaBrain-0, DreamVLA），预示两个子领域正在走向合并。

### 5.2 尚在争议的问题（有迹象但未确立）

- **VLA 的缩放律（Scaling Law）**：DiffusionVLA 2B→72B 显示泛化改善，但尚无系统性缩放曲线；证据为单点，不足以确立结论
- **真实世界中 VLA 的可靠性**：Penn PAL Lab 对 π0 的"野外测试"（Pi0-Experiment-in-the-Wild）显示真实家庭部署成功率明显低于实验室；"开放世界泛化"仍是挑战
- **推理时缩放（Test-time Scaling）**：有早期信号，但缺少严格验证

---

## 6. 开放问题 / 下一步方向

1. **评测标准化缺失**：无法客观比较不同论文成功率；需要类似 GLUE/SuperGLUE 的盲测基准
2. **真实部署可靠性**：实验室数字到生产部署之间的巨大差距尚未解决；鲁棒性（遮挡、光照变化、人为干扰）仍是关键瓶颈
3. **Sim-to-Real Gap**：即使大量合成数据，精细操作（小物体抓取、柔性物体）的迁移失败率仍高
4. **长时域任务规划**：π0.5 展示了厨房清洁等长任务的可能性，但稳定性和成功率仍低
5. **双手/全身协调**：人形机器人全身协调（双臂+移动底盘+手部末端）数据稀缺，建模困难
6. **数据效率**：大多数 SOTA 系统仍需数百到数千小时示教；少样本/零样本泛化能力有限
7. **安全性与失效模式**：VLA 失败往往难以预测；安全约束集成机制几乎空白
8. **跨体态泛化（Cross-Embodiment）**：动作空间异质性（joint/ee/delta）问题部分解决，但大规模跨体态零样本迁移仍是开放问题
9. **在线学习/持续学习**：绝大多数工作是离线训练；机器人部署后持续改进机制未成熟

---

## 关键论文（结构化）

按重要性大致排序，兼顾奠基性和时效性：

- 2307.15818 | RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic Control | 2023 | 首个大规模 VLA：将动作表示为语言 token 联合 VLM 训练，展示 emergent 泛化，奠定 VLA 研究范式
- 2410.24164 | π0: A Vision-Language-Action Flow Model for General Robot Control | 2024 | 首个流匹配 VLA；跨多机器人平台预训练；叠衣/装箱等复杂技能；RSS 2025 发表
- 2406.09246 | OpenVLA: An Open-Source Vision-Language-Action Model | 2024 | 开源 7B VLA；以更少参数超越 RT-2-X；推动社区开源生态
- 2405.12213 | Octo: An Open-Source Generalist Robot Policy | 2024 | 首个全开源跨体态策略；OXE 800k 轨迹预训练；9 机器人平台微调验证
- 2410.07864 | RDT-1B: a Diffusion Foundation Model for Bimanual Manipulation | 2024 | 最大规模扩散基础模型（1.2B）；统一动作空间；双臂 zero-shot 泛化；ICLR 2025 发表
- 2503.14734 | GR00T N1: An Open Foundation Model for Generalist Humanoid Robots | 2025 | NVIDIA 首个开源人形机器人基础模型；双系统架构；真实+人类视频+合成数据混合训练
- 2504.16054 | π0.5: a Vision-Language-Action Model with Open-World Generalization | 2025 | 首个在全新家庭环境完成厨房/卧室清洁等长时域任务的端到端 VLA
- 2501.09747 | FAST: Efficient Action Tokenization for Vision-Language-Action Models | 2025 | 频域 DCT 动作 token 化；使自回归 VLA 可扩展到高频精细操作，训练速度 5x 提升
- 2502.19645 | Fine-Tuning Vision-Language-Action Models: Optimizing Speed and Success (OpenVLA-OFT) | 2025 | 优化微调配方：推理速度 26x、LIBERO 成功率 76.5%→97.1%
- 2503.10631 | HybridVLA: Collaborative Diffusion and Autoregression in a Unified VLA | 2025 | 单 LLM 内协同自回归推理+扩散动作；仿真/真实任务超前 SOTA 14%/19%
- 2505.03233 | GraspVLA: a Grasping Foundation Model Pre-trained on Billion-scale Synthetic Action Data | 2025 | 10 亿帧合成数据预训练；直接 sim-to-real 零样本迁移；CoRL 2025 接收
- 2505.18719 | VLA-RL: Towards Masterful and General Robotic Manipulation with Scalable Reinforcement Learning | 2025 | 在线 RL 后训练提升 OOD 泛化；OpenVLA-7B 在 40 任务超最强微调基线 4.5%
- 2501.15830 | SpatialVLA: Exploring Spatial Representations for Visual-Language-Action Model | 2025 | Ego3D 位置编码增强空间理解，改善精细操作和复杂布局任务
- 2303.04137 | Diffusion Policy: Visuomotor Policy Learning via Action Diffusion | 2023 | 奠基性扩散策略；非 VLA 但为后续扩散 VLA 提供核心方法论（Chi et al., RSS 2023）
- 2412.03293 | Diffusion-VLA: Generalizable and Interpretable Robot Foundation Model via Self-Generated Reasoning | 2024 | AR 推理链引导扩散动作；2B→72B 展示泛化缩放趋势
- 2509.19012 | Pure Vision Language Action (VLA) Models: A Comprehensive Survey | 2025 | 系统综述：分类自回归/扩散/RL/混合/专用五类 VLA 范式
- 2510.07077 | Vision-Language-Action Models for Robotics: A Review Towards Real-World Applications | 2025 | 面向真实应用的 VLA 综述；覆盖 100+ 架构的统一分类体系
- 2505.04769 | Vision-Language-Action Models: Concepts, Progress, Applications and Challenges | 2025 | VLA 概念/进展/应用/挑战综述；列出 10 大开放挑战
- 2511.05936 | 10 Open Challenges Steering the Future of Vision-Language-Action Models | 2025 | 系统梳理 VLA 领域十大开放挑战
- 2602.12063 | VLAW: Iterative Co-Improvement of Vision-Language-Action Policy and World Model | 2026 | VLA 与 World Model 联合迭代训练；合成数据大规模扩展
