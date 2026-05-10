---
skill: miniprogram-developer
version: 1.1.0
updated: 2026-05-10
depends: [reference-e2e-testing, reference-devtools-usage]
provides: [真机测试, 远程调试, Midscene, 云测, ADB, HDC]
difficulty: advanced
official: https://developers.weixin.qq.com/miniprogram/dev/devtools/debug.html
---

# 微信小程序真机测试

## 概述

真机测试验证模拟器无法覆盖的场景：设备兼容性、真实网络、硬件交互（相机/GPS/传感器）、性能表现。

微信小程序真机测试的路径：

```
开发者工具(Automator) → 远程调试桥 → 真机
     └── 或 ──→ 云测平台(远程真机农场)
     └── 或 ──→ Midscene(视觉驱动, 实验性)
```

> **关键澄清**: `miniprogram-automator` 连接的是**开发者工具的自动化端口**，不直接连接物理设备。真机交互通过开发者工具的"远程调试"功能中转。

---

## 1. 真机远程调试

### 1.1 前置准备

- 手机开启"开发者选项"和"USB 调试"
- 微信开发者工具已打开项目
- 手机通过 USB 连接电脑

### 1.2 通过开发者工具启动

1. 微信开发者工具 → 工具栏 → "真机调试"
2. 选择"USB 连接"或"局域网连接"
3. 手机微信扫码确认
4. 调试面板自动打开

### 1.3 通过 Automator 间接控制真机

Automator 连接开发者工具自动化端口，在工具中启用"真机调试"后，Automator 的页面操作会通过工具中转到达真机：

```javascript
const automator = require('miniprogram-automator');

async function realDeviceViaAutomator() {
  // 前提: 开发者工具中已开启真机调试
  // Automator 连接的是开发者工具，不是设备
  const miniProgram = await automator.connect({
    wsEndpoint: 'ws://127.0.0.1:9420'
  });

  // 页面操作（通过开发者工具中转到达真机）
  const page = await miniProgram.currentPage();
  await page.waitFor('.button');
  await page.tap('.button');

  // 调用小程序 API
  const result = await miniProgram.callWxMethod('getSystemInfo');
  console.log('系统信息:', result);

  await miniProgram.close();
}
```

### 1.4 ADB 辅助命令

```bash
# 查看已连接设备
adb devices

# 查看设备 IP (Android 7+)
adb -s DEVICE_ID shell ip addr show wlan0

# WiFi 连接
adb tcpip 5555
adb connect DEVICE_IP:5555

# 获取设备信息
adb -s DEVICE_ID shell getprop ro.build.version.release
```

### 1.5 HDC (HarmonyOS 设备)

```bash
# 查看设备列表
hdc list targets

# 截图
hdc shell "screenshot -p /sdcard/screen.png"
hdc file recv /sdcard/screen.png ./screen.png
```

---

## 2. Midscene AI 视觉驱动测试 (实验性)

