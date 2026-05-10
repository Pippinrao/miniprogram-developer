# 上下文交换协议

## 核心规则

```
╔══════════════════════════════════════════════════════════╗
║  绝对不传代码原文         绝对不传完整文件内容         ║
║  只传: 文件路径 + 结构化摘要 + 关键发现 + 测试结果     ║
╚══════════════════════════════════════════════════════════╝
```

- **信息量**: 主→子 ≤500 tokens，子→主 ≤300 tokens
- **代码/文件**: 永远通过路径引用，不传内容
- **产物**: 通过文件路径传递，子Agent写入项目目录

---

## 主 → 子 (Task Spec)

```json
{
  "task": "code-analysis|test-design|test-execution|code-implementation|debugging|refactoring",
  "projectPath": "/absolute/path/to/project",
  "scope": ["dir1/", "file2.js"],
  "reference": ["references/unit-test.md"],
  "searchQuery": "从用户需求或错误信息中提取的关键词（用于语义搜索）",
  "searchResults": ["official-docs/framework/命中文档1.md", "official-docs/framework/命中文档2.md"],
  "context": {
    "previousPhase": "前一阶段的摘要",
    "designDoc": "/path/to/design.md",
    "userApproval": "用户确认的内容",
    "existingCode": {"summary": "已有代码的结构化摘要", "path": "可选的文件路径"},
    "focus": "cloudFunctions|pages|components|all（可选，聚焦领域）"
  },
  "mode": "ut|e2e|both|incremental（test-execution 专用）",
  "expectedOutput": {
    "summary": true,
    "keyFindings": "≤5",
    "filesChanged": true,
    "testResults": true,
    "artifacts": true
  }
}
```

### 字段说明

| 字段 | 类型 | 必须 | 说明 |
|------|------|------|------|
| task | string | 是 | 任务类型: code-analysis\|test-design\|test-execution\|code-implementation\|debugging\|refactoring |
| projectPath | string | 是 | 项目根目录绝对路径 |
| scope | string[] | 是 | 文件/目录范围列表。允许空列表 `[]`，此时子Agent自行通过搜索+代码grep确定范围 |
| reference | string[] | 否 | 需要加载的知识文件路径列表 |
| searchQuery | string | 否 | 语义搜索关键词（从用户需求或错误信息提取）。主Agent先运行 `python tools/search_docs.py "<searchQuery>"`，将命中路径填入 searchResults |
| searchResults | string[] | 否 | 语义搜索命中的官方文档路径列表（由主Agent搜索后填入，传给子Agent） |
| context | object | 否 | 前序阶段的产物（路径引用） |
| context.previousPhase | string | 否 | 前一阶段的摘要 |
| context.designDoc | string | 否 | 设计文档路径 |
| context.errorInfo | string | 否 | 错误描述/堆栈（debugging任务） |
| context.analysisResult | object | 否 | 代码分析子集 {summary, modules, testability, keyFindings} |
| context.testDesign | object | 否 | 测试设计输出 {utCases, e2eScenarios} |
| context.fixSuggestion | string | 否 | 修复建议（修复模式） |
| context.hotfix | boolean | 否 | 是否热修复模式（code-implementation） |
| mode | string | 否 | 执行模式: ut\|e2e\|both\|incremental（test-execution） |
| expectedOutput | object | 是 | 指定需要的返回字段 |

---

## 子 → 主 (Task Result)

```json
{
  "status": "success|failure|partial",
  "summary": "一句话摘要（≤200字）",
  "filesChanged": ["path/file1.js", "path/file2.wxml"],    // 修改或创建的文件路径列表。也可用 filesCreated 表示仅创建，filesAnalyzed 表示仅分析（code-analysis 用）
  "keyFindings": ["发现1", "发现2", "发现3"],
  "testResults": {              // 无测试的Agent可为 null
    "pass": 10,
    "fail": 0,
    "skip": 2,
    "coverage": "75%"
  },
  "artifacts": ["/path/to/report.md", "/path/to/screenshot.png"],  // 可选，无产物时为空数组
  "nextAction": "建议的下一步"   // 可选，无建议时可为空字符串或省略
}
```

### 状态码

| status | 含义 | 主Agent行为 |
|--------|------|-----------|
| success | 任务完成 | 进入下一阶段或验收 |
| failure | 任务失败 | 分析原因，决定重试或切换策略 |
| partial | 部分完成 | 检查哪些部分未完成，决定是否补充 |

---

## 禁止事项

- ❌ 主Agent把代码片段传给子Agent
- ❌ 子Agent返回完整文件内容给主Agent
- ❌ 主Agent代替子Agent读取项目文件
- ❌ 子Agent请求主Agent"帮我查一下XXX文件"
- ✅ 子Agent自己用 Read 工具读取 projectPath 下的文件
- ✅ 主Agent只传路径，子Agent自己读文件

---

## 阶段间传递

上一个阶段的输出 → 自然成为下一个阶段的输入:

```
阶段1 (需求设计) → designDoc 路径
    ↓
阶段2 (测试设计) → testSpec 路径 + utCases + e2eScenarios
    ↓
阶段3 (代码实现) → filesChanged + utResults
    ↓
阶段4 (E2E验证) → e2eResults
    ↓
阶段5 (验收)     → 汇总报告
```

每个阶段只接收上一阶段的**摘要**，不接收完整设计文档内容。
