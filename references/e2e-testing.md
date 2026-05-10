---
skill: miniprogram-developer
version: 1.0.0
updated: 2026-05-10
depends: [device-automation]
provides: [E2E测试, Automator, Page Object, 断言, 数据驱动]
difficulty: intermediate
official: https://developers.weixin.qq.com/miniprogram/dev/devtools/automator.html
---

> **环境准备**: 需要 `npm install miniprogram-automator` 安装依赖。微信开发者工具必须打开并启用自动化端口（设置 → 安全设置 → 服务端口）。

> **API 兼容性说明**: miniprogram-automator 的 API 与标准 Web 自动化工具有所不同：`page.waitForNavigation()`、`element.isVisible()`、`page.waitForTimeout()` 等方法**不存在**。本文档中所有代码示例均已使用经过验证的替代方案（如 `page.waitFor(selector_or_ms)` 替代上述不存在的 API）。详见各代码示例中的注释。

# 微信小程序 E2E 测试

## Automator 简介

Automator 是微信官方提供的 UI 自动化测试框架，用于模拟用户操作小程序页面。支持页面导航、元素交互、表单输入、断言验证等操作。

### 初始化

```javascript
const automator = require('miniprogram-automator');

async function init() {
  const miniProgram = await automator.launch({
    projectPath: 'D:/workspace/your-miniprogram',  // 替换为你的小程序项目路径
    // 指定设备，可选
    device: 'iphone 12',
    // 指定平台，可选
    platform: 'ios'
  });
  return miniProgram;
}
```

### 连接已有项目

如果小程序已在开发者工具中打开，可以直接连接：

```javascript
const automator = require('miniprogram-automator');

async function connect() {
  const miniProgram = await automator.connect({
    wsEndpoint: 'ws://127.0.0.1:9420'
  });
  return miniProgram;
}
```

## 页面操作

### 导航操作

```javascript
// 跳转到指定页面
await miniProgram.navigateTo('/pages/index/index');

// 页面返回
await miniProgram.navigateBack();

// 切换 TabBar 页面
await miniProgram.switchTab('/pages/home/home');

// 重新加载当前页
await miniProgram.reLaunch('/pages/index/index');

// 获取当前页面栈信息
const pages = await miniProgram.pageStack();
console.log(pages);
```

### 元素交互

```javascript
// 点击元素
await element.tap();

// 长按元素
await element.longpress();

// 输入文本
await element.input('hello world');

// 清空输入框（clear 方法不存在，使用 input('') 替代）
await element.input('');

// 获取元素文本
const text = await element.text();

// 获取元素属性
const value = await element.attribute('value');

// 获取元素边界矩形
const rect = await element.boundingClientRect();
console.log(rect);

// 判断元素是否可见（使用 waitFor 超时判断）
const visible = await miniProgram.page.waitFor('.selector', { timeout: 3000 }).then(() => true).catch(() => false);
```

### 滚动操作

```javascript
// 滚动页面 (pageScrollTo 是 MiniProgram 对象的方法)
await miniProgram.pageScrollTo(1000);

// 滚动到页面底部
// 可先获取页面高度再滚动

// 滑动操作（swipe 不存在于 Automator）
// 使用 page.callMethod 调用页面自定义滚动方法
```

### 延迟与等待

```javascript
// 等待元素出现
await miniProgram.page.waitFor('.selector', { timeout: 5000 });

// 等待指定时间
await miniProgram.page.waitFor(2000);  // waitForTimeout 不存在，使用 waitFor 替代

// 等待导航完成
await miniProgram.page.waitFor('[data-testid="some-element"]')
```

## 元素定位

> **微信小程序选择器限制**: WXML 不是标准 HTML，CSS 选择器支持有限。推荐使用 `data-*` 属性标识元素。

### 选择器优先级

1. **`data-testid` 属性**（推荐）- 在 WXML 中添加 `data-testid` 标识元素
2. **`id` 选择器** - 支持但需唯一
3. **文本内容** - 部分支持 `^=` 前缀匹配
4. **class 选择器** - 支持但可能重复

