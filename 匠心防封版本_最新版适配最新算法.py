import requests, time, hashlib, urllib.parse, os, re, base64, random
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
#================= 环境变量说明 =================
# 变量名 QWYX_DATA，请在环境变量中配置：
# 格式: miniOpenId#unionId
# 多账号，把多个账号用 & 符号连起来：账号1的miniOpenId#账号1的unionId & 账号2的miniOpenId#账号2的unionId
# 抓取域名为 https://api.quwayouxuan.com
# 示例搜索复制这个整个链接参数 https://api.quwayouxuan.com/consumer/consumer/checkOpenid.do?
# openid =miniOpenId
# unionid =unionid
# 欢迎进群交流：978659787，1016916079（群更新比较快）
def _0xdeb(s):
    return base64.b64decode(s).decode('utf-8')

def load_send():
    p = os.path.dirname(os.path.abspath(__file__)) + "/notify.py"
    if os.path.exists(p):
        try:
            from notify import send
            return send
        except: return None
    return None

send = load_send()

class _0x3b8a:
    def __init__(self):
        self._0x52a1 = base64.b64decode("c3VwZXJqaW5n").decode()
        self._0x4b22 = base64.b64decode("aHR0cHM6Ly9hcGkucXV3YXlvdXh1YW4uY29t").decode()
        self.headers = {
            _0xdeb("VXNlci1BZ2VudA=="): _0xdeb("TW96aWxsYS81LjAgKExpbnV4OyBBbmRyb2lkIDE2OyB3dikgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgTWljcm9NZXNzZW5nZXIvOC4wLjY1IE1pbmlQcm9ncmFtRW52L2FuZHJvaWQ="),
            _0xdeb("eHdlYl94aHI="): "1", 
            _0xdeb("Q29udGVudC1UeXBl"): _0xdeb("YXBwbGljYXRpb24veC13d3ctZm9ybS11cmxlbmNvZGVk"), 
            _0xdeb("QWNjZXB0"): "*/*",
            _0xdeb("UmVmZXJlcg=="): _0xdeb("aHR0cHM6Ly9zZXJ2aWNld2VjaGF0LmNvbS93eGRkYWEwODMyZTZhY2M1ZjEvMTIzL3BhZ2UtZnJhbWUuaHRtbA==")
        }
        self._0x88c = {
            "os": "miniProgram",
            "deviceabout": "miniProgram",
            "version": "1.3.00",
            "miniprogram_os": "Android"
        }
        self._0x221c = None
        self._0x119a = "o_" + "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=26))

    def _0x1c3d(self, _0x221a):
        _0x5b12 = sorted(_0x221a.keys())
        _0x33e1 = "".join([f"{k}={_0x221a[k]}" for k in _0x5b12])
        _0x44f2 = (_0x33e1 + self._0x52a1).replace(" ", "")
        _0x99a1 = urllib.parse.quote(_0x44f2, safe='')
        _0x77b2 = re.sub(r"[!|'|\(|\)|\~|\*]", lambda m: "%" + "{:02X}".format(ord(m.group(0))), _0x99a1)
        return hashlib.sha1(_0x77b2.encode('utf-8')).hexdigest().lower()

    def _0x4c2d(self, length=32):
        return "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789", k=length))

    def _0x3a4c(self, token):
        try:
            print(_0xdeb("ICBbK10g8J+UkCDmraPlnKjlkK/liqggRUNESCDlrpXp钥5Y2PllYblr7XpYvpmLLlsIHmj6HmiYsuLi4="))
            _0x99e1 = ec.generate_private_key(ec.SECP256R1())
            _0x88f2 = _0x99e1.public_key()
            _0x1c7a = _0x88f2.public_bytes(
                encoding=Encoding.X962,
                format=PublicFormat.UncompressedPoint
            )
            _0x33d1 = base64.b64encode(_0x1c7a).decode('utf-8')
            _0x4f1a = os.urandom(32)
            _0x55d1 = base64.b64encode(_0x4f1a).decode('utf-8')
            
            _0x11e2 = {
                **self._0x88c,
                _0xdeb("Y2xpZW50UHVibGljS2V5"): urllib.parse.quote(_0x33d1),
                _0xdeb("dGltZXN0YW1w"): str(int(time.time())),
                _0xdeb("c2FsdA=="): _0x55d1,
                _0xdeb("ZGV2aWNl"): self._0x119a,
                _0xdeb("dG9rZW4="): token
            }
            _0x11e2["key"] = self._0x1c3d(_0x11e2)
            
            _0x77d1 = requests.post(f"{self._0x4b22}" + _0xdeb("L2R5bmFtaWNfa2V5L2dldFNlcnZlclB1YmxpY0tleS5kbw=="), data=_0x11e2, headers=self.headers, timeout=10).json()
            if _0x77d1.get("code") != 1:
                print(f"  [-] ❌ 协商失败: {_0x77d1.get('message')}")
                return False
                
            _0xaa1c = _0x77d1.get("data", {}).get(_0xdeb("cHVibGljS2V5"))
            if not _0xaa1c:
                return False
                
            _0xbb11 = base64.b64decode(_0xaa1c)
            _0xee12 = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), _0xbb11)
            _0xdd1a = _0x99e1.exchange(ec.ECDH(), _0xee12)
            
            _0xcc2a = f'{{"device":"{self._0x119a}","token":"{token}"}}'
            _0xff21 = HKDF(algorithm=hashes.SHA256(), length=32, salt=_0x4f1a, info=_0xcc2a.encode('utf-8'))
            self._0x221c = _0xff21.derive(_0xdd1a)
            print(_0xdeb("ICBbK10g8J+RlSDlr4bku6XljYPljY9miJDlip8h5a6J5YWo5L+h6YGT5bu656uL5a6M5q+V4oCC"))
            return True
        except Exception as e:
            print(f"  [-] ❌ 密钥协商异常: {str(e)}")
            return False

    def _0x4f12(self, payload_dict):
        iv = os.urandom(12)
        import json
        plaintext = json.dumps(payload_dict, separators=(',', ':'), ensure_ascii=False)
        aesgcm = AESGCM(self._0x221c)
        ciphertext_with_tag = aesgcm.encrypt(iv, plaintext.encode('utf-8'), b"")
        return base64.b64encode(iv + ciphertext_with_tag).decode('utf-8')

    def _0x5b34(self, encrypted_base64):
        try:
            combined = base64.b64decode(encrypted_base64)
            iv, ciphertext_with_tag = combined[:12], combined[12:]
            aesgcm = AESGCM(self._0x221c)
            return aesgcm.decrypt(iv, ciphertext_with_tag, b"").decode('utf-8')
        except Exception as e:
            return None

    def _0x1f5d(self, url_path, biz_data, token):
        url = f"{self._0x4b22}{url_path}"
        full_biz_data = {**self._0x88c, "token": token, **biz_data}
        full_biz_data["key"] = self._0x1c3d(full_biz_data)
        
        headers = self.headers.copy()
        headers[_0xdeb("WC1SZXF1ZXN0LUlk")] = self._0x4c2d(32)
        headers[_0xdeb("WC1EZXZpY2UtSWQ=")] = self._0x119a
        headers[_0xdeb("WC1Ub2tlbg==")] = token
        
        if self._0x221c:
            try:
                headers[_0xdeb("WC1QYXJhbQ==")] = self._0x4f12(full_biz_data)
                res_obj = requests.post(url, data={}, headers=headers, timeout=10).json()
                if res_obj.get("code") == 4096:
                    self._0x221c = None
                    if self._0x3a4c(token):
                        return self._0x1f5d(url_path, biz_data, token)
                    return {"code": -1, "message": "ERR_TUNNEL"}
                
                if "data" in res_obj and res_obj.get("code") == 1 and isinstance(res_obj["data"], str):
                    decrypted_json_str = self._0x5b34(res_obj["data"])
                    if decrypted_json_str:
                        import json
                        res_obj["data"] = json.loads(decrypted_json_str)
                return res_obj
            except Exception:
                self._0x221c = None
                
        return requests.post(url, data=full_biz_data, headers=headers, timeout=10).json()

