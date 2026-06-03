---
domain: ai_science
date: 2026-06-03
confidence: high
last_updated_by: claude-sonnet-4-6
note: >
  AI for Science / 计算生物学顶尖成果多发表于 Nature / Science / Nature Methods 等期刊而非 arXiv。
  arXiv_id 仅在确认有预印本时标注；期刊来源优先标期刊。
  "未证实"标注表示信息来自二手报道或博客，原始论文尚未逐一核对。
  本报告覆盖截至 2026-06-03 的公开信息，重点 2024–2026 最新进展。
---

# AI for Science / AI 计算生物学领域现状基线

> 调研截止：2026-06-03 | 重点覆盖 2024–2026 最新进展

---

## 细分分支地图

### 1. 蛋白质结构预测（AlphaFold 系 / 开源生态）

**核心问题**：给定氨基酸序列，预测蛋白质三维原子级结构。

- **AlphaFold2（2021）** — DeepMind / Hassabis & Jumper，将结构预测精度提升至接近实验水平，标志性里程碑；已预测 2 亿+ 蛋白质结构，被引用次数创纪录。2024 年因此获诺贝尔化学奖。
- **AlphaFold3（2024）** — 扩展至蛋白质-核酸-小分子复合体，采用扩散架构；相比现有方法，蛋白质-配体预测精度提升 50%+，抗体-抗原精度显著提高。发表于 Nature 2024。
- **ESMFold（2022）** — Meta FAIR，基于 ESM-2 语言模型直接预测结构，推理速度极快（单序列秒级），已用于预测 6.17 亿个宏基因组蛋白结构（ESM 宏基因组图谱）。发表于 Science 2023。
- **Chai-1（2024）** — Chai Discovery，第一个公开可用的 AlphaFold3 级别替代方案（闭源但可免费访问），预测精度接近 AF3。
- **Boltz-1（2024 年 12 月）** — MIT Jameel Clinic（Barzilay、Jaakkola 团队），第一个完全开源、达到 AlphaFold3 精度的生物分子复合体预测模型；在 CASP15 蛋白质-配体 LDDT-PLI 达 65%（Chai-1 为 40%）。

**CASP 基准**：CASP15（2022）和 CASP16（2024）是两年一度的国际蛋白质结构预测竞赛。CASP16 首次将 AlphaFold3 纳入评测，多聚体结构预测成为重点方向。

---

### 2. 蛋白质设计

**核心问题**：从头（de novo）生成具有特定功能或能结合特定靶标的蛋白质。

#### 2.1 骨架生成（Backbone Design）

- **RFdiffusion（2023）** — Baker Lab（UW），基于 RoseTTAFold 微调的扩散模型，可设计对称组装体、金属结合蛋白、蛋白结合剂（Binder）；5 个靶标 19% 实验成功率，部分靶标达皮摩尔级亲和力。发表于 Nature 2023。
- **RFdiffusion2（2025）** — Baker Lab 升级版，支持原子级酶活性位点的骨架脚手架设计；41 个多样活性位点中全部成功生成骨架（旧方法仅 16 个）。发表于 Nature Methods 2025。
- **Chroma / FrameDiff / FoldingDiff** — 多个学术团队探索的扩散模型路线（2022-2023，部分未证实具体成果）。

#### 2.2 序列设计（Inverse Folding）

- **ProteinMPNN（2022）** — Baker Lab，给定 3D 骨架生成氨基酸序列，图神经网络架构，单链/多链均支持；实验验证率高，是 RFdiffusion 管线的标准配套工具。发表于 Science 2022。

#### 2.3 蛋白质 Binder / 抗体 / 酶设计

- **AlphaProteo（2024）** — Google DeepMind，生成式蛋白设计系统，在 7 个靶标上实现高达 300× 更高亲和力，对 BHRF1 成功率是传统方法 10×；已测试 VEGF-A、SARS-CoV-2 等靶标；对 TNFα 尚存挑战。于 2024 年 9 月发布（研究报告，未证实同行评审期刊发表状态）。
- **RFdiffusion 高亲和力 Binder（2023）** — Baker Lab，对生物活性螺旋肽靶标从头设计皮摩尔亲和力结合蛋白。发表于 Nature 2023。
- **新型酶设计（2025）** — Baker Lab 等，AI 流水线设计的蛋白酶活性接近天然蛋白酶，C&EN 报道称 2025 年底多个团队同期突破。

