#!/usr/bin/env python3
"""
FileWatcher-CLI - 终端美化输出管理
支持表格、JSON、简洁三种输出模式
"""

import sys
import json
from datetime import datetime


class DisplayManager:
    """终端显示管理器"""

    # ANSI颜色代码
    COLORS = {
        "reset": "\033[0m",
        "bold": "\033[1m",
        "dim": "\033[2m",
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "bg_red": "\033[41m",
        "bg_green": "\033[42m",
        "bg_blue": "\033[44m",
    }

    # 事件类型对应的图标和颜色
    EVENT_STYLES = {
        "created": ("✨", "green"),
        "modified": ("📝", "yellow"),
        "deleted": ("🗑️", "red"),
        "moved": ("📦", "blue"),
        "attribute": ("🔧", "magenta"),
    }

    def __init__(self, output_format="table", quiet=False):
        self.output_format = output_format
        self.quiet = quiet
        self._supports_color = self._check_color_support()

    def _check_color_support(self):
        """检测终端是否支持颜色"""
        if sys.platform == "win32":
            return os.environ.get("ANSICON") is not None
        return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

    def _colorize(self, text, color):
        """添加颜色"""
        if not self._supports_color:
            return text
        return f"{self.COLORS.get(color, '')}{text}{self.COLORS['reset']}"

    def _format_size(self, size_bytes):
        """格式化文件大小"""
        if size_bytes < 0:
            return f"{size_bytes}B"
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f}TB"

    def _format_time(self, dt):
        """格式化时间"""
        return dt.strftime("%H:%M:%S")

    def print_header(self, watch_path, file_count, patterns, events):
        """打印监控启动头部信息"""
        if self.quiet:
            return

        if self.output_format == "json":
            header = {
                "status": "started",
                "watch_path": watch_path,
                "file_count": file_count,
                "patterns": patterns,
                "events": events,
            }
            print(json.dumps(header, ensure_ascii=False))
            return

        # 表格/简洁模式
        print()
        print(self._colorize("╔══════════════════════════════════════════════════════════╗", "cyan"))
        print(self._colorize("║  🔍 FileWatcher-CLI - 文件变更智能监控引擎已启动          ║", "cyan"))
        print(self._colorize("╚══════════════════════════════════════════════════════════╝", "cyan"))
        print()
        print(f"  📂 监控目录:  {self._colorize(watch_path, 'bold')}")
        print(f"  📄 已索引文件: {self._colorize(str(file_count), 'green')} 个")
        print(f"  🔎 匹配模式:  {', '.join(patterns)}")
        print(f"  📡 监控事件:  {', '.join(events)}")
        print()
        print(self._colorize("  ⏳ 等待文件变更... (按 Ctrl+C 停止监控)", "dim"))
        print(self._colorize("  " + "─" * 56, "dim"))
        print()

    def print_event(self, event):
        """打印单个文件变更事件"""
        if self.output_format == "json":
            print(event.to_json())
            sys.stdout.flush()
            return

        icon, color = self.EVENT_STYLES.get(event.type, ("📄", "white"))
        time_str = self._format_time(event.timestamp)

        if self.output_format == "simple":
            print(f"[{time_str}] {icon} {event.type:10s} {event.file_path}")
            sys.stdout.flush()
            return

        # 表格模式 - 美化输出
        rel_path = event.file_path
        details_str = ""
        if event.details:
            if "new_size" in event.details:
                old_s = self._format_size(event.details.get("old_size", 0))
                new_s = self._format_size(event.details["new_size"])
                diff = event.details.get("size_diff", 0)
                diff_sign = "+" if diff >= 0 else ""
                details_str = f" ({old_s} → {new_s}, {diff_sign}{self._format_size(abs(diff))})"
            elif "size" in event.details:
                details_str = f" (大小: {self._format_size(event.details['size'])})"

        event_colored = self._colorize(f"{event.type:10s}", color)
        print(
            f"  {icon}  {self._colorize(time_str, 'dim')}  "
            f"{event_colored}  {self._colorize(rel_path, 'bold')}"
            f"{self._colorize(details_str, 'dim')}"
        )
        sys.stdout.flush()

    def print_error(self, message):
        """打印错误信息"""
        print(self._colorize(f"  ❌ {message}", "red"), file=sys.stderr)

    def print_summary(self, stats, event_history):
        """打印监控统计摘要"""
        if self.quiet and self.output_format == "json":
            summary = {
                "status": "stopped",
                "stats": {k: v for k, v in stats.items()},
                "total_events": stats.get("total_events", 0),
            }
            print(json.dumps(summary, ensure_ascii=False, default=str))
            return

        print()
        print(self._colorize("  " + "─" * 56, "dim"))
        print()
        print(self._colorize("  📊 监控统计摘要", "bold"))
        print()

        start_time = stats.get("start_time", "N/A")
        end_time = stats.get("end_time", "N/A")
        total = stats.get("total_events", 0)

        if isinstance(start_time, datetime) and isinstance(end_time, datetime):
            duration = (end_time - start_time).total_seconds()
            duration_str = f"{duration:.1f}秒"
        else:
            duration_str = "N/A"

        print(f"  ⏱️  监控时长:  {duration_str}")
        print(f"  📊 总事件数:  {self._colorize(str(total), 'bold')} 次")
        print()

        # 各类型事件统计
        event_types = ["created", "modified", "deleted", "moved", "attribute"]
        for etype in event_types:
            count = stats.get(etype, 0)
            if count > 0:
                icon, color = self.EVENT_STYLES.get(etype, ("📄", "white"))
                bar = "█" * min(count, 30)
                print(
                    f"  {icon}  {etype:10s}  "
                    f"{self._colorize(str(count), color):>5s} 次  "
                    f"{self._colorize(bar, color)}"
                )

        # 变更最频繁的文件（Top 5）
        if event_history:
            file_counts = {}
            for ev in event_history:
                file_counts[ev.file_path] = file_counts.get(ev.file_path, 0) + 1

            sorted_files = sorted(file_counts.items(), key=lambda x: x[1], reverse=True)
            if sorted_files:
                print()
                print(self._colorize("  🔥 变更最频繁的文件:", "bold"))
                for filepath, count in sorted_files[:5]:
                    filename = filepath.split("/")[-1].split("\\")[-1]
                    print(f"     {self._colorize(str(count), 'yellow'):>3s} 次  {filename}")

        print()
        print(self._colorize("  👋 监控已停止，感谢使用 FileWatcher-CLI！", "cyan"))
        print()


# 导入os模块（用于颜色检测）
import os
