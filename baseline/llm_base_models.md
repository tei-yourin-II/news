---
domain: llm_base
date: 2026-06-03
confidence: medium-high
sources:
  - OpenAI official (openai.com/index)
  - Anthropic official (anthropic.com)
  - Google DeepMind (deepmind.google)
  - Meta AI (ai.meta.com)
  - xAI (x.ai)
  - Mistral AI (mistral.ai)
  - DeepSeek API docs (api-docs.deepseek.com)
  - Qwen GitHub / Alibaba Cloud
  - ByteDance Seed (seed.bytedance.com)
  - Moonshot AI / Kimi (moonshot.ai)
  - Zhipu / Z.ai (huggingface.co/zai-org)
  - MiniMax (minimax.io)
  - Baidu ERNIE (ernie.baidu.com)
  - Stanford AI Index 2026 (April 13, 2026)
  - Arena Leaderboard (arena.ai/leaderboard)
  - BenchLM.ai, artificialanalysis.ai
注意: 部分信息为截止2026-06-03的最新公开数据，快速迭代领域数据时效性有限。
---

# LLM 基础模型横向格局（2025-2026 中）

> 更新日期：2026-06-03  
> 分析师：AI 大模型产业分析员（基于公开信息综合判断）  
> 置信度：medium-high（主体事实可核查；打分为主观综合判断）

---

## 一、各大厂当前旗舰/最新模型清单

### 🇺🇸 美国阵营

#### OpenAI
| 模型 | 发布时间 | 类型 | 备注 |
|------|---------|------|------|
| GPT-5 | 2025-08（推测） | 通用旗舰 | 替代 GPT-4o 成为默认模型 |
| GPT-5.2 | 2025年末（未证实具体日期） | 推理增强 | ARC-AGI-1 突破 90% |
| GPT-5.4 | 2026年初（未证实具体日期） | 推理旗舰 | Arena 数学 Elo 1515 领先 |
| GPT-5.5 | 2026-04-23（API可用） | 最新旗舰 | SWE-bench 88.7%；Terminal-Bench 82.7% |
| o3 | 2025年初 | 推理系列 | 已宣布将于2026-08-26 从ChatGPT退役 |
| o4-mini | 2025年 | 轻量推理 | AIME 2024/2025 最高分轻量模型 |

**GPT-5 关键 benchmark**（来源：openai.com，2025）：
- AIME 2025: 94.6%（无工具）
- SWE-bench Verified: 74.9%
- MMMU: 84.2%
- HealthBench Hard: 46.2%

**GPT-5.5 关键 benchmark**（来源：openai.com，2026-04-23）：
- SWE-bench: 88.7%
- SWE-bench Pro: 58.6%
- Terminal-Bench 2.0: 82.7%

#### Anthropic
| 模型 | 发布时间 | 类型 | 备注 |
|------|---------|------|------|
| Claude Sonnet 4 | 2025-05 | 均衡旗舰 | Claude 4 代首发 |
| Claude Opus 4 | 2025-05 | 高端旗舰 | |
| Claude Opus 4.5 | 2025-11 | 高端旗舰 | |
| Claude Opus 4.6 | 2026-02 | 高端旗舰 | Arena Elo 1503（公司级最高） |
| Claude Opus 4.7 | 2026-04 | 高端旗舰 | 编程 Arena Elo 1569（thinking模式） |
| **Claude Opus 4.8** | **2026-05-28** | **当前最新旗舰** | 强调诚实度与可靠性，代码自查能力提升4x |
| Claude Sonnet 4.6 | 2026-02 | 均衡版 | |

**Arena Leaderboard 表现**（来源：arena.ai，约2026-05~06）：
- Claude Opus 4.7 thinking：编程 Elo 1569（领先）
- Anthropic 公司整体 Arena Elo：1503（2026-03 数据，各家中最高）

