---
skill: miniprogram-developer
version: 1.0.0
updated: 2026-05-10
provides: [单元测试, Jest, Mock, TDD, 覆盖率, 工具函数测试, 云函数测试]
difficulty: intermediate
official: https://jestjs.io/docs/getting-started
---

# 微信小程序单元测试

## 前置依赖

```bash
npm install --save-dev jest babel-jest @babel/core @babel/preset-env
# 可选: XML/HTML snapshot 序列化和 JUnit 报告
npm install --save-dev jest-serializer-html jest-junit
```

## wx 全局 API Mock

小程序测试需要 mock `wx` 全局对象:

```javascript
// tests/setup.js
global.wx = {
  getStorageSync: jest.fn().mockReturnValue(null),
  setStorageSync: jest.fn(),
  navigateTo: jest.fn(),
  request: jest.fn(),
  showToast: jest.fn(),
  showLoading: jest.fn(),
  hideLoading: jest.fn(),
  login: jest.fn().mockResolvedValue({ code: 'mock-code' }),
  getSystemInfoSync: jest.fn().mockReturnValue({
    platform: 'ios',
    model: 'iPhone 12',
    SDKVersion: '3.0.0'
  })
};

// Mock wx.cloud
global.wx.cloud = {
  callFunction: jest.fn(),
  database: jest.fn(() => ({
    collection: jest.fn(() => ({
      get: jest.fn().mockResolvedValue({ data: [] }),
      add: jest.fn().mockResolvedValue({ _id: 'mock-id' })
    }))
  }))
};
```

## Jest 完整配置

### jest.config.js 完整配置

```javascript
// jest.config.js
module.exports = {
  // 测试环境
  testEnvironment: 'node',

  // 测试文件匹配模式
  testMatch: [
    '**/tests/**/*.test.js',
    '**/tests/**/*.spec.js'
  ],

  // 忽略文件
  testPathIgnorePatterns: [
    '/node_modules/',
    '/dist/'
  ],

  // 覆盖率收集
  collectCoverage: true,
  collectCoverageFrom: [
    'utils/**/*.js',
    'cloudfunctions/**/*.js',
    '!node_modules/**',
    '!**/*.config.js',
    '!**/index.js'  // 入口文件通常不测试
  ],

  // 覆盖率阈值（CI 中必须满足）
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70
    },
    // 针对特定文件可设置不同阈值
    './utils/util.js': {
      branches: 80,
      functions: 80,
      lines: 80
    }
  },

  // 转换器（处理 ES6+ 语法）
  transform: {
    '^.+\\.js$': 'babel-jest'
  },

  // 模块名称映射（处理别名路径）
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/$1',
    '^utils/(.*)$': '<rootDir>/utils/$1'
  },

  // setup 文件（每个测试前执行）
  setupFilesAfterEnv: ['<rootDir>/tests/setup.js'],

  // 快照序列化
  // 注意: jest-serializer-html 针对标准 HTML 设计，WXML 快照可能需自定义序列化器
  snapshotSerializers: ['jest-serializer-html'],

  // 报告格式
  reporters: [
    'default',
    ['jest-junit', { outputDirectory: 'coverage', outputName: 'junit.xml' }]
  ]
}
```

### package.json 测试脚本

```json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "test:ci": "jest --ci --coverage --maxWorkers=2",
    "test:util": "jest tests/util.test.js",
    "test:rotation": "jest tests/rotation.test.js",
    "test:cloud": "jest tests/cloudfunction.test.js"
  }
}
```

## Mock wx-server-sdk 详解

### Mock 模式选择指南

| 场景 | 推荐模式 | 说明 |
|------|---------|------|
| 纯工具函数测试 | 不需要 mock | utils/ 下函数无依赖 |
| 云函数集成测试 | `jest.mock` + `{ virtual: true }` | 每次测试重置，推荐 |
| 共享 mock 实例 | `__mocks__/` 目录单例 | 多个测试文件共享 |

