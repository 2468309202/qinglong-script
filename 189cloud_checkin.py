#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天翼云盘签到脚本
欢迎入群交流 qq群:978659787  qq群1016916079
该脚本为网上收集
青龙面板环境变量设置示例:
     TIAN_YI_ACCOUNTS="手机号1,密码1;手机号2,密码2"
    export PUSH_PLUS_TOKEN="你的PUSH PLUS TOKEN"
"""

import time
import re
import base64
import hashlib
import rsa
import requests
import os
import sys
from datetime import datetime
import json

BI_RM = list("0123456789abcdefghijklmnopqrstuvwxyz")
B64MAP = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"


class TianYiCloudSigner:
    def __init__(self):
        self.session = requests.Session()
        self.accounts = self._get_accounts()
        self.push_results = []

    def _get_accounts(self):
        """从环境变量获取账户信息"""
        accounts = []

        # 从环境变量 TIAN_YI_ACCOUNTS 获取账户信息，格式：用户名1,密码1;用户名2,密码2
        env_accounts = os.getenv('TIAN_YI_ACCOUNTS', '')
        if env_accounts:
            account_pairs = env_accounts.split(';')
            for pair in account_pairs:
                if ',' in pair:
                    parts = pair.strip().split(',', 1)
                    if len(parts) == 2:
                        username, password = parts
                        accounts.append({
                            'username': username.strip(),
                            'password': password.strip()
                        })

        # 如果没有环境变量，尝试从命令行参数获取
        if not accounts and len(sys.argv) > 1:
            arg_accounts = ' '.join(sys.argv[1:])
            if ';' in arg_accounts:
                account_groups = arg_accounts.split(';')
                for account_group in account_groups:
                    if ',' in account_group:
                        parts = account_group.split(',', 1)
                        if len(parts) == 2:
                            username, password = parts
                            accounts.append({
                                'username': username.strip(),
                                'password': password.strip()
                            })
            else:
                if ',' in arg_accounts:
                    parts = arg_accounts.split(',', 1)
                    if len(parts) == 2:
                        username, password = parts
                        accounts.append({
                            'username': username.strip(),
                            'password': password.strip()
                        })

        print(f"解析到的账户数量: {len(accounts)}")
        return accounts

    def int2char(self, a):
        return BI_RM[a]

    def b64tohex(self, a):
        d = ""
        e = 0
        c = 0
        for i in range(len(a)):
            if list(a)[i] != "=":
                v = B64MAP.index(list(a)[i])
                if 0 == e:
                    e = 1
                    d += self.int2char(v >> 2)
                    c = 3 & v
                elif 1 == e:
                    e = 2
                    d += self.int2char(c << 2 | v >> 4)
                    c = 15 & v
                elif 2 == e:
                    e = 3
                    d += self.int2char(c)
                    d += self.int2char(v >> 2)
                    c = 3 & v
                else:
                    e = 0
                    d += self.int2char(c << 2 | v >> 4)
                    d += self.int2char(15 & v)
        if e == 1:
            d += self.int2char(c << 2)
        return d

    def rsa_encode(self, j_rsakey, string):
        rsa_key = f"-----BEGIN PUBLIC KEY-----\n{j_rsakey}\n-----END PUBLIC KEY-----"
        pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(rsa_key.encode())
        result = self.b64tohex((base64.b64encode(rsa.encrypt(f'{string}'.encode(), pubkey))).decode())
        return result

    def calculate_md5_sign(self, params):
        return hashlib.md5('&'.join(sorted(params.split('&'))).encode('utf-8')).hexdigest()

    def mask_username(self, username):
        """隐藏用户名，只显示前2位和后2位"""
        if len(username) > 4:
            return f"{username[:2]}****{username[-2:]}"
        else:
            return "****"  # 如果用户名太短，全部隐藏

    def login(self, username, password):
        """登录天翼云盘"""
        try:
            urlToken = "https://m.cloud.189.cn/udb/udb_login.jsp?pageId=1&pageKey=default&clientType=wap&redirectURL=https://m.cloud.189.cn/zhuanti/2021/shakeLottery/index.html"
            r = self.session.get(urlToken)
            pattern = r"https?://[^\s'\"]+"  # 匹配以http或https开头的url
            match = re.search(pattern, r.text)  # 在文本中搜索匹配
            if match:  # 如果找到匹配
                url = match.group()  # 获取匹配的字符串
            else:  # 如果没有找到匹配
                print("没有找到登录URL")
                return None

            r = self.session.get(url)
            pattern = r"<a id=\"j-tab-login-link\"[^>]*href=\"([^\"]+)\""  # 匹配id为j-tab-login-link的a标签，并捕获href引号内的内容
            match = re.search(pattern, r.text)  # 在文本中搜索匹配
            if match:  # 如果找到匹配
                href = match.group(1)  # 获取捕获的内容
            else:  # 如果没有找到匹配
                print("没有找到登录链接")
                return None

            r = self.session.get(href)
            captchaToken = re.findall(r"captchaToken' value='(.+?)'", r.text)[0]
            lt = re.findall(r'lt = "(.+?)"', r.text)[0]
            returnUrl = re.findall(r"returnUrl= '(.+?)'", r.text)[0]
            paramId = re.findall(r'paramId = "(.+?)"', r.text)[0]
            j_rsakey = re.findall(r'j_rsaKey" value="(\S+)"', r.text, re.M)[0]
            self.session.headers.update({"lt": lt})

            username = self.rsa_encode(j_rsakey, username)
            password = self.rsa_encode(j_rsakey, password)
            url = "https://open.e.189.cn/api/logbox/oauth2/loginSubmit.do"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/76.0',
                'Referer': 'https://open.e.189.cn/',
            }
            data = {
                "appKey": "cloud",
                "accountType": '01',
                "userName": f"{{RSA}}{username}",
                "password": f"{{RSA}}{password}",
                "validateCode": "",
                "captchaToken": captchaToken,
                "returnUrl": returnUrl,
                "mailSuffix": "@189.cn",
                "paramId": paramId
            }
            r = self.session.post(url, data=data, headers=headers, timeout=5)

            if r.status_code == 200 and r.json().get('result') == 0:
                print("登录成功")
                redirect_url = r.json()['toUrl']
                self.session.get(redirect_url)
                return self.session
            else:
                error_msg = r.json().get('msg', '未知错误') if r.status_code == 200 else '网络错误'
                print(f"登录失败: {error_msg}")
                return None
        except Exception as e:
            print(f"登录异常: {str(e)}")
            return None

    def sign_only(self, session, masked_username):
        """仅签到功能"""
        try:
            rand = str(round(time.time() * 1000))
            surl = f'https://api.cloud.189.cn/mkt/userSign.action?rand={rand}&clientType=TELEANDROID&version=8.6.3&model=SM-G930K'

            headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; SM-G930K Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36 Ecloud/8.6.3 Android/22 clientId/355325117317828 clientModel/SM-G930K imsi/460071114317824 clientChannelId/qq proVersion/1.0.6',
                "Referer": "https://m.cloud.189.cn/zhuanti/2016/sign/index.jsp?albumBackupOpened=1",
                "Host": "m.cloud.189.cn",
                "Accept-Encoding": "gzip, deflate",
            }

            # 签到
            response = session.get(surl, headers=headers)
            if response.status_code == 200:
                resp_json = response.json()
                netdiskBonus = resp_json.get('netdiskBonus', 0)

                if resp_json.get('isSign') is True:
                    print(f"账户 {masked_username}: 已经签到过了，签到获得{netdiskBonus}M空间")
                    result = f"签到获得{netdiskBonus}M空间(重复签到)"
                else:
                    print(f"账户 {masked_username}: 签到成功，签到获得{netdiskBonus}M空间")
                    result = f"签到获得{netdiskBonus}M空间"
            else:
                print(f"账户 {masked_username}: 签到请求失败")
                result = "签到请求失败"

            # 记录推送结果
            account_result = {
                'username': masked_username,
                'result': result
            }
            self.push_results.append(account_result)

            return result

        except Exception as e:
            print(f"账户 {masked_username} 签到异常: {str(e)}")
            result = f"异常: {str(e)}"

            # 记录推送结果
            account_result = {
                'username': masked_username,
                'result': result
            }
            self.push_results.append(account_result)

            return result

    def push_results_to_pushplus(self):
        """将结果推送到PUSH PLUS"""
        try:
            pushplus_token = os.getenv('PUSH_PLUS_TOKEN', '')
            if not pushplus_token:
                print("未配置PUSH_PLUS_TOKEN环境变量，跳过推送")
                return

            # 构建推送内容
            title = f"天翼云盘签到结果 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            content_lines = [
                f"# 天翼云盘签到结果",
                f"> 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"",
                f"## 签到统计",
                f"- 总账户数: {len(self.push_results)}",
                f"- 成功数: {sum(1 for r in self.push_results if '异常' not in r['result'] and '失败' not in r['result'])}",
                f"- 异常数: {sum(1 for r in self.push_results if '异常' in r['result'] or '失败' in r['result'])}",
                f"",
                f"## 详细结果",
            ]

            for idx, result in enumerate(self.push_results, 1):
                status_icon = "✅" if '异常' not in result['result'] and '失败' not in result['result'] else "❌"
                content_lines.append(f"### 账户 {idx}")
                content_lines.append(f"- 账号: {result['username']}")
                content_lines.append(f"- 结果: {status_icon} {result['result']}")
                content_lines.append("")

            content = "\n".join(content_lines)

            # 发送推送
            push_url = "https://www.pushplus.plus/send"
            data = {
                "token": pushplus_token,
                "title": title,
                "content": content,
                "template": "markdown"  # 使用markdown模板
            }

            response = requests.post(push_url, json=data)
            if response.status_code == 200:
                resp_json = response.json()
                if resp_json.get("code") == 200:
                    print(f"PUSH PLUS推送成功: {resp_json.get('msg', '推送成功')}")
                else:
                    print(f"PUSH PLUS推送失败: {resp_json.get('msg', '推送失败')}")
            else:
                print(f"PUSH PLUS推送请求失败: HTTP {response.status_code}")

        except Exception as e:
            print(f"PUSH PLUS推送异常: {str(e)}")

    def run(self):
        """主执行函数"""
        print("=" * 50)
        print(f"天翼云盘签到开始 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"共检测到 {len(self.accounts)} 个账户")
        print("=" * 50)

        for idx, account in enumerate(self.accounts, 1):
            username = account["username"]
            password = account["password"]
            masked_username = self.mask_username(username)

            print(f"\n开始处理第 {idx} 个账户: {masked_username}")

            # 登录
            session = self.login(username, password)
            if session:
                # 仅签到
                result = self.sign_only(session, masked_username)
            else:
                print(f"账户 {masked_username} 登录失败，跳过后续操作")
                account_result = {
                    'username': masked_username,
                    'result': "登录失败"
                }
                self.push_results.append(account_result)

            # 账户间延迟
            if idx < len(self.accounts):
                print("等待5秒后继续下一个账户...")
                time.sleep(5)

        # 输出汇总结果
        print("\n" + "=" * 50)
        print("签到任务完成汇总:")
        print("=" * 50)
        for idx, result in enumerate(self.push_results, 1):
            print(f"账户{idx}: {result['username']} -> {result['result']}")

        print(f"\n总处理账户数: {len(self.push_results)}")
        print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 推送结果到PUSH PLUS
        print("\n开始推送结果到PUSH PLUS...")
        self.push_results_to_pushplus()


if __name__ == "__main__":
    # 青龙面板环境变量设置示例:
    # export TIAN_YI_ACCOUNTS="手机号1,密码1;手机号2,密码2"
    # export PUSH_PLUS_TOKEN="你的PUSH PLUS TOKEN"

    signer = TianYiCloudSigner()
    signer.run()