#### Google DeepMind
| 模型 | 发布时间 | 类型 | 备注 |
|------|---------|------|------|
| Gemini 2.5 Pro | 2025-06-17（GA） | 旗舰 | |
| Gemini 2.5 Flash-Lite | 2025-06-17 | 轻量 | |
| Gemini 3 Pro | 2025-11-18 | 旗舰升级 | |
| Gemini 3 Deep Think | 2025-11-18 | 推理增强 | |
| Gemini 3.1 Pro | 2026年初 | 旗舰 | Arena Elo 1493；AIME26 99.6（带工具，第二）|
| **Gemini 3.5 Flash** | **2026-05（Google I/O 2026）** | **当前最新旗舰** | Agent/代码任务领先 Gemini 3.1 Pro |
| Gemini 3.5 Pro | 预计2026-06~07 | 即将发布 | 尚未GA（未证实发布日期） |
| Gemini Omni | 2026-05（测试） | 全模态 | 任意输入→任意输出，包含视频生成 |

**Google 公司整体 Arena Elo**：1494（2026-03 数据）

#### Meta
| 模型 | 发布时间 | 类型 | 备注 |
|------|---------|------|------|
| **Llama 4 Scout** | **2026-04-05** | 开源轻量 | 17B 激活参数，16 experts；10M token 上下文；单 H100 可跑 |
| **Llama 4 Maverick** | **2026-04-05** | 开源旗舰 | 17B 激活参数，128 experts；MoE 架构 |
| Llama 4 Behemoth | 训练中（未发布） | 超旗舰 | 无官方 benchmark，预计2026年内 |

**Llama 4 Maverick benchmark**（来源：ai.meta.com，2026-04-05）：
- GPQA Diamond: 69.8%（远超 GPT-4o 的 53.6%）
- MMLU: 85.5%
- MMLU-Pro: 80.5%
- MGSM: 92.3%
- DocVQA: 94.4%

#### xAI（Elon Musk）
| 模型 | 发布时间 | 类型 | 备注 |
|------|---------|------|------|
| Grok 3 | 2025-02-17 | 推理旗舰 | 20万 GPU Colossus 训练 |
| Grok 4 | 2025年末（未证实具体日期） | 通用旗舰 | HLE 50.7%（全球领先）|
| Grok 4.20 | 2026-02（beta） | 旗舰增强 | 200万 token 上下文；多智能体协作 |
| **Grok 4.3** | **2026-05-06** | **当前最新** | 架构升级版 Grok 4.20；知识截止2025-12 |
| Grok 5 | 训练中（未发布） | 下一代 | 无 benchmark |

**Grok 4 benchmark**（来源：多家评测，含未证实数据）：
- AIME 2026: 88.9%
- GPQA Diamond: 83.3%（未证实，来源为泄露数据）
- SWE-bench: 69.1%（无脚手架）
- HLE（Humanity's Last Exam）: 50.7%（全球领先）
- **xAI 公司整体 Arena Elo：1495（2026-03）**

#### Mistral AI（法国，欧洲最强）
| 模型 | 发布时间 | 类型 | 备注 |
|------|---------|------|------|
| **Mistral Large 3** | **2025-12-02** | 当前最强闭源/开放 | 675B 总参数，41B 激活；MoE；OSS 非推理类 LMArena #2 |
| Mistral Small 4 | 2026-03 | 轻量 | |
| Mistral Large 3（推理版） | 预计2026年 | 推理增强 | 尚未发布（截至2026-04） |

**Mistral Large 3 规格**：
- 总参数 675B，激活参数 41B
- 上下文 262K tokens
- 定价：$0.5/M input，$1.5/M output
- LMArena 开源非推理模型类别 #2

---

### 🇨🇳 中国阵营

#### DeepSeek（幻方量化）
| 模型 | 发布时间 | 类型 | 备注 |
|------|---------|------|------|
| DeepSeek-V3 | 2024-12 | 开源旗舰 | MoE；MATH-500 超越 o1-preview |
| DeepSeek-R1 | 2025-01 | 开源推理 | MATH-500 97.3%；接近 OpenAI o1 |
| **DeepSeek-V3.2** | **2025年中（API已更新）** | 当前旗舰 | deepseek-chat（非思考）+deepseek-reasoner（思考）合并 |
| DeepSeek-R2 | 未发布 | 下一代推理 | 未证实，可能仍在开发 |

