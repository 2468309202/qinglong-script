# cron: 0 */6 * * *
# AVALON 自动签到 + 自动领取 + WxPusher推送
# 邀请链接 https://app.avalonavs.com/app/webapp/#/Register?code=78518122
# WxPusher推送变量里面配置WP_APP_TOKEN，WP_UID
# 变量AWL_ACCOUNT 值是邮箱#密码
# 注意看注释
# 注意看注释
# 注意看注释
# 注意看注释
import requests
import os
import hashlib
import base64
import random
import string

account = os.getenv("AWL_ACCOUNT")
WP_APP_TOKEN = os.getenv("WP_APP_TOKEN")
WP_UID = os.getenv("WP_UID")

if not account:
    print("❌ 未设置 AWL_ACCOUNT")
    exit()

username, password = account.split("#")
BASE = "https://app.avalonavs.com"

msg_log = []

def log(t):
    print(t)
    msg_log.append(t)

def push(msg):
    if not WP_APP_TOKEN or not WP_UID:
        print("⚠️ 未配置 WxPusher")
        return

    data = {
        "appToken": WP_APP_TOKEN,
        "content": msg,
        "contentType": 1,
        "uids": [WP_UID]
    }

    try:
        requests.post("https://wxpusher.zjiecode.com/api/send/message", json=data)
    except:
        pass

def make_device_uuid(username):
    h = hashlib.sha256(username.encode()).digest()
    return "0." + base64.urlsafe_b64encode(h).decode().rstrip("=")[:11]

def random_boundary(n=30):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(n))

def login():
    log("🔐 正在登录")

    boundary = random_boundary()
    device = make_device_uuid(username)

    data = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="loginName"\r\n\r\n{username}\r\n'
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="password"\r\n\r\n{password}\r\n'
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="deviceUuid"\r\n\r\n{device}\r\n'
        f"--{boundary}--\r\n"
    )

    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "com.avalonavs.app",
        "Origin": "http://app.avalonavs.com",
        "Referer": "http://app.avalonavs.com/",
    }

    r = requests.post(BASE + "/api/app/authentication/login", headers=headers, data=data)
    res = r.json()

    if res.get("code") == 0:
        log("✅ 登录成功")
        return res["data"]

    log("❌ 登录失败")
    return None

def req(token, method, url, data=""):
    headers = {
        "Authorization": token,
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "com.avalonavs.app",
        "Origin": "http://app.avalonavs.com",
        "Referer": "http://app.avalonavs.com/",
        "Accept": "application/json, text/plain, */*"
    }

    if method == "GET":
        return requests.get(BASE + url, headers=headers).json()
    else:
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        return requests.post(BASE + url, headers=headers, data=data).json()

def sign(token):
    log("📅 执行签到")
    r = req(token, "POST", "/api/app/api/signIn/keepSignIn")
    log("签到结果：" + r.get("msg", "未知"))

def receive(token):
    log("💰 检查收益")
    r = req(token, "GET", "/api/app/api/income/incomeList?balanceCapitalTyp=coin")

    if r.get("code") != 0:
        log("❌ 获取收益失败")
        return

    items = r.get("data", [])

    if not items:
        log("✅ 没有可领取收益")
        return

    count = 0

    for i in items:
        income_id = i["id"]
        req(token, "POST", f"/api/app/api/income/receiveIncome/{income_id}", f"id={income_id}")
        count += 1

    log(f"🎉 成功领取 {count} 个")

def main():
    log("🚀 AVALON 自动任务开始")

    token = login()
    if not token:
        push("\n".join(msg_log))
        return

    sign(token)
    receive(token)

    log("✅ 任务完成")

    push("\n".join(msg_log))

if __name__ == "__main__":
    main()
