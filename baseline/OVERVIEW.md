---
title: 具身智能 + 脑机接口 领域基线总览
generated: 2026-06-03
note: 由 8 份后台调研 baseline 汇总。各分支详情见同目录对应 .md。这是"锚",日更论文长在其上。
confidence: 综述级,具体数字/arxiv_id 以各分支文档为准;不确定项各文档已标注
---

# 具身智能 + 脑机接口 · 领域基线总览（2026-06）

本系统追踪 **两大领域**：🤖 具身智能（6 分支）+ 🧠 脑机接口（4 分支），并横向跟踪 🌏 中日美企业动态。
以下为截至 2026-06 的现状锚点；每天新论文/动态在此之上增量生长。

---

## 🤖 具身智能（domain: embodied_ai）

| 分支 | 文档 | 关键论文 | 一句话现状 |
|---|---|---|---|
| **VLA** 视觉-语言-动作 | [vla.md](vla.md) | 20 | 三范式（自回归/扩散/流匹配）确立，双系统架构（GR00T N1、Helix）成工业共识；π0.5 首次陌生家庭长时域；合成数据规模化直接 sim2real；在线 RL 后训练补 OOD |
| **世界模型 / WAM** | [world_model.md](world_model.md) | 30 | 五路线（Dreamer 隐动力学 / 视频预测 / Genie 交互环境 / Cosmos 物理AI / WAM）；**Cosmos 3 已 2026-06-01 发布**；2026 主线是"WAM 化"——世界模型×VLA 融合，用于合成数据/RL后训练/离线评估 |
| **全身控制 / 人形** | [whole_body_control.md](whole_body_control.md) | 30 | Loco-Manipulation 端到端融合；人类视频当免费数据源；行为基础模型兴起；跌倒恢复工程化（93%+）；Unitree G1/H1 成学术主力台 |
| **灵巧操作** | [dexterous_manipulation.md](dexterous_manipulation.md) | 32 | 人类大规模数据预训练（EgoDex 829h）现 log-linear scaling law；与 VLA 深度融合；**触觉从可选变必需**；零样本力控部署；中国产业链崛起（因时交付破万） |
| **Sim2Real / 数据** | [sim2real_data.md](sim2real_data.md) | 24 | 大规模真机集（OXE 100万轨迹 / DROID / AgiBot World）+ 低成本遥操作 + 仿真合成 + **世界模型造数据**；扩机体数 > 扩数据量；格式向 LeRobot v3 + RLDS 收敛 |
| **硬件 / Unitree** | [hardware_unitree.md](hardware_unitree.md) | 18 | 2025 中国"量产元年"：宇树 G1 出货 5500+、智元破万；宇树 R1 $5,900 刷新最低价；BD 量产 Atlas；瓶颈在精密执行器（行星滚柱丝杠供应商<10 家）与灵巧手 |

---

## 🧠 脑机接口（domain: bci）

详见 [bci.md](bci.md)（细分分支地图 + 19 成果 + 关键玩家）。

| 路线 | 覆盖 | 现状要点 |
|---|---|---|
| **神经解码 / BCI 核心** `bci_neural_decoding` | 运动/语音/视觉解码、侵入式/ECoG | 高性能语音神经假肢、handwriting BCI 等 Nature 级里程碑；NeuroXess 全球首例普通话语音+运动同步解码 |
| **神经基础模型 / NeuroAI** `bci_foundation_models` | Transformer 解码神经信号、跨受试者预训练 | CBraMod、MindEye2、NDT3 等；脑信号 foundation model 兴起（与本系统 AI 主线高度相关） |
| **BCI × 具身（重点）** `bci_embodied_robot` | 脑控机器人/假肢、脑脊接口、共享自主 | **两域连接点**：Neuralink CONVOY 脑控机械臂、Nature MI 2025 "AI copilot BCI"、脑脊接口行走恢复 |
| **非侵入式 / EEG** `bci_noninvasive_eeg` | 运动想象/SSVEP/P300、穿戴式 | MOABB 基准、EEG→图像重建、Cybathlon；消费级与临床并进 |

> ⚠️ BCI 顶尖工作多发 Nature/Science/bioRxiv 而非 arXiv，daily 管线（arXiv+HF）对 BCI 覆盖有限，数量会**慢热**；未来可补 bioRxiv / PubMed 源。

---

## 🌏 中日美企业动态（横切）

详见 [companies_cn_jp_us.md](companies_cn_jp_us.md)（42 企业 + 36 时间线事件）。

| | 具身智能 | 脑机接口 | 打法 |
|---|---|---|---|
| 🇨🇳 中国 | 宇树(出货全球第一,IPO过会)、智元、银河通用(25亿融资)、星动纪元… | 脑虎、博睿康(**全球首张植入式BCI注册证**)、强脑 | **量产 + 国资入场** |
| 🇺🇸 美国 | Figure($390亿估值)、Tesla Optimus、Agility(唯一真量产)、Physical Intelligence、Skild AI($14亿) | Neuralink($127亿)、Synchron、Precision、Paradromics | **资本最大 + 技术领先** |
| 🇯🇵 日本 | Toyota/TRI、FANUC/安川/川崎（**集体绑定 NVIDIA**） | 几无商业公司，国研机构为主 | **放弃整机，走核心零部件 + Physical AI 赋能存量工业机器人** |

---

## 🔭 跨领域主旋律（2026 上半年）

1. **世界模型 × VLA 融合（WAM）**——世界模型不再只做规划/评估，开始造数据、做后训练，成为具身智能新范式主线。
2. **数据瓶颈多管齐下**——人类视频、低成本遥操作、仿真合成、世界模型生成，四路并进；"扩机体 > 扩数据"成共识。
3. **触觉与灵巧成刚需**——精细接触任务推动触觉从可选变必需，灵巧手成人形 BOM 与产业链焦点。
4. **中国量产领先 / 美国资本技术 / 日本零部件**——三国错位竞争格局清晰。
5. **BCI×具身是两域接口**——脑控机器人、神经假肢、共享自主，是脑机接口与具身智能的天然连接点，也是本系统把两域并到一张图的依据。

---

*下一步：按各 baseline 的 `关键论文(结构化)` 与 config seed 的 arxiv_id 做 `--backfill-seeds`，把这些经典作为知识图谱**主干节点**入库（当前被 arXiv 限流暂缓）。*