**注**：V3.2 将 deepseek-chat 和 deepseek-reasoner 合并为统一 API，支持"思考模式"切换。R2 独立版本截至调研日期尚未正式发布。

**Arena Elo（DeepSeek）：1424（2026-03）** — 中国开源模型中较低，但成本/性能比极高。

#### 阿里云（Qwen 通义）
| 模型 | 发布时间 | 类型 | 备注 |
|------|---------|------|------|
| Qwen3（家族） | 2025-04-28 | 开源全系 | 含 0.6B~32B Dense 及 30B-A3B/235B-A22B MoE |
| Qwen3.5 | 2026-02-16 | 旗舰 | 397B-A17B MoE；支持文字/图片/视频 |
| **Qwen3.6 系列** | **2026年初** | 当前旗舰 | 多模态；Apache 2.0 开源，可商用 |
| Qwen3.7-Max | 2026-05（即将发布） | 超旗舰 | 阿里 I/O 2026 预告 |
| Qwen3.7-Plus | 2026年 | 多模态智能体 | 含 Agent 强化 |

**注**：阿里同期发布珍武（Zhenwu）AI 芯片，意图减少对英伟达依赖。

**Qwen3.5 benchmark**（来源：GitHub QwenLM）：
- GPQA Diamond: 88.4%（超越除最贵闭源模型外的所有模型）

**Arena Elo（Alibaba）：1449（2026-03）** — 中国厂商中最高。

#### 字节跳动（Doubao / Seed）
| 模型 | 发布时间 | 类型 | 备注 |
|------|---------|------|------|
| Doubao 1.5 Pro | 2025年 | 旗舰 | |
| Seed 2.0 | 2025年末 | 研究旗舰 | |
| **Doubao 2.0 系列** | **2026-02-14** | **当前旗舰** | Pro/Lite/Mini/Code；专为 Agent 场景设计 |

**Doubao 2.0 定位**：
- 对标 GPT-5.2 和 Gemini 3 Pro，但价格低约 10 倍
- 约 1.55 亿周活用户（中国 AI 应用最大）
- 数学/代码/多模态推理基准与前述对标模型接近（未证实独立 benchmark 具体数值）

**Arena Elo（ByteDance）：1464（2026-03 Stanford AI Index）**

#### 月之暗面（Kimi / Moonshot AI）
| 模型 | 发布时间 | 类型 | 备注 |
|------|---------|------|------|
| Kimi K2 | 2025-07 | 开源推理 | 1T 总参数，32B 激活；MoE |
| Kimi K2 Thinking | 2025-11 | 开源推理增强 | 训练成本约 460 万美元 |
| Kimi K2.5 | 2026-01 | 多模态 | 加入 MoonViT 视觉编码器（4亿参数）|
| **Kimi K2.6** | **2026-04-20** | **当前最新旗舰** | 1T MoE；256K 上下文；300智能体协同；4000步 |

**Kimi K2.6 规格**：
- 1T 总参数，32B 激活；384 experts（8选+1共享）
- 256K token 上下文（全变体）
- Agent Swarm：300 子智能体，4000 协调步
- SWE-bench 等 Agent 基准声称超越 GPT-5.4 和 Claude Opus 4.6（部分未经独立核实）

**融资**：2026-05 完成 20 亿美元融资，估值超 1400 亿人民币。

#### 智谱 AI / Z.ai（GLM 系列）
| 模型 | 发布时间 | 类型 | 备注 |
|------|---------|------|------|
| GLM-4.5 | 2025-07 | 旗舰 | 355B-A32B MoE |
| GLM-4.7 | 2025-12 | 旗舰 | |
| **GLM-5** | **2026-02** | **旗舰** | 744B-A40B MoE；28.5T token 预训练 |
| **GLM-5.1** | **2026-04-08（开源）** | **当前最新** | 开源发布；API 较 Claude Opus 4.6 便宜约 5-8x |

