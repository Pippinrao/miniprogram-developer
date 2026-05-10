---
skill: miniprogram-developer
version: 1.0.0
updated: 2026-05-10
provides: [CLI, 命令行, 自动化构建, 脚本]
difficulty: intermediate
official: https://developers.weixin.qq.com/miniprogram/dev/devtools/cli.html
---

# 微信开发者工具 CLI 参考

微信开发者工具提供命令行界面（CLI），支持自动化构建、预览、上传等操作。

## 前提条件

1. 已安装微信开发者工具
2. 已在开发者工具中开启「服务端口」：设置 → 安全设置 → 打开「服务端口」

## 自动检测与安装

CLI 默认路径（Windows）：

```
C:\Program Files (x86)\Tencent\微信web开发者工具\cli.bat
```

**自动检测脚本：**

```powershell
# scripts/wechat-cli-detect.ps1
function Get-WeChatCLIPath {
    $defaultPaths = @(
        "${env:ProgramFiles(x86)}\Tencent\微信web开发者工具\cli.bat",
        "${env:ProgramFiles}\Tencent\微信web开发者工具\cli.bat",
        "$env:LOCALAPPDATA\微信开发者工具\cli.bat"
    )

    # 先检查环境变量
    if ($env:WECHAT_DEVTOOLS_CLI -and (Test-Path $env:WECHAT_DEVTOOLS_CLI)) {
        return $env:WECHAT_DEVTOOLS_CLI
    }

    # 遍历默认路径
    foreach ($path in $defaultPaths) {
        if (Test-Path $path) {
            return $path
        }
    }

    # 未找到，提示安装
    return $null
}

$cliPath = Get-WeChatCLIPath
if (-not $cliPath) {
    Write-Host "CLI未找到，请安装微信开发者工具"
    Write-Host "下载: https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html"
    exit 1
}
Write-Host "CLI路径: $cliPath"
```

**设置环境变量：**

```powershell
# 自动设置永久环境变量
[System.Environment]::SetEnvironmentVariable(
    'WECHAT_DEVTOOLS_CLI',
    'C:\Program Files (x86)\Tencent\微信web开发者工具\cli.bat',
    'User'
)
```

---

## 安装流程

### 方式一：安装微信开发者工具（推荐）

1. 下载微信开发者工具：https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html
2. 安装时勾选「写入 PATH」或手动添加到环境变量
3. 安装完成后确认 CLI 可用：

```powershell
& "C:\Program Files (x86)\Tencent\微信web开发者工具\cli.bat" --version
```

### 方式二：使用 CI 工具（推荐用于自动化流水线）

对于 CI/CD 流水线中的自动化构建、预览、上传，推荐使用微信官方提供的 `miniprogram-ci` npm 包：

```bash
npm install miniprogram-ci --save-dev
```

官方文档: https://developers.weixin.qq.com/miniprogram/dev/devtools/ci.html

> 注意：`miniprogram-ci` 是纯 JavaScript 实现，无需安装微信开发者工具，可在 Linux CI 环境运行。但功能与 CLI 不完全对等，预览/上传需额外配置密钥。

### 方式三：便携版迁移

如果使用便携版或自定义路径：

```powershell
# 查找 cli.bat 位置
Get-ChildItem -Path "C:\" -Recurse -Filter "cli.bat" -ErrorAction SilentlyContinue |
    Select-Object -First 1 -ExpandProperty FullName
```

---

## CLI 命令

### 打开项目

启动开发者工具并打开指定项目。

```bash
cli.bat open --project <项目路径> --lang zh
```

**示例（PowerShell）：**

```powershell
& "$env:WECHAT_DEVTOOLS_CLI" open --project "D:\workspace\my-miniprogram" --lang zh
```

**首次运行提示：** CLI 会询问是否允许，点击允许即可。

---

### 编译构建

> **适用场景**: 小游戏引擎项目。对于通用小程序编译校验，推荐使用 `miniprogram-ci` 或开发者工具内置编译。

使用开发者工具的编译引擎校验项目。

