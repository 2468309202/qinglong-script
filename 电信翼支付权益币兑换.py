import asyncio
import aiohttp
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
import requests
from Crypto.Cipher import AES, DES3, PKCS1_v1_5
from Crypto.Util.Padding import pad, unpad
from concurrent.futures import ThreadPoolExecutor

gjc=['权益金','99元话费券']
#编辑productNo_list或者设置变量yzf，格式：手机号@服务密码,多号&隔开
productNo_list=''


########

cfcs = os.environ.get('yzfcf') or  50 # 重发次数

# 初始化日志字典
logg = {}

# 创建线程池执行器（用于CPU密集型操作）
executor = ThreadPoolExecutor(max_workers=10)
# 初始化参数





ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
ssl_context.set_ciphers('DEFAULT@SECLEVEL=0')

appType = "116"

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



async def userLoginNormal(ss,phone,password):
    alphabet = 'abcdef0123456789'
    uuid = [''.join(random.sample(alphabet, 8)),''.join(random.sample(alphabet, 4)),'4'+''.join(random.sample(alphabet, 3)),''.join(random.sample(alphabet, 4)),''.join(random.sample(alphabet, 12))]
    timestamp=datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    loginAuthCipherAsymmertric = 'iPhone 14 15.4.' + uuid[0] + uuid[1] + phone + timestamp + password[:6] + '0$$$0.'
    public_key_b64 = 'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDBkLT15ThVgz6/NOl6s8GNPofdWzWbCkWnkaAm7O2LjkM1H7dMvzkiqdxU02jamGRHLX/ZNMCXHnPcW/sDhiFCBN18qFvy8g6VYb9QtroI09e176s+ZCtiv7hbin2cCTj99iUpnEloZm19lwHyo69u5UMiPMpq0/XKBO8lYhN/gwIDAQAB'
    r = await ss.post('https://appgologin.189.cn:9031/login/client/userLoginNormal',json={"headerInfos": {"code": "userLoginNormal", "timestamp": timestamp, "broadAccount": "", "broadToken": "", "clientType": "#10.5.0#channel50#iPhone 14 Pro Max#", "shopId": "20002", "source": "110003", "sourcePassword": "Sid98s", "token": "", "userLoginName": encode_phone(phone)}, "content": {"attach": "test", "fieldData": {"loginType": "4", "accountType": "", "loginAuthCipherAsymmertric": rsa_encrypt(public_key_b64, loginAuthCipherAsymmertric), "deviceUid": uuid[0] + uuid[1] + uuid[2], "phoneNum": encode_phone(phone), "isChinatelecom": "0", "systemVersion": "15.4.0", "authentication": encode_phone(password)}}})
    r = await r.json()
    l = r.get('responseData').get('data')
    
    if l and l.get('loginSuccessResult'):
        l = l.get('loginSuccessResult')
        load_token[phone] = l
        with open(load_token_file, 'w') as f:
            json.dump(load_token, f)
        ticket = await get_ticket(ss,phone,l['userId'],l['token']) 
        
        return ticket
    else:
        print(r)
       
    return False
async def get_ticket(ss,phone,userId,token):
    r = await ss.post('https://appgologin.189.cn:9031/map/clientXML',data='<Request><HeaderInfos><Code>getSingle</Code><Timestamp>'+datetime.datetime.now().strftime("%Y%m%d%H%M%S")+'</Timestamp><BroadAccount></BroadAccount><BroadToken></BroadToken><ClientType>#9.6.1#channel50#iPhone 14 Pro Max#</ClientType><ShopId>20002</ShopId><Source>110003</Source><SourcePassword>Sid98s</SourcePassword><Token>'+token+'</Token><UserLoginName>'+phone+'</UserLoginName></HeaderInfos><Content><Attach>test</Attach><FieldData><TargetId>'+encrypt(userId)+'</TargetId><Url>4a6862274835b451</Url></FieldData></Content></Request>',headers={'user-agent': 'CtClient;10.4.1;Android;13;22081212C;NTQzNzgx!#!MTgwNTg1'})
    r = await r.text()
    tk = re.findall('<Ticket>(.*?)</Ticket>',r)
    if len(tk) == 0:        
        return False
    
    
    return  decrypt(tk[0])

