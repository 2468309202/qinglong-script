# cron: 0 */6 * * *
# AVALON 自动签到 + 自动领取 + WxPusher推送
# 邀请链接 https://app.avalonavs.com/app/webapp/#/Register?code=78518122
# WxPusher推送变量里面配置WP_APP_TOKEN，WP_UID
# 变量AWL_ACCOUNT 值是 邮箱#密码，多账号支持换行或者 & 符号分割

import requests
import os
import hashlib
import base64
import random
import string
import time

WP_APP_TOKEN = os.getenv("WP_APP_TOKEN")
WP_UID = os.getenv("WP_UID")
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

def login(username, password):
    log(f"🔐 正在登录账号: {username[:3]}***")

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

    log(f"❌ 登录失败: {res.get('msg', '未知原因')}")
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
    log("💰 获取收益明细")
    r = req(token, "GET", "/api/app/api/income/incomeList?balanceCapitalTyp=coin")

    if r.get("code") != 0:
        log("❌ 获取收益失败")
        return

    items = r.get("data", [])

    if not items:
        log("✅ 当前没有可领取收益")
        return

    count = 0
    total_amount = 0.0

    for i in items:
        income_id = i.get("id")
        amount = float(i.get("amount", i.get("num", i.get("money", i.get("incomeAmount", 0)))))
        
        # 领取请求也加入 2-4 秒延时，防止领取接口也被风控
        time.sleep(random.uniform(2.0, 4.0))
        res = req(token, "POST", f"/api/app/api/income/receiveIncome/{income_id}", f"id={income_id}")
        
        if res.get("code") == 0:
            count += 1
            total_amount += amount
            amt_str = f"{amount:.4f}" if amount > 0 else "未知"
            log(f"   - ✅ 成功领取明细 ID:{income_id} | 金额: {amt_str}")
        else:
            log(f"   - ❌ 领取失败 ID:{income_id} | 原因: {res.get('msg', '未知')}")

    log(f"🎉 本账号共成功领取 {count} 笔，预计合计获得: {total_amount:.4f}")

def main():
    log("🚀 AVALON 自动任务开始")

    account_str = os.getenv("AWL_ACCOUNT")
    if not account_str:
        log("❌ 未设置 AWL_ACCOUNT")
        push("\n".join(msg_log))
        return

    accounts = [acc.strip() for acc in account_str.replace('&', '\n').split('\n') if acc.strip() and '#' in acc]
    
    if not accounts:
        log("❌ AWL_ACCOUNT 变量格式错误，未找到有效账号")
        push("\n".join(msg_log))
        return
        
    log(f"🔍 共检测到 {len(accounts)} 个账号\n")

    for index, acc in enumerate(accounts):
        log(f"====== 开始执行第 {index + 1} 个账号 ======")
        try:
            username, password = acc.split("#", 1)
            token = login(username, password)
            if token:
                sign(token)
                receive(token)
        except Exception as e:
            log(f"❌ 解析或执行异常: {str(e)}")
            
        log("====================================")
        
        # 严格遵守官方 60 秒限制，强制随机休眠 65 到 85 秒
        if index < len(accounts) - 1:
            sleep_time = random.randint(65, 85)
            log(f"⏳ 触发严格防风控机制，强制等待 {sleep_time} 秒后执行下一个账号...\n")
            time.sleep(sleep_time)
        else:
            log("\n")

    log("✅ 所有账号任务执行完毕")
    push("\n".join(msg_log))

if __name__ == "__main__":
    main()