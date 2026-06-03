---
domain: bci
date: 2026-06-03
confidence: medium-high
last_updated_by: claude-sonnet-4-6
note: >
  BCI 顶尖成果多发表于 Nature/Science 系列期刊，而非 arXiv。
  arXiv_id 仅在确认有预印本时标注；期刊来源优先标期刊。
  "未证实"标注表示信息来自二手报道，原始论文尚未逐一核对。
---

# 脑机接口 (BCI) 领域现状基线

> 调研截止：2026-06-03 | 覆盖 2024–2026 最新进展

---

## 细分分支地图

### 1. 按信号采集方式分

#### 1.1 侵入式 BCI (Invasive BCI)
- **Utah Array / 微电极阵列** — 最成熟的侵入式方案，100 电极/阵列，Blackrock Neurotech NeuroPort 系列；已积累 40+ 例人体植入，信号质量最高，但长期面临胶质疤痕导致信号衰减（一年内 60%+ 电极失效，未证实统一数字）
- **ECoG（皮层脑电）** — 硬膜下高密度电极阵列，UCSF Chang Lab 的语音解码核心技术；空间分辨率优于 EEG，创伤小于 Utah Array
- **柔性电极 / 高密度阵列** — 下一代方向；脑虎科技 NeuroXess 256 导柔性阵列（2024 年植入成功）、Precision Neuroscience Layer 7 皮层刺激器（薄膜式，微创），Axoft Fleuron 超柔材料（比聚酰亚胺软 10,000 倍，未证实具体数字）
- **Neuralink N1** — 64 线程 × 1024+ 电极，机器人自动植入，已完成 7 例人体植入（截至 2025 年底，4 名脊髓损伤 + 3 名 ALS）
- **Stentrode（血管内电极）** — Synchron 公司，经颈静脉置入运动皮层旁血管，无需开颅，2024 年 COMMAND 研究 6 例患者达到主要终点（无严重不良事件）
- **Paradromics Connexus** — 高通量侵入式，最多 1,684 个皮层电极（4 枚模块），200 bps 比特率，2025 年 11 月获 FDA IDE 批准用于语音恢复临床试验

#### 1.2 非侵入式 BCI (Non-invasive BCI)
- **EEG（脑电图）** — 最普及，毫秒级时间分辨率，空间分辨率差；主要范式：运动想象(Motor Imagery)、SSVEP(稳态视觉诱发电位)、P300；被 MOABB 标准化评测
- **fNIRS（功能性近红外光谱）** — 穿戴友好，测量血氧变化，时间分辨率（秒级）低于 EEG，适合长期监测
- **MEG（脑磁图）** — 与 EEG 互补，空间分辨率更好，设备昂贵（传统 SQUID）；OPM（光泵磁力计）MEG 正在小型化，可在自由运动时录制
- **fMRI** — 主要用于研究/视觉解码（MinD-Vis、MindEye 系列），无法实时 BCI

### 2. 按应用目标分

#### 2.1 神经解码 (Neural Decoding)

**运动解码 (Motor Decoding)**
- 手写解码：BrainGate/Stanford — 2021 年 Nature 里程碑（90+ CPM，94.1% 在线准确率）；2026 年有跨用户迁移预印本
- 光标/游标控制：Neuralink PRIME 研究首例患者完成鼠标控制、视频游戏、CAD 建模
- 手指/抓握解码：博睿康 NEO 系统（脊髓损伤患者恢复抓握，已入国家创新医疗器械审查程序）
- 运动基础模型：NDT3（Neural Data Transformer 3），350M 参数 Transformer，在 30+ 猴和人 × 2000 小时数据上预训练，NeurIPS 2024

**语音 / 言语解码 (Speech Decoding)**
- 2023 年 Nature 里程碑：UCSF Chang Lab — 高密度 ECoG 实时解码语音/面部运动 + 化身控制
- 2024 年 Nature Biomedical Engineering：UCSF — 双语（英语/西班牙语）语音解码器
- 2025 年 3 月：UC Berkeley + UCSF — 自然语音合成（带语调/节奏），近实时延迟（Nature Neuroscience）
- 2025 年 6 月：UC Davis — ALS 患者真实语音合成，直接输出音频而非文字（ScienceDaily 报道）
- 脑虎科技 NeuroXess：2024 年 12 月全球首家同时实现实时运动解码 + 普通话语音解码（256 导柔性 ECoG）