**GLM-5 benchmark**（来源：Hugging Face blog，2026-02）：
- SWE-bench Verified: 77.8%
- AIME 2026: 92.7%
- GPQA-Diamond: 86.0%
- 上下文：200K tokens

**注**：Z.ai 于 2026-01 在港交所上市，成为首家上市的中国 AI 大模型公司。  
**Arena Search 排名**（2026-05）：ERNIE 5.1 以 1223 分排第四（GLM 数据未单独列出）。

#### MiniMax
| 模型 | 发布时间 | 类型 | 备注 |
|------|---------|------|------|
| MiniMax-M1 | 2025年 | 开源推理 | 超越原版 DeepSeek-R1、Qwen3-235B（工具调用/长上下文）|
| MiniMax M2.5 | 2025年末 | 通用旗舰 | SOTA 编程/工具调用 |
| MiniMax M2.7 | 2026年初 | 自进化旗舰 | SWE-Pro 56.22%；100 TPS；$0.30/M input |
| **MiniMax M3** | **2026-06-01** | **当前最新旗舰** | 1M token 上下文；原生多模态；MSA 架构 |

**MiniMax M3 benchmark**（来源：minimax.io，2026-06-01）：
- SWE-Bench Pro: 59.0%
- Terminal-Bench 2.1: 66.0%
- BrowseComp: 83.5（超越 Claude Opus 4.7 的 79.3）
- **注**：M3 benchmark 部分数据"前沿声称，未经独立验证"（TechTimes 2026-06-01）

#### 百度（ERNIE 文心）
| 模型 | 发布时间 | 类型 | 备注 |
|------|---------|------|------|
| ERNIE 5.0 | 2026-01-22（正式版） | 全模态旗舰 | 2.4T 参数；全模态理解与生成 |
| **ERNIE 5.1** | **2026-05-09** | **当前最新** | 参数压缩至 5.0 的 1/3；预训练成本 6%；AIME26 99.6（带工具） |

**ERNIE 5.1 表现**：
- AIME 2026（带工具）: 99.6 — 全球第二，仅次于 Gemini 3.1 Pro
- Arena Search 排行（2026-05）: 全球第 4，中国模型第 1（1223 分）

#### 腾讯（混元 Hunyuan）
| 模型 | 发布时间 | 类型 | 备注 |
|------|---------|------|------|
| Hunyuan T1 | 2026-02~03 | 推理旗舰 | Hybrid-Transformer-Mamba MoE；MMLU-PRO 87.2（全球第二，仅次于 o1）|
| Hunyuan T1 Vision | 2025-09-16 | 视觉推理 | |
| Hunyuan 2.0 Think | 2025-11-09 | 推理 | |
| Hunyuan 3.0 | 预计2026-04（未证实） | 全模态 | 重点推理+Agent+全模态 |

---

## 二、横向实力评估

### 综合能力（按 Arena Elo + 多维 benchmark 综合）

| 梯队 | 厂商/模型 | Arena Elo（约） | 备注 |
|------|----------|---------------|------|
| **T0 绝对顶端** | Claude Opus 4.7/4.8（Anthropic） | ~1503-1569 | 编程/Agent 领先 |
| **T0 绝对顶端** | GPT-5.5（OpenAI） | ~1500+ | 综合/代码/推理 |
| **T0 绝对顶端** | Grok 4（xAI） | ~1495 | HLE 全球第一（50.7%）|
| **T1 顶级** | Gemini 3.5 Flash/3.1 Pro（Google） | ~1493 | AIME26 带工具接近满分 |
| **T1 顶级** | GLM-5.1（Z.ai） | ~估计1450+ | GPQA 86.0%；开源可用 |
| **T1 顶级** | Kimi K2.6（Moonshot） | ~估计1440+ | Agent Swarm 领先 |
| **T2 强力** | Llama 4 Maverick（Meta，开源） | ~1430+ | GPQA 69.8%；开源可商用 |
| **T2 强力** | DeepSeek V3.2（开源） | ~1424 | 成本/性能比最优之一 |
| **T2 强力** | Qwen3.6（阿里，开源） | ~1449 | 中国开源最高 Arena |
| **T2 强力** | Doubao 2.0（字节） | ~1464 | 用户规模最大 |
| **T3 跟跑** | Mistral Large 3（欧洲） | ~1400+ | OSS 非推理#2；性价比高 |
| **T3 跟跑** | ERNIE 5.1（百度） | ~1223（Search Elo） | AIME 带工具领先，通用稍弱 |
| **T3 跟跑** | Hunyuan T1（腾讯） | 估计1380+ | MMLU-PRO 高；创意/中文强 |
| **T3 跟跑** | MiniMax M3 | 估计1390+ | BrowseComp 超越部分顶级 |

