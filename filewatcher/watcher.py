#!/usr/bin/env python3
"""
FileWatcher-CLI - 文件系统监控核心引擎
基于轮询机制实现跨平台文件变更检测
"""

import os
import time
import hashlib
import threading
import subprocess
import json
import urllib.request
import urllib.error
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from fnmatch import fnmatch

from .rules import RuleEngine
from .actions import ActionExecutor
from .display import DisplayManager


class FileInfo:
    """文件信息快照"""

    __slots__ = ("path", "size", "mtime", "exists", "checksum")

    def __init__(self, path):
        self.path = str(path)
        self.exists = os.path.exists(self.path)
        if self.exists and os.path.isfile(self.path):
            try:
                stat = os.stat(self.path)
                self.size = stat.st_size
                self.mtime = stat.st_mtime
                self.checksum = self._quick_checksum()
            except (OSError, PermissionError):
                self.size = 0
                self.mtime = 0
                self.checksum = ""
        else:
            self.size = 0
            self.mtime = 0
            self.checksum = ""

    def _quick_checksum(self):
        """快速文件校验（仅读取前8KB用于快速比对）"""
        try:
            with open(self.path, "rb") as f:
                data = f.read(8192)
            return hashlib.md5(data).hexdigest()
        except (OSError, PermissionError):
            return ""


class FileEvent:
    """文件变更事件"""

    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"
    MOVED = "moved"
    ATTRIBUTE = "attribute"

    def __init__(self, event_type, file_path, old_path=None, details=None):
        self.type = event_type
        self.file_path = str(file_path)
        self.old_path = str(old_path) if old_path else None
        self.details = details or {}
        self.timestamp = datetime.now()

    def to_dict(self):
        """转换为字典"""
        result = {
            "type": self.type,
            "file": self.file_path,
            "timestamp": self.timestamp.isoformat(),
        }
        if self.old_path:
            result["old_path"] = self.old_path
        if self.details:
            result["details"] = self.details
        return result

    def to_json(self):
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False)


class FileWatcherEngine:
    """文件监控引擎核心"""

    # 默认排除目录
    DEFAULT_EXCLUDES = [
        ".git", "__pycache__", "node_modules", ".idea", ".vscode",
        ".svn", ".hg", "venv", ".venv", "env", ".env",
        "dist", "build", ".next", ".nuxt", "target",
        "*.pyc", ".DS_Store", "Thumbs.db", "*.tmp",
    ]

    def __init__(
        self,
        watch_path,
        patterns=None,
        excludes=None,
        events=None,
        on_change_commands=None,
        recursive=True,
        debounce_seconds=0.1,
        webhook_url=None,
        output_format="table",
        quiet=False,
    ):
        self.watch_path = watch_path
        self.patterns = patterns or ["*"]
        self.excludes = excludes or self.DEFAULT_EXCLUDES
        self.events = events or ["created", "modified", "deleted", "moved"]
        self.on_change_commands = on_change_commands or []
        self.recursive = recursive
        self.debounce_seconds = debounce_seconds
        self.webhook_url = webhook_url
        self.output_format = output_format
        self.quiet = quiet

        # 内部状态
        self._snapshot = {}  # path -> FileInfo
        self._running = False
        self._lock = threading.Lock()

        # 统计信息
        self.stats = defaultdict(int)
        self.stats["start_time"] = None
        self.stats["total_events"] = 0
        self.event_history = []

        # 子模块
        self.rule_engine = RuleEngine(self.patterns, self.excludes)
        self.action_executor = ActionExecutor()
        self.display = DisplayManager(output_format, quiet)

    def _should_watch(self, path):
        """判断文件是否应被监控"""
        return self.rule_engine.should_watch(path)

    def _scan_directory(self):
        """扫描目录，返回当前文件快照"""
        current = {}
        try:
            if self.recursive:
                for root, dirs, files in os.walk(self.watch_path):
                    # 过滤排除的目录（原地修改dirs列表以阻止os.walk进入）
                    dirs[:] = [
                        d for d in dirs
                        if not self.rule_engine.is_excluded(os.path.join(root, d))
                    ]
                    for filename in files:
                        filepath = os.path.join(root, filename)
                        if self._should_watch(filepath):
                            current[filepath] = FileInfo(filepath)
            else:
                for entry in os.listdir(self.watch_path):
                    filepath = os.path.join(self.watch_path, entry)
                    if os.path.isfile(filepath) and self._should_watch(filepath):
                        current[filepath] = FileInfo(filepath)
        except (OSError, PermissionError) as e:
            if not self.quiet:
                self.display.print_error(f"扫描目录失败: {e}")
        return current

    def _detect_changes(self, current):
        """对比快照，检测文件变更"""
        changes = []
        old_paths = set(self._snapshot.keys())
        new_paths = set(current.keys())

        # 新增文件
        for path in new_paths - old_paths:
            if "created" in self.events:
                changes.append(FileEvent(
                    FileEvent.CREATED, path,
                    details={"size": current[path].size}
                ))

        # 删除文件
        for path in old_paths - new_paths:
            if "deleted" in self.events:
                changes.append(FileEvent(
                    FileEvent.DELETED, path,
                    details={"last_size": self._snapshot[path].size}
                ))

        # 修改文件（对比mtime和checksum）
        for path in old_paths & new_paths:
            old_info = self._snapshot[path]
            new_info = current[path]
            if old_info.checksum != new_info.checksum:
                if "modified" in self.events:
                    size_diff = new_info.size - old_info.size
                    changes.append(FileEvent(
                        FileEvent.MODIFIED, path,
                        details={
                            "old_size": old_info.size,
                            "new_size": new_info.size,
                            "size_diff": size_diff,
                        }
                    ))

        return changes

    def _handle_event(self, event):
        """处理单个文件变更事件"""
        # 更新统计
        self.stats["total_events"] += 1
        self.stats[event.type] += 1
        self.event_history.append(event)

        # 显示事件
        self.display.print_event(event)

        # 执行自定义命令
        for cmd_template in self.on_change_commands:
            self.action_executor.execute_command(
                cmd_template, event
            )

        # 发送Webhook通知
        if self.webhook_url:
            self.action_executor.send_webhook(
                self.webhook_url, event
            )

    def _watch_loop(self):
        """监控主循环"""
        while self._running:
            try:
                current = self._scan_directory()
                changes = self._detect_changes(current)

                # 去抖动处理
                if changes:
                    time.sleep(self.debounce_seconds)
                    # 重新扫描确认变更
                    current_confirmed = self._scan_directory()
                    changes_confirmed = self._detect_changes(current_confirmed)
                    with self._lock:
                        self._snapshot = current_confirmed
                    for event in changes_confirmed:
                        self._handle_event(event)
                else:
                    with self._lock:
                        self._snapshot = current

                # 轮询间隔
                time.sleep(0.5)

            except Exception as e:
                if not self.quiet:
                    self.display.print_error(f"监控异常: {e}")
                time.sleep(1)

    def start(self):
        """启动文件监控"""
        if not os.path.isdir(self.watch_path):
            self.display.print_error(f"目录不存在: {self.watch_path}")
            return

        self._running = True
        self.stats["start_time"] = datetime.now()

        # 初始快照
        self._snapshot = self._scan_directory()

        self.display.print_header(
            self.watch_path,
            len(self._snapshot),
            self.patterns,
            self.events,
        )

        try:
            self._watch_loop()
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """停止文件监控"""
        self._running = False
        self.stats["end_time"] = datetime.now()

    def print_summary(self):
        """打印监控统计摘要"""
        self.display.print_summary(self.stats, self.event_history)