**视觉解码 (Visual Decoding)**
- MinD-Vis：fMRI → 图像重建，稀疏脑掩码建模 + 双条件扩散模型
- MindEye / MindEye2（arXiv: 2305.18274 / 2403.11207）：对比学习 + 扩散先验，MindEye2 仅需 1 小时 fMRI 数据
- EEG 视觉解码：ATM 编码器 → CLIP 嵌入 → 扩散模型生成（arXiv: 2403.07721）
- 2025 年 npj Biomedical Innovations：脑机共生绘图，视觉 BCI 辅助艺术创作

#### 2.2 神经假肢 / 运动恢复 (Neuroprosthetics & Motor Rehabilitation)
- **仿生腿步态恢复**：2024 年 Nature Medicine — 持续神经控制仿生腿，截肢患者恢复自然步态（跨越坡面/楼梯）
- **脑脊接口恢复行走**：2023 年 Nature — Courtine/Bloch 团队（EPFL），ECoG 脑信号 + 脊髓硬膜外刺激，慢性脊髓损伤患者（Gert-Jan Oskam）恢复自然行走，12 个月稳定
- **双向 BCI / 感觉反馈**：2024–2025 Nature Biomedical Engineering — 仿生手感知形状和运动，UChicago Medicine 精调 BCI 让假肢更真实
- **外骨骼 BCI 控制**：EEG/ECoG 驱动下肢外骨骼，2024 年临床试验不完全脊髓损伤患者成功（65–75% 成功率，未证实统一数字）

#### 2.3 双向 BCI / 神经刺激反馈
- 感觉反馈闭环：皮质内微刺激（ICMS）恢复触觉感知，与运动解码结合构成真正双向回路
- 神经调控：经颅磁刺激（TMS）+ EEG、深脑刺激（DBS）闭环控制（帕金森、癫痫）
- 脑机协同演进框架：脑虎科技提出双环路（运动+认知）协同设计（未证实）

#### 2.4 BCI × 具身智能 / 机器人交叉（重点）
- **Neuralink CONVOY 研究**（2024 年 11 月启动）：N1 脑植入控制辅助机械臂，患者已完成写字演示（"convoy"），目标：喂食、物品抓放等日常生活自主操作
- **AI 副驾驶 / 共享自主**：Nature Machine Intelligence 2025 — 非侵入式 EEG BCI + AI 协同控制，目标命中率提升 3.9 倍，机械臂完成随机块摆放任务
- **多机器人多用户协作**：2026 年新工作，EEG + EMG + 眼动整合 BRI，厨房环境移动操作机器人，三级自主（辅助遥操 / 共享自主 / 全自动）
- **脑控机器人文献综述**：Mind Meets Robots（2025 年 Human-Computer Interaction 期刊），全面梳理 EEG 脑-机器人交互系统

#### 2.5 AI / 基础模型在神经解码中的应用
- **NDT3**（Neural Data Transformer 3）：350M Transformer，多任务运动解码基础模型，胜过专项单任务模型，NeurIPS 2024；代码：`joel99/ndt3`（HuggingFace）
- **CBraMod**（2024, arXiv: 2412.07236）：十字交叉脑基础模型，EEG 解码
- **NeurIPT**（ICLR 2025）：多任务 EEG 神经接口基础模型，捕获同质/异质时空特征
- **Brain-JEPA**（2025）：梯度定位 + 时空掩码，脑动力学基础模型
- **RPNT**（arXiv: 2601.17641）：鲁棒预训练神经 Transformer，广义运动解码
- **Chiral**（Synchron × Nvidia，GTC 2025）：人类认知 AI 基础模型，配合 Stentrode + Apple Vision Pro 演示
- **EEG Transformer 综述**（GWU, 2025）：基于 Transformer 和混合深度学习的 EEG 解码全面综述
- 核心挑战：受试者间/任务间/条件间巨大变异，电极配置不统一，限制跨数据集泛化

---

## 关键论文（结构化）

### 里程碑论文

