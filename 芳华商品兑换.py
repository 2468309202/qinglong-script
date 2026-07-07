import os
import requests
import random
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# ==================== 【核心抢购配置区】 ====================
BASE_URL = "https://api.cdwjyyh.com"
ENV_VAR_NAME = "fhb"
#如果账户已停用，那么需要去寻找任意有效请求：回到 HttpCanary，
#随便找一个刚刚抓到的、发往 api.cdwjyyh.com 的请求记录（比如 /app/user/getUserInfo 或 /app/common/getAppPageConfig）。
#提取 Token：点进这个请求，查看 Request（请求） -> Headers（请求头）。里面必定有一个叫 AppToken 的字段。
#长按复制它的值（通常是一大串很长的英文字母和数字的组合）。重新构造一下变量（fhb 变量支持 1.手机号#AppToken（这种情况是用于已停用的账号）  2.手机号#账户密码 2种方式登录），
#或者放到fhb_tokens.json 对应字段里面
#这里一定要注意看 TARGET_GOODS_ID   商品列表有脚本列出
#这里一定要注意看 TARGET_GOODS_ID   商品列表有脚本列出
#这里一定要注意看 TARGET_GOODS_ID   商品列表有脚本列出
#这里一定要注意看 TARGET_GOODS_ID   商品列表有脚本列出
#这里一定要注意看 TARGET_GOODS_ID   商品列表有脚本列出

TARGET_GOODS_ID = 3276  # 替换为你想要兑换的商品 ID ！！！！！这里要看清楚别兑换错了 
EXCHANGE_COUNT = 1      # 兑换数量
MAX_WORKERS = 1       # 并发线程数（也就是最多几个账号同时开抢） 
MAX_RETRIES = 3         # 网络波动时的重试次数

# ------ GOBOT 独立推送配置 ------
GOBOT_URL = os.environ.get("GOBOT_URL", "")
GOBOT_QQ = os.environ.get("GOBOT_QQ", "")
GOBOT_GROUP = os.environ.get("GOBOT_GROUP", "")
GOBOT_TOKEN = os.environ.get("GOBOT_TOKEN", "")
# ========================================================

# 线程锁，防止并发打印时日志错乱
print_lock = threading.Lock()
notify_lock = threading.Lock()

def safe_print(msg):
    with print_lock:
        print(msg)

def send_gobot_notify(title, content):
    with notify_lock:
        if not GOBOT_URL or (not GOBOT_QQ and not GOBOT_GROUP):
            return
        headers = {"Authorization": f"Bearer {GOBOT_TOKEN}"} if GOBOT_TOKEN else {}
        try:
            if GOBOT_QQ:
                requests.post(f"{GOBOT_URL}/send_private_msg", json={"user_id": int(GOBOT_QQ), "message": f"【{title}】\n\n{content}"}, headers=headers, timeout=5)
            if GOBOT_GROUP:
                requests.post(f"{GOBOT_URL}/send_group_msg", json={"group_id": int(GOBOT_GROUP), "message": f"【{title}】\n\n{content}"}, headers=headers, timeout=5)
        except Exception as e:
            safe_print(f"❌ GoBot 推送失败: {e}")

try:
    from notify import send as ql_send
except ImportError:
    ql_send = None

# 带重试机制的基础请求函数（专为抢购瞬间的服务器卡顿设计）
def request_with_retry(method, url, **kwargs):
    for attempt in range(MAX_RETRIES):
        try:
            res = requests.request(method, url, **kwargs)
            return res
        except requests.exceptions.RequestException as e:
            if attempt == MAX_RETRIES - 1:
                return None
            time.sleep(1)
    return None

def get_app_token(phone, password, jpush_id):
    url = f"{BASE_URL}/app/app/login"
    payload = {"phone": phone, "password": password, "jpushId": jpush_id, "loginType": 1, "source": "yyb"}
    
    safe_print(f"👉 账号 {phone} 正在请求登录接口...")
    res = request_with_retry("POST", url, json=payload, headers={"Content-Type": "application/json;charset=UTF-8"}, timeout=10)
    
    if res and res.status_code == 200:
        data = res.json()
        if data.get("code") == 200:
            safe_print(f"✅ 账号 {phone} 登录成功")
            return data.get("token") or data.get("data", {}).get("token")
        else:
            safe_print(f"❌ 账号 {phone} 登录失败: {data.get('msg', '未知错误')}")
    else:
        safe_print(f"❌ 账号 {phone} 登录网络异常")
    return None

