/**
 * 变量名：所有以 ksck 开头的变量（如 ksck, ksck1, ksck2...）
 * 定时任务：0 9 * * *
 */

const axios = require('axios');

// 1. 获取所有以 ksck 开头的环境变量并合并
let ksck_env = '';
for (const key in process.env) {
    if (key.startsWith('ksck')) {
        ksck_env += process.env[key] + '@'; // 用@分隔不同变量里的内容
    }
}

// 兼容换行、&符号 或 @ 符号分隔的多账号
const cookies = ksck_env.split(/[ \n&@]+/).filter(ck => ck && ck.includes('kpn'));

async function query(cookie, index) {
    console.log(`\n==== [账号 ${index + 1}] 查询开始 ====`);
    try {
        const res = await axios.post('http://111.170.14.11:3000/api/check-coin', 
            { cookie: cookie.trim() },
            { 
                headers: { 'Content-Type': 'application/json' },
                timeout: 15000 
            }
        );

        const data = res.data;
        if (data) {
            const getValue = (obj, keys) => {
                for (let k of keys) {
                    if (obj[k] !== undefined && obj[k] !== null) return obj[k];
                }
                if (obj.data && typeof obj.data === 'object') return getValue(obj.data, keys);
                return null;
            };

            const coin = getValue(data, ['totalCoin', 'total_coin', 'coin']) || "0";
            const money = getValue(data, ['allCash', 'balance', 'money']) || "0.00";
            const name = getValue(data, ['nickname', 'user_name', 'name']) || `快手用户_${index + 1}`;

            console.log(`👤 账号昵称: ${name}`);
            console.log(`💰 当前金币: ${coin}`);
            console.log(`💵 现金余额: ¥${money}`);
            console.log(`✨ 状态反馈: ${data.message || '查询成功'}`);
        }
    } catch (e) {
        console.log(`❌ 请求出错: ${e.message}`);
    }
}

async function main() {
    if (cookies.length === 0) {
        console.log("❌ 未检测到有效的 ksck 变量，请检查环境变量设置！");
        return;
    }

    console.log(`🚀 检测到 ${cookies.length} 个账号，准备开始批量查询...`);

    for (let i = 0; i < cookies.length; i++) {
        await query(cookies[i], i);
        if (cookies.length > 1) {
            await new Promise(r => setTimeout(r, 3000));
        }
    }
    console.log('\n✅ 所有查询任务已完成！');
}

main();