| # | 标题 | 来源 | arXiv_id | 年份 | 一句话贡献 |
|---|------|------|-----------|------|------------|
| 1 | High-performance brain-to-text communication via handwriting | Nature, Stanford/BrainGate | — | 2021 | 运动皮层解码手写意图，90+ CPM，94.1% 在线准确率，首个高速文字 BCI |
| 2 | A high-performance neuroprosthesis for speech decoding and avatar control | Nature, UCSF Chang Lab | — | 2023 | ECoG 实时解码语音 + 面部动画化身，言语恢复里程碑 |
| 3 | Online speech synthesis using a chronically implanted BCI in an individual with ALS | (PMC 11053081) | — | 2024 | ALS 患者长期植入 BCI，实时语音合成，首次大词汇量低错误率演示 |
| 4 | Walking naturally after spinal cord injury using a brain–spine interface | Nature, EPFL/Courtine/Bloch | — | 2023 | 脑脊数字桥接，慢性脊髓损伤患者恢复自然行走，12 个月稳定 |
| 5 | Continuous neural control of a bionic limb restores biomimetic gait after amputation | Nature Medicine | — | 2024 | 持续神经控制仿生腿，截肢患者恢复跨坡/楼梯自然步态 |
| 6 | Brain-to-voice neuroprosthesis restores naturalistic speech | Nature Neuroscience, UC Berkeley/UCSF | — | 2025 | 近实时语音合成（含语调节奏），ALS 患者恢复自然对话 |
| 7 | Bilingual speech decoder for paralysis | Nature Biomedical Engineering, UCSF | — | 2024 | 双语（英/西班牙语）语音解码器，首例双语言 BCI |

### 基础模型 / AI 神经解码

| # | 标题 | 来源 | arXiv_id | 年份 | 一句话贡献 |
|---|------|------|-----------|------|------------|
| 8 | Neural Data Transformer 3 (NDT3) | NeurIPS 2024 / bioRxiv | 2025.02.02.634313 | 2024 | 350M Transformer，30+ 受试者 2000 小时预训练，广义运动解码基础模型 |
| 9 | CBraMod: A Criss-Cross Brain Foundation Model for EEG Decoding | arXiv | 2412.07236 | 2024 | 十字交叉注意力 EEG 基础模型，跨任务 EEG 解码 |
| 10 | MindEye2: Shared-Subject Models Enable fMRI-To-Image With 1 Hour of Data | arXiv | 2403.11207 | 2024 | 跨受试者共享模型，仅需 1 小时 fMRI 即可准确重建视觉图像 |
| 11 | Brain Foundation Models: A Survey on Advancements in Neural Signal Processing | arXiv | 2503.00580 | 2025 | 脑基础模型综合综述，梳理挑战与方向 |

### BCI × 具身 / 机器人

| # | 标题 | 来源 | arXiv_id | 年份 | 一句话贡献 |
|---|------|------|-----------|------|------------|
| 12 | Brain-computer interface control with artificial intelligence copilots | Nature Machine Intelligence | — | 2025 | 非侵入式 EEG + AI 共享自主，任务命中率提升 3.9 倍，机械臂操作演示 |
| 13 | Levels of shared autonomy in brain-robot interfaces: enabling multi-robot multi-human collaboration | PMC 12852366 | — | 2026 | EEG+EMG+眼动三模态 BRI，三级自主厨房机器人协作 |
| 14 | Neuralink CONVOY Study Launch | Neuralink 官方 | — | 2024 | N1 脑植入控制辅助机械臂可行性试验，物理自主里程碑 |

### 非侵入式 / EEG / 视觉解码

| # | 标题 | 来源 | arXiv_id | 年份 | 一句话贡献 |
|---|------|------|-----------|------|------------|
| 15 | The largest EEG-based BCI reproducibility study for open science: MOABB | arXiv | 2404.15319 | 2024 | 36 数据集 × 30 机器学习流程系统评测，BCI 开放科学基准 |
| 16 | Visual Decoding and Reconstruction via EEG Embeddings with Guided Diffusion | arXiv | 2403.07721 | 2024 | EEG → CLIP → 扩散模型，零样本视觉图像重建 |
| 17 | Improving motor imagery decoding for EEG-based BCI (2024 Cybathlon) | arXiv | 2511.23384 | 2024 | S4D 层 EEG 运动想象解码，84% 离线准确率 |

