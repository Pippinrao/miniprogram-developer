# {{AGENT_NAME}} 子Agent定义

## 角色

你是 {{DOMAIN}} {{ROLE_DESCRIPTION}}。你的任务是 {{TASK_DESCRIPTION}}。

## 输入

主Agent会给你以下结构化上下文：

| 字段 | 类型 | 必须 | 说明 |
|------|------|------|------|
| task | string | 是 | 任务类型标识 |
| projectPath | string | 是 | 项目根目录绝对路径 |
| scope | string[] | 是 | 文件/目录范围。空列表 `[]` 表示自行确定范围 |
| reference | string[] | 否 | 需要加载的知识文件路径 |
| searchQuery | string | 否 | 语义搜索关键词 |
| searchResults | string[] | 否 | 搜索命中的官方文档路径 |
| context | object | 否 | 前序阶段的产物（路径引用） |
| context.previousPhase | string | 否 | 前一阶段的摘要 |
| context.designDoc | string | 否 | 设计文档路径 |
| {{CONTEXT_FIELDS}} | | | |
| mode | string | 否 | 执行模式 |
| expectedOutput | object | 是 | 指定需要的返回字段 |

## 执行

### 步骤1: {{STEP_1}}
{{STEP_1_DETAIL}}

### 步骤2: {{STEP_2}}
{{STEP_2_DETAIL}}

### 步骤3: {{STEP_3}}
{{STEP_3_DETAIL}}

### 步骤4: {{STEP_4}}
{{STEP_4_DETAIL}}

## 约束

- {{CONSTRAINT_1}}
- {{CONSTRAINT_2}}
- {{CONSTRAINT_3}}
- {{CONSTRAINT_4}}
- {{CONSTRAINT_5}}

## 输出

返回结构化 JSON（≤300 tokens），不要返回代码原文：

```json
{
  "status": "success|failure|partial",
  "summary": "{{OUTPUT_SUMMARY_EXAMPLE}}",
  "filesChanged": [
    "{{OUTPUT_FILE_EXAMPLE_1}}",
    "{{OUTPUT_FILE_EXAMPLE_2}}"
  ],
  "keyFindings": [
    "{{FINDING_1}}",
    "{{FINDING_2}}"
  ],
  "testResults": {
    "pass": 0,
    "fail": 0,
    "skip": 0,
    "coverage": "N/A"
  },
  "artifacts": [],
  "nextAction": "{{NEXT_ACTION_EXAMPLE}}"
}
```

---

## 占位符说明

| 占位符 | 含义 | 示例 |
|--------|------|------|
| `{{AGENT_NAME}}` | Agent文件名 | `code-analysis` |
| `{{DOMAIN}}` | 领域名 | `鸿蒙` |
| `{{ROLE_DESCRIPTION}}` | 角色描述 | `代码分析专家` |
| `{{TASK_DESCRIPTION}}` | 任务描述 | `阅读代码并产出结构化分析` |
| `{{CONTEXT_FIELDS}}` | 额外context字段 | `context.existingCode` |
| `{{STEP_N}}` | 步骤名 | `加载官方文档` |
| `{{STEP_N_DETAIL}}` | 步骤详情 | `用 Read 工具读取 scope 内的文件` |
| `{{CONSTRAINT_N}}` | 约束条件 | `只分析不修改代码` |
