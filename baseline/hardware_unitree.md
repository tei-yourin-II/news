---
id: hardware_unitree
title: 人形硬件 / 机器人平台生态现状基线
date: 2026-06-03
confidence: medium-high
coverage: 2025-01 至 2026-06
note: 部分数字来自三方聚合站点（robozaps、botinfo.ai 等），已尽量追溯原始出处；标注"未证实"的为单一来源或无法核查的数据
---

# 人形硬件 / 机器人平台生态现状基线

> 建立时间：2026-06-03 | 覆盖期间：2025-01 – 2026-06 | 置信度：中高

---

## 1. 当前主流人形/机器人平台清单

### 1.1 宇树科技 (Unitree Robotics)

**G1**
- 身高 1.27 m，体重 35 kg，23–43 自由度（EDU Ultimate D 版带 6-DOF 灵巧手达 43 DOF）
- 行走速度 2 m/s；折叠后高度 690 mm
- 售价：基础版 $16,000；EDU 版 $43,900 起，最高配 $73,900（共 16 种配置）
- 2025 年出货 5,500+ 台（宇树官方财报数据，Caixin 2026-06 报道）；2026 年目标 20,000 台（未证实确认）
- 是全球学术界使用最广泛的全身人形机器人，EDU 版开放底层关节控制，含 ROS2/Python SDK
- 2026-03：宇树开源 UnifoLM-VLA-0 视觉-语言-行动模型
- 2026 年：G1-D 变体换装差速轮底盘（保留上半身），专为数据采集设计
- 日本航空（JAL）与宇树合作，G1 在东京羽田机场行李/货物处理试运行（截至 2028）——首个商业机场部署案例

**H1**
- 行走速度 3.3 m/s，定价约 $90,000（面向企业/科研机构）
- 在高难度运动研究（跑步、跳跃、翻跟头）场景被多篇 2024-2025 论文引用

**R1**（2025-07 发布，Bloomberg 2025-07-25 报道）
- 身高 1.21 m，体重 25 kg，26 自由度
- 售价 $5,900（起），Pro 版约 $16,000——是当时全球最便宜全尺寸人形
- 内置 8核 CPU+GPU，运行 UnifoLM 多模态模型；无灵巧手（仅夹爪）
- Time 杂志"2025 年最佳发明"入选
- 2026-04 开始出货（预订）

**G1-D / 轮式变体**（未证实正式型号，来自 2026 年报道）
- 双足腿替换为轮式底盘，上半身与 G1 相同，定位数据采集与 AI 训练工具

**GD01（载人机甲）**（未证实量产计划）
- 据 AiXZD 平台整理，宇树发布全球首款载人双足机甲，处于原型展示阶段

**Go2（四足机器人）**
- 宇树四足平台，已成为学术界最常用四足研究平台之一
- 官方提供 unitree_sdk2（GitHub 开源），支持 ROS2/Python/C++
- 非官方 go2_ros2_sdk（abizovnuralem）提供 WiFi+以太网双模接入
- 2025 年新增 IsaacLab RL 训练支持、Mujoco sim-to-real 工具链
- 有论文数量高于任何其他四足平台（2024-2025，未找到精确计数，judged by GitHub star 与 arXiv 引用频率）

**IPO 进展**（Caixin 2026-06-02）
- 2026-06-01 上交所审核委员会通过宇树 IPO 申请，计划在上交所科创板募资约 42 亿元（$6.2 亿）
- 计划估值 42 亿元（RMB），目标市值不低于 420 亿元
- 2025 年营收 16.99 亿元，净利润 2.78 亿元；人形机器人收入占比从 2023 年 1.9% 升至 2025 年前三季度 51.5%
- 2026 Q1 收入增速降至 68%，利润同比下滑 52.55%（IPO 招股书数据）

---

### 1.2 Tesla Optimus

| 指标 | 数值 / 状态 |
|------|------------|
| 身高 | 1.73 m（5'8"） |
| 体重 | 57 kg（125 lb） |
| 自由度 | Gen3：37 关节（比 Gen2 多 9 个） |
| 手部执行器 | Gen3：每手 25 个执行器，合计 50 个（Gen2 的 4.5 倍）；谐波+行星驱动 |
| 行走速度 | 1.2 m/s（Gen3）；可稳定行走 15° 坡面 |
| 目标价格 | $20,000–$30,000（大规模量产后，Tesla 官方目标，未实现） |