### 各维度领先者

| 维度 | 全球领先 | 中国领先 | 说明 |
|------|---------|---------|------|
| **综合推理** | Claude Opus 4.7/GPT-5.5/Grok 4 | GLM-5.1/Kimi K2.6 | HLE Grok 领先；GPQA Claude/GLM |
| **数学** | GPT-5.4（Arena 1515） | ERNIE 5.1（AIME26 99.6带工具，#2全球） | |
| **代码** | Claude Opus 4.7（编程 Elo 1569） | Kimi K2.6 / GLM-5（SWE 77.8%） | |
| **多模态** | Gemini 3.5（Omni 全模态） / GPT-5.5 | ERNIE 5.0（2.4T 全模态） | Gemini Omni 类别最广 |
| **长上下文** | Llama 4 Scout（10M tokens，开源最长） | Kimi K2.6（256K） | |
| **Agent/工具调用** | Claude Opus/Kimi K2.6/GLM-5.1 | Kimi K2.6（300智能体协同） | |
| **开源/可部署性** | Llama 4 Maverick/Scout（Meta） | DeepSeek V3.2 / Qwen3.6 / Kimi K2（1T MoE 开源） | |
| **性价比** | DeepSeek V3.2 / Mistral Large 3 | Doubao 2.0（GPT-5.2 10分之一价）| |
| **中文能力** | -- | 通义Qwen3.5 / 文心ERNIE / 豆包 | 原生中文优势明显 |

---

## 三、2025-2026 关键趋势

### 3.1 推理模型全面铺开，合并到通用旗舰

- **2025年初**：推理模型（OpenAI o1/o3、DeepSeek-R1）以独立产品形态冲击市场。
- **2025-2026**：推理能力被内化到通用模型——GPT-5/5.5、Claude Opus 4.x、Gemini 3.x 均默认支持"思考模式"切换，推理不再是独立 SKU，而是旗舰标配。
- **轻量推理**：o4-mini、Gemini 3.5 Flash 等证明小参数可打超重量级推理基准（AIME 2024/2025 o4-mini 最优）。

### 3.2 开源 vs 闭源：能力差距几乎消除，博弈转向部署与生态

- 2025年初闭源仍有明显领先，2026年中差距收窄至"单位数百分比"（Stanford AI Index）。
- **开源优势**：DeepSeek V3.2、Kimi K2.6（1T MoE）、GLM-5.1、Qwen3.6、Llama 4 Maverick 在 SWE-bench、GPQA、Agent 基准上已逼近或局部超越闭源。
- **闭源优势**：复杂推理、大规模指令遵循、运营稳定性、安全护栏仍略胜；Claude Opus 系列在 coding/agent 实战仍领先。
- **趋势**：开源是中国厂商的主要武器（低价+可定制），闭源是 OpenAI/Anthropic 商业护城河。

### 3.3 中美差距：Stanford 2026 AI Index 实质性消除

- 2026-04-13 Stanford HAI 报告：美国顶级模型仅领先中国 **2.7%**（Arena Elo 39 点），而2023年差距曾高达 17.5-31.6 个百分点。
- 美国 AI 私人投资是中国的 **23 倍**（2858 亿 vs 124 亿美元），但性能差距已基本抹平。
- 中国优势：成本效率、中文能力、开源生态、应用落地（用户规模）、专利数量（全球专利的 69.7%）。
- 美国优势：底层原创能力（Transformer 架构仍在美）、通用推理前沿、算力基础设施（H100/H200 出口管制下仍领先）、全球生态。
- **评判**：中国已在"追赶赛"中胜出，但"原创引领"能力的争议持续存在。

