#!/usr/bin/env python3
"""
FileWatcher-CLI - 单元测试
"""

import os
import sys
import tempfile
import time
import unittest

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from filewatcher.rules import RuleEngine
from filewatcher.actions import ActionExecutor
from filewatcher.watcher import FileEvent, FileInfo
from filewatcher.config import _parse_yaml_simple, generate_template


class TestRuleEngine(unittest.TestCase):
    """规则引擎测试"""

    def setUp(self):
        self.engine = RuleEngine(
            patterns=["*.py", "*.js", "*.txt"],
            excludes=[".git", "__pycache__", "*.pyc"],
        )

    def test_should_watch_matching_file(self):
        """测试匹配的文件应被监控"""
        self.assertTrue(self.engine.should_watch("/project/main.py"))
        self.assertTrue(self.engine.should_watch("/project/app.js"))
        self.assertTrue(self.engine.should_watch("/project/readme.txt"))

    def test_should_not_watch_non_matching_file(self):
        """测试不匹配的文件不应被监控"""
        self.assertFalse(self.engine.should_watch("/project/image.png"))
        self.assertFalse(self.engine.should_watch("/project/data.csv"))

    def test_should_not_watch_excluded_file(self):
        """测试被排除的文件不应被监控"""
        self.assertFalse(self.engine.should_watch("/project/__pycache__/module.pyc"))
        self.assertFalse(self.engine.should_watch("/project/.git/config"))

    def test_is_excluded_dir(self):
        """测试目录排除"""
        self.assertTrue(self.engine.is_excluded("/project/.git"))
        self.assertTrue(self.engine.is_excluded("/project/__pycache__"))
        self.assertFalse(self.engine.is_excluded("/project/src"))

    def test_wildcard_pattern(self):
        """测试通配符模式"""
        engine = RuleEngine(patterns=["*"], excludes=[])
        self.assertTrue(engine.should_watch("/project/any_file.txt"))

    def test_add_pattern(self):
        """测试添加模式"""
        self.engine.add_pattern("*.go")
        self.assertTrue(self.engine.should_watch("/project/main.go"))

    def test_add_exclude(self):
        """测试添加排除规则"""
        self.engine.add_exclude("vendor")
        self.assertTrue(self.engine.is_excluded("/project/vendor"))


class TestFileEvent(unittest.TestCase):
    """文件事件测试"""

    def test_event_creation(self):
        """测试事件创建"""
        event = FileEvent(FileEvent.CREATED, "/test/file.py")
        self.assertEqual(event.type, "created")
        self.assertEqual(event.file_path, "/test/file.py")
        self.assertIsNone(event.old_path)

    def test_event_to_dict(self):
        """测试事件转字典"""
        event = FileEvent(FileEvent.MODIFIED, "/test/file.py", details={"size": 100})
        d = event.to_dict()
        self.assertEqual(d["type"], "modified")
        self.assertEqual(d["file"], "/test/file.py")
        self.assertEqual(d["details"]["size"], 100)

    def test_event_to_json(self):
        """测试事件转JSON"""
        event = FileEvent(FileEvent.DELETED, "/test/file.py")
        j = event.to_json()
        self.assertIn("deleted", j)
        self.assertIn("/test/file.py", j)


class TestActionExecutor(unittest.TestCase):
    """动作执行器测试"""

    def test_template_resolution(self):
        """测试模板变量解析"""
        executor = ActionExecutor()
        event = FileEvent(FileEvent.CREATED, "/project/src/main.py")
        event.timestamp = type(event.timestamp)(2026, 5, 19, 12, 0, 0)

        result = executor._resolve_template(
            "echo '{{event}}: {{filename}}'", event
        )
        self.assertIn("created", result)
        self.assertIn("main.py", result)

    def test_template_all_vars(self):
        """测试所有模板变量"""
        executor = ActionExecutor()
        event = FileEvent(FileEvent.MODIFIED, "/project/src/utils.py")
        event.timestamp = type(event.timestamp)(2026, 5, 19, 12, 0, 0)

        template = "{{file}} {{filename}} {{event}} {{path}} {{ext}} {{time}}"
        result = executor._resolve_template(template, event)
        self.assertIn("utils.py", result)
        self.assertIn("modified", result)
        self.assertIn("py", result)


class TestConfigParser(unittest.TestCase):
    """配置解析器测试"""

    def test_simple_yaml(self):
        """测试简单YAML解析"""
        yaml_text = """
# 测试配置
patterns:
  - "*.py"
  - "*.js"
excludes:
  - ".git"
  - "__pycache__"
debounce: 0.2
recursive: true
"""
        result = _parse_yaml_simple(yaml_text)
        self.assertIn("patterns", result)
        self.assertEqual(result["patterns"], ["*.py", "*.js"])
        self.assertIn("excludes", result)
        self.assertEqual(result["debounce"], 0.2)
        self.assertTrue(result["recursive"])

    def test_inline_list(self):
        """测试内联列表"""
        yaml_text = 'events: "created,modified,deleted"'
        result = _parse_yaml_simple(yaml_text)
        self.assertIn("events", result)

    def test_generate_template(self):
        """测试模板生成"""
        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
            path = f.name
        try:
            generate_template(path)
            self.assertTrue(os.path.exists(path))
            with open(path, "r") as f:
                content = f.read()
            self.assertIn("patterns", content)
            self.assertIn("excludes", content)
        finally:
            os.unlink(path)


class TestFileInfo(unittest.TestCase):
    """文件信息测试"""

    def test_existing_file(self):
        """测试已存在文件"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
            f.write(b"print('hello')")
            path = f.name
        try:
            info = FileInfo(path)
            self.assertTrue(info.exists)
            self.assertGreater(info.size, 0)
            self.assertNotEqual(info.checksum, "")
        finally:
            os.unlink(path)

    def test_nonexistent_file(self):
        """测试不存在文件"""
        info = FileInfo("/nonexistent/file.txt")
        self.assertFalse(info.exists)
        self.assertEqual(info.size, 0)


if __name__ == "__main__":
    unittest.main()
