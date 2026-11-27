# 事后验证 2026-11-27

样本:入库 90~30 天前的论文 2751 篇。其中真正同批排名的 0 篇,其余档位由旧分量分换算。

后来的关注度 = 被引×系数 + star×系数 + 会议/奖项加成(不含 HF 点赞),系数见 agent/weights.yaml。

## embodied_ai(1958 篇)

内容分与后来关注度的秩相关 ρ = 0.17;HF 点赞(头几天就定型)与后来关注度 ρ = 0.30

| 档位 | 篇数 | 后来有任何信号的占比 | 后来关注度中位数 | 进后来前 10% 的占比 |
|---|---|---|---|---|
| S | 120 | 75% | 10.0 | 28% |
| A | 384 | 59% | 4.0 | 15% |
| B | 1454 | 46% | 0.0 | 9% |

**当时排在 B、后来关注度最高的(漏判)**

- 256 票 · 2609.24170 · An Unexpected Robot Policy: Early Evaluations of GPT-6 Astra on RoboDo(引 64 / ★ 0 / -)
- 152 票 · 2609.12541 · Agent as Policy for Robotic Manipulation(引 38 / ★ 0 / -)
- 137 票 · 2609.19138 · In-Context Robot Learning with VLM Agents(引 27 / ★ 374 / -)
- 137 票 · 2609.10540 · Programmable World Model(引 29 / ★ 212 / -)
- 122 票 · 2610.01939 · Fewer Tokens, Better Action: GPT-6 Astra Robot Agents with 14% Higher (引 28 / ★ 0 / -)
- 120 票 · 2608.29910 · Matrix-Game 3.5: Enhancing Real-Time Streaming Interactive World Model(引 30 / ★ 0 / -)
- 92 票 · 2609.27308 · EmbodiedSWE: Coding Agents for Long Horizon Dexterous Robotics(引 23 / ★ 0 / -)
- 70 票 · 2610.23479 · HexaShell: A Thin Harness for Exploring the Limits of VLM Agents as Ro(引 10 / ★ 402 / -)

**当时排在 S、至今没有任何后续信号的:30 篇**(列前 8)

- 2610.18711 · Steertuning Policies from a Few Human Videos
- 2609.39403 · IronMind: Scaling Humanoid Dexterous Manipulation via Camera-Space Ego
- 2610.28626 · UniWALM: Unified World Action Language Model for Embodied Robot Contro
- 2609.37677 · Learning Expressive and Compositional Motion Representation via Spectr
- 2610.25600 · Vector-Quantized World Model: Latent Feedback Motion Planning for Robo
- 2609.18455 · ForwardDLO: Model-Based Bimanual Shape Matching of Unconstrained Defor
- 2608.27033 · Riemann-1.0: An Embodied World Action Model for Physical AI
- 2610.04765 · PatternDex: Learning Interaction Patterns to Guide Reinforcement Learn

**按特征分组的后来关注度中位数 / 有信号占比**

- reproducibility → project-page: 0 / 49%(n=1107) ; none: 0 / 45%(n=369) ; code-only: 4 / 57%(n=274) ; code+model+data: 8 / 64%(n=157) ; unknown: 4 / 52%(n=50)
- sim2real_status → sim-only: 0 / 50%(n=475) ; multi-embodiment: 4 / 56%(n=370) ; small-real: 0 / 46%(n=335) ; n/a: 1 / 52%(n=334) ; deployed: 0 / 49%(n=239) ; real-robot: 0 / 47%(n=189)
- org_type → unknown: 0 / 49%(n=869) ; university: 0 / 48%(n=803) ; company: 5 / 66%(n=197) ; institute: 0 / 51%(n=82)

## bci(285 篇)

内容分与后来关注度的秩相关 ρ = 0.16;HF 点赞(头几天就定型)与后来关注度 ρ = 0.26

| 档位 | 篇数 | 后来有任何信号的占比 | 后来关注度中位数 | 进后来前 10% 的占比 |
|---|---|---|---|---|
| S | 20 | 25% | 0.0 | 15% |
| A | 56 | 23% | 0.0 | 18% |
| B | 209 | 14% | 0.0 | 13% |

**当时排在 B、后来关注度最高的(漏判)**

- 10 票 · 2610.30364 · Gate-Based Feature Importance in Simulation-Based Inference for EEG: A(引 0 / ★ 0 / NeurIPS 2026)
- 10 票 · 2610.23620 · GRAFT-EEG: Gauge-Aware Physical Field Transport for Cross-Dataset Moto(引 0 / ★ 0 / ICLR 2027)
- 10 票 · 2610.10571 · SPERA: Spherical Prior EEG Foundation Model with Geometry- and Frequen(引 0 / ★ 0 / NeurIPS 2026)
- 10 票 · 2610.14497 · DEFT: Disentanglement-Enhanced Fine-Tuning for EEG Foundation Models(引 0 / ★ 0 / NeurIPS 2026)
- 10 票 · 2609.13991 · Mind2Cloud: EEG-to-Point Cloud Generation with Two-Granularity Diffusi(引 0 / ★ 0 / ECCV 2026)
- 10 票 · 2610.01794 · Continuous Conditioning of VLAs with Augmenting EMG and Visual Task De(引 0 / ★ 0 / IROS 2026)
- 10 票 · 2610.10850 · Similar Predictive Fit but Different Latent Dynamics: Characterizing L(引 0 / ★ 0 / NeurIPS 2026)
- 8 票 · 2610.09355 · Multimodal LLMs Can Learn to Read Brain Signals: A Vision--Language Mo(引 2 / ★ 0 / -)

