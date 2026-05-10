# 自定义组件开发工作流

多Agent协作的自定义组件开发流程。从需求分析到验收，生成完整的组件四件套（JS/WXML/WXSS/JSON）和单元测试。

## 流程

```
用户: "开发一个XXX组件"
  │
  ├─ ► 阶段1: 需求分析与设计 [子Agent: requirement-designer]
  │     输入: { projectPath, requirement }
  │     加载: agents/requirement-designer.md
  │          + official-docs/framework/自定义组件.md
  │          + official-docs/FRAMEWORK_INDEX.md
  │     输出: designDoc { overview, componentLib, pages[], components[], acceptance[] }
  │     重点: 定义组件 properties, events, slots, styleIsolation
  │     决策: 用户确认设计文档 → 阶段2, 否则修改重来
  │
  ├─ ► 阶段2: UI骨架构建 [子Agent: ui-page-builder]
  │     输入: { designDoc.pages, designDoc.components, designDoc.componentLib }
  │     加载: agents/ui-page-builder.md
  │          + official-docs/framework/WXML_模板.md
  │          + official-docs/design/设计.md
  │          + 组件库文档（如使用 WeUI/Vant/TDesign）
  │     输出: WXML/WXSS/JSON 骨架文件 + app.json 更新
  │     约束: 只生成 UI 骨架，不写业务逻辑 JS
  │     决策: UI文件生成成功 → 阶段3
  │
  ├─ ► 阶段3: 逻辑实现+UT [子Agent: code-implementation]
  │     输入: { designDoc, context: { uiOutput } }
  │     加载: agents/code-implementation.md
  │          + official-docs/framework/自定义组件.md
  │          + official-docs/framework/behaviors.md
  │          + references/unit-test.md
  │     TDD: 写UT → 失败 → 实现Component() → 通过 → 重构
  │     实现内容:
  │     - Component({ properties, data, methods, lifetimes })
  │     - 事件触发 (this.triggerEvent)
  │     - 插槽渲染逻辑
  │     - 样式隔离配置 (styleIsolation)
  │     决策: UT全部通过 → 阶段4, 否则修复
  │
  └─ ► 阶段4: 组件验收 [主Agent]
        加载: official-docs/framework/自定义组件.md
        检查清单:
        1. properties 类型/默认值/observer 正确
        2. events 触发时机和参数正确
        3. slots 渲染逻辑正确
        4. styleIsolation 隔离有效
        5. UT 覆盖 properties/events/slots/lifetimes
        输出: 组件验收报告
```

---

## 阶段1: 需求分析与设计

### 主Agent动作

1. 收集用户需求描述和项目路径
2. 启动子Agent: `requirement-designer`

### 知识加载

子Agent启动时自动加载:
- `agents/requirement-designer.md` — 需求设计Agent定义
- `official-docs/FRAMEWORK_INDEX.md` — 框架索引
- `official-docs/framework/自定义组件.md` — 组件开发规范

### 传递子Agent

```
task: "requirement-designer"
projectPath: "D:/projects/my-miniapp"
requirement: "开发一个评分组件 score-board，支持星级展示、半星、点击打分、只读模式"
reference: [
  "official-docs/framework/自定义组件.md",
  "official-docs/FRAMEWORK_INDEX.md"
]
```

### 设计重点: 组件规范定义

子Agent必须在设计文档中明确定义以下组件契约:

```markdown
### 组件: components/score-board/score-board

| 属性 | 说明 |
|------|------|
| **名称** | score-board |
| **路径** | components/score-board/score-board |
| **创建理由** | 组件库中无评分组件（WeUI/Vant/TDesign 均无原生评分组件） |

#### Properties
| 属性名 | 类型 | 默认值 | 说明 | observer |
|--------|------|--------|------|----------|
| max | Number | 5 | 最大星数 | - |
| value | Number | 0 | 当前分值（支持小数表示半星） | - |
| readonly | Boolean | false | 只读模式 | - |
| size | Number | 28 | 星星大小(rpx) | - |
| color | String | "#FFD700" | 高亮颜色 | - |

#### Events
| 事件名 | 触发时机 | 参数 |
|--------|---------|------|
| change | 用户点击星星改变分值 | { value: Number } |
| select | 用户点击确认（场景：弹窗中评分完成后） | { value: Number } |

#### Slots
| 插槽名 | 说明 |
|--------|------|
| default | 默认插槽：分值文本自定义（如 "4.2分"） |

#### 样式
| 配置 | 值 |
|------|-----|
| styleIsolation | isolated（默认，样式隔离） |
| externalClasses | []（无外部样式类需求） |
```

