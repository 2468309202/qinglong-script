# -*- coding: utf-8 -*-
"""
new Env('网易云全能打卡');
cron: 30 9 * * *
变量格式：NETEASE_COOKIE，值去浏览器抓取 MUSIC_U 和 __csrf！
qq群：978659787
"""

import requests
import os
import time
import random

# ================= 配置区域 =================
BARK_URL = 'https://api.day.app/在此处添加自己的bark推送id'
# 调用网易云 Node.js 开源 API 服务节点
API_BASE = "https://netease-cloud-music-api.fe-mm.com"


# ============================================

def get_300_random_songs(cookie):
    """从各大榜单获取300首不重复的歌曲ID用于随机打卡"""
    song_ids = set()
    # 榜单ID：热歌榜, 新歌榜, 飙升榜, 原创榜
    playlist_ids = [3778678, 3779629, 19723756, 2884035]

    for pid in playlist_ids:
        try:
            res = requests.post(f"{API_BASE}/playlist/track/all", data={"cookie": cookie, "id": pid}, timeout=10).json()
            if res.get('code') == 200:
                for song in res.get('songs', []):
                    song_ids.add(song['id'])
            if len(song_ids) >= 300:
                break
        except Exception:
            continue

    song_list = list(song_ids)
    random.shuffle(song_list)
    return song_list[:300]