### 数据集 / 硬件

| # | 标题 | 来源 | arXiv_id | 年份 | 一句话贡献 |
|---|------|------|-----------|------|------------|
| 18 | FALCON Benchmark: Few-shot Algorithms for Consistent Neural Decoding | bioRxiv / NeurIPS 2024 | 2409.15613126（bioRxiv） | 2024 | 少样本鲁棒长期神经解码标准评测，含人体 iBCI handwriting 数据集 |
| 19 | A multi-day and high-quality EEG dataset for motor imagery BCI | Scientific Data (Nature) | — | 2025 | 高质量多日运动想象 EEG 数据集，促进跨会话泛化研究 |

---

## 关键玩家

### 公司（侵入式 / 临床级）

| 公司 | 国家 | 技术路线 | 2024–2025 关键里程碑 |
|------|------|----------|----------------------|
| **Neuralink** | 美国 | 全植入式，64 线程 1024+ 电极，机器人植入 | 截至 2025 年底 7 例人体植入；CONVOY 研究（脑控机械臂）；Blindsight 视觉假体进入人体试验 |
| **Synchron** | 美国 | Stentrode 血管内电极，无需开颅 | COMMAND 研究 6 例达主要终点（2024）；$200M 系列 D（2025 年 11 月）；Chiral AI 基础模型（与 Nvidia 合作） |
| **Precision Neuroscience** | 美国 | Layer 7 薄膜皮层电极，微创 | 2024–2025 扩大临床合作 |
| **Paradromics** | 美国 | Connexus，1,684 电极，高通量语音恢复 | 2024 获两项 FDA Breakthrough；2025 年 11 月获 IDE 批准语音恢复试验，全球首家 |
| **Blackrock Neurotech** | 美国 | NeuroPort Utah Array，研究级+临床级 | 全球最多人体植入（40/50 BCI 植入用户）；MoveAgain 获 FDA Breakthrough |
| **脑虎科技 / NeuroXess** | 中国 | 256 导柔性 ECoG，半植入 | 2024 年植入 21 岁患者；全球首例实时普通话语音解码 + 运动解码同步（2024 年 12 月） |
| **博睿康** | 中国 | NEO 侵入式系统，神经假肢 | 进入国家创新医疗器械特别审查；华山医院首例植入，脊髓损伤患者恢复抓握 |
| **强脑科技 (BrainCo)** | 中美 | 非侵入 EEG + 智能假肢 | 估值超 10 亿美元（2022 D 轮），2025 年 2 月累计融资约 3 亿美元 |
| **阶梯医疗** | 中国 | 侵入式 BCI，康复 | 2025 年最具潜力企业（前瞻产业研究院），单笔融资 3.5 亿元人民币 |

### 公司（非侵入 / 消费级）

| 公司 | 特点 |
|------|------|
| **OpenBCI** | 开源 EEG 硬件平台，研究与创客生态 |
| **Emotiv** | 商用 EEG 头显，心理状态监测 |
| **Muse (InteraXon)** | 消费级 EEG，冥想/神经反馈 |
| **NextMind（已被 Snap 收购）** | 视觉 BCI，SSVEP |

### 顶尖实验室

| 实验室 | 机构 | 方向 | 代表人物 |
|--------|------|------|----------|
| **Chang Lab** | UCSF | 语音解码 ECoG 神经假肢 | Edward Chang |
| **BrainGate 联盟** | Stanford/Brown/Harvard/Case Western | 侵入式 BCI 临床研究，手写/语音/运动解码 | Jaimie Henderson, John Donoghue（创始）, Francis Willett |
| **Henderson Lab** | Stanford | 手写解码，跨用户迁移学习 | Jaimie Henderson, Frank Willett |
| **NeuroRestore** | EPFL | 脑脊接口，行走恢复 | Grégoire Courtine, Jocelyne Bloch |
| **Shenoy Lab** | Stanford | 运动皮层解码，神经流形 | Krishna Shenoy |
| **Gallego Lab** | Imperial College London | 神经流形，低维解码 | Juan Gallego |
| **Kamitani Lab** | 京都大学 / ATR | fMRI 视觉解码 | Yukiyasu Kamitani |
| **Hirata Lab** | 大阪大学 | 超薄皮层电极，创办 JiMED | Masayuki Hirata |
| **脑虎科技背后研究团队** | 复旦/华山医院 | 柔性 ECoG 临床 | （联合团队） |