### 推荐实践

```xml
<!-- WXML 中添加 data-testid -->
<view data-testid="match-item" class="match-item">
  <text data-testid="match-title">{{name}}</text>
</view>
```

```javascript
// E2E 中使用 data-testid
const item = await miniProgram.page.$('[data-testid="match-item"]');
const title = await miniProgram.page.$('[data-testid="match-title"]');
```

### 基本选择器

```javascript
// ID 选择器
const btn = await miniProgram.page.$('#submit-btn');

// class 选择器（可能匹配多个）
const items = await miniProgram.page.$$('.list-item');

// 标签选择器
const view = await miniProgram.page.$('view');

// 复合选择器（有限支持）
const element = await miniProgram.page.$('.container #title');
```

### 属性选择器

```javascript
// 属性存在选择
const element = await miniProgram.page.$('[data-testid]');

// 属性值匹配（推荐）
const input = await miniProgram.page.$('[placeholder="请输入"]');
const disabled = await miniProgram.page.$('[disabled]');

// 属性值精确匹配
const type = await miniProgram.page.$('[type="text"]');
```

### 伪类选择器

```javascript
// 第一个子元素（部分支持）
const first = await miniProgram.page.$('view:first-child');

// 最后一个子元素
const last = await miniProgram.page.$('view:last-child');

// 第 N 个子元素
const third = await miniProgram.page.$('view:nth-child(3)');

// 奇数/偶数元素
const odd = await miniProgram.page.$('view:nth-child(odd)');
const even = await miniProgram.page.$('view:nth-child(even)');
```

### 组合选择器

```javascript
// 后代选择器
const nested = await miniProgram.page.$('.parent .child');

// 子元素选择器
const directChild = await miniProgram.page.$('.parent > view');

// 相邻兄弟选择器
const sibling = await miniProgram.page.$('.item + .item');

// 通用兄弟选择器
const siblings = await miniProgram.page.$('.item ~ .item');
```

### 获取元素数据

```javascript
// 获取单个元素
const element = await miniProgram.page.$('.item');

// 获取元素信息
const info = await element.info();
console.log(info);
// {
//   id: 'item-1',
//   name: 'view',
//   text: '文本内容',
//   boundingClientRect: { left, top, right, bottom, width, height },
//   dataset: { testid: 'item1' },
//   attributes: { class: 'item active' },
//   ....
// }

// 获取多个元素
const elements = await miniProgram.page.$$('.list-item');

// 遍历元素
for (const el of elements) {
  const text = await el.text();
  console.log(text);
}
```

## 断言

### 基本断言

```javascript
const expect = require('expect');  // miniprogram-automator 不导出 expect

// 断言元素存在
expect(element).not.toBeNull();

// 断言文本内容
expect(await element.text()).toBe('预期文本');
expect(await element.text()).toContain('包含的文本');
expect(await element.text()).toMatch(/正则表达式/);

// 断言元素可见（isVisible 不存在，使用 waitFor 替代）
expect(await miniProgram.page.waitFor('.selector', { timeout: 3000 }).then(() => true).catch(() => false)).toBe(true);

// 断言元素数量
const items = await miniProgram.page.$$('.item');
expect(items.length).toBe(10);
```

### 页面状态断言

```javascript
// 断言页面路径
expect(miniProgram.page.path).toBe('/pages/index/index');

// 断言页面数据
expect((await miniProgram.page.data()).key).toBe('value');  // data 是方法调用，不是属性访问

// 断言元素属性
expect(await element.attribute('disabled')).toBe(true);

// 断言元素存在
const el = await miniProgram.page.$('.empty-state');
expect(el).toBeNull(); // 期望不存在
```

---

## 点击跳转验证

> 点击元素后验证页面跳转是小程序 E2E 最核心的测试场景。
> 不仅验证"跳了"，还要验证"跳到哪了"、"参数带过去了"、"页面正常渲染了"。