### 组件设计验证问题（展示给用户）

```
确认以下问题：
1. properties 类型和默认值是否合理？
2. events 触发时机是否符合使用场景？
3. 是否需要额外插槽？（当前仅 default）
4. 样式隔离策略是否正确？
5. 是否需要 behaviors 复用逻辑？
```

### 决策点

- 用户确认 → 阶段2
- 用户修改 → 更新设计文档后重新确认

---

## 阶段2: UI骨架构建

### 主Agent动作

1. 从阶段1获取 `designDoc.pages`, `designDoc.components`, `designDoc.componentLib`
2. 启动子Agent: `ui-page-builder`
3. 子Agent只创建 WXML/WXSS/JSON，不写业务逻辑

### 知识加载

子Agent启动时自动加载:
- `agents/ui-page-builder.md` — UI构建Agent定义
- `official-docs/framework/WXML_模板.md` — WXML语法规范
- `official-docs/design/设计.md` — 设计规范
- 组件库文档（根据 designDoc.componentLib 动态加载）

### 传递子Agent

```
task: "ui-page-builder"
projectPath: "D:/projects/my-miniapp"
scope: ["components/score-board/"]
context: {
  designDoc: {
    pages: [],
    components: [
      {
        path: "components/score-board/score-board",
        name: "score-board",
        reason: "组件库无评分组件",
        properties: [
          { name: "max", type: "Number", default: 5 },
          { name: "value", type: "Number", default: 0 },
          { name: "readonly", type: "Boolean", default: false },
          { name: "size", type: "Number", default: 28 },
          { name: "color", type: "String", default: "#FFD700" }
        ],
        events: [
          { name: "change", detail: { value: "Number" } },
          { name: "select", detail: { value: "Number" } }
        ],
        slots: ["default"],
        styleIsolation: "isolated"
      }
    ],
    componentLib: { base: ["view", "image", "text"], extended: null, custom: ["score-board"] }
  }
}
reference: [
  "official-docs/framework/WXML_模板.md",
  "official-docs/design/设计.md"
]
```

### 预期生成文件

```json
{
  "filesCreated": [
    "components/score-board/score-board.wxml",
    "components/score-board/score-board.wxss",
    "components/score-board/score-board.json",
    "components/score-board/score-board.js"
  ],
  "filesChanged": []
}
```

> **注意**: `score-board.js` 仅生成 `Component({})` 骨架，由阶段3填充。

### UI骨架内容要点

**score-board.wxml**:
```xml
<view class="score-board" data-testid="score-board">
  <block wx:for="{{stars}}" wx:key="index">
    <image
      class="star {{readonly ? 'readonly' : ''}}"
      src="{{item.icon}}"
      data-index="{{index}}"
      data-testid="star-{{index}}"
      style="width: {{size}}rpx; height: {{size}}rpx;"
      bindtap="{{readonly ? '' : 'onStarTap'}}"
    />
  </block>
  <slot />
</view>
```

**score-board.wxss**:
```css
.score-board {
  display: flex;
  align-items: center;
  gap: 4rpx;
}

.star {
  transition: transform 0.15s ease;
}

.star:not(.readonly):active {
  transform: scale(1.15);
}
```

**score-board.json**:
```json
{
  "component": true,
  "styleIsolation": "isolated",
  "usingComponents": {}
}
```

### 决策点

- 文件生成成功且无错误 → 阶段3
- 生成失败 → 报告错误，重新执行或终止

---

## 阶段3: 逻辑实现+UT

### 主Agent动作

1. 收集: `designDoc`（阶段1）+ `uiOutput`（阶段2文件清单）
2. 启动子Agent: `code-implementation`

### 知识加载

子Agent启动时自动加载:
- `agents/code-implementation.md` — 代码实现Agent定义
- `official-docs/framework/自定义组件.md` — 组件开发规范
- `official-docs/framework/behaviors.md` — behaviors 复用
- `references/unit-test.md` — 单元测试规范

### 传递子Agent

