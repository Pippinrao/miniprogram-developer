# miniprogram-developer

微信小程序全栈开发 Agent Skill — 基于语义搜索知识库的 Multi-Agent 协作开发系统。

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-1-brightgreen.svg)](https://agentskills.io)

## 特性

- **语义搜索知识库**: 约 390 个官方文档页面，396 个向量化 chunks，基于 BGE-large-zh-v1.5 + ChromaDB
- **Multi-Agent 架构**: 1 个主调度 Agent + 10 个领域专家子 Agent，协作完成需求→设计→实现→测试→验收
- **12 个开发工作流**: 覆盖项目初始化、功能开发、组件开发、云函数、测试、调试、重构、性能优化、紧急修复、知识查询、代码审查、技术选型
- **渐进式知识加载**: 搜索→定位→按需加载，避免上下文窗口爆炸
- **Context Exchange 协议**: 主Agent≤500 tokens，子Agent≤300 tokens，严格的结构化 JSON 通信

## 目录结构

```
miniprogram-developer/
├── SKILL.md                    # 核心 Skill 定义
├── agents/                     # 10 个子Agent 角色定义
├── workflows/                  # 12 个工作流定义
├── protocols/                  # 上下文交换协议
├── references/                 # 实践指南（测试/CI/CD/CLI/自动化）
├── official-docs/              # 微信官方文档知识库（约 390 页，387 个有效内容页）
│   ├── framework/              # 365 个框架文档
│   ├── design/                 # 22 个设计规范文档
│   ├── api/                    # 1 个 API 参考文档
│   ├── component/              # 2 个组件文档
│   └── FRAMEWORK_INDEX.md      # 文档索引
└── tools/                      # 语义搜索工具
    ├── embed_docs.py           # 文档向量化
    ├── search_docs.py          # 语义搜索 CLI
    └── requirements.txt        # Python 依赖
```

## 快速开始

### 安装

```bash
npx skills add Pippinrao/miniprogram-developer
```

### 构建知识库索引（首次使用）

```bash
cd miniprogram-developer/tools
pip install -r requirements.txt
python embed_docs.py
```

首次运行会下载 BGE-large-zh-v1.5 模型（~1.3GB），后续离线运行。

### 语义搜索

```bash
cd miniprogram-developer/tools
python search_docs.py "组件生命周期" --top 5
```

## 工作流

| 用户意图 | 工作流 |
|---------|--------|
| "创建项目"、"初始化小程序" | `project-init` |
| "做XXX功能"、"新增XXX" | `feature-dev` |
| "写组件"、"自定义组件" | `component-dev` |
| "写云函数" | `cloud-fn-dev` |
| "性能优化"、"太卡了" | `perf-tuning` |
| "帮我测试"、"跑测试" | `testing` |
| "有个bug"、"报错了" | `bugfix` |
| "重构XXX" | `refactor` |
| "线上挂了" | `hotfix` |
| "如何使用XXX"、"查文档" | `knowledge-lookup` |
| "帮我 review 代码"、"代码审查" | `code-review` |
| "技术选型"、"跨端对比" | `tech-selection` |

## 技术栈

| 组件 | 选型 |
|------|------|
| 嵌入模型 | BAAI/bge-large-zh-v1.5 (1024维) |
| 向量数据库 | ChromaDB (余弦相似度) |
| 分块策略 | 按 Markdown 标题 + 段落 |
| 知识来源 | 微信官方小程序开发文档 |

## 相关链接

- [微信小程序官方文档](https://developers.weixin.qq.com/miniprogram/dev/framework/) — 框架与API参考
- [微信小程序设计指南](https://developers.weixin.qq.com/miniprogram/design/) — 设计规范与无障碍
- [ChromaDB](https://www.trychroma.com/) — 向量数据库
- [BGE-large-zh-v1.5](https://huggingface.co/BAAI/bge-large-zh-v1.5) — 中文嵌入模型
- [agentskills.io](https://agentskills.io) — Agent Skills 规范与市场

## License

Apache 2.0 — 详见 [LICENSE](LICENSE)