---

### 3. 蛋白质语言模型（Protein Language Models, PLM）

**核心思路**：将蛋白质序列类比自然语言，用大规模无监督预训练学习进化约束与序列-结构-功能关系。

- **ESM-1b / ESM-2（2022）** — Meta FAIR，ESM-2 最大版本 650M 参数，在 2.5 亿蛋白质序列上训练，广泛用于结构预测、功能预测、变异效应预测；ESMFold 的骨干。发表于 Science 2023。
- **ESM3（2024/2025）** — EvolutionaryScale（由前 Meta FAIR 团队创立），多模态掩码生成语言模型，同时对序列、结构、功能三个 token 轨道建模；98B 参数版，训练计算量超过之前所有生物模型；生成了与天然 GFP 序列相似度很低的功能性荧光蛋白（模拟 5 亿年进化）。发表于 Science 2025（2024 年 7 月 bioRxiv 预印本）。
- **ProGen2（2023）** — Salesforce AI，自回归生成模型，最大 6.4B 参数，在 10 亿+ 蛋白质序列训练，具备家族标签条件生成能力。发表于 Cell Systems 2023。
- **ProtGPT2（2022）** — 7.38 亿参数自回归 GPT 风格模型，生成蛋白序列，88% 预测为球状蛋白。发表于 Nature Communications 2022。
- **ByteDance DPLM-2（2025）** — 字节跳动，扩散蛋白语言模型，对序列+结构联合建模；650M 版超越 3B 规模基线，ICLR 2025 亮点论文。
- **趋势**：PLM 正向多模态（序列+结构+功能）、条件生成（靶向家族/功能）演化；ESM3 代表当前最高水平（截至 2025 年），但领域竞争激烈。

---

### 4. 基因组 / DNA 基础模型

**核心问题**：在 DNA 序列层面建模，预测变异效应、基因调控、非编码功能；并延伸至全基因组从头生成。

- **Nucleotide Transformer（2023/2024）** — InstaDeep/EMBL-EBI，最大 2.5B 参数编码器，在 3202 个人类基因组 + 850 个多物种基因组训练；零样本表示在 11/18 预测任务持平或超过专用方法，Fine-tune 后达 15/18。发表于 Nature Methods 2024。
- **Evo（2024）** — Arc Institute / Stanford / NVIDIA，7B 参数，131k token 上下文，基于 StripedHyena 架构，在单核生物+噬菌体基因组训练（OpenGenome 数据集，300B token）；支持从分子到基因组尺度的生成与预测。发表于 Science 2024。
- **Evo 2（2025/2026）** — Arc Institute / NVIDIA，40B 参数，1 兆碱基上下文窗口，在 9 万亿核苷酸（100,000+ 物种）上训练，覆盖原核/古菌/真核；零样本预测 BRCA1 致病变异效应，能生成简单细菌基因组长度的 DNA 序列。2025 年 2 月 bioRxiv 预印本，2026 年 3 月发表于 Nature。
- **Hyena DNA / HyenaDNA（2023）** — Evo 所基于的前代架构，长序列 DNA 建模（1M token），Stanford / Together AI。arXiv: 2306.15794。
- **基因调控 / 变异效应方向**：Enformer（2021, DeepMind, Nature Methods），Sei（2022, Nature Genetics）等专用模型用于基因调控预测；2024-2025 年 Evo/Evo2 通用模型开始在此任务上与专用模型竞争。

---

### 5. 单细胞 / 细胞图谱 AI

**核心问题**：从单细胞 RNA-seq（scRNA-seq）数据学习细胞状态、细胞类型、基因调控网络；跨批次整合与多模态融合。

