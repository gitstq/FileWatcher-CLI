#!/usr/bin/env python3
"""
FileWatcher-CLI - 配置文件管理
支持YAML配置文件的加载、解析与模板生成
"""

import os
import sys


def _parse_yaml_simple(text):
    """
    简易YAML解析器（零依赖）
    仅支持 FileWatcher-CLI 所需的配置格式
    """
    result = {}
    current_section = result
    current_key = None
    current_list = None

    for line in text.split("\n"):
        stripped = line.strip()

        # 跳过空行和注释
        if not stripped or stripped.startswith("#"):
            continue

        # 计算缩进级别
        indent = len(line) - len(line.lstrip())

        # 顶级键值对
        if indent == 0 and ":" in stripped:
            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip()

            if value:
                # 简单键值对
                if value.startswith("[") and value.endswith("]"):
                    # 内联列表
                    items = value[1:-1].split(",")
                    result[key] = [
                        item.strip().strip("'\"") for item in items if item.strip()
                    ]
                elif value.lower() in ("true", "false"):
                    result[key] = value.lower() == "true"
                elif value.isdigit():
                    result[key] = int(value)
                else:
                    try:
                        result[key] = float(value)
                    except ValueError:
                        result[key] = value.strip("'\"")
            else:
                # 可能是列表或字典
                current_key = key
                current_section = result
                current_list = None

        # 列表项
        elif stripped.startswith("- ") and current_key:
            if current_key not in current_section:
                current_section[current_key] = []
            item_value = stripped[2:].strip().strip("'\"")
            current_section[current_key].append(item_value)
            current_list = current_section[current_key]

    return result


def load_config(config_path):
    """
    加载YAML配置文件

    Args:
        config_path: 配置文件路径

    Returns:
        解析后的配置字典
    """
    if not os.path.exists(config_path):
        print(f"⚠️  配置文件不存在: {config_path}")
        return {}

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read()

        config = _parse_yaml_simple(content)
        return config

    except Exception as e:
        print(f"⚠️  配置文件解析失败: {e}")
        return {}


def generate_template(output_path="filewatcher.yaml"):
    """
    生成配置文件模板

    Args:
        output_path: 输出文件路径
    """
    template = """# FileWatcher-CLI 配置文件
# FileWatcher-CLI Configuration File
# https://github.com/gitstq/FileWatcher-CLI

# 监控的文件模式（glob语法）
# File patterns to watch (glob syntax)
patterns:
  - "*.py"
  - "*.js"
  - "*.ts"
  - "*.json"
  - "*.yaml"
  - "*.yml"
  - "*.md"
  - "*.txt"
  - "*.html"
  - "*.css"

# 排除的文件/目录模式
# Patterns to exclude
excludes:
  - ".git"
  - "__pycache__"
  - "node_modules"
  - ".idea"
  - ".vscode"
  - "venv"
  - ".venv"
  - "dist"
  - "build"
  - "*.pyc"
  - ".DS_Store"
  - "Thumbs.db"
  - "*.tmp"
  - "*.log"

# 文件变更时执行的命令（支持模板变量）
# Commands to execute on file change (supports template variables)
# 可用变量: {{file}}, {{filename}}, {{event}}, {{path}}, {{ext}}, {{time}}
on_change:
  - "echo '[{{time}}] {{event}}: {{file}}'"

# Webhook通知URL（可选）
# Webhook notification URL (optional)
# webhook_url: "https://hooks.example.com/filewatcher"

# 事件去抖动间隔（秒）
# Event debounce interval (seconds)
debounce: 0.1

# 是否递归监控子目录
# Whether to watch subdirectories recursively
recursive: true
"""

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(template)
    except Exception as e:
        print(f"❌ 生成配置文件失败: {e}")
        sys.exit(1)
