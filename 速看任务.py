'''
本脚本仅供学习研究使用，严禁用于任何商业、刷量、违规获利等行为。
使用本脚本所产生的一切风险、账号封禁、法律责任及后果，均由使用者自行承担。
作者仅提供代码参考，不承担任何相关责任。使用即代表您已阅读并同意本声明。
脚本更新链接 记得转存实时更新：https://pan.quark.cn/s/c6416fe69380
'''
# -*- coding: utf-8 -*-
import os
import sys
import time
import random
import json
import logging
import urllib.parse
import signal
import threading
import requests
from typing import Dict, Any

# 全局停止信号
STOP = False

# ====================== 极简日志配置（只保留核心信息） ======================
logging.basicConfig(
    format="%(asctime)s | %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO
)
logger = logging.getLogger("SuKanAuto")
# 禁用多余日志（requests/urllib3）
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

# 关闭SSL警告
requests.packages.urllib3.disable_warnings()

# ====================== 真人化配置（核心防封） ======================
CONFIG = {
    # 任务次数（随机波动，避免固定值）
    "BOX_MAX": random.randint(18, 22),        # 宝箱次数：18-22次（原20）
    "REDPACK_MAX": random.randint(38, 42),    # 拆红包次数：38-42次（原40）
    "VIDEO_MAX": random.randint(190, 210),    # 视频次数：190-210次（原200）
    
    # 真人化延迟（随机波动+非整数，模拟手动操作）
    "BOX_COOLDOWN": (170, 190),               # 宝箱冷却：170-190秒（原175-185）
    "NORMAL_COOLDOWN": (20, 35),              # 视频/红包冷却：20-35秒（原25-30）
    "AD_FAKE_WATCH": (28, 32),                # 看广告时长：28-32秒（原固定30）
    "CLICK_DELAY": (0.5, 2.0),                # 模拟点击延迟：0.5-2秒
    "TASK_INTERVAL": (1, 3),                  # 任务启动间隔：1-3秒（避免同时启动）
    
    # 其他配置
    "RETRY_TIMES": 1,                         # 减少重试（避免高频请求）
    "TIMEOUT": random.randint(18, 22),        # 超时时间：18-22秒（原20）
}

# ====================================================================