### 3.4 推理成本大幅下降，但竞争态势激烈

- GPT-4 同等性能的成本：2022年末约 $20/M tokens → 2025年末约 $0.40/M tokens（**下降 50x**）。
- 2023年以来前沿模型 API 输出价格指数下降约 **94.5%**。
- 驱动力：MoE 架构减少激活参数、KV cache 优化、模型蒸馏、硬件效率提升。
- Gartner（2026-03）预测：2030年 1T 参数 LLM 推理成本较2025年再降 **90%**。
- 中国厂商（Doubao、DeepSeek）激进定价对美国主导厂商构成价格压力。

### 3.5 Agent 能力成为新赛点

- 2026年上半年，竞争重心从"单一问答能力"转向"多步 Agent 任务完成率"。
- SWE-bench、Terminal-Bench、BrowseComp、Agent Swarm 等成为新核心基准。
- Kimi K2.6 的 300-智能体/4000步协同、GLM-5 的"Agentic Engineering"定位、Doubao 2.0 的"Agent Era"均体现此趋势。
- Claude Opus 系列在实际 coding agent 中仍是开发者首选（Arena coding Elo 领先）。

### 3.6 全模态成新前线

- Gemini Omni（2026-05）：任意输入→任意输出，含视频生成
- ERNIE 5.0：2.4T 参数原生全模态
- GPT-5.5：原生多模态
- 中国跟进：Qwen3-VL、Doubao 视频（Seedance 2.0）、Kimi K2.5（MoonViT）

---

## 四、厂商横向（结构化）

> 格式：厂商 | 国家 | 最新旗舰模型 | 实力分(0-100) | 一句话定位
> 实力分说明：综合 Arena 排名、benchmark、生态影响力、技术原创性、商业落地的挑剔判断（100=不存在的完美分）

| 厂商 | 国家 | 最新旗舰模型 | 实力分(0-100) | 一句话定位 |
|------|------|------------|-------------|-----------|
| OpenAI | US | GPT-5.5（2026-04-23） | 92 | 综合天花板+商业生态最强，但高度闭源、定价昂贵，近年推理领域被追赶 |
| Anthropic | US | Claude Opus 4.8（2026-05-28） | 91 | 编程/Agent 实战最强，安全可靠性领先，迭代频率最高，但不开源 |
| Google DeepMind | US | Gemini 3.5 Flash（2026-05） | 88 | 多模态+全模态最广，Google 生态整合强，但旗舰产品化稍滞后竞争对手 |
| xAI | US | Grok 4.3（2026-05-06） | 84 | HLE 世界第一，具备黑马潜力，但商业化+生态尚不成熟，数据来源争议 |
| Meta | US | Llama 4 Maverick（2026-04-05） | 82 | 开源多模态 MoE 性能最强，10M 上下文领先，不做推理闭源产品 |
| Mistral AI | EU/FR | Mistral Large 3（2025-12-02） | 70 | 欧洲最强，675B MoE 开源标杆，但综合实力与美中顶级仍有差距 |
| DeepSeek | CN | DeepSeek-V3.2（2025年中） | 83 | 成本革命发起者，开源 MoE 最具性价比，倒逼全行业降价，R2 推进中 |
| 阿里 Qwen | CN | Qwen3.6/Qwen3.7-Max（2026-05预告） | 82 | 中国开源生态最强，Arena Elo 中国最高（1449），多模态+商用许可完善 |
| 字节 Doubao | CN | Doubao 2.0（2026-02-14） | 78 | 用户规模全国第一（1.55亿周活），Agent 定向优化，但技术透明度低 |
| Moonshot Kimi | CN | Kimi K2.6（2026-04-20） | 80 | 1T MoE 开源 Agent 黑马，300智能体协同，但小公司独立支撑不确定性高 |
| 智谱 Z.ai | CN | GLM-5.1（2026-04-08） | 79 | 首家上市中国大模型公司，GPQA 86% 技术扎实，Agentic Engineering 定位清晰 |
| MiniMax | CN | MiniMax M3（2026-06-01） | 73 | BrowseComp 超越部分顶级，1M 上下文，但 benchmark 独立验证不足，需观察 |
| 百度 ERNIE | CN | ERNIE 5.1（2026-05-09） | 72 | 中文+搜索场景强，AIME 带工具全球第二，但通用能力与顶级有差距 |
| 腾讯 混元 | CN | Hunyuan T1（2026-02~03） | 68 | 混合架构特色，MMLU-PRO 全球第二，中文/创意强，但国际化影响力弱 |