- **Geneformer（2023/2024）** — Theodoris 等（Gladstone Institutes/现为 CZI），在 3000 万（V1）→ 1.04 亿（V2）单细胞转录组上预训练；用于基因网络调控预测与治疗靶点发现。V1 发表于 Nature 2023；V2 于 2024 年更新，纳入量化多任务学习。
- **scGPT（2024）** — 多伦多大学，33M+ 单细胞 RNA-seq 数据上的生成预训练 Transformer；支持批次整合、细胞类型注释、多模态整合（scRNA + scATAC + 蛋白质）。发表于 Nature Methods 2024。
- **scGPT-spatial（2025）** — scGPT 在空间转录组学数据上的持续预训练扩展（bioRxiv 预印本，2025）。
- **细胞图谱基础模型（2025）** — 一个用于可扩展人类细胞相似性搜索的细胞图谱基础模型，发表于 Nature 2025（具体团队未证实）。
- **虚拟细胞（Virtual Cell）** — CZI（Chan Zuckerberg Initiative）战略项目，2024 年启动，与 NVIDIA 合作扩大规模；包含：虚拟细胞平台（VCP）、Billion Cells Project（2025 年 2 月启动，目标 10 亿细胞数据集）、rBio（第一个基于虚拟细胞模拟训练的推理模型）。目标：可预测健康与疾病细胞行为的生成式 AI 细胞模型。

---

### 6. RNA 建模

- **BigRNA** — 可预测非编码变异对表达和剪接的影响，辅助 RNA 治疗药物（siRNA、ASO 等）设计（来源：二手报道，未证实同行评审状态）。
- **Orthrus（2024）** — RNA 基础模型，使用对比学习（剪接异构体+跨物种同源基因为正样本对）预训练，RNA 性质预测 SOTA。
- **LoRNA（2024）** — 长上下文 RNA 基础模型（StripedHyena 架构），专门预测转录组架构（剪接、polyA 位点等）。bioRxiv 2024。
- **RNA 结构预测**：RhoFold+（2023/2024，字节跳动/DP Technology）预测 RNA 三维结构，性能大幅超越传统方法（未证实最新排名）。

---

### 7. 药物发现 / 分子生成 / 分子对接

#### 7.1 分子对接

- **DiffDock（2022/2023）** — MIT（Barzilay 团队），扩散生成模型用于蛋白质-配体对接；盲对接 RMSD<2Å top-1 率 38%，超越 AutoDock Vina 等传统方法。arXiv: 2210.01776；发表于 ICLR 2023。
- **Uni-Mol Docking v2（2024）** — DP Technology，AI 对接引擎，77%+ 配体 RMSD<2Å，克服手性翻转和立体冲突，2024 年 5 月开源。

#### 7.2 分子生成与属性预测

- **Uni-Mol（2022/2024）** — DP Technology，3D 分子预训练表示学习模型，用于量子化学属性预测（Uni-Mol+, Nature Commun. 2024）、对接、属性预测。
- **GNoME（2023）** — Google DeepMind，图神经网络用于材料发现，预测了 220 万种稳定晶体结构（与药物分子生成领域相邻但非同一方向，供参考）。

#### 7.3 AI 制药管线里程碑

- **Rentosertib（ISM001-055）** — Insilico Medicine，第一个靶点（TNIK）和候选化合物均由 AI（Pharma.AI 平台）从头设计的小分子药，用于特发性肺纤维化（IPF）；Phase IIa GENESIS-IPF 试验（71 名患者，中国多中心）达到主要终点，60 mg QD 组 FVC 改善 +98.4 mL vs 安慰剂 −20.3 mL，2025 年 6 月发表于 Nature Medicine。同年获 USAN 命名，成为第一个经 USAN 命名的全 AI 设计药物。
- **Recursion Exscientia 合并（2024）** — 2024 年 8 月 Exscientia 被 Recursion 收购，整合表型组学筛选与精准化学为端到端平台；2025 年获第一个 AI 驱动临床概念验证（REC-4881）。
- **Isomorphic Labs（DeepMind 子公司）** — 2024 年 1 月与诺华、礼来签署合计 ~30 亿美元合作协议；2025 年 3 月完成 6 亿美元 A 轮融资；2026 年 5 月完成 21 亿美元融资；首批 AI 设计药物预计 2026 年底进入临床试验。

---

### 8. 生物 World Model / 仿真

- **虚拟细胞（CZI）** — 可视为生物学领域的 World Model 尝试：给定扰动（基因敲除、药物处理），预测细胞状态变化。
- **BioLab（2025）** — 多智能体 AI 系统，集成计算建模与湿实验室自动化，实现"设计-构建-测试-学习"闭环（bioRxiv 2025，未证实同行评审状态）。
- **GPT-5 + Ginkgo Bioworks（2026）** — GPT-5 通过机器人云实验室自主设计并运行 3.6 万个生物学实验，目标蛋白质生产成本降低 40%（2026 年 2 月报道，来源：二手媒体报道，具体技术细节未证实）。

