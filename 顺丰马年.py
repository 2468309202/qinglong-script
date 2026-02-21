# 当前脚本来自于 http://script.345yun.cn 脚本库下载！
# 当前脚本来自于 http://2.345yun.cn 脚本库下载！
# 当前脚本来自于 http://2.345yun.cc 脚本库下载！
# 脚本库官方QQ群1群: 429274456
# 脚本库官方QQ群2群: 1077801222
# 脚本库官方QQ群3群: 433030897
# 脚本库中的所有脚本文件均来自热心网友上传和互联网收集。
# 脚本库仅提供文件上传和下载服务，不提供脚本文件的审核。
# 您在使用脚本库下载的脚本时自行检查判断风险。
# 所涉及到的 账号安全、数据泄露、设备故障、软件违规封禁、财产损失等问题及法律风险，与脚本库无关！均由开发者、上传者、使用者自行承担。

EXCHANGE_COUPON = False # 蜂蜜兑券 True为启用、False为禁用[默认禁用]
HONEY_LOTTERY = False # 蜂蜜抽奖 True为启用、False为禁用[默认禁用]
DRAW_CARDS = False  # 周年庆卡牌抽奖 True为启用、False为禁用[默认禁用]
DRAGONBOAT_LOTTERY2 = True # False为直接开启端午活动
DISNEY_ACTIVITY = False  # 迪士尼主题活动 True为启用、False为禁用[默认启用]
YEAREND_2025_ACTIVITY = True

import os
import re
import io
import sys
import time
import json
import socket
import random
import logging
import hashlib
import requests
from notify import send
from datetime import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from urllib.parse import urlparse, parse_qs, unquote

# 禁用SSL警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# 日志
log_stream = io.StringIO()
logging.basicConfig(level=logging.INFO,format="%(message)s",handlers=[logging.StreamHandler(sys.stdout),logging.StreamHandler(log_stream)])
log = logging.getLogger()
inviteId = ['F5E70D771ABD4D86AFB0782313945C91','16A1E9AF32C1441894D27E0F1453F7CB','3ED135C9A3254CCFACA88781CD9B3A91', '6931380B6A234074A318CECD9E62089D','C883BE3AE638494B90BAB440A4CFFDEC',]


