/**
 * 变量名：USERNAME  PASSWORD
 * 注意 天翼需要二次验证码验证  
 * 解决办法是关闭设备锁，
 * 但是天翼云盘APP的安全中心的设备锁，只能打开，不能关闭，
 * 哪怕你使劲按终于给关闭了，返回再进来也是打开状态，
 * 正确的关闭方式去e.189.cn操作关闭（当然，你得收验证码才可以关闭）。
 * 值：手机号#密码，多账号，直接换行或者重新弄一个变量，格式一样。 
 *  需要安装的依赖 cloud189-sdk
 * 定时规则
 * 每天早上8点，跟晚上8点签到。
 * cron: 0 0 8,20 * * *
 */
// 直接定义用户名和密码，避免特殊字符处理问题
const USERNAME = "xxx";
const PASSWORD = "xxx&";
// 使用修补后的SDK以支持deviceId参数
const { CloudClient } = require("./patch-sdk.js");

// 生成设备ID（模拟Web端登录）
function generateDeviceId() {
  // 生成更真实的设备ID格式
  const chars = '0123456789ABCDEF';
  let deviceId = '';
  for (let i = 0; i < 32; i++) {
    deviceId += chars[Math.floor(Math.random() * 16)];
  }
  return deviceId;
}
const DEVICE_ID = generateDeviceId();
const fs = require('fs'); // 引入文件系统模块，用于写入日志
console.log('当前使用的 cloud189-sdk 版本:', require('cloud189-sdk/package.json').version);
console.log('用户名和密码是否正确传递:', !!USERNAME, !!PASSWORD);

const mask = (s, start, end) => s.split("").fill("*", start, end).join("");

const buildTaskResult = (res, result) => {
  const index = result.length;
  if (res.errorCode === "User_Not_Chance") {
    result.push(`第${index}次抽奖失败,次数不足`);
  } else {
    result.push(`第${index}次抽奖成功,抽奖获得${res.prizeName}`);
  }
};

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const message = [];
// 任务 1.签到
const doTask = async (cloudClient) => {
  const result = [];
  const res1 = await cloudClient.userSign();
  result.push(
    `${res1.isSign? "已经签到过了，" : ""}签到获得${res1.netdiskBonus}M空间`
  );
  return result;
};

const doFamilyTask = async (cloudClient) => {
  const { familyInfoResp } = await cloudClient.getFamilyList();
  const result = [];
  if (familyInfoResp) {
    for (let index = 0; index < familyInfoResp.length; index += 1) {
      const { familyId } = familyInfoResp[index];
      const res = await cloudClient.familyUserSign(familyId);
      result.push(
        "家庭任务" +
          `${res.signStatus? "已经签到过了，" : ""}签到获得${
            res.bonusSpace
          }M空间`
      );
    }
  }
  return result;
};

// 开始执行程序
async function main(userName, password) {
  console.log('进入main函数，用户名:', userName, '密码长度:', password ? password.length : 0);
  if (userName && password) {
    const userNameInfo = mask(userName, 3, 7);
    try {
      message.push(`账户 ${userNameInfo}开始执行`);
      console.log(`账户 ${userNameInfo}开始执行`);
      // 创建CloudClient实例并检查可用方法
      console.log('正在创建CloudClient实例...');
      // 根据SDK要求，使用对象参数传递认证信息，并添加设备ID
      const cloudClient = new CloudClient({
        username: userName,
        password: password,
        deviceId: DEVICE_ID
      });
      console.log('CloudClient实例创建成功，检查实例方法:', Object.keys(cloudClient));
      
      // 尝试登录
      console.log('尝试登录...');
      try {
        await cloudClient.login();
        console.log('登录成功');
      } catch (loginError) {
        console.log('登录失败或不需要登录:', loginError.message);
      }
      
      const result = await doTask(cloudClient);
      result.forEach((r) => console.log(r));
      
      try {
        const familyResult = await doFamilyTask(cloudClient);
        familyResult.forEach((r) => console.log(r));
      } catch (familyError) {
        console.log('家庭任务执行失败:', familyError.message);
      }

      console.log("任务执行完毕");
      try {
        const { cloudCapacityInfo, familyCapacityInfo } =
          await cloudClient.getUserSizeInfo();
        let txt =
          `个人：${(
            cloudCapacityInfo.totalSize /
            1024 /
            1024 /
            1024
          ).toFixed(2)}G,家庭：${(
            familyCapacityInfo.totalSize /
            1024 /
            1024 /
            1024
          ).toFixed(2)}G`;

        message.push(txt);
        console.log(txt);
      } catch (infoError) {
        console.log('获取用户信息失败:', infoError.message);
      }
    } catch (e) {
      console.error(e);
      if (e.code === "ECONNRESET") {
        throw e;
      }
    } finally {
      message.push(`账户 ${userNameInfo}执行完毕`);
    }
  }
}

(async () => {
  try {
    // 直接使用定义好的用户名和密码
    await main(USERNAME, PASSWORD);
  } finally {
    console.log(message.join('\n'));
    // 将消息内容写入日志文件
    const logContent = message.join('\n');
    fs.writeFileSync('天翼云盘签到日志.txt', logContent);
  }
})();
