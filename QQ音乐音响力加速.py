import requests
import random
import time
from datetime import datetime
import os


# ======================
# 作者信息展示模块
# ======================
def show_author_info():
    print("┌──────[ 作者信息 ]───────────────────────┐")
    print("│                                         │")
    print("│   作者：孔方兄                          │")
    print("│   联系方式：QQ 1478752457（微信同号）   │")
    print("└─────────────────────────────────────────┘")
    print()


# 调用展示函数
show_author_info()

# 用户代理（可选）
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


# PushPlus 通知函数
def send_pushplus_notification(token, title, content):
    url = 'http://www.pushplus.plus/send'
    data = {
        "token": token,
        "title": title,
        "content": content,
        "template": "html"
    }
    try:
        response = requests.post(url, json=data)
        response_json = response.json()
        if response_json.get("code") == 200:
            print("🎉 推送成功")
        else:
            print(f"⚠️ 推送失败: {response_json.get('msg')}")
        return response_json
    except Exception as e:
        print(f"⚠️ 推送时发生异常: {e}")
        return None


def parse_qq_and_token(combined_str):
    """解析 'qq&qqtoken' 格式的字符串"""
    if not combined_str:
        return None, None
    parts = combined_str.split('&', 1)
    if len(parts) != 2:
        return None, None
    return parts[0].strip(), parts[1].strip()


def send_request(qq, url, key):
    """发送请求到API"""
    api_url = f"http://shanhe.kim/api/qy/qyv1.php?qq={qq}&url={requests.utils.quote(url)}&ck={key}&size=4"
    try:
        response = requests.get(api_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        try:
            return response.json(), api_url
        except ValueError:
            return {"error": "Invalid JSON response"}, api_url
    except requests.exceptions.Timeout:
        return {"error": "Request timeout"}, api_url
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}, api_url


def main():
    # 从环境变量中读取配置
    qq_token_combined = os.getenv("QQ_AND_TOKEN", "").strip()
    pushplus_token = os.getenv("PUSHPLUS_TOKEN", "").strip()

    # 解析 QQ 和 Token
    qq, qq_token = parse_qq_and_token(qq_token_combined)

    if not qq:
        print("⛔️ 错误：未提供QQ号（格式：QQ_AND_TOKEN='123456&your_token'）")
        return
    if not qq_token:
        print("⛔️ 错误：未提供QQTOKEN（格式：QQ_AND_TOKEN='123456&your_token'）")
        return

    # 歌曲链接集合
    song_links = [
        "https://c6.y.qq.com/base/fcgi-bin/u?__=PDcyU4N",
        "https://c6.y.qq.com/base/fcgi-bin/u?__=3iU10lKg0KyF",
        "https://c6.y.qq.com/base/fcgi-bin/u?__=7i9PuX1J1LsA",
        "https://c6.y.qq.com/base/fcgi-bin/u?__=0weSa8gM05dT",
        "https://c6.y.qq.com/base/fcgi-bin/u?__=ddngM0S000RS",
        "https://c6.y.qq.com/base/fcgi-bin/u?__=88bAwMBD05uB",
        "https://c6.y.qq.com/base/fcgi-bin/u?__=SvS3YBJL0iRx",
        "https://c6.y.qq.com/base/fcgi-bin/u?__=eVu8xUUe04pc",
        "https://c6.y.qq.com/base/fcgi-bin/u?__=38fL5Lh",
        "https://c6.y.qq.com/base/fcgi-bin/u?__=iTxmU1K",
        "https://c6.y.qq.com/base/fcgi-bin/u?__=EbJxzCVO1bbs",
        "https://c6.y.qq.com/base/fcgi-bin/u?__=4Ba4Xpz",
        "https://c6.y.qq.com/base/fcgi-bin/u?__=NI1IVfN70TAp",
        "https://c6.y.qq.com/base/fcgi-bin/u?__=6bYGj24g4TdO",
        "https://c6.y.qq.com/base/fcgi-bin/u?__=GQZgc3S10w9b",
        "https://c6.y.qq.com/base/fcgi-bin/u?__=zPEad8Sp0Ja8",
        "https://c6.y.qq.com/base/fcgi-bin/u?__=VGxz87DO0INb",
        "https://c6.y.qq.com/base/fcgi-bin/u?__=I4iU1AED0JvN",
        "https://c6.y.qq.com/base/fcgi-bin/u?__=hW4UAs2A0j6Z",
        "https://c6.y.qq.com/base/fcgi-bin/u?__=BCqQ5Uv10FNv",
        "https://c6.y.qq.com/base/fcgi-bin/u?__=mt5MDQLI0TFj",
        "https://c6.y.qq.com/base/fcgi-bin/u?__=a4xVStAg0AsV",
        "https://c6.y.qq.com/base/fcgi-bin/u?__=p8Cg9fj8esjl",
        "https://c6.y.qq.com/base/fcgi-bin/u?__=AqdZzjDY01Lj",
        "https://c6.y.qq.com/base/fcgi-bin/u?__=0b2yIbPwe0Va",
        "https://c6.y.qq.com/base/fcgi-bin/u?__=tvFsJAeH0ID4",
        "https://c6.y.qq.com/base/fcgi-bin/u?__=z8V97lMv0dh0",
        "https://c6.y.qq.com/base/fcgi-bin/u?__=xny40Ok75xNI"
    ]

    max_requests = 20
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 开始推送
    if pushplus_token:
        start_title = "🚀 ✅QQ音乐✅脚本已启动"
        start_content = f"<p>📅 启动时间: {start_time}</p><p>✅ QQ音乐任务启动 | QQ: {qq} | 总请求数: {max_requests}</p>"
        send_pushplus_notification(pushplus_token, start_title, start_content)

    # 控制台显示
    print(f"✅ QQ音乐任务启动 | QQ: {qq} | 总请求数: {max_requests}")

    success_count = 0
    failure_count = 0

    for count in range(1, max_requests + 1):
        url = random.choice(song_links)
        result, api_url = send_request(qq, url, qq_token)

        # 控制台简洁输出
        if "error" in result:
            console_output = f"❌ {count}/{max_requests} 请求失败 | {result['error'][:40]}..."
            failure_count += 1
        else:
            song = result.get("Song", "未知歌曲")
            singer = result.get("Singer", "未知歌手")
            console_output = f"🎵 {count}/{max_requests} | {song} - {singer}"
            success_count += 1

        print(console_output)

        # 随机延迟（除非是最后一次请求）
        if count < max_requests:
            delay = random.randint(180, 300)
            delay_output = f"⏰ 等待 {delay} 秒..."
            print(delay_output)
            time.sleep(delay)

    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    summary = f"<br><p>🎉 所有QQ音乐任务完成！</p><p>✅ 成功次数: {success_count}</p><p>❌ 失败次数: {failure_count}</p><p>🔚 结束时间: {end_time}</p>"

    # 结束推送
    if pushplus_token:
        end_title = "🏁 ✅QQ音乐✅脚本已结束"
        end_content = summary
        send_pushplus_notification(pushplus_token, end_title, end_content)

    print(summary)
    print("🎉 所有QQ音乐任务完成！")


if __name__ == "__main__":
    main()