---

## 关键论文（结构化）

> 格式：标题 | 作者/团队 | 来源 | arXiv ID 或期刊+年份 | 一句话贡献

### 里程碑论文

| # | 标题（简称）| 团队 | 来源 | 贡献 |
|---|------------|------|------|------|
| M1 | AlphaFold2 | Jumper, Hassabis 等 (DeepMind) | Nature, 2021 | 用 Evoformer+SE(3)等变网络将蛋白质结构预测精度首次接近实验水平，预测 2 亿+ 结构 |
| M2 | ESM-2 / ESMFold | Lin 等 (Meta FAIR) | Science, 2023 | 蛋白质语言模型直接从序列端到端预测结构，秒级推理，预测 6.17 亿宏基因组蛋白结构 |
| M3 | RFdiffusion | Watson 等 (Baker Lab) | Nature, 2023 | 扩散模型从头设计蛋白骨架，含对称组装、金属结合蛋白与 binder 设计 |
| M4 | ProteinMPNN | Dauparas 等 (Baker Lab) | Science, 2022 | 图神经网络逆折叠（给定骨架设计序列），实验验证率高，成为蛋白设计标准工具 |
| M5 | AlphaFold3 | Abramson 等 (DeepMind/Isomorphic) | Nature, 2024 | 扩展至蛋白-核酸-小分子复合体，扩散架构，蛋白-配体精度比最优方法提升 50%+ |
| M6 | ESM3 | Hayes 等 (EvolutionaryScale) | Science, 2025 (bioRxiv 2024.07.01.600583) | 多模态掩码生成语言模型，同时建模序列/结构/功能，98B 参数，设计功能性新型荧光蛋白 |
| M7 | Evo | Nguyen 等 (Arc Institute/Stanford) | Science, 2024 | 7B 参数 DNA 语言模型，131k token 上下文，从分子到基因组尺度生成与预测 |
| M8 | Evo 2 | 同 Arc Institute / NVIDIA | Nature, 2026 (bioRxiv 2025.02.18.638918) | 40B 参数，1M token 上下文，9 万亿核苷酸训练，覆盖全生命树，零样本预测 BRCA1 致病变异 |
| M9 | Geneformer | Theodoris 等 (Gladstone/CZI) | Nature, 2023 | 单细胞转录组预训练 Transformer，用于基因网络调控推断与治疗靶点发现 |
| M10 | scGPT | Cui 等 (Univ. Toronto) | Nature Methods, 2024 | 33M+ 单细胞数据预训练生成 Transformer，多模态单细胞分析通用基础模型 |

### 2024–2026 最新重要成果

| # | 标题（简称）| 团队 | 来源 | 贡献 |
|---|------------|------|------|------|
| N1 | Boltz-1 | Wohlwend, Corso 等 (MIT) | bioRxiv 2024/预印本发布 2024-12 | 第一个完全开源、达到 AF3 精度的生物分子复合体结构预测模型 |
| N2 | AlphaProteo | DeepMind 团队 | 技术报告, 2024-09（未证实同行评审状态）| 生成式蛋白 binder 设计，7 个靶标亲和力最高 300×，BHRF1 成功率 10× |
| N3 | RFdiffusion2 | Baker Lab | Nature Methods, 2025 (bioRxiv 2025.04.09.648075) | 原子级酶活性位点骨架脚手架，41/41 多样活性位点设计成功 |
| N4 | Nucleotide Transformer v2 | InstaDeep/EMBL-EBI | Nature Methods, 2024 | 2.5B 参数人类基因组基础模型，零样本表示超过大多数专用方法 |
| N5 | Rentosertib Phase IIa | Insilico Medicine | Nature Medicine, 2025 | 第一个全 AI 设计（靶点+化合物）的临床 PoC 药物，IPF 患者肺功能改善显著 |
| N6 | DPLM-2 | 字节跳动 Seed | ICLR 2025 | 扩散蛋白语言模型，序列+结构联合建模，650M 版超越 3B 规模基线 |
| N7 | Uni-Mol Docking v2 | DP Technology | 开源发布 2024-05 | AI 分子对接引擎，77%+ 配体 RMSD<2Å，克服手性翻转与空间冲突 |
| N8 | Geneformer V2 | Chen 等 (CZI) | 2024 | 量化多任务学习，Genecorpus-104M 训练，上下文特异基因网络表示 |
| N9 | scGPT-spatial | (Univ. Toronto 等) | bioRxiv 2025 | scGPT 在空间转录组学数据的持续预训练扩展 |
| N10 | rBio (Virtual Cell Reasoning) | CZI | 博客发布 2025 | 第一个基于虚拟细胞模拟训练的推理模型 |
| N11 | ProGen2 | Nijkamp 等 (Salesforce AI) | Cell Systems, 2023 | 6.4B 参数自回归蛋白质语言模型，家族条件生成，功能蛋白序列大规模生成 |
| N12 | DiffDock | Stärk 等 (MIT) | ICLR 2023 (arXiv: 2210.01776) | 扩散模型分子对接，盲对接 top-1 RMSD<2Å 率 38%，超越传统搜索方法 |

