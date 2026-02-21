# -*- coding: UTF-8 -*-

import requests
import json
import time
import random
import os
from requests.exceptions import RequestException
from collections import defaultdict

TOKEN_LIST = os.getenv('TOKEN_LIST', '')
SEND_KEY_LIST = os.getenv('SEND_KEY_LIST', '')

# 接口配置
url = 'https://m.jlc.com/api/activity/sign/signIn?source=3'
gold_bean_url = "https://m.jlc.com/api/appPlatform/center/assets/selectPersonalAssetsInfo"
seventh_day_url = "https://m.jlc.com/api/activity/sign/receiveVoucher"


# ======== 工具函数 ========

def mask_account(account):
    """用于打印时隐藏部分账号信息"""
    if len(account) >= 4:
        return account[:2] + '****' + account[-2:]
    return '****'


def mask_json_customer_code(data):
    """递归地脱敏 JSON 中的 customerCode 字段"""
    if isinstance(data, dict):
        new_data = {}
        for k, v in data.items():
            if k == "customerCode" and isinstance(v, str):
                new_data[k] = v[:1] + "xxxxx" + v[-2:]  # 例: 1xxxxx8A
            else:
                new_data[k] = mask_json_customer_code(v)
        return new_data
    elif isinstance(data, list):
        return [mask_json_customer_code(i) for i in data]
    else:
        return data


# ======== 推送通知 ========

def send_msg_by_server(send_key, title, content):
    push_url = f'https://sctapi.ftqq.com/{send_key}.send'
    data = {
        'text': title,
        'desp': content
    }
    try:
        response = requests.post(push_url, data=data)
        return response.json()
    except RequestException:
        return None


# ======== 单个账号签到逻辑 ========

def sign_in(access_token):
    headers = {
        'X-JLC-AccessToken': access_token,
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) '
                      'AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Html5Plus/1.0 (Immersed/20) JlcMobileApp',
    }

    try:
        # 1. 获取金豆信息（先获取，用于获取 customer_code）
        bean_response = requests.get(gold_bean_url, headers=headers)
        bean_response.raise_for_status()
        bean_result = bean_response.json()

        # 获取 customerCode
        customer_code = bean_result['data']['customerCode']
        integral_voucher = bean_result['data']['integralVoucher']

        # 2. 执行签到请求
        sign_response = requests.get(url, headers=headers)
        sign_response.raise_for_status()
        sign_result = sign_response.json()

        # 打印签到响应 JSON（已脱敏）
        # print(f"🔍 [账号{mask_account(customer_code)}] 签到响应JSON:")
        # print(json.dumps(mask_json_customer_code(sign_result), indent=2, ensure_ascii=False))

        # 检查签到是否成功
        if not sign_result.get('success'):
            message = sign_result.get('message', '未知错误')
            if '已经签到' in message:
                print(f"ℹ️ [账号{mask_account(customer_code)}] 今日已签到")
                return None  # 今日已签到，不返回消息
            else:
                print(f"❌ [账号{mask_account(customer_code)}] 签到失败 - {message}")
                return None  # 签到失败，不返回消息

        # 解析签到数据
        data = sign_result.get('data', {})
        
        # 安全地获取 gainNum 和 status
        gain_num = data.get('gainNum') if data else None
        status = data.get('status') if data else None

        # 处理签到结果
        if status and status > 0:
            if gain_num is not None and gain_num != 0:
                print(f"✅ [账号{mask_account(customer_code)}] 今日签到成功")
                return f"✅ 账号({mask_account(customer_code)})：获取{gain_num}个金豆，当前总数：{integral_voucher + gain_num}"
            else:
                # 第七天特殊处理
                seventh_response = requests.get(seventh_day_url, headers=headers)
                seventh_response.raise_for_status()
                seventh_result = seventh_response.json()

                if seventh_result.get("success"):
                    print(f"🎉 [账号{mask_account(customer_code)}] 第七天签到成功")
                    return f"🎉 账号({mask_account(customer_code)})：第七天签到成功，当前金豆总数：{integral_voucher + 8}"
                else:
                    print(f"ℹ️ [账号{mask_account(customer_code)}] 第七天签到失败，无金豆获取")
                    return None
        else:
            print(f"ℹ️ [账号{mask_account(customer_code)}] 今日已签到或签到失败")
            return None

    except RequestException as e:
        print(f"❌ [账号{mask_account(access_token)}] 网络请求失败: {str(e)}")
        return None
    except KeyError as e:
        print(f"❌ [账号{mask_account(access_token)}] 数据解析失败: 缺少键 {str(e)}")
        return None
    except Exception as e:
        print(f"❌ [账号{mask_account(access_token)}] 未知错误: {str(e)}")
        return None


# ======== 主函数 ========

def main():
    # 从 GitHub Secrets 获取配置
    AccessTokenList = [token.strip() for token in TOKEN_LIST.split(',') if token.strip()]
    SendKeyList = [key.strip() for key in SEND_KEY_LIST.split(',') if key.strip()]

    # 检查配置是否为空
    if not AccessTokenList:
        print("❌ 请设置 TOKENS")
        return
        
    if not SendKeyList:
        print("❌ 请设置 SENDKEYS")
        return

    # 确保长度一致
    min_length = min(len(AccessTokenList), len(SendKeyList))
    AccessTokenList = AccessTokenList[:min_length]
    SendKeyList = SendKeyList[:min_length]

    print(f"🔧 共发现 {min_length} 个账号需要签到")

    # 按 SendKey 分组
    task_groups = defaultdict(list)
    for access_token, send_key in zip(AccessTokenList, SendKeyList):
        task_groups[send_key].append(access_token)

    print(f"📊 共分为 {len(task_groups)} 个通知组")

    # 顺序执行签到任务
    group_results = {}

    for send_key, tokens in task_groups.items():
        print(f"\n🚀 开始处理 SendKey: {send_key[:5]}... 的 {len(tokens)} 个账号")
        results = []
        
        for i, token in enumerate(tokens):
            print(f"📝 处理第 {i+1}/{len(tokens)} 个账号...")
            
            # 执行签到
            result = sign_in(token)
            if result is not None:
                results.append(result)
            
            # 如果不是最后一个账号，则等待随机时间
            if i < len(tokens) - 1:
                wait_time = random.randint(5, 15)
                print(f"⏳ 等待 {wait_time} 秒后处理下一个账号...")
                time.sleep(wait_time)
        
        group_results[send_key] = results

    # 推送通知 - 只在有获取到金豆时才发送
    print("\n📬 开始检查是否需要发送通知...")
    notification_sent = False
    
    for send_key, results in group_results.items():
        if results:
            content = "\n\n".join(results)
            print(f"📤 检测到有金豆获取，准备发送通知给 SendKey: {send_key[:5]}...")
            
            response = send_msg_by_server(send_key, "嘉立创签到汇总", content)
            
            if response and response.get('code') == 0:
                print(f"✅ 通知发送成功！消息ID: {response.get('data', {}).get('pushid', '')}")
                notification_sent = True
            else:
                error_msg = response.get('message') if response else '未知错误'
                print(f"❌ 通知发送失败！错误: {error_msg}")
        else:
            print(f"⏭️ SendKey: {send_key[:5]}... 组内无金豆获取，跳过通知")
    
    if not notification_sent:
        print("ℹ️ 所有账号均未获取到金豆，无通知发送")


# ======== 程序入口 ========

if __name__ == '__main__':
    print("🏁 嘉立创自动签到任务开始")
    main()
    print("🏁 任务执行完毕")
