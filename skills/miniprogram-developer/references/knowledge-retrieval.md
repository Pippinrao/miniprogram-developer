# 知识检索指南

所有子Agent共享的官方文档检索参考。使用**语义搜索优先**的策略获取最相关的官方文档。

## 语义搜索工具

```bash
python tools/search_docs.py "<搜索关键词>" [选项]
```

### 选项

| 选项 | 说明 | 示例 |
|------|------|------|
| `--top 5` | 返回结果数（默认5） | `--top 10` |
| `--category design` | 按分类过滤: `framework` / `design` | `--category design` |
| `--json` | JSON格式输出（便于程序解析） | `--json` |

### 搜索结果解读

每条结果包含:
- **source_file**: 官方文档路径（如 `framework/组件生命周期.md`）→ 用 Read 加载此文件
- **score**: 余弦相似度（0~1，越高越相关）
- **title/section**: 文档/章节标题
- **source_url**: 原始官网URL（可 WebFetch 获取最新版）
- **content**: 文档内容片段（前500字符）

## 搜索技巧

### 1. 中文关键词效果最好

嵌入模型 BGE-large-zh-v1.5 专为中文优化。使用自然中文短语搜索，不要用单个英文字母或缩写。

```
✓ python tools/search_docs.py "自定义组件的生命周期 created attached detached"
✗ python tools/search_docs.py "component lifecycle"
```

### 2. 分类过滤

当明确需要框架API文档或设计规范时，用 `--category` 过滤提高精度:

```bash
# 框架API文档
python tools/search_docs.py "路由跳转" --category framework

# 设计规范
python tools/search_docs.py "颜色 字体 间距" --category design
```

### 3. 搜索失败时的回退

如果搜索结果相关度都 < 0.3，说明关键词不够精准:

1. **调整关键词**: 用更具体的术语重新搜索
2. **查阅索引**: 加载 `official-docs/FRAMEWORK_INDEX.md` 浏览全貌
3. **扩展搜索**: 减少 --top 返回更多结果再人工筛选

## 与 FRAMEWORK_INDEX.md 的关系

| 工具 | 用途 | 场景 |
|------|------|------|
| `search_docs.py` | **语义搜索**（主要方式） | 90%的查询场景 |
| `FRAMEWORK_INDEX.md` | 索引浏览（辅助） | 浏览全貌、确认遗漏 |

**流程**:
```
用户需求 → 提取关键词 → search_docs.py → 加载命中文档
                                      ↓
                              相关度不理想 → 查 FRAMEWORK_INDEX.md → 加载邻近文档
```

## 谁负责搜索

| 角色 | 职责 |
|------|------|
| **主Agent** | 初始搜索: 从用户需求/错误信息中提取关键词，执行 `search_docs.py`，将命中路径通过 `searchResults` 传给子Agent |
| **子Agent** | 补充搜索: 如果传入的 `searchResults` 不足或覆盖不全，可自行执行 `search_docs.py` 补充搜索 |

**子Agent执行搜索时的注意事项:**
- `search_docs.py` 路径: `miniprogram-developer/tools/search_docs.py`
- 需从 tools/ 目录或指定 --db-dir 运行
- 用 `--json` 获取结构化结果便于解析

## BGE 嵌入模型说明

- **模型**: BAAI/bge-large-zh-v1.5（1024维）
- **语言**: 专为中文优化
- **运行**: 本地CPU推理，无需网络（首次运行自动下载模型，约1.3GB）
- **查询时**: 自动添加 BGE 查询前缀，无需手动处理
- **存储**: ChromaDB 余弦相似度索引

## 故障排查

| 问题 | 原因 | 解决 |
|------|------|------|
| `ModuleNotFoundError: No module named 'chromadb'` | 依赖未安装 | `pip install -r tools/requirements.txt` |
| 首次运行卡住/慢 | 正在下载 BGE 模型（~1.3GB） | 等待下载完成；后续离线运行 |
| HF Hub 限流警告 | 未设置 HF_TOKEN | `export HF_TOKEN=your_token` 或忽略（限流下仍可下载） |
| `Collection not found` | ChromaDB 索引未构建 | 运行 `python tools/embed_docs.py` 构建索引 |
| 搜索结果得分都 < 0.3 | 关键词不精准 | 调整关键词，用更具体的术语重试 |
| `search_docs.py` 执行失败 | Python 版本 < 3.10 | 升级到 Python 3.10+ |
| ChromaDB 版本不兼容 | 升级后索引格式变化 | 删除 `tools/chroma_db/` 目录后重新运行 `embed_docs.py` |