---

## 关键玩家

### 学术/研究机构

| 机构 | 核心贡献 | 代表人物/项目 |
|------|---------|--------------|
| **DeepMind / Google** | AlphaFold 系列（AF2, AF3, AlphaProteo），蛋白质结构预测定义者 | Demis Hassabis、John Jumper；2024 诺贝尔化学奖 |
| **Isomorphic Labs** | AlphaFold 商业化，AI 药物设计管线；诺华、礼来 ~30 亿美元合作；2026 首批临床试验 | Demis Hassabis（兼任 CEO） |
| **Baker Lab / Institute for Protein Design (UW)** | 蛋白质设计权威：RFdiffusion、ProteinMPNN、RFdiffusion2；21 个生物科技公司；2024 诺贝尔化学奖 | David Baker |
| **Meta FAIR** | ESM-2、ESMFold、ESM 宏基因组图谱；蛋白质语言模型领域奠基者 | - |
| **EvolutionaryScale** | ESM3，多模态蛋白语言模型，前 Meta FAIR 成员创立；AWS 战略投资 | - |
| **Arc Institute** | Evo、Evo 2 基因组基础模型；Stanford/UC Berkeley/UCSF 合作研究所 | Patrick Hsu 等 |
| **MIT（Barzilay/Jaakkola 团队）** | DiffDock、Boltz-1，开源分子对接与结构预测 | Regina Barzilay、Tommi Jaakkola |
| **Chan Zuckerberg Initiative (CZI)** | Virtual Cell 战略，Geneformer（托管），scGPT（合作），rBio；与 NVIDIA 深度合作 | - |
| **Insilico Medicine** | 全 AI 药物设计管线，Rentosertib（第一个全 AI 设计药物 Phase IIa 成功） | Alex Zhavoronkov |
| **Recursion Pharmaceuticals** | 表型组学 + AI 平台，2024 年收购 Exscientia；2025 年首个 AI 临床 PoC | Chris Gibson |
| **Chai Discovery** | Chai-1，开源 AlphaFold3 复现；2026 年 GSK 合作（$50M 预付款，未证实） | - |

### 中国玩家

| 机构 | 核心方向 | 代表产品/成果 |
|------|---------|--------------|
| **字节跳动（ByteDance Seed）** | 蛋白质基础模型、量子化学 AI、分子动力学 | DPLM-2（扩散蛋白语言模型，ICLR 2025）；RhoFold+（RNA 结构预测）（未证实 RhoFold+ 是否为字节主导） |
| **DP Technology（深势科技）** | 分子动力学（DeePMD），分子对接（Uni-Mol Docking v2），量子化学属性预测（Uni-Mol+） | Uni-Mol 系列；OpenLAM 大原子模型倡议 |
| **BioMap（百图生科）** | 生命科学 AI 平台，100B+ 参数生命科学基础模型（未证实具体成果规模）；Sanofi 合作 | xTrimo 系列蛋白/抗体模型 |
| **华为（Huawei）** | Pangu Drug（药物发现基础模型），云原生生物医学解决方案 | Pangu Drug；与 Hybio 制药合作探讨 |
| **腾讯 AI Lab / 腾讯量子实验室** | 蛋白质结构预测（tFold），分子对接（未证实最新进展） | tFold（蛋白质结构预测，2022-2023，未证实后续版本） |

