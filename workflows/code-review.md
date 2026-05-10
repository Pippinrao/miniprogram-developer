# 代码审查工作流

审查代码质量，识别问题和改进点。不修改代码，仅输出结构化审查报告。

## 触发条件

| 关键词 |
|--------|
| "帮我 review 代码"、"代码审查"、"review 代码"、"CR"、"检查代码质量" |

## 流程

```
用户: "帮我 review 一下这段代码"
  │
  ├─ ► 阶段0: 审查准备 [主Agent]
  │     确认: 审查范围（文件/目录）、审查重点（性能/安全/规范/全部）
  │     搜索: search_docs.py "代码最佳实践 架构设计 安全" --top 5
  │     【用户确认审查范围和重点】
  │
  ├─ ► 阶段1: 代码分析 [子Agent: code-analysis]
  │     输入: { projectPath, scope, searchResults, context: { focusAreas } }
  │     子Agent分析: 模块结构、依赖关系、代码质量、测试盲区、安全风险
  │
  └─ ► 阶段2: 审查报告与讨论 [主Agent]
        汇总分析结果，输出结构化审查报告
        【用户审阅报告，可对具体问题提问或调整严重度】
        └─ 用户有疑问 → 深入分析 → 更新报告
```

## 阶段0: 审查准备

### 审查范围确认

向用户确认：
1. **审查范围**: 哪些文件/目录？(默认: 最近修改的文件)
2. **审查重点** (可多选):
   - 代码结构与模块化
   - 命名规范
   - 性能问题 (setData/渲染/内存)
   - 安全风险 (敏感数据/权限/注入)
   - 测试覆盖
   - 无障碍/可访问性
   - 全部检查
3. **严重度侧重**: 只报 Critical / Critical+Major / 全部等级

### 知识准备

```bash
python tools/search_docs.py "代码最佳实践 架构设计 安全 性能优化" --top 5
```

## 阶段2: 审查报告

### 严重度分级标准

| 等级 | 定义 | 示例 | 必须修复 |
|------|------|------|---------|
| **Critical** | 安全漏洞、数据丢失风险、线上崩溃 | SQL注入、未校验的openid、死循环setData | 是 |
| **Major** | 性能显著下降、功能缺陷、规范严重违反 | 循环中setData、缺少错误处理、内存泄漏 | 是（本次） |
| **Minor** | 代码异味、可维护性问题、轻微规范违反 | 命名不规范、函数过长、缺少注释 | 建议修复 |
| **Info** | 改进建议、最佳实践提醒 | 可用新API替代、可提取公共函数 | 自行决定 |

### 审查清单

#### 1. 代码结构 (Critical+Major)
- [ ] 页面/组件是否职责单一？（一个Page ≤ 500 行，一个Component ≤ 300 行）
- [ ] 是否存在跨页面/跨组件的紧耦合？
- [ ] 工具函数是否正确抽取到 utils/ ？
- [ ] 目录结构是否符合项目约定？

#### 2. 性能问题 (Critical+Major+Minor)
- [ ] setData 是否在循环中调用？是否传递了过大数据？
- [ ] 是否在 onLoad/onReady 中执行了同步耗时操作？
- [ ] WXML 中是否存在不必要的嵌套或过长的列表渲染？
- [ ] 图片资源是否过大未压缩？
- [ ] 是否存在未清理的定时器/监听器（内存泄漏风险）？

#### 3. 安全风险 (Critical)
- [ ] 用户输入是否经过校验和转义？
- [ ] openid / unionid 是否在后端校验（而非仅前端判断）？
- [ ] 敏感数据（token/key）是否硬编码在代码中？
- [ ] 云函数是否有权限校验（检查 _openid 匹配）？
- [ ] 是否存在 XSS 风险（rich-text / web-view 未过滤内容）？

#### 4. 错误处理 (Major+Minor)
- [ ] wx.request / 云函数调用是否有 .catch() 或 fail 回调？
- [ ] 异步操作是否正确使用 async/await + try-catch？
- [ ] Promise 链是否完整（无悬空 Promise）？

#### 5. 测试覆盖 (Major+Minor)
- [ ] 关键业务逻辑是否有单元测试？
- [ ] 新增页面/组件是否有对应的测试文件？
- [ ] 边界条件（空数据/网络失败/权限拒绝）是否被测试覆盖？

#### 6. 小程序特有检查 (Critical+Major)
- [ ] app.json 中注册的页面是否与 pages/ 目录一致？
- [ ] 自定义组件是否在需要的页面的 .json 中注册？
- [ ] 分包配置是否正确（路径/预下载规则）？
- [ ] 是否在小程序限制内（主包2MB/总包20MB/单个分包2MB）？

### 输出格式

```json
{
  "status": "success",
  "summary": {
    "filesReviewed": 5,
    "totalIssues": 12,
    "critical": 2,
    "major": 4,
    "minor": 4,
    "info": 2
  },
  "issues": [
    {
      "severity": "critical",
      "file": "pages/order/order.js",
      "line": 45,
      "issue": "openid 仅在前端校验，未调用云函数验证",
      "fix": "将 openid 传入云函数，在服务端通过 wxContext.OPENID 校验",
      "reference": "official-docs/framework/开放数据校验与解密.md"
    },
    {
      "severity": "major",
      "file": "pages/index/index.js",
      "line": 78,
      "issue": "setData 在 for 循环中调用 15 次",
      "fix": "将数据合并到临时对象，循环结束后一次性 setData",
      "reference": "official-docs/framework/合理使用_setData.md"
    }
  ],
  "statistics": {
    "issueDensity": "2.4 issues/file",
    "topIssueTypes": ["setData滥用", "缺少错误处理", "命名不规范"],
    "testCoverageEstimate": "约30%",
    "filesWithZeroTests": ["pages/order/order.js", "utils/format.js"]
  },
  "nextAction": "建议优先修复 2 个 Critical 问题，然后处理 4 个 Major 问题"
}
```

## 错误处理

| 场景 | 处理 |
|------|------|
| 审查文件不存在 | 报告主Agent，确认文件路径是否正确 |
| 文件量过大（>20个文件） | 建议分批审查，或仅审查关键模块 |
| 代码语法错误导致无法解析 | 标注为 Critical：代码无法编译，需先修复语法错误 |
| code-analysis 子Agent返回 failure | 展示原始错误信息，请用户确认是否重试或缩小范围 |
| search_docs.py 无搜索结果 | 使用内置审查清单，标注"未加载官方文档参考" |

## 约束
- 只审查不修改代码
- 每个 issue 必须标注文件路径和行号（或函数名）
- Critical/Major 问题必须给出具体修复代码建议
- 优先检查小程序最常见的 5 个问题：setData 滥用、内存泄漏、异步处理缺失、openid 前端校验、分包配置错误
- 审查报告保存到 `review-report-{timestamp}.md` 以便追踪
