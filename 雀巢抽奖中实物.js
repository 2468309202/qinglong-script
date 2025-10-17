// 当前脚本来自于http://script.345yun.cn脚本库下载！
/**
 * 大大鸣版
 * #小程序
 * 抓包 Host：crm.nestlechinese.com
 * 
 * 环境变量配置：
 * export NESTLE_TOKEN='haxxxxXXXXxxxxxXXX'  # 必填，多账号用 & 或换行
 * 
 */
const axios = require('axios');


const $ = {
  name: '雀巢会员',
  wait: (ms) => new Promise(resolve => setTimeout(resolve, ms)),
  logErr: (e) => console.error(e),
  done: () => console.log('任务完成')
};


const nestleList = process.env.NESTLE_TOKEN ? process.env.NESTLE_TOKEN.split(/[\n&]/) : [];
let message = '';

const baseUrl = 'https://crm.nestlechinese.com'


const activityConfig = {
  show_channel: process.env.NESTLE_ACTIVITY_CHANNEL || 'NNXKC75FWQX5', // 活动频道标识，留空则不执行活动任务
  task_type: 1,
  gift_count: 0
};


async function printBanner() {
  try {
    const bannerUrl = 'http://1324539008-h6588dczqs.ap-shanghai.tencentscf.com/print';
    const response = await axios.get(bannerUrl);
    console.log(response.data);
  } catch (e) {
    console.log(e);
  }
}

// 生成随机UA
function getRandomUserAgent() {
  const userAgents = [
    'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'
  ];
  return userAgents[Math.floor(Math.random() * userAgents.length)];
}


function getRandomWait(min, max) {
  return Math.floor(Math.random() * (max - min + 1) + min);
}

async function sendRequest(url, method, headers, data = null) {
  try {
    const options = {
      url,
      method,
      headers,
      timeout: 10000,
      validateStatus: () => true 
    };
    
    if (data && (method.toLowerCase() === 'post' || method.toLowerCase() === 'put')) {
      options.data = data;
    }
    
    const response = await axios(options);
    return response.data;
  } catch (e) {
    console.error(`请求失败: ${e.message}`);
    return { errcode: 500, errmsg: '请求失败: ' + e.message };
  }
}

const headers = {
  'User-Agent': getRandomUserAgent(),
  'content-type': 'application/json',
  'referer': 'https://servicewechat.com/wxc5db704249c9bb31/353/page-frame.html',
};


(async () => {

  await printBanner();
  
  console.log(`\n已随机分配 User-Agent\n${headers['User-Agent']}`);
  
  // 显示配置信息
  if (activityConfig.show_channel) {
    console.log(`\n🎯 活动任务已启用，频道：${activityConfig.show_channel}`);
  } else {
    console.log(`\nℹ️  活动任务未启用（可通过 NESTLE_ACTIVITY_CHANNEL 环境变量配置）`);
  }
  
  for (let i = 0; i < nestleList.length; i++) {
    const index = i + 1;
    console.log(`\n${'='.repeat(60)}`);
    console.log(`*****第[${index}]个${$.name}账号*****`);
    console.log('='.repeat(60));
    headers.authorization = `Bearer ${nestleList[i]}`;
    message += `📣====${$.name}账号[${index}]====📣\n`;
    await main();
    await $.wait(getRandomWait(2000, 2500));
  }
  
  // 打印结果消息
  if (message) {
    console.log(`\n${'='.repeat(60)}`);
    console.log('执行结果汇总：');
    console.log('='.repeat(60));
    console.log(message);
  }
})().catch((e) => $.logErr(e)).finally(() => $.done());

async function main() {
  await getUserInfo();
  await $.wait(getRandomWait(1000, 2000));
  
  // 执行签到
  await doSign();
  await $.wait(getRandomWait(1000, 2000));
  
  // 执行通用任务
  // await getTaskList();
  // await $.wait(getRandomWait(1000, 2000));
  
  // 执行活动任务（如果配置了活动频道）
  if (activityConfig.show_channel) {
    await getActivityTaskList();
    await $.wait(getRandomWait(1000, 2000));
    
    // 执行抽奖
    await doLuckyDraw();
    await $.wait(getRandomWait(1000, 2000));
  }
  
  await getUserBalance();
}

/**
 * 获取用户信息
 */