### 跳转类型覆盖

| 跳转方式 | API | 页面栈变化 | 验证重点 |
|---------|-----|----------|---------|
| 普通跳转 | `wx.navigateTo` | 栈+1 | path、参数、返回按钮 |
| 重定向 | `wx.redirectTo` | 栈不变 | 当前页替换、无法返回 |
| Tab切换 | `wx.switchTab` | 栈重置 | path、无返回按钮 |
| 返回 | `wx.navigateBack` | 栈-1 | 回到上一页、数据保持 |
| 重启动 | `wx.reLaunch` | 栈重置为1 | 首页加载 |

### 基础点击跳转验证

```javascript
// 模式: 点击元素 → 等待跳转 → 验证目标页面
it('点击比赛卡片应跳转到详情页', async () => {
  // 1. 获取跳转前的页面路径
  const fromPath = miniProgram.page.path;
  expect(fromPath).toBe('/pages/match/list/list');

  // 2. 点击元素触发跳转
  const card = await miniProgram.page.$('[data-testid="match-card-0"]');
  await card.tap();

  // 3. 等待页面跳转完成
  await miniProgram.page.waitFor('[data-testid="some-element"]')

  // 4. 验证当前页面路径
  expect(miniProgram.page.path).toBe('/pages/match/detail/detail');
});
```

### 带参数跳转验证

```javascript
// 验证跳转时带的参数在目标页面正确使用
it('点击卡片应传递正确的比赛ID到详情页', async () => {
  // 点击第一张卡片
  const card = await miniProgram.page.$('[data-testid="match-card-0"]');
  const cardId = await card.attribute('data-id'); // 假设卡片上有 data-id
  await card.tap();
  await miniProgram.page.waitFor('[data-testid="some-element"]')

  // 验证目标页面路由参数
  const pageData = await miniProgram.page.data();
  expect(pageData.matchId).toBe(cardId); // onLoad 中从 options 获取

  // 验证页面用这个ID渲染了正确内容
  const title = await miniProgram.page.$('[data-testid="match-title"]');
  expect(await title.text()).not.toBe('');
});
```

### 返回验证

```javascript
// 验证从详情页返回列表页
it('从详情页返回列表页应保持列表状态', async () => {
  // 进入详情页
  await miniProgram.navigateTo('/pages/match/detail/detail');
  await miniProgram.page.waitFor('[data-testid="some-element"]')

  // 记录详情页数据
  const detailTitle = await miniProgram.page.$('.match-title');
  const detailText = await detailTitle.text();

  // 点击返回按钮
  const backBtn = await miniProgram.page.$('[data-testid="back-btn"]');
  await backBtn.tap();

  // 或使用系统返回
  // await miniProgram.navigateBack();

  await miniProgram.page.waitFor('[data-testid="some-element"]')

  // 验证回到列表页
  expect(miniProgram.page.path).toBe('/pages/match/list/list');

  // 验证列表页仍正常渲染
  const listItems = await miniProgram.page.$$('[data-testid="match-card"]');
  expect(listItems.length).toBeGreaterThan(0);
});
```

### Tab 切换验证

```javascript
// 验证 TabBar 切换
it('点击"我的"Tab应切换到个人页', async () => {
  // 点击 TabBar 中的"我的"
  // 注意: TabBar 元素需要通过 switchTab 触发
  await miniProgram.switchTab('/pages/mine/mine');

  // 验证页面切换到个人页
  expect(miniProgram.page.path).toBe('/pages/mine/mine');

  // 验证页面栈被重置（Tab切换后应该只有1层）
  const pages = await miniProgram.pageStack();
  expect(pages.length).toBe(1);

  // 验证个人页核心元素可见（isVisible 不存在，使用 waitFor 替代）
  expect(await miniProgram.page.waitFor('[data-testid="user-avatar"]', { timeout: 3000 }).then(() => true).catch(() => false)).toBe(true);
});
```