**2025 进展**
- 目标年产 5,000 台用于内部工厂（Tesla Q4 2024 财报）；实际产量未公开，外部估计在低千台量级（判断）
- 未完成此前宣布的"2025 年 10,000 台"对外目标（多家媒体 2026-04 报道）

**2026 进展**
- Gen3 Fremont 厂量产于 2026-01 启动（未证实；部分来源称 2026-07/08）
- 2026-04-22 Q1 财报：Musk 拒绝设定 2026 年产量目标
- Fremont 最后一条 Model S/X 产线 2026-05 关闭，改建为 Optimus 产线
- 实际 2026 产量：业界估计低千台至数千台（判断，非官方数据）
- 百万台/年目标：官方称"2026 年底冲击 100 万台/年产能率"——被多数分析师视为高度乐观（判断）

**来源**：robozaps.com；beginnersinai.org；standardbots.com；Tesla Q1 2026 earnings call

---

### 1.3 Boston Dynamics Atlas（电动版）

| 指标 | 数值 |
|------|------|
| 自由度 | 56 DOF，全关节电动（消除液压系统）|
| 举重能力 | 50 kg（110 lb） |
| 臂展 | 2.3 m |
| 关节旋转 | 支持 360° 旋转（关键关节） |
| 传感器 | LiDAR、立体相机、RGB 相机、深度传感器 |
| 估价 | $140,000–$150,000（第三方估计，未证实官方定价） |
| 电池 | 自主换电，支持不间断运行 |

**2025–2026 关键事件**
- 2024：彻底转型全电动（淘汰液压），重新设计底盘
- 2026-01-05（CES 2026）：Boston Dynamics CEO Robert Playter 发布量产版 Atlas；宣布 2026 年全部产能已被 Hyundai 与 Google DeepMind 预定
- 部署地点：韩国现代 Robotics Metaplant Application Center（RMAC）；Google DeepMind（AI 研究）
- Hyundai 计划：2028 年建成年产 30,000 台机器人工厂（Georgia 州）；2026 年已在 Georgia 工厂开始测试
- Google DeepMind 合作：集成 DeepMind 基础模型，据称新任务学习时间 < 1 天（未证实效果）
- 2027 年起向其他客户开放（Boston Dynamics 官方声明）

**来源**：bostondynamics.com；automate.org；The Register 2026-01-06；steelindustry.news

---

### 1.4 Figure AI

**Figure 02**（量产工业验证版）
- BMW Spartanburg 工厂（美国）：10 个月内辅助生产 30,000+ 辆 BMW X3；累计运行 1,250 小时；处理 90,000+ 零件（BMW 官方 press release）

**Figure 03**（2025-10 发布）
- 身高 5'8"（1.73 m），体重 61 kg，有效负载 20 kg
- 支持足部无线充电
- 定位量产工业级，全面重设计

**BMW Leipzig（欧洲首次）**（2026-02 公告）
- BMW Leipzig 工厂引入人形机器人，初步为 Hexagon Robotics 的 AEON（轮式人形，苏黎世）；Figure 03 评估中用于其他工况

**融资**（figure.ai 官网，2025-09）
- Series C 超过 $10 亿承诺资本，估值 $390 亿（post-money）
- BotQ 自建工厂：设计产能年产 12,000 台（第一年），最终目标 100,000 台/年

**来源**：figure.ai/news/series-c；bmwgroup.com；press.bmwgroup.com；iiot-world.com

---

### 1.5 Agility Robotics（Digit）

| 指标 | 数值 |
|------|------|
| 当前版本 | Digit（现役量产版）|
| 最大载重 | 现役约 16 kg；下代目标 50 lb（22.6 kg）|
| 主要客户 | Amazon（试点）、Toyota（RaaS）|

**2025–2026 关键事件**
- 自建工厂（俄勒冈州）产能：10,000 台/年（Agility 官方）
- 2026-02：与丰田汽车加拿大（Woodstock 工厂）签 RaaS 协议，7+ 台商业机器人支持 RAV4 物流——被认为是首个持续商业化人形部署案例（判断）
- 下代 Digit：目标 2026 年中至年底获 ISO 功能安全认证，首个获准与人协同（无物理隔离）的人形机器人（目标，未证实实现）