> **重要**: `jest.mock()` 工厂函数内不能引用外部变量（除 mock- 前缀变量名外）。

### 基础 Mock（单例模式）

```javascript
// tests/__mocks__/wx-server-sdk.js
const _cmd = {
  gte: (v) => v,
  lte: (v) => v,
  and: (...a) => a,
  or: (...a) => a,
  in: (a) => a,
  nin: (a) => a,
  neq: (v) => v,
  eq: (v) => v,
  exists: (v) => v
};

const mockCollection = {
  doc: jest.fn(),
  where: jest.fn(),
  orderBy: jest.fn(),
  limit: jest.fn(),
  skip: jest.fn(),
  field: jest.fn(),
  count: jest.fn(),
  add: jest.fn(),
  update: jest.fn(),
  remove: jest.fn()
};

const _db = {
  collection: jest.fn(() => mockCollection),
  command: _cmd,
  serverDate: jest.fn(() => new Date())
};

module.exports = {
  cloud: {
    init: jest.fn(),
    DYNAMIC_CURRENT_ENV: 'test'
  },
  db: _db,
  // 便捷方法
  getMockDb: () => _db,
  getMockCollection: () => mockCollection
};
```

### 云函数测试的 Mock（每次测试重置）

```javascript
// tests/cloudfunction.test.js

// 方式 1：使用虚拟 mock（推荐）
jest.mock('wx-server-sdk', () => {
  const _cmd = {
    gte: (v) => v,
    lte: (v) => v,
    and: (...a) => a,
    in: (a) => a,
    neq: (v) => v
  };

  const mockAdd = jest.fn();
  const mockUpdate = jest.fn();
  const mockRemove = jest.fn();
  const mockCount = jest.fn();

  const mockCollection = {
    doc: jest.fn(),
    where: jest.fn().mockReturnThis(),
    orderBy: jest.fn().mockReturnThis(),
    limit: jest.fn().mockReturnThis(),
    skip: jest.fn().mockReturnThis(),
    field: jest.fn().mockReturnThis(),
    count: jest.fn().mockResolvedValue({ total: 0 }),
    add: mockAdd,
    update: mockUpdate,
    remove: mockRemove
  };

  return {
    cloud: { init: jest.fn(), DYNAMIC_CURRENT_ENV: 'test' },
    db: {
      collection: jest.fn(() => mockCollection),
      command: _cmd,
      serverDate: jest.fn(() => new Date())
    },
    // 导出 mock 函数以便测试中断言
    __mockAdd: mockAdd,
    __mockUpdate: mockUpdate,
    __mockRemove: mockRemove,
    __mockCollection: mockCollection
  };
}, { virtual: true });

const { __mockAdd, __mockUpdate, __mockCollection } = require('wx-server-sdk');
const matchFunction = require('../../cloudfunctions/match/index');

describe('match cloud function', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    __mockAdd.mockResolvedValue({ id: 'test-id' });
    __mockUpdate.mockResolvedValue({ updated: 1 });
  });

  describe('create action', () => {
    it('should create match successfully', async () => {
      const result = await matchFunction.main({
        action: 'create',
        name: '测试比赛',
        playerCount: 8
      }, {});

      expect(__mockCollection).toHaveBeenCalledWith('matches');
      expect(__mockAdd).toHaveBeenCalled();
      expect(result.id).toBe('test-id');
    });

    it('should validate playerCount', async () => {
      await expect(matchFunction.main({
        action: 'create',
        name: '测试比赛',
        playerCount: 2  // 无效
      }, {})).rejects.toThrow('参赛人数需在3-32人之间');
    });
  });
});
```

### Mock 返回值链式调用

