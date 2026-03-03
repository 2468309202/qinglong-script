#低保版,魔改各路大佬的,已完成每日签到,开宝箱和分享3000币,每日3000币起,测试约为3000-8000币
# 变量名ksjsbCookie 多个用&分割，需要完整cookies，青龙单容器快手完整cookies只能放63个。建议启用60个,否则会报错

import json
import os
import time
import urllib.parse
import urllib.request

env_dist = os.environ
# 获取环境变量
_Cookie = env_dist.get("ksjsbCookie")
# 分割环境变量
Cookies = _Cookie.split("&") if _Cookie else []  # 新增：处理Cookie为空的情况
# 协议头
Agent = "Mozilla/5.0 (Linux; Android 11; Redmi K20 Pro Premium Edition Build/RKQ1.200826.002; wv) AppleWebKit/537.36 " \
        "(KHTML, like Gecko) Version/4.0 Chrome/90.0.4430.226 KsWebView/1.8.90.488 (rel;r) Mobile Safari/537.36 " \
        "Yoda/2.8.3-rc1 ksNebula/10.3.41.3359 OS_PRO_BIT/64 MAX_PHY_MEM/7500 AZPREFIX/yz ICFO/0 StatusHT/34 " \
        "TitleHT/44 NetType/WIFI ISLP/0 ISDM/0 ISLB/0 locale/zh-cn evaSupported/false CT/0 "


# 获取账号信息
def getInformation(can_cookie):
    url = "https://nebula.kuaishou.com/rest/n/nebula/activity/earn/overview/basicInfo"
    headers = {'User-Agent': Agent, 'Accept': '*/*', 'Accept-Language': ' zh-CN,zh;q=0.9', 'Cookie': can_cookie}
    arr_result = {'code': -1}  # 初始化默认值
    try:
        request = urllib.request.Request(url=url, headers=headers)
        response = urllib.request.urlopen(request, timeout=10)  # 新增超时
        str_result = response.read().decode('UTF-8')
        arr_json = json.loads(str_result)
        
        if arr_json.get('result') == 1 and arr_json.get('data'):
            arr_result = {
                'code': arr_json['result'],
                'data': {
                    'nickname': str(arr_json['data'].get('userData', {}).get('nickname', '未知账号')),
                    'cah': str(arr_json['data'].get('totalCash', 0)),
                    'coin': str(arr_json['data'].get('totalCoin', 0))
                }
            }
    except Exception as reason:  # 捕获所有异常
        print("获取信息出错啦: " + str(reason))
    return arr_result


# 开宝箱
def openBox(can_cookie, name):
    url = "https://nebula.kuaishou.com/rest/n/nebula/box/explore?isOpen=true&isReadyOfAdPlay=true"
    headers = {'User-Agent': Agent, 'Accept': '*/*', 'Accept-Language': ' zh-CN,zh;q=0.9', 'Cookie': can_cookie}
    try:
        request = urllib.request.Request(url=url, headers=headers)
        response = urllib.request.urlopen(request, timeout=10)
        str_result = response.read().decode('UTF-8')
        arr_json01 = json.loads(str_result, strict=False)
        
        show = arr_json01.get('data', {}).get('show', False)
        if show:
            common_award = arr_json01.get('data', {}).get('commonAwardPopup')
            if common_award:
                print(f"账号[{name}]开宝箱获得{common_award.get('awardAmount', 0)}金币")
            else:
                open_time = arr_json01.get('data', {}).get('openTime', 0)
                if open_time == -1:
                    print(f"账号[{name}]今日开宝箱次数已用完")
                else:
                    print(f"账号[{name}]开宝箱冷却时间还有{int(open_time / 1000)}秒")
        else:
            print(f"账号[{name}]账号获取开宝箱失败:疑似cookies格式不完整")
    except Exception as reason:  # 捕获所有异常
        print(f"账号[{name}]开宝箱出错啦: {str(reason)}")