```
task: "code-implementation"
projectPath: "D:/projects/my-miniapp"
scope: ["components/score-board/"]
context: {
  designDoc: {
    overview: "评分组件，支持星级展示、半星、点击打分、只读模式",
    knowledgeRefs: [
      "official-docs/framework/自定义组件.md"
    ],
    components: [
      {
        path: "components/score-board/score-board",
        properties: [
          { name: "max", type: "Number", default: 5 },
          { name: "value", type: "Number", default: 0 },
          { name: "readonly", type: "Boolean", default: false },
          { name: "size", type: "Number", default: 28 },
          { name: "color", type: "String", default: "#FFD700" }
        ],
        events: [
          { name: "change", detail: { value: "Number" } },
          { name: "select", detail: { value: "Number" } }
        ],
        slots: ["default"],
        styleIsolation: "isolated"
      }
    ]
  },
  uiOutput: {
    filesCreated: [
      "components/score-board/score-board.wxml",
      "components/score-board/score-board.wxss",
      "components/score-board/score-board.json",
      "components/score-board/score-board.js"
    ]
  }
}
reference: [
  "official-docs/framework/自定义组件.md",
  "official-docs/framework/behaviors.md",
  "references/unit-test.md"
]
```

### TDD 实现循环

```
1. 写 UT (tests/components/score-board.test.js)
   ├─ properties 测试: 默认值、类型校验、observer 回调
   ├─ events 测试: change 触发参数、select 触发参数
   ├─ slots 测试: default 插槽渲染
   ├─ methods 测试: 半星计算、边界值 max=10
   └─ lifetimes 测试: attached 初始化 starred 列表

2. 运行测试 → 全部失败（Red）

3. 实现 Component() 逻辑
   ├─ properties 定义（类型、默认值、observer）
   ├─ data: { stars: [] }
   ├─ lifetimes.attached(): 计算 stars 数组（全星/半星/空星）
   ├─ methods.onStarTap(e): 处理点击 → 计算分值 → triggerEvent('change')
   └─ methods: 辅助函数（getStarType, clampValue）

4. 运行测试 → 全部通过（Green）

5. 重构代码（Refactor）
   ├─ 提取通用计算逻辑
   └─ 运行测试 → 仍全通过
```

### 预期 UT 覆盖清单

```markdown
## 组件 UT 覆盖

### Properties
- [ ] max 默认值为 5
- [ ] value 默认值为 0
- [ ] readonly 默认值为 false
- [ ] size 默认值为 28
- [ ] color 默认值为 "#FFD700"

### Events
- [ ] 点击第3颗星 → triggerEvent('change', { value: 3 })
- [ ] readonly=true 时点击不触发事件
- [ ] 点击半星 → 正确计算 .5 分值

### Slots
- [ ] default 插槽内容正确渲染
- [ ] 自定义分值文本通过 slot 显示

### Lifetimes
- [ ] attached: stars 数组长度等于 max
- [ ] 初始 value=3.5 → stars 包含 3全星+1半星+1空星

### 边界
- [ ] value=0 → 全部空星
- [ ] value=max → 全部满星
- [ ] value>max → clamp 到 max
- [ ] value<0 → clamp 到 0
- [ ] max=10 → 10颗星
```

### 决策点

- UT 全部通过 → 阶段4
- 有失败用例 → 报告给主Agent，迭代修复

---

## 阶段4: 组件验收

### 主Agent动作

1. 收集阶段3实现结果
2. 加载 `official-docs/framework/自定义组件.md` 对照验收
3. 执行组件验收检查清单
4. 输出验收报告

### 知识加载

- `official-docs/framework/自定义组件.md` — 组件开发规范（验收对照）

### 组件验收检查清单

```markdown
## 组件验收: score-board

### 1. Properties 验证
- [ ] 属性名与设计文档一致
- [ ] type 定义正确（Number/Boolean/String/Array/Object）
- [ ] value 提供合理默认值
- [ ] observer 存在且逻辑正确（如有）
- [ ] optionalTypes 声明（TypeScript 项目）

### 2. Events 验证
- [ ] triggerEvent 事件名与设计一致
- [ ] detail 参数结构正确
- [ ] bubbles/composed 配置合理
- [ ] 事件触发时机符合文档描述
- [ ] 事件在预期生命周期阶段触发

### 3. Slots 验证
- [ ] 所有声明的插槽在 WXML 中定义
- [ ] 插槽名称与设计一致
- [ ] 插槽有合理默认内容（如适用）
- [ ] 多插槽模式配置正确（`multipleSlots: true`）

### 4. 样式隔离验证
- [ ] styleIsolation 配置正确
- [ ] 组件内部样式不被外部覆盖（isolated）
- [ ] 组件样式不透出影响外部（isolated）
- [ ] externalClasses 声明（如需要）
- [ ] 尺寸使用 rpx 单位
- [ ] 主题色通过 properties 传入，不硬编码

### 5. 单元测试验证
- [ ] 测试文件位置：tests/components/<name>.test.js
- [ ] Properties 默认值测试通过
- [ ] Events 触发测试通过
- [ ] Slots 渲染测试通过
- [ ] Lifetimes 回调测试通过
- [ ] 边界值测试通过
- [ ] 测试覆盖率 ≥ 80%

### 6. 文件完整性
- [ ] .js — Component() 定义完整
- [ ] .wxml — 模板语义化 + data-testid
- [ ] .wxss — 样式隔离 + rpx 单位
- [ ] .json — `"component": true` + usingComponents
- [ ] tests/<name>.test.js — UT 覆盖

### 7. 代码质量
- [ ] 无 console.log 调试代码
- [ ] methods 命名语义化（onStarTap 而非 tap1）
- [ ] 复杂计算提取为独立函数
- [ ] 有合理的注释（为什么而非是什么）
- [ ] data-testid 覆盖关键交互元素
```

