# 技能创建工作流 — skill-init

## 触发

用户说"创建XXX技能"、"搭建skill"、"脚手架"、"新建skill"

## 流程

```
用户: "我想创建一个鸿蒙开发技能"
  │
  ├─ ► 阶段1: 信息收集 [主Agent]
  │     1. 收集技能配置
  │        - 技能名称（英文，小写+连字符）
  │        - 领域描述（中文）
  │        - 目标平台/框架
  │        - 官方文档URL
  │        - 需要的Agent类型和数量
  │        - 需要的工作流类型和数量
  │     2. 展示配置摘要 → 等用户确认
  │     3. 加载 `patterns/multi-agent-architecture.md` 参考Agent命名
  │     决策: 用户确认 → 阶段2
  │
  ├─ ► 阶段2: 脚手架生成 [主Agent + scaffold-skill.py]
  │     1. 运行脚手架工具:
  │        python tools/scaffold-skill.py --name <name> --domain <domain> --path <path>
  │     2. 生成目录结构和模板文件
  │     3. 复制协议模板到 protocols/
  │     展示创建的文件清单
  │     决策: 脚手架成功 → 阶段3
  │
  ├─ ► 阶段3: 模板填充 [子Agent: 主Agent逐个填充]
  │     1. 填充 SKILL.md 占位符（工作流表、Agent表、搜索示例）
  │     2. 填充每个 Agent 的角色/执行/约束/示例
  │     3. 填充每个工作流的阶段/知识/错误处理
  │     4. 填充知识索引模板
  │     展示每个文件的填充结果
  │     决策: 用户确认 → 阶段4
  │
  └─ ► 阶段4: 首次盲审 [主Agent]
        1. 运行 `workflows/skill-audit.md` 工作流
        2. 获得首次评分
        3. 如 < 7.0 → 启动 `workflows/skill-improve.md` 改进
        4. 如 ≥ 7.0 → 输出完成报告
```

---

## 阶段1: 信息收集

### 信息收集清单

```markdown
## 技能配置收集

### 必填
- [ ] 技能名称（英文，小写+连字符，如 `harmonyos-dev`）
- [ ] 领域描述（中文，如 `鸿蒙单框架开发`）
- [ ] 目标平台/框架（如 `HarmonyOS NEXT API 12+`）

### Agent选型（选填，有默认值）
- [ ] 需求设计 Agent: `requirement-designer` (默认: 是)
- [ ] 代码分析 Agent: `code-analysis` (默认: 是)
- [ ] 代码实现 Agent: `code-implementation` (默认: 是)
- [ ] 测试设计 Agent: `test-design` (默认: 是)
- [ ] 测试执行 Agent: `test-execution` (默认: 是)
- [ ] 调试排错 Agent: `debugging` (默认: 是)
- [ ] 重构执行 Agent: `refactoring` (默认: 是)
- [ ] UI构建 Agent: `ui-page-builder` (默认: 否)
- [ ] 脚手架 Agent: `project-scaffold` (默认: 否)
- [ ] 领域特定 Agent: [自定义名称和描述]

### 工作流选型（选填，有默认值）
- [ ] 项目初始化: `project-init`
- [ ] 功能开发: `feature-dev`
- [ ] 组件开发: `component-dev`
- [ ] 测试: `testing`
- [ ] Bug修复: `bugfix`
- [ ] 重构: `refactor`
- [ ] 知识查询: `knowledge-lookup`
- [ ] 代码审查: `code-review`
- [ ] 性能优化: `perf-tuning`
- [ ] 技术选型: `tech-selection`
- [ ] 领域特定工作流: [自定义名称]
```

### 配置摘要模板

```markdown
## 技能配置摘要

| 配置项 | 值 |
|--------|-----|
| 技能名称 | harmonyos-dev |
| 领域 | 鸿蒙单框架开发 |
| Agent数 | 8 |
| 工作流数 | 10 |
| 知识库 | 是 |
| 模板目录 | ./templates/ |

确认以上配置开始创建技能？(yes/no)
```

---

## 阶段2: 脚手架生成

### 运行命令

```bash
python tools/scaffold-skill.py \
  --name harmonyos-dev \
  --domain "鸿蒙单框架开发" \
  --path /abs/path \
  --agents "requirement-designer,code-analysis,code-implementation,test-design,test-execution" \
  --workflows "project-init,feature-dev,component-dev,testing,bugfix,knowledge-lookup" \
  --with-knowledge
```

### 预期输出

```
skills/
└── harmonyos-dev/
    ├── SKILL.md
    ├── README.md
    ├── agents/
    │   ├── requirement-designer.md
    │   ├── code-analysis.md
    │   ├── code-implementation.md
    │   ├── test-design.md
    │   └── test-execution.md
    ├── workflows/
    │   ├── project-init.md
    │   ├── feature-dev.md
    │   └── ...
    ├── protocols/
    │   └── context-exchange.md
    ├── references/
    ├── official-docs/
    │   ├── INDEX.md
    │   └── framework/
    └── tools/
```

---

## 阶段3: 模板填充

### 主Agent动作

按以下顺序填充模板中的占位符：

1. **SKILL.md**: 填充 `{{WORKFLOW_TABLE}}`、`{{AGENT_TABLE}}`、`{{SEARCH_EXAMPLES}}`、`{{REFERENCE_TABLE}}`
2. **每个Agent**: 填充角色描述、执行步骤、约束、示例输出
3. **每个工作流**: 填充阶段名、执行者、动作、知识加载、错误处理表
4. **协议**: 填充任务类型枚举、执行模式、领域特定context字段
5. **知识索引**: 填充场景分类和文档列表

### 填充示例 (Agent)

将模板中的：
```
你是 {{DOMAIN}} {{ROLE_DESCRIPTION}}。
你的任务是 {{TASK_DESCRIPTION}}。
```

填充为：
```
你是鸿蒙单框架代码分析专家。
你的任务是仔细阅读ArkTS代码并产出结构化分析，不做任何修改。
```

---

## 错误处理

| 场景 | 处理 |
|------|------|
| 技能名称已存在 | 询问用户：覆盖/选择新名称/取消 |
| scaffold-skill.py 执行失败 | 检查 Python 版本（需 3.10+），检查模板目录是否存在 |
| 模板文件缺失 | 列出缺失的模板，手动创建或使用默认内容 |
| 占位符填充不完整 | 列出未填充的占位符，逐项补充 |
| 用户拒绝配置 | 调整配置后重新展示摘要 |
