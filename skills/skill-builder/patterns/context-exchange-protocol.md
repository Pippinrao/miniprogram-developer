# 上下文交换协议设计模式

## 设计目标

在多Agent系统中建立标准化的通信协议，确保：
- 信息不丢失（通过路径引用）
- 上下文不膨胀（Token预算控制）
- 语义可解析（结构化JSON字段）
- 契约可验证（字段类型和必须性约束）

## 双向消息格式

### 主 → 子 (Task Spec)

目的：给子Agent足够的信息独立完成任务。

```json
{
  "task": "string (必须) — 任务类型枚举值",
  "projectPath": "string (必须) — 项目根目录绝对路径",
  "scope": ["string[] (必须) — 文件/目录范围，空数组=自行确定"],
  "reference": ["string[] (可选) — 预加载的知识文件路径"],
  "searchQuery": "string (可选) — 语义搜索关键词",
  "searchResults": ["string[] (可选) — 搜索命中的文档路径"],
  "context": {
    "previousPhase": "string — 前一阶段摘要",
    "designDoc": "string — 设计文档路径",
    "userApproval": "string — 用户确认内容",
    "<领域特定字段>": "..."
  },
  "mode": "string (可选) — 执行模式",
  "expectedOutput": {
    "summary": true,
    "keyFindings": true,
    "filesChanged": true,
    "testResults": true,
    "artifacts": true
  }
}
```

### 子 → 主 (Task Result)

目的：让主Agent汇总和决策，不传输代码原文。

```json
{
  "status": "success | failure | partial",
  "summary": "string — 一句话摘要（≤200字）",
  "filesChanged": ["string[]"],
  "keyFindings": ["string[] (≤5条)"],
  "testResults": {
    "pass": 0, "fail": 0, "skip": 0,
    "coverage": "string"
  },
  "artifacts": ["string[]"],
  "nextAction": "string — 建议的下一步"
}
```

## 字段可选性规则

| 字段 | 设计原则 |
|------|---------|
| `status` | 必须。三元状态覆盖所有场景 |
| `summary` | 必须。主Agent决策依据 |
| `filesChanged` | 必须。追踪变更 |
| `keyFindings` | 必须。提取关键信息 |
| `testResults` | 可null。非测试Agent不产生测试结果 |
| `artifacts` | 可空数组。无产物时省略 |
| `nextAction` | 可省略。无建议时不需要 |

## Token 预算设计

### 为什么要限制
- 防止上下文窗口溢出
- 强制信息压缩（只传关键信息）
- 鼓励路径引用（而非内容传输）

### 预算分配建议

**主→子 (500 tokens)**:
- 结构开销（task/projectPath/expectedOutput）: ~50 tokens
- scope 路径: ~30-50 tokens
- reference 路径: ~20-30 tokens
- searchQuery: ~20-30 tokens
- searchResults 路径: ~40-80 tokens
- context 数据: ~150-200 tokens
- mode/其他: ~10-20 tokens

**子→主 (300 tokens)**:
- 结构开销: ~35 tokens
- summary: ~30-50 tokens
- filesChanged 路径: ~30-60 tokens
- keyFindings (≤5条): ~80-120 tokens
- testResults: ~30-40 tokens
- 其他: ~20-30 tokens

## 禁止事项清单

```
❌ 主Agent传代码片段给子Agent
❌ 子Agent返回完整文件内容给主Agent
❌ 主Agent代替子Agent读取项目文件
❌ 子Agent请求主Agent"帮我查一下"
✅ 子Agent自己读取 projectPath 下的文件
✅ 主Agent只传路径，子Agent自己读
```

## 常见扩展模式

### 模式1: 分析类Agent
额外 context 字段：`context.existingCode`（已有代码的结构化摘要）

### 模式2: 修复类Agent
额外 context 字段：`context.errorInfo`（错误描述）, `context.fixSuggestion`（修复建议）

### 模式3: 设计类Agent
额外 context 字段：`context.focus`（聚焦领域，如 "pages"/"data"/"all"）

### 模式4: 测试类Agent
额外 mode 值：`ut` / `e2e` / `both` / `incremental`