**母公司**：Amazon（2023 年战略投资 + 收购控股，未证实完全收购）；Toyota（战略伙伴）

**来源**：therobotreport.com；techcrunch.com；manufacturingdive.com

---

### 1.6 Apptronik Apollo

| 指标 | 数值 |
|------|------|
| 身高 | 5'8"（1.73 m）|
| 体重 | 160 lb（72.6 kg）|
| 有效负载 | 55 lb（25 kg）|
| 电池续航 | 4 小时 |
| 计算单元 | NVIDIA Jetson AGX Orin + Jetson Orin NX（275+ TOPS）|
| AI 平台 | NVIDIA GR00T 基础模型；Google DeepMind RT-2/RT-X |

**2025–2026 关键事件**
- 梅赛德斯-奔驰商业协议：Apollo 在梅奔柏林数字工厂（MBDFC）开展内部物流试点
- 合作代工：Jabil（全球最大电子代工之一）负责量产制造
- 2026-02/03：完成 $5.2 亿 Series A 扩展轮，总 Series A 超 $9.35 亿；估值 $55 亿（Google + 梅赛德斯领投）
- 商业规模交付目标：2027 年（当前为试点阶段）

**来源**：prnewswire.com；ifactoryapp.com；mercedes-benz.com；newatlas.com

---

### 1.7 1X Technologies（NEO）

| 指标 | 数值 |
|------|------|
| 产品 | NEO（消费级家用人形）|
| 价格 | $20,000 预购；或 $499/月订阅 |
| 工厂位置 | Hayward, California（美国） |
| 年产能 | 第一年 10,000 台 |

**2025–2026 关键事件**
- 2025-10：预购开放 5 天内首年全部产能售罄（公司自述，未独立核实）
- 2025-12（TechCrunch 报道）：与 EQT 达成协议，向其 300+ 投资组合公司（制造、仓储、物流）提供最多 10,000 台 NEO（2026–2030）
- 2025：Hayward 工厂开始 NEO 量产
- 目标：2027 年底累计 100,000 台
- 投资方：OpenAI（战略投资，金额未披露）

**来源**：therobotreport.com；techcrunch.com 2025-12-11；1x.tech；techfundingnews.com

---

### 1.8 智元机器人（AGIBOT）

| 指标 | 数值 |
|------|------|
| 主要产品 | 远征 A2（双足）、A2-W（轮式）、A2-D（差速轮）、灵犀 X1 |
| A2 身高 | 175 cm（未证实统一规格，来自多家媒体） |
| 认证 | 中国 CR、欧盟 CE-MD、CE-RED、美国 FCC（四区认证，全球首个同时具备） |

**2025 关键数据**
- 2025-01-06：第 1,000 台量产机器人下线（731 台双足 + 269 台轮式）
- 全年出货超 5,100 台（2025 年总结，yicai.com）
- 远征 A2 系列成本较 2025 年初下降约 50%（CEO 邓泰华披露）
- 2025-08：与富临精工合作，近百台 A2-W 落地富临精工工厂
- LG Electronics、韩国未来资产领投战略融资（2025-08-01）
- 2025-05：获京东及上海具身智能基金投资（C 轮预投）
- 估值：超 150 亿元（人民币）（2026 年初报道）

**2026 关键数据（截至 2026-06）**
- 累计出货突破 10,000 台（TechTimes 2026-06-02 报道）
- 与宇树并列形成"中国人形机器人双寡头"格局（媒体判断）
- AI 大模型：GO-1（ViLLA 架构 VLA 模型）

**来源**：yicai.com；stcn.com；chnfund.com；TechTimes 2026-06-02

---

### 1.9 优必选（UBTECH）

| 指标 | 数值 |
|------|------|
| 主要产品 | Walker S1、Walker S2、Walker X |
| Walker S2 自由度 | 41 DOF |
| 配套大模型 | 盘古大模型（华为） |

**2025–2026 关键数据**
- 2025：Walker S2 月产能超 300 台；全年交付超 500 台；产能突破 1,000 台
- 工厂实训：已进入汽车工厂（具体厂商未公开）
- 2025 年融资：$10 亿战略融资设施（UBTECH 官方，来源：tracxn.com）
- 2026 年产能目标：万台规模（公司规划）
- 已上市（香港联交所：9880.HK，2024 年）