```javascript
// 模拟链式 API：db.collection('users').where({...}).get()
jest.mock('wx-server-sdk', () => {
  const mockWhere = jest.fn().mockReturnThis();
  const mockOrderBy = jest.fn().mockReturnThis();
  const mockLimit = jest.fn().mockReturnThis();
  const mockGet = jest.fn();

  const mockCollection = {
    doc: jest.fn(),
    where: mockWhere,
    orderBy: mockOrderBy,
    limit: mockLimit,
    get: mockGet,
    count: jest.fn().mockResolvedValue({ total: 0 }),
    add: jest.fn().mockResolvedValue({ id: 'new-id' }),
    update: jest.fn().mockResolvedValue({ updated: 1 }),
    remove: jest.fn().mockResolvedValue({ deleted: 1 })
  };

  return {
    cloud: { init: jest.fn(), DYNAMIC_CURRENT_ENV: 'test' },
    db: {
      collection: jest.fn(() => mockCollection),
      command: {
        gte: (v) => v,
        lte: (v) => v,
        eq: (v) => v,
        neq: (v) => v,
        in: (a) => a,
        and: (...a) => a
      }
    }
  };
}, { virtual: true });

// 使用示例
const { db } = require('wx-server-sdk');
const mockCollection = db.collection('matches');

// 链式调用
db.collection('matches')
  .where({ status: 'ongoing' })
  .orderBy('createTime', 'desc')
  .limit(10)
  .get();
```

## 工具函数测试模板

### 基础工具函数测试

```javascript
// tests/util.test.js
const {
  validateMatchParams,
  formatDate,
  deepClone,
  generateJoinCode
} = require('../utils/util');

describe('util.js', () => {
  describe('validateMatchParams', () => {
    it('playerCount范围3-32', () => {
      expect(validateMatchParams({ playerCount: 2 }))
        .toBe('参赛人数需在3-32人之间');
      expect(validateMatchParams({ playerCount: 33 }))
        .toBe('参赛人数需在3-32人之间');
    });

    it('playerCount有效范围应返回null', () => {
      expect(validateMatchParams({ playerCount: 4 })).toBeNull();
      expect(validateMatchParams({ playerCount: 16 })).toBeNull();
    });

    it('format必须为rotation', () => {
      expect(validateMatchParams({ playerCount: 4, format: 'roundRobin' }))
        .toBe('当前仅支持轮换排表');
    });

    it('空对象应有默认校验', () => {
      expect(validateMatchParams({})).not.toBeNull();
    });
  });

  describe('formatDate', () => {
    it('应格式化为YYYY-MM-DD', () => {
      const date = new Date('2026-05-01T12:00:00');
      expect(formatDate(date)).toBe('2026-05-01');
    });

    it('应支持自定义格式', () => {
      const date = new Date('2026-05-01T12:00:00');
      expect(formatDate(date, 'YYYY/MM/DD')).toBe('2026/05/01');
      expect(formatDate(date, 'MM-DD')).toBe('05-01');
    });

    it('应处理时间戳', () => {
      expect(formatDate(1714564800000)).toBe('2026-05-01');
    });
  });

  describe('deepClone', () => {
    it('应深拷贝嵌套对象', () => {
      const original = { a: 1, b: { c: 2, d: [1, 2, 3] } };
      const cloned = deepClone(original);

      cloned.b.c = 999;
      cloned.b.d.push(4);

      expect(original.b.c).toBe(2);  // 原对象不变
      expect(original.b.d).toEqual([1, 2, 3]);
    });

    it('应处理数组', () => {
      const original = [{ a: 1 }, { b: 2 }];
      const cloned = deepClone(original);

      cloned[0].a = 999;
      expect(original[0].a).toBe(1);
    });
  });

  describe('generateJoinCode', () => {
    it('应生成6位数字码', () => {
      const code = generateJoinCode();
      expect(code).toMatch(/^\d{6}$/);
    });

    it('每次调用应生成唯一码', () => {
      const codes = new Set();
      for (let i = 0; i < 100; i++) {
        codes.add(generateJoinCode());
      }
      expect(codes.size).toBe(100);
    });
  });
});
```

### 轮转赛算法测试