---

## 数据集 / Benchmark / 开源工具

### 数据集与 Benchmark

| 名称 | 类型 | 说明 |
|------|------|------|
| **Neural Latents Benchmark (NLB)** | 侵入式，运动/认知 | 标准化运动皮层潜变量评测，多数据集统一框架 |
| **FALCON** | 侵入式，BCI 解码 | 少样本鲁棒长期神经解码，含人体 handwriting iBCI（H2 数据集），NeurIPS 2024 |
| **MOABB** | EEG | 最大开放 EEG-BCI 可重复性评测，36 数据集（运动想象×14 / P300×15 / SSVEP×7）× 30 流程（arXiv: 2404.15319） |
| **BCI Competition IV (BNCI2014-001)** | EEG，运动想象 | 22 导 EEG，9 受试者，社区标准评测集 |
| **NSD (Natural Scenes Dataset)** | fMRI，视觉 | 视觉解码/图像重建基准，MindEye 系列核心 |
| **Multi-day Motor Imagery EEG (2025)** | EEG，运动想象 | Scientific Data 2025，促进跨会话泛化 |
| **NeuralBench** | 多模态 NeuroAI | 统一 NeuroAI 模型评测框架（arXiv: 2605.08495）|

### 开源工具

| 工具 | 语言 | 用途 |
|------|------|------|
| **MNE-Python** | Python | EEG/MEG/fNIRS/ECoG 分析与可视化，学术标准 |
| **BrainFlow** | C++/Python（多语言绑定） | 统一多设备神经信号采集 API，实时处理优化 |
| **OpenBCI GUI** | Java | 开源 EEG 硬件控制+可视化 |
| **NDT3** | PyTorch | 运动解码 Transformer 基础模型（`joel99/ndt3`，HuggingFace） |
| **awesome-neurofm** | 列表 | 神经基础模型资源索引（GitHub: mazabou/awesome-neurofm） |
| **NeuroTechX awesome-bci** | 列表 | BCI 综合资源清单（GitHub: NeuroTechX/awesome-bci） |

---

## 近 1-2 年趋势（2024–2026）

1. **基础模型涌入神经解码**：NDT3、CBraMod、NeurIPT、Brain-JEPA 密集出现，从"一人一模型"向"预训练 + 少样本适配"迁移，是 BCI 领域的 GPT 时刻前夜
2. **语音 BCI 进入实用门槛**：UCSF/UC Davis 2024–2025 实现接近自然的语音合成，错误率下降，延迟缩短；Paradromics 获 FDA 批准语音 BCI 临床试验
3. **通道数快速攀升**：从 Utah Array 的 100 通道 → Neuralink 1024+ 通道 → Paradromics 1684 通道 → NeuroXess 256 导柔性（皮层表面）；通道数 × 信号质量 × 长期稳定性的三角矛盾仍是核心挑战
4. **中国快速追赶**：NeuroXess 成为全球首家同时实现普通话语音 + 运动实时解码的公司，中国 BCI 植入人数突破 50 例（2025 年初报道）
5. **BCI × 机器人正式启动**：Neuralink CONVOY（脑控机械臂）标志该方向从理论进入人体试验；Nature Machine Intelligence 2025 AI 副驾驶论文将共享自主推进到非侵入式可用状态
6. **商业化加速**：Synchron $200M D 轮（2025 年 11 月），BCI 行业 2024–2025 年总投资超过 10 亿美元（未证实精确数字）；Synchron Stentrode 入选 TIME 2025 年度最佳发明
7. **长期稳定性获突破性进展**：BrainGate2 ALS 患者 2 年无需每日重新校准（99% 词语准确率）；脑脊接口 12 个月稳定（Courtine/Bloch）
8. **柔性材料 / 微创方向快速发展**：Axoft Fleuron、NeuroXess 柔性 ECoG、Precision Layer 7 均在 2024–2025 年取得进展，降低侵入性同时保持信号质量

