#!/usr/bin/env python3
"""
FileWatcher-CLI - 动作执行器
处理文件变更后的自动响应动作（Shell命令执行、Webhook通知）
"""

import subprocess
import json
import os
import urllib.request
import urllib.error
import threading
from datetime import datetime


class ActionExecutor:
    """动作执行器 - 负责执行文件变更后的响应动作"""

    # 命令模板中可用的变量
    TEMPLATE_VARS = {
        "{{file}}": "变更文件的完整路径",
        "{{filename}}": "变更文件名",
        "{{event}}": "事件类型（created/modified/deleted/moved）",
        "{{path}}": "变更文件所在目录",
        "{{ext}}": "文件扩展名",
        "{{time}}": "事件发生时间（ISO格式）",
        "{{timestamp}}": "事件发生时间戳",
    }

    def __init__(self, max_workers=4):
        self._thread_pool = []
        self._max_workers = max_workers

    def _resolve_template(self, template, event):
        """
        解析命令模板中的变量

        Args:
            template: 命令模板字符串
            event: FileEvent对象

        Returns:
            解析后的命令字符串
        """
        filepath = event.file_path
        filename = os.path.basename(filepath)
        dirpath = os.path.dirname(filepath)
        _, ext = os.path.splitext(filepath)
        ext = ext.lstrip(".")

        replacements = {
            "{{file}}": filepath,
            "{{filename}}": filename,
            "{{event}}": event.type,
            "{{path}}": dirpath,
            "{{ext}}": ext,
            "{{time}}": event.timestamp.isoformat(),
            "{{timestamp}}": str(int(event.timestamp.timestamp())),
        }

        result = template
        for key, value in replacements.items():
            result = result.replace(key, str(value))

        return result

    def execute_command(self, cmd_template, event):
        """
        执行Shell命令

        Args:
            cmd_template: 命令模板
            event: FileEvent对象
        """
        cmd = self._resolve_template(cmd_template, event)

        def _run():
            try:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if result.returncode != 0:
                    print(
                        f"  ⚠️  命令执行失败 (exit={result.returncode}): {cmd}"
                    )
                    if result.stderr:
                        print(f"     错误: {result.stderr.strip()[:200]}")
            except subprocess.TimeoutExpired:
                print(f"  ⚠️  命令执行超时: {cmd}")
            except Exception as e:
                print(f"  ⚠️  命令执行异常: {e}")

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()

    def send_webhook(self, url, event):
        """
        发送Webhook通知

        Args:
            url: Webhook URL
            event: FileEvent对象
        """
        payload = {
            "event": event.type,
            "file": event.file_path,
            "timestamp": event.timestamp.isoformat(),
            "details": event.details,
        }

        if event.old_path:
            payload["old_path"] = event.old_path

        def _send():
            try:
                data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
                req = urllib.request.Request(
                    url,
                    data=data,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    if resp.status >= 400:
                        print(f"  ⚠️  Webhook响应异常: HTTP {resp.status}")
            except urllib.error.URLError as e:
                print(f"  ⚠️  Webhook发送失败: {e}")
            except Exception as e:
                print(f"  ⚠️  Webhook异常: {e}")

        thread = threading.Thread(target=_send, daemon=True)
        thread.start()

    @classmethod
    def get_template_help(cls):
        """获取模板变量帮助信息"""
        lines = ["📋 可用命令模板变量:"]
        for var, desc in cls.TEMPLATE_VARS.items():
            lines.append(f"  {var:20s} - {desc}")
        return "\n".join(lines)
