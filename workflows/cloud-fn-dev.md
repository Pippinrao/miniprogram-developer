# 云函数开发工作流

多Agent协作的云函数开发流程。从需求分析到代码生成再到验收，确保每个云函数具备完整的鉴权、校验和统一返回格式。

## 流程

```
用户: "开发一个XXX的云函数"
  │
  ├─ ► 阶段1: 需求设计 [子Agent: requirement-designer]
  │     输入: { projectPath, requirement }
  │     聚焦: 云函数输入参数、输出结构、数据库操作
  │     输出: 设计文档 (designDoc.cloudFunctions + designDoc.dataModel)
  │     决策: 用户确认 → 阶段2
  │
  ├─ ► 阶段2: 云函数构建 [子Agent: cloud-fn-builder]
  │     输入: { designDoc.cloudFunctions, designDoc.dataModel }
  │     参考: ["official-docs/framework/云开发.md"]
  │     生成: index.js + package.json + config.json (含鉴权+校验)
  │     决策: 生成成功 → 阶段3
  │
  └─ ► 阶段3: 验收 [主Agent]
        验证: 鉴权 → 参数校验 → 错误处理 → 返回格式
        输出: 验收报告
```

---

## 阶段1: 需求设计

### 主Agent动作

1. 接收用户需求，提取云函数相关关键词
2. 启动子Agent: `requirement-designer`
3. 传递参数:

```
task: "requirement-designer"
projectPath: [项目路径]
requirement: [用户原始需求]
context: {
  focus: "cloudFunctions"  // 聚焦云函数设计
}
```

4. 子Agent 返回后，向用户展示设计文档中的云函数部分:

```markdown
## 云函数设计确认

### 云函数: [函数名]

| 维度 | 设计 |
|------|------|
| **输入参数** | `{ param1: string, param2: number }` |
| **输出结构** | `{ code: 0, msg: 'success', data: {...} }` |
| **数据库操作** | `collection.collection_name` — 查询/新增/更新/删除 |
| **权限要求** | 仅创建者可写 / 所有用户可读 / 管理员 |
| **鉴权方式** | `cloud.getWXContext().OPENID` |

### 数据模型涉及
| 集合 | 字段 | 类型 | 说明 |
|------|------|------|------|
| xxx | field1 | string | 说明 |
```

5. **必须等用户确认**后才能进入阶段2。确认内容包括:
   - 输入参数是否完整
   - 输出数据是否满足前端需求
   - 数据库权限策略是否正确
   - 是否需要关联其他集合

---

## 阶段2: 云函数构建

### 主Agent动作

1. 启动子Agent: `cloud-fn-builder`
2. 传递参数:

```
task: "cloud-fn-builder"
projectPath: [项目路径]
scope: [阶段1中 designDoc.cloudFunctions 涉及的云函数名称列表]
context: {
  designDoc: {
    cloudFunctions: [阶段1设计文档中的云函数定义],
    dataModel: [阶段1设计文档中的数据模型]
  }
}
reference: ["official-docs/framework/云开发.md"]
```

3. 子Agent 为每个云函数生成以下文件:
   - `cloudfunctions/<函数名>/index.js` — 业务逻辑 + 鉴权 + 校验 + 统一返回
   - `cloudfunctions/<函数名>/package.json` — wx-server-sdk 依赖声明
   - `cloudfunctions/<函数名>/config.json` — 权限配置

4. 子Agent 必须遵循以下约束:
   - 每个云函数包含 `cloud.getWXContext().OPENID` 身份校验
   - 每个云函数包含必填参数校验
   - 返回格式统一为 `{ code, msg, data }`
   - 数据库操作必须过滤 `_openid`（用户只能操作自己的数据）
   - 云函数目录不存在时自动创建

5. 子Agent 返回后，主Agent检查输出完整性:
   - 所有云函数目录是否已创建
   - index.js / package.json / config.json 三文件是否齐全
   - `authVerified: true` 是否确认

---

## 阶段3: 验收

### 主Agent动作

逐项验证每个生成的云函数，输出验收报告。

### 验收检查清单

