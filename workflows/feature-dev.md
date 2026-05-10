# 功能开发工作流

多Agent协作的完整功能开发流程。

## 流程

```
用户: "我想做XXX功能"
  │
  ├─ ► 阶段1: 需求设计 [子Agent: requirement-designer]
  │     输入: { projectPath, requirement }
  │     子Agent加载: agents/requirement-designer.md + FRAMEWORK_INDEX.md + 领域文档
  │     执行: 识别领域→查知识库→组件库选型→扫描项目→输出设计文档
  │     输出: designDoc (含 pages/components/cloudFunctions/dataModel)
  │     决策: 用户确认 → 阶段2
  │
  ├─ ► 阶段2: 并行开发 [子Agent: ui-page-builder + code-implementation]
  │     分支A [ui-page-builder]:
  │       输入: { designDoc.pages, designDoc.components, designDoc.componentLib }
  │       加载: agents/ui-page-builder.md + WXML/WXSS/组件库文档
  │       输出: WXML/WXSS/JSON 文件 + app.json 注册 + uiOutput(交接数据)
  │     分支B [code-implementation]:
  │       输入: { designDoc, context: { uiOutput } }
  │       加载: agents/code-implementation.md + 设计文档引用的官方页面
  │       TDD循环: 写测试→失败→实现→通过→重构
  │       输出: .js 业务逻辑 + UT 通过
  │     合并: 主Agent检查 UI/Logic 一致性(bindtap事件 vs JS方法)
  │     决策: 全部通过 → 阶段3, 否则补充修复
  │
  ├─ ► 阶段3: 测试设计 [子Agent: test-design]
  │     输入: { projectPath, scope, context: { analysisResult } }
  │     子Agent加载: agents/test-design.md + references/unit-test.md + references/e2e-testing.md
  │     输出: { utCases, e2eScenarios }
  │     决策: 用户确认测试用例 → 阶段4
  │
  ├─ ► 阶段4: E2E验证 [子Agent: test-execution, mode=e2e]
  │     输入: { projectPath, context: { testDesign: { e2eScenarios } } }
  │     子Agent加载: agents/test-execution.md + references/e2e-testing.md
  │     决策: E2E全部通过 → 阶段5, 否则返回修复
  │
  └─ ► 阶段5: 验收 [主Agent]
        整合所有结果，输出验收报告
```

## 阶段调度指令

### 阶段1: 需求设计 [主Agent → requirement-designer]

主Agent动作:
1. 启动子Agent: `requirement-designer`
2. 传递: `{ task: "requirement-designer", projectPath, requirement: "用户原文", reference: ["official-docs/FRAMEWORK_INDEX.md"] }`
3. 展示 designDoc 给用户（含技术方案+组件库选择+知识来源）
4. **必须等用户确认**才能进入阶段2。如用户说"直接开发"→ 跳到阶段2但必须提示跳过设计可能返工

### 阶段2: 并行开发 [主Agent]

主Agent同时启动两个子Agent:

**分支A: UI构建**
1. 启动子Agent: `ui-page-builder`
2. 传递: `{ task: "ui-page-builder", projectPath, scope: ["designDoc中所有页面和组件路径"], context: { designDoc: { pages, components, componentLib } }, reference: ["official-docs/framework/WXML_模板.md", "official-docs/framework/WXSS_样式.md"] }`
3. 等待返回: `{ filesCreated, uiOutput }`

**分支B: 逻辑实现**
1. 启动子Agent: `code-implementation`
2. 传递: `{ task: "code-implementation", projectPath, scope: ["designDoc中所有JS文件路径"], context: { designDoc, testDesign: null, uiOutput: "来自分支A的交接数据" }, reference: ["设计文档中引用的官方页面"] }`
3. TDD循环: 写测试 → 失败 → 写实现 → 通过 → 重构
4. 检查 testResults.pass/fail

**合并检查**:
主Agent比对 uiOutput.eventBindings 和 code-implementation 实现的方法:
- WXML 中 `bindtap="handleLogin"` → JS 中有 `handleLogin()` ✓
- 不一致 → 启动补充 code-implementation 轮次修复

### 阶段3: 测试设计 [主Agent → test-design]

1. 启动子Agent: `test-design`
2. 传递: `{ task: "test-design", projectPath, scope: ["阶段2涉及的所有文件"], context: { analysisResult: null, designDoc: "阶段1输出" } }`
3. 展示 utCases + e2eScenarios 给用户
4. **必须等用户确认**才能进入阶段4

### 阶段4: E2E验证 [主Agent → test-execution]

1. 启动子Agent: `test-execution`, mode=e2e
2. 传递: `{ task: "test-execution", projectPath, scope: ["所有页面/组件"], mode: "e2e", context: { testDesign: { e2eScenarios } } }`
3. 全部通过 → 阶段5, 否则返回阶段2修复

### 阶段5: 验收 [主Agent]

1. 汇总所有阶段输出
2. 验收报告: 实现内容 + 测试结果 + 覆盖率 + 验收标准逐项检查
3. 状态: ✅/⚠️

## 设计文档模板

阶段1 主Agent输出以下格式的设计文档:

```markdown
# [功能名] 需求设计

## 知识库参考
设计前已查询以下官方文档:
- `official-docs/framework/XXX.md` — [用途]
- `official-docs/framework/YYY.md` — [用途]
- `official-docs/design/ZZZ.md` — [设计规范参考]

## 功能概述
[一句话描述]

## 用户故事
- 作为 [角色]，我想要 [功能]，以便 [收益]

## 功能列表
- [ ] 功能A — 参考: [官方组件/API名称]
- [ ] 功能B — 参考: [官方组件/API名称]

## 技术方案

### 组件库选择
- 基础组件: 微信原生 [列出使用的]
- 扩展组件: [WeUI / Vant Weapp / TDesign / 无]
- 自定义组件: [列出，仅组件库无法满足的部分]

### 页面: pages/xxx/xxx
  路由方式: [navigateTo/switchTab] — 参考: FRAMEWORK_INDEX#页面与路由
  使用组件: [基础:view,button] + [WeUI:mp-form] + [自定义:score-board]
### 自定义组件: components/xxx
  组件模式: [Component/Behavior] — 参考: official-docs/framework/自定义组件.md
  创建理由: [组件库中无对应组件，因为...]
### 云函数: cloudfunctions/xxx
  数据操作: [collection.add/get] — 参考: FRAMEWORK_INDEX#网络与数据
### 数据模型: [集合名/字段]
  权限: [所有用户可读/仅创建者可写]

## UI 规范 (如涉及)
- 参考: official-docs/design/ [具体页面]
- 字体/色板/间距: [引用设计规范值]

## 验收标准
- [ ] 标准A
- [ ] 标准B
```
