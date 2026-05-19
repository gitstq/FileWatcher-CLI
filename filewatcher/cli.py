#!/usr/bin/env python3
"""
FileWatcher-CLI - CLI入口模块
命令行参数解析与主程序启动
"""

import argparse
import sys
import os

from . import __version__


def create_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        prog="filewatcher",
        description="🔍 FileWatcher-CLI - 轻量级终端文件变更智能监控与自动响应引擎",
        epilog="示例: filewatcher watch ./src --pattern '*.py' --on-change 'echo {{file}} changed'",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # === watch 子命令 ===
    watch_parser = subparsers.add_parser(
        "watch",
        help="启动文件监控",
        description="监控指定目录的文件变更事件",
    )
    watch_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="要监控的目录路径（默认: 当前目录）",
    )
    watch_parser.add_argument(
        "--pattern", "-p",
        action="append",
        default=None,
        help="文件匹配模式（glob语法），可多次指定。如: '*.py' '*.js'",
    )
    watch_parser.add_argument(
        "--exclude", "-e",
        action="append",
        default=None,
        help="排除的文件/目录模式（glob语法），可多次指定。如: 'node_modules' '.git'",
    )
    watch_parser.add_argument(
        "--events",
        type=str,
        default="created,modified,deleted,moved",
        help="监控的事件类型，逗号分隔（默认: created,modified,deleted,moved）",
    )
    watch_parser.add_argument(
        "--on-change",
        action="append",
        default=None,
        help="文件变更时执行的Shell命令。可用变量: {{file}}, {{event}}, {{path}}",
    )
    watch_parser.add_argument(
        "--recursive", "-r",
        action="store_true",
        default=True,
        help="递归监控子目录（默认开启）",
    )
    watch_parser.add_argument(
        "--no-recursive",
        action="store_true",
        default=False,
        help="不递归监控子目录",
    )
    watch_parser.add_argument(
        "--debounce",
        type=float,
        default=0.1,
        help="事件去抖动间隔（秒，默认: 0.1）",
    )
    watch_parser.add_argument(
        "--webhook",
        type=str,
        default=None,
        help="Webhook通知URL，文件变更时发送POST请求",
    )
    watch_parser.add_argument(
        "--config", "-c",
        type=str,
        default=None,
        help="YAML配置文件路径",
    )
    watch_parser.add_argument(
        "--output", "-o",
        choices=["table", "json", "simple"],
        default="table",
        help="输出格式（默认: table）",
    )
    watch_parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        default=False,
        help="静默模式，仅输出事件数据",
    )

    # === init 子命令 ===
    init_parser = subparsers.add_parser(
        "init",
        help="生成配置文件模板",
        description="在当前目录生成 filewatcher.yaml 配置文件模板",
    )
    init_parser.add_argument(
        "--output", "-o",
        type=str,
        default="filewatcher.yaml",
        help="输出文件名（默认: filewatcher.yaml）",
    )

    # === stats 子命令 ===
    stats_parser = subparsers.add_parser(
        "stats",
        help="查看监控统计信息",
        description="显示当前监控会话的统计数据",
    )

    return parser


def main():
    """CLI主入口"""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "watch":
        from .watcher import FileWatcherEngine
        from .config import load_config

        # 加载配置文件（如果指定）
        config = {}
        if args.config:
            config = load_config(args.config)

        # 合并CLI参数与配置文件
        watch_path = os.path.abspath(args.path)
        patterns = args.pattern or config.get("patterns", ["*"])
        excludes = args.exclude or config.get("excludes", [
            ".git", "__pycache__", "node_modules", ".idea", ".vscode",
            "*.pyc", ".DS_Store", "Thumbs.db",
        ])
        events_str = args.events
        on_change_commands = args.on_change or config.get("on_change", [])
        recursive = not args.no_recursive
        debounce = args.debounce
        webhook_url = args.webhook or config.get("webhook_url")
        output_format = args.output
        quiet = args.quiet

        # 解析事件类型
        events = [e.strip() for e in events_str.split(",")]

        # 启动监控引擎
        engine = FileWatcherEngine(
            watch_path=watch_path,
            patterns=patterns,
            excludes=excludes,
            events=events,
            on_change_commands=on_change_commands,
            recursive=recursive,
            debounce_seconds=debounce,
            webhook_url=webhook_url,
            output_format=output_format,
            quiet=quiet,
        )

        try:
            engine.start()
        except KeyboardInterrupt:
            engine.stop()
            if not quiet:
                engine.print_summary()

    elif args.command == "init":
        from .config import generate_template
        generate_template(args.output)
        print(f"✅ 配置文件模板已生成: {args.output}")

    elif args.command == "stats":
        print("📊 监控统计功能需要配合 watch 命令使用")
        print("   使用 filewatcher watch <path> 启动监控后，按 Ctrl+C 查看统计")


if __name__ == "__main__":
    main()