### 日本玩家

- **Preferred Networks（日本）** — 深度学习驱动的材料/蛋白质研究（具体 AI4Bio 成果未收集到充分信息，标注：信息不足）。
- **理化学研究所（RIKEN）** — 基因组生物信息学研究，但在 AI 基础模型方向尚无主要里程碑（未证实）。

---

## 数据集 / Benchmark / 工具

### 核心数据集

| 数据集 | 规模 | 用途 |
|--------|------|------|
| **Protein Data Bank (PDB)** | 227,000+ 实验结构（2024 年，2025 年超 20,000 新存入） | 蛋白质结构训练/评测基准 |
| **UniRef50/90/100** | 2.5 亿+ 蛋白质序列 | 蛋白质语言模型预训练 |
| **PDB + 宏基因组（ESM 宏基因组图谱）** | 6.17 亿预测结构 | 宏基因组蛋白结构参考库 |
| **OpenGenome（Arc Institute）** | 300B token，270 万+ 原核/噬菌体基因组 | Evo 训练，公开最大 DNA 预训练集 |
| **Genecorpus-30M / 104M** | 3000 万 / 1.04 亿单细胞转录组 | Geneformer 预训练 |
| **CZI Billion Cells Project（进行中）** | 目标 10 亿细胞数据（2025 年启动） | Virtual Cell 模型训练 |

### 核心 Benchmark

| Benchmark | 领域 | 说明 |
|-----------|------|------|
| **CASP（每两年一届）** | 蛋白质结构预测 | 国际竞赛，CASP15（2022）/ CASP16（2024）为最近两届 |
| **PDBBind** | 分子对接 | 蛋白质-配体对接标准数据集和评测集 |
| **ProteinGym** | 蛋白质突变效应预测 | 约 2000 深度突变扫描（DMS）实验数据集 |
| **FLIP（Fitness Landscape Inference for Proteins）** | 序列-功能关系 | 多任务蛋白质适应度预测 |
| **GUE（Genome Understanding Evaluation）** | 基因组建模 | 多任务 DNA 序列基准 |
| **CZI Virtual Cell Benchmarks（2025）** | 单细胞/虚拟细胞 | CZI 与行业合作社区基准套件 |

### 常用工具

- **AlphaFold Server** — Google 提供，免费非商业访问，基于 AF3
- **ESMFold API / LocalColabFold** — 快速开源结构预测
- **RFdiffusion / ProteinMPNN** — Baker Lab 开源，蛋白设计核心流水线
- **Boltz-1** — MIT 开源，替代 AF3 的生物分子复合体预测
- **NVIDIA BioNeMo** — 企业级生物 AI 框架，集成 ESM、OpenFold、Evo2 等
- **OpenFold** — 开源 AF2 复现，支持再训练

---

## 近 1–2 年趋势（2024–2026）

### 趋势 1：基础模型化 / 大一统方向

从专用模型（只做结构预测，或只做序列生成）到多模态统一基础模型（序列+结构+功能联合建模）。ESM3（蛋白）、Evo 2（DNA），以及 CZI Virtual Cell（细胞尺度）均代表这一趋势。生物学大模型规模正追赶 LLM，从 10B 向 100B+ 参数迈进。

### 趋势 2：蛋白质 × 基因组多模态融合

预测基因组变异如何影响蛋白质功能（sequence → structure → function 全链路），Evo 2 的零样本 BRCA1 变异预测是典型案例。蛋白质设计与基因组工程（合成生物学）的边界日益模糊。

### 趋势 3：AI + 自动化实验室（实验闭环）

"设计-构建-测试-学习"（DBTL）循环加速：AI 提出设计方案，机器人自动执行湿实验，数据反馈训练模型。Baker Lab 与 Isomorphic 的研究管线、Recursion 的表型组学平台、GPT-5+Ginkgo Bioworks 的云机器人实验室（2026 年初）均是代表。自动化实验室正从科研工具走向药物研发核心基础设施。

### 趋势 4：商业化加速 / AI 制药临床验证

- 2025 年：Insilico Rentosertib Phase IIa 成功（Nature Medicine），全 AI 设计药物首次人体 PoC。
- 2025-2026 年：Recursion 首个 AI 驱动临床 PoC；Isomorphic Labs 首批临床试验预计 2026 年底启动。
- 投资规模：Isomorphic Labs 完成 21 亿美元融资（2026 年 5 月）。
- 合作模式：大型药企（诺华、礼来、GSK、Sanofi 等）与 AI 公司签署数十亿美元战略合作。