class SuKanTask:
    def __init__(self, url: str):
        self.url = url.strip()
        self.params = self._parse_params()
        self.session = self._init_session()
        
        # 收益统计（仅核心）
        self.box_gold = 0
        self.redpack_gold = 0
        self.video_gold = 0
        
        # 任务状态
        self.box_done = False
        self.redpack_done = False
        self.video_done = False
        self.box_exhausted = False
        self.redpack_exhausted = False
        self.video_exhausted = False

    def _parse_params(self) -> Dict[str, str]:
        """解析参数（极简日志）"""
        try:
            qs = self.url.split("?")[1] if "?" in self.url else self.url
            params = dict(urllib.parse.parse_qsl(qs))
            required = ["zyeid", "kt", "p1", "p35"]
            missing = [p for p in required if p not in params]
            if missing:
                logger.error(f"❌ 缺失参数：{missing}")
                sys.exit(1)
            return params
        except Exception as e:
            logger.error(f"❌ 参数解析失败：{e}")
            sys.exit(1)

    def _init_session(self) -> requests.Session:
        """初始化会话（真人化Header）"""
        session = requests.Session()
        session.verify = False
        
        # 真人化User-Agent（随机版本）
        chrome_ver = random.choice(["131.0.6778.260", "130.0.6723.91", "132.0.6831.119"])
        android_ver = random.choice(["15", "14", "13"])
        device_model = random.choice(["23049RAD8C", "22101320C", "23127PN0CC"])
        
        session.headers.update({
            "Host": "welfare-user.palmestore.com",
            "User-Agent": f"Mozilla/5.0 (Linux; Android {android_ver}; {device_model} Build/AQ3A.250226.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/{chrome_ver} Mobile Safari/537.36 zyApp/SuKanRead zyVersion/8.0.{random.randint(1, 3)} zyChannel/801003",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://welfare-user.palmestore.com",
            "X-Requested-With": "com.chaozh.xincao.only.sk",
            "Referer": self.url if "welfare.html" in self.url else f"https://welfare-user.palmestore.com/sukanread/welfare-package/sudu/welfare.html?{urllib.parse.urlencode(self.params)}",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            # 随机添加/移除部分Header（模拟真人请求差异）
            **({"Sec-Fetch-Site": "same-origin"} if random.random() > 0.2 else {}),
            **({"Sec-Fetch-Mode": "cors"} if random.random() > 0.2 else {}),
        })
        return session

    def _simulate_human_click(self, task_name: str):
        """模拟真人点击延迟（防封核心）"""
        delay = random.uniform(*CONFIG["CLICK_DELAY"])
        time.sleep(delay)
        # 极简日志：不打印延迟细节

    def _safe_post(self, payload: dict, task_name: str) -> dict:
        """安全请求（真人化+极简日志）"""
        if STOP:
            return {}
            
        # 模拟真人点击后再请求
        self._simulate_human_click(task_name)
            
        for retry in range(CONFIG["RETRY_TIMES"]):
            try:
                # 随机请求间隔（防封）
                time.sleep(random.uniform(0.3, 1.2))
                
                resp = self.session.post(
                    "https://welfare-user.palmestore.com/api/task/receive",
                    data=payload,
                    timeout=CONFIG["TIMEOUT"]
                )
                resp.raise_for_status()
                
                if not resp.text:
                    time.sleep(2)
                    continue
                    
                result = resp.json()
                return result
            except Exception:
                time.sleep(2)
        
        return {}

    def _wait(self, cooldown_range: tuple, task_name: str):
        """智能等待（随机时长+极简日志）"""
        if STOP:
            return
        sec = random.randint(*cooldown_range)
        # 极简日志：只打印关键等待
        logger.info(f"[{task_name}] 等待 {sec} 秒")
        for _ in range(sec):
            if STOP:
                return
            time.sleep(1)

    # ====================== 宝箱任务（真人化+极简日志） ======================
    def run_box_task(self):
        """宝箱任务（真人化操作）"""
        logger.info(f"[宝箱] 启动任务（{CONFIG['BOX_MAX']}次）")
        done = 0
        
        while done < CONFIG["BOX_MAX"] and not STOP and not self.box_exhausted:
            payload = self.params.copy()
            payload.update({
                'source': 'welfare',
                'showContentInStatusBar': '1',
                'ecpmMix': '0.0',
                'ecpmVideo': '0.0',
                'mcTacid': '',
                'task_type': '201',
                'sub_id': '',
                'smboxid': 'Bh7KiB2kPwPbOwFWlXbn5p2ySx/ogLpWhR4HNY9FQMyQeRcXidW1jvg5UAGel6+ZEK6NRdU6ASBcbEzR27MbBzQ==',
                'id': '1771674648276000008'
            })

            result = self._safe_post(payload, "宝箱")
            
            try:
                if result and result.get("code") == 0:
                    body = result.get("body", {}) or {}
                    gold = body.get("gold_num", 0)
                    
                    if gold <= 0 and done > 0:
                        self.box_exhausted = True
                        logger.info("[宝箱] 任务已完成，跳过后续")
                        break
                    
                    if gold > 0:
                        done += 1
                        self.box_gold += gold
                        logger.info(f"[宝箱] 第{done}次领取 +{gold}金币（累计{self.box_gold}）")
                else:
                    self.box_exhausted = True
                    logger.info("[宝箱] 任务已完成，跳过后续")
                    break
            except Exception:
                self.box_exhausted = True
                logger.info("[宝箱] 任务已完成，跳过后续")
                break

            if done < CONFIG["BOX_MAX"] and not STOP and not self.box_exhausted:
                self._wait(CONFIG["BOX_COOLDOWN"], "宝箱")

        self.box_done = True
        logger.info(f"[宝箱] 任务结束 | 累计{self.box_gold}金币")

    # ====================== 拆红包任务（真人化+极简日志） ======================
    def run_redpack_task(self):
        """拆红包任务（真人化操作）"""
        logger.info(f"[拆红包] 启动任务（{CONFIG['REDPACK_MAX']}次）")
        done = 0
        
        while done < CONFIG["REDPACK_MAX"] and not STOP and not self.redpack_exhausted:
            if self.redpack_exhausted:
                break
                
            # 模拟真人看广告（随机时长）
            ad_sec = random.randint(*CONFIG["AD_FAKE_WATCH"])
            logger.info(f"[拆红包] 看广告 {ad_sec} 秒")
            for _ in range(ad_sec):
                if STOP or self.redpack_exhausted:
                    break
                # 随机停顿（模拟真人中途操作）
                if random.random() > 0.8:
                    time.sleep(random.uniform(0.5, 1.0))
                time.sleep(1)
            
            payload = self.params.copy()
            payload.update({
                'source': 'welfare',
                'showContentInStatusBar': '1',
                'ecpmMix': '0.0',
                'ecpmVideo': '0.0',
                'mcTacid': '',
                'task_type': '224',
                'sub_id': '',
                'smboxid': 'BXORUW3tHy5xhwgvI9UfVHINt4dlONOWeXYekMDoWnwmbu90jDwfjpM0uvFXq33EGuxWIxQgUKeXJIC6US+Oqfg==',
                'id': '4302',
                'position': 'VIDEO_WELFARE_OPEN',
                'reward_ecpm': f"{random.uniform(55.0, 58.0):.2f}",  # 随机ecpm值
                'levelId': '2'
            })

            result = self._safe_post(payload, "拆红包")
            
            try:
                if result:
                    if result.get("code") == 0:
                        body = result.get("body", {}) or {}
                        receive_res = body.get("receive_res", {}) or {}
                        gold = receive_res.get("gold", 0)
                        remaining = receive_res.get("remaining_count", 0)
                        
                        if remaining <= 0:
                            self.redpack_exhausted = True
                            logger.info("[拆红包] 任务已完成，跳过后续")
                            break
                        
                        if gold > 0:
                            done += 1
                            self.redpack_gold += gold
                            logger.info(f"[拆红包] 第{done}次领取 +{gold}金币（累计{self.redpack_gold}）| 剩余{remaining}次")
                    else:
                        self.redpack_exhausted = True
                        logger.info("[拆红包] 任务已完成，跳过后续")
                        break
                else:
                    self.redpack_exhausted = True
                    logger.info("[拆红包] 任务已完成，跳过后续")
                    break
            except Exception:
                self.redpack_exhausted = True
                logger.info("[拆红包] 任务已完成，跳过后续")
                break

            if done < CONFIG["REDPACK_MAX"] and not STOP and not self.redpack_exhausted:
                self._wait(CONFIG["NORMAL_COOLDOWN"], "拆红包")

        self.redpack_done = True
        logger.info(f"[拆红包] 任务结束 | 累计{self.redpack_gold}金币")

    # ====================== 视频任务（真人化+极简日志） ======================
    def run_video_task(self):
        """视频任务（真人化操作）"""
        logger.info(f"[视频] 启动任务（{CONFIG['VIDEO_MAX']}次）")
        done = 0
        
        while done < CONFIG["VIDEO_MAX"] and not STOP and not self.video_exhausted:
            if self.video_exhausted:
                break
                
            # 模拟真人看广告（随机时长+中途停顿）
            ad_sec = random.randint(*CONFIG["AD_FAKE_WATCH"])
            logger.info(f"[视频] 看广告 {ad_sec} 秒")
            for _ in range(ad_sec):
                if STOP or self.video_exhausted:
                    break
                if random.random() > 0.7:
                    time.sleep(random.uniform(0.3, 0.8))
                time.sleep(1)
            
            payload = self.params.copy()
            payload.update({
                'source': 'welfare',
                'showContentInStatusBar': '1',
                'ecpmMix': '0.0',
                'ecpmVideo': '0.0',
                'mcTacid': '',
                'task_type': '216',
                'sub_id': '',
                'smboxid': 'BXORUW3tHy5xhwgvI9UfVHINt4dlONOWeXYekMDoWnwmbu90jDwfjpM0uvFXq33EGuxWIxQgUKeXJIC6US+Oqfg==',
                'id': '3339',
                'position': 'VIDEO_POP_WINDOW',
                'levelId': '2'
            })

            result = self._safe_post(payload, "视频")
            
            try:
                if result:
                    if result.get("code") == 0:
                        body = result.get("body", {}) or {}
                        receive_res = body.get("receive_res", {}) or {}
                        gold = receive_res.get("gold", 0)
                        remaining = receive_res.get("remaining_count", 0)
                        
                        if remaining <= 0:
                            self.video_exhausted = True
                            logger.info("[视频] 任务已完成，跳过后续")
                            break
                        
                        if gold > 0:
                            done += 1
                            self.video_gold += gold
                            logger.info(f"[视频] 第{done}次领取 +{gold}金币（累计{self.video_gold}）| 剩余{remaining}次")
                    else:
                        self.video_exhausted = True
                        logger.info("[视频] 任务已完成，跳过后续")
                        break
                else:
                    self.video_exhausted = True
                    logger.info("[视频] 任务已完成，跳过后续")
                    break
            except Exception:
                self.video_exhausted = True
                logger.info("[视频] 任务已完成，跳过后续")
                break

            if done < CONFIG["VIDEO_MAX"] and not STOP and not self.video_exhausted:
                self._wait(CONFIG["NORMAL_COOLDOWN"], "视频")

        self.video_done = True
        logger.info(f"[视频] 任务结束 | 累计{self.video_gold}金币")

    def run_all_tasks(self):
        """启动所有任务（真人化间隔）"""
        logger.info("\n===== 速看任务启动 =====")
        
        # 真人化：任务不同时启动（间隔1-3秒）
        t1 = threading.Thread(target=self.run_box_task, daemon=True)
        t2 = threading.Thread(target=self.run_redpack_task, daemon=True)
        t3 = threading.Thread(target=self.run_video_task, daemon=True)
        
        t1.start()
        time.sleep(random.uniform(*CONFIG["TASK_INTERVAL"]))
        t2.start()
        time.sleep(random.uniform(*CONFIG["TASK_INTERVAL"]))
        t3.start()
        
        # 等待所有任务完成
        while not STOP:
            if self.box_done and self.redpack_done and self.video_done:
                break
            time.sleep(1)
        
        # 极简汇总
        total = self.box_gold + self.redpack_gold + self.video_gold
        logger.info("\n===== 任务全部完成 =====")
        logger.info(f"宝箱：{self.box_gold}金币 | 拆红包：{self.redpack_gold}金币 | 视频：{self.video_gold}金币")
        logger.info(f"总收益：{total}金币")
        logger.info("=======================")

def signal_handler(signum, frame):
    """停止信号（极简日志）"""
    global STOP
    STOP = True
    logger.warning("\n🛑 停止任务...")

if __name__ == "__main__":
    # 注册停止信号
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 从环境变量读取URL
    YOUR_URL = os.getenv("SUKAN_URL", "").strip()
    if not YOUR_URL:
        logger.error("❌ 未设置环境变量 SUKAN_URL")
        sys.exit(1)

    # 启动任务
    task = SuKanTask(YOUR_URL)
    task.run_all_tasks()
