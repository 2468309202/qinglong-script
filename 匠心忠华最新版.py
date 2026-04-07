import requests, time, hashlib, urllib.parse, os, re, base64, random
# ================= 环境变量说明 =================
# 变量名 QWYX_DATA，请在环境变量中配置：
# 格式: miniOpenId#unionId
# 多账号，把多个账号用 & 符号连起来：账号1的miniOpenId#账号1的unionId & 账号2的miniOpenId#账号2的unionId
# 抓取域名为 https://api.quwayouxuan.com
# 示例搜索复制这个整个链接参数 https://api.quwayouxuan.com/consumer/consumer/checkOpenid.do?
# openid =miniOpenId
# unionid =unionid
# 欢迎进群交流：978659787，1016916079
# 脚本都在这里迅雷：
# 链接：https://pan.xunlei.com/s/VOpYg9wMaY0Uxnd-0Pmzo0GiA1?pwd=px5h#
def load_send():
    p = os.path.dirname(os.path.abspath(__file__)) + "/notify.py"
    if os.path.exists(p):
        try:
            from notify import send
            return send
        except: return None
    return None

send = load_send()

class QuWaRobot:
    def __init__(self):
        # 核心混淆存储
        self._0x52a1 = base64.b64decode("c3VwZXJqaW5n").decode()
        self._0x4b22 = base64.b64decode("aHR0cHM6Ly9hcGkucXV3YXlvdXh1YW4uY29t").decode()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Mac MacWechat/WMPF MacWechat/3.8.7(0x13080712) UnifiedPCMacWechat(0xf2641843) XWEB/19346",
            "xweb_xhr": "1", "Content-Type": "application/x-www-form-urlencoded", "Accept": "*/*",
            "Referer": "https://servicewechat.com/wxddaa0832e6acc5f1/123/page-frame.html"
        }

    # 加密后的算法逻辑
    def _0x1c3d(self, _0x221a):
        _0x5b12 = sorted(_0x221a.keys())
        _0x33e1 = "".join([f"{k}={_0x221a[k]}" for k in _0x5b12])
        _0x44f2 = (_0x33e1 + self._0x52a1).replace(" ", "")
        _0x99a1 = urllib.parse.quote(_0x44f2, safe='')
        _0x77b2 = re.sub(r"[!|'|\(|\)|\~|\*]", lambda m: "%" + "{:02X}".format(ord(m.group(0))), _0x99a1)
        return hashlib.sha1(_0x77b2.encode('utf-8')).hexdigest().lower()

    def run_account(self, idx, acc_data):
        if "#" not in acc_data: return f"👤 账号{idx}: 格式错误"
        oid, uid = acc_data.strip().split("#")
        _0x88c = {"os": "miniProgram", "deviceabout": "miniProgram", "version": "1.3.00", "miniprogram_os": "Mac"}
        
        print(f"\n" + "-"*35 + f"\n▶ 正在处理账号 [{idx}]")
        
        try:
            # 1. 登录
            _0x11a = {**_0x88c, "current_time": str(int(time.time() * 1000)), "miniOpenId": oid, "unionId": uid}
            _0x11a["key"] = self._0x1c3d(_0x11a)
            res = requests.get(f"{self._0x4b22}/login/third.do", params=_0x11a, headers=self.headers, timeout=10).json()
            if res.get("code") != 1: 
                print(f"  [-] 登录失败: {res.get('message')}")
                return f"👤 账号{idx}: 登录失败"
            _t = res.get("data", {}).get("token")

            # 2. 获取状态
            _0x22b = {**_0x88c, "current_time": str(int(time.time() * 1000)), "token": _t, "source": "4"}
            _0x22b["key"] = self._0x1c3d(_0x22b)
            l_res = requests.post(f"{self._0x4b22}/task/task/taskList.do", data=_0x22b, headers=self.headers, timeout=10).json()
            u_i = l_res.get("data", {}).get("userinfo", {})
            name, pts = u_i.get("username", "用户"), u_i.get("points", "0")
            print(f"  [-] 账户: {name} | 当前积分: {pts}")

            # 3. 签到 (ID: 1)
            _0x33c = {**_0x88c, "current_time": str(int(time.time() * 1000)), "token": _t, "taskid": "1", "subtask_id": "0"}
            _0x33c["key"] = self._0x1c3d(_0x33c)
            c_res = requests.get(f"{self._0x4b22}/task/task/taskSuccrss.do", params=_0x33c, headers=self.headers, timeout=10).json()
            c_m = c_res.get('message', '完成')
            print(f"  [-] 签到结果: {c_m}")
            c_s = "✅ 签到成功" if c_res.get('code') == 1 or "已" in c_m else f"❌ {c_m}"

            # 4. 视频任务 (ID: 40 循环)
            a_c = 0
            print("  [-] 正在开始视频任务循环...")
            for i in range(1, 11):
                _0x44d = {**_0x88c, "current_time": str(int(time.time() * 1000)), "token": _t, "taskid": "40", "subtask_id": "0"}
                _0x44d["key"] = self._0x1c3d(_0x44d)
                a_res = requests.get(f"{self._0x4b22}/task/task/taskSuccrss.do", params=_0x44d, headers=self.headers, timeout=10).json()
                
                if a_res.get("code") == 1:
                    a_c += 1
                    print(f"      进度({i}/10): 领取成功")
                    if i < 10: 
                        _wt = random.randint(25, 35)
                        print(f"      (随机等待 {_wt} 秒防止异常...)")
                        time.sleep(_wt)
                else:
                    print(f"      进度({i}/10): 任务已看完或今日上限")
                    break
            
            v_s = f"🎬 完成({a_c}/10)" if a_c > 0 else "🎬 视频任务已看完"
            print(f"  [√] 账号 [{idx}] 处理完毕")
            return f"👤 昵称：{name}\n   ├ 积分：{pts}\n   ├ 签到：{c_s}\n   └ 视频：{v_s}"

        except Exception as e:
            print(f"  [x] 异常: {str(e)}")
            return f"⚠️ 账号{idx}: 异常"

def main():
    _h = "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n┃      匠 心 忠 华 助 手 (v6.5)      ┃\n┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛"
    print(_h)
    _d = os.environ.get("QWYX_DATA", "")
    if not _d:
        print("\n❌ 未找到 QWYX_DATA，请检查环境变量配置")
        return

    _accs = _d.replace("\n", "&").split("&")
    bot = QuWaRobot()
    _reps = []
    
    for i, a in enumerate(_accs, 1):
        if a.strip(): _reps.append(bot.run_account(i, a))
    
    _f = "\n" + "="*35 + "\n🎯 任务汇总报告：\n\n" + "\n\n".join(_reps)
    print(_f)
    
    if send:
        send("匠心忠华任务报告", _h + "\n\n" + "\n\n".join(_reps))

if __name__ == "__main__":
    main()