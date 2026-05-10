---
skill: miniprogram-developer
version: 1.0.0
updated: 2026-05-10
depends: [reference-debugging, reference-cloud-development]
provides: [错误码, 故障排查, errMsg, 常见错误]
difficulty: beginner
official: https://developers.weixin.qq.com/miniprogram/dev/api基础/报错码.html
---

# 微信小程序错误码对照表

## 微信小程序 API 错误码

### 通用错误码

| 错误码 | errMsg | 原因 | 解决方案 |
|--------|--------|------|----------|
| -1 | System error | 系统异常 | 稍后重试 |
| -2 | invalid data format | 数据格式错误 | 检查参数格式 |
| -3 | invalid url | URL 格式错误 | 检查请求路径 |
| -4 | request cost timeout | 请求超时 | 增加超时时间或重试 |
| -5 | unsupported protocol | 不支持的协议 | 使用 https:// |

### 授权类错误码

> **注意**：以下 40001 等 5 位正数错误码属于**微信开放平台服务端 API**（如 `access_token`、`openid` 相关接口）返回的错误码，由服务端 HTTP 响应返回。而 **小程序客户端 API**（如 `wx.request`、`wx.login`）的错误码为负数（-1~-5），通过 `fail` 回调的 `err.errno` 获取。二者来源与处理方式不同，请勿混淆。

| 错误码 | errMsg | 原因 | 解决方案 |
|--------|--------|------|----------|
| 40001 | invalid credential | access_token 无效 | 重新获取 |
| 40002 | invalid grant_type | grant_type 错误 | 检查授权类型 |
| 40003 | invalid openid | openid 错误 | 确认用户 openid |
| 40013 | invalid appid | appid 错误 | 检查 appid 配置 |
| 40125 | invalid appsecret | appsecret 错误 | 检查 appsecret |
| 41001 | access_token missing | 缺少 access_token | 带上 access_token |
| 41002 | appid missing | 缺少 appid | 检查 appid |
| 41004 | appsecret missing | 缺少 appsecret | 检查 appsecret |
| 42001 | access_token expired | access_token 过期 | 刷新 token |

### 支付类错误码

| 错误码 | errMsg | 原因 | 解决方案 |
|--------|--------|------|----------|
| -100 | payment fail | 支付失败 | 稍后重试 |
| -1000 | system error | 系统错误 | 联系微信支付 |
| -1001 | signature error | 签名错误 | 检查签名算法 |
| -1002 | appid not bound | appid 未绑定 | 配置 appid |
| -1003 | mch_id not bound | 商户号未绑定 | 配置商户号 |
| -1004 | key error | 密钥错误 | 检查密钥配置 |
| -1005 | crypt error | 加解密错误 | 检查加密方式 |

### 模板消息错误码

| 错误码 | errMsg | 原因 | 解决方案 |
|--------|--------|------|----------|
| 40003 | invalid template_id | 模板 ID 错误 | 检查模板 ID |
| 40037 | template_id not exist | 模板不存在 | 重新选择模板 |
| 41028 | form_id不正确 | form_id 错误 | 使用真实的 form_id |
| 41029 | form_id 已使用 | form_id 已用过 | 生成新的 form_id |
| 41030 | form_id 无效 | form_id 过期 | form_id 有效期 7 天 |

## 云开发错误码

### 云数据库错误码

| 错误码 | 说明 | 原因 | 解决方案 |
|--------|------|------|----------|
| -502001 | 数据库操作失败 | 权限不足或语法错误 | 检查权限设置 |
| -502002 | collection 不存在 | 集合未创建 | 创建集合 |
| -502003 | document 不存在 | 记录不存在 | 检查记录 ID |
| -502004 | update failed | 更新失败 | 检查更新条件 |
| -502005 | delete failed | 删除失败 | 检查权限 |
| -502006 | 数据类型不匹配 | 字段类型错误 | 检查数据类型 |

### 云函数错误码

| 错误码 | 说明 | 原因 | 解决方案 |
|--------|------|------|----------|
| -501001 | 云函数不存在 | 函数名错误 | 检查函数名 |
| -501002 | 云函数执行失败 | 函数内部错误 | 查看函数日志 |
| -501003 | 云函数超时 | 执行时间过长 | 优化函数逻辑 |
| -501004 | 云函数内存超限 | 内存使用过大 | 优化内存使用 |
| -501005 | 参数格式错误 | 传入参数格式错误 | 检查 event 参数 |

### 云存储错误码

| 错误码 | 说明 | 原因 | 解决方案 |
|--------|------|------|----------|
| -503001 | 上传文件失败 | 文件过大或格式错误 | 检查文件 |
| -503002 | 删除文件失败 | 文件不存在或无权限 | 检查权限 |
| -503003 | 获取文件失败 | 文件不存在 | 检查文件路径 |
| -503004 | 文件大小超限 | 超出存储限制 | 清理存储空间 |

### wx.cloud.callFunction 错误处理

```javascript
// 小程序端调用云函数
wx.cloud.callFunction({
  name: 'myFunction',
  data: { action: 'query' }
}).then(res => {
  // res.result 是云函数 return 的内容
  if (res.result.code !== 0) {
    wx.showToast({ title: res.result.msg, icon: 'none' });
  }
}).catch(err => {
  // 调用失败：云函数不存在(-501001)、网络异常等
  console.error('云函数调用失败:', err);
  const tips = {
    '-501001': '云函数不存在，请检查函数名',
    '-501002': '云函数执行失败，请查看日志',
    '-501003': '云函数执行超时',
    '-501004': '云函数内存超限',
  };
  const msg = tips[String(err.errCode)] || err.errMsg || '调用失败';
  wx.showToast({ title: msg, icon: 'none' });
});

// 云函数端统一返回格式
exports.main = async (event, context) => {
  try {
    const result = await businessLogic(event);
    return { code: 0, data: result };
  } catch (err) {
    return { code: -1, msg: err.message };
  }
};
```