class _0x9f1a(_0x3b8a):
    def run_account(self, idx, acc_data):
        parts = acc_data.strip().split("#")
        _t = parts[0]
        acc_name = parts[1] if len(parts) > 1 else f"账号{idx}"
        
        print(f"\n" + "-"*35 + f"\n▶ [安全版] 正在处理: {acc_name}")
        
        try:
            _0x37c = self._0x3a4c(_t)
            if not _0x37c:
                print("  [-] ⚠️ 协商失败，切换至明文降级模式...")
            
            biz_validate = {"current_time": str(int(time.time() * 1000)), "source": "4"}
            l_res = self._0x1f5d(_0xdeb("L3Rhc2svdGFzay90YXNrTGlzdC5kbw=="), biz_validate, _t)
            
            if l_res.get("code") != 1 and not l_res.get("data", {}).get("userinfo"):
                print(f"  [-] ❌ Token已失效或请求被拦截: {l_res.get('message', '未知错误')}")
                return f"👤 {acc_name}: Token失效，请重新抓包"

            u_i = l_res.get("data", {}).get("userinfo", {})
            real_name = u_i.get("username", acc_name)
            initial_pts = u_i.get("points", "0")
            print(f"  [-] 账户: {real_name} | 跑前积分: {initial_pts}")

            biz_signin = {
                "current_time": str(int(time.time() * 1000)),
                "taskid": "1",
                "subtask_id": "0"
            }
            c_res = self._0x1f5d(_0xdeb("L3Rhc2svdGFzay90YXNrU3VjY3Jzcy5kbw=="), biz_signin, _t)
            c_m = c_res.get('message', '完成')
            print(f"  [-] 签到结果: {c_m}")
            c_s = "✅ 签到成功" if c_res.get('code') == 1 or any(k in c_m for k in ["已", "完成"]) else f"❌ {c_m}"

            a_c = 0
            gained_pts = 0
            max_attempts = 30 
            
            print("  [-] 正在进行视频任务，遵循 160-200 秒防封冷却并全程处于国密隧道保护中...")
            for i in range(max_attempts):
                biz_video = {
                    "current_time": str(int(time.time() * 1000)),
                    "taskid": "40",
                    "subtask_id": "0"
                }
                a_res = self._0x1f5d(_0xdeb("L3Rhc2svdGFzay90YXNrU3VjY3Jzcy5kbw=="), biz_video, _t)
                
                code = a_res.get("code")
                msg = a_res.get("message", "未知错误")

                if code == 1:
                    a_c += 1
                    pts = a_res.get("data", {}).get("points", 60)
                    gained_pts += int(pts) if str(pts).isdigit() else 60
                    
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
                    print(f"      └─ 异常拦截: {msg} (建议稍后再试)")
                    break
            
            v_s = f"🎬 执行({a_c}次) | 收益: +{gained_pts}分"
            print(f"  [√] 账号 [{real_name}] 处理完毕")
            return f"👤 昵称：{real_name}\n   ├ 原有：{initial_pts} 分\n   ├ 签到：{c_s}\n   └ 视频：{v_s}"

        except Exception as e:
            print(f"  [x] 异常: {str(e)}")
            return f"⚠️ {acc_name}: 运行异常"

def main():
    _h = "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n┃  匠 心 忠 华 助 手 (v9.0 大飞版) ┃\n┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛"
    print(_h)
    _d = os.environ.get("QWYX_DATA", "")
    if not _d:
        print("\n❌ 未找到 QWYX_DATA，请配置环境变量 (格式: token#备注名)")
        return

    _accs = _d.replace("\n", "&").split("&")
    bot = _0x9f1a()
    _reps = []
    
    for i, a in enumerate(_accs, 1):
        if a.strip(): _reps.append(bot.run_account(i, a))
    
    _f = "\n" + "="*35 + "\n🎯 任务汇总报告：\n\n" + "\n\n".join(_reps)
    print(_f)
    
    if send:
        send("匠心忠华安全版任务报告", _h + "\n\n" + "\n\n".join(_reps))

if __name__ == "__main__":
    main()