### 趋势 5：诺贝尔奖背书与学界/工业界人才流动

2024 年诺贝尔化学奖同时颁给 Hassabis/Jumper（结构预测）和 Baker（蛋白设计），标志 AI4Biology 已被主流科学界完全认可。学界人才向工业界流动加速（Meta FAIR → EvolutionaryScale 为典型案例）。

---

## 开放问题

1. **蛋白质动力学与构象变化**：AF3 等模型预测单一静态结构，蛋白质天然存在多构象（apo/holo，intrinsically disordered regions），如何用生成模型表征动力学系综？
2. **蛋白质-蛋白质相互作用（PPI）设计**：AlphaProteo 在 TNFα 等靶标上仍有挑战，灵活构象靶标的 binder 设计成功率仍低。
3. **DNA 基础模型 → 细胞表型预测**：从 DNA 序列到细胞表型的完整因果链建模（基因型-表型预测），Evo 2 零样本变异效应只是起点。
4. **单细胞 AI 的扰动预测**：给定药物/基因敲除，预测细胞状态变化（CRISPRi/a + scRNA-seq 数据正快速积累，但模型泛化性仍有限）。
5. **长时间尺度分子动力学**：传统 MD 仿真受时间尺度限制（ns-μs），AI 驱动的 MD（Deep Potential / MLMD）如何可靠扩展到生物学相关时间尺度（ms）？
6. **数据质量与偏差**：PDB 中高分辨率结构偏向可溶性、容易结晶的蛋白质；膜蛋白、无序区域训练数据严重不足。
7. **实验验证通量瓶颈**：AI 设计速度已远超实验验证速度，自动化实验室能否跟上计算输出？成本是否可持续？
8. **基础模型的可解释性**：PLM 和 DNA 语言模型学到了什么"生物学知识"？如何机制性理解（Evo 2 的 Mechanistic Interpretability 研究已启动，Goodfire AI 合作）。

---

## 建议路线配置（给 config 用）

