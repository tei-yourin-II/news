#!/usr/bin/env python3
"""本地小红书工作台服务器:配 docs/ 静态页 + 一个 /api/gen 端点(点哪篇生成哪篇)。

设计:生成不是批量预跑,而是**你在详情/列表里点某篇 → 只对那一篇调 LLM 生成**。
静态 GitHub Pages 做不到这个(没后端),所以本地用这个小服务器跑工作流;
线上若要同样能力,再接 serverless 函数/Action,逻辑复用 gen_xhs。

用法: python serve_xhs.py [port]   # 默认 8731,然后开 http://localhost:8731/xhs_preview.html
"""
import hmac
import json
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

import gen_xhs
from pipeline import config

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"

config.load_env()                                   # 读 .env(含 XHS_PASSWORD / QWEN_API_KEY)
PASSWORD = (os.environ.get("XHS_PASSWORD") or "").strip()
COOKIE = "xhs_auth"

LOGIN_HTML = """<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>登录 · 小红书工作台</title>
<style>body{margin:0;height:100vh;display:flex;align-items:center;justify-content:center;
background:#0d0f14;font-family:-apple-system,"PingFang SC",sans-serif}
.box{background:#fff;padding:30px 28px;border-radius:18px;width:300px;box-shadow:0 12px 40px rgba(0,0,0,.4)}
h1{font-size:18px;margin:0 0 4px}.sub{color:#888;font-size:13px;margin-bottom:18px}
input{width:100%;box-sizing:border-box;padding:12px 14px;border:1px solid #e3e3e6;border-radius:10px;font-size:15px}
button{width:100%;margin-top:12px;padding:12px;border:none;border-radius:10px;background:#ff2e4d;color:#fff;
font-size:15px;font-weight:700;cursor:pointer}.err{color:#ff2e4d;font-size:13px;margin-top:10px;min-height:18px}</style>
</head><body><div class="box">
<h1>🔒 小红书工作台</h1><div class="sub">输入密码后才能生成 / 查看</div>
<input id="pw" type="password" placeholder="密码" autofocus onkeydown="if(event.key==='Enter')go()">
<button onclick="go()">进入</button><div class="err" id="err"></div>
<script>
function go(){var pw=document.getElementById('pw').value;
 fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},
   body:'password='+encodeURIComponent(pw)})
 .then(function(r){return r.json();})
 .then(function(j){ if(j.ok){location.reload();} else {document.getElementById('err').textContent='密码错误';}})
 .catch(function(){document.getElementById('err').textContent='登录失败';});}
</script></div></body></html>"""


def run_gen(aid, force=False):
    """按 arxiv_id 跨 daily/weekly/库 生成单篇,写入 xhs_store.json,返回该 JSON。"""
    xhs, src = gen_xhs.gen_and_store(aid, gen_xhs.llm_config(), force=force)
    print(f"  ✓ [{src}] {aid} → {'/'.join(xhs['cover'].get('title_lines', []))}")
    return xhs


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(DOCS), **k)

    def _json(self, code, obj, cookie=None):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(body)

    def _authed(self):
        if not PASSWORD:
            return True                              # 没设密码 = OPEN(仅 localhost,开发用)
        raw = self.headers.get("Cookie", "") or ""
        for part in raw.split(";"):
            if "=" in part:
                k, v = part.strip().split("=", 1)
                if k == COOKIE and hmac.compare_digest(v, PASSWORD):
                    return True
        return False

    def _serve_login(self):
        body = LOGIN_HTML.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        u = urlparse(self.path)
        if u.path == "/api/login":
            n = int(self.headers.get("Content-Length", 0) or 0)
            data = parse_qs(self.rfile.read(n).decode("utf-8")) if n else {}
            pw = (data.get("password", [""])[0] or "").strip()
            if PASSWORD and hmac.compare_digest(pw, PASSWORD):
                self._json(200, {"ok": True},
                           cookie=f"{COOKIE}={PASSWORD}; Path=/; HttpOnly; SameSite=Lax; Max-Age=2592000")
            else:
                self._json(401, {"ok": False, "error": "密码错误"})
            return
        self.send_error(404)

    def do_GET(self):
        u = urlparse(self.path)
        # ---- 鉴权门:未登录时 /api/* 给 401,页面给登录页 ----
        if not self._authed():
            if u.path.startswith("/api/"):
                self._json(401, {"error": "未登录"})
            else:
                self._serve_login()
            return
        if u.path == "/api/gen":
            q = parse_qs(u.query)
            aid = (q.get("id", [""])[0] or "").strip()
            force = (q.get("force", ["0"])[0] in ("1", "true"))
            print(f"[gen] id={aid} force={force}")
            try:
                self._json(200, run_gen(aid, force=force))
            except Exception as e:
                self._json(500, {"error": str(e)})
            return
        return super().do_GET()

    def log_message(self, fmt, *args):
        pass  # 静音静态请求日志,只留生成日志


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8731
    host = os.environ.get("XHS_HOST", "127.0.0.1")   # 要手机/外网访问时设 0.0.0.0(务必先设 XHS_PASSWORD)
    srv = ThreadingHTTPServer((host, port), Handler)
    print(f"小红书工作台: http://localhost:{port}/xhs_preview.html  (Ctrl+C 退出)")
    if PASSWORD:
        print(f"🔒 已启用密码登录(XHS_PASSWORD 已设);未登录访问会跳登录页,/api/* 返回 401。")
    else:
        print(f"⚠️  未设 XHS_PASSWORD —— 当前 OPEN 模式(仅 {host} 可达)。要对外开放务必先在 .env 设密码。")
    print(f"生成端点: POST /api/login(密码) → GET /api/gen?id=ARXIV_ID&force=0|1")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nbye")


if __name__ == "__main__":
    main()