def get_default_address_id(token, phone):
    res = request_with_retry("GET", f"{BASE_URL}/app/userAddress/getAddressList", headers={
        "User-Agent": "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 uni-app",
        "AppToken": token
    }, timeout=8)
    
    if res and res.status_code == 200:
        data = res.json()
        if data.get("code") == 200 and data.get("data"):
            addr_list = data.get("data")
            default_addr = next((addr for addr in addr_list if addr.get("isDefault") == 1), addr_list[0])
            safe_print(f"✅ 账号 {phone} 找到收货地址: {default_addr.get('province')}{default_addr.get('city')}{default_addr.get('detail')}")
            return default_addr.get("addressId")
    safe_print(f"⚠️ 账号 {phone} 获取收货地址失败或列表为空。")
    return None

def get_goods_detail(token, phone, goods_id):
    res = request_with_retry("GET", f"{BASE_URL}/app/integral/getIntegralGoodsById?goodsId={goods_id}", headers={
        "User-Agent": "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 uni-app",
        "AppToken": token
    }, timeout=8)
    
    if res and res.status_code == 200:
        data = res.json()
        if data.get("code") == 200 and data.get("data"):
            goods = data.get("data")
            safe_print(f"✅ 账号 {phone} 确认商品: [{goods.get('goodsName')}] | 所需积分: {goods.get('integral')} 芳华币")
            return True
    safe_print(f"⚠️ 账号 {phone} 拉取商品明细失败。")
    return False

def do_exchange(token, phone, address_id):
    url = f"{BASE_URL}/app/integral/createOrder"
    safe_print(f"🚀 账号 {phone} 提交抢兑订单中...")
    
    res = request_with_retry("POST", url, json={
        "goodsId": TARGET_GOODS_ID, "count": EXCHANGE_COUNT, "addressId": address_id
    }, headers={
        "User-Agent": "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 uni-app",
        "Content-Type": "application/json;charset=UTF-8",
        "AppToken": token
    }, timeout=10)
    
    if res and res.status_code == 200:
        data = res.json()
        if data.get("code") == 200:
            msg = f"🎉 账号 {phone} 抢兑成功！\n🎁 商品ID: {TARGET_GOODS_ID}\n数量: {EXCHANGE_COUNT}"
            safe_print(f"✅ {msg}")
        else:
            msg = f"❌ 账号 {phone} 抢兑失败！\n原因: {data.get('msg', '未知')}"
            safe_print(msg)
    else:
        msg = f"❌ 账号 {phone} 抢兑发生网络超时或严重错误"
        safe_print(msg)
    
    send_gobot_notify(f"芳华币抢兑结果 - {phone}", msg)
    if ql_send: ql_send(f"芳华币抢兑 - {phone}", msg)

# 单账号执行流（独立线程）
def process_account(account_str):
    parts = [p.strip() for p in account_str.split("#")]
    if len(parts) < 2:
        return
    
    phone = parts[0]
    secret = "".join(c for c in parts[1] if ord(c) < 128) # 清理隐藏字符
    
    # 随机微小错峰（50毫秒~500毫秒），防止并发瞬间触发服务器高频风控
    time.sleep(random.uniform(0.05, 0.5))
    
    safe_print(f"\n================ 启动账号: {phone} ================")
    
    if len(secret) > 20:
        safe_print(f"👉 账号 {phone} 检测到提供的是 Token，已跳过账密登录")
        token = secret
    else:
        jpush_id = parts[2] if len(parts) > 2 else f"1a0018970ae5{random.randint(1000, 9999)}"
        token = get_app_token(phone, secret, jpush_id)

    if not token:
        safe_print(f"🛑 账号 {phone} 获取 Token 失败，终止任务！")
        return

    address_id = get_default_address_id(token, phone)
    if not address_id:
        safe_print(f"🛑 账号 {phone} 无收货地址，终止任务！")
        return

    if not get_goods_detail(token, phone, TARGET_GOODS_ID):
        safe_print(f"🛑 账号 {phone} 商品验证失败，终止任务！")
        return

    do_exchange(token, phone, address_id)

def main():
    env_str = os.environ.get(ENV_VAR_NAME, "")
    if not env_str:
        safe_print(f"❌ 未配置 {ENV_VAR_NAME} 环境变量。")
        return

    accounts = [item for item in env_str.split("@") if item.strip()]
    safe_print(f"🚀 共检测到 {len(accounts)} 个账号，即将开启多线程并发抢兑...\n")
    
    # 使用线程池并发执行所有账号
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(process_account, acc) for acc in accounts]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                safe_print(f"❌ 某线程执行异常: {e}")
                
    safe_print("\n🎉 所有账号抢兑任务执行完毕！")

if __name__ == "__main__":
    main()