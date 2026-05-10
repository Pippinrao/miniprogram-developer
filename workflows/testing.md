# 生产级自动化测试工作流

## 触发

用户说"帮我测试"|"跑测试"|"检查质量"|"上线前检查"|"自动化测试"|"完整测试"

## 分层测试策略

```
┌────────────────────────────────────────────────────────────────┐
│                    生产级测试体系                               │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  L1: 静态检查 ──► L2: 单元测试 ──► L3: 集成测试 ──► L4: E2E   │
│      1min             3min             2min             5min    │
│                                                                 │
│  全量运行只在: PR合并前 / 上线前 / 用户明确要求                │
│  日常增量: 只测变更文件 + 依赖链                               │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

---

## 阶段0: 测试策略分析

**目标**: 不看代码就决定测什么 → 先扫描项目结构，根据文件类型自动决策

### 步骤

1. 用 `ls` 扫描项目目录: `pages/` `components/` `utils/` `cloudfunctions/`
2. 自动生成测试策略:

| 目录存在 | 测试类型 | 执行模式 | 加载知识 |
|---------|---------|---------|---------|
| `utils/` 有 `.js` 文件 | L2 UT | mode=ut | references/unit-test.md |
| `cloudfunctions/` 有云函数 | L2 UT(带Mock) | mode=ut | references/unit-test.md |
| `pages/` 有页面 | L4 E2E | mode=e2e | references/e2e-testing.md |
| `components/` 有组件 | L4 E2E | mode=e2e | references/e2e-testing.md |

3. 输出测试策略表:

```json
{
  "strategy": {
    "ut": { "scope": ["utils/", "cloudfunctions/"], "estimatedCases": 15, "mode": "ut" },
    "e2e": { "scope": ["pages/", "components/"], "estimatedCases": 5, "mode": "e2e" }
  },
  "skipReasons": {},
  "estimatedDuration": "8min",
  "parallelizable": true
}
```

### 决策点

- **UT + E2E 都有**: 并行启动两个子Agent
- **只有UT**: 只启动 test-execution mode=ut
- **只有E2E**: 只启动 test-execution mode=e2e
- **什么都没**: 报告"无可测试代码"

---

## 阶段1: 测试设计 [子Agent: test-design]

主Agent:
   │
   ├─► 启动 test-design 子Agent
   │    加载: agents/test-design.md + references/unit-test.md + references/e2e-testing.md
   │    任务: 根据 scope 设计 UT 和 E2E 测试用例
   │    输出: { utCases, e2eScenarios }
   │
   └─► 决策: 用例设计合理 → 阶段2

## 阶段2: 并行执行 [子Agent: test-execution]

主Agent:
   │
   ├─► [并行] test-execution-subagent-A (mode=ut)
   │     加载: agents/test-execution.md + references/unit-test.md
   │     输入: { testDesign: { utCases } }
   │     任务: 根据 utCases 编写测试代码 → 运行 → 报告
   │
   └─► [并行] test-execution-subagent-B (mode=e2e)
         加载: agents/test-execution.md + references/e2e-testing.md
         输入: { testDesign: { e2eScenarios } }
         任务: 根据 e2eScenarios 编写E2E测试 → 运行 → 报告

---

## 阶段3: 结果汇总

主Agent 收集两个子Agent返回的结构化结果，生成测试报告:

```json
{
  "report": {
    "timestamp": "2026-05-10T12:00:00Z",
    "duration": "7min 32s",
    "summary": "UT 15/15通过(82%覆盖率), E2E 5/5通过",
    "status": "PASS",
    "qualityGate": {
      "utCoverage": { "actual": 82, "threshold": 70, "pass": true },
      "e2ePassRate": { "actual": 100, "threshold": 100, "pass": true },
      "noFlakyTests": { "actual": 0, "threshold": 0, "pass": true }
    },
    "details": {
      "ut": { "pass": 15, "fail": 0, "skip": 0, "coverage": "82%" },
      "e2e": { "pass": 5, "fail": 0, "skip": 0, "screenshots": [] }
    }
  }
}
```

---

## 增量测试模式（日常开发）

当用户说"快速测试"|"测一下改动"时:

```
1. git diff --name-only → 找到变更文件
2. 确定变更影响的测试范围:
   - utils/xxx.js 变更 → 运行 tests/xxx.test.js
   - pages/xxx/xxx.js 变更 → 运行相关 UT + E2E
   - cloudfunctions/xxx/ 变更 → 运行相关 UT
3. 只运行受影响的测试
4. 报告: "增量测试 3/3通过, 耗时45秒"
```

---

## 质量门禁

必须全部通过才算测试通过:

| 门禁 | 阈值 | 不通过时 |
|------|------|---------|
| UT 覆盖率 | ≥70% | 列出未覆盖模块 |
| UT 通过率 | 100% | 列出失败用例 |
| E2E 通过率 | 100% | 列出失败场景+截图 |
| 无 flaky 测试 | 0个 | 列出 flaky 用例 |
| 无控制台错误 | 0个 | 列出错误日志 |

---

## 测试报告模板

```markdown
# 自动化测试报告

**时间**: 2026-05-10 12:00
**耗时**: 7min 32s
**状态**: ✅ PASS

## 质量门禁
| 门禁 | 实际 | 阈值 | 结果 |
|------|------|------|------|
| UT覆盖率 | 82% | 70% | ✅ |
| UT通过率 | 15/15 | 100% | ✅ |
| E2E通过率 | 5/5 | 100% | ✅ |
| Flaky测试 | 0 | 0 | ✅ |

## 测试详情
### UT (15个用例)
- utils/util.test.js: 5/5
- utils/rotation.test.js: 3/3
- cloudfunctions/match.test.js: 7/7

### E2E (5个场景)
- 首页加载: ✅
- 列表→详情跳转: ✅
- 表单提交: ✅
- 返回导航: ✅
- 空状态展示: ✅

## 未覆盖代码
- utils/logger.js (0%) - 建议补充测试
- cloudfunctions/admin/index.js (45%) - 边界条件未覆盖

## 产物
- 覆盖率报告: coverage/lcov-report/index.html
- E2E截图: artifacts/
```

---

## 错误处理

| 错误 | 自动处理 |
|------|---------|
| npm test 命令不存在 | 检查 package.json，添加 test script |
| jest 未安装 | 自动 `npm install --save-dev jest` |
| 测试文件目录不存在 | 自动创建 tests/ 目录 |
| Automator 连接失败 | 提示用户开启开发者工具自动化端口 |
| 单个测试超时 | 标记为 flaky，跳过后重试 |
