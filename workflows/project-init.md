# 项目初始化工作流

从零创建微信小程序项目。收集需求 → 脚手架生成 → 验收交付。

## 流程

```
用户: "创建一个小程序项目" / "初始化小程序"
  │
  ├─ ► 阶段1: 信息收集 [主Agent]
  │     1. 收集项目配置
  │        - 项目名称、路径
  │        - AppID（或使用测试号）
  │        - TypeScript / SCSS / Less
  │        - 云开发
  │        - 组件库选型
  │     2. 搜索: `python tools/search_docs.py "小程序项目结构 目录配置" --top 5`
  │     3. 加载搜索命中文档 + FRAMEWORK_INDEX.md
  │     4. 展示配置摘要 → 等用户确认
  │     决策: 用户确认 → 阶段2
  │
  ├─ ► 阶段2: 项目脚手架生成 [子Agent: project-scaffold]
  │     输入: { projectPath, projectName, appId, options }
  │     加载: agents/project-scaffold.md
  │           reference: ["official-docs/framework/目录结构.md"]
  │     子Agent执行:
  │     - 创建目录结构
  │     - 生成 app.js / app.json / app.wxss
  │     - 生成 project.config.json
  │     - 生成首页 pages/index/
  │     - 按需: tsconfig.json / 云函数 / 组件库 / jest
  │     - 生成 .gitignore
  │     决策: 脚手架成功 → 阶段3, 否则报错返回
  │
  └─ ► 阶段3: 验收交付 [主Agent]
        1. 展示创建的文件清单
        2. 输出后续步骤
        3. 输出完成报告
```

---

## 阶段1: 信息收集

### 主Agent动作

1. 询问用户项目基础信息
2. 执行 `python tools/search_docs.py "小程序项目结构 目录配置" --top 5` 搜索相关文档
3. 加载 `official-docs/FRAMEWORK_INDEX.md` 和 `official-docs/framework/目录结构.md` 了解小程序项目规范
3. 展示配置摘要给用户确认

### 信息收集清单

```markdown
## 项目配置收集

### 必填
- [ ] 项目名称（英文，小写+连字符，如 `my-miniapp`）
- [ ] 项目存放路径（绝对路径，如 `D:/projects/my-miniapp`）

### 选填（有默认值）
- [ ] AppID: 正式 AppID 或留空使用测试号 (touristappid)
- [ ] TypeScript: `true` | `false` — 默认 `false`
- [ ] 样式语言: `wxss` | `scss` | `less` — 默认 `wxss`
- [ ] 云开发: `true` | `false` — 默认 `false`
- [ ] 组件库: `无` | `weui` | `vant` | `tdesign` — 默认 `无`
```

### 组件库选型参考

| 组件库 | 包名 | 特点 | 推荐场景 |
|--------|------|------|---------|
| 微信原生 | 无需安装 | view/button/input/scroll-view/swiper... | 简单项目，组件需求少 |
| WeUI | `weui-miniprogram` | 微信官方扩展，风格统一 | 需要微信原生风格 |
| Vant Weapp | `@vant/weapp` | 社区最活跃，70+组件 | 电商/表单密集型 |
| TDesign | `tdesign-miniprogram` | 腾讯设计体系 | 企业级/数据密集型 |

### 配置摘要模板（展示给用户确认）

```markdown
## 项目配置摘要

| 配置项 | 值 |
|--------|-----|
| 项目名称 | my-miniapp |
| 项目路径 | D:/projects/my-miniapp |
| AppID | touristappid（测试号） |
| TypeScript | 否 |
| 样式 | wxss |
| 云开发 | 是 |
| 组件库 | vant (@vant/weapp) |

确认以上配置开始创建项目？(yes/no)
```

### 决策点

- 用户确认 → 阶段2
- 用户修改 → 更新配置后重新展示摘要
- 用户取消 → 终止工作流

---

## 阶段2: 项目脚手架生成

### 知识加载

子Agent启动时自动加载:
- `agents/project-scaffold.md` — 脚手架Agent定义
- `reference: ["official-docs/framework/目录结构.md"]` — 官方目录结构规范

### 传递子Agent

