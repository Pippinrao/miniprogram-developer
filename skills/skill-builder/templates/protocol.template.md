# 上下文交换协议 — {{SKILL_NAME}}

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
  "task": "{{TASK_TYPES}}",
  "projectPath": "/absolute/path/to/project",
  "scope": ["dir1/", "file2.ext"],
  "reference": ["references/xxx.md"],
  "searchQuery": "从用户需求提取的搜索关键词",
  "searchResults": ["official-docs/category/命中文档.md"],
  "context": {
    "previousPhase": "前一阶段的摘要",
    "designDoc": "/path/to/design.md",
    "userApproval": "用户确认的内容",
    "{{EXTRA_CONTEXT_FIELDS}}": "..."
  },
  "mode": "{{EXECUTION_MODES}}",
  "expectedOutput": {
    "summary": true,
    "keyFindings": true,
    "filesChanged": true,
    "testResults": true,
    "artifacts": true
  }
}
```

### 字段说明

| 字段 | 类型 | 必须 | 说明 |
|------|------|------|------|
| task | string | 是 | 任务类型: {{TASK_TYPE_ENUMS}} |
| projectPath | string | 是 | 项目根目录绝对路径 |
| scope | string[] | 是 | 文件/目录范围。允许空 `[]`，子Agent自行确定范围 |
| reference | string[] | 否 | 需要加载的知识文件路径列表 |
| searchQuery | string | 否 | 语义搜索关键词（主Agent事先搜索，结果放入 searchResults） |
| searchResults | string[] | 否 | 语义搜索命中的官方文档路径列表 |
| context | object | 否 | 前序阶段的产物（路径引用） |
| context.previousPhase | string | 否 | 前一阶段的摘要 |
| context.designDoc | string | 否 | 设计文档路径 |
| context.userApproval | string | 否 | 用户确认的内容 |
| {{EXTRA_FIELD_DEFS}} | | | |
| mode | string | 否 | 执行模式: {{MODE_ENUMS}} |
| expectedOutput | object | 是 | 指定需要的返回字段（true=需要，false=跳过） |

---

## 子 → 主 (Task Result)

```json
{
  "status": "success|failure|partial",
  "summary": "一句话摘要（≤200字）",
  "filesChanged": ["path/file1.ext", "path/file2.ext"],
  "keyFindings": ["发现1", "发现2"],
  "testResults": {
    "pass": 10,
    "fail": 0,
    "skip": 2,
    "coverage": "75%"
  },
  "artifacts": ["/path/to/report.md"],
  "nextAction": "建议的下一步"
}
```

- `testResults`: 无测试场景时可为 `null`
- `artifacts`: 可选，无产物时为空数组 `[]`
- `nextAction`: 可选，无建议时可省略

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
阶段2 (测试设计) → testSpec 路径
    ↓
阶段3 (代码实现) → filesChanged + testResults
    ↓
阶段4 (验收)     → 汇总报告
```

每个阶段只接收上一阶段的**摘要**，不接收完整设计文档内容。

---

## 占位符说明

| 占位符 | 含义 | 示例 |
|--------|------|------|
| `{{SKILL_NAME}}` | 技能名称 | `harmonyos-dev` |
| `{{TASK_TYPES}}` | 任务类型（用\|分隔） | `code-analysis\|code-implementation\|test-execution` |
| `{{EXECUTION_MODES}}` | 执行模式（用\|分隔） | `ut\|e2e\|both` |
| `{{EXTRA_CONTEXT_FIELDS}}` | 领域特定的context字段 | `existingCode`, `errorInfo` |
| `{{EXTRA_FIELD_DEFS}}` | 额外字段定义 | `context.existingCode \| object \| 否 \| 已有代码摘要` |
| `{{MODE_ENUMS}}` | 执行模式枚举值 | `ut` / `e2e` / `both` |
