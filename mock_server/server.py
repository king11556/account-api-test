#!/usr/bin/env python3
"""阶段 4 · 项目 A：账号模块模拟服务（注册 / 登录 / 改密 / 我的资料）

只用标准库，不装依赖。数据放内存，重启即清空。

需求文档：Obsidian/阶段4 项目A · 需求文档.md
本服务按该文档实现，但**有 5 处与文档不一致**（埋的缺陷），请对照文档找出来。
"""
import json
import re
import sys
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

USERS = []      # [{userId, phone, password, nickname, createdAt, tokens:[...]}]
SEQ = [0]


def now():
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def send_json(handler, status, payload):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def find_by_phone(phone):
    for u in USERS:
        if u["phone"] == phone:
            return u
    return None


def find_by_token(token):
    if not token:
        return None
    for u in USERS:
        if token in u["tokens"]:
            return u
    return None


class Handler(BaseHTTPRequestHandler):
    server_version = "MockAccount/1.0"

    def log_message(self, fmt, *args):
        sys.stderr.write("[%s] %s %s\n" % (now(), self.command, self.path))
        sys.stderr.flush()

    # ---------- 工具 ----------
    def read_body(self):
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length).decode("utf-8", "replace") if length else ""
        try:
            return json.loads(raw) if raw else {}
        except Exception:
            return None

    def auth_token(self):
        h = self.headers.get("Authorization") or ""
        if h.lower().startswith("bearer "):
            return h[7:].strip()
        return ""

    def route(self):
        p = urlparse(self.path)
        return p.path.rstrip("/") or "/", parse_qs(p.query)

    # ---------- GET ----------
    def do_GET(self):
        path, qs = self.route()

        if path == "/api/v1/_debug/users":
            data = [{
                "userId": u["userId"],
                "phone": u["phone"],
                "nickname": u["nickname"],
                "passwordLength": len(u["password"]),
                "createdAt": u["createdAt"],
                "tokenCount": len(u["tokens"]),
            } for u in USERS]
            return send_json(self, 200, {"code": 0, "message": "ok", "data": data})

        if path == "/api/v1/profile":
            user = find_by_token(self.auth_token())
            if not user:
                return send_json(self, 401, {"code": 1002, "message": "登录状态已失效，请重新登录"})

            # 预留参数 userId：文档要求"仅允许查询本人"
            target = user
            if "userId" in qs:
                try:
                    want = int(qs["userId"][0])
                except Exception:
                    return send_json(self, 400, {"code": 4001, "message": "userId 必须是数字"})
                for u in USERS:
                    if u["userId"] == want:
                        target = u          # 缺陷：未校验是否为本人
                        break

            return send_json(self, 200, {"code": 0, "message": "ok", "data": {
                "userId": target["userId"],
                "phone": target["phone"],
                "nickname": target["nickname"],
                "createdAt": target["createdAt"],
            }})

        return send_json(self, 404, {"code": 404, "message": "接口不存在: " + path})

    # ---------- POST ----------
    def do_POST(self):
        path, _ = self.route()
        handler = {
            "/api/v1/register": self.register,
            "/api/v1/login": self.login,
            "/api/v1/change-password": self.change_password,
        }.get(path)
        if not handler:
            return send_json(self, 404, {"code": 404, "message": "接口不存在: " + path})

        body = self.read_body()
        if body is None:
            return send_json(self, 400, {"code": 400, "message": "请求体不是合法的 JSON"})
        return handler(body)

    # ---------- 注册 ----------
    def register(self, d):
        phone = d.get("phone", "")
        pwd = d.get("password", "")
        nickname = d.get("nickname", "") or ""
        if not isinstance(phone, str) or not isinstance(pwd, str) or not isinstance(nickname, str):
            return send_json(self, 400, {"code": 400, "message": "字段必须是字符串"})

        # 1 非空
        if phone == "":
            return send_json(self, 400, {"code": 2001, "message": "手机号不能为空"})
        # 2 格式
        if not re.fullmatch(r"1\d{10}", phone):
            return send_json(self, 400, {"code": 2004, "message": "手机号格式不正确"})
        # 3 密码非空
        if pwd == "":
            return send_json(self, 400, {"code": 2001, "message": "密码不能为空"})
        # 4 密码长度：文档为 8-16 位（含两端）
        if len(pwd) < 8 or len(pwd) > 15:          # 缺陷：上边界写错
            return send_json(self, 400, {"code": 2002, "message": "密码长度需 8-16 位"})
        # 5 密码组成：文档为必须同时包含字母和数字
        if not re.search(r"[0-9]", pwd):           # 缺陷：只查了数字，漏了字母
            return send_json(self, 400, {"code": 2003, "message": "密码必须同时包含字母和数字"})
        # 6 昵称长度
        if nickname and len(nickname) > 20:
            return send_json(self, 400, {"code": 2005, "message": "昵称长度不能超过 20 个字符"})
        # 7 查重
        if find_by_phone(phone):
            return send_json(self, 409, {"code": 2006, "message": "该手机号已注册"})

        SEQ[0] += 1
        USERS.append({"userId": SEQ[0], "phone": phone, "password": pwd,
                      "nickname": nickname, "createdAt": now(), "tokens": []})
        return send_json(self, 200, {"code": 0, "message": "注册成功",
                                     "data": {"userId": SEQ[0]}})

    # ---------- 登录 ----------
    def login(self, d):
        phone = d.get("phone", "")
        pwd = d.get("password", "")
        if not isinstance(phone, str) or not isinstance(pwd, str):
            return send_json(self, 400, {"code": 400, "message": "字段必须是字符串"})
        if phone == "":
            return send_json(self, 400, {"code": 2001, "message": "手机号不能为空"})
        if pwd == "":
            return send_json(self, 400, {"code": 2001, "message": "密码不能为空"})

        user = find_by_phone(phone)
        if not user or user["password"] != pwd:
            # 缺陷：文档要求 401，这里返回了 200
            return send_json(self, 200, {"code": 1001, "message": "手机号或密码错误"})

        token = uuid.uuid4().hex
        user["tokens"].append(token)
        return send_json(self, 200, {"code": 0, "message": "登录成功",
                                     "data": {"token": token, "userId": user["userId"]}})

    # ---------- 修改密码 ----------
    def change_password(self, d):
        user = find_by_token(self.auth_token())
        if not user:
            return send_json(self, 401, {"code": 1002, "message": "登录状态已失效，请重新登录"})

        old = d.get("oldPassword", "")
        new = d.get("newPassword", "")
        if not isinstance(old, str) or not isinstance(new, str):
            return send_json(self, 400, {"code": 400, "message": "字段必须是字符串"})
        if old == "" or new == "":
            return send_json(self, 400, {"code": 2001, "message": "密码不能为空"})
        if user["password"] != old:
            return send_json(self, 400, {"code": 3001, "message": "原密码不正确"})
        if new == old:
            return send_json(self, 400, {"code": 3002, "message": "新密码不能与原密码相同"})
        if len(new) < 8 or len(new) > 16:
            return send_json(self, 400, {"code": 2002, "message": "密码长度需 8-16 位"})
        if not re.search(r"[A-Za-z]", new) or not re.search(r"[0-9]", new):
            return send_json(self, 400, {"code": 2003, "message": "密码必须同时包含字母和数字"})

        user["password"] = new
        # 缺陷：文档要求修改成功后所有旧 token 立即失效，这里没有清空
        return send_json(self, 200, {"code": 0, "message": "修改成功"})


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8100), Handler)
    print("账号模块已启动: http://127.0.0.1:8100  (Ctrl+C 停止)", flush=True)
    server.serve_forever()
