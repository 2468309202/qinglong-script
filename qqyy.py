# -*- coding: utf-8 -*-
"""
千千音乐刷播放量 - 青龙环境变量版
变量名：QQMUSIC_CONFIG
格式：歌曲ID#目标播放量#线程数#最小间隔#最大间隔#AccessToken#设备ID前缀
示例：T10065195961#10000#100#1#3#YzBjNmE0NzIxZDdjMGZlYWUxYjIxNzVlOTMyYTc1Y2E=#70fb0e9a174fd
"""

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import time
import random
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import wraps
import threading
import os

# ========== 全局变量 ==========
success_count = 0
fail_count = 0
lock = threading.Lock()
running = True
start_time = 0

# ========== 读取青龙环境变量 ==========
def load_env_config():
    env = os.getenv("QQMUSIC_CONFIG", "")
    if not env or "#" not in env:
        print("❌ 请添加环境变量 QQMUSIC_CONFIG")
        print("📌 格式：歌曲ID#目标播放量#线程数#最小间隔#最大间隔#AccessToken#设备ID前缀")
        exit(1)

    arr = env.strip().split("#")
    if len(arr) < 7:
        print("❌ 变量格式错误！")
        exit(1)

    return {
        "SONG_ID": arr[0],
        "TARGET_PLAYS": arr[1],
        "MAX_THREADS": arr[2],
        "MIN_INTERVAL": arr[3],
        "MAX_INTERVAL": arr[4],
        "ACCESS_TOKEN": arr[5],
        "DEVICE_ID_PREFIX": arr[6],
        "USER_AGENT": "okhttp-okgo/jeasonlzy",
        "BATCH_SIZE": "50"
    }

# ========== 日志装饰器 ==========
def log(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            return False
    return wrapper

# ========== 生成设备ID ==========
def generate_random_device_id(prefix):
    return prefix + ''.join(random.choices('0123456789abcdef', k=4))

# ========== 生成签名 ==========
@log
def generate_sign(params):
    sign_str = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
    sign_str += "qianqianmusic"
    return hashlib.md5(sign_str.encode()).hexdigest()

# ========== 模拟播放 ==========
@log
def simulate_play(config):
    global running
    if not running:
        return False

    try:
        timestamp = str(int(time.time() * 1000))
        device_id = generate_random_device_id(config["DEVICE_ID_PREFIX"])

        params = {
            "playrefer": "5",
            "playreferid": "",
            "restype": "song",
            "suid": config["SONG_ID"],
            "rate": "128",
            "pt": "226",
            "isplay": "true",
            "action": "play",
            "pid": "121",
            "v": "8.3.1.9",
            "islogin": "true",
            "luid": "1127219571493699584",
            "cuid": f"[IMEI]{device_id}",
            "mc": "Original",
            "mod": "Android",
            "dm": "ICL-AL10",
            "dm_ver": "12",
            "ns": "4",
            "carri": "3",
            "appid": "16073360",
            "timestamp": timestamp
        }

        params["sign"] = generate_sign(params)

        headers = {
            "host": "click-qianqian.91q.com",
            "accept-language": "zh-CN,zh;q=0.8",
            "user-agent": config["USER_AGENT"],
            "device-id": device_id,
            "app-version": "v8.3.1.9",
            "channel": "Original",
            "from": "android",
            "timestamp": timestamp,
            "authorization": f"access_token {config['ACCESS_TOKEN']}",
            "requestid": f"{timestamp}uuid{''.join(random.choices('0123456789abcdef', k=32))}"
        }

        response = requests.get(
            "https://click-qianqian.91q.com/v.gif",
            params=params,
            headers=headers,
            timeout=5,
            verify=False
        )
        response.raise_for_status()
        return True

    except Exception:
        return False

# ========== 主任务 ==========
def play_task():
    global success_count, fail_count, running, start_time
    success_count = 0
    fail_count = 0
    running = True
    start_time = time.time()

    config = load_env_config()
    target_plays = int(config["TARGET_PLAYS"])
    max_threads = int(config["MAX_THREADS"])
    min_interval = int(config["MIN_INTERVAL"])
    max_interval = int(config["MAX_INTERVAL"])
    batch_size = int(config["BATCH_SIZE"])

    print("=" * 60)
    print("🎵 千千音乐刷播放量（青龙环境变量版）")
    print(f"歌曲ID：{config['SONG_ID']}")
    print(f"目标播放：{target_plays} 次")
    print(f"线程数：{max_threads}")
    print("=" * 60)

    try:
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = []

            while success_count < target_plays and running:
                remaining = target_plays - success_count
                current_batch = min(batch_size, remaining)

                for _ in range(current_batch):
                    if not running:
                        break
                    futures.append(executor.submit(simulate_play, config))

                for future in as_completed(futures):
                    if not running:
                        break
                    res = future.result()
                    with lock:
                        if res:
                            success_count += 1
                        else:
                            fail_count += 1
                    futures.remove(future)

                speed = success_count / (time.time() - start_time) if (time.time() - start_time) > 0 else 0
                print(f"✅ 成功：{success_count} | ❌ 失败：{fail_count} | ⚡ 速度：{speed:.2f}/s")

                if success_count < target_plays and running:
                    time.sleep(random.uniform(min_interval, max_interval))

        total_time = time.time() - start_time
        total = success_count + fail_count
        rate = success_count / total * 100 if total > 0 else 0

        print("\n" + "=" * 60)
        print("🎉 任务完成！")
        print(f"✅ 成功播放：{success_count} 次")
        print(f"❌ 失败次数：{fail_count} 次")
        print(f"⏱️ 总耗时：{int(total_time//60)}分{int(total_time%60)}秒")
        print(f"⚡ 平均速度：{success_count/total_time:.2f} 次/秒")
        print(f"📊 成功率：{rate:.2f}%")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 异常：{str(e)}")

# ========== 入口 ==========
if __name__ == "__main__":
    try:
        import requests
    except ImportError:
        os.system("pip install requests -q")

    play_task()