```javascript
// tests/rotation.test.js
const { generateRotationSchedule, validateRotationParams } = require('../utils/rotation');

describe('rotation.js', () => {
  describe('generateRotationSchedule', () => {
    it('4人轮转赛生成6场比赛', () => {
      const schedule = generateRotationSchedule(4);
      expect(schedule).toHaveLength(6);
    });

    it('6人轮转赛生成15场比赛', () => {
      const schedule = generateRotationSchedule(6);
      expect(schedule).toHaveLength(15);
    });

    it('比赛格式应为[[p1,p2],[p3,p4],...]', () => {
      const schedule = generateRotationSchedule(4);
      schedule.forEach(match => {
        expect(match).toHaveLength(2);
        match.forEach(player => {
          expect(typeof player).toBe('number');
        });
      });
    });

    it('每场比赛的两名选手不同', () => {
      const schedule = generateRotationSchedule(4);
      schedule.forEach(match => {
        expect(match[0]).not.toBe(match[1]);
      });
    });

    it('每人应参与相同场次', () => {
      const schedule = generateRotationSchedule(6);
      const playerCounts = {};

      schedule.flat().forEach(player => {
        playerCounts[player] = (playerCounts[player] || 0) + 1;
      });

      const counts = Object.values(playerCounts);
      const avgCount = counts.reduce((a, b) => a + b, 0) / counts.length;
      counts.forEach(c => expect(c).toBe(avgCount));
    });
  });

  describe('validateRotationParams', () => {
    it('人数必须是偶数', () => {
      expect(validateRotationParams(3)).toBe('参赛人数必须是偶数');
      expect(validateRotationParams(5)).toBe('参赛人数必须是偶数');
    });

    it('人数范围4-32', () => {
      expect(validateRotationParams(2)).toBe('参赛人数需在4-32人之间');
      expect(validateRotationParams(34)).toBe('参赛人数需在4-32人之间');
    });

    it('有效人数应返回null', () => {
      expect(validateRotationParams(4)).toBeNull();
      expect(validateRotationParams(8)).toBeNull();
    });
  });
});
```

## TDD 流程

```
┌─────────────────────────────────────────────────────────────┐
│                      TDD 循环                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   1. 写测试（Red）                                          │
│      ↓                                                      │
│      it('should do X', () => {                              │
│        expect(doX()).toBe(expected);  // 测试失败 ✓        │
│      });                                                    │
│                                                             │
│   2. 写实现（Green）                                        │
│      ↓                                                      │
│      function doX() {                                       │
│        return something;  // 让测试通过                     │
│      }                                                      │
│                                                             │
│   3. 重构（Refactor）                                       │
│      ↓                                                      │
│      // 保持测试通过，优化代码                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### TDD 示例

```javascript
// 1. 先写测试（Red）
describe('calculateScore', () => {
  it('应计算基础分', () => {
    expect(calculateScore({ base: 10, multiplier: 1 }))
      .toBe(10);
  });

  it('应应用倍数', () => {
    expect(calculateScore({ base: 10, multiplier: 2 }))
      .toBe(20);
  });

  it('应处理小数', () => {
    expect(calculateScore({ base: 10, multiplier: 1.5 }))
      .toBe(15);
  });
});

// 2. 写实现（Green）
function calculateScore({ base, multiplier = 1 }) {
  return base * multiplier;
}

// 3. 运行测试通过后，可以重构...
```

## Mock 最佳实践

### 避免 Mock 地狱

```javascript
// ❌ 嵌套过深的 Mock（应避免）
beforeEach(() => {
  jest.mock('moduleA', () => ({
    fn1: jest.fn().mockReturnValue(1),
    fn2: jest.fn().mockResolvedValue({ data: 'test' })
  }));
  jest.mock('moduleB', () => ({
    fn3: jest.fn().mockImplementation(() => Promise.resolve(1))
  }));
  // ... 越来越多的 mock
});