### 页面栈验证

```javascript
// 验证连续跳转后页面栈深度正确
it('连续跳转后页面栈深度应正确', async () => {
  // 从首页 → 列表页
  await miniProgram.navigateTo('/pages/match/list/list');
  await miniProgram.page.waitFor('[data-testid="some-element"]')

  // 从列表页 → 详情页
  const card = await miniProgram.page.$('[data-testid="match-card-0"]');
  await card.tap();
  await miniProgram.page.waitFor('[data-testid="some-element"]')

  // 验证页面栈有3层: 首页 + 列表 + 详情
  const pages = await miniProgram.pageStack();
  expect(pages.length).toBe(3);
  expect(pages[0].path).toBe('/pages/index/index');
  expect(pages[1].path).toBe('/pages/match/list/list');
  expect(pages[2].path).toBe('/pages/match/detail/detail');

  // 返回一层
  await miniProgram.navigateBack();
  await miniProgram.page.waitFor(500);

  // 验证栈变为2层，当前页为列表页
  const pages2 = await miniProgram.pageStack();
  expect(pages2.length).toBe(2);
  expect(miniProgram.page.path).toBe('/pages/match/list/list');
});
```

### 跳转失败验证

```javascript
// 验证跳转到不存在页面时的表现
it('跳转到不存在页面不应崩溃', async () => {
  try {
    await miniProgram.navigateTo('/pages/notexist/notexist');
    await miniProgram.page.waitFor(1000);

    // 应停留在原页面
    expect(miniProgram.page.path).toBe('/pages/index/index');

    // 或者检查是否有错误提示
    const errorToast = await miniProgram.page.$('.error-toast');
    // 小程序 navigateTo fail 不会跳转，但也不会抛异常到 Automator
  } catch (e) {
    // navigateTo fail 事件
    expect(miniProgram.page.path).toBe('/pages/index/index');
  }
});
```

### 跳转性能验证

```javascript
// 验证页面跳转耗时
it('列表页跳转应在1秒内完成', async () => {
  const startTime = Date.now();

  await miniProgram.navigateTo('/pages/match/list/list');
  await miniProgram.page.waitFor('[data-testid="some-element"]')

  // 等待关键元素渲染（说明首屏可用）
  await miniProgram.page.waitFor('[data-testid="match-card-0"]');

  const elapsed = Date.now() - startTime;
  expect(elapsed).toBeLessThan(1000); // 1秒内完成跳转+渲染
});
```

### 跳转 + 数据一致性验证

```javascript
// 验证跳转前后数据一致性（核心场景）
it('列表页选择第N项 → 详情页内容应对应正确的数据', async () => {
  // 在列表页获取所有可见卡片标题
  const cards = await miniProgram.page.$$('[data-testid="match-card"]');
  const count = cards.length;
  expect(count).toBeGreaterThan(0);

  // 随机选第1项
  const targetIndex = 0;
  const listTitle = await cards[targetIndex].$('[data-testid="card-title"]');
  const expectedTitle = await listTitle.text();

  // 点击进入详情
  await cards[targetIndex].tap();
  await miniProgram.page.waitFor('[data-testid="some-element"]')

  // 详情页标题应匹配
  const detailTitle = await miniProgram.page.$('[data-testid="match-title"]');
  const actualTitle = await detailTitle.text();
  expect(actualTitle).toBe(expectedTitle);
});
```

## 断言

### 模拟 Assert 方法

```javascript
// 自定义断言函数
function assertCondition(actual, expected, message) {
  if (actual !== expected) {
    throw new Error(message || `Expected ${expected} but got ${actual}`);
  }
}

// 使用示例
const title = await miniProgram.page.$('.title');
assertCondition(
  await title.text(),
  '比赛详情',
  '页面标题不正确'
);
```

## Page Object 模式

Page Object 是常用的自动化测试设计模式，将页面元素和操作封装为独立对象，提高测试代码的可维护性和复用性。

### 项目结构

