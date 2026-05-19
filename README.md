<div align="center">

# 🔍 FileWatcher-CLI

**轻量级终端文件变更智能监控与自动响应引擎**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero-brightgreen.svg)]()

**零依赖 · 跨平台 · 开箱即用**

[简体中文](#-简体中文) · [繁體中文](#-繁體中文) · [English](#-english)

</div>

---

<a id="-简体中文"></a>

## 🇨🇳 简体中文

### 🎉 项目介绍

**FileWatcher-CLI** 是一款轻量级的终端文件变更智能监控与自动响应引擎，完全基于 Python 标准库开发，**零外部依赖**，开箱即用。

在日常开发中，我们经常需要监控文件变化：代码修改后自动运行测试、配置文件变更后自动重启服务、日志文件更新时实时查看……FileWatcher-CLI 就是为此而生的一站式解决方案。

💡 **灵感来源**：受到 `watchdog`、`entr`、`fswatch` 等工具的启发，但追求更极致的轻量化和零依赖体验。

### ✨ 核心特性

- 🔍 **智能文件监控** — 实时检测文件的创建、修改、删除、移动、属性变更等5种事件
- 🎯 **灵活规则引擎** — 支持 Glob 模式匹配与排除规则，精准控制监控范围
- ⚡ **自动响应动作** — 文件变更时自动执行 Shell 命令，支持丰富的模板变量
- 📡 **Webhook 通知** — 变更事件可实时推送至指定 Webhook URL
- 📊 **三种输出模式** — 美化表格、JSON 数据、简洁模式，适配不同场景
- 📝 **YAML 配置文件** — 支持持久化监控规则，一键复用
- 🎨 **终端美化输出** — 彩色事件面板、实时统计、变更热力图
- 🪶 **零依赖设计** — 纯 Python 标准库实现，无需安装任何第三方包
- 🖥️ **跨平台兼容** — 完美支持 Windows、macOS、Linux

### 🚀 快速开始

#### 环境要求

- **Python 3.8+**（无需额外依赖）

#### 安装

```bash
# 方式一：pip 安装（推荐）
pip install filewatcher-cli

# 方式二：从源码安装
git clone https://github.com/gitstq/FileWatcher-CLI.git
cd FileWatcher-CLI
pip install -e .
```

#### 基本使用

```bash
# 监控当前目录的所有文件变更
filewatcher watch .

# 监控指定目录，仅关注 Python 文件
filewatcher watch ./src --pattern '*.py'

# 监控多种文件类型
filewatcher watch ./project -p '*.py' -p '*.js' -p '*.css'

# 文件变更时自动执行命令
filewatcher watch ./src -p '*.py' --on-change 'python {{file}}'

# 排除特定目录
filewatcher watch . -p '*.py' -e 'venv' -e '__pycache__' -e '.git'

# 使用 JSON 输出（适合管道处理）
filewatcher watch . -o json -q

# 生成配置文件模板
filewatcher init
```

### 📖 详细使用指南

#### 📋 命令行参数

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `path` | — | 监控目录路径 | `.`（当前目录） |
| `--pattern` | `-p` | 文件匹配模式（可多次指定） | `*` |
| `--exclude` | `-e` | 排除模式（可多次指定） | `.git`, `__pycache__` 等 |
| `--events` | — | 监控的事件类型 | `created,modified,deleted,moved` |
| `--on-change` | — | 变更时执行的命令 | — |
| `--recursive` | `-r` | 递归监控子目录 | 开启 |
| `--no-recursive` | — | 不递归监控 | — |
| `--debounce` | — | 事件去抖动间隔（秒） | `0.1` |
| `--webhook` | — | Webhook 通知 URL | — |
| `--config` | `-c` | YAML 配置文件路径 | — |
| `--output` | `-o` | 输出格式：`table`/`json`/`simple` | `table` |
| `--quiet` | `-q` | 静默模式 | — |

#### 🔧 命令模板变量

在 `--on-change` 命令中可使用以下变量：

| 变量 | 说明 |
|------|------|
| `{{file}}` | 变更文件的完整路径 |
| `{{filename}}` | 文件名 |
| `{{event}}` | 事件类型 |
| `{{path}}` | 文件所在目录 |
| `{{ext}}` | 文件扩展名 |
| `{{time}}` | 事件时间（ISO 格式） |
| `{{timestamp}}` | Unix 时间戳 |

#### 📝 配置文件示例

```yaml
# filewatcher.yaml
patterns:
  - "*.py"
  - "*.js"
  - "*.json"

excludes:
  - ".git"
  - "__pycache__"
  - "node_modules"
  - "venv"

on_change:
  - "echo '[{{time}}] {{event}}: {{file}}'"

debounce: 0.1
recursive: true
```

使用配置文件启动：

```bash
filewatcher watch . -c filewatcher.yaml
```

#### 💡 典型使用场景

**1. 代码修改后自动运行测试**
```bash
filewatcher watch ./src -p '*.py' --on-change 'pytest tests/'
```

**2. Markdown 文件变更后自动生成文档**
```bash
filewatcher watch ./docs -p '*.md' --on-change 'mkdocs build'
```

**3. 配合 Webhook 实现团队通知**
```bash
filewatcher watch ./config -p '*.yaml' --webhook 'https://hooks.slack.com/xxx'
```

**4. CI/CD 中监控构建产物**
```bash
filewatcher watch ./dist -o json -q | python3 process_events.py
```

### 💡 设计思路与迭代规划

#### 设计理念

- **零依赖优先**：纯标准库实现，降低安装门槛，避免供应链风险
- **规则驱动**：灵活的匹配/排除规则引擎，适应各种监控场景
- **事件驱动架构**：文件变更 → 规则匹配 → 动作执行，清晰的数据流
- **开发者友好**：丰富的输出格式、模板变量、配置文件支持

#### 后续迭代计划

- [ ] 🔔 支持邮件通知渠道
- [ ] 📊 Web Dashboard 实时监控面板
- [ ] 🔌 插件系统，支持自定义动作扩展
- [ ] 📁 支持目录级别的批量监控规则
- [ ] 🎯 正则表达式模式匹配支持
- [ ] 🔄 文件变更历史回放功能

### 📦 打包与部署指南

#### 本地开发

```bash
# 克隆仓库
git clone https://github.com/gitstq/FileWatcher-CLI.git
cd FileWatcher-CLI

# 开发模式安装
pip install -e .

# 运行测试
python3 -m unittest tests.test_filewatcher -v
```

#### 构建 PyPI 包

```bash
python3 -m build
twine upload dist/*
```

### 🤝 贡献指南

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

- 🐛 **Bug 报告**：请提交 Issue，附上复现步骤
- 💡 **功能建议**：欢迎提交 Issue 讨论
- 🔧 **代码贡献**：Fork → 分支 → PR，遵循 Conventional Commits 规范

### 📄 开源协议

本项目基于 [MIT License](LICENSE) 开源，可自由使用、修改和分发。

---

<a id="-繁體中文"></a>

## 🇹🇼 繁體中文

### 🎉 專案介紹

**FileWatcher-CLI** 是一款輕量級的終端檔案變更智慧監控與自動回應引擎，完全基於 Python 標準函式庫開發，**零外部依賴**，開箱即用。

在日常開發中，我們經常需要監控檔案變化：程式碼修改後自動執行測試、設定檔變更後自動重啟服務、日誌檔案更新時即時檢視……FileWatcher-CLI 就是為此而生的一站式解決方案。

💡 **靈感來源**：受到 `watchdog`、`entr`、`fswatch` 等工具的啟發，但追求更極致的輕量化和零依賴體驗。

### ✨ 核心特性

- 🔍 **智慧檔案監控** — 即時偵測檔案的建立、修改、刪除、移動、屬性變更等5種事件
- 🎯 **靈活規則引擎** — 支援 Glob 模式比對與排除規則，精準控制監控範圍
- ⚡ **自動回應動作** — 檔案變更時自動執行 Shell 命令，支援豐富的模板變數
- 📡 **Webhook 通知** — 變更事件可即時推送至指定 Webhook URL
- 📊 **三種輸出模式** — 美化表格、JSON 資料、簡潔模式，適配不同場景
- 📝 **YAML 設定檔** — 支援持久化監控規則，一鍵復用
- 🎨 **終端美化輸出** — 彩色事件面板、即時統計、變更熱力圖
- 🪶 **零依賴設計** — 純 Python 標準函式庫實現，無需安裝任何第三方套件
- 🖥️ **跨平台相容** — 完美支援 Windows、macOS、Linux

### 🚀 快速開始

#### 環境需求

- **Python 3.8+**（無需額外依賴）

#### 安裝

```bash
# 方式一：pip 安裝（推薦）
pip install filewatcher-cli

# 方式二：從原始碼安裝
git clone https://github.com/gitstq/FileWatcher-CLI.git
cd FileWatcher-CLI
pip install -e .
```

#### 基本使用

```bash
# 監控當前目錄的所有檔案變更
filewatcher watch .

# 監控指定目錄，僅關注 Python 檔案
filewatcher watch ./src --pattern '*.py'

# 監控多種檔案類型
filewatcher watch ./project -p '*.py' -p '*.js' -p '*.css'

# 檔案變更時自動執行命令
filewatcher watch ./src -p '*.py' --on-change 'python {{file}}'

# 排除特定目錄
filewatcher watch . -p '*.py' -e 'venv' -e '__pycache__' -e '.git'

# 使用 JSON 輸出（適合管道處理）
filewatcher watch . -o json -q

# 產生設定檔模板
filewatcher init
```

### 📖 詳細使用指南

#### 📋 命令列參數

| 參數 | 簡寫 | 說明 | 預設值 |
|------|------|------|--------|
| `path` | — | 監控目錄路徑 | `.`（當前目錄） |
| `--pattern` | `-p` | 檔案比對模式（可多次指定） | `*` |
| `--exclude` | `-e` | 排除模式（可多次指定） | `.git`, `__pycache__` 等 |
| `--events` | — | 監控的事件類型 | `created,modified,deleted,moved` |
| `--on-change` | — | 變更時執行的命令 | — |
| `--recursive` | `-r` | 遞迴監控子目錄 | 開啟 |
| `--no-recursive` | — | 不遞迴監控 | — |
| `--debounce` | — | 事件去抖動間隔（秒） | `0.1` |
| `--webhook` | — | Webhook 通知 URL | — |
| `--config` | `-c` | YAML 設定檔路徑 | — |
| `--output` | `-o` | 輸出格式：`table`/`json`/`simple` | `table` |
| `--quiet` | `-q` | 靜默模式 | — |

#### 🔧 命令模板變數

在 `--on-change` 命令中可使用以下變數：

| 變數 | 說明 |
|------|------|
| `{{file}}` | 變更檔案的完整路徑 |
| `{{filename}}` | 檔案名稱 |
| `{{event}}` | 事件類型 |
| `{{path}}` | 檔案所在目錄 |
| `{{ext}}` | 檔案副檔名 |
| `{{time}}` | 事件時間（ISO 格式） |
| `{{timestamp}}` | Unix 時間戳 |

#### 📝 設定檔範例

```yaml
# filewatcher.yaml
patterns:
  - "*.py"
  - "*.js"
  - "*.json"

excludes:
  - ".git"
  - "__pycache__"
  - "node_modules"
  - "venv"

on_change:
  - "echo '[{{time}}] {{event}}: {{file}}'"

debounce: 0.1
recursive: true
```

使用設定檔啟動：

```bash
filewatcher watch . -c filewatcher.yaml
```

#### 💡 典型使用場景

**1. 程式碼修改後自動執行測試**
```bash
filewatcher watch ./src -p '*.py' --on-change 'pytest tests/'
```

**2. Markdown 檔案變更後自動產生文件**
```bash
filewatcher watch ./docs -p '*.md' --on-change 'mkdocs build'
```

**3. 配合 Webhook 實現團隊通知**
```bash
filewatcher watch ./config -p '*.yaml' --webhook 'https://hooks.slack.com/xxx'
```

**4. CI/CD 中監控建構產物**
```bash
filewatcher watch ./dist -o json -q | python3 process_events.py
```

### 💡 設計思路與迭代規劃

#### 設計理念

- **零依賴優先**：純標準函式庫實現，降低安裝門檻，避免供應鏈風險
- **規則驅動**：靈活的比對/排除規則引擎，適應各種監控場景
- **事件驅動架構**：檔案變更 → 規則比對 → 動作執行，清晰的資料流
- **開發者友善**：豐富的輸出格式、模板變數、設定檔支援

#### 後續迭代計畫

- [ ] 🔔 支援電子郵件通知管道
- [ ] 📊 Web Dashboard 即時監控面板
- [ ] 🔌 外掛系統，支援自訂動作擴充
- [ ] 📁 支援目錄層級的批次監控規則
- [ ] 🎯 正規表示式模式比對支援
- [ ] 🔄 檔案變更歷史回放功能

### 📦 打包與部署指南

#### 本地開發

```bash
# 複製儲存庫
git clone https://github.com/gitstq/FileWatcher-CLI.git
cd FileWatcher-CLI

# 開發模式安裝
pip install -e .

# 執行測試
python3 -m unittest tests.test_filewatcher -v
```

#### 建構 PyPI 套件

```bash
python3 -m build
twine upload dist/*
```

### 🤝 貢獻指南

歡迎貢獻！請查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解詳情。

- 🐛 **Bug 回報**：請提交 Issue，附上重現步驟
- 💡 **功能建議**：歡迎提交 Issue 討論
- 🔧 **程式碼貢獻**：Fork → 分支 → PR，遵循 Conventional Commits 規範

### 📄 開源授權

本專案基於 [MIT License](LICENSE) 開源，可自由使用、修改和分發。

---

<a id="english"></a>

## 🇬🇧 English

### 🎉 Introduction

**FileWatcher-CLI** is a lightweight terminal file change intelligent monitoring and auto-response engine, built entirely on the Python standard library with **zero external dependencies** — ready to use out of the box.

In daily development, we often need to monitor file changes: auto-run tests after code modifications, restart services when config files change, or watch log files in real-time. FileWatcher-CLI is the all-in-one solution designed for exactly these scenarios.

💡 **Inspired by** tools like `watchdog`, `entr`, and `fswatch`, but pursuing the ultimate lightweight and zero-dependency experience.

### ✨ Core Features

- 🔍 **Intelligent File Monitoring** — Real-time detection of 5 event types: create, modify, delete, move, and attribute changes
- 🎯 **Flexible Rule Engine** — Glob pattern matching and exclusion rules for precise monitoring scope control
- ⚡ **Auto-Response Actions** — Automatically execute Shell commands on file changes with rich template variables
- 📡 **Webhook Notifications** — Push change events to any Webhook URL in real-time
- 📊 **Three Output Modes** — Beautiful table, JSON data, and simple mode for different scenarios
- 📝 **YAML Configuration** — Persistent monitoring rules with one-click reuse
- 🎨 **Beautiful Terminal Output** — Colored event panels, real-time statistics, and change heatmaps
- 🪶 **Zero Dependencies** — Pure Python standard library implementation, no third-party packages required
- 🖥️ **Cross-Platform** — Full support for Windows, macOS, and Linux

### 🚀 Quick Start

#### Requirements

- **Python 3.8+** (no additional dependencies needed)

#### Installation

```bash
# Option 1: pip install (recommended)
pip install filewatcher-cli

# Option 2: Install from source
git clone https://github.com/gitstq/FileWatcher-CLI.git
cd FileWatcher-CLI
pip install -e .
```

#### Basic Usage

```bash
# Watch all file changes in the current directory
filewatcher watch .

# Watch a specific directory, only Python files
filewatcher watch ./src --pattern '*.py'

# Watch multiple file types
filewatcher watch ./project -p '*.py' -p '*.js' -p '*.css'

# Auto-execute command on file change
filewatcher watch ./src -p '*.py' --on-change 'python {{file}}'

# Exclude specific directories
filewatcher watch . -p '*.py' -e 'venv' -e '__pycache__' -e '.git'

# JSON output (ideal for piping)
filewatcher watch . -o json -q

# Generate config file template
filewatcher init
```

### 📖 Detailed Usage Guide

#### 📋 Command Line Arguments

| Argument | Short | Description | Default |
|----------|-------|-------------|---------|
| `path` | — | Directory to watch | `.` (current dir) |
| `--pattern` | `-p` | File glob pattern (can specify multiple) | `*` |
| `--exclude` | `-e` | Exclude pattern (can specify multiple) | `.git`, `__pycache__`, etc. |
| `--events` | — | Event types to monitor | `created,modified,deleted,moved` |
| `--on-change` | — | Command to execute on change | — |
| `--recursive` | `-r` | Recursively watch subdirectories | Enabled |
| `--no-recursive` | — | Disable recursive watching | — |
| `--debounce` | — | Event debounce interval (seconds) | `0.1` |
| `--webhook` | — | Webhook notification URL | — |
| `--config` | `-c` | YAML config file path | — |
| `--output` | `-o` | Output format: `table`/`json`/`simple` | `table` |
| `--quiet` | `-q` | Quiet mode | — |

#### 🔧 Command Template Variables

Use these variables in `--on-change` commands:

| Variable | Description |
|----------|-------------|
| `{{file}}` | Full path of the changed file |
| `{{filename}}` | File name |
| `{{event}}` | Event type |
| `{{path}}` | Directory containing the file |
| `{{ext}}` | File extension |
| `{{time}}` | Event time (ISO format) |
| `{{timestamp}}` | Unix timestamp |

#### 📝 Configuration File Example

```yaml
# filewatcher.yaml
patterns:
  - "*.py"
  - "*.js"
  - "*.json"

excludes:
  - ".git"
  - "__pycache__"
  - "node_modules"
  - "venv"

on_change:
  - "echo '[{{time}}] {{event}}: {{file}}'"

debounce: 0.1
recursive: true
```

Launch with config file:

```bash
filewatcher watch . -c filewatcher.yaml
```

#### 💡 Typical Use Cases

**1. Auto-run tests after code changes**
```bash
filewatcher watch ./src -p '*.py' --on-change 'pytest tests/'
```

**2. Auto-build docs on Markdown changes**
```bash
filewatcher watch ./docs -p '*.md' --on-change 'mkdocs build'
```

**3. Team notifications via Webhook**
```bash
filewatcher watch ./config -p '*.yaml' --webhook 'https://hooks.slack.com/xxx'
```

**4. Monitor build artifacts in CI/CD**
```bash
filewatcher watch ./dist -o json -q | python3 process_events.py
```

### 💡 Design Philosophy & Roadmap

#### Design Philosophy

- **Zero-Dependency First**: Pure standard library implementation reduces installation barriers and supply chain risks
- **Rule-Driven**: Flexible match/exclude rule engine adapts to various monitoring scenarios
- **Event-Driven Architecture**: File change → Rule matching → Action execution, a clear data flow
- **Developer-Friendly**: Rich output formats, template variables, and config file support

#### Roadmap

- [ ] 🔔 Email notification channel support
- [ ] 📊 Web Dashboard for real-time monitoring
- [ ] 🔌 Plugin system for custom action extensions
- [ ] 📁 Directory-level batch monitoring rules
- [ ] 🎯 Regex pattern matching support
- [ ] 🔄 File change history playback

### 📦 Build & Deployment

#### Local Development

```bash
# Clone the repository
git clone https://github.com/gitstq/FileWatcher-CLI.git
cd FileWatcher-CLI

# Install in development mode
pip install -e .

# Run tests
python3 -m unittest tests.test_filewatcher -v
```

#### Build PyPI Package

```bash
python3 -m build
twine upload dist/*
```

### 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

- 🐛 **Bug Reports**: Please submit an Issue with reproduction steps
- 💡 **Feature Suggestions**: Open an Issue for discussion
- 🔧 **Code Contributions**: Fork → Branch → PR, following Conventional Commits

### 📄 License

This project is licensed under the [MIT License](LICENSE) — free to use, modify, and distribute.

---

<div align="center">

**⭐ If this project helps you, please give it a Star! ⭐**

Made with ❤️ by SoloBot

</div>