> **注意**: Midscene 对微信小程序的支持处于实验阶段。`@midscene/miniprogram` 包的可用性请以 [Midscene 官方文档](https://midscenejs.com/) 为准。

Midscene 通过视觉 AI 识别屏幕内容，用自然语言描述操作步骤。适用于无法通过 DOM/Automator 定位元素的场景。

### 2.1 安装

```bash
npm install @midscene/web --save-dev
# 注意: @midscene/miniprogram 如不可用，可尝试 @midscene/web 通过截图模式工作
```

### 2.2 环境配置

创建 `.env` 文件：

```bash
MIDSCENE_MODEL_API_KEY="your-api-key"
MIDSCENE_MODEL_NAME="qwen-vl-max"     # 或其他视觉模型
MIDSCENE_MODEL_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
MIDSCENE_MODEL_FAMILY="qwen"
```

### 2.3 基本操作流程

```bash
# 截图分析 → AI 识别 → 执行操作 → 截图确认
```

完整工作流示例（通过 Midscene Web SDK 驱动小程序模拟器截图）：

```javascript
const { agentFromWebPage } = require('@midscene/web');

async function midsceneTest() {
  // 前提: 开发者工具已打开，小程序页面在模拟器中可见
  // Midscene 通过分析开发者工具的模拟器截图来工作

  // 具体 API 和集成方式以 Midscene 官方文档为准
  // 参考: https://midscenejs.com/
}
```

---

## 3. 云测平台

微信官方提供的小程序云测平台，在云端真机农场运行测试。

### 3.1 平台功能

| 功能 | 说明 |
|------|------|
| 远程真机测试 | 在真实设备上手动/自动执行测试 |
| AI Monkey 测试 | AI 驱动的智能随机测试（云端执行） |
| 录制回放 | 录制操作并回放验证 |
| 性能分析 | FPS、内存、CPU、启动耗时 |
| 兼容性测试 | 多机型、多系统版本并行测试 |

### 3.2 访问方式

1. 微信公众平台 → 开发 → 开发工具 → 云测
2. 或直接访问: https://mp.weixin.qq.com/wxamp/cloudtest/

### 3.3 在 CI/CD 中触发云测

```yaml
# 云测通过微信开放平台 API 触发，不是通过 Automator
# 参考: https://developers.weixin.qq.com/miniprogram/dev/devtools/cloudtest/
- name: Trigger cloud test
  run: |
    curl -X POST https://api.weixin.qq.com/wxa/cloudtest/commitsubmit?access_token=$TOKEN \
      -H "Content-Type: application/json" \
      -d '{"miniprogram_appid": "$APP_ID", "test_type": "monkey"}'
```

---

## 4. Automator 正确 API 参考

> Automator 连接的是**开发者工具**，不是真机。以下为实际存在的 API。

### 4.1 安装和启动

```bash
npm install miniprogram-automator
```

```javascript
const automator = require('miniprogram-automator');

// 方式1: 启动开发者工具并打开项目
const miniProgram = await automator.launch({
  projectPath: '/path/to/project'
});

// 方式2: 连接已打开的开发者工具（需先在工具中开启自动化端口）
const miniProgram = await automator.connect({
  wsEndpoint: 'ws://127.0.0.1:9420'
});
```

### 4.2 页面操作

```javascript
const page = await miniProgram.currentPage();

// 导航
await miniProgram.navigateTo('/pages/detail/detail');
await miniProgram.reLaunch('/pages/index/index');

// 等待元素
await page.waitFor('.button');

// 点击
await page.tap('.button');

// 输入
await page.input('.input-field', 'hello');

// 获取元素
const element = await page.$('.title');
const text = await element.text();

// 调用小程序方法
await page.callMethod('scrollTo', 0, 100);

// 获取页面数据 (方法调用, 不是属性)
const data = await page.data();

// 调用 wx API
const sysInfo = await miniProgram.callWxMethod('getSystemInfo');
```

### 4.3 实际页面数据访问

```javascript
// ✅ 正确: data() 是异步方法
const pageData = await page.data();
console.log('页面数据:', pageData);

// ❌ 错误: data 不是属性
// const pageData = page.data;
```

### 4.4 等待与选择器

```javascript
// 等待元素出现
await page.waitFor('.list-item');

// 等待指定时间
await page.waitFor(2000);

// 选择器
const item = await page.$('.list-item:nth-child(1)');
const items = await page.$$('.list-item');
```

---

## 5. 弱网络测试

### 5.1 开发者工具模拟

在微信开发者工具中：
1. 调试器 → Network 面板
2. 选择网络类型: 2G / 3G / 4G / WiFi / 离线

### 5.2 真机弱网络

真机上通过系统设置或代理工具模拟:

```bash
# Android: 通过 ADB 设置网络类型
adb shell cmd connectivity airplane-mode    # 飞行模式
adb shell svc wifi enable                   # 开启 WiFi
adb shell cmd connectivity set-mobile-data-enabled false  # 关闭移动数据

# iOS: 在设置 → 开发者 → Network Link Conditioner 中配置
```

### 5.3 常见网络场景配置参考

| 场景 | 下行带宽 | 上行带宽 | 延迟 |
|------|----------|----------|------|
| 2G | 15KB/s | 5KB/s | 500ms |
| 3G | 50KB/s | 20KB/s | 200ms |
| 4G | 500KB/s | 100KB/s | 50ms |
| 弱WiFi | 100KB/s | 50KB/s | 100ms |

### 5.4 弱网络测试检查点

```javascript
async function weakNetworkCheckpoints(page) {
  // 1. loading 状态是否显示
  const hasLoading = await page.waitFor('.loading', { timeout: 1500 })
    .then(() => true).catch(() => false);
  console.log('Loading状态:', hasLoading ? '正常' : '缺失');

  // 2. 超时提示
  const hasTimeoutTip = await page.waitFor('.timeout-tip', { timeout: 12000 })
    .then(() => true).catch(() => false);
  console.log('超时提示:', hasTimeoutTip ? '正常' : '缺失');

  // 3. 重试机制
  const retryButton = await page.$('.retry-button');
  console.log('重试按钮:', retryButton ? '存在' : '缺失');

  // 4. 离线缓存
  const cachedData = await page.callMethod('getStorageSync', 'cache');
  console.log('缓存数据:', cachedData ? '有' : '无');
}
```

---

## 最佳实践

1. 真机测试优先通过开发者工具的"远程调试"功能进行
2. Automator 连接开发者工具（非直接连接设备）来驱动模拟器/真机操作
3. 云测平台用于多机型兼容性覆盖，通过 API 触发
4. Midscene 视觉驱动适合 UI 验收测试（标注实验性）
5. 每次关键操作后截图保存，便于问题定位
6. 测试结束后断开连接

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| 设备未找到 (ADB) | 检查 USB 连接，确认已开启 USB 调试 |
| Automator 连接失败 | 确认开发者工具已开启"工具 → 设置 → 安全 → 服务端口" |
| 真机调试无法连接 | 手机与电脑在同一网络，关闭防火墙重试 |
| 操作超时 | 增加 waitFor 超时参数 |
| 元素定位失败 | 使用 `data-testid` 属性替代 CSS class |

---

## 相关文档

- [真机调试官方文档](https://developers.weixin.qq.com/miniprogram/dev/devtools/debug.html#真机调试)
- [云测平台](https://developers.weixin.qq.com/miniprogram/dev/devtools/cloudtest/)
- [miniprogram-automator](https://www.npmjs.com/package/miniprogram-automator)
- [Midscene 官网](https://midscenejs.com/)