## 网络请求错误码

### wx.request 错误

| 错误码 | errMsg | 原因 | 解决方案 |
|--------|--------|------|----------|
| -1 | request:fail | 网络请求失败 | 检查网络连接 |
| -2 | request:fail abort | 请求被中断 | 检查请求是否超时 |
| -3 | request:fail timeout | 请求超时 | 增加超时时间 |
| -4 | request:fail ssl | SSL 错误 | 检查证书 |

### 错误处理示例

```javascript
// 统一错误处理
function handleRequestError(err, defaultMsg = '请求失败') {
  // err.errMsg 是字符串（如 "request:fail timeout"），err.errno 是数字（如 -3）
  // 用 err.errno 匹配错误码表，再用 err.errMsg 子串匹配兜底
  const errorMap = {
    '-1': '网络连接失败，请检查网络',
    '-2': '请求被中断，请重试',
    '-3': '请求超时，请重试',
    '-4': '安全证书错误',
  };

  let msg = errorMap[String(err.errno)];
  if (!msg && err.errMsg) {
    if (err.errMsg.includes('timeout')) {
      msg = '请求超时，请重试';
    } else if (err.errMsg.includes('abort')) {
      msg = '请求被中断，请重试';
    } else if (err.errMsg.includes('ssl')) {
      msg = '安全证书错误';
    }
  }
  msg = msg || err.errMsg || defaultMsg;
  wx.showToast({ title: msg, icon: 'none' });
  console.error('Request error:', err);
}

// 使用
wx.request({
  url: API_BASE + '/match/list',
  success(res) {
    if (res.data.code === 0) {
      // 业务成功
    } else {
      // 业务错误
      wx.showToast({ title: res.data.msg, icon: 'none' });
    }
  },
  fail(err) {
    handleRequestError(err);
  }
});
```

## 前端常见错误

### 页面报错

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| "Cannot read property 'xxx' of undefined" | 访问了 undefined 的属性 | 使用可选链 `?.` 或判空 |
| "setData is not a function" | this 指向错误 | 使用 `that = this` 或箭头函数 |
| "Component not found" | 组件未注册 | 检查 components 定义 |
| "template not found" | 模板未引入 | 检查 import |

### 异步回调中的 this

```javascript
// ❌ 错误
Page({
  data: { count: 0 },
  fetchData() {
    wx.request({
      url: 'api',
      success(res) {
        this.setData({ count: res.data.count }); // this 指向 undefined
      }
    });
  }
});

// ✅ 正确
Page({
  data: { count: 0 },
  fetchData() {
    const that = this;
    wx.request({
      url: 'api',
      success(res) {
        that.setData({ count: res.data.count });
      }
    });
  }
});

// ✅ 或者使用箭头函数
Page({
  data: { count: 0 },
  fetchData() {
    wx.request({
      url: 'api',
      success: (res) => {
        this.setData({ count: res.data.count });
      }
    });
  }
});
```

## 自定义错误码规范

### 错误码格式

```
{类型}{模块}{序号}
```

| 类型 | 说明 |
|------|------|
| 1xxx | 参数/输入错误 |
| 2xxx | 业务逻辑错误 |
| 3xxx | 权限错误 |
| 4xxx | 资源错误 |
| 5xxx | 系统错误 |

### 示例

```javascript
// 错误码定义
const ERROR_CODES = {
  // 参数错误 (1xxx)
  PARAM_REQUIRED: 1001,
  PARAM_FORMAT_ERROR: 1002,
  PARAM_RANGE_ERROR: 1003,

  // 业务错误 (2xxx)
  MATCH_NOT_FOUND: 2001,
  MATCH_FULL: 2002,
  ALREADY_REGISTERED: 2003,

  // 权限错误 (3xxx)
  NOT_LOGIN: 3001,
  NOT_ADMIN: 3002,
  NOT_OWNER: 3003,

  // 资源错误 (4xxx)
  RESOURCE_NOT_FOUND: 4001,
  RESOURCE_CONFLICT: 4002,

  // 系统错误 (5xxx)
  SYSTEM_ERROR: 5001,
  DB_ERROR: 5002
};

// 云函数中使用
exports.main = async (event, context) => {
  const { action, data } = event;

  if (!data.matchId) {
    return { code: ERROR_CODES.PARAM_REQUIRED, msg: '缺少 matchId' };
  }

  const match = await db.collection('matches').doc(data.matchId).get();
  if (!match) {
    return { code: ERROR_CODES.MATCH_NOT_FOUND, msg: '比赛不存在' };
  }

  // ...
};
```

## 调试技巧

### 查看详细错误

```javascript
// 开启详细日志
wx.request({
  url: '...',
  header: { 'X-Debug': 'true' },
  success(res) {
    console.log('完整响应:', res);
    console.log('状态码:', res.statusCode);
    console.log('响应头:', res.header);
  }
});
```

### 云函数日志

```javascript
// 云函数中打印日志
exports.main = async (event, context) => {
  console.log('Received event:', JSON.stringify(event));
  console.log('Context:', JSON.stringify(context));

  try {
    const result = await doSomething(event);
    console.log('Result:', result);
    return result;
  } catch (err) {
    console.error('Error:', err);
    throw err;
  }
};

// 查看云函数日志
// 云开发控制台 → 云函数 → 日志
```