async function getUserInfo() {
  try {
    const data = await sendRequest(`${baseUrl}/openapi/member/api/User/GetUserInfo`, 'get', headers);
    if (200 !== data.errcode) {
      return console.error(`❌ 获取用户信息失败：${data.errmsg}`);
    }
    const {nickname, mobile} = data.data;
    console.log(`\n👤 用户信息：${nickname} (${mobile})`);
    message += `用户：${nickname}(${mobile})\n`;
  } catch (e) {
    console.error(`❌ 获取用户信息时发生异常 -> ${e}`);
  }
}

/**
 * 每日签到
 */
async function doSign() {
  try {
    console.log(`\n${'='.repeat(50)}`);
    console.log('📅 执行每日签到');
    console.log('='.repeat(50));
    
    const signData = {
      rule_id: 1,
      goods_rule_id: 1
    };
    
    const data = await sendRequest(`${baseUrl}/openapi/activityservice/api/sign2025/sign`, 'post', headers, signData);
    
    if (200 === data.errcode) {
      const { sign_day, sign_points, goods_name } = data.data;
      console.log(`\n✅ 签到成功！`);
      console.log(`   📆 连续签到：${sign_day} 天`);
      console.log(`   💰 获得巢币：${sign_points} 个`);
      
      if (goods_name) {
        console.log(`   🎁 额外奖励：${goods_name}`);
      }
      
      message += `签到：第${sign_day}天，获得${sign_points}巢币\n`;
    } else {
      const errorMsg = data.errmsg || '未知错误';
      
      // 判断是否已签到
      if (errorMsg.includes('已签到') || errorMsg.includes('已经签到') || errorMsg.includes('重复签到')) {
        console.log(`\nℹ️  今日已签到`);
        message += `签到：今日已签到\n`;
      } else {
        console.log(`\n⚠️  签到失败：${errorMsg}`);
        message += `签到：失败(${errorMsg})\n`;
      }
    }
    
    console.log('='.repeat(50));
  } catch (e) {
    console.error(`❌ 签到时发生异常 -> ${e}`);
    message += `签到：异常\n`;
  }
}

async function getTaskList() {
  try {
    const data = await sendRequest(`${baseUrl}/openapi/activityservice/api/task/getlist`, 'post', headers);
    if (200 !== data.errcode) {
      return console.error(`❌ 获取任务列表失败：${data.errmsg}`);
    }
    
    console.log(`\n📝 通用任务：获取到 ${data.data.length} 个任务`);
    let successCount = 0;
    let failCount = 0;
    
    for (const task of data.data) {
      console.log(`\n[${successCount + failCount + 1}/${data.data.length}] 开始【${task.task_title}】任务`);
      const result = await doTask(task.task_guid);
      if (result) successCount++;
      else failCount++;
      await $.wait(getRandomWait(2000, 2500));
    }
    
    console.log(`\n${'='.repeat(50)}`);
    console.log(`📊 通用任务执行完成：✅ 成功 ${successCount} 个${failCount > 0 ? ` | ⚠️ 失败 ${failCount} 个` : ''}`);
    console.log('='.repeat(50));
    message += `通用任务：${successCount}/${data.data.length}\n`;
  } catch (e) {
    console.error(`❌ 获取任务列表时发生异常 -> ${e}`);
  }
}

async function getActivityTaskList() {
  try {
    const data = await sendRequest(`${baseUrl}/openapi/activityservice/api/task/getlistbyshowchanneltype`, 'post', headers, activityConfig);
    if (200 !== data.errcode) {
      return console.error(`❌ 获取活动任务列表失败：${data.errmsg}`);
    }
    
    // 过滤未完成的任务
    const unfinishedTasks = data.data.filter(task => task.task_status === 0);
    const finishedCount = data.data.length - unfinishedTasks.length;
    
    console.log(`\n🎯 活动任务：共 ${data.data.length} 个任务，已完成 ${finishedCount} 个，待完成 ${unfinishedTasks.length} 个`);
    
    if (unfinishedTasks.length === 0) {
      console.log('✅ 所有活动任务已完成！');
      message += `活动任务：已全部完成\n`;
      return;
    }
    
    let successCount = 0;
    let failCount = 0;
    
    for (const task of unfinishedTasks) {
      console.log(`\n[${successCount + failCount + 1}/${unfinishedTasks.length}] 开始【${task.task_title}】任务`);
      const result = await doTask(task.task_guid);
      if (result) successCount++;
      else failCount++;
      await $.wait(getRandomWait(2000, 2500));
    }
    
    console.log(`\n${'='.repeat(50)}`);
    console.log(`📊 活动任务执行完成：✅ 成功 ${successCount} 个${failCount > 0 ? ` | ⚠️ 失败 ${failCount} 个` : ''}`);
    console.log('='.repeat(50));
    message += `活动任务：${successCount}/${unfinishedTasks.length}\n`;
  } catch (e) {
    console.error(`❌ 获取活动任务列表时发生异常 -> ${e}`);
  }
}