---

## 开放问题

1. **长期稳定性**：胶质疤痕导致侵入式电极信号衰减，Utah Array 一年内 60%+ 通道失效；柔性材料能否在 10 年尺度维持信号质量尚无定论
2. **跨受试者泛化**：神经编码个体差异巨大，当前基础模型少样本适配仍需分钟至小时级数据；真正零样本跨人解码尚未实现
3. **实时性 vs 精度权衡**：高维解码（125,000 词汇语音）仍有 23.8% 词错误率；闭环延迟在语音合成场景对用户体验影响大
4. **双向 BCI 闭环**：感觉反馈（触觉、本体感觉）的皮质内刺激与运动解码的协同整合仍处于早期；难以同时高质量记录和刺激
5. **非侵入式信号质量瓶颈**：EEG 空间分辨率从根本上受颅骨散射限制；OPM-MEG 前景大但设备成本高，普及路径不明确
6. **AI 解码可解释性**：大型 Transformer 解码模型黑箱化，监管批准和临床信任面临挑战
7. **伦理与隐私**：神经数据是最敏感个人数据，目前缺乏专门立法；认知自由、神经主权概念尚无法律框架
8. **BCI × 机器人：控制带宽**：脑信号低带宽（典型 EEG BCI ~10–20 bps）与机器人操作任务所需高带宽的鸿沟；共享自主是当前主要解决思路，但自主度边界如何设定仍是开放问题

---

## 建议路线配置（给 config 用）

以下 4 条路线建议直接写入 `config.yaml` 的 `routes:` 段。其中 `seed.arxiv_id` 为空时表示该论文无公开 arXiv 预印本，系统以标题匹配检索。

---

### 路线 1：`bci_neural_decoding` — 神经解码核心

**覆盖**: 运动解码、语音解码、视觉解码、神经信号处理、侵入式 / ECoG 解码

```yaml
- id: bci_neural_decoding
  name: 神经解码 / BCI 核心
  domain: bci
  tier: core
  weight: 1.0
  enabled: true
  keywords:
    - neural decoding
    - brain-computer interface
    - BCI
    - brain-machine interface
    - speech decoding
    - motor decoding
    - ECoG
    - intracortical
    - spiking neural
    - neural signal
    - neuroprosthesis
    - electrocorticography
    - speech neuroprosthesis
    - neural population
    - motor cortex
    - language decoding
  seeds:
    - title: "A high-performance neuroprosthesis for speech decoding and avatar control"
      journal: "Nature 2023"
      arxiv_id: ""
    - title: "High-performance brain-to-text communication via handwriting"
      journal: "Nature 2021"
      arxiv_id: ""
    - title: "Neural Data Transformer 3: A Foundation Model for Motor Cortical Decoding"
      journal: "NeurIPS 2024 / bioRxiv"
      arxiv_id: "2025.02.02.634313"
    - title: "Online speech synthesis using a chronically implanted brain-computer interface in an individual with ALS"
      journal: "Nature Communications 2024"
      arxiv_id: ""
```

---

### 路线 2：`bci_foundation_models` — BCI 神经基础模型

**覆盖**: Transformer / foundation model 用于神经信号解码，跨受试者预训练，EEG/fMRI 大模型

```yaml
- id: bci_foundation_models
  name: 神经基础模型 / NeuroAI
  domain: bci
  tier: core
  weight: 1.0
  enabled: true
  keywords:
    - neural foundation model
    - brain foundation model
    - EEG transformer
    - neural data transformer
    - NDT
    - CBraMod
    - NeurIPT
    - cross-subject decoding
    - few-shot neural decoding
    - neural pretraining
    - brain-JEPA
    - neuro-AI
    - EEG pretrain
    - neural population dynamics
    - latent neural
  seeds:
    - title: "CBraMod: A Criss-Cross Brain Foundation Model for EEG Decoding"
      journal: "arXiv 2024"
      arxiv_id: "2412.07236"
    - title: "MindEye2: Shared-Subject Models Enable fMRI-To-Image With 1 Hour of Data"
      journal: "arXiv 2024"
      arxiv_id: "2403.11207"
    - title: "Brain Foundation Models: A Survey on Advancements in Neural Signal Processing"
      journal: "arXiv 2025"
      arxiv_id: "2503.00580"
    - title: "A Generalist Intracortical Motor Decoder"
      journal: "bioRxiv 2025"
      arxiv_id: "2025.02.02.634313"
```