**来源**：21jingji.com；ubtrobot.com；eastmoney.com

---

### 1.10 银河通用机器人（Galbot）

| 指标 | 数值 |
|------|------|
| 主要产品 | Galbot G1（移动操作机器人）|
| 设计理念 | 轮式底盘 + 人形躯干 + 双臂 |
| 电池续航 | 10 小时 |
| 抓取成功率 | 95–97%（多材质、多形态，公司自述） |
| 售价 | $87,000+（高端版本） |

**2025–2026 关键数据**
- 融资：2025-06 完成 $3 亿轮（Robot Report 报道）；2026-03 再完成 25 亿元人民币融资（国家人工智能产业基金、中国石化、中信集团、中国银行等领投）；累计融资超 $8 亿，估值约 $30 亿
- 最大工业订单：千台规模（具体客户未公开，ofweek.com 报道）
- 合作伙伴：CATL、Bosch、Toyota、Hyundai（探索部署，非正式量产）
- 2025 年春晚亮相（与魔法原子合作，品牌曝光）
- 具身大模型：GraspVLA

**来源**：therobotreport.com；cnr.cn；eet-china.com；ofweek.com

---

### 1.11 星动纪元（Robotera）

| 指标 | 数值 |
|------|------|
| 主要产品 | 星动 L7、星动 Q5 |
| 大模型 | ERA-42（端到端 VLA 具身模型）|
| 落地场景 | 物流、制造、商业服务 |

**2025–2026 关键数据**
- 2026-03-05：完成 10 亿元战略轮融资，估值突破 100 亿元（百亿独角兽）
- CES 2026 参展，展示 L7/Q5 两款人形机器人

**来源**：robotera.com；leaderobot.com；tmtpost.com

---

### 1.12 众擎机器人（ZQ Robotics）

| 指标 | 数值 |
|------|------|
| 主要产品 | PM01、T800 |
| PM01 售价 | 8.8 万元（统一定价，2024-12-26 发布）|
| T800 峰值扭矩 | 450 Nm（自研全栈一体化高爆发关节模组）|
| 技术自研范围 | 电机、减速器、控制伺服、扭力传感器、通信架构全栈 |

**来源**：leaderobot.com（CES 2026 报道）；stcn.com

---

### 1.13 傅利叶智能（Fourier Intelligence / Fourier）

| 指标 | 数值 |
|------|------|
| 主要产品 | GR-2 |
| 身高 | 175 cm |
| 体重 | 63 kg |
| 自由度 | 53 DOF |
| 单臂负载 | 3 kg |
| 电池 | 容量翻倍（vs GR-1），续航 2 小时；支持换电 |
| 关节架构 | 由并联改为串联（降低成本，方便调试） |

**2024 数据**：交付超 100 台（GR-2，来自 2024-09 发布时数据）

**来源**：finance.sina.com.cn（2024-09-26）；aibangbots.com

---

## 2. 执行器 / 关键零部件趋势与主要供应商

### 2.1 谐波减速器

| 供应商 | 背景 | 市场地位 |
|--------|------|---------|
| 绿的谐波（上交所：688017） | 中国龙头，国内市占率约 26%，全球 35%+ | 已通过 Tesla 供应链认证，为 Tesla 墨西哥工厂独家供货；为优必选 Walker X、傅利叶 GR-1 供货；2025H1 机器人关节相关业务营收同比增长 90% |
| 双环传动（002472）旗下浙江环动机器人 | 主产 RV 减速器 + 谐波减速器 | 国内重要供应商 |
| 国内合计已有 23+ 家谐波减速器供应商（艾邦机器人统计） | — | 行业进入竞争激烈阶段 |

### 2.2 行星滚柱丝杠（Planetary Roller Screw）

- 北特科技、恒立液压：已投入超 20 亿元布局，单台成本占比约 35%；Tesla Optimus 直线关节中该部件成本超 12 万元（来源：cnblogs.com，2025 年分析）
- 无锡新松（Wuzhou New Spring，未证实正式英文名）：反向行星滚柱丝杠主要供应商，用于髋关节、膝关节等高扭矩部位
- 绿的谐波：规划将正向/反向行星滚柱丝杠研发成果推向工程化
- 国内已有 38 家丝杠制造商（知乎盘点，2025 年）