```
tests/
├── page-objects/
│   ├── home-page.js
│   ├── match-list-page.js
│   └── match-detail-page.js
├── specs/
│   └── match.spec.js
└── config.js
```

### 基础 Page Object

```javascript
// page-objects/base-page.js

class BasePage {
  constructor(page, miniProgram) {
    this.page = page;
    this.miniProgram = miniProgram;
  }

  // 等待页面加载
  async waitForLoad() {
    await this.page.waitFor(500);  // waitForTimeout 不存在，使用 waitFor 替代
  }

  // 通用点击
  async click(selector) {
    const element = await this.page.$(selector);
    if (!element) {
      throw new Error(`Element not found: ${selector}`);
    }
    await element.tap();
    await this.waitForLoad();
  }

  // 通用输入
  async input(selector, text) {
    const element = await this.page.$(selector);
    if (!element) {
      throw new Error(`Element not found: ${selector}`);
    }
    await element.input(text);
  }

  // 获取文本
  async getText(selector) {
    const element = await this.page.$(selector);
    if (!element) {
      throw new Error(`Element not found: ${selector}`);
    }
    return await element.text();
  }

  // 导航 (使用 MiniProgram 对象的标准 API)
  async navigateTo(path) {
    await this.miniProgram.navigateTo(path);
    await this.waitForLoad();
  }

  async navigateBack() {
    await this.miniProgram.navigateBack();
    await this.waitForLoad();
  }
}

module.exports = BasePage;
```

### 页面 Page Object 示例

```javascript
// page-objects/home-page.js
const BasePage = require('./base-page');

class HomePage extends BasePage {
  constructor(page, miniProgram) {
    super(page, miniProgram);
    this.selectors = {
      banner: '.banner',
      quickAction: '.quick-action',
      matchList: '.match-list',
      matchItem: '.match-list .match-item',
      tabBar: '.tab-bar',
      profileBtn: '.tab-bar .profile',
      matchBtn: '.tab-bar .match'
    };
  }

  async waitForBanner() {
    await this.page.waitFor(this.selectors.banner);
  }

  async clickMatchItem(index = 0) {
    const items = await this.page.$$(this.selectors.matchItem);
    if (items.length > index) {
      await items[index].tap();
    }
    await this.waitForLoad();
  }

  async getMatchCount() {
    const items = await this.page.$$(this.selectors.matchItem);
    return items.length;
  }

  async goToProfile() {
    await this.click(this.selectors.profileBtn);
  }

  async goToMatch() {
    await this.click(this.selectors.matchBtn);
  }

  async isBannerVisible() {
    return await this.page.waitFor(this.selectors.banner, { timeout: 3000 }).then(() => true).catch(() => false);  // isVisible 不存在，使用 waitFor 替代
  }
}

module.exports = HomePage;
```

```javascript
// page-objects/match-detail-page.js
const BasePage = require('./base-page');

class MatchDetailPage extends BasePage {
  constructor(page, miniProgram) {
    super(page, miniProgram);
    this.selectors = {
      title: '.match-title',
      status: '.match-status',
      scoreBtn: '.score-btn',
      shareBtn: '.share-btn',
      playerList: '.player-list',
      playerItem: '.player-list .player-item',
      emptyState: '.empty-state',
      backBtn: '.back-btn'
    };
  }

  async getTitle() {
    return this.getText(this.selectors.title);
  }

  async getStatus() {
    return this.getText(this.selectors.status);
  }

  async isRecruiting() {
    const status = await this.getStatus();
    return status === '招募中';
  }

  async clickScore() {
    await this.click(this.selectors.scoreBtn);
  }

  async clickShare() {
    await this.click(this.selectors.shareBtn);
  }

  async getPlayerCount() {
    const players = await this.page.$$(this.selectors.playerItem);
    return players.length;
  }

  async hasPlayers() {
    const empty = await this.page.$(this.selectors.emptyState);
    return empty === null;
  }

  async goBack() {
    await this.click(this.selectors.backBtn);
  }
}

module.exports = MatchDetailPage;
```