class SFAPI:
    def __init__(self, info, index):
        self.index = index + 1
        self.all_logs = [] 
        self.headers = {}
        # 解析账号信息
        if '#' in info:
            raw_url, self.deviceid = info.split('#', 1)
            self.url = unquote(raw_url.strip())
            self.deviceid = self.deviceid.strip()
        else:
            self.url = unquote(info.strip())
            self.deviceid = None

        log.info(f"\n====== 第{self.index}个账号 ======")

        # 初始化会话和代理
        self.proxy = self.fetch_proxy_ip()
        self.s = requests.Session()
        if self.proxy:
            self.s.proxies = {"http": f"http://{self.proxy}","https": f"http://{self.proxy}"}
        
        # 关闭SSL证书验证
        self.s.verify = False
        # 初始化用户信息
        self.user_id = ''
        self.phone = ''
        self.mobile = ''
        self.lottery_count = 0
        self.login_res = self.login(self.url)

    # 获取代理IP
    def fetch_proxy_ip(self, max_retries=3):
        proxy_url = os.getenv("ProxyIP")
        if not proxy_url:
            return None

        for attempt in range(max_retries):
            try:
                response = requests.get(proxy_url, timeout=5)
                proxy_ip = response.text.strip()
                if re.match(r'^\d+\.\d+\.\d+\.\d+:\d+$', proxy_ip):
                    return proxy_ip

                res = response.json()

                if res.get('code') == -1:
                    message = res.get('message', '未知错误')
                    print(f"[代理异常] {message}")
                    return None

            except Exception as e:
                print(f"[提取代理失败] 执行第 {attempt + 1} 次重试")
                time.sleep(3)
                
        return None

    # 签名
    def get_sign(self, config_mode, data={}):
        timestamp = str(int(round(time.time() * 1000)))
        if config_mode == "1":
            token = 'wwesldfs29aniversaryvdld29'
            sysCode = 'MCS-MIMP-CORE'
            raw_data = f'token={token}&timestamp={timestamp}&sysCode={sysCode}'
            signature = self.calculate_md5(raw_data)
            return {
                'sysCode': sysCode,
                'timestamp': timestamp,
                'signature': signature
            }

        else:
            input_string_1 = f'{data}&080R3MAC57J2{{A19!$3:WO{{I<1N$31BI'
            md5_hash_1 = self.calculate_md5(input_string_1)

            input_string_2 = (
                f"{self.deviceid}{timestamp}9.75.20"
                f"2NBF+BE4{{@P:@X${{Q9BAE>{{PAK!D:N*^CNsc{md5_hash_1}"
                f"6909dd64d423b255a14d5fff251eb97e&2NBF+BE4{{@P:@X${{Q9BAE>{{PAK!D:N*^"
            )
            md5_hash_2 = self.calculate_md5(input_string_2)

            key = "0HQ%H91K&AA{DH$*XV>XR)VKL:QFE{&%"
            input_string_3 = f"{md5_hash_2}&{key}"
            md5_hash_3 = self.calculate_md5(input_string_3)

            return md5_hash_3, timestamp

    # 计算 MD5
    def calculate_md5(self, input_string):
        return hashlib.md5(input_string.encode()).hexdigest()

    # 生成设备ID
    def get_deviceId(self, characters='abcdef0123456789'):
        result = ''
        for char in 'xxxxxxxx-xxxx-xxxx':
            if char == 'x':
                result += random.choice(characters)
            elif char == 'X':
                result += random.choice(characters).upper()
            else:
                result += char
        return result

    # 请求头配置
    def get_headers(self, config_mode, timestamp=None, syttoken=None):
        headers = {
                'Host': 'mcs-mimp-web.sf-express.com',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090551) XWEB/6945 Flue',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'accept-language': 'zh-CN,zh',
                'platform': 'MINI_PROGRAM'
            }
        if config_mode == "1":
            return headers

                

        elif config_mode == "3":
            headers.update({
                'syscode': 'MCS-MIMP-CORE',
                'channel': 'wxwdsj',
                'accept': 'application/json, text/plain, */*',
                'content-type': 'application/json;charset=UTF-8',
                'platform': 'MINI_PROGRAM'
            })

            return headers

        elif config_mode == "4":
            headers['channel'] = 'wxwdsj'
            return headers

        elif config_mode == "5":
            headers.update({
                'syscode': 'MCS-MIMP-CORE',
                'channel': 'newshoujianapp',
                'accept': 'application/json, text/plain, */*',
                'content-type': 'application/json;charset=UTF-8',
                'platform': 'SFAPP'
            })

            return headers

        elif config_mode == "6":
            headers.update({
                'syscode': 'MCS-MIMP-CORE',
                'channel': '32annidb',
                'accept': 'application/json, text/plain, */*',
                'content-type': 'application/json',
                'platform': 'SFAPP'
            })

            return headers

        else:
            # 配置2
            return {
                "Host": "ccsp-egmas.sf-express.com",
                "jsbundle": "6909dd64d423b255a14d5fff251eb97e",
                "srcdeviceguid": "DUrM7IPORlQt0kGfg3xEh5BpwAqH72g8i364",
                "clientversion": "9.75.20",
                "languagecode": "sc",
                "systemversion": "13",
                "deviceid": self.deviceid,
                "regioncode": "CN",
                "carrier": "unknown",
                "screensize": "1440x3200",
                "syttoken": syttoken,  # 计算后的签名
                "timeinterval": timestamp,
                "model": "23013RK75C",
                "mediacode": "AndroidML",
                "memberid": self.user_id,
                "content-type": "application/json",
                "accept-encoding": "gzip",
                "user-agent": "okhttp/4.9.1"
            }

    # 请求方法
    def do_request(self, url, data={}, req_type='post',max_retries=10, timeout=10, retry_delay=2, config_mode="1"):

        sign_data = self.get_sign(config_mode=config_mode, data=data)
        if config_mode == "1":
            headers = self.get_headers(config_mode=config_mode)
            headers.update({
                'sysCode': sign_data['sysCode'],
                'timestamp': sign_data['timestamp'],
                'signature': sign_data['signature']
            })
        else:
            headers = self.get_headers(
                config_mode=config_mode,
                timestamp=sign_data[1],
                syttoken=sign_data[0]
            )

        for attempt in range(1, max_retries + 1):
            error_msg = "未知错误"
            try:
                proxies = {'http': self.proxy, 'https': self.proxy} if hasattr(self, 'proxy') and self.proxy else None
                if req_type.lower() == 'post':
                    if config_mode == "2":
                        response = self.s.post(url, data=data, headers=headers, proxies=proxies, timeout=timeout)
                    else:
                        response = self.s.post(url, json=data, headers=headers, proxies=proxies, timeout=timeout)

                elif req_type.lower() == 'get':
                    response = self.s.get(url, params=data, headers=headers, proxies=proxies, timeout=timeout)

                else:
                    print(f"❌ Unsupported request type: {req_type}")
                    return None

                if response.status_code == 200:
                    return response.json()

            except requests.exceptions.Timeout:
                error_msg = '⏳ 请求超时'
            except requests.exceptions.SSLError:
                error_msg = '🔐 SSL 错误'
            except requests.exceptions.ProxyError:
                error_msg = '代理连接失败'
                self.proxy = self.fetch_proxy_ip()
                print(f"🔄 已更换代理为: {self.proxy}")
            except ValueError as e:
                error_msg = f'数据异常: {str(e)}'
            except requests.exceptions.RequestException as e:
                error_msg = f'未知错误: {type(e).__name__}'
                print(f'⚠️ {error_msg} - {str(e)}')

            print(f'⚠️ {error_msg} 重试第{attempt}次')
            if attempt < max_retries:
                time.sleep(retry_delay)

        print(f'❌ 请求 {url} 失败，已达最大重试次数')
        return None

    # 登录
    def login(self, login_url, max_retries=3, retry_delay=2):
        if hasattr(self, 'proxy') and self.proxy:
            print(f"代理IP：{self.proxy}")
        for attempt in range(1, max_retries + 1):
            error_msg = "未知错误"
            try:
                proxies = {'http': self.proxy, 'https': self.proxy} if hasattr(self, 'proxy') and self.proxy else None
                ress = self.s.get(login_url,headers=self.get_headers("1"),timeout=10,proxies=proxies,allow_redirects=True)
                match = re.search(r'"token"\s*:\s*"([A-Za-z0-9]+)"', ress.text)
                if match:
                    self.token = match.group(1)
                self.user_id = self.s.cookies.get_dict().get('_login_user_id_', '')
                self.phone = self.s.cookies.get_dict().get('_login_mobile_', '')
                self.mobile = self.phone
                if self.phone != '':
                    log.info(f'✅ {self.mobile}')
                    print(f'登陆成功')
                    self.sign_in()
                    return True
            
            except requests.exceptions.Timeout:
                error_msg = '请求超时'
            except requests.exceptions.SSLError:
                error_msg = 'SSL验证失败'
            except requests.exceptions.ProxyError:
                error_msg = '代理连接失败'
                self.proxy = self.fetch_proxy_ip()
                print(f"🔄 已更换代理为: {self.proxy}")
            except ValueError as e:
                error_msg = f'数据异常: {str(e)}'
            except Exception as e:
                error_msg = f'未知错误: {type(e).__name__}'
                print(f'⚠️ {error_msg} - {str(e)}')
                if attempt == max_retries:
                    print('❌ 最终失败: 遇到未处理的异常')
                return False
            
            print(f'⚠️ {error_msg} 重试第{attempt}次')
            if attempt < max_retries:
                time.sleep(retry_delay)
        
        print('❌ 登录失败: 已达最大重试次数')
        return False

    # 签到
    def sign_in(self):
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~integralTaskSignPlusService~automaticSignFetchPackage'
        data = {
            "comeFrom": "vioin",
            "channelFrom": "WEIXIN"
        }
        try:
            response = self.do_request(url, data, req_type="post", config_mode="1")
            if response.get('success') == True:
                if response.get('obj') and response['obj'].get('integralTaskSignPackageVOList'):
                    packet_name = response["obj"]["integralTaskSignPackageVOList"][0]["packetName"]
                    print(f'签到成功，获得{packet_name}')
                else:
                    print(f'已完成-签到')

        except Exception as e:
            print(f'⚠️ [签到异常] {str(e)}')


    def get_SignTaskList(self):
        url = "https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~integralTaskStrategyService~queryPointTaskAndSignFromES"
        data = {
            'channelType': '1',
            'deviceId': self.get_deviceId(),
        }
        excluded_tasks = [
            "用行业模板寄件下单",
            "用积分兑任意礼品",
            "去新增一个收件偏好",
            "参与积分活动",
            "每月累计寄件",
            "设置你的顺丰ID",
            "完成每月任务"  
        ]

        try:
            response = self.do_request(url, data, req_type="post", config_mode="1")
            if response.get('success') == True and response.get('obj') != []:
                tasks = response["obj"].get("taskTitleLevels", [])
                filtered_tasks = [task for task in tasks if task["title"] not in excluded_tasks]
                if not filtered_tasks:
                    log.info("⚠️ 无积分任务 - 请先寄件进行养号解禁")

                for task in filtered_tasks:
                    # 提取任务关键属性
                    self._set_task_attrs(task)
                    
                    status = task["status"]
                    if status == 3:
                        print(f'已完成-{self.title}')
                        continue
                    
                    if self.title in excluded_tasks:
                        continue
                    
                    # 如果没有taskCode，尝试从buttonRedirect提取
                    if not hasattr(self, 'taskCode') or not self.taskCode:
                        # print(f'任务"{self.title}"缺少taskCode，尝试从buttonRedirect提取...')
                        if 'buttonRedirect' in task:
                            self._extract_taskcode_from_url(task['buttonRedirect'])
                    
                    # 如果还是没有taskCode，跳过此任务
                    if not hasattr(self, 'taskCode') or not self.taskCode:
                        print(f'任务"{self.title}"无法获取taskCode，跳过')
                        continue
                    
                    print(f'未完成-{self.title}')
                    self.doTask(self.taskCode)

            self.get_points()

        except Exception as e:
            print(f'⚠️ 积分任务查询异常: {e}')
            return None

    def _set_task_attrs(self, task: dict) -> None:
        """提取任务关键属性"""
        self.taskId = str(task["taskId"])
        self.taskCode = task.get("taskCode", "")
        self.strategyId = str(task["strategyId"])
        self.title = task["title"]
        self.point = task["point"]
        
    def _extract_taskcode_from_url(self, url: str) -> None:
        """从URL中提取taskCode"""
        try:
            # 解析URL
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            
            # 获取 _ug_view_param 参数
            if "_ug_view_param" in query_params:
                ug_view_param = unquote(query_params["_ug_view_param"][0])
                # 解析JSON字符串
                param_dict = json.loads(ug_view_param)
                # 提取taskId
                if "taskId" in param_dict:
                    self.taskCode = param_dict["taskId"]
                    # print(f'✓ 从buttonRedirect中提取到taskCode: {self.taskCode}')
            
            # 如果还有其他的参数包含taskId，也可以尝试提取
            elif "taskId" in query_params:
                self.taskCode = query_params["taskId"][0]
                print(f'✓ 从URL参数中提取到taskCode: {self.taskCode}')
                
        except json.JSONDecodeError as e:
            print(f'解析_ug_view_param失败: {e}')
        except Exception as e:
            print(f'从URL提取taskCode失败: {e}')

    # 积分任务执行
    def doTask(self, task_Code):
        time.sleep(3)
        if self.title == "领任意生活特权福利":
            success = self.get_LifeBenefitsCoupons(task_type="points_query", task_Code=task_Code)
            if success:
                self.receiveTask(task_Code)
        
        elif self.title == "完成连签7天":
            self.receiveTask(task_Code)
            return

        else:
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonRoutePost/memberEs/taskRecord/finishTask'
            data = {
                'taskCode': task_Code
            }
            try:
                response = self.do_request(url, data, req_type="post", config_mode="1")
                if response.get('success') == True:
                    self.receiveTask(task_Code)
                else:
                    error_msg = response.get("errorMessage", "未知错误")
                    print(f"执行失败：{error_msg}")
                    return False
            
            except Exception as e:
                print(f'⚠️ 积分任务执行异常：{str(e)}')
                return False   

    # 领取已完成积分任务奖励
    def receiveTask(self, task_Code):
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~integralTaskStrategyService~fetchIntegral'
        data = {
            "strategyId": self.strategyId,
            "taskId": self.taskId,
            "taskCode": task_Code,
            "deviceId": self.get_deviceId()
        }

        try:
            response = self.do_request(url, data, req_type="post", config_mode="1")
            if response.get('success') == True:
                print(f'执行成功，获得{self.point}积分')
                return True

            else:
                error_msg = response.get("errorMessage", "未知错误")
                print(f'{self.title}奖励领取失败：{error_msg}')
                return False
        
        except Exception as e:
            print(f'⚠️ 积分奖励领取异常：{str(e)}')
            return False

    # 积分查询
    def get_points(self):
        if not self.deviceid:
            url = "https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberIntegral~userInfoService~queryUserInfo"
            data = {
                "sysCode": "ESG-CEMP-CORE",
                "optionalColumns": ["usablePoint", "cycleSub", "leavePoint"],
                "token": "zeTLTYeG0bLetfRk"
            }
            config_mode = "1"

        else:
            url = "https://ccsp-egmas.sf-express.com/cx-app-member/member/app/point/queryMemberPointInside"
            data = {
                "userId": self.user_id,
                "flag": "2"
            }
            config_mode = "2"
        try:
            if config_mode == "2":
                data_str = json.dumps(data, separators=(',', ':'))
                response = self.do_request(url, data=data_str, req_type="post", config_mode=config_mode)
            else:
                response = self.do_request(url, data, req_type="post", config_mode=config_mode)

            if response.get("errorMessage") == "您的登录信息已失效，请重新登录":
                url = "https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberIntegral~userInfoService~queryUserInfo"
                data = {
                    "sysCode": "ESG-CEMP-CORE",
                    "optionalColumns": ["usablePoint", "cycleSub", "leavePoint"],
                    "token": "zeTLTYeG0bLetfRk"
                }
                config_mode = "1"
                response = self.do_request(url, data, req_type="post", config_mode=config_mode)

            if response.get('success') == True:
                obj = response.get('obj', {})
                usable_point = obj.get("usablePoint", 0)
                expiringMessage = obj.get("expiringMessage")
                if expiringMessage:
                    log.info(f"当前积分：【{usable_point}】  {expiringMessage}")
                else:
                    log.info(f"当前积分：【{usable_point}】")
          

        except Exception as e:
            print(f'⚠️ 积分查询异常：{str(e)}')
            return None

    # 新增自动签到方法
    def automatic_daily_sign(self):
        try:
            # 自动签到请求
            sign_url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~integralTaskSignPlusService~automaticSignFetchPackage'
            sign_data = {"comeFrom":"vioin","channelFrom":"SFAPP"}
            
            response = self.do_request(sign_url, sign_data, req_type="post", config_mode="1")
            
            if response.get('success'):
                print("已完成-APP额外签到")
                # 领取连签奖励
                self.get_sign_rewards_record()
                self.receive_sign_rewards()
            else:
                print(f"⚠️ 自动签到失败：{response.get('errorMessage', '未知错误')}")

        except Exception as e:
            print(f'⚠️ 自动签到异常：{str(e)}')

    # 新增领取连签奖励方法
    def receive_sign_rewards(self):
        try:
            # 查询可领取奖励
            query_url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~integralTaskSignPlusService~getUnFetchPointAndDiscount'
            query_response = self.do_request(query_url, {}, req_type="post", config_mode="1")
            
            if query_response.get('success') and query_response.get('obj'):
                for reward in query_response['obj']:
                    # 领取奖励包
                    receive_url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberIntegral~packetService~receivePacket'
                    receive_data = {"packageId": reward['packageId']}
                    
                    receive_response = self.do_request(receive_url, receive_data, req_type="post", config_mode="1")
                    if receive_response.get('success'):
                        print(f"✅ 成功领取{reward['packetName']}")
                    else:
                        print(f"✅ 成功领取{reward['packetName']}")
                        
        except Exception as e:
            print(f'⚠️ 领取奖励异常：{str(e)}')


    def get_sign_rewards_record(self):
        """
        查询连续签到奖励结果（最近6次）
        """
        try:
            url = "https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~integralTaskSignPlusService~getUserOneWeekSignRecord"
            data = {}
            
            # 发送请求
            response = self.do_request(url, data, req_type="post", config_mode="1")
            
            if not response.get("success"):
                print(f"⚠️ 签到记录查询失败：{response.get('errorMessage', '未知错误')}")
                return
            
            records = response.get("obj", [])
            recent_records = records[:6]  # 取最近6条记录
            
            if not recent_records:
                print("📅 暂无签到记录")
                return
            
            print("【连续签到奖励记录】")
            for record in recent_records:
                # 转换时间戳为可读格式
                sign_date = time.strftime("%Y-%m-%d", time.localtime(record["recordTm"] / 1000))
                
                # 格式化奖励信息
                reward_info = f"{record['packetName']}x{record['commodityCount']}"
                if record.get("invalidTm"):
                    reward_info += f" (有效期至:{record['invalidTm']})"
                
                # 输出结果
                print(f"{sign_date} 第{record['countDay']}天签到: {reward_info}")
            
            #print(f"共计 {len(recent_records)} 条记录\n")
        
        except Exception as e:
            print(f'⚠️ 签到记录查询异常：{str(e)}')


    # 免单券查询
    def query_free_coupon(self):
        url = "https://mcs-mimp-web.sf-express.com/mcs-mimp/coupon/available/list"
        data = {
            "type": "1",
            "pageSize": 10,
            "pageNum": 1,
            "couponType": "",
            "labelCode": "0",
            "channel": "SFAPP"
        }
        try:
            response = self.do_request(url, data, req_type="post", config_mode="1")
            #print(f"{response}")
            if response.get('success') and response.get('obj'):
                keywords = ["免单", "15元运费券"]
                filtered_coupons = [coupon for coupon in response['obj']if any(keyword in coupon.get('couponName', '') for keyword in keywords)]
                if filtered_coupons:
                    for coupon in filtered_coupons:
                        log.info(f"{coupon.get('couponName')}：{coupon.get('couponNum', 0)}张，过期时间：{coupon.get('invalidTm')}")

                return filtered_coupons

        except Exception as e:
            print(f'⚠️ 免单券查询异常：{str(e)}')
            return None

    # 待支付订单
    def query_unpay_orders(self):
        if not self.deviceid:
            return
        url = "https://ccsp-egmas.sf-express.com/cx-app-query/query/app/sfpay/queryUnPayOrderList"
        data = {
            "pageSize": "10",
            "page": "1",
            "memberId": self.user_id
        }

        try:
            data_str = json.dumps(data, separators=(',', ':'))
            response = self.do_request(url, data=data_str, req_type="post", config_mode="2")
            if response.get('success') == True:
                orders = []
                for order in response['obj']['unpaidOrderDetail']:
                    orders.append({"waybillNo": order.get('waybillNo', ''), "amount": float(order.get('amt', '0')) / 100})
                for idx, order in enumerate(orders, 1):
                    log.info(f"⚠️ 待支付订单{idx}: 单号 {order['waybillNo']} | 金额 {order['amount']}元")

            else:
                error_msg = response.get('errorMessage', '')
                if error_msg == '您的登录信息已失效，请重新登录':
                    log.info(f"⚠️ 待支付订单-deviceid与账号不匹配")


        except Exception as e:
            print(f'⚠️ 待支付订单查询异常：{str(e)}')    

    # 生活特权领券
    def get_LifeBenefitsCoupons(self, task_type, task_Code):
        if task_type == "points_query":
            data = {"memGrade": 3, "categoryCode": "SHTQ"}
        else:
            data = {"memGrade": 2, "categoryCode": "SHTQ", "showCode": "SHTQWNTJ"}

        url = "https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberGoods~mallGoodsLifeService~list"

        try:
            # 先查询生活特权商品列表（使用config_mode=1）
            response = self.do_request(url, data, req_type="post", config_mode="1")
            if not response.get('success') or not response.get('obj'):
                print("⚠️ 生活特权商品列表查询失败")
                return False

            goodsList = []
            for category in response["obj"]:
                goodsList.extend(category.get("goodsList", []))

            # 优先筛选顺丰同城商品
            sftc_ticket = next((goods for goods in goodsList if goods.get('brandName') == '顺丰同城'), None)
            if sftc_ticket:
                # 检查商品是否可兑换
                if sftc_ticket.get('exchangeStatus', 2) >= 2 or sftc_ticket.get('exchangeMemLevel', 1) > 0:
                    print("⚠️ 顺丰同城券当前不可兑换")
                    return False

                # 构建完整请求参数（包含所有商品原始字段）
                request_data = {
                    **sftc_ticket,  # 继承商品所有原始字段（关键）
                    "orderSource": "H5",
                    "taskCode": task_Code,
                    "from": "LIFE_MALL_EXCHANGE"
                }

                # 使用config_mode=5（匹配抓包的channel和platform）
                url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberGoods~pointMallService~pushCommonOrderInfoH5'
                response = self.do_request(url, request_data, req_type="post", config_mode="5")
                
                if response.get('success'):
                    # print('✓ 生活特权（顺丰同城）领券成功')
                    return True
                else:
                    error_msg = response.get('errorMessage', '未知错误')
                    print(f'⚠️ 顺丰同城券领取失败：{error_msg}')
                    return False

            # 如果没有顺丰同城券，尝试其他商品
            available_goods = [goods for goods in goodsList if goods.get('currentStore', 0) > 0]
            selected_goods = None
            for goods in available_goods:
                exchangeStatus = goods.get('exchangeStatus', -1)
                exchangeMemLevel = goods.get('exchangeMemLevel', -1)
                if exchangeStatus < 2 and exchangeMemLevel == 0:
                    selected_goods = goods
                    break
            
            if selected_goods:
                self.goodsNo = selected_goods['goodsNo']
                url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberGoods~pointMallService~createOrder'
                data = {
                    "from": "Point_Mall",
                    "orderSource": "POINT_MALL_EXCHANGE",
                    "goodsNo": self.goodsNo,
                    "quantity": 1,
                    "taskCode": task_Code
                }
                response = self.do_request(url, data, req_type="post", config_mode="1")
                if response.get('success') == True:
                    return True
                else:
                    print(f'⚠️ 其他特权领券失败：{response.get("errorMessage", "未知错误")}')
                    return False

            else:
                print("⚠️ 无可用的生活特权商品")
                return False

        except Exception as e:
            print(f'⚠️ 生活特权领券异常：{str(e)}')
            return False

    # 采蜜大冒险
    def honey_damaoxian(self,task_type):
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~receiveExchangeGameService~gameReport'
        data = {'gatherHoney': 20}

        try:
            response = self.do_request(url, data, req_type="post", config_mode="1")
            if response and response.get("success") and response.get("obj"):
                self.receive_honeyTask(task_type)

            elif response.get("errorMessage") == '容量不足':
                self.honey_expand(task_type)
        
            else:

                print(f"采蜜大冒险失败！")

        except Exception as e:
            print(f'⚠️ 采蜜大冒险异常: {e}')
            return None

    # 蜂蜜领取
    def receive_honeyTask(self, task_type):
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~receiveExchangeIndexService~receiveHoney'
        data = {"taskType": task_type}
        try:
            response = self.do_request(url, data, req_type="post", config_mode="3")
            if response.get("errorCode") == "994003":
                return

            if response.get('success') == True:
                print(f"{self.task_name}领取完成")

            elif response.get("errorMessage") == '容量不足':
                self.honey_expand(task_type)

            #else:
            #    print(f"{self.task_name}领取失败")

        except Exception as e:
            print(f'⚠️ 蜂蜜领取异常: {e}')
            return None
    
    # 蜂蜜扩容
    def honey_expand(self,task_type):
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~receiveExchangeIndexService~expand'
        data = {}
        try:
            response = self.do_request(url, data, req_type="post", config_mode="1")
            stu = response.get('success', False)
            if stu:
                obj = response.get('obj')
                print(f'容量不足已扩容-{obj}')
                self.receive_honeyTask(task_type)

        except Exception as e:
            print(f'⚠️ 蜂蜜扩容异常: {e}')
            return None



    # 蜂蜜兑换库存
    def query_honey_stock(self):
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~receiveExchangeGiftBagService~list'
        data = {"exchangeType": "EXCHANGE_SFC"}
        try:
            response = self.do_request(url, data, req_type="post", config_mode="4")
            stock_list = response["obj"]
            valid_coupons = [coupon for coupon in stock_list if coupon['giftBagWorth'] in [23.0, 20.0, 15.0]]
            exchanged_coupons = []
            for coupon in sorted(valid_coupons, key=lambda x: x['giftBagWorth'], reverse=True):
                while self.usableHoney >= coupon['exchangeHoney']:
                    self.usableHoney -= coupon['exchangeHoney']
                    self.exchange_coupon(coupon)
                    exchanged_coupons.append(coupon)

                if self.usableHoney > 0:
                    self.honey_lottery()
                        
            return exchanged_coupons

        except Exception as e:
            print(f'⚠️ 蜂蜜兑换库存异常: {e}')
            return None

    # 蜂蜜兑券
    def exchange_coupon(self, coupon_item):
        if not EXCHANGE_COUPON:
            return

        rule_code = coupon_item["ruleCode"]
        coupon_name = coupon_item["giftBagName"]
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~receiveExchangeGiftBagService~exchange'
        data = {
            "exchangeType": "EXCHANGE_SFC",
            "ruleCode": rule_code
        }
        try:
            response = self.do_request(url, data, req_type="post", config_mode="5")
            if response.get('success') == True:
                print(f"{coupon_name}兑换成功")
                print(f"剩余蜂蜜: 【{self.usableHoney}】")
            else:
                print(f"兑换失败: {response.get('errorMsg', '未知错误')}")

        except Exception as e:
            print(f'⚠️ 蜂蜜兑换库存异常: {e}')

    # 蜂蜜抽奖
    def honey_lottery(self):
        if not HONEY_LOTTERY:
            return
        if self.usableHoney < 500:
            return
        if self.lottery_count >= 5:
            return
        if self.usableHoney >= 1000:
            lottery_type = "highValue"
        else:
            lottery_type = "lowValue"
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~receiveExchangeGiftBagService~honeyLottery'
        data = {"type": lottery_type}
        try:
            response = self.do_request(url, data, req_type="post", config_mode="5")
            error_code = response.get('errorCode')
            if error_code in ['916012', '916007']:
                return

            if response.get('success') == True:
                lottery_result = response.get('obj')
                consumed_honey = 1000 if lottery_type == "highValue" else 500
                self.usableHoney -= consumed_honey
                if lottery_result.get('productList'):
                    for product in lottery_result['productList']:
                        if "丰蜜" in product['productName']:
                            prize_honey = product['amount']
                            self.usableHoney += prize_honey
                            print(f"抽奖获得蜂蜜: {prize_honey}")
                            print(f"剩余蜂蜜: 【{self.usableHoney}】")
                        else:
                            log.info(f"抽奖获得奖品: {lottery_result['giftBagName']}")

                        self.lottery_count += 1

                        if self.usableHoney >= 500 and self.lottery_count < 5:
                            self.honey_lottery()

            else:
                print(f"抽奖失败: {response.get('errorMsg', '未知错误')}")
        
        except Exception as e:
            print(f'⚠️ 蜂蜜抽奖异常: {e}')

    # 周年庆
    def anniversary2025_taskList(self):
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~anniversary2025TaskService~fetchTasksReward'
        data = {"channelType": "SFAPP"}
        completed_tasks = []
        incomplete_tasks = []
        # 排除特定的任务类型
        excluded_task_types = [
            "INTEGRAL_EXCHANGE",  # 积分兑换次数
            "INVITEFRIENDS_PARTAKE_ACTIVITY",  # 邀好友首次访问活动
            "EXCHANGE_INTEGRAL_MALL",  # 积分兑礼品 低至5折
            "SEND_SUCCESS_RECALL",  # 去寄快递
            "OPEN_SUPER_CARD",  # 开通至尊会员
            "OPEN_FAMILY_CARD",  # 开通亲情卡
            "CHARGE_NEW_EXPRESS_CARD_REBATE",  # 充100元得132元
            "CHARGE_NEW_EXPRESS_CARD"  # 充值新速运通全国卡
        ]
        try:
            response = self.do_request(url, data, req_type="post", config_mode="1")

        except Exception as e:
            print(f'⚠️ 活动主界面次数初始奖励异常: {e}')
            return None

        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~anniversary2025ClaimService~giveWealthChance'
        data ={}
        try:
            response = self.do_request(url, data, req_type="post", config_mode="6")
            if response.get('success') == True:
                print(f"周年庆抽卡次数耗尽等待30秒领取1次成功")

        except Exception as e:
            print(f'⚠️ 周年庆抽卡次数耗尽等待30秒领取1次异常: {e}')
            return None

        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~activityTaskService~taskList'
        data = {
            'activityCode': 'ANNIVERSARY_2025',
            'channelType': 'SFAPP'
        }
        try:
            response = self.do_request(url, data, req_type="post", config_mode="1")
            if response.get('success') and response.get('obj'):
                tasks = response.get('obj', [])
                for task in tasks:
                    if task['status'] in [1, 3]:
                        completed_tasks.append(task['taskName'])
                    elif task['taskType'] not in excluded_task_types:
                        incomplete_tasks.append(task)
                
                if completed_tasks:
                    for task in completed_tasks:
                        print(f"已完成-{task}")
                
                if incomplete_tasks:
                    for task in incomplete_tasks:
                        print(f"未完成-{task['taskName']}")
                        if task['taskName'] == "为顺丰送生日祝福" or 'taskCode' in task:
                            self.execute_incomplete_task(task)

            self.anniversary2025_draw_card()
                            
        except Exception as e:
            print(f'⚠️ 活动任务查询异常: {e}')
            return None

    # 周年庆任务执行
    def execute_incomplete_task(self, task):
        if task['taskName'] == '领取寄件会员权益':
            self.claim_equity()
        
        elif task['taskName'] == '为顺丰送生日祝福':
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~anniversary2025WishService~sendWish'
            data = {}
            try:
                response = self.do_request(url, data, req_type="post", config_mode="1")
                if response.get('success') == True:
                    print(f"{task['taskName']} 执行成功!")
                else:
                    print(f"{task['taskName']} 执行失败!")

            except Exception as e:
                print(f'⚠️ 为顺丰送生日祝福异常: {e}')
                return None

        else:
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonRoutePost/memberEs/taskRecord/finishTask'
            data = {'taskCode': task['taskCode']}
            try:
                response = self.do_request(url, data, req_type="post", config_mode="1")
                if response.get('success') == True:
                    print(f"{task['taskName']} 执行成功!")
                else:
                    print(f"{task['taskName']} 执行失败!")

            except Exception as e:
                print(f'⚠️ 周年庆任务执行异常: {e}')
                return None

    # 周年庆抽卡
    def anniversary2025_draw_card(self):
        time.sleep(5)
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~anniversary2025ClaimService~claimStatus'
        data = {}
        last_draw_response = None
        balance = 0
        card_names = {
            'DAI_BI': '坐以待币',
            'DING_ZHU': '都顶得住',
            'TIETIE_CARD': '贴贴卡',
            'ZHI_SHUI': '心如止水',
            'CHENG_GONG': '成功人士',
            'GAN_FAN': '干饭圣体'
        }
        try:
            response = self.do_request(url, data, req_type="post", config_mode="1")
            if response.get('success') == True:
                balance = next((account.get('balance', 0) for account in response.get('obj', {}).get('currentAccountList', [])if account.get('currency') == 'CLAIM_CHANCE'),0)
                print(f"剩余抽卡次数：{balance}")

            if balance > 0:
                url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~anniversary2025ClaimService~claim'
                for i in range(balance):
                    time.sleep(random.uniform(1, 2))
                    try:
                        response = self.do_request(url, data, req_type="post", config_mode="1")
                        if response.get('success') == True:
                            last_draw_response = response
                            received_list = response.get('obj', {}).get('receivedAccountList', [])
                            claim_award = response.get('obj', {}).get('claimAward', {})
                            rewards = []
                            for item in received_list:
                                rewards.append(f"{card_names.get(item.get('currency'), item.get('currency'))} × {item.get('amount')}")

                            if claim_award:
                                rewards.append(f"{claim_award.get('productName')} × {claim_award.get('amount')}")

                            reward_str = ", ".join(rewards) if rewards else "无"
                            print(f"第 {i+1} 次抽卡获得：{reward_str}")

            

                    except Exception as e:
                        print(f'⚠️ 周年庆抽卡异常: {e}')
                        return None
            
            final_response = last_draw_response if last_draw_response else response
            if final_response:
                current_cards = final_response.get('obj', {}).get('currentAccountList', [])
                card_info = [f"{card_names.get(card.get('currency'), card.get('currency'))} × {card.get('balance')}"for card in current_cards if card.get('currency') != 'CLAIM_CHANCE']
                log.info("----- 周年庆卡片信息 -----\n" + "\n".join(card_info))

                card_counts = {'DAI_BI': 0, 'DING_ZHU': 0, 'ZHI_SHUI': 0, 'CHENG_GONG': 0, 'GAN_FAN': 0}
                for card in current_cards:
                    currency = card.get('currency')
                    if currency in card_counts:
                        card_counts[currency] = card.get('balance', 0)
                
                available_card_types = {k: v for k, v in card_counts.items() if v > 0}

                while len(available_card_types) >= 5:
                    currency_list = list(available_card_types.keys())[:5]
                    draw_count = min(available_card_types[k] for k in currency_list)
                    for _ in range(draw_count):
                        if not self.draw_cards(currency_list):
                            return

                    for card in currency_list:
                        available_card_types[card] -= draw_count

                    available_card_types = {k: v for k, v in available_card_types.items() if v > 0}
                
                while len(available_card_types) >= 4:
                    currency_list = list(available_card_types.keys())[:4]
                    draw_count = min(available_card_types[k] for k in currency_list)
                    for _ in range(draw_count):
                        if not self.draw_cards(currency_list):
                            return
                    for card in currency_list:
                        available_card_types[card] -= draw_count
                    
                    available_card_types = {k: v for k, v in available_card_types.items() if v > 0}

        except Exception as e:
            print(f'⚠️ 周年庆抽卡次数查询异常: {e}')
            return None

    # 周年庆卡牌抽奖
    def draw_cards(self, currency_list):
        if not DRAW_CARDS:
            return

        time.sleep(1)
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~anniversary2025LotteryService~prizeDraw'
        data = {"currencyList": currency_list}
        try:
            response = self.do_request(url, data, req_type="post", config_mode="6")
            if response.get('success') is False:
                error_message = response.get('errorMessage', '未知错误')
                print(f"{error_message}")
                return False

            if response.get('success') == True:
                gift_bag_name = response.get('obj', {}).get('giftBagName', '未知奖励')
                product_list = response.get('obj', {}).get('productDTOList', [])
                all_rewards = [gift_bag_name] + [product.get('productName', '') for product in product_list]
                is_physical = not any("券" in reward for reward in all_rewards)

                if is_physical:
                    log.info(f"卡牌抽奖成功！获得：{gift_bag_name}") # 实物推送
                else:
                    print(f"卡牌抽奖成功！获得：{gift_bag_name}") # 券普通打印
                
                return True

        except Exception as e:
            print(f'⚠️ 卡牌抽奖请求失败: {e}')
 
    # 领取寄件会员权益
    def claim_equity(self):
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberManage~memberEquity~equityList' # 查询可领取权益
        data = {'envConfig': '1'}
        try:
            response = self.do_request(url, data, req_type="post", config_mode="1")
            equity_list = response.get('obj', {}).get('receiveEquityLists', [])
            received_count = 0
            for equity in equity_list:
                equity_key = equity.get('equityKey')
                equity_name = equity.get('equityName')
                is_to_receive = equity.get('isToReceive', 0)
                if is_to_receive == 1:
                    claim_url = ""
                    claim_data = {}
                    # 超寄星期三权益
                    if equity_key == 'super_send_wed':
                        claimable_equities = []
                        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~weeklySendApiService~freePacketInfo'
                        data = {}
                        received_count = 0
                        response = self.do_request(url, data, req_type="post", config_mode="1")
                        if isinstance(response, dict) and 'obj' in response:
                            free_packets = response['obj']
                            claimable_packets = [p for p in free_packets if p.get('giftBagStatus') == 1]
                            if claimable_packets:
                                for packet in claimable_packets:
                                    rule_code = packet.get('ruleCode')
                                    url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~weeklySendApiService~receiveFreePacket'
                                    data = {'ruleCode': rule_code}
                                    response = self.do_request(url, data, req_type="post", config_mode="1")
                                    if response.get('success') == True:
                                        received_count += 1

                    # 惊喜权益
                    if equity_key in ['surprise_benefit']:
                        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberManage~memberEquity~commonEquityReceive'
                        data = {"key": equity_key}
                        # 升级有礼
                        if equity_key == 'upgrade_gift':
                            data = {"key": equity_key}
                            data["channel"] = "point240613"

                    # 保价优惠
                    elif equity_key in ['valuation_services']:
                        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberManage~memberEquity~commonEquityReceive'
                        data["strategyCode"] = "HYQY202211160000103"
                         # 密钥认证
                        if equity_key == 'forward_return':
                            data = {"strategyCode": "HYQY202209010000403"}

                    if url and claim_data:
                        response = self.do_request(url, data, req_type="post", config_mode="1")
                        if response.get('success') == True:
                            print(f"{equity_name} 领取成功！")
                            received_count += 1
                        else:
                            print(f"{equity_name} 领取失败，请稍后再试。")
            
            if received_count == 0:
                print("😵‍💫 寄件会员券-查询库存暂时无可领取")

        except Exception as e:
            print(f"领取寄件会员权益时发生错误: {e}")

    # 2025端午加速活动
    def Exchangee_2025(self):#################################################
        json_data = {
            "exchangeNum": 1,
            "activityCode": "DRAGONBOAT_2025"
        }
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~dragonBoat2025TaskService~integralExchange'
        response = self.do_request(url, data=json_data)
        if response.get('success') == True:
            print(f'> 获得一次抽奖次数')
        else:
            print(f'已完成-积分兑次数')


    def game202505(self):
        #self.headers['channel']='25dwappty
        response = self.do_request("https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~dragonBoatGame2025Service~init")
        if response.get("obj",{}).get("alreadyDayPass",True):
            print(f'今日粽子游戏已完成\n')
        else:
            print(f'====== 开始连粽子 ======')
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~dragonBoatGame2025Service~win'
            for i in range(1, 5):
                json_data = {
                    "levelIndex": i
                }
                response = self.do_request(url, data=json_data)
                #print(response)
                if response.get('success') == True:
                    print(f'第{i}关成功！')
                else:
                    print(f'第{i}关失败！')
                time.sleep(random.randint(25, 35))


    def csy2025(self):##############################################################################
        """
        查询财神爷任务列表，并处理任务逻辑。
        """
        try:
            random_invite = random.choice([invite for invite in inviteId if invite != self.user_id])
            self.do_request("https://mcs-mimp-web.sf-express.com/mcs-mimp/commonNoLoginPost/~memberNonactivity~dragonBoat2025IndexService~index", {"inviteType":4,"inviteUserId":random_invite})
            payload = {"activityCode": "DRAGONBOAT_2025", "channelType": "MINI_PROGRAM"}
            url = "https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~activityTaskService~taskList"
            response = self.do_request(url, payload)
            if isinstance(response, dict) and response.get('success'):
                tasks = response.get('obj', [])
                for task in tasks:
                    taskType = task.get('taskType', None)
                    taskName = task.get('taskName', '未知任务')
                    taskCode = task.get('taskCode', None)
                    taskStatus = task.get('status', 0)
                    skip_tasks = ["去寄快递", "开通至尊会员", "充值新速运通全国卡","玩一笔连粽游戏"]
                    if taskName in skip_tasks:
                        #print(f"🚫 检测到需跳过任务【{taskName}】 ➜ 类型:{taskType} 状态:{taskStatus}")
                        continue

                    #print(f"> 正在处理任务【{taskName}】")

                    if taskStatus == 3:
                        print(f"已完成-{taskName}")
                        continue

                    if taskCode:
                        self.DRAGONBOAT_2025_finishTask(taskCode, taskName)
        except Exception as e:
            import traceback
            print(f"任务查询时出现异常：{e}\n{traceback.format_exc()}")

    def lingtili(self):
        """领取体力"""
        try:
            #print("领体力")
            url = "https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~dragonBoat2025HastenService~receiveCountdownReward"
            response = self.do_request(url, {})
            return response.get('success', False)
        except Exception as e:
            import traceback
            print(f"领体力时出现异常：{e}\n{traceback.format_exc()}")
            return False

    #迪士尼活动
    def dsl2025(self):
        print('\n====== 开始迪士尼主题活动 ======')
        try:
            random_invite = random.choice([invite for invite in inviteId if invite != self.user_id])
            self.do_request("https://mcs-mimp-web.sf-express.com/mcs-mimp/commonNoLoginPost/~memberNonactivity~disneyService~index", {"inviteType":0,"inviteUserId":random_invite})
            payload = {"activityCode": "DISNEY", "channelType": "MINI_PROGRAM"}
            url = "https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~activityTaskService~taskList"

            response = self.do_request(url, payload)
            if isinstance(response, dict) and response.get('success'):
                tasks = response.get('obj', [])
                for task in tasks:
                    taskType = task.get('taskType', None)
                    taskName = task.get('taskName', '未知任务')
                    taskCode = task.get('taskCode', None)
                    taskStatus = task.get('status', 0)
                    if taskType not in ['BROWSE_LIFE_SERVICE','INTEGRAL_EXCHANGE','BROWSE_VIP_CENTER','LOOK_BRAND_VIDEO','BROWSE_STUDENT_BENEFIT']:
                        continue
                    print(f"> 正在处理任务【{taskName}】")
                    if taskStatus == 3:
                        print(f"> 任务【{taskName}】已完成，跳过")
                        continue
                    if taskCode:
                        self.DRAGONBOAT_2025_finishTask(taskCode, taskName)
                        self.dsl2025_fetchTasksReward()
        except Exception as e:
            import traceback
            print(f"任务查询时出现异常：{e}\n{traceback.format_exc()}")

    def dsl2025_cj(self):
        try:
            self.headers['channel'] = 'DISNEY2'
            payload = {}
            url = "https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~disneyService~getStatus"
            self.dsl2025_fetchTasksReward()#领取次数
            response = self.do_request(url, payload)
            if isinstance(response, dict) and response.get('success'):
                receivedAccount = response.get('obj', {}).get('receivedAccount', {})
                cs = response.get('obj', {}).get('remainTimes',0)
                print(f"> 当前 拆快递 次数 {cs} 次")
                for i in range(cs):
                    print(f'>> 开始第 {i + 1} 次 拆快递 ')
                    draw_url = "https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~disneyService~openPackage"
                    draw_response = self.do_request(draw_url)
                    if draw_response.get('success') and draw_response.get('obj'):
                        productName=''
                        if  draw_response.get('obj').get('paidProductPacket',{}):
                            print(f"拆快递成功: 获得 {draw_response.get('obj').get('paidProductPacket',{}).get('productName','-')}")
                        elif  draw_response.get('obj').get('award',{}):
                            print(f"拆快递成功: 获得 {draw_response.get('obj').get('award',{}).get('productName','-')}")
                        else:
                            print(f"拆快递成功: 获得 未知奖品")
                            print(draw_response.get('obj'))
                    else:
                        error_message = draw_response.get('errorMessage', '无返回')
                        print(f'拆快递失败: {error_message}')
                    time.sleep(1)  # 添加延迟避免请求过快
                

                
                print("拆快递 已用完机会")
                response = self.do_request("https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~activityCore~userAwardService~queryUserAward", {"tag":"DISNEY","productType":"","pageNo":1,"pageSize":200})

                if response.get('success') and response.get('obj')  and response.get('obj',{}).get('total',0):
                    print(f"拆快递 抽中奖品 {response.get('obj',{}).get('total',0)} 个")
                    arr=[]
                    for on_ in response.get('obj',{}).get('list',[]):
                        arr.append(on_['productName'])
                    print(f"奖品列表{arr}")
        except Exception as e:
            import traceback
            print(f"任务查询时出现异常：{e}\n{traceback.format_exc()}")
        print('\n====== 结束迪士尼主题活动 ======')

    def dsl2025_fetchTasksReward(self):
        response = self.do_request(
            "https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~disneyTaskService~fetchTasksReward",
            {"channelType":"SFAPP"}
        )
        
        if response.get('success'):
            if len(response.get('obj',[])):
                print(f">领取已完成任务奖励 {len(response.get('obj',[]))} 次")


    def yearEnd2025_main(self):
        """
        马年年终活动主函数 - 优化版
        """
        if not YEAREND_2025_ACTIVITY:
            return
        
        print('\n====== 开始马年年终活动 ======')
        
        try:
            # 1. 初始化活动状态（包含部分任务处理）
            self.yearEnd2025_init()

            # 2. 签到（获取20积分）
            self.yearEnd2025_sign()

            #马年游戏
            self.xcsm2026_game_init()

            # 3. 获取任务列表并处理（先完成任务获取积分）
            self.yearEnd2025_get_task_list()
            
            # 4. 领取任务奖励次数（应该在执行任务后立即领取）
            self.yearEnd2025_fetchTasksReward()
            
            # 5. 获取累计任务奖励（可能会有额外积分/次数）
            self.yearEnd2025_get_accrued_task_award()
            
            # 6. 如果积分足够，尝试兑换抽奖次数
            current_integral = self.yearEnd2025_get_user_rest_integral()
            if current_integral >= 10:  # 根据抓包数据，兑换1次需要10积分
                self.yearEnd2025_integral_exchange()
        
            # 7. 执行抽奖（使用最新的剩余次数）
            self.yearEnd2025_forward()
            
        except Exception as e:
            print(f'⚠️ 马年年终活动异常: {e}')
            import traceback
            traceback.print_exc()
        
        print('====== 结束马年年终活动 ======')

    
    def yearEnd2025_init(self):
        """
        初始化马年年终活动
        """
        try:
            # 获取Dilate状态
            random_invite = random.choice([invite for invite in inviteId if invite != self.user_id])
            self.do_request("https://mcs-mimp-web.sf-express.com/mcs-mimp/commonNoLoginPost/~memberNonactivity~yearEnd2025IndexService~index", {"inviteType":1,"inviteUserId":random_invite})
            payload = {"activityCode": "YEAREND_2025", "channelType": "MINI_PROGRAM"}
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~yearEnd2025DilateService~getDilateStatus'
            response = self.do_request(url, payload)
            
            if isinstance(response, dict) and response.get('success'):
                obj_data = response.get('obj', [])
                
                # 修复：检查返回的数据类型
                if isinstance(obj_data, dict):
                    # 如果是字典，尝试获取tasks字段
                    tasks = obj_data.get('tasks', [])
                elif isinstance(obj_data, list):
                    # 如果是列表，直接使用
                    tasks = obj_data
                elif isinstance(obj_data, str):
                    # 如果是字符串，尝试解析JSON
                    try:
                        tasks = json.loads(obj_data).get('tasks', [])
                    except:
                        tasks = []
                else:
                    tasks = []
                
                for task in tasks:
                    # 确保task是字典类型
                    if not isinstance(task, dict):
                        print(f"任务数据格式异常，跳过: {task}")
                        continue
                        
                    taskType = task.get('taskType', None)
                    taskName = task.get('taskName', '未知任务')
                    taskCode = task.get('taskCode', None)
                    taskStatus = task.get('status', 0)
                    skip_tasks = ["去寄快递", "开通至尊会员", "充值新速运通全国卡","玩一笔连粽游戏"]
                    
                    if taskName in skip_tasks:
                        #print(f"🚫 检测到需跳过任务【{taskName}】 ➜ 类型:{taskType} 状态:{taskStatus}")
                        continue

                    #print(f"> 正在处理任务【{taskName}】")

                    if taskStatus == 3:
                        print(f"已完成-{taskName}")
                        continue

                    if taskCode:
                        # 修改这里，使用正确的方法名
                        self.yearEnd2025_finish_task(taskCode, taskName)
        except Exception as e:
            import traceback
            print(f"任务查询时出现异常：{e}\n{traceback.format_exc()}")



    def yearEnd2025_sign(self):
        """
        马年年终活动签到
        """
        try:
            print('\n--- 马年年终活动签到 ---')
            
            # 1. 先检查签到状态
            status_url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~activitySignService~signStatus'
            status_data = {"activityCode": "YEAREND_2025"}
            
            status_response = self.do_request(status_url, status_data, req_type="post", config_mode="1")
            
            if not status_response.get('success'):
                print(f'签到状态查询失败: {status_response.get("errorMessage", "未知错误")}')
                return False
            
            obj = status_response.get('obj', {})
            sign_count_cache = obj.get('signCountCache', {})
            sign_count = sign_count_cache.get('signCount', 0)
            sign_time = sign_count_cache.get('signTime')
            
            if sign_time:
                print(f'今日已签到 (签到次数: {sign_count}, 签到时间: {sign_time})')
                return True
            else:
                print(f'今日未签到，可以签到 (历史签到次数: {sign_count})')
            
            # 2. 执行签到
            sign_url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~activitySignService~sign'
            sign_data = {"activityCode": "YEAREND_2025"}
            
            sign_response = self.do_request(sign_url, sign_data, req_type="post", config_mode="1")
            
            if sign_response.get('success'):
                obj = sign_response.get('obj', {})
                signed = obj.get('signed', False)
                sign_count = obj.get('signCount', 0)
                common_sign_packet = obj.get('commonSignPacketDTO', {})
                
                if signed or sign_count > 0:
                    if common_sign_packet:
                        gift_name = common_sign_packet.get('giftBagName', '未知奖励')
                        gift_worth = common_sign_packet.get('giftBagWorth', 0)
                        print(f'✅ 签到成功! 获得: {gift_name} ({gift_worth}积分)')
                    else:
                        print(f'✅ 签到成功! 当前签到次数: {sign_count}')
                    return True
                else:
                    print('❌ 签到失败: 返回状态异常')
                    return False
            else:
                error_msg = sign_response.get('errorMessage', '未知错误')
                print(f'❌ 签到失败: {error_msg}')
                return False
                
        except Exception as e:
            print(f'⚠️ 签到异常: {e}')
            return False



    def yearEnd2025_get_task_list(self):
        """
        获取马年年终活动任务列表
        """
        try:
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~activityTaskService~taskList'
            data = {
                'activityCode': 'YEAREND_2025',
                'channelType': 'SFAPP'
            }
            
            response = self.do_request(url, data, req_type="post", config_mode="1")
            
            if response.get('success'):
                tasks = response.get('obj', [])
                print(f'发现 {len(tasks)} 个任务')
                
                # 需要排除的任务类型（需要实际操作的）
                excluded_task_types = [
                    'RECEIVE_VIP_BENEFIT',        # 领取寄件会员权益
                    'OPEN_FAMILY_HOME_MUTUAL',    # 开通家庭8折互寄权益
                    'SEND_SUCCESS_RECALL',        # 去寄快递
                    'SEND_LARGE_SUCCESS',         # 春节寄大件行李
                    'CHARGE_NEW_EXPRESS_CARD',    # 充值新速运通全国卡
                    'INVITEFRIENDS_PARTAKE_ACTIVITY',  # 邀好友首次访问活动
                    'PLAY_ACTIVITY_GAME',         # 套财神游戏
                ]
                
                # 可自动完成的任务类型
                auto_task_types = [
                    'BROWSE_LIFE_SERVICE',        # 看看生活服务
                    'SIGN_IN',                    # 签到（如果有的话）
                    'VIEW_COUPON',                # 查看优惠券（如果有的话）
                ]
                
                completed_tasks = 0
                
                for task in tasks:
                    task_name = task.get('taskName', '未知任务')
                    task_type = task.get('taskType', '未知类型')
                    task_code = task.get('taskCode')
                    status = task.get('status', 0)
                    
                    # 检查任务状态
                    if status == 2:  # 未完成
                        print(f'未完成: {task_name} ({task_type})')
                        
                        # 处理可自动完成的任务
                        if task_type in auto_task_types and task_code:
                            print(f'执行任务: {task_name}')
                            if self.yearEnd2025_finish_task(task_code, task_name):
                                completed_tasks += 1
                    
                    elif status == 3:  # 已完成
                        print(f'已完成: {task_name}')
                    
                    elif status == 4:  # 可领取奖励
                        print(f'可领取奖励: {task_name}')
                        # 这里可以添加领取奖励的逻辑
                
                print(f'共完成了 {completed_tasks} 个任务')
                
            else:
                print(f'获取任务列表失败: {response.get("errorMessage", "未知错误")}')
                
        except Exception as e:
            print(f'⚠️ 获取任务列表异常: {e}')
    
    def yearEnd2025_finish_task(self, task_code, task_name):
        """
        完成马年年终活动任务
        """
        try:
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonRoutePost/memberEs/taskRecord/finishTask'
            data = {
                'taskCode': task_code
            }
            
            response = self.do_request(url, data, req_type="post", config_mode="1")
            
            if response.get('success'):
                print(f'任务 {task_name} 执行成功!')
                return True
            else:
                error_msg = response.get('errorMessage', '未知错误')
                print(f'任务 {task_name} 执行失败: {error_msg}')
                return False
                
        except Exception as e:
            print(f'⚠️ 完成任务异常: {e}')
            return False

    def xcsm2026_game_init(self):
        """初始化中秋活动游戏，并开始闯关"""
        print('🎮 初始化新春赛马游戏...')
        # 保存原来的headers
        original_headers = self.headers.copy()
        # 更新headers
        self.headers.update({
            'referer': 'https://mcs-mimp-web.sf-express.com/origin/a/mimp-activity/yearEnd2025Game'
        })
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~yearEnd2025GameService~init'
        response = self.do_request(url,{}, req_type="post")
        
        # 恢复headers 
        self.headers = original_headers
        if response and response.get('success'):
            obj = response.get('obj', {})
            if not obj.get('alreadyDayPass', False):
                start_level = obj.get('currentIndex', 0)
                print(f'今日未通关，从第【{start_level}】关开始...')
                num = len(obj.get('levelConfig', [])) + 1
                url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~yearEnd2025GameService~win'
                for i in range(start_level, num):
                    print(f'闯关...第【{i}】关 总共 {num}')
                    response = self.do_request(url, {"levelIndex": i}, req_type="post")
                    if response and response.get('success'):
                        # 修改这里：处理currentAwardList列表
                        award_list = response.get('obj', {}).get('currentAwardList', [])
                        if award_list:
                            for award in award_list:
                                print(f'> 🎉 获得：【{award.get("currency")}】x{award.get("amount")}')
                        else:
                            print('> 本关无即时奖励')
                        time.sleep(random.uniform(15, 19))
                    else:
                        error_msg = response.get("errorMessage", "未知错误") if response else "请求失败"
                        print(f'❌ 第【{i}】关闯关失败: {error_msg}')
                        break  # 失败则停止
            else:
                print('今日已通关，跳过游戏！')
        else:
            print('❌ 游戏初始化失败')
            print(response)


    def yearEnd2025_get_accrued_task_award(self):
        """
        获取累计任务奖励
        """
        try:
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~yearEnd2025TaskService~getAccruedTaskAward'
            data = {}
            
            response = self.do_request(url, data, req_type="post", config_mode="1")
            
            if response.get('success'):
                obj = response.get('obj', {})
                current_progress = obj.get('currentProgress', 0)
                print(f'累计任务进度: {current_progress}')
                
                # 获取进度配置
                progress_config = obj.get('progressConfig', {})
                # if progress_config:
                #     print(f'进度配置: {progress_config}')
                    
            else:
                print(f'获取累计任务奖励失败: {response.get("errorMessage", "未知错误")}')
                
        except Exception as e:
            print(f'⚠️ 获取累计任务奖励异常: {e}')
    
    def yearEnd2025_get_forward_status(self):
        """
        获取转发状态
        """
        try:
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~yearEnd2025ForwardService~forwardStatus'
            data = {}
            
            response = self.do_request(url, data, req_type="post", config_mode="1")
            
            if response.get('success'):
                obj = response.get('obj', {})
                current_times = obj.get('currentTimes', 0)
                total_times = obj.get('totalTimes', 0)
                remain_chance = obj.get('remainChance', 0)
                current_ratio = obj.get('currentRatio', 0)
                
                print(f'抽奖状态: 已抽 {current_times}/{total_times} 次, 剩余 {remain_chance} 次机会, 当前进度: {current_ratio}%')
                
            else:
                print(f'获取转发状态失败: {response.get("errorMessage", "未知错误")}')
                
        except Exception as e:
            print(f'⚠️ 获取转发状态异常: {e}')
    
    def yearEnd2025_get_user_rest_integral(self):
        """
        获取用户剩余积分
        """
        try:
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~activityTaskService~getUserRestIntegral'
            data = {}
            
            response = self.do_request(url, data, req_type="post", config_mode="1")
            
            if response.get('success'):
                integral = response.get('obj', 0)
                print(f'当前可用积分: {integral}')
                return integral
            else:
                print(f'获取用户剩余积分失败: {response.get("errorMessage", "未知错误")}')
                return 0
                
        except Exception as e:
            print(f'⚠️ 获取用户剩余积分异常: {e}')
            return 0
    
    def yearEnd2025_integral_exchange(self, exchange_num=1):
        """
        积分兑换抽奖次数
        """
        try:
            # 先检查积分是否足够
            current_integral = self.yearEnd2025_get_user_rest_integral()
            
            # 根据抓包数据，兑换1次需要10积分
            required_integral = exchange_num * 10
            
            if current_integral < required_integral:
                print(f'积分不足，需要 {required_integral} 积分，当前只有 {current_integral} 积分')
                return False
            
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~yearEnd2025TaskService~integralExchange'
            data = {
                'exchangeNum': exchange_num,
                'activityCode': 'YEAREND_2025'
            }
            
            response = self.do_request(url, data, req_type="post", config_mode="1")
            
            if response.get('success'):
                obj = response.get('obj', {})
                remain_chance = obj.get('remainChance', 0)
                print(f'积分兑换成功! 剩余抽奖机会: {remain_chance} 次')
                return True
            else:
                error_msg = response.get('errorMessage', '未知错误')
                print(f'积分兑换失败: {error_msg}')
                return False
                
        except Exception as e:
            print(f'⚠️ 积分兑换异常: {e}')
            return False

    def yearEnd2025_forward(self):
        """
        执行抽奖
        """
        try:
            # 先获取最新的转发状态
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~yearEnd2025ForwardService~forwardStatus'
            data = {}
            
            response = self.do_request(url, data, req_type="post", config_mode="1")
            
            if not response.get('success'):
                print('无法获取抽奖状态')
                return
            
            obj = response.get('obj', {})
            remain_chance = obj.get('remainChance', 0)
            current_times = obj.get('currentTimes', 0)
            total_times = obj.get('totalTimes', 0)
            
            if remain_chance <= 0:
                print(f'没有抽奖机会 (已抽 {current_times}/{total_times} 次)')
                return
            
            print(f'开始抽奖，剩余机会: {remain_chance} 次 (已抽 {current_times}/{total_times} 次)')
            
            # 执行抽奖
            forward_url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~yearEnd2025ForwardService~forward'
            forward_data = {}
            
            for i in range(remain_chance):
                print(f'第 {i+1} 次抽奖...')
                response = self.do_request(forward_url, forward_data, req_type="post", config_mode="1")
                
                if response.get('success'):
                    obj = response.get('obj', {})
                    result_type = obj.get('resultType', 0)
                    award = obj.get('award', {})
                    
                    if result_type == 3 and award:  # 获得奖品
                        product_name = award.get('productName', '未知奖品')
                        coupon_name = award.get('couponName', '')
                        denomination = award.get('denomination', '')
                        
                        if coupon_name:
                            print(f'🎉 抽奖获得: {coupon_name} ({denomination}元)')
                        else:
                            print(f'🎉 抽奖获得: {product_name}')
                    else:
                        print(f'抽奖结果: {result_type} (未获得奖品)')
                    
                    # 短暂延迟，避免请求过快
                    time.sleep(1)
                else:
                    error_msg = response.get('errorMessage', '未知错误')
                    print(f'抽奖失败: {error_msg}')
                    break
            
            print('抽奖完成')
            
        except Exception as e:
            print(f'⚠️ 抽奖异常: {e}')
    
    def yearEnd2025_get_widget_status(self):
        """
        获取Widget状态
        """
        try:
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~yearEnd2025DilateService~getWidgetStatus'
            data = {}
            
            response = self.do_request(url, data, req_type="post", config_mode="1")
            
            if response.get('success'):
                obj = response.get('obj', {})
                dilate_widget = obj.get('dilateWidget', {})
                receive_status = dilate_widget.get('receiveStatus', 0)
                
                print(f'Widget状态: {receive_status}')
                
                if receive_status == 1:
                    print('可以领取Widget奖励')
                else:
                    print('Widget奖励已领取或不可用')
                    
            else:
                print(f'获取Widget状态失败: {response.get("errorMessage", "未知错误")}')
                
        except Exception as e:
            print(f'⚠️ 获取Widget状态异常: {e}')

    def yearEnd2025_fetchTasksReward(self):
        """
        领取任务奖励次数，并查询剩余次数
        """
        try:
            print('\n--- 领取任务奖励次数 ---')
            
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~yearEnd2025TaskService~fetchTasksReward'
            data = {"activityCode": "YEAREND_2025", "channelType": "SFAPP"}
            
            response = self.do_request(url, data, req_type="post", config_mode="1")
            
            if response and response.get('success'):
                print('✅ 任务奖励领取成功')
                
                # 领取成功后，查询一下剩余次数
                status_url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~yearEnd2025ForwardService~forwardStatus'
                status_response = self.do_request(status_url, {}, req_type="post", config_mode="1")
                
                if status_response and status_response.get('success'):
                    obj = status_response.get('obj', {})
                    remainChance = obj.get('remainChance', 0)
                    currentRatio = obj.get('currentRatio', 0)
                    currentTimes = obj.get('currentTimes', 0)
                    totalTimes = obj.get('totalTimes', 0)
                    
                    print(f'ℹ️ 当前剩余抽奖次数: {remainChance}')
                    print(f'ℹ️ 抽奖进度: {currentTimes}/{totalTimes} 次, 进度 {currentRatio}%')
                    
                    return remainChance
                else:
                    error_msg = status_response.get("errorMessage", "未知错误") if status_response else "请求失败"
                    print(f'❌ 查询抽奖次数失败: {error_msg}')
            else:
                error_msg = response.get("errorMessage", "未知错误") if response else "请求失败"
                print(f'❌ 领取任务奖励次数失败: {error_msg}')
                
            return 0
                    
        except Exception as e:
            print(f'⚠️ 领取任务奖励异常: {e}')
            return 0
    # 主程序
    def main(self):
        if not self.login_res:
            print("登录失败，终止处理")
            return False
        self.automatic_daily_sign()
        if DRAGONBOAT_LOTTERY2:
            self.get_SignTaskList() # 积分任务
            self.query_free_coupon() # 免单券查询
            self.query_unpay_orders() # 待支付订单查询
            # self.get_honeyTaskListStart() # 蜂蜜任务

        if YEAREND_2025_ACTIVITY:
            self.yearEnd2025_main()

        #self.anniversary2025_taskList() # 周年庆
        # self.csy2025() #浏览任务
        # self.Exchangee_2025() #积分兑换一次加速
        # self.lingtili() #领取体力
        # self.fetchTasksReward()
        # self.cxcs() #端午加速
        # self.game202505() #连粽子游戏
        # self.index2025() #查询端午活动
        # if DRAGONBOAT_LOTTERY:
        #     self.duanwuChoujiang() #端午抽奖
        if DISNEY_ACTIVITY:    
            self.dsl2025()
            self.dsl2025_cj()
            self.dsl2025_fetchTasksReward()

        return True