**当时排在 S、至今没有任何后续信号的:15 篇**(列前 8)

- 2608.24597 · Taming foundation model with invariance-oriented pre-training for broa
- 10.64898/2026.09.26.754608 · STAMP-LME: A spatiotemporal surface-mapping framework for population-l
- 2609.36087 · PHASE: A Physiology-Guided Hierarchical Foundation Model for Intracran
- 2610.28422 · How Much of Cross-Subject EEG Emotion Recognition Is Stimulus Memoriza
- 2610.20942 · How large an effect would we have seen? Positive controls, detection f
- 2610.32950 · CoupleFlow: Null-Calibrated Auditory Attention Decoding With Time-Lock
- 2610.17507 · Merit: Making every modality earn its contribution in multimodal atten
- 10.64898/2026.08.21.746318 · SPOUT: An open-source hardware and software platform to study decision

**按特征分组的后来关注度中位数 / 有信号占比**

- reproducibility → project-page: 0 / 17%(n=162) ; none: 0 / 5%(n=57) ; code-only: 0 / 29%(n=35) ; code+model+data: 0 / 26%(n=19) ; unknown: 0 / 17%(n=12)
- sim2real_status → n/a: 0 / 17%(n=276)
- org_type → university: 0 / 19%(n=132) ; unknown: 0 / 16%(n=120) ; institute: 0 / 7%(n=28)

## ai_science(508 篇)

内容分与后来关注度的秩相关 ρ = 0.14;HF 点赞(头几天就定型)与后来关注度 ρ = -0.02

| 档位 | 篇数 | 后来有任何信号的占比 | 后来关注度中位数 | 进后来前 10% 的占比 |
|---|---|---|---|---|
| S | 31 | 23% | 0.0 | 23% |
| A | 100 | 14% | 0.0 | 14% |
| B | 377 | 9% | 0.0 | 8% |

**当时排在 B、后来关注度最高的(漏判)**

- 46 票 · 2609.05818 · Agentic BAIM-LLM Evaluation (ABLE): Benchmarking LLM Use of Protein De(引 9 / ★ 0 / NeurIPS 2026)
- 14 票 · 2610.26009 · ProtGlycanDock: Towards Accurate Protein-Glycan Docking with Tailored (引 1 / ★ 0 / NeurIPS 2026)
- 14 票 · 2610.04475 · VCLMU: Mechanism-Centric Virtual Cell World Modeling for Perturbation (引 1 / ★ 0 / NeurIPS 2026)
- 10 票 · 2608.31009 · Language-Informed Flow Matching for Trend-Guided Structure-Based 3D Mo(引 0 / ★ 6 / EMNLP 2026)
- 10 票 · 2609.08305 · FPicker: Topology-Guided Evolution for Filament Tracing in Low-SNR Mic(引 0 / ★ 3 / ECCV 2026)
- 10 票 · 2610.01891 · RipplePLM: Structural and Property Decoupling for Protein Mutation Eff(引 0 / ★ 0 / NeurIPS 2026)
- 10 票 · 2610.15284 · FragFlex: Fragment-Based Flexible Molecular Generation for Exploring V(引 0 / ★ 0 / NeurIPS 2026)
- 10 票 · 2610.04740 · Toward a Locally Deployable Agentic Co-Scientist: Small-Model Planning(引 0 / ★ 0 / NeurIPS 2026)

**当时排在 S、至今没有任何后续信号的:24 篇**(列前 8)

- 10.64898/2026.10.05.756407 · Joint protein, mRNA and DNA sequence design and optimization with nucl
- 10.64898/2026.10.21.760573 · Design of full-length agonist and antagonist antibodies for hard targe
- 10.64898/2026.09.21.749940 · A Community-Driven Single-Cell PBMC Reference Integrating Landmark Dat
- 10.64898/2026.08.22.746371 · A multi-tissue epigenomic atlas links the sheep non-coding genome to d
- 10.64898/2026.09.12.751118 · Latent generative search unlocks de novo design of untapped biomolecul
- 10.64898/2026.09.04.749355 · BOTANIC-1: a series of long-context plant genomic foundation models in
- 10.64898/2026.09.08.749775 · Site-resolved spatial and structural interactome of a human cell
- 10.64898/2026.10.01.756017 · Designing enzymes for new-to-nature chemistry and non-natural substrat

**按特征分组的后来关注度中位数 / 有信号占比**

- reproducibility → project-page: 0 / 8%(n=315) ; code-only: 0 / 17%(n=78) ; code+model+data: 0 / 21%(n=53) ; none: 0 / 4%(n=45) ; unknown: 0 / 24%(n=17)
- sim2real_status → n/a: 0 / 10%(n=502)
- org_type → university: 0 / 9%(n=205) ; unknown: 0 / 10%(n=176) ; institute: 0 / 13%(n=103) ; company: 0 / 33%(n=18)
