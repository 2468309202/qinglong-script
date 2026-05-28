const { exec } = require('child_process');
const fs = require('fs');

const PYTHON_SCRIPT = "fhb大飞修改版.py"; //这里注意看下 要和脚本名字对应
const PYTHON_EXECUTABLE = "python3";
const LOCK_FILE = "auto_watch_scheduler.lock";

const TIME_PERIOD_POOL = [ [8, 11], [10, 13], [14, 17], [16, 19], [19, 22] ];
const DAILY_PERIODS_MIN = 2;
const DAILY_PERIODS_MAX = 3;
const SKIP_DAY_PROBABILITY = 5;  

let todayPeriods = [];
let todayRunDates = [];
let runningProcess = null;

function log(message, type = "info") {
    const time = new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' });
    const prefix = { info: "✅", warn: "⚠️", error: "❌", debug: "🔍" }[type] || "ℹ️";
    console.log(`[${time}] ${prefix} ${message}`);
}

function createLockFile() {
    try {
        fs.writeFileSync(LOCK_FILE, process.pid.toString(), 'utf8');
        return true;
    } catch (e) {
        return false;
    }
}

function checkLockFile() {
    try {
        if (!fs.existsSync(LOCK_FILE)) return false;
        const pid = parseInt(fs.readFileSync(LOCK_FILE, 'utf8'));
        try {
            process.kill(pid, 0); 
            log(`⚠️ 检测到已有调度器进程在运行 (PID: ${pid})，本次启动取消`, "warn");
            return true;
        } catch (e) {
            fs.unlinkSync(LOCK_FILE);
            return false;
        }
    } catch (e) {
        return true; 
    }
}

function removeLockFile() {
    if (fs.existsSync(LOCK_FILE)) fs.unlinkSync(LOCK_FILE);
}

function generateTodayPeriods() {
    if (Math.random() < SKIP_DAY_PROBABILITY / 100) {
        log("🎲 今天随机休息，不运行脚本", "warn");
        return [];
    }
    const shuffled = [...TIME_PERIOD_POOL].sort(() => Math.random() - 0.5);
    const count = Math.floor(Math.random() * (DAILY_PERIODS_MAX - DAILY_PERIODS_MIN + 1)) + DAILY_PERIODS_MIN;
    const selected = shuffled.slice(0, count).sort((a, b) => a[0] - b[0]);
    log(`📅 今日随机选择的运行时间段: ${selected.map(p => `${p[0]}:00-${p[1]}:00`).join('、')}`);
    return selected;
}

function getRandomTimeInPeriod(startHour, endHour) {
    const runTime = new Date();
    const hour = Math.floor(Math.random() * (endHour - startHour + 1)) + startHour;
    runTime.setHours(hour, Math.floor(Math.random() * 60), 0, 0);
    if (runTime < new Date()) runTime.setDate(runTime.getDate() + 1);
    return runTime;
}

function hasRunToday(period) {
    const today = new Date().toDateString();
    return todayRunDates.some(item => item.date === today && item.period[0] === period[0] && item.period[1] === period[1]);
}

function recordRun(period) {
    const today = new Date().toDateString();
    todayRunDates.push({ date: today, period: period, runTime: new Date() });
    todayRunDates = todayRunDates.filter(item => item.date === today);
}

function runPythonScript(period) {
    return new Promise((resolve) => {
        log(`开始运行任务脚本，时间段：${period[0]}:00-${period[1]}:00`);
        runningProcess = exec(`${PYTHON_EXECUTABLE} "${PYTHON_SCRIPT}"`);
        runningProcess.stdout.on('data', (data) => process.stdout.write(data.toString()));
        runningProcess.stderr.on('data', (data) => process.stderr.write(`Error: ${data.toString()}`));
        runningProcess.on('close', (code) => {
            runningProcess = null;
            log(`脚本运行完成，退出码：${code}`);
            recordRun(period);
            resolve();
        });
    });
}

function calculateNextCheckTime() {
    const now = new Date();
    if (now.getHours() === 0 || todayPeriods.length === 0) {
        todayPeriods = generateTodayPeriods();
        todayRunDates = [];
    }
    
    let nextTime = null;
    for (const period of todayPeriods) {
        if (hasRunToday(period)) continue;
        const runTime = getRandomTimeInPeriod(period[0], period[1]);
        if (!nextTime || runTime < nextTime) nextTime = runTime;
    }
    
    if (!nextTime) {
        const tomorrow = new Date(now);
        tomorrow.setDate(tomorrow.getDate() + 1);
        tomorrow.setHours(0, 5, 0, 0); 
        nextTime = tomorrow;
    }
    return nextTime;
}

async function schedulerLoop() {
    while (true) {
        try {
            const nextCheckTime = calculateNextCheckTime();
            const delay = nextCheckTime.getTime() - Date.now();
            log(`下一次运行时间：${nextCheckTime.toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' })}`);
            
            await new Promise(resolve => setTimeout(resolve, delay));
            
            const now = new Date();
            let currentPeriod = null;
            for (const period of todayPeriods) {
                if (now.getHours() >= period[0] && now.getHours() <= period[1]) {
                    currentPeriod = period;
                    break;
                }
            }
            if (currentPeriod && !hasRunToday(currentPeriod)) {
                await runPythonScript(currentPeriod);
            }
            await new Promise(resolve => setTimeout(resolve, 60000));
            
        } catch (err) {
            log("5分钟后重试...", "warn");
            await new Promise(resolve => setTimeout(resolve, 300000));
        }
    }
}

function main() {
    if (checkLockFile() || !createLockFile()) process.exit(1);

    ['SIGTERM', 'SIGINT'].forEach(signal => {
        process.on(signal, () => {
            if (runningProcess) runningProcess.kill('SIGTERM');
            removeLockFile();
            process.exit(0);
        });
    });

    process.on('uncaughtException', () => {
        removeLockFile();
        process.exit(1);
    });

    schedulerLoop();
}

main();