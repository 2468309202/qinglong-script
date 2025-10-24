// 当前脚本来自于http://script.345yun.cn脚本库下载！
const got = require('got');
const { CookieJar } = require('tough-cookie');
//百度环境变量BDUSS，支持逗号(英文状态下)、换行、分号分隔
// ======================
// WxPusher 微信通知配置
// ======================

const WXPUSHER_APP_TOKEN = process.env.WXPUSHER_APP_TOKEN; // 必填：你的 WxPusher AppToken
const WXPUSHER_UID = process.env.WX_PUSHER_USER_IDS;         // 可选：指定 UID，不填则发给所有订阅者

// WxPusher 消息发送函数
async function sendWxPusherNotification(title, content) {
  if (!WXPUSHER_APP_TOKEN) {
    console.log('ℹ️ 未配置 WxPusher AppToken，跳过微信通知');
    return;
  }

  const url = 'https://wxpusher.zjiecode.com/api/send/message';

  const payload = {
    appToken: WXPUSHER_APP_TOKEN,
    content: `${title}\n\n${content}`,
    summary: title,
    contentType: 1,
    uids: [WXPUSHER_UID], // 可选：指定 UID
  };

  try {
    const response = await got.post(url, {
      json: payload,
    });

    const result = JSON.parse(response.body);
    if (result.code === 1000) {
      console.log('📨 WxPusher 微信通知发送成功');
    } else {
      console.log('⚠️ WxPusher 微信通知发送失败：', result.msg);
    }
  } catch (error) {
    console.log('⚠️ WxPusher 通知请求异常：', error.message);
  }
}

// ======================
// 错误重试机制封装
// ======================

async function withRetry(fn, maxRetries = 3) {
  let lastError;
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      console.log(`⚠️ 第 ${i + 1} 次尝试失败，重试中... 错误：${error.message}`);
      if (i < maxRetries - 1) {
        await new Promise(res => setTimeout(res, 2000 * (i + 1))); // 延迟递增
      }
    }
  }
  throw lastError;
}

// ======================
// 签到核心逻辑
// ======================

// 获取我的贴吧列表 & tbs
async function getMyBarsAndTbs(headers) {
  const url = 'https://tieba.baidu.com/mo/q/newmoindex';
  try {
    const response = await got(url, { headers, throwHttpErrors: false });
    const data = JSON.parse(response.body);

    if (data.no !== 0) {
      console.log('❌ 获取贴吧列表失败：', data.error);
      return { bars: [], tbs: '0' };
    }

    const tbs = data.data.tbs || '0';
    const bars = data.data.like_forum || [];

    return { bars, tbs };
  } catch (error) {
    console.log('❌ 请求贴吧列表失败：', error.message);
    return { bars: [], tbs: '0' };
  }
}

// 签到单个贴吧（带重试）
async function signSingleBar(headers, bar, tbs) {
  const kw = bar.forum_name;

  const signUrl = 'https://tieba.baidu.com/sign/add';
  const payload = new URLSearchParams({
    ie: 'utf-8',
    kw: kw,
    tbs: tbs,
  });

  const doSign = async () => {
    const response = await got.post(signUrl, {
      headers: {
        ...headers,
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: payload.toString(),
    });

    const result = JSON.parse(response.body);

    if (result.no === 0 || result.no === 1101) {
      console.log(`✅ [${kw}] 签到成功`);
      return { name: kw, status: 'success', msg: result.error || '', tbs };
    } else if (result.no === 1102) {
      console.log(`⚠️ [${kw}] 签到太频繁`);
      return { name: kw, status: 'warning', msg: result.error || '', tbs };
    } else if (result.no === 2150040) {
      console.log(`⚠️ [${kw}] 需要验证码`);
      return { name: kw, status: 'warning', msg: result.error || '', tbs };
    } else {
      const errMsg = result.error || '未知错误';
      throw new Error(`[${kw}] 签到失败：${errMsg}`);
    }
  };

  return await withRetry(doSign);
}

// ======================
// 主函数
// ======================

(async () => {
  console.log('🔔 开始执行百度贴吧多账号增强版签到');

  // 从环境变量获取所有 BDUSS，支持逗号、换行、分号分隔
  const bdussListRaw = process.env.BDUSS || '';
  const bdussList = bdussListRaw
    .split(/[,\n;]/)
    .map(s => s.trim())
    .filter(s => s);

  if (!bdussList || bdussList.length === 0) {
    console.log('❌ 未配置任何 BDUSS，请设置环境变量 BDUSS_LIST（多个用逗号/换行/分号分隔）');
    return;
  }

  console.log(`📌 共检测到 ${bdussList.length} 个 BDUSS，开始逐个处理...\n`);

  let allResults = [];

  for (const bduss of bdussList) {
    if (!bduss) continue;

    console.log(`🔐 正在处理账号（BDUSS截断显示）: ${bduss.substring(0, 10)}...`);

    const headers = {
      Cookie: `BDUSS=${bduss}`,
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0 Safari/537.36',
    };

    const { bars, tbs } = await getMyBarsAndTbs(headers);

    if (!bars || bars.length === 0) {
      console.log('⚠️ 该账号未获取到贴吧列表，可能未登录或 BDUSS 失效');
      continue;
    }

    console.log(`📚 当前账号共有 ${bars.length} 个关注的贴吧，开始签到...\n`);

    let accountResults = [];

    for (const bar of bars) {
      try {
        const result = await signSingleBar(headers, bar, tbs);
        accountResults.push(result);
      } catch (error) {
        console.log(`❌ [${bar.forum_name}] 签到异常：`, error.message);
        accountResults.push({
          name: bar.forum_name,
          status: 'error',
          msg: error.message,
          tbs,
        });
      }
    }

    allResults = allResults.concat(accountResults);

    console.log(`✅ 账号 BDUSS=${bduss.substring(0, 10)}... 的所有贴吧签到处理完成\n`);
  }

  // 汇总通知
  let finalSummary = `✅ 百度贴吧多账号增强版签到执行完毕，共处理 ${bdussList.length} 个账号，${allResults.length} 个贴吧。\n\n`;
  allResults.forEach(r => {
    finalSummary += `📌 [${r.name}] 状态: ${r.status}，信息: ${r.msg}\n`;
  });

  console.log(finalSummary);
  await sendWxPusherNotification('✅ 百度贴吧增强版签到完成', finalSummary);
})();

// 当前脚本来自于http://script.345yun.cn脚本库下载！