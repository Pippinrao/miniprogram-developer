---
skill: miniprogram-developer
version: 1.0.0
updated: 2026-05-10
depends: [reference-cli, reference-devtools-usage]
provides: [CI/CD, GitHub Actions, 自动化测试, 部署, Jest, Automator]
difficulty: intermediate
official: https://developers.weixin.qq.com/miniprogram/dev/devtools/cicd.html
---

# 微信小程序 CI/CD 参考资料

本文档介绍微信小程序的持续集成与持续部署流程，涵盖 GitHub Actions 工作流配置、自动化测试、部署流程以及环境变量管理。

## 1. GitHub Actions 工作流

### 1.1 基础工作流配置

微信小程序的 CI/CD 通常使用 GitHub Actions 实现自动化构建、测试和部署。以下是典型的配置文件结构：

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run unit tests
        run: npm test

      - name: Upload coverage
        uses: actions/upload-artifact@v4
        with:
          name: coverage
          path: coverage/

  build:
    needs: test
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Build npm
        run: cli build-npm --project .

      - name: Upload build artifacts
        uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/
```

### 1.2 完整部署工作流

> **重要**: 微信开发者工具 CLI 必须在开发者工具设置中开启服务端口才能使用。

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      environment:
        description: '部署环境'
        required: true
        default: 'staging'
        type: choice
        options:
          - staging
          - production

jobs:
  deploy-staging:
    if: github.event.inputs.environment == 'staging' || github.event_name == 'push'
    runs-on: windows-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test

      - name: Build npm
        run: cli build-npm --project .

      - name: Preview to WeChat
        env:
          APP_ID: ${{ secrets.STAGING_APP_ID }}
        run: |
          cli preview --project . --appid $APP_ID

  deploy-production:
    if: github.event.inputs.environment == 'production' || github.event_name == 'workflow_dispatch'
    runs-on: windows-latest
    environment: production
    concurrency:
      group: production-deploy
      cancel-in-progress: false
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run all tests
        run: |
          npm test
          npm run test:e2e

      - name: Build npm
        run: cli build-npm --project .

      - name: Deploy to production
        env:
          APP_ID: ${{ secrets.PROD_APP_ID }}
          VERSION: ${{ github.run_id }}
        run: |
          cli upload --project . --appid $APP_ID -v $VERSION -d "Release $VERSION"
```

## 2. 自动化测试

### 2.1 Jest 单元测试配置

```yaml
# jest.config.js
module.exports = {
  testEnvironment: 'node',
  roots: ['<rootDir>/tests', '<rootDir>/utils'],
  testMatch: ['**/*.test.js'],
  collectCoverageFrom: [
    'utils/**/*.js',
    'cloudfunctions/**/*.js',
    '!/**/*.test.js'
  ],
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'html'],
  setupFilesAfterEnv: ['<rootDir>/tests/setup.js'],
  testTimeout: 10000
}
```

### 2.2 E2E 测试工作流 (Automator)

> **注意**: 微信小程序 E2E 测试需要使用 `miniprogram-automator`，不是 Playwright。
> Automator 连接微信开发者工具的自动化端口，需要在 CI runner 上安装微信开发者工具。

```yaml
# .github/workflows/e2e.yml
name: E2E Tests

on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  e2e:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Build preview
        run: cli preview --project .

      - name: Run E2E tests
        run: npm run test:e2e

      - name: Upload test results
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: e2e-results
          path: artifacts/
```

### 2.3 Minium 自动化测试配置

```yaml
# miniprogram_automation/config/config.json
{
  "project_path": "./",
  "test_timeout": 30000,
  "parallel": false,
  "rm_report": true,
  "apifox": {
    "enable": false
  },
  "unittest": {
    "enable": true,
    "dir": "tests/minium/"
  },
  "uitest": {
    "enable": true,
    "dir": "miniprogram_automation/test_case/"
  }
}
```

## 3. 部署流程

### 3.1 部署阶段说明

微信小程序的部署通常包含以下阶段：

| 阶段 | 描述 | 触发条件 |
|------|------|----------|
| 构建 | 编译小程序代码，生成 dist 目录 | PR 合并、发布 |
| 预览 | 生成预览二维码，供测试 | feature 分支推送 |
| 上传 | 上传代码至微信后台 | 主分支推送 |
| 发布 | 提交审核并发布 | 手动触发 |

### 3.2 云函数部署

```yaml
# .github/workflows/cloud-deploy.yml
name: Deploy Cloud Functions

on:
  push:
    branches: [main]
    paths:
      - 'cloudfunctions/**'

jobs:
  deploy-cloud:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Install Cloudbase CLI
        run: npm install -g @cloudbase/cli

      - name: Deploy cloud functions
        env:
          TCB_SECRET_ID: ${{ secrets.TCB_SECRET_ID }}
          TCB_SECRET_KEY: ${{ secrets.TCB_SECRET_KEY }}
          TCB_ENV_ID: ${{ secrets.TCB_ENV_ID }}
        run: |
          tcb functions:deploy --names match,login,notify
```

### 3.3 环境配置