# 查询签到
def querySign(can_cookie, name):
    url = "https://nebula.kuaishou.com/rest/n/nebula/sign/queryPopup"
    headers = {'User-Agent': Agent, 'Accept': '*/*', 'Accept-Language': ' zh-CN,zh;q=0.9', 'Cookie': can_cookie}
    try:
        request = urllib.request.Request(url=url, headers=headers)
        response = urllib.request.urlopen(request, timeout=10)
        str_result = response.read().decode('UTF-8')
        json_arr = json.loads(str_result)
        
        # 逐层校验字段，避免KeyError
        data = json_arr.get('data', {})
        sign_popup = data.get('nebulaSignInPopup', {})
        result_code = sign_popup.get('todaySigned', None)
        
        if result_code is True:
            sub_title = sign_popup.get('subTitle', '')
            title = sign_popup.get('title', '')
            print(f"账号[{name}]今日已签到{sub_title},{title}")
        elif result_code is False:
            sign(can_cookie, name)  # 未签到则执行签到
        else:
            print(f"账号[{name}]签到状态查询失败: 返回字段不完整")
    except Exception as reason:
        print(f"账号[{name}]查询签到出错啦: {str(reason)}")


# 签到
def sign(can_cookie, name):
    url = "https://nebula.kuaishou.com/rest/n/nebula/sign/sign?source=activity"
    headers = {'User-Agent': Agent, 'Accept': '*/*', 'Accept-Language': ' zh-CN,zh;q=0.9', 'Cookie': can_cookie}
    try:
        request = urllib.request.Request(url=url, headers=headers)
        response = urllib.request.urlopen(request, timeout=10)
        str_result = response.read().decode('UTF-8')
        json_arr = json.loads(str_result)
        
        result_code = json_arr.get('result', -1)
        if result_code == 1:
            toast = json_arr.get('data', {}).get('toast', '无提示')
            print(f"账号[{name}]签到成功: {toast}")
        else:
            error_msg = json_arr.get('error_msg', '无错误信息')
            print(f"账号[{name}]签到失败: {error_msg}")
    except Exception as reason:
        print(f"账号[{name}]签到执行出错啦: {str(reason)}")


# 准备分享得金币任务
def setShare(can_cookie, name):
    url = "https://nebula.kuaishou.com/rest/n/nebula/account/withdraw/setShare"
    headers = {'User-Agent': Agent, 'Accept': '*/*', 'Accept-Language': ' zh-CN,zh;q=0.9', 'Cookie': can_cookie}
    try:
        data_can = ""
        data = urllib.parse.urlencode(data_can).encode('utf-8')
        request = urllib.request.Request(url=url, data=data, headers=headers)
        response = urllib.request.urlopen(request, timeout=10)
        str_result = response.read().decode('UTF-8')
        json_arr = json.loads(str_result)
        
        if json_arr.get('result') == 1:
            print(f"账号[{name}]准备分享任务成功,正在执行分享...")
            # 执行分享
            share_url = "https://nebula.kuaishou.com/rest/n/nebula/daily/report?taskId=122"
            share_request = urllib.request.Request(url=share_url, headers=headers)
            share_response = urllib.request.urlopen(share_request, timeout=10)
            share_result = share_response.read().decode('UTF-8')
            share_json = json.loads(share_result)
            
            if share_json.get('result') == 1:
                msg = share_json.get('data', {}).get('msg', '')
                amount = share_json.get('data', {}).get('amount', 0)
                print(f"账号[{name}]分享任务成功: {msg}{amount}")
            else:
                error_msg = share_json.get('error_msg', '无错误信息')
                print(f"账号[{name}]分享任务执行失败:疑似今日已分享. {error_msg}")
        else:
            error_msg = json_arr.get('error_msg', '无错误信息')
            print(f"账号[{name}]准备分享任务失败: {error_msg}")
    except Exception as reason:
        print(f"账号[{name}]执行分享任务出错啦: {str(reason)}")


# 依次执行任务
def taskStat():
    i = 0
    for cookie in Cookies:
        i += 1
        print(f"========开始序号[{i}]任务========")
        cookie = cookie.replace("@", "").strip()  # 新增去空格
        if not cookie:  # 跳过空Cookie
            print(f"序号[{i}]Cookie为空，跳过")
            time.sleep(1)
            continue
            
        json_str = getInformation(cookie)
        code = json_str.get('code', -1)
        if code == 1:
            name = json_str['data']['nickname']
            # 查询签到
            querySign(cookie, name)
            # 分享任务
            setShare(cookie, name)
            # 开宝箱
            openBox(cookie, name)
        else:
            print(f"========序号[{i}]获取信息失败,请检查cookies是否正确========")

        time.sleep(1)


num = len(Cookies)
if num > 0:
    print(f"共找到{num}个快手变量,开始执行任务...")
    taskStat()
else:
    print("未找到快手变量,请检查您的变量名是否为ksjsbCookie,且多个账号用&分割")