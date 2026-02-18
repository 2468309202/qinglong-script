#!/usr/bin/env python3
# coding: utf-8
'''
项目名称: AKA-Cigma / QLscripts (Modified by AI)
Author: AKA-Cigma
功能：中兴商城自动签到
签到积分买东西可抵扣
抓手机端签到请求链接里面的accessToken=后面的字符串（如dc487xxxx9d67）填到环境变量'zxscck'里，多账号&连接，网页版签到抓到的accessToken没有测试，有可能能用
如果账号触发风控（需要滑块验证），脚本可能会失败
Date: 2026/02/02
cron: 3 0 * * *
new Env('中兴商城');
'''
import requests
import os
import json
import time
from urllib.parse import unquote

try:
    from notify import send
except:
    def send(title, content):
        print(f"【通知】{title}\n{content}")

# ================= 配置区 =================
URL = "https://www.ztemall.com/index.php/topapi"

# 根据抓包数据  更新 Headers
HEADERS = {
    "Accept": "*/*",
    "platform": "android",
    "C-Version": "5.3.60.2506031027",
    "model": "2304FPN6DC",
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; 2304FPN6DC Build/TKQ1.221114.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/144.0.7559.109 Mobile Safari/537.36/ZTEMALL_APP",
    "Accept-Encoding": "gzip",
    "Host": "www.ztemall.com",
    "Connection": "Keep-Alive"
}
# =========================================

def main():
    accounts = os.getenv('zxscck')

    if accounts is None:
        print('❌ 未检测到 zxscck 环境变量')
        exit(1)

    # 支持多账号，用 & 分隔
    accounts_list = accounts.split('&')
    print(f"获取到 {len(accounts_list)} 个账号\n")
    
    result = []

    for i, raw_account in enumerate(accounts_list, start=1):
        print(f"======= 开始执行账号 {i} =======")
        
        # 自动解码：如果用户填入的是 token%24%24... 自动转为 token$$...
        if '%' in raw_account:
            access_token = unquote(raw_account)
        else:
            access_token = raw_account

        # 1. 获取用户信息 & 检查签到状态 (member.index) 
        try:
            user_params = {
                "method": "member.index",
                "format": "json",
                "v": "v1",
                "accessToken": access_token
            }
            user_resp = requests.get(URL, headers=HEADERS, params=user_params, timeout=10).json()
            
            if user_resp.get('errorcode') != 0:
                err_msg = user_resp.get('msg', 'Token失效或接口错误')
                print(f"账号{i} 获取信息失败: {err_msg}")
                result.append(f"账号{i}: 获取信息失败 ({err_msg})")
                continue

            user_data = user_resp.get('data', {})
            user_name = user_data.get('username', '未知用户')
            point = user_data.get('point', 0)
            is_checkin = str(user_data.get('isCheckin', '0')) # "1" 表示已签到 [cite: 2]

            print(f"用户: {user_name} | 当前积分: {point}")

            if is_checkin == "1":
                msg = f"账号{i} ({user_name}) 今日已签到，无需重复。"
                print(f"✅ {msg}")
                result.append(msg)
                continue

        except Exception as e:
            print(f"账号{i} 状态检查异常: {e}")
            # 如果检查状态出错，尝试强行签到

        # 2. 执行签到 (member.checkIn.add) 
        # 注意：抓包中含有 captchaVerifyParam，脚本无法自动生成。
        # 如果服务器强制校验该参数，此请求将失败。
        print("尝试签到中...")
        checkin_params = {
            "method": "member.checkIn.add",
            "format": "json",
            "v": "v1",
            "accessToken": access_token
        }

        try:
            checkin_resp = requests.get(URL, headers=HEADERS, params=checkin_params, timeout=10).json()
            
            if checkin_resp.get('errorcode') == 0:
                data = checkin_resp.get('data', {})
                earned = data.get('currentCheckInPoint', 0)
                total = data.get('point', point)
                days = data.get('checkin_days', 1)
                
                msg = f"账号{i} 签到成功！\n获得积分: {earned}\n连签天数: {days}\n当前总分: {total}"
                print(f"✅ {msg}\n")
                result.append(msg)
            else:
                msg = checkin_resp.get('msg', '未知错误')
                # 检查是否因为缺少验证码参数报错
                if "验证" in msg or "captcha" in str(checkin_resp):
                    extra_info = " (触发风控，APP端强制要求滑块验证，脚本无法通过)"
                else:
                    extra_info = ""
                
                print(f"❌ 账号{i} 签到失败: {msg}{extra_info}\n")
                result.append(f"账号{i} 签到失败: {msg}")

        except Exception as e:
            print(f"❌ 账号{i} 请求异常: {e}\n")
            result.append(f"账号{i} 请求异常: {e}")
        
        # 避免并发过快
        time.sleep(2)

    # 推送消息
    if result:
        try:
            send("中兴商城签到", "\n".join(result))
        except Exception as e:
            print(f"消息推送失败：{e}")

if __name__ == '__main__':
    main()
