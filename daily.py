#!/usr/bin/env python3
"""每日编排(cron/GitHub Actions 入口):增量刷新「每日变」的模块。
  1. run.py        —— 抓新论文(双源)→ 三级漏斗 → 基石校准打分 → 写库/导出
  2. fetch_thumbs  —— 给当天新论文补 teaser 配图(幂等,只抓没图的)

「慢变」模块(dynamics.json 企业评估 / progress.json 领域基石 / llm_base.json 基模)
不每天重算 —— 它们只在有新突破/新闻时更新(各自 gen_*.py 脚本,接入 RSS 后由 #7 触发)。
"""
import run
import fetch_thumbs
import progress_update
import gen_news
import gen_graph


def _safe(name, fn):
    try:
        fn()
    except Exception as e:
        print(f"{name} 出错(不阻断): {e}")


def main():
    print("=== [1/5] 论文管线 ===")
    run.main()
    print("=== [2/5] 领域进展门控(大突破才动基石榜)===")
    _safe("门控", progress_update.main)
    print("=== [3/5] 新论文配图 ===")
    _safe("配图", fetch_thumbs.main)
    print("=== [4/5] 企业/基模 RSS 新闻 ===")
    _safe("新闻", gen_news.main)
    print("=== [5/5] 重建知识图谱 ===")
    _safe("图谱", gen_graph.main)


if __name__ == "__main__":
    main()