```yaml
# .github/workflows/env-config.yml
name: Environment Configuration

on:
  workflow_dispatch:
    inputs:
      env_name:
        description: '环境名称'
        required: true
        type: choice
        options:
          - development
          - staging
          - production

jobs:
  setup-env:
    runs-on: windows-latest
    steps:
      - name: Generate environment file
        run: |
          cat > .env.${{ github.event.inputs.env_name }} << EOF
          NODE_ENV=${{ github.event.inputs.env_name }}
          API_BASE_URL=https://api-${{ github.event.inputs.env_name }}.example.com
          CLOUD_ENV_ID=${{ secrets.CLOUD_ENV_ID }}-${{ github.event.inputs.env_name }}
          DEBUG=false
          EOF

      - name: Upload environment file
        uses: actions/upload-artifact@v4
        with:
          name: env-${{ github.event.inputs.env_name }}
          path: .env.${{ github.event.inputs.env_name }}
```

## 4. 环境变量配置

### 4.1 GitHub Secrets 配置

在 GitHub 仓库的 Settings > Secrets and variables > Actions 中配置以下密钥：

| 密钥名称 | 描述 | 示例值 |
|----------|------|--------|
| STAGING_APP_ID | 体验版 AppID | wx1234567890abcdef |
| STAGING_PRIVATE_KEY | 体验版私钥文件内容 | -----BEGIN PRIVATE KEY-----... |
| PROD_APP_ID | 正式版 AppID | wxabcdef1234567890 |
| PROD_PRIVATE_KEY | 正式版私钥文件内容 | -----BEGIN PRIVATE KEY-----... |
| TCB_SECRET_ID | 云开发 SecretId | AKIDxxxxxxxxxxxxxxxxx |
| TCB_SECRET_KEY | 云开发 SecretKey | xxxxxxxxxxxxxxxxxxxxxxxx |
| TCB_ENV_ID | 云开发环境 ID | cloud-xxxxxx |

### 4.2 本地环境变量文件

```bash
# .env.example
NODE_ENV=development
APP_ID=wx0000000000000000
PRIVATE_KEY_PATH=./keys/private.key

# 云开发配置
TCB_SECRET_ID=your_secret_id
TCB_SECRET_KEY=your_secret_key
TCB_ENV_ID=your_env_id

# API 配置
API_BASE_URL=http://localhost:3000
```

### 4.3 CI 环境变量注入

```yaml
# 工作流中注入环境变量
- name: Inject environment variables
  run: |
    echo "APP_ID=${{ secrets.STAGING_APP_ID }}" >> $GITHUB_ENV
    echo "NODE_ENV=staging" >> $GITHUB_ENV
    echo "BUILD_VERSION=${{ github.sha }}" >> $GITHUB_ENV

  - name: Build npm
    run: cli build-npm --project .
    env:
      APP_ID: ${{ env.APP_ID }}
      PRIVATE_KEY: ${{ secrets.STAGING_PRIVATE_KEY }}
```

## 5. 完整示例项目结构

```
.github/
└── workflows/
    ├── ci.yml          # 持续集成
    ├── deploy.yml      # 部署工作流
    ├── e2e.yml         # 端到端测试
    └── cloud-deploy.yml # 云函数部署

tests/
├── unit/               # 单元测试
├── e2e/                # E2E 测试
└── minium/             # Minium 自动化测试

scripts/
├── devtools-build.sh   # 构建脚本
├── deploy.sh           # 部署脚本
└── upload.sh           # 上传脚本
```

## 6. 微信开发者工具 CLI 命令参考

> **Windows**: `<安装路径>/cli.bat`
> **macOS**: `<安装路径>/Contents/MacOS/cli`

### 6.1 常用命令

| 命令 | 功能 |
|------|------|
| `cli login` | 登录（终端打印二维码） |
| `cli islogin` | 检查登录状态 |
| `cli preview --project <path>` | 生成预览二维码 |
| `cli upload --project <path> -v <ver> -d <desc>` | 上传代码 |
| `cli build-npm --project <path>` | 构建 npm |
| `cli auto --project <path>` | 开启自动化端口 |
| `cli open --project <path>` | 启动开发者工具 |
| `cli cache --clean all --project <path>` | 清除缓存 |

### 6.2 预览命令选项

```bash
cli preview --project /path/demo
cli preview --qr-format base64 --qr-output base64@/path/code.txt
cli preview --info-output /path/info.json
cli preview --compile-condition '{"pathName":"pages/index/index","query":"x=1"}'
```

### 6.3 上传命令选项

```bash
cli upload --project /path/demo -v 1.0.0 -d 'initial release'
cli upload --project /path/demo -v 1.0.0 -d '备注' -i /path/info.json
```

## 7. 最佳实践

### 7.1 分支策略

- `main`: 稳定分支，合并后自动部署至体验环境
- `develop`: 开发分支，集成测试
- `feature/*`: 功能分支，PR 合并前需通过 CI

### 7.2 版本号管理

```yaml
- name: Generate version
  id: version
  run: |
    VERSION=$(date +'%Y.%m.%d')
    echo "version=$VERSION" >> $GITHUB_OUTPUT
```

### 7.3 回滚策略

```yaml
- name: Rollback on failure
  if: failure()
  run: |
    echo "Deployment failed. Rolling back..."
    tcb fn rollback --service match --version ${{ steps.deploy.outputs.version }}
```