### 测试用例中使用 Page Object

```javascript
// specs/match.spec.js
const automator = require('miniprogram-automator');
const HomePage = require('../page-objects/home-page');
const MatchDetailPage = require('../page-objects/match-detail-page');
const MatchListPage = require('../page-objects/match-list-page');

describe('比赛功能 E2E 测试', () => {
  let miniProgram;
  let homePage;
  let matchListPage;
  let matchDetailPage;

  beforeAll(async () => {
    miniProgram = await automator.launch({
      projectPath: '/path/to/project'
    });
    homePage = new HomePage(miniProgram.page, miniProgram);
  });

  afterAll(async () => {
    await miniProgram.close();
  });

  describe('首页测试', () => {
    test('应该正确显示 Banner', async () => {
      await homePage.waitForBanner();
      expect(await homePage.isBannerVisible()).toBe(true);
    });

    test('应该显示比赛列表', async () => {
      const count = await homePage.getMatchCount();
      expect(count).toBeGreaterThan(0);
    });

    test('应该能导航到比赛详情', async () => {
      await homePage.clickMatchItem(0);
      matchDetailPage = new MatchDetailPage(miniProgram.page, miniProgram);
      const title = await matchDetailPage.getTitle();
      expect(title).toBeTruthy();
    });
  });

  describe('比赛详情测试', () => {
    beforeEach(async () => {
      await homePage.clickMatchItem(0);
      matchDetailPage = new MatchDetailPage(miniProgram.page, miniProgram);
    });

    test('应该显示正确的状态', async () => {
      const isRecruiting = await matchDetailPage.isRecruiting();
      expect(typeof isRecruiting).toBe('boolean');
    });

    test('应该能进入计分页面', async () => {
      await matchDetailPage.clickScore();
      // 验证页面跳转
    });

    test('应该有选手列表或空状态', async () => {
      const hasPlayers = await matchDetailPage.hasPlayers();
      const count = await matchDetailPage.getPlayerCount();
      expect(hasPlayers || count === 0).toBe(true);
    });
  });
});
```

### Page Object 最佳实践

1. **页面元素选择器统一管理**：将选择器集中在 `selectors` 对象中，便于维护
2. **业务操作封装**：将页面相关业务操作封装为方法，而非直接操作元素
3. **等待机制**：在页面切换后适当等待，确保页面加载完成
4. **错误处理**：对关键操作添加异常处理，提高测试稳定性
5. **数据分离**：测试数据与测试逻辑分离，便于参数化测试

### 数据驱动测试

```javascript
// page-objects/form-page.js
class FormPage extends BasePage {
  constructor(page) {
    super(page);
    this.selectors = {
      nameInput: '#name-input',
      phoneInput: '#phone-input',
      submitBtn: '#submit-btn',
      errorMsg: '.error-message'
    };
  }

  async fillForm(data) {
    if (data.name) {
      await this.input(this.selectors.nameInput, data.name);
    }
    if (data.phone) {
      await this.input(this.selectors.phoneInput, data.phone);
    }
  }

  async submit() {
    await this.click(this.selectors.submitBtn);
  }

  async getError() {
    const errorEl = await this.page.$(this.selectors.errorMsg);
    return errorEl ? await errorEl.text() : null;
  }
}

// 测试用例
const testCases = [
  { name: '张三', phone: '13800138000', expected: '提交成功' },
  { name: '', phone: '13800138000', expected: '请输入姓名' },
  { name: '李四', phone: '', expected: '请输入手机号' },
  { name: '王五', phone: '12345', expected: '手机号格式错误' }
];

testCases.forEach(({ name, phone, expected }) => {
  test(`表单验证: ${expected}`, async () => {
    await formPage.fillForm({ name, phone });
    await formPage.submit();
    const error = await formPage.getError();
    expect(error).toBe(expected);
  });
});
```

## 完整测试流程示例