---

## 五、数据可信度说明

| 数据类型 | 置信度 | 说明 |
|---------|-------|------|
| 发布时间（主要厂商官方） | 高 | 来自官网博客/API 文档 |
| Arena Elo 数值 | 中高 | 来自 Stanford 2026 AI Index 及 arena.ai，有截止日期限制 |
| Benchmark 数字（官方发布） | 中高 | 原厂发布，方法论不统一，存在"刷榜"风险 |
| Benchmark 数字（第三方评测） | 中 | 来自 BenchLM.ai、artificialanalysis.ai 等，有滞后 |
| Grok 4 GPQA/SWE 数字 | 低-中 | 部分来自泄露/非官方来源，标注"未证实" |
| MiniMax M3 benchmark | 低-中 | TechTimes 明确标注"前沿声称，未经独立验证" |
| 腾讯 Hunyuan 3.0 发布日期 | 低 | 仅为预告，截至调研日期未正式发布 |
| 打分（实力分） | 主观判断 | 综合多维度的分析师判断，非客观数值 |

---

## 六、参考来源（带日期）

- OpenAI: https://openai.com/index/introducing-gpt-5/ ; https://openai.com/index/introducing-gpt-5-5/ (2026-04-23)
- Anthropic: https://www.anthropic.com/claude/opus (Opus 4.8, 2026-05-28)
- Google: https://techstartups.com/2026/05/20/google-launches-gemini-3-5-flash-and-omni-world-model-at-i-o-2026-as-ai-race-with-openai-heats-up/
- Meta Llama 4: https://ai.meta.com/blog/llama-4-multimodal-intelligence/ (2026-04-05)
- xAI Grok 4.3: https://venturebeat.com/technology/xai-launches-grok-4-3-at-an-aggressively-low-price-and-a-new-fast-powerful-voice-cloning-suite/
- Mistral Large 3: https://mistral.ai/news/mistral-3/ (2025-12-02)
- DeepSeek API: https://api-docs.deepseek.com/updates
- Qwen: https://github.com/QwenLM/Qwen3.6 ; https://aimlapi.com/blog/qwen-3-6-series-alibabas-open-source-llm-revolution-in-2026
- Doubao 2.0: https://seed.bytedance.com/en/blog/seed2-0-正式发布 (2026-02-14)
- Kimi K2.6: https://rits.shanghai.nyu.edu/ai/moonshot-ai-releases-kimi-k2-6-with-256k-context-and-300-agent-swarms/
- GLM-5: https://huggingface.co/blog/mlabonne/glm-5 ; https://arxiv.org/html/2602.15763v1
- MiniMax M3: https://www.minimax.io/blog/minimax-m3 (2026-06-01)
- ERNIE 5.1: https://ernie.baidu.com/blog/posts/ernie-5.1-0508-release/
- Hunyuan T1: https://tencent.github.io/llm.hunyuan.T1/README_EN.html
- Stanford AI Index 2026: https://thenextweb.com/news/stanford-ai-index-2026-china-us-performance-gap (2026-04-13)
- Arena Leaderboard: https://arena.ai/leaderboard
- LLM 推理成本: https://epoch.ai/data-insights/llm-inference-price-trends ; https://a16z.com/llmflation-llm-inference-cost/
- Gartner 2030 预测: https://www.gartner.com/en/newsroom/press-releases/2026-03-25-gartner-predicts... (2026-03-25)
