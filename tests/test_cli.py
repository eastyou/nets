"""命令行测试。"""

import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

from nets.cli import main


def run_cli(argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(argv)
    return code, out.getvalue(), err.getvalue()


class NetCommandTest(unittest.TestCase):
    def test_writes_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = os.path.join(folder, "net.html")
            code, out, _ = run_cli(["net", "5", "4", "3", "-o", target])
            self.assertEqual(code, 0)
            self.assertIn("已写入", out)
            with open(target, encoding="utf-8") as handle:
                page = handle.read()
            self.assertEqual(page.count("<rect"), 6)

    def test_stdout(self):
        code, out, _ = run_cli(["net", "4", "3", "2"])
        self.assertEqual(code, 0)
        self.assertIn("<!DOCTYPE html>", out)

    def test_custom_title(self):
        code, out, _ = run_cli(["net", "4", "3", "2", "--title", "课堂材料"])
        self.assertEqual(code, 0)
        self.assertIn("课堂材料", out)

    def test_custom_scale(self):
        code, out, _ = run_cli(["net", "4", "3", "2", "--mm-per-cm", "10"])
        self.assertEqual(code, 0)
        self.assertIn("120.00mm", out)

    def test_invalid_scale(self):
        code, _, err = run_cli(["net", "4", "3", "2", "--mm-per-cm", "0"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_invalid_dimension(self):
        code, _, err = run_cli(["net", "0", "3", "2"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_nested_output(self):
        with tempfile.TemporaryDirectory() as folder:
            target = os.path.join(folder, "a", "b", "net.html")
            code, _, _ = run_cli(["net", "2", "2", "2", "-o", target])
            self.assertEqual(code, 0)
            self.assertTrue(os.path.exists(target))


class InfoCommandTest(unittest.TestCase):
    def test_output(self):
        code, out, _ = run_cli(["info", "5", "4", "3"])
        self.assertEqual(code, 0)
        self.assertIn("长方体", out)
        self.assertIn("94", out)
        self.assertIn("60", out)
        self.assertIn("16 × 11", out)

    def test_cube(self):
        code, out, _ = run_cli(["info", "2", "2", "2"])
        self.assertEqual(code, 0)
        self.assertIn("正方体", out)
        self.assertIn("24", out)
        self.assertIn("8", out)

    def test_invalid(self):
        code, _, err = run_cli(["info", "0", "2", "3"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)


class SheetCommandTest(unittest.TestCase):
    def test_writes_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = os.path.join(folder, "sheet.html")
            code, out, _ = run_cli(["sheet", "--count", "6", "--seed", "1", "-o", target])
            self.assertEqual(code, 0)
            self.assertIn("已写入", out)
            with open(target, encoding="utf-8") as handle:
                page = handle.read()
            self.assertEqual(page.count('class="item"'), 6)

    def test_stdout(self):
        code, out, _ = run_cli(["sheet", "--count", "3", "--seed", "2"])
        self.assertEqual(code, 0)
        self.assertIn("<!DOCTYPE html>", out)

    def test_answers(self):
        code, out, _ = run_cli(["sheet", "--count", "2", "--seed", "3", "--answers"])
        self.assertEqual(code, 0)
        self.assertIn("参考答案", out)

    def test_custom_title(self):
        code, out, _ = run_cli(["sheet", "--count", "2", "--seed", "3", "--title", "单元小测"])
        self.assertEqual(code, 0)
        self.assertIn("单元小测", out)

    def test_custom_range(self):
        code, out, _ = run_cli(
            ["sheet", "--count", "4", "--seed", "4", "--low", "2", "--high", "3"]
        )
        self.assertEqual(code, 0)
        self.assertNotIn("长 4 cm", out)

    def test_invalid_count(self):
        code, _, err = run_cli(["sheet", "--count", "0"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_invalid_range(self):
        code, _, err = run_cli(["sheet", "--low", "9", "--high", "3"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_reproducible(self):
        _, first, _ = run_cli(["sheet", "--count", "5", "--seed", "7"])
        _, second, _ = run_cli(["sheet", "--count", "5", "--seed", "7"])
        self.assertEqual(first, second)

    def test_nested_output(self):
        with tempfile.TemporaryDirectory() as folder:
            target = os.path.join(folder, "x", "y", "sheet.html")
            code, _, _ = run_cli(["sheet", "--count", "1", "-o", target])
            self.assertEqual(code, 0)
            self.assertTrue(os.path.exists(target))


class HelpTest(unittest.TestCase):
    def test_help_exits_zero(self):
        with redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as ctx:
                main(["--help"])
        self.assertEqual(ctx.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