```markdown
## 云函数验收: [函数名]

### 鉴权验证
- [ ] 使用 cloud.getWXContext() 获取用户身份
- [ ] 数据库查询/更新/删除操作过滤 _openid
- [ ] 敏感操作有权限判断逻辑

### 参数校验验证
- [ ] 检查了必填参数 (event.xxx 非空判断)
- [ ] 参数类型校验 (typeof / Array.isArray)
- [ ] 参数范围校验 (长度/数值范围)
- [ ] 校验失败返回 { code: -1, msg: '具体原因' }

### 错误处理验证
- [ ] try-catch 包裹主逻辑
- [ ] 数据库操作异常有 catch 处理
- [ ] catch 返回 { code: -1, msg: '服务内部错误', error: err.message }
- [ ] 不暴露敏感错误栈到前端（可记录到日志）

### 返回格式验证
- [ ] 成功返回 { code: 0, msg: 'success', data: {...} }
- [ ] 失败返回 { code: -1, msg: '具体错误描述' }
- [ ] data 字段结构符合设计文档定义
```

### 验收报告模板

```markdown
# 云函数开发完成报告

## 云函数: [函数名]

### 生成文件
| 文件 | 路径 |
|------|------|
| index.js | cloudfunctions/[函数名]/index.js |
| package.json | cloudfunctions/[函数名]/package.json |
| config.json | cloudfunctions/[函数名]/config.json |

### 验收结果
| 检查项 | 状态 |
|--------|------|
| OPENID 鉴权 | ✅ / ❌ |
| 参数校验 | ✅ / ❌ |
| 错误处理 | ✅ / ❌ |
| 返回格式 | ✅ / ❌ |
| 数据库 _openid 过滤 | ✅ / ❌ / N/A |

### 云函数调用示例
```javascript
// 前端调用
const res = await wx.cloud.callFunction({
  name: '[函数名]',
  data: { param1: 'xxx', param2: 123 }
});

// 期望返回
// { code: 0, msg: 'success', data: {...} }
// 或
// { code: -1, msg: '缺少必要参数: param1' }
```

## 状态: ✅ 云函数开发完成
```

---

## 云函数 index.js 统一模板

所有云函数必须遵循以下结构: **参数校验 → 鉴权 → 业务逻辑 → 统一返回**。

```javascript
const cloud = require('wx-server-sdk');
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV });

const db = cloud.database();

exports.main = async (event, context) => {
  try {
    // ==========================================
    // 1. 获取用户身份
    // ==========================================
    const { OPENID } = cloud.getWXContext();
    if (!OPENID) {
      return { code: -1, msg: '未获取到用户身份，请重新登录' };
    }

    // ==========================================
    // 2. 参数校验
    // ==========================================
    const { param1, param2 } = event;
    const errors = [];

    if (!param1 || typeof param1 !== 'string') {
      errors.push('param1 为必填字符串');
    }
    if (param2 !== undefined && typeof param2 !== 'number') {
      errors.push('param2 必须为数字类型');
    }

    if (errors.length > 0) {
      return { code: -1, msg: errors.join('; ') };
    }

    // ==========================================
    // 3. 权限验证（按需补充）
    // ==========================================
    // 示例: 检查是否为资源所有者
    // const resource = await db.collection('xxx').doc(param1).get();
    // if (resource.data._openid !== OPENID) {
    //   return { code: -1, msg: '无权操作此资源' };
    // }

    // ==========================================
    // 4. 业务逻辑
    // ==========================================
    // 示例: 数据库查询
    // const result = await db.collection('collection_name')
    //   .where({ _openid: OPENID })
    //   .orderBy('createTime', 'desc')
    //   .limit(20)
    //   .get();

    // 示例: 数据库新增
    // const result = await db.collection('collection_name').add({
    //   data: {
    //     ...validatedData,
    //     _openid: OPENID,
    //     createTime: db.serverDate()
    //   }
    // });

    // ==========================================
    // 5. 统一返回
    // ==========================================
    return {
      code: 0,
      msg: 'success',
      data: {
        // 按设计文档填充返回数据
      }
    };

  } catch (err) {
    console.error('[云函数名] 执行异常:', err);
    return {
      code: -1,
      msg: '服务内部错误',
      error: err.message
    };
  }
};
```

### 返回格式约定

| 场景 | code | msg | data |
|------|------|-----|------|
| 成功 | `0` | `'success'` | 业务数据对象 |
| 参数缺失 | `-1` | `'缺少必要参数: xxx'` | — |
| 参数非法 | `-1` | `'参数xxx格式错误/超出范围'` | — |
| 鉴权失败 | `-1` | `'未获取到用户身份'` / `'无权操作'` | — |
| 资源不存在 | `-1` | `'资源不存在或已被删除'` | — |
| 服务异常 | `-1` | `'服务内部错误'` | `error: err.message` |
