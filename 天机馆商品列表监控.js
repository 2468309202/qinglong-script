/**
 * 天机馆商品补货监控 - 积分增强版
 * 适配青龙面板，支持自动通知
 */

const axios = require('axios');
const notify = require('./sendNotify'); 

// ========== 1. 配置区域 ==========
const token = process.env.TIANJITOKEN;

// 监控关键词：留空则监控所有商品。
const KEYWORDS = []; 

// 缓存对象：记录商品 ID 的库存状态，防止重复推送
let lastStatus = {};

const headers = {
    "Host": "xcx.tianjiguan.cn",
    "X-Access-Token": token,
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.73(0x18004926) NetType/4G Language/zh_CN",
    "Referer": "https://servicewechat.com/wx7829675630d0305e/9/page-frame.html"
};

// ========== 2. 核心监控逻辑 ==========
async function checkMonitor() {
    if (!token) {
        console.log("❌ 错误：未检测到环境变量 TIANJITOKEN");
        return;
    }

    try {
        const url = `https://xcx.tianjiguan.cn/api/product/list?page=1&limit=20&token=${token}`;
        const response = await axios.get(url, { headers, timeout: 10000 });
        const res = response.data;

        if (res.code === 1) {
            const products = res.data.data || [];
            let msgList = [];

            products.forEach(item => {
                const id = item.id;
                const title = item.title;
                const stock = parseInt(item.stock || 0);
                const price = item.price || "未知"; // 对应积分价格

                // 逻辑判断：匹配关键词且有库存
                const isMatch = KEYWORDS.length === 0 || KEYWORDS.some(k => title.includes(k));
                
                if (isMatch && stock > 0) {
                    // 仅在状态变更（无变有）时通知
                    if (!lastStatus[id]) {
                        msgList.push(`📦 【${title}】\n💰 所需积分：${price}\n📊 当前库存：${stock}`);
                    }
                    lastStatus[id] = true;
                } else {
                    lastStatus[id] = false;
                }
            });

            if (msgList.length > 0) {
                const content = msgList.join('\n' + '─'.repeat(15) + '\n');
                console.log("🔔 检测到补货，推送中...");
                await notify.sendNotify("天机馆补货提醒", content);
            } else {
                console.log(`[${new Date().toLocaleTimeString()}] 暂无补货商品`);
            }
        } else {
            console.log(`⚠️ 接口响应异常：${res.msg}`);
        }
    } catch (err) {
        console.log(`❌ 请求失败：${err.message}`);
    }
}

// ========== 3. 运行入口 ==========
(async () => {
    console.log("🚀 天机馆补货监控启动...");
    
    // 首次运行
    await checkMonitor();

    // 如果你想在脚本内实现循环监控（手动挂机模式），取消下面代码的注释：
    /*
    setInterval(async () => {
        await checkMonitor();
    }, 60000); 
    */
})();