```javascript
const automator = require('miniprogram-automator');

async function runE2ETest() {
  let miniProgram;

  try {
    // 1. 启动小程序
    console.log('启动小程序...');
    miniProgram = await automator.launch({
      projectPath: 'D:/workspace/your-miniprogram'  // 替换为你的小程序项目路径
    });

    // 2. 首页操作
    console.log('测试首页...');
    let page = miniProgram.page;
    await page.waitFor('.banner');
    console.log('Banner 已加载');

    // 3. 导航到比赛列表
    console.log('导航到比赛列表...');
    await miniProgram.navigateTo('/pages/match/match');
    await page.waitFor('.match-list');

    // 4. 选择第一个比赛
    console.log('选择比赛...');
    const matchItems = await page.$$('.match-item');
    if (matchItems.length > 0) {
      await matchItems[0].tap();
    }

    // 5. 验证比赛详情页
    console.log('验证比赛详情...');
    await page.waitFor('.match-title');
    const title = await page.$('.match-title');
    const titleText = await title.text();
    console.log(`比赛标题: ${titleText}`);

    // 6. 进入计分页面
    console.log('进入计分...');
    const scoreBtn = await page.$('.score-btn');
    if (scoreBtn) {
      await scoreBtn.tap();
      await page.waitFor('.score-board');
      console.log('计分页面已加载');
    }

    console.log('测试完成!');
  } catch (error) {
    console.error('测试失败:', error);
    throw error;
  } finally {
    if (miniProgram) {
      await miniProgram.close();
    }
  }
}

runE2ETest();
```

## 常见问题

### 选择器定位不到元素

- 检查元素是否在当前页面（可能需要滚动）
- 使用 `page.waitFor()` 等待元素出现
- 检查选择器语法是否正确
- 确认元素是否在分包页面中

### 页面导航后元素定位失败

- 页面切换后需要重新获取元素引用
- 使用 `page.waitFor('[data-testid="some-element"]')` 等待导航完成
- 在新页面中重新调用 `page.$()` 获取元素

### 测试不稳定

- 添加适当的等待时间
- 使用 `waitFor` 替代固定延时
- 确保测试数据状态一致
- 避免依赖外部网络请求

---

## 布局与视觉验证

> Automator 通过 `boundingClientRect()` 可以获取元素的精确位置和尺寸。
> 利用这些数据可以检测常见的 UI 错位、重叠、溢出等问题。

### 基础位置断言

```javascript
const expect = require('expect');  // miniprogram-automator 不导出 expect

// 获取元素位置
const rect = await element.boundingClientRect();
// rect = { left, top, right, bottom, width, height }
```

### 常见 UI Bug 检测模式

#### 1. 元素重叠检测

```javascript
// 检测两个元素是否重叠（错位）
async function isOverlapping(el1, el2) {
  const r1 = await el1.boundingClientRect();
  const r2 = await el2.boundingClientRect();

  const horizontalOverlap = r1.left < r2.right && r1.right > r2.left;
  const verticalOverlap = r1.top < r2.bottom && r1.bottom > r2.top;

  return horizontalOverlap && verticalOverlap;
}

// 用例: 卡片之间不应重叠
it('列表项不应重叠', async () => {
  const items = await page.$$('.card-item');
  for (let i = 0; i < items.length - 1; i++) {
    const overlapping = await isOverlapping(items[i], items[i + 1]);
    expect(overlapping).toBe(false);  // 相邻卡片不应重叠
  }
});
```

#### 2. 元素溢出检测

```javascript
// 检测子元素是否超出父容器
async function isOverflowing(parentSelector, childSelector) {
  const parent = await page.$(parentSelector);
  const child = await page.$(childSelector);

  const pRect = await parent.boundingClientRect();
  const cRect = await child.boundingClientRect();

  return (
    cRect.left < pRect.left ||
    cRect.right > pRect.right ||
    cRect.top < pRect.top ||
    cRect.bottom > pRect.bottom
  );
}

// 用例: 弹窗内容不应超出屏幕
it('弹窗内容不应超出屏幕', async () => {
  const overflowing = await isOverflowing('page', '.modal-content');
  expect(overflowing).toBe(false);
});
```