### 验收报告模板

```markdown
# 组件开发完成报告

## 组件: score-board
## 路径: components/score-board/score-board
## 耗时: X分钟

## 设计回顾
- 类型: 自定义组件（组件库无对应组件）
- Properties: max, value, readonly, size, color (5个)
- Events: change, select (2个)
- Slots: default (1个)
- styleIsolation: isolated

## 文件清单
| 文件 | 大小 | 说明 |
|------|------|------|
| score-board.js | 2.1KB | Component() 逻辑实现 |
| score-board.wxml | 0.8KB | 星星模板 (data-testid) |
| score-board.wxss | 0.5KB | 隔离样式 (rpx) |
| score-board.json | 0.1KB | component:true |
| tests/score-board.test.js | 3.2KB | 15个用例 |

## 测试结果
| 类别 | 通过 | 失败 | 覆盖率 |
|------|------|------|--------|
| Properties 测试 | 5 | 0 | 100% |
| Events 测试 | 3 | 0 | 100% |
| Slots 测试 | 2 | 0 | 100% |
| Lifetimes 测试 | 2 | 0 | 100% |
| 边界测试 | 3 | 0 | 100% |
| **合计** | **15** | **0** | **92%** |

## 验收检查清单
| 类别 | 状态 |
|------|------|
| Properties | ✅ 5个属性全部验收通过 |
| Events | ✅ 2个事件触发正确 |
| Slots | ✅ default 插槽渲染正确 |
| 样式隔离 | ✅ isolated 模式生效 |
| 单元测试 | ✅ 15/15 通过，覆盖率92% |
| 文件完整性 | ✅ 四件套+测试齐全 |
| 代码质量 | ✅ 无调试代码，命名规范 |

## 使用示例

```xml
<!-- 只读模式 -->
<score-board value="{{3.5}}" readonly="{{true}}" />

<!-- 可交互模式 -->
<score-board
  max="{{5}}"
  value="{{rating}}"
  bind:change="onRatingChange"
  bind:select="onRatingConfirm"
>
  <text>{{rating}}分</text>
</score-board>
```

## 状态: ✅ 组件验收通过
```

---

## 常见场景速查

### 纯展示组件

```
阶段1 → designDoc.components[].readonly 始终 true
阶段2 → 无点击事件绑定
阶段3 → 跳过事件相关 UT，专注 properties + slots
阶段4 → 检查清单跳过 events 项
```

### 表单控件组件

```
阶段1 → 定义双向绑定模式（value + bind:change）
阶段2 → 表单控件 WXML 模式（label + input/textarea）
阶段3 → 补充表单校验逻辑 UT
阶段4 → 增加"表单提交"集成测试
```

### 容器/布局组件

```
阶段1 → 定义多个 slots（header/content/footer）
阶段2 → WXML 中声明 multipleSlots: true
阶段3 → 专注 slots 渲染逻辑
阶段4 → 增加"嵌套子组件"验收
```

---

## 错误处理

| 场景 | 处理 |
|------|------|
| requirement-designer 设计文档缺少组件 contracts | 补充 properties/events/slots 定义后重试 |
| ui-page-builder WXML/WXSS 生成失败 | 检查组件库模式表匹配，切换集成方式重试（最多2次） |
| code-implementation TDD 循环失败（3次迭代后仍有失败） | 报告主Agent，展示失败日志，等待决策（继续/跳过/修改设计） |
| 组件间样式冲突（styleIsolation 未生效） | 检查 styleIsolation 配置，添加 externalClasses 或调整为 isolated 模式 |
| 组件注册后页面报 "Component not found" | 检查页面 .json 的 usingComponents 注册路径 |
| 验收阶段组件与设计文档不一致 | 更新设计文档标注偏差，评估是否需要修复 |
