#!/usr/bin/env python3
"""
技能脚手架生成器 — 从模板快速生成新技能目录结构。

用法:
    python tools/scaffold-skill.py --name harmonyos-dev --domain "鸿蒙单框架开发" --path /abs/path

选项:
    --name          技能名称（英文小写+连字符）
    --domain        领域描述（中文）
    --path          输出路径（绝对路径）
    --agents        子Agent列表，逗号分隔
    --workflows     工作流列表，逗号分隔
    --with-knowledge 创建知识库目录结构
    --template-dir  模板目录（默认 ./templates/）
"""

import argparse
import os
import sys
from pathlib import Path
from datetime import date

# ─── 默认配置 ───────────────────────────────────────────

DEFAULT_AGENTS = [
    "requirement-designer",
    "code-analysis",
    "code-implementation",
    "test-design",
    "test-execution",
    "debugging",
    "refactoring",
]

DEFAULT_WORKFLOWS = [
    "project-init",
    "feature-dev",
    "component-dev",
    "testing",
    "bugfix",
    "refactor",
    "knowledge-lookup",
    "code-review",
]

SKILL_DIRS = [
    "agents",
    "workflows",
    "protocols",
    "references",
    "official-docs",
    "tools",
]

# ─── 核心逻辑 ───────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="技能脚手架生成器")
    p.add_argument("--name", required=True, help="技能名称（英文小写+连字符）")
    p.add_argument("--domain", required=True, help="领域描述（中文）")
    p.add_argument("--path", required=True, help="输出路径（绝对路径）")
    p.add_argument("--agents", help="子Agent列表，逗号分隔")
    p.add_argument("--workflows", help="工作流列表，逗号分隔")
    p.add_argument("--with-knowledge", action="store_true", help="创建知识库目录")
    p.add_argument("--force", action="store_true", help="跳过碰撞检测，直接覆盖")
    p.add_argument("--dry-run", action="store_true", help="仅显示将要创建的文件，不实际创建")
    p.add_argument("--template-dir", default=None, help="模板目录路径")
    return p.parse_args()


def create_dirs(skill_path, with_knowledge):
    """创建技能目录结构"""
    dirs = SKILL_DIRS.copy()
    if with_knowledge:
        dirs.extend(["official-docs/framework", "official-docs/api", "official-docs/design"])
    for d in dirs:
        full = os.path.join(skill_path, d)
        os.makedirs(full, exist_ok=True)
        print(f"  ✓ {d}/")


def fill_template(template_path, variables):
    """用变量替换模板中的占位符"""
    if not os.path.exists(template_path):
        return None
    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()
    for k, v in variables.items():
        content = content.replace("{{" + k + "}}", str(v))
    return content


def generate_skill_md(skill_path, args, template_dir):
    """从模板生成 SKILL.md"""
    variables = {
        "SKILL_NAME": args.name,
        "DOMAIN": args.domain,
        "DOMAIN_DESCRIPTION": f"{args.domain}开发技能",
        "TRIGGER_KEYWORDS": "开发, 创建项目, 新增功能, 测试, 调试, 部署",
        "AUTHOR": os.environ.get("USER", "developer"),
        "VERSION": "1.0",
    }

    tmpl = os.path.join(template_dir, "SKILL.template.md")
    if not os.path.exists(tmpl):
        print(f"  ⚠ 模板不存在: {tmpl}，生成占位文件")
        with open(os.path.join(skill_path, "SKILL.md"), "w", encoding="utf-8") as f:
            f.write(f"# {args.name} — {args.domain} 开发技能\n\n> 使用 skill-builder 生成\n")
        return

    agents_list = (args.agents or "").split(",") if args.agents else DEFAULT_AGENTS
    workflows_list = (args.workflows or "").split(",") if args.workflows else DEFAULT_WORKFLOWS

    # 构建工作流表
    wf_table = ""
    for wf in workflows_list:
        wf = wf.strip()
        if wf:
            wf_table += f'| "关键词" | {wf} | `workflows/{wf}.md` |\n'

    # 构建Agent表
    agent_table = ""
    for ag in agents_list:
        ag = ag.strip()
        if ag:
            agent_table += f'| {ag} | `agents/{ag}.md` | 语义搜索对应领域 → 加载命中文档 |\n'

    # 搜索示例
    search_examples = "| 项目初始化 | `python tools/search_docs.py \"项目结构 配置\" --top 5` |\n"

    # 参考表
    ref_table = "| 测试 | `references/testing.md` |\n"

    variables.update({
        "WORKFLOW_TABLE": wf_table,
        "AGENT_TABLE": agent_table,
        "SEARCH_EXAMPLES": search_examples,
        "REFERENCE_TABLE": ref_table,
    })

    content = fill_template(tmpl, variables)
    if content:
        with open(os.path.join(skill_path, "SKILL.md"), "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✓ SKILL.md")


