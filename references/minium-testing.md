---
skill: miniprogram-developer
version: 1.0.0
updated: 2026-05-06
depends: [reference-e2e-testing]
provides: [Minium, Python测试, 自动化测试, 自动化用例]
difficulty: intermediate
official: https://developers.weixin.qq.com/miniprogram/dev/devtools/mini.html
---

# Minium 自动化测试框架

Minium 是微信官方提供的 Python 自动化测试框架，用于小程序自动化测试。

## 环境准备

### 安装 Python

Minium 需要 Python 3.8+ 环境。

```bash
# 检查 Python 版本
python --version

# 如果没有安装，从 https://www.python.org/downloads/ 下载安装
```

### 安装 Minium

```bash
# 使用 pip 安装
pip install minium

# 验证安装
minium --version
```

### 配置开发者工具

1. 打开微信开发者工具
2. 设置 → 安全设置 → 打开「服务端口」
3. 开启自动化端口：`工具 → 自动化测试 → 开启自动化端口`

## 项目初始化

### 创建测试项目

```bash
# 创建测试目录
mkdir miniprogram-test
cd miniprogram-test

# 初始化 minium 配置
minium -c .
```

### 目录结构

```
miniprogram-test/
├── minium.config.json    # 配置文件
├── test_cases/          # 测试用例目录
│   └── demo_test.py     # 示例测试用例
└── reports/             # 测试报告目录
```

### 配置文件

```json
{
  "project_path": "D:/workspace/my-miniprogram",
  "appid": "wx1234567890abcdef",
  "test_port": 9420,
  "devtools_path": "C:\\Program Files (x86)\\Tencent\\微信web开发者工具\\cli.bat"
}
```

## 编写测试用例

### 基本结构

```python
import minium

class DemoTest(minium.MiniTest):
    """示例测试用例"""

    def setUp(self):
        """测试前准备"""
        self.app = minium.get_app()
        self.page = self.app.navigate_to("/pages/index/index")

    def test_home_page_load(self):
        """测试首页加载"""
        # 获取页面元素
        title = self.page.get_element("view.title")
        assert title.text == "首页"

    def test_navigation(self):
        """测试导航"""
        # 点击按钮跳转
        self.page.get_element("view.go-detail").click()
        # 验证跳转
        self.assertEqual(self.app.get_current_page().path, "/pages/detail/index")

    def tearDown(self):
        """测试后清理"""
        pass
```

### 元素定位

| 定位方式 | 示例 |
|---------|------|
| CSS 选择器 | `self.page.get_element("view.className")` |
| data-testid | `self.page.get_element("[data-testid='btn']")` |
| 文本内容 | `self.page.get_element("view.text('提交')")` |
| wxml 结构 | `self.page.get_element("view > view.button")` |

### 页面操作

```python
def test_form_input(self):
    """测试表单输入"""
    # 输入文本
    self.page.get_element("input.name").input("张三")

    # 获取输入值
    value = self.page.get_element("input.name").value
    assert value == "张三"

def test_button_click(self):
    """测试按钮点击"""
    self.page.get_element("button.submit").click()

def test_swipe(self):
    """测试滑动"""
    self.page.get_element("scroll-view").swipe_up(5)
```

### 断言

```python
def test_assertions(self):
    """常用断言"""
    # 文本断言
    self.assertEqual(actual, expected)
    self.assertNotEqual(actual, expected)

    # 存在性断言
    self.assertIsNotNone("view.title")
    self.assertIsNone("view.error")

    # 布尔断言
    self.assertTrue(condition)
    self.assertFalse(condition)

    # 页面断言
    self.assertEqual(self.app.get_current_page().path, "/pages/detail/index")
```

### 网络请求监控

```python
def test_network_request(self):
    """测试网络请求"""
    # 开启请求监控
    with self.app.capture_http_request() as requests:
        self.page.get_element("button.fetch").click()
        self.page.wait_for(2)  # 等待请求完成

    # 验证请求
    assert len(requests) > 0
    assert requests[0].url == "https://api.example.com/data"
```

## 运行测试

### 命令行运行

```bash
# 运行所有测试
minium -p test_cases/

# 运行指定文件
minium -p test_cases/demo_test.py

# 运行指定测试函数
minium -p test_cases/demo_test.py::DemoTest::test_home_page_load

# 生成报告
minium -p test_cases/ -r reports/
```

### 在代码中运行

```python
import minium

# 初始化
mini = minium.Mini({
    "project_path": "D:/workspace/my-miniprogram",
    "devtools_path": "C:\\Program Files (x86)\\Tencent\\微信web开发者工具\\cli.bat"
})

# 加载测试用例
mini.load_test_cases("test_cases/")

# 运行
mini.run()
```

## CI/CD 集成

> **重要**：Minium 依赖微信开发者工具提供的自动化端口。在 CI 环境中运行时，必须在 CI runner 上安装微信开发者工具，并确保自动化端口（默认 9420）已开启且未被占用。CI runner 需为 Windows 或 macOS（微信开发者工具不支持 Linux）。

### GitHub Actions

```yaml
name: Minium Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install Minium
        run: pip install minium

      - name: Run Tests
        run: minium -p test_cases/ -r reports/
```

### 测试报告

Minium 支持生成 HTML 测试报告：

```bash
# 使用 allure 生成报告
pip install allure-pytest

minium -p test_cases/ --alluredir reports/
allure serve reports/
```

## 最佳实践

### 推荐 data-testid

在 WXML 中添加 `data-testid` 属性，方便定位：

```xml
<button data-testid="submit-btn" bindtap="onSubmit">提交</button>
```

```python
self.page.get_element("[data-testid='submit-btn']").click()
```

### 等待策略

```python
# 显式等待
self.page.wait_for(2)  # 等待2秒

# 条件等待
self.page.wait_for_selector("view.result", timeout=5000)

# 等待请求完成
self.app.wait_for_request("**/api/data**", timeout=10000)
```

### 测试隔离

```python
class TestSuite(minium.MiniTest):
    def setUp(self):
        # 每个测试前清理数据
        self.app.clear_storage()
        self.page = self.app.navigate_to("/pages/index/index")
```
