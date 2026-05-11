"""
微信小程序官方文档向量化工具

将 official-docs/ 下的中文 Markdown 文档分块、嵌入并存入 ChromaDB，
支持语义搜索检索。

用法:
    python embed_docs.py [--docs-dir PATH] [--db-dir PATH] [--reset]
"""

import os

os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

import argparse
import re
import sys
import time
from pathlib import Path
from typing import List, Optional, Tuple

import chromadb
from sentence_transformers import SentenceTransformer
from tqdm import tqdm


# === 配置 ===
CHUNK_MIN_CHARS = 200
CHUNK_MAX_CHARS = 1500
BATCH_SIZE = 32
COLLECTION_NAME = "wechat_miniprogram_docs"
BGE_QUERY_PREFIX = "为这个句子生成表示以用于检索相关文章："


def find_docs_dir(script_dir: Path) -> Path:
    """查找 official-docs 目录"""
    # 脚本在 tools/ 下，official-docs 在 ../official-docs/
    candidates = [
        script_dir.parent / "official-docs",
        script_dir.parent.parent / "official-docs",
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError(
        f"未找到 official-docs 目录。已尝试: {[str(c) for c in candidates]}"
    )


def extract_metadata(content: str, file_rel_path: str, category: str) -> dict:
    """从 Markdown 内容中提取元数据"""
    meta = {
        "source_file": file_rel_path,
        "category": category,
        "title": "",
        "source_url": "",
    }

    # 提取第一个 # 标题
    h1_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if h1_match:
        meta["title"] = h1_match.group(1).strip()

    # 提取来源 URL
    url_match = re.search(r"来源:\s*(https?://[^\s\n]+)", content)
    if url_match:
        meta["source_url"] = url_match.group(1).strip()

    return meta


def chunk_markdown(content: str) -> List[Tuple[str, str, str]]:
    """
    按 Markdown 标题分块，返回 [(chunk_text, h1_title, h2_section), ...]

    规则:
    - 以 # 和 ## 标题为边界切分
    - 每个 chunk 的文本包含标题行
    - 最小 200 字符（低于此值合并到上一 chunk）
    - 最大 2000 字符（超出按空行再切）
    """
    lines = content.split("\n")
    chunks = []
    current_h1 = ""
    current_h2 = ""
    current_lines = []

    def finalize_chunk(lines_list: List[str], h1: str, h2: str):
        text = "\n".join(lines_list).strip()
        if not text:
            return
        chunks.append((text, h1, h2))

    # 处理无标题的内容（第一段）
    pre_header_lines = []
    for line in lines:
        if re.match(r"^#{1,2}\s", line):
            break
        pre_header_lines.append(line)
    else:
        # 整个文件都没有标题
        if pre_header_lines:
            _split_long_chunk("\n".join(pre_header_lines).strip(), "", "", chunks)
        return chunks

    if pre_header_lines:
        pre_text = "\n".join(pre_header_lines).strip()
        if pre_text:
            _split_long_chunk(pre_text, "", "", chunks)

    # 跳过已处理的前导行
    start_idx = len(pre_header_lines)

    for line in lines[start_idx:]:
        h1_match = re.match(r"^#\s+(.+)", line)
        h2_match = re.match(r"^##\s+(.+)", line)

        if h1_match or h2_match:
            # 保存当前 chunk
            if current_lines:
                finalize_chunk(current_lines, current_h1, current_h2)
                current_lines = []

            if h1_match:
                current_h1 = h1_match.group(1).strip()
                current_h2 = ""  # 新的 h1 重置 h2
            elif h2_match:
                current_h2 = h2_match.group(1).strip()

        current_lines.append(line)

    # 最后一个 chunk
    if current_lines:
        finalize_chunk(current_lines, current_h1, current_h2)

    # 合并过短的 chunk
    merged = _merge_short_chunks(chunks)
    return merged


def _split_long_chunk(
    text: str, h1: str, h2: str, output: list
) -> None:
    """将过长文本按段落切分"""
    if len(text) <= CHUNK_MAX_CHARS:
        if len(text) >= CHUNK_MIN_CHARS or not output:
            output.append((text, h1, h2))
        else:
            # 与上一个合并
            prev_text, prev_h1, prev_h2 = output[-1]
            output[-1] = (prev_text + "\n\n" + text, prev_h1, prev_h2)
        return

    # 按空行切段落
    paragraphs = re.split(r"\n\s*\n", text)
    current = ""
    for para in paragraphs:
        if len(current) + len(para) > CHUNK_MAX_CHARS and current:
            if len(current) >= CHUNK_MIN_CHARS:
                output.append((current.strip(), h1, h2))
            else:
                # 合并到上一个
                if output:
                    pt, ph1, ph2 = output[-1]
                    output[-1] = (pt + "\n\n" + current.strip(), ph1, ph2)
                else:
                    output.append((current.strip(), h1, h2))
            current = para
        else:
            current = current + "\n\n" + para if current else para

    if current.strip():
        if len(current) >= CHUNK_MIN_CHARS or not output:
            output.append((current.strip(), h1, h2))
        else:
            pt, ph1, ph2 = output[-1]
            output[-1] = (pt + "\n\n" + current.strip(), ph1, ph2)


def _merge_short_chunks(
    chunks: List[Tuple[str, str, str]]
) -> List[Tuple[str, str, str]]:
    """合并过短的 chunk 到前一个"""
    if not chunks:
        return chunks

    merged = [chunks[0]]
    for text, h1, h2 in chunks[1:]:
        if len(text) < CHUNK_MIN_CHARS and merged:
            prev_text, prev_h1, prev_h2 = merged[-1]
            # 保留前一个的 h2 作为主导航
            merged[-1] = (prev_text + "\n\n" + text, prev_h1, prev_h2)
        else:
            merged.append((text, h1, h2))

    return merged


def build_documents(docs_dir: Path) -> Tuple[List[str], List[dict], List[str]]:
    """
    遍历 docs_dir 下所有 .md 文件，分块并提取元数据。
    返回 (chunk_texts, metadatas, chunk_ids)
    """
    all_texts = []
    all_metas = []
    all_ids = []

    categories = {
        "framework": docs_dir / "framework",
        "design": docs_dir / "design",
        "component": docs_dir / "component",
        "api": docs_dir / "api",
    }

    for category, cat_dir in categories.items():
        if not cat_dir.exists():
            print(f"[WARN] 目录不存在，跳过: {cat_dir}")
            continue

        md_files = sorted(cat_dir.glob("*.md"))
        print(f"[INFO] 发现 {len(md_files)} 个 {category} 文档")

        for md_file in tqdm(md_files, desc=f"分块 {category}", unit="文件"):
            try:
                content = md_file.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                try:
                    content = md_file.read_text(encoding="gbk")
                except Exception as e:
                    print(f"[WARN] 无法读取 {md_file.name}: {e}")
                    continue

            if not content.strip():
                continue

            # 跳过索引/摘要文件，它们包含所有关键词但无实质内容，干扰搜索
            name_upper = md_file.name.upper()
            if any(skip in name_upper for skip in ["SUMMARY.", "INDEX.", "FRAMEWORK_INDEX."]):
                continue

            rel_path = str(md_file.relative_to(docs_dir))
            base_meta = extract_metadata(content, rel_path, category)

            chunks = chunk_markdown(content)
            if not chunks:
                continue

            for i, (chunk_text, h1, h2) in enumerate(chunks):
                chunk_id = f"{md_file.stem}_{i}"
                meta = dict(base_meta)
                meta["title"] = h1 or base_meta["title"]
                meta["section"] = h2
                meta["chunk_index"] = i

                all_texts.append(chunk_text)
                all_metas.append(meta)
                all_ids.append(chunk_id)

    return all_texts, all_metas, all_ids


def build_index(
    texts: List[str],
    metadatas: List[dict],
    ids: List[str],
    db_dir: str,
    model_name: str,
    reset: bool = False,
    offline: bool = False,
):
    """生成嵌入并存入 ChromaDB"""
    print(f"[INFO] 加载嵌入模型: {model_name}")
    model_kwargs = {}
    if offline:
        model_kwargs["local_files_only"] = True
    model = SentenceTransformer(model_name, **model_kwargs)
    dim = model.get_sentence_embedding_dimension()  # noqa: keep for older sentence-transformers compat
    print(f"[INFO] 嵌入维度: {dim}")

    print(f"[INFO] 生成 {len(texts)} 个 chunk 的嵌入向量...")
    start = time.time()
    embeddings = model.encode(
        texts,
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    elapsed = time.time() - start
    print(f"[INFO] 嵌入生成完成，耗时 {elapsed:.1f}s ({len(texts)/elapsed:.0f} chunks/s)")

    print(f"[INFO] 连接 ChromaDB: {db_dir}")
    client = chromadb.PersistentClient(path=db_dir)

    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
            print(f"[INFO] 已删除旧 collection: {COLLECTION_NAME}")
        except Exception:
            pass

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={
            "description": "微信小程序官方文档向量索引",
            "hnsw:space": "cosine",
        },
    )

    # 分批写入 ChromaDB
    batch_size = 100
    for i in range(0, len(ids), batch_size):
        collection.add(
            ids=ids[i : i + batch_size],
            embeddings=embeddings[i : i + batch_size].tolist(),
            documents=texts[i : i + batch_size],
            metadatas=metadatas[i : i + batch_size],
        )

    print(f"[INFO] 已写入 {len(ids)} 条记录到 ChromaDB")
    return collection.count()


def main():
    parser = argparse.ArgumentParser(description="微信小程序文档向量化")
    parser.add_argument(
        "--docs-dir",
        type=str,
        default=None,
        help="official-docs 目录路径（默认自动查找）",
    )
    parser.add_argument(
        "--db-dir",
        type=str,
        default=None,
        help="ChromaDB 存储目录（默认 tools/chroma_db）",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="BAAI/bge-large-zh-v1.5",
        help="嵌入模型名称",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="删除旧索引后重建",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="离线模式，不检查 HuggingFace 更新",
    )
    args = parser.parse_args()

    if args.offline:
        os.environ["HF_HUB_OFFLINE"] = "1"

    script_dir = Path(__file__).parent.resolve()

    # 定位目录
    docs_dir = Path(args.docs_dir) if args.docs_dir else find_docs_dir(script_dir)
    db_dir = args.db_dir or str(script_dir / "chroma_db")

    print(f"[INFO] 文档目录: {docs_dir}")
    print(f"[INFO] 数据库目录: {db_dir}")

    # 构建文档
    texts, metas, ids = build_documents(docs_dir)
    print(f"[INFO] 总计 {len(texts)} 个 chunks（来自 {len(set(m['source_file'] for m in metas))} 个文件）")

    if not texts:
        print("[ERROR] 没有可处理的文档内容")
        sys.exit(1)

    # 统计
    frameworks = sum(1 for m in metas if m["category"] == "framework")
    designs = sum(1 for m in metas if m["category"] == "design")
    avg_len = sum(len(t) for t in texts) / len(texts)
    print(f"[INFO] framework: {frameworks} chunks, design: {designs} chunks")
    print(f"[INFO] 平均 chunk 长度: {avg_len:.0f} 字符")

    # 生成嵌入并存储
    count = build_index(
        texts, metas, ids, db_dir, args.model, reset=args.reset, offline=args.offline
    )
    print(f"[SUCCESS] 完成! ChromaDB 中共 {count} 条记录")
    print(f"[INFO] 搜索工具: python {script_dir / 'search_docs.py'} <query>")


if __name__ == "__main__":
    main()
