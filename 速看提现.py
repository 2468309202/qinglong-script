'''
本脚本仅供学习研究使用，严禁用于任何商业、刷量、违规获利等行为。
使用本脚本所产生的一切风险、账号封禁、法律责任及后果，均由使用者自行承担。
作者仅提供代码参考，不承担任何相关责任。使用即代表您已阅读并同意本声明。
脚本更新链接 记得转存实时更新：https://pan.quark.cn/s/c6416fe69380
'''
import requests
import json
import os
import time
from urllib.parse import urlparse, parse_qs

# 关闭烦人的 SSL 警告
requests.packages.urllib3.disable_warnings()

# ===================== 读取环境变量 =====================
def get_env(name, default=""):
    return os.getenv(name, default).strip()

SUKAN_URL = get_env("SUKAN_URL")
WITHDRAW_AMOUNT = "0.3"

# ===================== 从你给的 SUKAN_URL 里提取所有参数 =====================
def get_all_params(url):
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    params = {k: v[0] for k, v in query.items()}
    return params

# ===================== 调用任务同步接口（GET请求，标记任务完成） =====================
def sync_task_status():
    if not SUKAN_URL:
        print("❌ 未配置 SUKAN_URL，无法同步任务状态")
        return False
    
    # 提取SUKAN_URL里的参数 + 补充task_type=518（关键任务类型）
    params = get_all_params(SUKAN_URL)
    params["task_type"] = "518"  # 0.3元提现任务专属类型ID
    
    # 任务同步接口地址
    task_url = "https://welfare-user.palmestore.com/api/task/welfare/list"
    
    # 任务接口请求头（和提现接口一致）
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 15; 23049RAD8C Build/AQ3A.250226.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/131.0.6778.260 Mobile Safari/537.36 zyApp/SuKanRead zyVersion/8.0.2 zyChannel/801003",
        "X-Requested-With": "com.chaozh.xincao.only.sk",
        "Referer": SUKAN_URL,
        "Origin": "https://welfare-user.palmestore.com",
        "Host": "welfare-user.palmestore.com"
    }
    
    try:
        print("✅ 开始调用任务同步接口（标记任务完成）")
        # 发送GET请求（核心：点击任务接口）
        resp = requests.get(
            task_url,
            params=params,
            headers=headers,
            verify=False,
            timeout=10
        )
        
        result = resp.json()
        print(f"📝 任务同步返回：{result.get('code')} - {result.get('msg')}")
        
        # 验证任务是否同步成功
        task_info = result.get("body", {}).get("task_info", {}).get("deposit_withdraw", {})
        if result.get("code") == 0 and task_info.get("done_status") == 1:
            print("✅ 任务同步成功！服务器已标记任务完成")
            return True
        else:
            print(f"⚠️  任务同步失败：done_status={task_info.get('done_status')}")
            return True  # 即使状态显示未完成，也继续尝试提现（兼容部分场景）
    except Exception as e:
        print(f"❌ 任务同步异常：{e}")
        return True  # 接口异常也继续尝试提现

# ===================== 真实提现接口（你抓包的那个） =====================
def do_withdraw():
    if not SUKAN_URL:
        print("❌ 未配置 SUKAN_URL")
        return

    params = get_all_params(SUKAN_URL)

    # 真实接口：你抓包给我的 POST /api/user/cashWithdraw
    url = "https://welfare-user.palmestore.com/api/user/cashWithdraw"

    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 15; 23049RAD8C Build/AQ3A.250226.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/131.0.6778.260 Mobile Safari/537.36 zyApp/SuKanRead zyVersion/8.0.2 zyChannel/801003",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "com.chaozh.xincao.only.sk",
        "Referer": SUKAN_URL,
        "Origin": "https://welfare-user.palmestore.com",
        "Host": "welfare-user.palmestore.com"
    }

    data = {
        **params,
        "type": "cash_wallet",
        "price": WITHDRAW_AMOUNT,
        "product_id": "0",
        "item_id": "12010000",
        "method": "2",
        "extract_type": "2",
        "discount": "false"
    }

    try:
        resp = requests.post(
            url,
            headers=headers,
            data=data,
            verify=False,
            timeout=15
        )

        result = resp.json()
        print(f"📝 提现返回：{result}")

        if "今日已领完" in str(result):
            print("✅ 接口调用成功 → 今日已领完（正常业务限制）")
        elif "成功" in str(result) or result.get("code") in (0, 200):
            print(f"✅ 提现 {WITHDRAW_AMOUNT} 元成功！")
        else:
            print(f"⚠️ 提现失败：{result.get('msg')}")

    except Exception as e:
        print(f"❌ 提现异常：{e}")

# ===================== 主流程：先同步任务 → 再提现 =====================
if __name__ == "__main__":
    print("✅ 开始执行 任务同步 + 0.3 元提现流程")
    # 1. 调用任务同步接口（点击任务接口）
    sync_task_status()
    # 2. 等待2秒（让服务器同步状态）
    time.sleep(2)
    # 3. 执行提现
    do_withdraw()
    print("✅ 执行完成")