```
task: "project-scaffold"
projectPath: "D:/projects/my-miniapp"
projectName: "my-miniapp"
appId: "wx1234567890abcdef"    (或 "touristappid" 使用测试号)
options: {
  typescript: false,
  css: "wxss",
  cloud: true,
  componentLib: "vant"          (或 null 不安装)
}
reference: ["official-docs/framework/目录结构.md"]
```

### 子Agent执行内容

1. 创建标准目录结构（pages/, components/, utils/, tests/, 按需 cloudfunctions/）
2. 生成 app.js / app.json / app.wxss（默认框架内容）
3. 生成 project.config.json（含 AppID 和云函数根目录配置）
4. 生成首页 pages/index/index.{js,wxml,wxss,json}
5. TypeScript → 生成 tsconfig.json + 类型声明文件
6. 云开发 → 创建 cloudfunctions/ 目录 + 示例云函数 hello/
7. 组件库 → `npm init -y` + `npm install <lib>` + 使用说明
8. 生成 tests/ 目录 + jest.config.js（如不存在）
9. 生成 .gitignore

### 预期输出结构

```json
{
  "status": "success",
  "summary": "已创建项目 my-miniapp: 目录结构+配置+首页",
  "filesCreated": [
    "app.js",
    "app.json",
    "app.wxss",
    "pages/index/index.js",
    "pages/index/index.wxml",
    "pages/index/index.wxss",
    "pages/index/index.json",
    "project.config.json",
    "package.json",
    ".gitignore",
    "tests/setup.js",
    "jest.config.js"
  ],
  "keyFindings": [],
  "testResults": null,
  "projectReady": true,
  "nextSteps": [
    "npm install",
    "用微信开发者工具打开项目",
    "如启用云开发: 在开发者工具中点击'云开发'开通",
    "如使用组件库: npm run build-npm"
  ]
}
```

### 决策点

- `status: "success"` → 阶段3
- `status: "error"` → 向用户报告错误，终止

---

## 阶段3: 验收交付

### 主Agent动作

1. 解析子Agent返回的 `filesCreated` 列表
2. 解析子Agent返回的 `nextSteps`
3. 展示文件清单和后续步骤
4. 输出完成报告

### 文件清单展示

```markdown
## 创建的文件

### 根目录 (7个)
- `app.js` — 小程序入口
- `app.json` — 全局配置
- `app.wxss` — 全局样式
- `project.config.json` — 开发者工具配置
- `package.json` — 依赖管理
- `.gitignore` — Git忽略规则
- `jest.config.js` — 测试配置

### 页面 (4个)
- `pages/index/index.js`
- `pages/index/index.wxml`
- `pages/index/index.wxss`
- `pages/index/index.json`

### 工具与测试 (2个)
- `tests/setup.js`
- ... (按需扩展)
```

### 后续步骤

```markdown
## 下一步

1. **安装依赖**: 在项目目录运行 `npm install`
2. **打开项目**: 用微信开发者工具打开项目目录
3. **填写 AppID**: 如有正式 AppID，在 project.config.json 中替换 touristappid
4. **[云开发]**: 在开发者工具中点击"云开发"开通环境
5. **[组件库]**: 运行 `npm run build-npm` 构建 npm 包
6. **[TypeScript]**: 确认 tsconfig.json 编译配置
7. **开始开发**: 使用 `feature-dev` 工作流开发功能模块
```

---

## 完成报告模板

```markdown
# 项目初始化完成报告

## 项目信息
| 项目名称 | my-miniapp |
| 项目路径 | D:/projects/my-miniapp |
| AppID | wx1234567890abcdef |
| 技术栈 | JS + wxss + 云开发 + Vant Weapp |

## 文件统计
| 类型 | 数量 |
|------|------|
| 配置文件 | 5 |
| 页面文件 | 4 |
| 云函数 | 1 (示例) |
| 测试文件 | 2 |
| **合计** | **12** |

## 组件库
- 基础: 微信原生组件 (view/button/input/...)
- 扩展: Vant Weapp (@vant/weapp)

## 云开发
- 已启用
- 云函数目录: cloudfunctions/
- 示例函数: hello

## TypeScript
- 未启用 (使用 JavaScript)

## 后续步骤
1. `npm install` — 安装依赖
2. 微信开发者工具打开项目
3. 云开发: 在开发者工具中开通环境
4. `npm run build-npm` — 构建组件库

## 状态: ✅ 项目初始化完成
```