// ✅ 使用 __mocks__ 目录集中管理
// tests/__mocks__/moduleA.js
// tests/__mocks__/moduleB.js
beforeEach(() => {
  jest.clearAllMocks();
});
```

### Mock 函数断言

```javascript
// 基础断言
expect(mockFn).toHaveBeenCalled();
expect(mockFn).toHaveBeenCalledTimes(1);
expect(mockFn).toHaveBeenCalledWith(arg1, arg2);

// 特定调用断言
expect(mockFn).toHaveBeenNthCalledWith(1, arg1, arg2);

// 返回值断言
mockFn.mockReturnValue('test');
mockFn.mockResolvedValue({ success: true });
mockFn.mockRejectedValue(new Error('fail'));

// 链式调用验证
expect(db.collection).toHaveBeenCalledWith('matches');
expect(db.collection('matches').where).toHaveBeenCalledWith({ status: 'ongoing' });
```

### 异步测试

```javascript
// Promise 方式
it('should resolve with data', async () => {
  const result = await fetchData();
  expect(result).toEqual({ data: 'test' });
});

// async/await + rejects
it('should reject on error', async () => {
  await expect(fetchData()).rejects.toThrow('Network error');
});

// Promise 链式
it('should resolve with data', () => {
  return fetchData().then(result => {
    expect(result).toEqual({ data: 'test' });
  });
});
```

## 测试命令

```bash
# 运行所有测试
npm test

# 监听模式（文件变化时自动运行）
npm run test:watch

# 生成覆盖率报告
npm run test:coverage

# CI 模式（CI 中使用）
npm run test:ci

# 只测工具函数
npm run test:util

# 只测轮转赛算法
npm run test:rotation

# 只测云函数
npm run test:cloud
```

## 测试目录结构

```
tests/
├── setup.js                    # Jest 配置（全局 setup）
├── teardown.js                 # 全局 teardown
├── __mocks__/
│   ├── wx-server-sdk.js        # 云开发 mock
│   └── other-external-module.js
├── util.test.js               # 工具函数测试
├── rotation.test.js           # 轮转赛算法测试
├── schedule.test.js           # 赛程生成测试
├── matchListLogic.test.js     # 列表逻辑测试
├── cloudfunction.test.js      # 云函数测试
└── fixtures/
    ├── sample-match.json      # 测试数据
    └── sample-player.json
```

## 常见问题

### Jest 与 ES6 模块

```javascript
// babel.config.js
module.exports = {
  presets: [
    ['@babel/preset-env', { targets: { node: 'current' } }]
  ]
};
```

### ESM 模式 (可选替代)

> 默认使用 CommonJS。如项目使用 ESM (`"type": "module"`):

```json
{
  "type": "module",
  "scripts": {
    "test": "node --experimental-vm-modules node_modules/.bin/jest"
  }
}
```

### 调试测试

```javascript
// 在测试中添加 debugger
it('debug test', () => {
  debugger;
  const result = someFunction();
  expect(result).toBe(expected);
});

// 运行并调试
npx jest --debug tests/my.test.js
```

---

## 测试数据管理

### Fixtures 目录结构

```
tests/
├── fixtures/
│   ├── matches.json          # 比赛数据
│   ├── players.json          # 选手数据
│   ├── edge-cases.json       # 边界条件数据
│   └── invalid-inputs.json   # 非法输入数据
└── utils/
    └── test-helpers.js       # 测试辅助函数
```

### 使用 Fixtures

```javascript
// tests/util.test.js
const matches = require('./fixtures/matches.json');
const edgeCases = require('./fixtures/edge-cases.json');
const { validateMatchParams } = require('../utils/util');