### 2.3 集成关节模组

- 宇树科技：自研执行器模组，供自家产品
- 智元机器人指定供应商 Eyou Technology（眼又科技）：谐波关节模组、行星关节模组、人形线性关节模组
- HONPINE（苏州鸿品精密）：谐波/行星集成关节模组，内含无框力矩电机+编码器+制动器
- 众擎机器人：执行器全栈自研（电机/减速器/控制伺服/扭力传感器）

### 2.4 灵巧手

| 供应商 | 主要产品 | 地位 |
|--------|---------|------|
| INSPIRE-ROBOTS（灵巧手） | RH56DFQ/RH56BFX 系列，6 DOF，12 电机 | 2025 年单品交付突破 10,000 台；最广泛商用化中国灵巧手 |
| Wonik Robotics（韩国）| Allegro Hand v4.0，4 指，16 DOF，直驱力矩控制 | 全球学术界使用最广泛的研究级灵巧手（ROS/ROS2 兼容）|
| Unitree 自研 | G1 EDU 版 6-DOF 三指灵巧手 | 集成在 G1 EDU，带完整低层控制 |

**成本结构**：灵巧手占整机 BOM 约 31%，是最大单项成本构成（IDTechEx 报告，2026 年）

### 2.5 传感器

- 力传感器：六轴力矩传感器为关节控制必备，多为自研或 ATI/Bota Systems 进口
- 视觉：RGB-D 相机（Intel RealSense、Luxonis OAK-D 等）广泛使用
- IMU：双冗余六轴 IMU（宇树 R1 方案）

---

## 3. 2025–2026 重大产品发布与公司动态

| 时间 | 事件 | 来源 |
|------|------|------|
| 2025-07 | Unitree R1 发布，$5,900 起，全球最低价全尺寸人形 | Bloomberg 2025-07-25 |
| 2025-09 | Figure AI Series C 超 $10 亿，估值 $390 亿 | figure.ai 官网 |
| 2025-10 | Figure 03 发布（量产工业版） | 多家媒体 |
| 2025-10 | 1X NEO 开放预购，5 天售罄年度产能（公司自述） | techfundingnews.com |
| 2025-12 | 1X 与 EQT 签协议，最多 10,000 台 NEO 用于工业场景 | TechCrunch 2025-12-11 |
| 2025 全年 | 宇树 G1 出货 5,500+；智元出货 5,100+；优必选交付 500+ | Caixin/yicai |
| 2026-01-05 | Boston Dynamics CES 2026 发布量产 Atlas，全年产能锁定 Hyundai + Google DeepMind | automate.org；The Register |
| 2026-02 | 1X 加州 Hayward 工厂正式开始 NEO 量产 | therobotreport.com |
| 2026-02 | Agility 与 Toyota Motor Manufacturing Canada 签 RaaS，7+ 台 Digit 支持 RAV4 物流 | therobotreport.com |
| 2026-02 | BMW Leipzig 启动欧洲首个人形机器人量产试点（含 Hexagon AEON；Figure 03 评估中）| bmwblog.com；press.bmwgroup.com |
| 2026-03 | 银河通用完成 25 亿元人民币新轮融资 | cnr.cn；therobotreport.com |
| 2026-03 | 星动纪元完成 10 亿元战略轮，估值破 100 亿元 | tmtpost.com |
| 2026-03 | Apptronik 完成 $5.2 亿 Series A 扩展轮，总融资超 $9.35 亿，估值 $55 亿 | ifactoryapp.com |
| 2026-03 | 宇树开源 UnifoLM-VLA-0 视觉-语言-行动模型 | 多家媒体 |
| 2026-04 | Unitree R1 开始出货（预购交付）| therobotreport.com |
| 2026-05 | Tesla Fremont 关闭最后 Model S/X 产线，改建 Optimus 产线 | beginnersinai.org |
| 2026-06-01 | 宇树 IPO 获上交所审核委员会通过（首个具身 AI A 股上市）| Caixin 2026-06-02；TechNode 2026-06-02 |
| 2026-06-02 | 智元累计出货突破 10,000 台 | TechTimes 2026-06-02 |

