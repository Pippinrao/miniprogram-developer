# {{WORKFLOW_NAME}} 工作流

## 触发条件

| 关键词 |
|--------|
| {{TRIGGER_KEYWORDS}} |

## 流程

```
用户: "{{EXAMPLE_USER_INPUT}}"
  │
  ├─ ► 阶段1: {{PHASE_1_NAME}} [{{PHASE_1_EXECUTOR}}]
  │     {{PHASE_1_ACTIONS}}
  │     决策: {{PHASE_1_DECISION}}
  │
  ├─ ► 阶段2: {{PHASE_2_NAME}} [{{PHASE_2_EXECUTOR}}]
  │     {{PHASE_2_ACTIONS}}
  │     决策: {{PHASE_2_DECISION}}
  │
  ├─ ► 阶段3: {{PHASE_3_NAME}} [{{PHASE_3_EXECUTOR}}]
  │     {{PHASE_3_ACTIONS}}
  │     决策: {{PHASE_3_DECISION}}
  │
  └─ ► 阶段N: {{PHASE_N_NAME}} [{{PHASE_N_EXECUTOR}}]
        {{PHASE_N_ACTIONS}}
        输出: {{PHASE_N_OUTPUT}}
```

---

## 阶段1: {{PHASE_1_NAME}}

### 主Agent动作

{{PHASE_1_MAIN_ACTIONS}}

### 知识加载

{{PHASE_1_KNOWLEDGE}}

### 传递子Agent

```
task: "{{PHASE_1_TASK_TYPE}}"
projectPath: "{{PHASE_1_PROJECT_PATH}}"
scope: {{PHASE_1_SCOPE}}
context: {
  {{PHASE_1_CONTEXT}}
}
reference: {{PHASE_1_REFERENCES}}
```

### 决策点

- 成功 → 阶段2
- 失败 → {{PHASE_1_FAILURE_HANDLING}}

---

## 阶段2: {{PHASE_2_NAME}}

### 主Agent动作

{{PHASE_2_MAIN_ACTIONS}}

### 知识加载

{{PHASE_2_KNOWLEDGE}}

### 传递子Agent

```
task: "{{PHASE_2_TASK_TYPE}}"
projectPath: "{{PHASE_2_PROJECT_PATH}}"
scope: {{PHASE_2_SCOPE}}
context: {
  {{PHASE_2_CONTEXT}}
}
reference: {{PHASE_2_REFERENCES}}
```

### 决策点

- 成功 → 阶段3
- 失败 → {{PHASE_2_FAILURE_HANDLING}}

---

## 阶段3: {{PHASE_3_NAME}}

### 主Agent动作

{{PHASE_3_MAIN_ACTIONS}}

### 验收模板

```markdown
# {{WORKFLOW_NAME}} 完成报告

## {{REPORT_SECTION_1}}
| 项目 | 值 |
|------|-----|
| {{FIELD_1}} | {{VALUE_1}} |

## {{REPORT_SECTION_2}}
...

## 状态: ✅ / ⚠️ / ❌
```

---

## 错误处理

| 场景 | 处理 |
|------|------|
| {{ERROR_1}} | {{ERROR_1_HANDLING}} |
| {{ERROR_2}} | {{ERROR_2_HANDLING}} |
| {{ERROR_3}} | {{ERROR_3_HANDLING}} |
| {{ERROR_4}} | {{ERROR_4_HANDLING}} |
| {{ERROR_5}} | {{ERROR_5_HANDLING}} |

---

## 占位符说明

| 占位符 | 含义 | 填写格式提示 |
|--------|------|-------------|
| `{{WORKFLOW_NAME}}` | 工作流名 | 中文，如 `功能开发` |
| `{{TRIGGER_KEYWORDS}}` | 触发关键词列表 | 逗号分隔，如 `"新增功能", "开发XXX", "实现需求"` |
| `{{PHASE_N_NAME}}` | 阶段名称 | 中文，如 `需求设计`、`并行开发`、`验收交付` |
| `{{PHASE_N_EXECUTOR}}` | 执行者 | `[主Agent]` 或 `[子Agent: agent-name]` |
| `{{PHASE_N_ACTIONS}}` | 该阶段的核心动作 | 编号列表，每项一行 |
| `{{PHASE_N_DECISION}}` | 决策条件 | 如 `用户确认 → 阶段2`、`全部通过 → 阶段3` |
| `{{PHASE_N_MAIN_ACTIONS}}` | 主Agent在该阶段的具体动作 | 编号列表，每项一行 |
| `{{PHASE_N_KNOWLEDGE}}` | 需要加载的知识文档 | 文件路径列表，如 `加载: agents/xxx.md + official-docs/yyy.md` |
| `{{PHASE_N_TASK_TYPE}}` | 传递给子Agent的task类型 | 与协议中的task枚举值一致 |
| `{{PHASE_N_CONTEXT}}` | 传递给子Agent的context字段 | JSON键值对，如 `"designDoc": "/path/to/design.md"` |
| `{{REPORT_SECTION_N}}` | 验收报告的章节标题 | 中文，如 `测试结果`、`变更统计` |
| `{{ERROR_N}}` | 错误场景描述 | 中文，如 `子Agent返回failure` |
| `{{ERROR_N_HANDLING}}` | 错误处理方式 | 中文，如 `分析原因，重试（最多3次）` |

### 复合占位符填写示例

`{{WORKFLOW_TABLE}}` 期望格式：
```markdown
| "创建项目"、"初始化" | project-init | `workflows/project-init.md` |
| "做XXX功能"、"新增XXX" | feature-dev | `workflows/feature-dev.md` |
```

`{{AGENT_TABLE}}` 期望格式：
```markdown
| 代码分析 | `agents/code-analysis.md` | 搜索对应领域关键词 → 加载命中文档 |
| 代码实现 | `agents/code-implementation.md` | 加载设计文档 + 官方API文档 |
```

`{{REFERENCE_TABLE}}` 期望格式：
```markdown
| 单元测试配置 | `references/unit-test.md` |
| E2E测试模式 | `references/e2e-testing.md` |
```