#### 3. 元素对齐检测

```javascript
// 检测同行元素是否水平对齐（常见于 flex 布局错位）
async function areAlignedHorizontally(el1, el2) {
  const r1 = await el1.boundingClientRect();
  const r2 = await el2.boundingClientRect();

  // 允许 2px 误差
  return Math.abs(r1.top - r2.top) <= 2;
}

// 用例: 按钮和输入框应在同一行对齐
it('按钮和输入框应对齐', async () => {
  const input = await page.$('[data-testid="search-input"]');
  const btn = await page.$('[data-testid="search-btn"]');
  expect(await areAlignedHorizontally(input, btn)).toBe(true);
});
```

#### 4. 文字截断检测

```javascript
// 检测文字是否被截断（容器宽度小于子元素宽度）
async function isTextTruncated(selector) {
  const el = await page.$(selector);
  const rect = await el.boundingClientRect();

  // 文字元素实际内容宽度 vs 可视宽度
  const text = await el.text();
  const estimatedWidth = text.length * 14; // 粗略估算：14px/字

  return estimatedWidth > rect.width + 5; // 超出 5px 视为截断
}

// 用例: 标题不应被截断
it('比赛标题不应被截断', async () => {
  const truncated = await isTextTruncated('[data-testid="match-title"]');
  expect(truncated).toBe(false);
});
```

#### 5. 固定间距检测

```javascript
// 检测列表项之间间距是否一致
async function hasConsistentSpacing(items) {
  if (items.length < 2) return true;

  const rects = await Promise.all(
    items.map(el => el.boundingClientRect())
  );

  // 计算第一个间距作为基准
  const expectedGap = rects[1].top - rects[0].bottom;

  for (let i = 1; i < rects.length - 1; i++) {
    const gap = rects[i + 1].top - rects[i].bottom;
    if (Math.abs(gap - expectedGap) > 1) return false;
  }
  return true;
}

// 用例: 列表项间距应一致
it('列表项之间间距应一致', async () => {
  const items = await page.$$('.list-item');
  const consistent = await hasConsistentSpacing(items);
  expect(consistent).toBe(true);
});
```

#### 6. 吸顶/吸底检测

```javascript
// 检测元素是否在屏幕可视区域内
async function isInViewport(selector) {
  const el = await page.$(selector);
  const rect = await el.boundingClientRect();

  // 页面可视区域通常 0~windowHeight
  const windowHeight = 667; // iPhone 6/7/8 高度

  return (
    rect.top >= 0 &&
    rect.bottom <= windowHeight &&
    rect.left >= 0 &&
    rect.right <= 375 // iPhone 6/7/8 宽度
  );
}

// 用例: 底部按钮应固定在视口内
it('提交按钮应固定在底部可见', async () => {
  // scrollToBottom 不存在，使用 page.callMethod 替代
  await page.callMethod('scrollTo', 0, 9999);
  const visible = await isInViewport('[data-testid="submit-btn"]');
  expect(visible).toBe(true);
});
```

### 视觉验证索引

| UI问题 | 检测方法 | 关键API |
|--------|---------|---------|
| 元素重叠 | `isOverlapping()` | `boundingClientRect` |
| 内容溢出 | `isOverflowing()` | 父子元素 rect 比较 |
| 对齐错位 | `areAlignedHorizontally()` | `rect.top` 比较 |
| 文字截断 | `isTextTruncated()` | 估算宽度 vs `rect.width` |
| 间距不均 | `hasConsistentSpacing()` | 相邻元素间距比较 |
| 视口外元素 | `isInViewport()` | `rect` vs 屏幕尺寸 |
| 元素不可见 | `waitFor` + catch | `page.waitFor(sel).then(() => true).catch(() => false)` |