async def dh(session, productNo, sessionKey, sku, ts='1'):
    goodsName, equityCoinExpendAmount, skuId, showStartDate = sku
    data=process_data({"orderChannel":"H5","goodsInfoList":[{"goodsId":skuId,"goodsNum":1}],"shelvesNo":"GS0002023110800055791611c","fromChannelId":"POINT_EXCHANGE","businessProductNo":"","appId":"","traceLogId":trace_log_id(),"requestDate":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"operator":productNo,"appType":"116","fromchannelId":"H5","requestSystem":"equity-goods-h5","requestNo":generate_mixed(),"productNo":productNo,"sessionKey":sessionKey,"agreeId":"20211223030100213484984697094168"})
    r = await async_post(session, 'https://mapi-h5.bestpay.com.cn/gapi/ep-product-center/quotaCenter/WaitManualCollectionService/buildBusinessOrder', data)
    if r["success"]:
        orderId = r.get('result').get('orderId')    
        data=process_data({"mallPayTool":"REDEMPTION_OF_POINTS","subject":goodsName,"orderAmt":0,"orderId":orderId,"payScene":"H5","tradeChannel":"H5","auxiliaryPayToolDTO":{"exchangeDTOList":[]},"appTypePlatform":"android","shelvesNo":"GS0002023110800055791611c","quotaDeductCount":0,"couponInstNbr":"","businessProductNo":"","traceLogId":trace_log_id(),"requestDate":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"operator":productNo,"appType":"116","fromchannelId":"H5","requestSystem":"equity-goods-h5","requestNo":generate_mixed(),"productNo":productNo,"sessionKey":sessionKey,"agreeId":"20211223030100213484984697094168"})
        r = await async_post(session, 'https://mapi-h5.bestpay.com.cn/gapi/ep-product-center/quotaCenter/WaitManualCollectionService/buildPayOrder', data)
        if r['success']:
            msg = f"{productNo}[{goodsName}]兑换成功"
            
            print(msg)
        else:
            print(goodsName, "兑换失败", r['errorMsg'])
    else:
        print(goodsName, "下单失败", r['errorMsg'])


def run_Time(sj):
    sj = sj.split(':')
    hour,miute,second = int(sj[0]), int(sj[1]), int(sj[2])
    date = datetime.datetime.now()
    date_zero = datetime.datetime.now().replace(year=date.year, month=date.month, day=date.day, hour=hour, minute=miute, second=second)
    date_zero_time = int(time.mktime(date_zero.timetuple()))
    return date_zero_time
    
    
# 异步HTTP客户端会话
async def create_session():
    resolver = aiohttp.AsyncResolver(nameservers=["119.29.29.29"])
    connector = aiohttp.TCPConnector(resolver=resolver, limit=100, ssl=ssl_context)  # 根据需要调整连接池大小
    return aiohttp.ClientSession(connector=connector)

# 同步加密函数（保持同步，通过线程池执行）
def aes_encrypt(plaintext, key):
    cipher = AES.new(key.encode(), AES.MODE_CBC, 16 * b'\0')
    return base64.b64encode(cipher.encrypt(pad(plaintext.encode(), AES.block_size))).decode()

def rsa_encrypt(j_rsakey, string):
    pub_key = rsa.PublicKey.load_pkcs1_openssl_pem(f"-----BEGIN PUBLIC KEY-----\n{j_rsakey}\n-----END PUBLIC_KEY-----".encode())
    return base64.b64encode(rsa.encrypt(string.encode(), pub_key)).decode()

    
def rsa_encrypt(j_rsakey, string):
    rsa_key = f"-----BEGIN PUBLIC KEY-----\n{j_rsakey}\n-----END PUBLIC KEY-----"
    pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(rsa_key.encode())
    result = (base64.b64encode(rsa.encrypt(f'{string}'.encode(), pubkey))).decode()
    return result
    
def generate_mixed():
    return ''.join(str(random.randint(0,9)) for _ in range(16))

def trace_log_id():
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ''.join(str(random.randint(0,9)) for _ in range(18))

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



async def proper_sleep(end_time: float):
    while time.time() < end_time:
        remaining = end_time - time.time()
        await asyncio.sleep(max(remaining, 0.001))  # 最小休眠 1ms
# 异步请求函数
async def async_post(session, url, data):
    try:
        async with session.post(url, json=data) as response:
            response.raise_for_status()
            return await response.json()
    except Exception as e:
        print(f"请求失败: {url} - {str(e)}")
        return None

async def process_product2(sem, session, product_no, sl):
    async with sem:
        for _ in range(3):
            try:
                await process_product(session, product_no, sl)
                break
            except:
                await asyncio.sleep(1)


