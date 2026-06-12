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

# 端口/绑定:Railway 等托管会注入 PORT → 自动公网模式(0.0.0.0);本地无 PORT → 只听 127.0.0.1
_ARGV_PORT = next((a for a in sys.argv[1:] if a.isdigit()), None)
PORT = int(os.environ.get("PORT") or _ARGV_PORT or 8731)
HOST = os.environ.get("XHS_HOST") or ("0.0.0.0" if os.environ.get("PORT") else "127.0.0.1")
EXPOSED = HOST == "0.0.0.0"                          # 对外可达
NEEDS_SETUP = EXPOSED and not PASSWORD               # 公网却没设密码 = 危险,锁死

NOTICE_HTML = """<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>需要配置</title>
<style>body{margin:0;height:100vh;display:flex;align-items:center;justify-content:center;
background:#0d0f14;font-family:-apple-system,"PingFang SC",sans-serif;color:#eee;text-align:center;padding:24px}
.b{max-width:420px}.b h1{font-size:19px}.b code{background:#222;padding:2px 7px;border-radius:5px;color:#ffd84d}</style>
</head><body><div class="b"><h1>⚠️ 部署到公网必须先设密码</h1>
<p>检测到对外开放(0.0.0.0)但未设置 <code>XHS_PASSWORD</code>。<br>
为避免别人调用你的生成接口(烧 LLM 额度),已暂时锁定。</p>
<p>请在托管(Railway)的环境变量里加 <code>XHS_PASSWORD</code>(和 <code>QWEN_API_KEY</code>)后重启。</p>
</div></body></html>"""

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
        if NEEDS_SETUP:
            self._json(403, {"error": "服务器未设 XHS_PASSWORD,已锁定"}); return
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
        # ---- 公网裸奔保护:没设密码就锁死 ----
        if NEEDS_SETUP:
            if u.path.startswith("/api/"):
                self._json(403, {"error": "服务器未设 XHS_PASSWORD,已锁定"})
            else:
                body = NOTICE_HTML.encode("utf-8")
                self.send_response(403); self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
            return
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
    srv = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"小红书工作台: http://{'localhost' if HOST=='127.0.0.1' else HOST}:{PORT}/xhs_preview.html  (Ctrl+C 退出)")
    if NEEDS_SETUP:
        print(f"⛔ 公网模式({HOST})但未设 XHS_PASSWORD —— 已锁定!请在环境变量设 XHS_PASSWORD 后重启。")
    elif PASSWORD:
        print(f"🔒 已启用密码登录;未登录访问跳登录页,/api/* 返回 401。绑定 {HOST}:{PORT}")
    else:
        print(f"⚠️  未设密码,但仅 {HOST} 本地可达(OPEN 模式,开发用)。")
    print(f"生成端点: POST /api/login(密码) → GET /api/gen?id=ARXIV_ID&force=0|1")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nbye")


if __name__ == "__main__":
    main()
