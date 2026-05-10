"""
微信小程序文档语义搜索工具

在已向量化的官方文档中执行语义搜索，返回最相关的结果。

用法:
    python search_docs.py "Skyline 渲染引擎的优势"
    python search_docs.py "组件生命周期" --top 10
    python search_docs.py "路由配置" --category framework
"""

import os

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

import argparse
import json
import sys
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


BGE_QUERY_PREFIX = "为这个句子生成表示以用于检索相关文章："
COLLECTION_NAME = "wechat_miniprogram_docs"


def find_db_dir(script_dir: Path) -> Path:
    """查找 ChromaDB 存储目录"""
    candidates = [
        script_dir / "chroma_db",
        script_dir.parent / "tools" / "chroma_db",
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError(
        f"未找到 ChromaDB 索引目录。请先运行 embed_docs.py 构建索引。\n"
        f"已尝试: {[str(c) for c in candidates]}"
    )


def format_result_markdown(result: dict, idx: int) -> str:
    """将单条结果格式化为 Markdown"""
    meta = result.get("metadata", {})
    source = meta.get("source_file", "unknown")
    title = meta.get("title", "无标题")
    section = meta.get("section", "")
    category = meta.get("category", "")
    url = meta.get("source_url", "")
    score = result.get("distance", 0)
    content = result.get("document", "")[:500]

    lines = [f"### 结果 {idx} — 相关度: {score:.4f}"]
    lines.append(f"- **文档**: {source}")
    lines.append(f"- **分类**: {category}")
    lines.append(f"- **标题**: {title}")
    if section:
        lines.append(f"- **章节**: {section}")
    if url:
        lines.append(f"- **来源**: {url}")
    lines.append(f"")
    lines.append(f"```")
    lines.append(content)
    lines.append(f"```")
    lines.append(f"")
    return "\n".join(lines)


def format_result_json(results: list) -> str:
    """将结果格式化为 JSON"""
    output = []
    for r in results:
        output.append(
            {
                "score": r.get("distance", 0),
                "source_file": r.get("metadata", {}).get("source_file", ""),
                "category": r.get("metadata", {}).get("category", ""),
                "title": r.get("metadata", {}).get("title", ""),
                "section": r.get("metadata", {}).get("section", ""),
                "source_url": r.get("metadata", {}).get("source_url", ""),
                "content": r.get("document", ""),
            }
        )
    return json.dumps(output, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="微信小程序文档语义搜索",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python search_docs.py "Skyline 渲染引擎的优势"
  python search_docs.py "组件生命周期" --top 10
  python search_docs.py "路由配置" --category framework
  python search_docs.py "无障碍设计规范" --json
        """,
    )
    parser.add_argument("query", type=str, help="搜索查询（中文）")
    parser.add_argument(
        "--top", "-k", type=int, default=5, help="返回结果数量（默认: 5）"
    )
    parser.add_argument(
        "--category",
        "-c",
        type=str,
        default=None,
        choices=["framework", "design"],
        help="按分类过滤",
    )
    parser.add_argument(
        "--db-dir",
        type=str,
        default=None,
        help="ChromaDB 存储目录（默认自动查找）",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="BAAI/bge-large-zh-v1.5",
        help="嵌入模型名称（需与 embed_docs.py 一致）",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        default=True,
        help="离线模式，不检查 HuggingFace 更新（默认启用）",
    )
    parser.add_argument(
        "--json", "-j", action="store_true", help="以 JSON 格式输出"
    )
    args = parser.parse_args()

    script_dir = Path(__file__).parent.resolve()
    db_dir = Path(args.db_dir) if args.db_dir else find_db_dir(script_dir)

    print(f"[INFO] 加载嵌入模型: {args.model}", file=sys.stderr)
    model_kwargs = {}
    if args.offline:
        model_kwargs["local_files_only"] = True
    model = SentenceTransformer(args.model, **model_kwargs)

    print(f"[INFO] 连接 ChromaDB: {db_dir}", file=sys.stderr)
    client = chromadb.PersistentClient(path=str(db_dir))

    try:
        collection = client.get_collection(COLLECTION_NAME)
    except Exception:
        print(
            f"[ERROR] 未找到 collection '{COLLECTION_NAME}'。请先运行 embed_docs.py",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"[INFO] 索引共 {collection.count()} 条记录", file=sys.stderr)

    # 生成查询向量（BGE 需要查询前缀）
    query_with_prefix = f"{BGE_QUERY_PREFIX}{args.query}"
    query_embedding = model.encode(
        [query_with_prefix],
        normalize_embeddings=True,
        convert_to_numpy=True,
    )

    # 构建过滤条件
    where = None
    if args.category:
        where = {"category": args.category}

    # 搜索
    results = collection.query(
        query_embeddings=query_embedding.tolist(),
        n_results=args.top,
        where=where,
        include=["documents", "metadatas", "distances"],
    )

    # 合并结果
    formatted = []
    for i in range(len(results["ids"][0])):
        formatted.append(
            {
                "id": results["ids"][0][i],
                "document": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": 1.0
                - results["distances"][0][i],  # cosine distance → similarity
            }
        )

    # 输出
    if args.json:
        print(format_result_json(formatted))
    else:
        print(f"# 搜索: \"{args.query}\"")
        print(f"# 返回 {len(formatted)} 条结果")
        print()
        for idx, r in enumerate(formatted, 1):
            print(format_result_markdown(r, idx))


if __name__ == "__main__":
    main()