def generate_agents(skill_path, agents_list, template_dir):
    """为每个Agent生成骨架文件"""
    tmpl_path = os.path.join(template_dir, "agent.template.md")
    if not os.path.exists(tmpl_path):
        print(f"  ⚠ Agent模板不存在: {tmpl_path}")
        return
    tmpl_content = open(tmpl_path, "r", encoding="utf-8").read()

    for ag in agents_list:
        ag = ag.strip()
        if not ag:
            continue
        content = tmpl_content.replace("{{AGENT_NAME}}", ag)
        ag_path = os.path.join(skill_path, "agents", f"{ag}.md")
        with open(ag_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✓ agents/{ag}.md")


def generate_workflows(skill_path, workflows_list, template_dir):
    """为每个工作流生成骨架文件"""
    tmpl_path = os.path.join(template_dir, "workflow.template.md")
    if not os.path.exists(tmpl_path):
        print(f"  ⚠ 工作流模板不存在: {tmpl_path}")
        return
    tmpl_content = open(tmpl_path, "r", encoding="utf-8").read()

    for wf in workflows_list:
        wf = wf.strip()
        if not wf:
            continue
        content = tmpl_content.replace("{{WORKFLOW_NAME}}", wf)
        wf_path = os.path.join(skill_path, "workflows", f"{wf}.md")
        with open(wf_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✓ workflows/{wf}.md")


def generate_protocol(skill_path, template_dir):
    """从模板生成协议文件"""
    tmpl = os.path.join(template_dir, "protocol.template.md")
    if os.path.exists(tmpl):
        content = open(tmpl, "r", encoding="utf-8").read()
        with open(os.path.join(skill_path, "protocols", "context-exchange.md"), "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✓ protocols/context-exchange.md")


def generate_readme(skill_path, args, agents_list, workflows_list):
    """生成 README.md"""
    content = f"""# {args.name}

{args.domain}全栈开发 Agent Skill — 基于语义搜索知识库的 Multi-Agent 协作开发系统。

## 特性

- **Multi-Agent 架构**: 1 个主调度 Agent + {len(agents_list)} 个领域专家子Agent
- **语义搜索知识库**: 基于 BGE + ChromaDB 的官方文档搜索
- **{len(workflows_list)} 个开发工作流**: 覆盖从项目初始化到部署的完整生命周期
- **上下文交换协议**: 主Agent≤500 tokens，子Agent≤300 tokens

## 目录结构

```
{args.name}/
├── SKILL.md
├── agents/                 # {len(agents_list)} 个子Agent
├── workflows/              # {len(workflows_list)} 个工作流
├── protocols/              # 上下文交换协议
├── references/             # 实践指南
├── official-docs/          # 官方文档知识库
└── tools/                  # 语义搜索工具
```

## 快速开始

### 构建知识库索引

```bash
cd {args.name}/tools
pip install -r requirements.txt
python embed_docs.py
```

### 语义搜索

```bash
python tools/search_docs.py "查询关键词" --top 5
```

## License

Apache 2.0
"""
    with open(os.path.join(skill_path, "README.md"), "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  ✓ README.md")


def validate_inputs(args):
    """验证输入参数，返回错误列表"""
    errors = []
    # 名称检查
    if not args.name or not args.name.strip():
        errors.append("--name 不能为空")
    elif not all(c.islower() or c.isdigit() or c == '-' for c in args.name):
        errors.append("--name 只能包含小写字母、数字和连字符")
    elif args.name.startswith('-') or args.name.endswith('-'):
        errors.append("--name 不能以连字符开头或结尾")
    # 路径检查
    if not args.path or not args.path.strip():
        errors.append("--path 不能为空")
    elif not os.path.isabs(args.path):
        errors.append("--path 必须是绝对路径")
    # 领域检查
    if not args.domain or not args.domain.strip():
        errors.append("--domain 不能为空")
    return errors


def check_collision(skill_path):
    """检查目标路径是否已存在，返回文件列表"""
    if os.path.exists(skill_path):
        existing = []
        for root, dirs, files in os.walk(skill_path):
            for f in files:
                existing.append(os.path.relpath(os.path.join(root, f), skill_path))
        return existing
    return []


def main():
    args = parse_args()

    # 输入验证
    errors = validate_inputs(args)
    if errors:
        print("❌ 参数错误:")
        for e in errors:
            print(f"   - {e}")
        sys.exit(1)

    skill_path = os.path.abspath(os.path.join(args.path, args.name))
    template_dir = args.template_dir or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "templates"
    )

    # 碰撞检测
    existing = check_collision(skill_path)
    if existing and not args.force:
        print(f"⚠ 目标路径已存在 ({len(existing)} 个文件):")
        for f in existing[:10]:
            print(f"   - {f}")
        if len(existing) > 10:
            print(f"   ... 及其他 {len(existing) - 10} 个文件")
        resp = input("是否覆盖? (yes/no): ").strip().lower()
        if resp not in ('yes', 'y'):
            print("已取消。")
            sys.exit(0)
    elif existing and args.force:
        print(f"⚠ 目标路径已存在 ({len(existing)} 个文件)，--force 已启用，直接覆盖。")

    # 干运行模式
    if args.dry_run:
        print(f"\n{'='*60}")
        print(f"  [DRY RUN] 将创建以下内容:")
        print(f"  目录: {skill_path}/")
        for d in SKILL_DIRS:
            print(f"    ├── {d}/")
        print(f"  文件: SKILL.md, README.md, protocols/context-exchange.md")
        print(f"  Agent ({len(agents_list)}): {', '.join(agents_list)}")
        print(f"  工作流 ({len(workflows_list)}): {', '.join(workflows_list)}")
        print(f"  知识库目录: {'是' if args.with_knowledge else '否'}")
        print(f"{'='*60}\n")
        sys.exit(0)

    # 模板目录检查
    if not os.path.isdir(template_dir):
        print(f"❌ 模板目录不存在: {template_dir}")
        sys.exit(1)

    agents_list = [a.strip() for a in (args.agents or "").split(",") if a.strip()] or DEFAULT_AGENTS
    workflows_list = [w.strip() for w in (args.workflows or "").split(",") if w.strip()] or DEFAULT_WORKFLOWS

    print(f"\n{'='*60}")
    print(f"  技能脚手架: {args.name}")
    print(f"  领域: {args.domain}")
    print(f"  路径: {skill_path}")
    print(f"  Agent: {len(agents_list)} 个")
    print(f"  工作流: {len(workflows_list)} 个")
    print(f"  知识库: {'是' if args.with_knowledge else '否'}")
    print(f"{'='*60}\n")

    try:
        print("[1/6] 创建目录结构...")
        create_dirs(skill_path, args.with_knowledge)

        print("[2/6] 生成 SKILL.md...")
        generate_skill_md(skill_path, args, template_dir)

        print("[3/6] 生成 Agent 骨架...")
        generate_agents(skill_path, agents_list, template_dir)

        print("[4/6] 生成工作流骨架...")
        generate_workflows(skill_path, workflows_list, template_dir)

        print("[5/6] 生成协议文件...")
        generate_protocol(skill_path, template_dir)

        print("[6/6] 生成 README.md + references/...")
        generate_readme(skill_path, args, agents_list, workflows_list)

        # 生成知识检索指南
        kr_path = os.path.join(skill_path, "references", "knowledge-retrieval.md")
        os.makedirs(os.path.dirname(kr_path), exist_ok=True)
        with open(kr_path, "w", encoding="utf-8") as f:
            f.write(f"""# 知识检索指南 — {args.name}

## 语义搜索工具

```bash
python tools/search_docs.py "<搜索关键词>" [选项]
```

| 选项 | 说明 |
|------|------|
| `--top 5` | 返回结果数 |
| `--category <name>` | 按分类过滤 |
| `--json` | JSON格式输出 |

## 搜索技巧
- 使用领域术语搜索效果最好
- 如结果不理想，调整关键词重试（最多3轮）
- 搜索失败时降级为查阅 `official-docs/INDEX.md`

## 谁负责搜索
| 角色 | 职责 |
|------|------|
| 主Agent | 初始搜索，将命中路径通过 searchResults 传给子Agent |
| 子Agent | 补充搜索，如传入的 searchResults 不足可自行搜索 |
""")
        print(f"  ✓ references/knowledge-retrieval.md")

    except PermissionError as e:
        print(f"❌ 权限不足: {e}")
        sys.exit(1)
    except OSError as e:
        print(f"❌ 文件系统错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        print("   脚手架生成失败，请检查路径和权限。")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"  ✅ 技能 {args.name} 创建完成!")
    print(f"  路径: {skill_path}")
    print(f"")
    print(f"  下一步:")
    print(f"  1. cd {skill_path}")
    print(f"  2. 填充 SKILL.md 中的占位符（工作流表、Agent表、搜索示例）")
    print(f"  3. 为每个 Agent 填充角色/执行/约束/示例")
    print(f"  4. 为每个工作流填充阶段/知识/错误处理")
    print(f"  5. 采集官方文档到 official-docs/")
    print(f"  6. 运行 embed_docs.py 构建知识库")
    print(f"  7. 运行 skill-builder 的 skill-audit 工作流进行首次盲审")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