---

## 4. 融资 / 商业化进展

### 4.1 重大融资汇总（2025–2026）

| 公司 | 金额 | 估值 | 时间 | 主要投资方 |
|------|------|------|------|-----------|
| Figure AI | >$10 亿（Series C）| $390 亿 | 2025-09 | 未披露详细投资方 |
| Apptronik | $5.2 亿（Series A 扩展）| $55 亿 | 2026-03 | Google、Mercedes-Benz |
| 银河通用 | 25 亿元人民币（约 $3.5 亿）| ~$30 亿（估值）| 2026-03 | 国家 AI 产业基金、中国石化、中信、中国银行 |
| 星动纪元 | 10 亿元人民币 | >100 亿元 | 2026-03-05 | 未完全披露 |
| UBTECH | $10 亿战略融资设施 | — | 2025 | — |
| 智元机器人 | 多轮（总估值 150 亿元+）| 150 亿元（RMB）| 2025 | 京东、上海具身智能基金、LG Electronics、Mirae Asset |

**2026 Q1 中国具身智能赛道**：披露融资超 50 起，累计约 200 亿元，同比增长约 60%，创历史新高

**2026 总体**：全球人形机器人公司 2026 年前三个月融资 $23.7 亿（11 轮），较 2025 年增长 288%（来源：tracxn.com，须注意聚合数据口径差异）

### 4.2 商业化量产进展

| 公司 | 量产/出货状态 | 主要工厂/客户 |
|------|-------------|-------------|
| 宇树科技 | 2025 出货 5,500+（全球最多）| 自建；Haneda 机场（JAL）|
| 智元机器人 | 2025 出货 5,100+；2026-06 突破 10,000 | 自建；富临精工等工厂 |
| Agility Robotics | 10,000 台/年产能（2025 建成）；7+ 台商业部署 | 俄勒冈工厂；Toyota Canada |
| 1X Technologies | 2026 开始量产交付 10,000 台目标 | Hayward, CA；EQT 投组公司 |
| Boston Dynamics | 2026 量产 Atlas，产能全预定 | 自建；Hyundai RMAC；Google DeepMind |
| Figure AI | 12,000 台/年（BotQ 设计产能，第一年）| BotQ 自建工厂 |
| Tesla Optimus | 低千台（2025 估计）；2026 量产扩产中 | Fremont 工厂 |
| 优必选 | 2025 交付 500+；产能突破 1,000 台/年 | 汽车工厂实训 |

---

## 5. 作为研究平台的生态

### 5.1 学术界广泛使用的平台

**宇树 G1/H1（最广泛全身人形研究平台）**
- G1 EDU 版 2025 年批量发货至全球高校实验室；据 RoboticsCenter Silicon Valley（2026 年评测），是 2026 年"大学里数量最多的全身人形机器人平台"
- EDU 版开放底层关节力矩控制；含 Python API、ROS2 接口、MuJoCo/IsaacLab sim 资产
- arXiv 上已有多篇以 G1/H1 为实验平台的论文（具体计数未核实；2024-2025 年高度活跃）
- 典型研究类型：全身操控、强化学习步态控制、灵巧操作

**宇树 Go2（最广泛四足研究平台）**
- unitree_sdk2（官方，GitHub 开源）；go2_ros2_sdk（非官方，广受使用）
- ROS2 Jazzy × Gazebo Harmonic 完整集成包（2025 年 ROS Discourse 发布）
- IsaacLab RL 支持：速度控制任务、复杂地形训练
- Agent SDK（AI 代理控制）：grasp-lyrl/unitree_go2w_agent_sdk

**Wonik Allegro Hand**
- 全球使用最广泛的研究级灵巧手，16 DOF，直驱力矩控制，ROS/ROS2 兼容

### 5.2 开源生态