if __name__ == '__main__':
    accounts_list = os.getenv('sfsyUrl')#修改成你自己的环境变量
    if accounts_list is None:
        log.info("未找到账号变量，请检查")
        exit(1)

    accounts = [x.strip() for x in accounts_list.split('\n') if x.strip()]
    print(f"检测到 {len(accounts)} 个账号")

    for index, info in enumerate(accounts):
        try:
            instance = SFAPI(info, index)
            if not instance.main():
                print(f"第 {index + 1} 个账号处理失败")
        except Exception as e:
            print(f"处理账号时发生异常: {str(e)}")

    push_content = (log_stream.getvalue().strip())
    if push_content:
        sys.stdout = io.StringIO()
        # 添加热修补代码
        import requests
        def empty_hitokoto():
            return ""
        import notify
        notify.one = empty_hitokoto
        send("顺丰速运", push_content)


# 当前脚本来自于 http://script.345yun.cn 脚本库下载！
# 当前脚本来自于 http://2.345yun.cn 脚本库下载！
# 当前脚本来自于 http://2.345yun.cc 脚本库下载！
# 脚本库官方QQ群1群: 429274456
# 脚本库官方QQ群2群: 1077801222
# 脚本库官方QQ群3群: 433030897
# 脚本库中的所有脚本文件均来自热心网友上传和互联网收集。
# 脚本库仅提供文件上传和下载服务，不提供脚本文件的审核。
# 您在使用脚本库下载的脚本时自行检查判断风险。
# 所涉及到的 账号安全、数据泄露、设备故障、软件违规封禁、财产损失等问题及法律风险，与脚本库无关！均由开发者、上传者、使用者自行承担。