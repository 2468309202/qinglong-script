/**
 * 天机馆商品补货监控 - 优化完整版
 * 适配青龙面板，支持自动通知
 */

const axios = require('axios');
const notify = require('./sendNotify'); // 确保 scripts 目录下有此文件

// ========== 1. 配置区域 ==========
// 优先读取青龙环境变量中的 TIANJITOKEN
const token = process.env.TIANJITOKEN;

// 监控关键词：留空则监控所有商品。例如：["话费", "E卡"]
const KEYWORDS = []; 

// 缓存对象：用于记录商品上次的库存状态，防止重复报警
let lastStatus = {};

// 请求头配置
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
        console.log("❌ 错误：未在环境变量中检测到 TIANJITOKEN，脚本退出。");
        return;
    }

    try {
        // 使用提供的接口地址
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
                const price = item.price;

                // 逻辑判断：匹配关键词且库存大于0
                const isMatch = KEYWORDS.length === 0 || KEYWORDS.some(k => title.includes(k));
                
                if (isMatch && stock > 0) {
                    // 仅当该商品之前记录为无货（或首次监控）时，才触发通知
                    if (!lastStatus[id]) {
                        msgList.push(`📦 【${title}】\n💰 价格：${price}\n📊 库存：${stock}`);
                    }
                    lastStatus[id] = true; // 标记为有货状态
                } else {
                    lastStatus[id] = false; // 标记为无货或不匹配
                }
            });

            // 如果有新上架/补货的商品，发送通知
            if (msgList.length > 0) {
                const content = msgList.join('\n' + '─'.repeat(15) + '\n');
                console.log("🔔 检测到补货，正在发送通知...");
                await notify.sendNotify("天机馆补货提醒", content);
            } else {
                console.log(`[${new Date().toLocaleTimeString()}] 巡检完毕：暂无匹配商品或库存为空`);
            }
        } else {
            console.log(`⚠️ 接口报错：${res.msg}`);
        }
    } catch (err) {
        console.log(`❌ 网络请求失败：${err.message}`);
    }
}

// ========== 3. 运行入口 ==========
(async () => {
    console.log("🚀 天机馆监控助手启动成功");
    console.log(`当前监控模式：${KEYWORDS.length === 0 ? "全部监控" : "关键词：" + KEYWORDS.join(",")}`);

    // 执行一次监控
    await checkMonitor();

    /**
     * 注意：
     * 如果你在青龙设置了定时任务（如每分钟一次），请直接删除下面的 setInterval 部分。
     * 如果你是想手动运行一次后一直挂着，请保留下方代码。
     */
    // setInterval(async () => {
    //     await checkMonitor();
    // }, 60000); // 每 60 秒检查一次
})();