| 项目 | 描述 | 维护方 |
|------|------|--------|
| unitree_sdk2 | 官方 SDK，支持 G1/H1/R1/Go2/B2 | 宇树官方 |
| go2_ros2_sdk | 非官方 ROS2 SDK（WiFi+以太网）| 开源社区 |
| LeRobot（HF）| Python 原生硬件无关接口，标准化 LeRobotDataset 格式 | Hugging Face |
| LeRobot Humanoid | $2,500 3D 打印开源人形（Pollen Robotics 架构，含 sim-to-real 工具链）| Hugging Face（2025-04 收购 Pollen）|
| Unitree IsaacLab | RL 训练环境，适配 Go2/G1 等 | 宇树官方 |
| UnifoLM-VLA-0 | 开源 VLA 模型（自然语言 → 家务操作）| 宇树官方，2026-03 |

---

## 6. 近 6–12 个月趋势（2025-06 至 2026-06）

### 6.1 量产进展
- **"量产元年"已成立**：宇树 G1（5,500+）、智元 A2（5,100+）均在 2025 年完成千台级出货；行业共识是 2025 年是中国人形机器人量产元年
- **工厂部署从试验转向商业**：Agility-Toyota 属于持续商业 RaaS；Figure-BMW Spartanburg 10 个月实际生产；这些是真实产出，不再是 demo
- **IPO 加速**：宇树 2026-06-01 通过 A 股审核；超 20 家具身智能企业处于 IPO 倒计时（2026 年新浪财经）

### 6.2 成本趋势
- IDTechEx（2026-05）：全球平均售价从 2024 年的 $114,700 预计降至 2030 年约 $37,000（-68%）
- 智元 A2：成本 2025 年内下降约 50%（CEO 自述）
- Unitree R1：$5,900 是当前全球最低全尺寸人形价格基准（2025-07）
- 高利用率工业场景：2026 年运营成本已可降至约 $5/小时（IDTechEx 预测）；回本周期可缩短至约 6 个月（高利用率假设，IDTechEx 2026-05）

### 6.3 格局判断（分析师判断，非事实）
- 中国："宇树 + 智元"双寡头格局初步形成（TechTimes 2026-06-02 用语）；银河通用、星动纪元、优必选等紧随
- 美国：Boston Dynamics（工业顶端）、Figure（中端工业）、Agility（商业部署先发）、Tesla（规模野心最大但产能最不确定）
- 价格区间分层清晰：$5,900（R1）→ $16,000（G1）→ $20,000（NEO）→ $87,000–$90,000（H1/Galbot）→ $140,000+（Atlas）

---

## 7. 开放问题 / 瓶颈

### 7.1 硬件可靠性
- 长时工业运行的 MTBF（平均无故障时间）数据极少公开；Figure-BMW 1,250 小时是目前最具说服力的公开数据，但仍属早期
- 关节密封、防尘/防水、热管理在非受控环境下表现未经充分验证

### 7.2 成本结构
- 灵巧手占 BOM 约 31%，是最大单项成本（IDTechEx）
- 精密执行器（行星滚柱丝杠）：全球高精度供应商不足 10 家，产能扩张速度制约整机规模化
- 电池：连续工业工况下 2–4 小时续航是共性限制（Apptronik 4h；GR-2 2h）

### 7.3 供应链
- 行星滚柱丝杠：中国尚未在高精度品种形成领先优势；主要高端来源仍依赖欧洲（Rollvis 等）（未证实，判断）
- 谐波减速器：中国已有 23+ 供应商，但高端精度品种的良率和一致性仍低于日本 Harmonic Drive AG/Nabtesco（判断）
- McKinsey 报告：执行器供应链是人形机器人从千台量级跨越到百万台的最大单一约束

### 7.4 智能化
- 感知-决策-执行闭环在非结构化场景（家庭、建筑）仍不稳定
- VLA/端到端模型泛化能力：实验室演示 ≠ 工厂/家庭可靠性，数据飞轮尚未形成正反馈（行业判断）

### 7.5 商业模式
- RaaS 模式兴起（Agility-Toyota）但经济模型尚待验证
- 消费级（1X NEO、R1）市场接受度尚未被实际销售规模证明（均处于预购/早期交付阶段）

---

## 关键平台/公司（结构化）

> 格式：公司/平台 | 最新型号 | 关键规格 | 状态 | 出处