---

### 路线 3：`bci_embodied_robot` — BCI × 具身智能 / 机器人交叉（重点）

**覆盖**: 脑控机器人、神经假肢、共享自主、脑脊接口行走恢复、脑控外骨骼、BCI 辅助操作
> 这是与本系统机器人主线的核心连接点。

```yaml
- id: bci_embodied_robot
  name: BCI × 具身智能 / 神经假肢
  domain: bci
  tier: core
  weight: 1.0
  enabled: true
  keywords:
    - brain-controlled robot
    - neuroprosthetic
    - neuroprosthetics
    - prosthetic control
    - exoskeleton BCI
    - shared autonomy BCI
    - brain-robot interface
    - neural control robotic arm
    - assistive robot BCI
    - brain spine interface
    - closed-loop BCI
    - rehabilitation robot BCI
    - BCI manipulation
    - walking restoration BCI
    - bionic limb neural
    - CONVOY Neuralink
    - AI copilot BCI
  seeds:
    - title: "Brain-computer interface control with artificial intelligence copilots"
      journal: "Nature Machine Intelligence 2025"
      arxiv_id: ""
    - title: "Walking naturally after spinal cord injury using a brain-spine interface"
      journal: "Nature 2023"
      arxiv_id: ""
    - title: "Continuous neural control of a bionic limb restores biomimetic gait after amputation"
      journal: "Nature Medicine 2024"
      arxiv_id: ""
    - title: "Levels of shared autonomy in brain-robot interfaces: enabling multi-robot multi-human collaboration"
      journal: "Frontiers 2026"
      arxiv_id: ""
```

---

### 路线 4：`bci_noninvasive_eeg` — 非侵入式 BCI / EEG 解码

**覆盖**: 运动想象 EEG、SSVEP、P300、EEG 基准、穿戴式 BCI、消费级应用

```yaml
- id: bci_noninvasive_eeg
  name: 非侵入式 BCI / EEG 解码
  domain: bci
  tier: secondary
  weight: 0.7
  enabled: true
  keywords:
    - EEG BCI
    - motor imagery EEG
    - SSVEP
    - P300 BCI
    - non-invasive BCI
    - EEG decoding
    - EEG classification
    - fNIRS BCI
    - wearable BCI
    - dry electrode EEG
    - EEG benchmark
    - MOABB
    - EEGNet
    - EEG conformer
    - consumer BCI
  seeds:
    - title: "The largest EEG-based BCI reproducibility study for open science: the MOABB benchmark"
      journal: "arXiv 2024"
      arxiv_id: "2404.15319"
    - title: "Visual Decoding and Reconstruction via EEG Embeddings with Guided Diffusion"
      journal: "arXiv 2024"
      arxiv_id: "2403.07721"
    - title: "FALCON: Few-shot Algorithms for Consistent Neural Decoding Benchmark"
      journal: "NeurIPS 2024 / bioRxiv"
      arxiv_id: ""
    - title: "Improving motor imagery decoding methods for an EEG-based mobile BCI (2024 Cybathlon)"
      journal: "arXiv 2024"
      arxiv_id: "2511.23384"
```

---

## 附：现有 config.yaml 路线建议更新

当前 `config.yaml` 中 `bci_decoding` 和 `bci_embodied` 两条 BCI 路线 seed 为空占位。建议用以上 4 条路线替换（可保留现有路线 id，合并 keywords 和 seeds）。同时建议在 `arxiv.search_terms` 中补充：
```yaml
- speech neuroprosthesis
- motor cortex decoding
- neural foundation model
- brain-spine interface
- shared autonomy BCI
- brain-controlled robot
- ECoG decoding
```

---

*文档版本：v1.0 | 生成模型：claude-sonnet-4-6 | 调研来源：PubMed/PMC、Nature.com、arXiv、ScienceDaily、公司官网、前瞻产业研究院*
