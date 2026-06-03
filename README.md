# robot-intel · 具身智能 / 脑机接口 / AI科学 情报台

每日自动追踪三大领域(+大厂LLM基模)的**论文**与**企业动态**,用 LLM 打**分量分**(对标领域基石校准),
产出一个静态 dashboard(`docs/`,可 GitHub Pages 直接 serve)。

## 看板(docs/index.html)
- 顶栏选**领域**(具身 / 脑机 / AI科学 / LLM基模)+ 切**📄论文 / 📰动态**
- 左栏:论文卡(分量排序 + teaser 配图)/ 企业卡(综合实力 + 多维强项 + 产品 + 近期动态)
- 右栏:各细分的**基石标尺榜** + 代表玩家 + 「谁更屌」横评
- 点卡片 → 右抽屉看完整详情

## 三级漏斗(论文打分)
`双源抓取(arXiv关键词检索 + HF Daily,互为兜底)`
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

## 待办
- 企业/基模动态接 **RSS 每日活水**(PR Times / 36氪 / The Robot Report)
- **领域进展门控更新**(大突破才动基石榜,LLM 判定)
- 产品/公司配图;bioRxiv 源补脑机/蛋白冷门域
