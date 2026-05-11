# Skills

AI-assisted development skills collection — domain-specific multi-agent collaboration systems for rapid application development.

## Skills

### [miniprogram-developer](./skills/miniprogram-developer/)

WeChat Mini Program full-stack development skill. Covers project initialization, architecture design, pages/components, routing, networking, cloud functions, testing, debugging, performance tuning, and cross-platform development.

**Features:**
- Multi-Agent architecture: 1 coordinator + 10 domain-expert sub-agents
- Semantic search knowledge base: ~390 official WeChat doc pages + ChromaDB + BGE-large-zh-v1.5
- 12 development workflows: project-init, feature-dev, component-dev, cloud-fn-dev, testing, bugfix, refactor, perf-tuning, hotfix, knowledge-lookup, code-review, tech-selection
- Context Exchange Protocol: structured JSON, token budgets, path-only references
- Quality audit score: **8.2/10** (verified through 8 rounds of blind review)

### [skill-builder](./skills/skill-builder/)

Meta-framework for rapidly scaffolding domain-specific AI development skills. Extracts reusable patterns (multi-agent collaboration, context exchange protocol, blind review cycles, semantic knowledge base) from proven skills.

**Features:**
- 6 reusable templates with documented placeholders
- 6 meta-patterns (architecture, protocol, blind review, knowledge base, workflow design, quality gates)
- 3 meta-workflows (skill-init, skill-audit, skill-improve)
- Scaffold CLI tool with validation and collision detection
- Quality audit score: **9.3/10** (verified through 4 rounds of blind review)
- 12/12 public pattern coverage from miniprogram-developer, zero domain-specific content

## Architecture

Each skill follows the same proven meta-pattern:

```
Coordinator (SKILL.md)     — dispatches, never executes
    │
    ├─ Workflows (N)       — phase-gated, keyword-triggered
    ├─ Agents (M)          — domain experts, structured I/O
    ├─ Protocol             — context exchange, token budgets
    ├─ Knowledge Base       — semantic search, official docs
    └─ Quality Gates        — blind review, iterative scoring
```

## Quick Start

Clone and use a skill directly:

```bash
npx skills add Pippinrao/miniprogram-developer
```

Create a new skill using the builder:

```bash
cd skills/skill-builder
python tools/scaffold-skill.py --name my-skill --domain "我的领域" --path /output/path
```

## License

Apache 2.0 — see [LICENSE](./skills/miniprogram-developer/LICENSE)
