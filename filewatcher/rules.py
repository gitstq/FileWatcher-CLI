#!/usr/bin/env python3
"""
FileWatcher-CLI - 规则匹配引擎
基于glob模式匹配与排除规则过滤文件
"""

import os
from fnmatch import fnmatch
from pathlib import PurePath


class RuleEngine:
    """文件规则匹配引擎"""

    def __init__(self, patterns=None, excludes=None):
        """
        初始化规则引擎

        Args:
            patterns: 包含的文件glob模式列表（如 ['*.py', '*.js']）
            excludes: 排除的文件/目录模式列表（如 ['.git', '__pycache__']）
        """
        self.patterns = patterns or ["*"]
        self.excludes = excludes or []

    def _match_patterns(self, filepath):
        """检查文件是否匹配任一包含模式"""
        filename = os.path.basename(filepath)
        for pattern in self.patterns:
            # 支持完整路径匹配和文件名匹配
            if fnmatch(filepath, pattern) or fnmatch(filename, pattern):
                return True
        return False

    def _match_excludes(self, filepath):
        """检查文件是否匹配任一排除模式"""
        filename = os.path.basename(filepath)
        dirname = os.path.dirname(filepath)

        for pattern in self.excludes:
            # 匹配文件名
            if fnmatch(filename, pattern):
                return True
            # 匹配完整路径中的任何部分
            parts = PurePath(filepath).parts
            for part in parts:
                if fnmatch(part, pattern) or part == pattern:
                    return True
        return False

    def should_watch(self, filepath):
        """
        判断文件是否应该被监控

        规则：匹配包含模式 且 不匹配排除模式
        """
        if not self._match_patterns(filepath):
            return False
        if self._match_excludes(filepath):
            return False
        return True

    def is_excluded(self, dirpath):
        """判断目录是否被排除"""
        dirname = os.path.basename(dirpath)
        for pattern in self.excludes:
            if fnmatch(dirname, pattern) or dirname == pattern:
                return True
        return False

    def add_pattern(self, pattern):
        """添加包含模式"""
        if pattern not in self.patterns:
            self.patterns.append(pattern)

    def add_exclude(self, pattern):
        """添加排除模式"""
        if pattern not in self.excludes:
            self.excludes.append(pattern)

    def get_stats(self):
        """获取规则统计"""
        return {
            "patterns_count": len(self.patterns),
            "excludes_count": len(self.excludes),
            "patterns": self.patterns,
            "excludes": self.excludes,
        }