```yaml
routes:
  - id: protein_structure_design
    name: "蛋白质结构预测与设计"
    description: >
      覆盖 AlphaFold 系（AF2/AF3）、RFdiffusion/RFdiffusion2、ProteinMPNN、
      AlphaProteo、Boltz-1/Chai-1、酶设计、抗体设计等核心方向。
      重点追踪 Baker Lab、DeepMind/Isomorphic、EvolutionaryScale 最新成果。
    keywords:
      - "protein structure prediction"
      - "de novo protein design"
      - "RFdiffusion"
      - "AlphaFold3"
      - "protein binder"
      - "inverse folding"
      - "enzyme design"
      - "antibody design"
      - "diffusion protein"
      - "ProteinMPNN"
    seeds:
      - title: "De novo design of protein structure and function with RFdiffusion"
        source: "Nature, 2023"
      - title: "Accurate structure prediction of biomolecular interactions with AlphaFold 3"
        source: "Nature, 2024"
      - title: "Robust deep learning-based protein sequence design using ProteinMPNN"
        source: "Science, 2022"
      - title: "Atom level enzyme active site scaffolding using RFdiffusion2"
        source: "Nature Methods, 2025 (bioRxiv 2025.04.09.648075)"

  - id: protein_language_model
    name: "蛋白质语言模型（ESM 系）"
    description: >
      蛋白质语言模型（PLM）：ESM-2、ESMFold、ESM3（EvolutionaryScale）、
      ProGen2、ProtGPT2、DPLM-2 等；多模态序列-结构-功能联合建模趋势。
    keywords:
      - "protein language model"
      - "ESM"
      - "ESMFold"
      - "protein representation learning"
      - "variant effect prediction"
      - "zero-shot fitness"
      - "generative protein"
      - "sequence generation"
      - "PLM"
    seeds:
      - title: "Evolutionary-scale prediction of atomic-level protein structure with a language model (ESM-2/ESMFold)"
        source: "Science, 2023"
      - title: "Simulating 500 million years of evolution with a language model (ESM3)"
        source: "Science, 2025 (bioRxiv 2024.07.01.600583)"
      - title: "ProGen2: Exploring the boundaries of protein language models"
        source: "Cell Systems, 2023"
      - title: "DPLM-2: A Multimodal Diffusion Protein Language Model"
        source: "ICLR 2025 (ByteDance Seed)"

  - id: genomic_foundation_model
    name: "基因组 / DNA 基础模型"
    description: >
      DNA/基因组基础模型：Evo（Arc Institute）、Evo 2（Nature 2026）、
      Nucleotide Transformer、HyenaDNA 等；变异效应预测、基因调控建模、
      全基因组生成；与合成生物学的交叉。
    keywords:
      - "genomic foundation model"
      - "DNA language model"
      - "Evo"
      - "Nucleotide Transformer"
      - "variant effect prediction"
      - "gene regulation"
      - "non-coding DNA"
      - "genome design"
      - "BRCA1"
      - "long-context DNA"
    seeds:
      - title: "Sequence modeling and design from molecular to genome scale with Evo"
        source: "Science, 2024"
      - title: "Genome modelling and design across all domains of life with Evo 2"
        source: "Nature, 2026 (bioRxiv 2025.02.18.638918)"
      - title: "Nucleotide Transformer: Building and Evaluating Robust Foundation Models for Human Genomics"
        source: "Nature Methods, 2024"
      - title: "HyenaDNA: Long-Range Genomic Sequence Modeling at Single Nucleotide Resolution"
        source: "arXiv: 2306.15794 (NeurIPS 2023)"

  - id: single_cell_drug_discovery
    name: "单细胞 AI 与药物分子发现"
    description: >
      单细胞基础模型（scGPT、Geneformer）与虚拟细胞（CZI）；
      分子对接（DiffDock）与分子生成；AI 制药管线（Insilico、Recursion、Isomorphic Labs）；
      RNA 建模与扰动预测。
    keywords:
      - "single cell foundation model"
      - "scGPT"
      - "Geneformer"
      - "virtual cell"
      - "molecular docking"
      - "DiffDock"
      - "drug discovery AI"
      - "molecular generation"
      - "perturbation prediction"
      - "RNA splicing"
      - "Uni-Mol"
    seeds:
      - title: "scGPT: toward building a foundation model for single-cell multi-omics using generative AI"
        source: "Nature Methods, 2024"
      - title: "Transfer learning enables predictions in network biology (Geneformer)"
        source: "Nature, 2023"
      - title: "DiffDock: Diffusion Steps, Twists, and Turns for Molecular Docking"
        source: "ICLR 2023 (arXiv: 2210.01776)"
      - title: "A generative AI-discovered TNIK inhibitor for idiopathic pulmonary fibrosis: a randomized phase 2a trial (Rentosertib)"
        source: "Nature Medicine, 2025"
```

---

## 附：领域全景总结

```
AI for Science / 计算生物学
│
├── 蛋白质结构预测 ── AlphaFold2/3, ESMFold, Boltz-1, Chai-1
│
├── 蛋白质设计
│   ├── 骨架生成 ─── RFdiffusion, RFdiffusion2, Chroma
│   ├── 序列设计 ─── ProteinMPNN, ESM-IF
│   └── 功能设计 ─── Binder, Antibody, Enzyme (AlphaProteo)
│
├── 蛋白质语言模型 ── ESM-2, ESM3, ProGen2, ProtGPT2, DPLM-2
│
├── 基因组 / DNA 基础模型 ── Evo, Evo 2, Nucleotide Transformer, HyenaDNA
│
├── 单细胞 / 细胞图谱 AI ── scGPT, Geneformer, Virtual Cell (CZI)
│
├── RNA 建模 ── Orthrus, LoRNA, BigRNA, RhoFold+
│
├── 分子对接 / 药物发现
│   ├── 对接 ─── DiffDock, Uni-Mol Docking v2
│   ├── 生成 ─── 分子生成模型（RDKit 生态 + DL 模型）
│   └── 管线 ─── Insilico, Recursion, Isomorphic Labs, BioMap
│
└── 实验闭环 / World Model ── BioLab, Virtual Cell, AI + Robot Lab
```

---

*生成于 2026-06-03 | 模型：claude-sonnet-4-6 | 置信度：high（核心里程碑）/ medium（2025-2026 最新进展）*
