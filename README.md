# robot-intel · 具身智能 / 脑机接口 / AI科学 情报台

每日自动追踪三大领域(+大厂LLM基模)的**论文**与**企业动态**,用 LLM 打**分量分**(对标领域基石校准),
产出一个静态 dashboard(`docs/`,可 GitHub Pages 直接 serve)。

## 看板(docs/index.html)
- 顶栏选**领域**(具身 / 脑机 / AI科学 / LLM基模)+ 切**📄论文 / 📰动态**
- 左栏:论文卡(分量排序 + teaser 配图)/ 企业卡(综合实力 + 多维强项 + 产品 + 近期动态)
- 右栏:各细分的**基石标尺榜** + 代表玩家 + 「谁更屌」横评
- 点卡片 → 右抽屉看完整详情

## 三级漏斗(论文打分)
`双源抓取(OpenAlex锁arXiv源 主力 + HF Daily 兜底)`
→ `免费锚点门(领域关键词必命中)`
→ `LLM 初筛(qwen-turbo 批量判相关性+分路线)`
→ `qwen-plus 深拆解 + 分量分(对标基石校准,自吹不算)`
→ `写库 / 导出 / 配图`

## 数据产物(docs/*.json)
| 文件 | 内容 | 生成 | 节奏 |
|---|---|---|---|
| data.json | 论文库(含基石+每日新论文) | `run.py` + `ingest_cornerstones.py` | 每日(新论文) |
| progress.json | 各领域基石标尺 + 玩家 + 横评 | `gen_progress.py` | 慢变(有突破时) |
| dynamics.json | 企业为中心动态(实力/产品/动态) | `gen_dynamics.py` | 慢变(有新闻时) |
| llm_base.json | 大厂基模横评 | `gen_llm.py` | 慢变 |
| assets/thumbs/ | 论文 teaser 配图(VLM 定位裁剪+压缩) | `fetch_thumbs.py` | 每日(新论文) |

## 跑
```bash
pip install -r requirements.txt          # pyyaml openai sentence-transformers PyMuPDF Pillow
echo 'QWEN_API_KEY=sk-...' > .env          # 或设环境变量
python daily.py                            # 每日编排:新论文 + 配图
# 慢变模块按需重跑:python gen_progress.py / gen_dynamics.py / gen_llm.py
python ingest_cornerstones.py              # progress 更新后把基石灌进库
cd docs && python -m http.server 8731      # 本地预览
```

## 部署(每日自动)
`.github/workflows/daily.yml` 已配:每天 cron 跑 `daily.py` → commit `data/`+`docs/` → GitHub Pages 自动刷新。
需在仓库 Settings 配 secret `QWEN_API_KEY`,并开启 Pages(source: `docs/`)。

## 配置驱动
路线/关键词/检索词/打分权重/LLM 选型全在 `config.yaml`——改配置即调系统,不改代码。
领域分 `domain`:embodied_ai / bci / ai_science(+ llm_base 走动态)。

## 取数为何用 OpenAlex
arXiv 老 API(`export.arxiv.org/api/query`)从云 IP(尤其 GitHub Actions)几乎必 **429**。
改用 **OpenAlex 锁预印本源**(`primary_location.source.id`)做关键词×日期检索:
为轮询而生、带 `mailto` 进礼貌池实测无 429,拿到的就是预印本本身,且**白送被引用数/venue/机构/abstract**。
- **多源**:arXiv(`S4306400194`,主力,key=arXiv号能抓图)+ **bioRxiv**(`S4306402567`,补脑机/蛋白冷门域,key=DOID自动跳过抓图)。要 medRxiv 在 `config.yaml: openalex.sources` 解开即可。
- **引用/venue 也走 OpenAlex**(DOI 批量,一发请求)→ 已**彻底移除 Semantic Scholar** 的逐篇限流。
HF Daily 降为兜底。

## 待办
- 产品/公司配图
- cron 失败/缩水时的**通知**(HF-only 缩退时能察觉)
- 最小**冒烟测试**防回归(如 generated_at、源 schema、arxiv_id 抽取)