describe('validateMatchParams - 数据驱动', () => {
  // ✅ 用数据驱动替代重复的 it() 块
  test.each(matches.validParams)(
    '有效参数: $desc',
    ({ input, expected }) => {
      expect(validateMatchParams(input)).toBe(expected);
    }
  );

  test.each(edgeCases.boundaryValues)(
    '边界值: $desc',
    ({ input, expected }) => {
      expect(validateMatchParams(input)).toBe(expected);
    }
  );
});
```

### Fixture 文件示例

```javascript
// tests/fixtures/matches.js (使用 .js 而非 .json 以支持注释)
module.exports = {
  validParams: [
    { desc: "4人赛", input: { playerCount: 4 }, expected: null },
    { "desc": "8人赛", "input": { "playerCount": 8, "format": "rotation" }, "expected": null },
    { "desc": "32人赛", "input": { "playerCount": 32 }, "expected": null }
  ],
  "invalidParams": [
    { "desc": "人数太少", "input": { "playerCount": 2 }, "expected": "参赛人数需在3-32人之间" },
    { "desc": "人数太多", "input": { "playerCount": 33 }, "expected": "参赛人数需在3-32人之间" },
    { "desc": "空对象", "input": {}, "expected": "缺少参赛人数参数" }
  ]
}
```

### 测试隔离

```javascript
// tests/setup.js - 每个测试文件加载前执行
beforeEach(() => {
  // 每个测试前清理所有 Mock
  jest.clearAllMocks();
});

afterEach(() => {
  // 每个测试后恢复所有 Mock
  jest.restoreAllMocks();
});

// tests/teardown.js - 全局清理
afterAll(() => {
  // 清理临时文件
});
```

### 环境配置

```javascript
// tests/config.js - 测试环境配置
module.exports = {
  // 根据环境切换
  getDbConfig: () => {
    if (process.env.CI) {
      return { env: 'ci', mockDb: true };
    }
    return { env: 'local', mockDb: true };
  },

  // 测试超时
  timeout: process.env.CI ? 30000 : 10000,

  // 覆盖率阈值
  coverageThreshold: {
    global: { branches: 70, functions: 70, lines: 70 }
  },

  // 快照目录
  snapshotDir: './tests/__snapshots__'
};
```

### 测试辅助函数

```javascript
// tests/utils/test-helpers.js

// 快速创建 Mock 云函数上下文
function mockCloudContext(overrides = {}) {
  return {
    OPENID: 'test-openid-123',
    APPID: 'test-appid',
    UNIONID: 'test-unionid',
    ENV: 'test-env',
    ...overrides
  };
}

// 快速创建 Mock 云函数调用事件
function mockCloudEvent(overrides = {}) {
  return {
    action: 'default',
    userInfo: { openId: 'test-openid-123' },
    ...overrides
  };
}

// 快速创建 Mock DB 返回值
function mockDbResult(data) {
  return { data, errMsg: 'collection.get:ok' };
}

// 断言函数抛出特定错误
async function expectError(fn, message) {
  await expect(fn()).rejects.toThrow(message);
}

module.exports = {
  mockCloudContext,
  mockCloudEvent,
  mockDbResult,
  expectError
};
```

### 使用辅助函数

```javascript
const { mockCloudContext, mockCloudEvent, mockDbResult } = require('../utils/test-helpers');

describe('match cloud function', () => {
  it('应使用正确的 openId', async () => {
    const context = mockCloudContext({ OPENID: 'custom-id' });
    const event = mockCloudEvent({ action: 'create', name: '测试' });

    await matchFunction.main(event, context);

    // 验证使用了正确的 openId
    expect(mockAdd).toHaveBeenCalledWith(
      expect.objectContaining({ creatorId: 'custom-id' })
    );
  });
});
```

## 快照测试

用于验证 UI 组件输出或数据结构不变:

```javascript
// 数据结构快照验证
it('generateRotationSchedule输出结构应保持一致', () => {
  const schedule = generateRotationSchedule(8);
  expect(schedule).toMatchSnapshot();
});

// 特定版本的输出快照
it('8人赛固定输出', () => {
  const schedule = generateRotationSchedule(8);
  expect(schedule).toMatchSnapshot('8player-schedule');
});
```