```bash
cli.bat engine build <项目路径> --logPath <日志路径> --lang zh
```

**示例：**

```bash
cli.bat engine build "D:\workspace\my-miniprogram" --logPath "D:\workspace\build.log" --lang zh
```

**用法：**
- 提交代码前做自动化校验
- CI/CD 流程中替代人工编译检查
- `--logPath` 指定日志输出路径

---

### 预览

生成预览二维码图片，用于手机扫描真机预览。

```bash
cli.bat preview --project <项目路径> --lang zh --qr-format image --qr-output <输出图片路径>
```
> 短参数 `-f image -o` 已废弃，请使用长参数 `--qr-format` 和 `--qr-output`。

**参数说明：**

| 参数 | 说明 |
|------|------|
| `-f image` | 输出格式为图片 |
| `-o` | 输出文件路径 |

**示例：**

```bash
cli.bat preview --project "D:\workspace\my-miniprogram" --lang zh -f image -o "D:\workspace\preview-qr.png"
```

---

### 上传发布

上传代码至微信后台，可指定版本号和备注。

```bash
cli.bat upload --project <项目路径> --version <版本号> --description <备注> --lang zh
```

**参数说明：**

| 参数 | 说明 |
|------|------|
| `--version` | 版本号，格式如 `1.0.0` |
| `--description` | 上传说明 |

**示例：**

```bash
cli.bat upload --project "D:\workspace\my-miniprogram" --version "1.0.0" --description "首次发布" --lang zh
```

---

## 自动化测试

### 开启自动化端口

开启自动化测试端口，用于外部自动化测试工具连接。

```bash
cli.bat auto --project <项目路径>
```

### 自动化测试回放 (实验性)

> 此子命令可能在不同版本的开发者工具中不可用。

打开自动化测试窗口并支持回放功能。

```bash
cli.bat auto-replay --project <项目路径>
```

**用途**：
- Minium 自动化测试
- 自定义自动化脚本调试
- 重复执行测试用例

### 自动预览

开启后每次编译自动生成预览二维码。

```bash
cli.bat auto-preview --project <项目路径>
```

---

## 清除缓存

清除开发者工具本地缓存，支持多种选项。

```bash
cli.bat cache --clean <选项> --project <项目路径>
```

| 选项 | 说明 |
|------|------|
| `storage` | 清除本地存储 |
| `file` | 清除文件缓存 |
| `session` | 清除会话数据 |
| `auth` | 清除登录授权信息 |
| `network` | 清除网络缓存 |
| `compile` | 清除编译缓存 |
| `all` | 清除所有缓存 |

**示例**：

```bash
# 清除所有缓存
cli.bat cache --clean all --project "D:\workspace\my-miniprogram"

# 清除编译缓存
cli.bat cache --clean compile --project "D:\workspace\my-miniprogram"
```

---

## 工具控制命令

### 重建文件监视器

当文件监视出现问题时使用。

```bash
cli.bat reset-fileutils --project <项目路径>
```

### 打开/关闭项目

```bash
# 打开项目
cli.bat open --project <项目路径>

# 关闭当前项目窗口
cli.bat close

# 退出开发者工具
cli.bat quit
```

---

## 云函数部署

微信开发者工具 CLI 提供 `cli cloud` 命令族用于云开发相关操作：

### 列出云环境
```bash
cli.bat cloud env list --project <项目路径>
```

### 云函数管理
```bash
# 上传云函数
cli.bat cloud functions deploy --project <项目路径> --name <云函数名称>

# 增量上传云函数
cli.bat cloud functions inc-deploy --project <项目路径> --name <云函数名称>

# 查看云函数信息
cli.bat cloud functions info --project <项目路径> --name <云函数名称>

# 下载云函数
cli.bat cloud functions download --project <项目路径> --name <云函数名称>

# 云函数列表
cli.bat cloud functions list --project <项目路径>
```

> 以上 `cli cloud` 命令族的可用性取决于微信开发者工具版本（需较新版本支持）。在 CI/CD 流水线中，推荐使用 `@cloudbase/cli`（`tcb fn deploy`）实现跨平台自动化部署，因为它不依赖开发者工具的 GUI 环境。