- 宇树科技（Unitree）| G1 / G1-D / R1 / H1 | G1: 35kg, 23–43 DOF, $16K–$73.9K; R1: 25kg, 26 DOF, $5,900 | G1 量产出货（2025年5,500+台）；R1 2026-04 开始交付 | Caixin 2026-06-02；Bloomberg 2025-07-25
- Tesla Optimus | Gen3（Optimus V3）| 57kg, 37 关节, Gen3 手部 50 执行器, 目标$20K–$30K | Fremont 量产启动（2026-01/07不确定），实际产量低千台 | Tesla Q1 2026 earnings；beginnersinai.org
- Boston Dynamics | Atlas（电动版）| 56 DOF, 50kg 举重, 2.3m 臂展, 估价$140K–$150K | 量产（2026年全年产能锁定给 Hyundai + Google DeepMind）| automate.org；The Register 2026-01-06
- Figure AI | Figure 03 | 61kg, 20kg 有效负载, 足部无线充电, 估价未公开 | 量产筹备；BMW Spartanburg 试点完成（Figure 02：30,000辆车） | bmwgroup.com；figure.ai
- Agility Robotics | Digit（现役）| 16kg 负载, 4小时续航, RaaS 模式 | 商业量产（10,000台/年产能），Toyota Canada 首个持续商业部署 | therobotreport.com；manufacturingdive.com
- Apptronik | Apollo | 72.6kg, 25kg 负载, 4h 续航, NVIDIA Jetson AGX Orin | 试点阶段（Mercedes-Benz MBDFC）；量产目标2027 | prnewswire.com；ifactoryapp.com
- 1X Technologies | NEO | $20,000 / $499/月, 10,000台/年设计产能 | 量产交付开始（2026），首年产能据称售罄 | therobotreport.com；techcrunch.com 2025-12-11
- 智元机器人（AGIBOT）| 远征 A2 / 灵犀 X1 / A2-W / A2-D | 175cm（未证实），通过四区认证，成本2025年降幅50% | 量产出货（2025年5,100+台；2026-06达10,000台）| yicai.com；TechTimes 2026-06-02
- 优必选（UBTECH）| Walker S2 / Walker S1 / Walker X | 41 DOF, 配套盘古大模型, 月产300+台 | 量产（2025全年交付500+台），已进入工厂实训 | 21jingji.com；eastmoney.com
- 银河通用（Galbot）| Galbot G1 | 轮式底盘, 10h 续航, 抓取成功率95–97%, $87K+ | 商业出货（千台级工业订单），30城店面运营 | therobotreport.com；cnr.cn
- 星动纪元（Robotera）| 星动 L7 / 星动 Q5 | ERA-42 VLA 大模型, 物流/制造落地 | 研发+小批量出货，2026-03 估值破100亿 | robotera.com；tmtpost.com
- 众擎机器人（ZQ Robotics）| PM01 / T800 | PM01 售价8.8万元；T800 峰值扭矩450Nm，全栈自研 | 小批量销售（PM01 2024-12 开始销售）| leaderobot.com；stcn.com
- 傅利叶智能（Fourier Intelligence）| GR-2 | 175cm, 63kg, 53 DOF, 单臂3kg负载, 2h续航, 可换电 | 小批量出货（2024年交付100+台）| finance.sina.com.cn 2024-09-26；aibangbots.com
- Unitree Go2（四足）| Go2 / Go2-W | 四足平台，ROS2+Python SDK，开源社区活跃 | 量产出货，学术界最广泛四足研究平台 | github.com/unitreerobotics；support.unitree.com
- Wonik Robotics（韩国）| Allegro Hand v4.0 | 4指, 16 DOF, 直驱力矩控制, ROS/ROS2 | 量产研究级灵巧手，全球学术使用最广 | marketresearchreports.com
- INSPIRE-ROBOTS（灵巧手）| RH56DFQ / RH56BFX | 6 DOF, 12 电机, 0.2mm 定位精度 | 量产（2025年单品出货突破10,000台）| en.inspire-robots.com；rbtx.com
- 绿的谐波（Green Harmonic，688017）| 谐波减速器 / 行星滚柱丝杠 | 国内市占率26%，全球35%+，通过Tesla认证 | 量产，为Tesla/优必选/傅利叶供货 | cnblogs.com；aibangbots.com
- Hugging Face / Pollen Robotics | LeRobot Humanoid | $2,500 3D打印开源人形，含sim-to-real工具链 | 开源研究平台（2025-04 HF收购Pollen Robotics）| huggingface.co；interestingengineering.com
