# 语义搜索知识库模式

## 架构

```
官方文档网站 → 爬取 → Markdown文件 → 向量化 → ChromaDB → 语义搜索
                                                    ↓
                                              关键词查询 → 返回相关文档
```

## 组件选型

| 组件 | 推荐选型 | 说明 |
|------|---------|------|
| 嵌入模型 | BGE-large-zh-v1.5 (中文) / all-MiniLM-L6-v2 (英文) | 1024维/384维，本地CPU推理 |
| 向量数据库 | ChromaDB | 余弦相似度，轻量级 |
| 分块策略 | 按标题+段落 | Markdown感知，合并短块，拆分长块 |
| 搜索接口 | Python CLI | `search_docs.py "关键词" --top N` |

## 文档采集

### 爬取策略
1. 确定官方文档的URL结构
2. 爬取所有页面，保留原始结构和代码示例
3. 每个页面存为一个 `.md` 文件
4. 记录 source_url 和爬取时间

### 目录组织
```
official-docs/
├── INDEX.md              # 按场景分类的索引
├── framework/            # 框架/架构文档
├── api/                  # API参考文档
├── design/               # 设计规范文档
└── guides/               # 实践指南
```

## 向量化流程

### 分块规则
```
1. 按 ## 标题分割
2. 块 < 200字符 → 与上一块合并
3. 块 > 1500字符 → 按段落再次分割
4. 跳过 INDEX.md 和纯导航页面
5. 每个块记录: source_file, title, section, category, source_url
```

### embed_docs.py 模板
```python
from sentence_transformers import SentenceTransformer
import chromadb
from pathlib import Path

model = SentenceTransformer('BAAI/bge-large-zh-v1.5')
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(
    name="docs",
    metadata={"hnsw:space": "cosine"}
)

# 遍历 official-docs/ 目录
# 对每个 .md 文件分块 → 向量化 → 存入 ChromaDB
```

## 搜索接口

### search_docs.py CLI
```bash
python tools/search_docs.py "查询关键词" [选项]

选项:
  --top N          返回结果数（默认5）
  --category CAT   按分类过滤
  --json           输出JSON格式
```

### 输出格式
```json
{
  "source_file": "framework/组件生命周期.md",
  "title": "组件生命周期",
  "section": "生命周期回调",
  "score": 0.78,
  "content": "文档片段...",
  "source_url": "https://..."
}
```

## 降级策略

```
语义搜索
  │
  ├─ 最高得分 ≥ 0.5 → 直接使用
  ├─ 最高得分 0.3-0.5 → 标注"信息有限"
  ├─ 最高得分 < 0.3 → 同义词重试（最多3轮）
  │     └─ 仍<0.3 → 降级为 INDEX.md 手动浏览
  │
  └─ search_docs.py 不可用 → 降级为 INDEX.md 手动查找 → 告知用户
```

## 检索指南文档

每个技能需要一份 `references/knowledge-retrieval.md`，包含：
- 搜索工具CLI用法
- 搜索结果解读
- 搜索技巧（关键词选择、分类过滤）
- 搜索失败时的回退策略
- 主Agent vs 子Agent的搜索职责

## 适配不同领域

| 领域 | 嵌入模型 | 注意 |
|------|---------|------|
| 中文为主 | BGE-large-zh-v1.5 | 查询时自动加BGE前缀 |
| 英文为主 | all-MiniLM-L6-v2 | 轻量，384维 |
| 混合中英 | BGE-large-zh-v1.5 | 对英文也有一定效果 |
| 代码为主 | CodeBERT / UniXcoder | 代码语义搜索 |

## 维护

- 定期重新爬取官方文档（建议每月）
- 重新向量化（`python embed_docs.py`）
- ChromaDB版本升级后可能需要重建索引
- 检查搜索结果质量，调整分块参数