async function doTask(task_guid, progress_rule_id = 1) {
  try {
    const data = await sendRequest(`${baseUrl}/openapi/activityservice/api/task/add`, 'post', headers, {
      "task_guid": task_guid,
      "progress_rule_id": progress_rule_id
    });
    
    if (200 === data.errcode) {
      console.log(`   ✅ 任务完成：${data.errmsg}`);
      return true;
    } else {
      console.log(`   ⚠️  任务失败：${data.errmsg}`);
      return false;
    }
  } catch (e) {
    console.error(`   ❌ 任务异常：${e}`);
    return false;
  }
}

async function doLuckyDraw() {
  try {
    if (!activityConfig.show_channel) {
      console.log('⚠️  未配置活动频道，跳过抽奖');
      return;
    }
    
    console.log(`\n${'='.repeat(50)}`);
    console.log('🎰 开始活动抽奖');
    console.log('='.repeat(50));
    
    let drawCount = 0;
    let totalCoins = 0;
    const prizes = [];
    
    // 最多尝试抽奖20次（通常完成9个任务可得3次抽奖机会）
    for (let i = 0; i < 20; i++) {
      const result = await drawOnce();
      
      if (!result.success) {
        if (result.noChance) {
          console.log('\nℹ️  抽奖次数已用完');
          break;
        } else {
          console.log(`\n⚠️  第${i + 1}次抽奖失败: ${result.msg}`);
          break;
        }
      }
      
      drawCount++;
      const prize = result.prize;
      prizes.push(prize);
      
      console.log(`\n🎁 第${drawCount}次抽奖: ${prize.title}${prize.value ? ` (${prize.value}${prize.goods_type === 'points' ? '巢币' : ''})` : ''}`);
      
      if (prize.goods_type === 'points') {
        totalCoins += parseInt(prize.value) || 0;
      }
      
      // 抽奖间隔
      await $.wait(getRandomWait(2000, 3000));
    }
    
    console.log(`\n${'='.repeat(50)}`);
    if (drawCount > 0) {
      console.log(`🎉 抽奖完成：共抽奖 ${drawCount} 次`);
      if (totalCoins > 0) {
        console.log(`💰 获得巢币：${totalCoins} 个`);
      }
      // 显示所有奖品
      console.log(`🎁 奖品列表：`);
      prizes.forEach((p, idx) => {
        console.log(`   ${idx + 1}. ${p.title}${p.value ? ` (${p.value})` : ''}`);
      });
      message += `抽奖：${drawCount}次，获得${totalCoins}巢币\n`;
    } else {
      console.log('ℹ️  暂无抽奖次数');
      message += `抽奖：暂无次数\n`;
    }
    console.log('='.repeat(50));
    
  } catch (e) {
    console.error(`❌ 抽奖时发生异常 -> ${e}`);
  }
}

async function drawOnce() {
  try {
    const url = `${baseUrl}/openapi/activityservice/api/LuckyDraw/LuckyDrawByPoints/${activityConfig.show_channel}`;
    const data = await sendRequest(url, 'get', headers);
    
    if (200 === data.errcode) {
      return {
        success: true,
        prize: {
          title: data.data.title || '未知奖品',
          goods_type: data.data.goods_type,
          value: data.data.value,
          icon: data.data.icon
        }
      };
    } else {
      // 判断是否是次数不足
      const noChanceKeywords = ['次数', '不足', '用完', '已用完'];
      const isNoChance = noChanceKeywords.some(kw => (data.errmsg || '').includes(kw));
      
      return {
        success: false,
        noChance: isNoChance,
        msg: data.errmsg || '未知错误'
      };
    }
  } catch (e) {
    return {
      success: false,
      noChance: false,
      msg: `请求异常: ${e.message}`
    };
  }
}

async function getUserBalance() {
  try {
    const data = await sendRequest(`${baseUrl}/openapi/pointsservice/api/Points/getuserbalance`, 'post', headers);
    if (200 !== data.errcode) {
      return console.error(`❌ 获取用户积分余额失败：${data.errmsg}`);
    }
    console.log(`\n💰 当前巢币：${data.data}`);
    message += `当前巢币：${data.data}\n\n`;
  } catch (e) {
    console.error(`❌ 获取用户巢币时发生异常 -> ${e}`);
  }
}

// 当前脚本来自于http://script.345yun.cn脚本库下载！