# 核心业务逻辑（异步版本）
async def process_product(session, product_no, sl):
    
    product_no, password = product_no.split('@')
    logg[product_no] = []
    ticket = False
    await asyncio.sleep(sl/10)     
    if product_no in load_token:
        print(f'{product_no} 使用缓存登录')
        ticket = await get_ticket(session,product_no,load_token[product_no]['userId'],load_token[product_no]['token'])
    
    if ticket == False:
        print(f'{product_no} 使用密码登录')
        ticket = await userLoginNormal(session,product_no,password)
        
    if ticket ==False:
        print(f"{product_no} 登录失败")
        return
    # 获取会话密钥
    session_key = await get_session_key_async(session, product_no, ticket)
    #print(session_key)
    if not session_key:
        print(f"{product_no} 翼支付session_key获取失败")
        return
        
    data = process_data({"encyType":"C005","appType":"116","fromchannelId":"H5","fromChannelId":"H5","traceLogId":"20250501004718816046282805102942","productNo":product_no,"sessionKey":session_key})
    myCashPage = await async_post(session, 'https://mapi-h5.bestpay.com.cn/gapi/op-product-system/myCashPageService/myCashPage', data)
    availableShowValue = myCashPage.get('result').get('availableShowValue', 0)
    msga = f"{product_no} 权益币余额: {availableShowValue}"
    print(msga)
    if str(availableShowValue) == "None":
        return
    data=process_data({"shelvesShowPosition":"EQUITY_POINT_PAGE","shelvesNo":"GS0002023110800055791611c","pageNum":1,"pageSize":100,"classifyNo":"CL00020240130160418630918","fromchannelId":"H5","channel":"CUSTOMER_MANAGER","phoneNo":product_no,"encyType":"C005","appType":"116","agreeId":"20210310030100109056788136984665","fromChannelId":"H5","traceLogId":"20250501005113275395886286262098","productNo":product_no,"sessionKey":session_key})
    r = await async_post(session, 'https://mapi-h5.bestpay.com.cn/gapi/vipproduct/shelves/shelvesGoodsQuery', data)
    bh = []
    

    
    for i in r.get('result').get('resList',[]):
        goodsName = i['goodsName']
        goodsNo = i['goodsNo']
        equityCoinExpendAmount = i['equityCoinExpendAmount']
        if str(int(equityCoinExpendAmount)/10).split('.')[0] not in goodsName:            
            continue
        
        
        for g in gjc:
            if g in goodsName:
                data=process_data({"spuId":goodsNo, "traceLogId":trace_log_id(),"requestDate":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"operator":product_no,"appType":"116","fromchannelId":"H5","requestSystem":"equity-goods-h5","requestNo":generate_mixed(),"productNo":product_no,"sessionKey":session_key,"agreeId":"20211223030100213484984697094168"})
            
                r = await async_post(session, 'https://mapi-h5.bestpay.com.cn/gapi/ep-product-center/goodsCenter/GoodsService/querySpuDetails', data)
                

                skuId = r.get('result').get('skuList')[0].get('skuId')       
                showStartDate = r.get('result').get('seckillInfoResDTO').get('showStartDate','').split(' ')[-1]
                bh.append([goodsName, equityCoinExpendAmount, skuId, showStartDate])     
    msg = [msga]
    bh.sort(key=lambda x: int(x[1]), reverse=True)
    

    for _ in bh:
        if int(availableShowValue) + 1  > int(_[1]):
            await proper_sleep(run_Time(showStartDate))
            for __ in range(2):
                await dh(session, product_no, session_key, _, '1')
    availableShowValue = myCashPage.get('result').get('availableShowValue', 0)
    msga = f"{product_no} 权益币余额: {availableShowValue}"
    print(msga)

# 异步会话密钥获取
async def get_session_key_async(session, product_no, code):
    data = process_data({"appType":appType,"agreeId":"20201016030100056487302393758758","encryptData":code,"systemType":"","imei":"","mtMac":"","wifiMac":"","location":""})#ticket方案 
    
    response = await async_post(session, 'https://mapi-welcome.bestpay.com.cn/gapi/AppFusionLogin/authorizeAndRegister', data)
    return response['result']['sessionKey'] if response else None

async def main():
    global kproductNo, public_key
    
    # 初始化参数
    kproductNo = str(int(datetime.datetime.now().timestamp()))

    # 创建会话
    async with await create_session() as session:
        # 获取初始参数
        public_key = await async_post(session, 'https://mapi-h5.bestpay.com.cn/gapi/mapi-gateway/applyLoginFactor', {
            "productNo": kproductNo,
            "requestType": "H5",
            "traceLogId": trace_log_id()
        })
        public_key = public_key['result']['nonce']
        
        # 并发处理所有产品
        productNo_lists = os.environ.get('yzf') or productNo_list
        productNo_lists = productNo_lists.split('&')
        
        # 并发处理所有产品
        tasks = [process_product(session, productNo_lists[p], p) for p in range(len(productNo_lists))]
        #tasks = [process_product(session, p) for p in productNo_lists.split('&')]
        await asyncio.gather(*tasks)
        
        

if __name__ == "__main__":
    # 配置事件循环策略（Windows需要）

    rq = datetime.datetime.now().strftime("%Y-%m-%d")
    load_token_file = 'chinaTelecom_cache.json'
    try:
        from notify import send
        qlts = 1
        print("加载青龙通知服务成功！")
    except:
        qlts = 0
        


    try:
        with open(load_token_file, 'r') as f:
            load_token = json.load(f)
    except:
        load_token = {}
    
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # 启动异步主函数
    asyncio.run(main())