官方文档: https://developers.weixin.qq.com/miniprogram/dev/wxcloud/guide/functions/getting-started.html

---

## NPM 脚本集成

在 `package.json` 中封装 CLI 命令，便于团队统一使用。

### Windows PowerShell 脚本方式

创建 `scripts/wechat-devtools-env.ps1` 统一管理 CLI 路径（带自动检测）：

```powershell
# scripts/wechat-devtools-env.ps1
function Get-WeChatCLIPath {
    $defaultPaths = @(
        "${env:ProgramFiles(x86)}\Tencent\微信web开发者工具\cli.bat",
        "${env:ProgramFiles}\Tencent\微信web开发者工具\cli.bat",
        "$env:LOCALAPPDATA\微信开发者工具\cli.bat"
    )

    # 优先使用环境变量
    if ($env:WECHAT_DEVTOOLS_CLI -and (Test-Path $env:WECHAT_DEVTOOLS_CLI)) {
        return $env:WECHAT_DEVTOOLS_CLI
    }

    # 遍历默认路径
    foreach ($path in $defaultPaths) {
        if (Test-Path $path) {
            return $path
        }
    }

    # 未找到，抛出错误
    throw "微信开发者工具 CLI 未找到。请确认已安装微信开发者工具并设置 WECHAT_DEVTOOLS_CLI 环境变量。"
}

if (-not $env:WECHAT_DEVTOOLS_CLI) {
    $env:WECHAT_DEVTOOLS_CLI = Get-WeChatCLIPath
}
```

### 打开项目

```powershell
# scripts/wechat-open-project.ps1
. "$PSScriptRoot\wechat-devtools-env.ps1"
$proj = Resolve-Path (Join-Path $PSScriptRoot '..')

cmd /c "(echo y)|`"$env:WECHAT_DEVTOOLS_CLI`" open --project `"$proj`" --lang zh"
```

### 编译校验

```powershell
# scripts/wechat-engine-build.ps1
. "$PSScriptRoot\wechat-devtools-env.ps1"
$proj = Resolve-Path (Join-Path $PSScriptRoot '..')
$log = Join-Path $proj '.wechat-build.log'

cmd /c "(echo y)|`"$env:WECHAT_DEVTOOLS_CLI`" engine build `"$proj`" --logPath `"$log`" --lang zh"
```

### 预览二维码

```powershell
# scripts/wechat-preview-qr.ps1
. "$PSScriptRoot\wechat-devtools-env.ps1"
$proj = Resolve-Path (Join-Path $PSScriptRoot '..')
$out = Join-Path $proj '.wechat-preview-qr.png'

cmd /c "`"$env:WECHAT_DEVTOOLS_CLI`" preview --project `"$proj`" --lang zh -f image -o `"$out`""
```

### package.json 脚本

```json
{
  "scripts": {
    "devtools:open": "powershell -NoProfile -ExecutionPolicy Bypass -File scripts/wechat-open-project.ps1",
    "devtools:build": "powershell -NoProfile -ExecutionPolicy Bypass -File scripts/wechat-engine-build.ps1",
    "devtools:preview": "powershell -NoProfile -ExecutionPolicy Bypass -File scripts/wechat-preview-qr.ps1"
  }
}
```

**使用方式：**

```bash
npm run devtools:open      # 打开项目
npm run devtools:build     # 编译校验
npm run devtools:preview   # 生成预览二维码
```

---

## 常见问题

### 服务端口未开启

报错「服务端口已关闭」。

**解决：** 开发者工具 → 设置 → 安全设置 → 打开「服务端口」

### 首次运行需要确认

CLI 首次运行会询问是否允许，可通过管道自动应答：

```bash
cmd /c "(echo y)|cli.bat open ..."
```

### 环境变量未找到

检查 CLI 路径是否正确，或显式设置环境变量：

```powershell
$env:WECHAT_DEVTOOLS_CLI = "C:\Program Files (x86)\Tencent\微信web开发者工具\cli.bat"
```
