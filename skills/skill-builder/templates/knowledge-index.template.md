# {{DOMAIN}} 官方文档索引

> 来源: {{OFFICIAL_DOC_URL}}
> 爬取时间: {{CRAWL_DATE}}
> 总页面: {{TOTAL_PAGES}} ({{CATEGORY_BREAKDOWN}})

## 按开发场景索引

### {{SCENARIO_1}}
- [{{DOC_TITLE_1}}]({{DOC_PATH_1}})
- [{{DOC_TITLE_2}}]({{DOC_PATH_2}})

### {{SCENARIO_2}}
- [{{DOC_TITLE_3}}]({{DOC_PATH_3}})
- [{{DOC_TITLE_4}}]({{DOC_PATH_4}})

### {{SCENARIO_3}}
- [{{DOC_TITLE_5}}]({{DOC_PATH_5}})

### {{SCENARIO_4}}
- [{{DOC_TITLE_6}}]({{DOC_PATH_6}})
- [{{DOC_TITLE_7}}]({{DOC_PATH_7}})

---

## 索引使用指南

### 与语义搜索的关系

| 工具 | 用途 | 场景 |
|------|------|------|
| `search_docs.py` | **语义搜索**（主要方式） | 90%的查询场景 |
| 本索引文件 | 索引浏览（辅助） | 浏览全貌、确认遗漏 |

### 流程

```
用户需求 → 提取关键词 → search_docs.py → 加载命中文档
                                    ↓
                            相关度不理想 → 查本索引 → 加载邻近文档
```

---

## 占位符说明

| 占位符 | 含义 | 示例 |
|--------|------|------|
| `{{DOMAIN}}` | 领域名 | `鸿蒙 ArkTS` |
| `{{OFFICIAL_DOC_URL}}` | 官方文档首页 URL | `https://developer.huawei.com/...` |
| `{{CRAWL_DATE}}` | 文档爬取日期 | `2026-05-11` |
| `{{TOTAL_PAGES}}` | 总页面数 | `250` |
| `{{CATEGORY_BREAKDOWN}}` | 分类统计 | `200 framework + 30 api + 20 design` |
| `{{SCENARIO_N}}` | 开发场景分类 | `项目初始化`, `UI组件`, `网络与数据` |
| `{{DOC_PATH_N}}` | 文档文件路径 | `framework/组件生命周期.md` |