def do_netease_task():
    cookie = os.getenv('NETEASE_COOKIE')
    if not cookie:
        return "⚠️ 网易云任务失败：未在青龙环境变量中找到 NETEASE_COOKIE"

    msg_list = []
    payload = {"cookie": cookie}

    try:
        # 1. 检查登录状态
        login_res = requests.post(f"{API_BASE}/login/status", data=payload, timeout=15).json()
        if login_res.get('data', {}).get('code') != 200 or not login_res.get('data', {}).get('profile'):
            return "❌ Cookie已失效或格式不正确，请重新去浏览器抓取 MUSIC_U 和 __csrf！"

        nickname = login_res['data']['profile']['nickname']
        vip_type = login_res['data']['profile'].get('vipType', 0)
        vip_str = "👑黑胶VIP" if vip_type > 0 else "👤普通用户"
        msg_list.append(f"账号：{nickname} ({vip_str})")

        # 2. 手机端与网页端双端签到
        sign_m = requests.post(f"{API_BASE}/daily_signin", data={"cookie": cookie, "type": 0}, timeout=10).json()
        if sign_m.get('code') == 200:
            point = sign_m.get('point', 0)
            msg_list.append(f"📱 手机端签到：✅ 成功 (+{point} 云贝)")
        elif sign_m.get('code') == -2:
            msg_list.append(f"📱 手机端签到：☕ 今日已签到")

        sign_w = requests.post(f"{API_BASE}/daily_signin", data={"cookie": cookie, "type": 1}, timeout=10).json()
        if sign_w.get('code') == 200:
            msg_list.append(f"💻 网页端签到：✅ 成功")
        elif sign_w.get('code') == -2:
            msg_list.append(f"💻 网页端签到：☕ 今日已签到")

        # 3. 云贝中心自动打卡与任务领取
        yunbei = requests.post(f"{API_BASE}/yunbei/sign", data=payload, timeout=10).json()
        if yunbei.get('code') == 200:
            # 尝试提取领取的云贝数量
            yb_point = yunbei.get('data', {}).get('point') or yunbei.get('point', '未知')
            msg_list.append(f"💰 云贝签到：✅ 签到成功 (+{yb_point} 云贝)")
        else:
            msg_list.append("💰 云贝签到：☕ 今日已打卡")

        # 尝试自动领取云贝任务奖励
        try:
            tasks_res = requests.post(f"{API_BASE}/yunbei/tasks/todo", data=payload, timeout=10).json()
            if tasks_res.get('code') == 200:
                receipt_count = 0
                total_reward = 0
                for task in tasks_res.get('data', []):
                    # status 1 代表已完成可领取，0 可能是其他状态也尝试一下
                    if task.get('taskStatus') in [0, 1]:
                        rcv_res = requests.post(f"{API_BASE}/yunbei/task/receipt",
                                                data={"cookie": cookie, "userTaskId": str(task.get('userTaskId'))},
                                                timeout=5).json()
                        if rcv_res.get('code') == 200:
                            receipt_count += 1
                            # 累加任务奖励的具体云贝数
                            task_point = task.get('reward') or task.get('taskPoint') or 0
                            total_reward += int(task_point)
                if receipt_count > 0:
                    msg_list.append(f"🎁 云贝任务：✅ 成功领取 {receipt_count} 个任务奖励 (+{total_reward} 云贝)")
                else:
                    msg_list.append(f"🎁 云贝任务：☕ 暂无可领取的任务奖励")
        except Exception as e:
            msg_list.append(f"🎁 云贝任务：⚠️ 奖励领取请求失败 ({e})")

        # 4. VIP专属：自动领取黑胶成长值
        if vip_type > 0:
            vip_sign = requests.post(f"{API_BASE}/vip/growthpoint/sign", data=payload, timeout=10).json()
            if vip_sign.get('code') == 200:
                # 解析获得的成长值
                growth_score = vip_sign.get('data', {}).get('score') or vip_sign.get('point', '未知')
                msg_list.append(f"💎 VIP成长值：✅ 签到成功 (+{growth_score} 成长值)")
            elif vip_sign.get('code') == -2:
                msg_list.append("💎 VIP成长值：☕ 今日已签到过")
            else:
                msg_list.append(f"💎 VIP成长值：❌ {vip_sign.get('msg', '领取失败')}")

            # 尝试获取 VIP 任务奖励并额外获取成长值 (部分隐藏成长值在这个接口)
            try:
                vip_tasks = requests.post(f"{API_BASE}/vip/tasks", data=payload, timeout=10).json()
                # 这个接口调用本身就是一种“领取”，能触发额外成长值入账
            except:
                pass

        # 5. 核心：触发每日听歌300首任务 (随机抽取榜单歌曲)
        msg_list.append("🎵 每日300首：正在获取各大榜单并模拟随机播放...")
        songs_to_play = get_300_random_songs(cookie)

        if not songs_to_play:
            msg_list.append("   - ❌ 获取歌单失败，无法执行300首任务")
        else:
            success_cnt = 0
            for sid in songs_to_play:
                try:
                    # 随机生成模拟听歌时间 (60秒到250秒之间)
                    play_time = random.randint(60, 250)
                    res = requests.post(f"{API_BASE}/scrobble",
                                        data={"cookie": cookie, "id": sid, "sourceid": "al", "time": play_time},
                                        timeout=5).json()
                    if res.get('code') == 200:
                        success_cnt += 1
                    # 稍微延迟，防止请求过快被拦截 (如果青龙运行超时可以适当调低此数值)
                    time.sleep(0.15)
                except Exception:
                    continue
            msg_list.append(f"   - ✅ 成功提交 {success_cnt}/{len(songs_to_play)} 首歌的播放记录")

        # 6. 获取当前听歌量与等级进度
        level_res = requests.post(f"{API_BASE}/user/level", data=payload, timeout=10).json()
        if level_res.get('code') == 200:
            now_level = level_res['data']['level']
            listen_songs = level_res['data']['nowPlayCount']
            msg_list.append(f"📈 当前等级：Lv.{now_level}")
            msg_list.append(f"🎧 累计听歌：{listen_songs}首 (听歌任务经验值和数量稍后在App内刷新)")

    except Exception as e:
        msg_list.append(f"❌ 任务执行发生错误: {e}")

    return "\n".join(msg_list)


def send_bark(title, content):
    if not BARK_URL: return
    base_url = BARK_URL.rstrip('/')
    data = {
        "title": title,
        "body": content,
        "group": "网易云打卡",
        "icon": "https://cdn-icons-png.flaticon.com/512/3128/3128293.png"
    }
    try:
        requests.post(base_url, json=data)
    except:
        pass


if __name__ == '__main__':
    print(f"开始执行网易云音乐打卡任务... {time.strftime('%Y-%m-%d %H:%M:%S')}")
    result_msg = do_netease_task()
    print("=" * 30)
    print(result_msg)
    print("=" * 30)

    send_bark("🎵 网易云自动签到", result_msg)
    print("任务执行完毕。")