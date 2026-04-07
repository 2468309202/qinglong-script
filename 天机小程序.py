#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本脚本仅供学习研究使用，严禁用于任何商业、刷量、违规获利等行为。
使用本脚本所产生的一切风险、账号封禁、法律责任及后果，均由使用者自行承担。
作者仅提供代码参考，不承担任何相关责任。使用即代表您已阅读并同意本声明。
脚本更新链接 记得转存实时更新：https://pan.quark.cn/s/c6416fe69380

"""
"""
天机馆自动化脚本 - 青龙面板适配版
环境变量：TIANJITOKEN（单个token）
功能：签到、分享商品、观看广告
#小程序://天机观/Bd1Y0cGS5NkMT3t   （复制到wx打开）
"""
# 屏蔽SSL警告
import warnings
from urllib3.exceptions import InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)

import requests
import json
import os
import time
import random

# ========== 日志美化模块 ==========
class SimpleLogger:
    """简约日志输出类（参考酷我风格）"""
    
    @staticmethod
    def _log(message):
        """统一打印方法"""
        print(message)
    
    @staticmethod
    def info(msg):
        """信息日志"""
        SimpleLogger._log(msg)
    
    @staticmethod
    def success(msg):
        """成功日志"""
        SimpleLogger._log(f"✅ {msg}")
    
    @staticmethod
    def warning(msg):
        """警告日志"""
        SimpleLogger._log(f"⚠️ {msg}")
    
    @staticmethod
    def error(msg):
        """错误日志"""
        SimpleLogger._log(f"❌ {msg}")
    
    @staticmethod
    def step(msg):
        """步骤日志"""
        SimpleLogger._log(f"📌 {msg}")
    
    @staticmethod
    def title(msg):
        """标题日志"""
        SimpleLogger._log(f"\n{'='*50}")
        SimpleLogger._log(f"{msg}")
        SimpleLogger._log(f"{'='*50}\n")
    
    @staticmethod
    def separator():
        """分隔线"""
        # 移除虚线分隔线
        SimpleLogger._log("")
    
    @staticmethod
    def box(title, content_dict):
        """信息框"""
        SimpleLogger._log(f"\n{title}")
        for key, value in content_dict.items():
            SimpleLogger._log(f"  {key}: {value}")
        SimpleLogger._log("")
    
    @staticmethod
    def progress(current, total, prefix="进度"):
        """进度显示"""
        percent = (current / total) * 100
        bar_length = 20
        filled = int(bar_length * current / total)
        bar = '=' * filled + '-' * (bar_length - filled)
        SimpleLogger._log(f"{prefix}: [{bar}] {current}/{total} ({percent:.1f}%)")

# 创建全局日志实例
log = SimpleLogger()

# ========== 核心配置 ==========
TIANJITOKEN = os.getenv("TIANJITOKEN", "")
BASE_URL = "https://xcx.tianjiguan.cn"

# 接口地址
USER_INFO_URL = f"{BASE_URL}/api/user/userinfo"
TASK_LIST_URL = f"{BASE_URL}/api/user/tasklist"
SIGN_URL = f"{BASE_URL}/api/user/sign"
SEE_AD_URL = f"{BASE_URL}/api/user/seeAd"
SHARE_URL = f"{BASE_URL}/api/user/share"  # 新的分享商品接口
PRODUCT_DETAIL_URL = f"{BASE_URL}/api/product/detail/id"

# 配置参数
SHARE_PRODUCT_COUNT = 10  # 分享商品次数（每日上限10次）
WATCH_AD_COUNT = 50  # 观看广告次数（每日上限50次）

# ========== 请求头 ==========
def get_headers():
    """获取请求头"""
    headers = {
        "host": "xcx.tianjiguan.cn",
        "x-access-token": TIANJITOKEN,
        "x-requested-with": "XMLHttpRequest",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf254181c) XWEB/19201",
        "xweb_xhr": "1",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "accept": "*/*",
        "sec-fetch-site": "cross-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://servicewechat.com/wx7829675630d0305e/8/page-frame.html",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9"
    }
    return headers

# 随机延时
def random_sleep(min_sec=1, max_sec=3):
    """随机延时"""
    sleep_time = random.uniform(min_sec, max_sec)
    time.sleep(sleep_time)

# ========== 用户信息查询 ==========
def get_user_info():
    """查询用户信息"""
    if not TIANJITOKEN:
        log.error("未配置TIANJITOKEN环境变量！")
        return None
    
    headers = get_headers()
    params = {"token": TIANJITOKEN}
    
    try:
        log.step("正在查询用户信息...")
        response = requests.get(
            url=USER_INFO_URL,
            headers=headers,
            params=params,
            timeout=15,
            verify=False
        )
        result = response.json()
        
        if result.get("code") == 1:
            data = result.get("data", {})
            log.box("用户信息", {
                "用户名": data.get("username", ""),
                "昵称": data.get("nickname", ""),
                "手机号": data.get("mobile", ""),
                "积分": data.get("score", 0),
                "兑换次数": data.get("exchange_num", 0),
                "等级": data.get("level", 0)
            })
            return data
        else:
            log.error(f"查询用户信息失败：{result.get('msg', '未知')}")
            return None
            
    except Exception as e:
        log.error(f"查询用户信息异常：{str(e)[:100]}")
        return None

# ========== 签到功能 ==========
def daily_sign():
    """每日签到"""
    if not TIANJITOKEN:
        log.error("未配置TIANJITOKEN环境变量！")
        return False
    
    headers = get_headers()
    params = {"token": TIANJITOKEN}
    
    try:
        log.step("正在执行签到...")
        random_sleep(1, 2)
        response = requests.get(
            url=SIGN_URL,
            headers=headers,
            params=params,
            timeout=15,
            verify=False
        )
        result = response.json()
        
        if result.get("code") == 1:
            msg = result.get("msg", "")
            if "签到成功" in msg:
                log.success(f"签到成功！获得50积分")
                return True
            elif "已签到" in msg:
                log.success("今日已签到")
                return True
            else:
                log.warning(f"签到结果：{msg}")
                return False
        else:
            log.error(f"签到失败：{result.get('msg', '未知')}")
            return False
            
    except Exception as e:
        log.error(f"签到异常：{str(e)[:100]}")
        return False

# ========== 分享商品功能 ==========
def share_product():
    """分享商品"""
    if not TIANJITOKEN:
        log.error("未配置TIANJITOKEN环境变量！")
        return False
    
    headers = get_headers()
    params = {"token": TIANJITOKEN}
    
    try:
        log.step("正在分享商品...")
        random_sleep(1, 2)
        response = requests.get(
            url=SHARE_URL,
            headers=headers,
            params=params,
            timeout=15,
            verify=False
        )
        result = response.json()
        
        if result.get("code") == 1:
            msg = result.get("msg", "")
            if "分享成功" in msg:
                log.success("分享商品成功！获得30积分")
                return True
            else:
                log.warning(f"分享商品结果：{msg}")
                return False
        else:
            log.error(f"分享商品失败：{result.get('msg', '未知')}")
            return False
            
    except Exception as e:
        log.error(f"分享商品异常：{str(e)[:100]}")
        return False

# ========== 观看广告功能 ==========
def watch_ad():
    """观看广告"""
    if not TIANJITOKEN:
        log.error("未配置TIANJITOKEN环境变量！")
        return False
    
    headers = get_headers()
    params = {"token": TIANJITOKEN}
    
    try:
        log.step("正在观看广告...")
        random_sleep(20, 22)  # 观看广告需要20秒左右的延迟
        response = requests.get(
            url=SEE_AD_URL,
            headers=headers,
            params=params,
            timeout=15,
            verify=False
        )
        result = response.json()
        
        if result.get("code") == 1:
            log.success("观看广告成功！获得30积分")
            return True
        else:
            log.error(f"观看广告失败：{result.get('msg', '未知')}")
            return False
            
    except Exception as e:
        log.error(f"观看广告异常：{str(e)[:100]}")
        return False

# ========== 批量分享商品 ==========
def batch_share_product():
    """批量分享商品"""
    if not TIANJITOKEN:
        log.error("未配置TIANJITOKEN环境变量！")
        return
    
    log.title(f"开始执行分享商品任务（共 {SHARE_PRODUCT_COUNT} 次）")
    success_count = 0
    fail_count = 0
    
    for i in range(1, SHARE_PRODUCT_COUNT + 1):
        log.progress(i, SHARE_PRODUCT_COUNT, "分享商品进度")
        
        # 商品间随机间隔
        if i > 1:
            log.info("分享间隔休息...（2-4秒）")
            random_sleep(2, 4)
        
        log.separator()
        is_success = share_product()
        if is_success:
            success_count += 1
        else:
            fail_count += 1
    
    # 汇总结果
    log.title("分享商品任务执行汇总")
    log.separator()
    log.info(f"总任务数：{SHARE_PRODUCT_COUNT}")
    log.info(f"成功次数：{success_count}")
    log.info(f"失败次数：{fail_count}")
    log.info(f"成功率：{(success_count/SHARE_PRODUCT_COUNT*100):.1f}%")
    if SHARE_PRODUCT_COUNT > 0:
        progress_percent = (success_count / SHARE_PRODUCT_COUNT) * 100
        bar_length = 20
        filled = int(bar_length * success_count / SHARE_PRODUCT_COUNT)
        bar = '=' * filled + '-' * (bar_length - filled)
        log.info(f"任务进度：[{bar}] {success_count}/{SHARE_PRODUCT_COUNT} ({progress_percent:.1f}%)")
    log.separator()

# ========== 批量观看广告 ==========
def batch_watch_ad():
    """批量观看广告"""
    if not TIANJITOKEN:
        log.error("未配置TIANJITOKEN环境变量！")
        return
    
    log.title(f"开始执行观看广告任务（共 {WATCH_AD_COUNT} 次）")
    success_count = 0
    fail_count = 0
    
    for i in range(1, WATCH_AD_COUNT + 1):
        log.progress(i, WATCH_AD_COUNT, "观看广告进度")
        
        # 广告间随机间隔
        if i > 1:
            log.info("广告间隔休息...（2-4秒）")
            random_sleep(2, 4)
        
        log.separator()
        is_success = watch_ad()
        if is_success:
            success_count += 1
        else:
            fail_count += 1
    
    # 汇总结果
    log.title("观看广告任务执行汇总")
    log.separator()
    log.info(f"总任务数：{WATCH_AD_COUNT}")
    log.info(f"成功次数：{success_count}")
    log.info(f"失败次数：{fail_count}")
    log.info(f"成功率：{(success_count/WATCH_AD_COUNT*100):.1f}%")
    if WATCH_AD_COUNT > 0:
        progress_percent = (success_count / WATCH_AD_COUNT) * 100
        bar_length = 20
        filled = int(bar_length * success_count / WATCH_AD_COUNT)
        bar = '=' * filled + '-' * (bar_length - filled)
        log.info(f"任务进度：[{bar}] {success_count}/{WATCH_AD_COUNT} ({progress_percent:.1f}%)")
    log.separator()

# ========== 主程序 ==========
if __name__ == "__main__":
    log.title("天机馆自动化脚本")
    log.info(f"脚本启动时间：{time.strftime('%Y-%m-%d %H:%M:%S')}")
    log.separator()
    
    # 转存提示
    log.info("请转存支持一下 https://pan.xunlei.com/s/VOodnb5uV0DuzprIV_m66JfVA1 谢谢！")
    log.separator()
    
    # 查询用户信息
    user_info = get_user_info()
    if not user_info:
        log.error("无法获取用户信息，脚本终止！")
        exit(1)
    
    log.separator()
    
    # 执行签到
    daily_sign()
    log.separator()
    
    # 执行分享商品任务
    batch_share_product()
    log.separator()
    
    # 执行观看广告任务
    batch_watch_ad()
    log.separator()
    
    # 再次查询用户信息
    log.step("再次查询用户信息，查看积分变化...")
    final_user_info = get_user_info()
    if final_user_info and user_info:
        score_change = final_user_info.get("score", 0) - user_info.get("score", 0)
        log.success(f"积分变化：{user_info.get('score', 0)} -> {final_user_info.get('score', 0)} (+{score_change})")
    
    log.title("任务执行完成")
    log.success("签到+分享商品+观看广告任务全部执行完毕！")
    log.info(f"脚本结束时间：{time.strftime('%Y-%m-%d %H:%M:%S')}")
    
