import requests, time, hashlib, urllib.parse, os, re, base64, random

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
        self._0x52a1 = base64.b64decode("c3VwZXJqaW5n").decode()
        self._0x4b22 = base64.b64decode("aHR0cHM6Ly9hcGkucXV3YXlvdXh1YW4uY29t").decode()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 16; wv) AppleWebKit/537.36 MicroMessenger/8.0.65 MiniProgramEnv/android",
            "xweb_xhr": "1", "Content-Type": "application/x-www-form-urlencoded", "Accept": "*/*",
            "Referer": "https://servicewechat.com/wxddaa0832e6acc5f1/123/page-frame.html"
        }

    def _0x1c3d(self, _0x221a):
        _0x5b12 = sorted(_0x221a.keys())
        _0x33e1 = "".join([f"{k}={_0x221a[k]}" for k in _0x5b12])
        _0x44f2 = (_0x33e1 + self._0x52a1).replace(" ", "")
        _0x99a1 = urllib.parse.quote(_0x44f2, safe='')
        _0x77b2 = re.sub(r"[!|'|\(|\)|\~|\*]", lambda m: "%" + "{:02X}".format(ord(m.group(0))), _0x99a1)
        return hashlib.sha1(_0x77b2.encode('utf-8')).hexdigest().lower()

    def run_account(self, idx, acc_data):
        parts = acc_data.strip().split("#")
        _t = parts[0]
        acc_name = parts[1] if len(parts) > 1 else f"账号{idx}"
        
        _0x88c = {"os": "miniProgram", "deviceabout": "miniProgram", "version": "1.3.00", "miniprogram_os": "Android"}
        
        print(f"\n" + "-"*35 + f"\n▶ 正在处理: {acc_name}")
        
        try:
            # 1. 验证 Token
            _0x22b = {**_0x88c, "current_time": str(int(time.time() * 1000)), "token": _t, "source": "4"}
            _0x22b["key"] = self._0x1c3d(_0x22b)
            l_res = requests.post(f"{self._0x4b22}/task/task/taskList.do", data=_0x22b, headers=self.headers, timeout=10).json()
            
            if l_res.get("code") != 1 and not l_res.get("data", {}).get("userinfo"):
                print(f"  [-] ❌ Token已失效: {l_res.get('message', '未知错误')}")
                return f"👤 {acc_name}: Token失效，请重新抓包"

            u_i = l_res.get("data", {}).get("userinfo", {})
            real_name = u_i.get("username", acc_name)
            initial_pts = u_i.get("points", "0")
            print(f"  [-] 账户: {real_name} | 跑前积分: {initial_pts}")

            # 2. 每日签到
            _0x33c = {**_0x88c, "current_time": str(int(time.time() * 1000)), "token": _t, "taskid": "1", "subtask_id": "0"}
            _0x33c["key"] = self._0x1c3d(_0x33c)
            c_res = requests.get(f"{self._0x4b22}/task/task/taskSuccrss.do", params=_0x33c, headers=self.headers, timeout=10).json()
            c_m = c_res.get('message', '完成')
            print(f"  [-] 签到结果: {c_m}")
            c_s = "✅ 签到成功" if c_res.get('code') == 1 or any(k in c_m for k in ["已", "完成"]) else f"❌ {c_m}"

            # 3. 视频任务 (强力冷却防封模式)
            a_c = 0
            gained_pts = 0
            max_attempts = 30 
            
            print("  [-] 正在进行视频任务，遵循 160-200 秒防封冷却...")
            for i in range(max_attempts):
                _0x44d = {**_0x88c, "current_time": str(int(time.time() * 1000)), "token": _t, "taskid": "40", "subtask_id": "0"}
                _0x44d["key"] = self._0x1c3d(_0x44d)
                a_res = requests.get(f"{self._0x4b22}/task/task/taskSuccrss.do", params=_0x44d, headers=self.headers, timeout=10).json()
                
                code = a_res.get("code")
                msg = a_res.get("message", "未知错误")

                if code == 1:
                    a_c += 1
                    pts = a_res.get("data", {}).get("points", 60)
                    gained_pts += int(pts) if str(pts).isdigit() else 60
                    
                    # 核心防封逻辑：按照要求，严格挂机 160 到 200 秒
                    wait_time = random.randint(160, 200)
                    print(f"      └─ 第{a_c}次: ✅ +{pts}积分 | 累计: {gained_pts}")
                    print(f"         🛡️ [深度防封] 冷却中，等待 {wait_time} 秒后再执行下一次...")
                    time.sleep(wait_time)
                    
                elif any(kw in msg for kw in ["上限", "已达", "超出"]):
                    print(f"      └─ 触发服务器上限，今日共成功 {a_c} 次")
                    break
                elif any(kw in msg for kw in ["不能重复", "已完成", "已领取"]):
                    print(f"      └─ 任务已全部看完 ({msg})")
                    break
                else:
                    print(f"      └─ 异常拦截: {msg} (已被风控拦截)")
                    break
            
            v_s = f"🎬 执行({a_c}次) | 收益: +{gained_pts}分"
            print(f"  [√] 账号 [{real_name}] 处理完毕")
            return f"👤 昵称：{real_name}\n   ├ 原有：{initial_pts} 分\n   ├ 签到：{c_s}\n   └ 视频：{v_s}"

        except Exception as e:
            print(f"  [x] 异常: {str(e)}")
            return f"⚠️ {acc_name}: 运行异常"

def main():
    _h = "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n┃  匠 心 忠 华 助 手 (v8.2 冷却版)   ┃\n┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛"
    print(_h)
    _d = os.environ.get("QWYX_DATA", "")
    if not _d:
        print("\n❌ 未找到 QWYX_DATA，请配置环境变量 (格式: token#备注名)")
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