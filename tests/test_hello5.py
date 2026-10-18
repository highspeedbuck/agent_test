"""Unit tests for hello5.py (REQ-0005).

Run from the repository root:

    python -m unittest discover -s tests -v

Only the Python standard library is used (no third-party dependencies),
and no network / database / real-clock access is required.
"""

import contextlib
import io
import os
import subprocess
import sys
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# `unittest discover -s tests` puts tests/ on sys.path, not the repo root,
# so the repo root must be added explicitly before importing hello5.
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import hello  # noqa: E402  (import after sys.path fix-up, used by coexistence tests)
import hello5  # noqa: E402  (import after sys.path fix-up)

EXPECTED_MESSAGE = "Hello World 5"
EXPECTED_NAME = "My name is Tan"
EXPECTED_STDOUT = EXPECTED_MESSAGE + "\n" + EXPECTED_NAME + "\n"


class Hello5MessageTest(unittest.TestCase):
    """Normal path + boundary: the greeting and name strings themselves."""

    def test_message_constant_equals_expected_literal(self):
        self.assertEqual(hello5.MESSAGE, EXPECTED_MESSAGE)

    def test_name_message_constant_equals_expected_literal(self):
        self.assertEqual(hello5.NAME_MESSAGE, EXPECTED_NAME)

    def test_message_is_plain_ascii_without_surrounding_whitespace(self):
        self.assertTrue(hello5.MESSAGE.isascii())
        self.assertEqual(hello5.MESSAGE, hello5.MESSAGE.strip())
        self.assertNotIn("\n", hello5.MESSAGE)

    def test_name_message_is_plain_ascii_without_surrounding_whitespace(self):
        self.assertTrue(hello5.NAME_MESSAGE.isascii())
        self.assertEqual(hello5.NAME_MESSAGE, hello5.NAME_MESSAGE.strip())
        self.assertNotIn("\n", hello5.NAME_MESSAGE)

    def test_message_length_is_thirteen(self):
        # "Hello World 5" keeps one space between "World" and "5"; dropping it
        # (as REQ-0002/0003 spelled "Hello World3") must fail this assertion.
        self.assertEqual(len(hello5.MESSAGE), 13)

    def test_name_message_length_is_fourteen(self):
        # A trailing space or a typo such as "My Name is Tan" must fail here.
        self.assertEqual(len(hello5.NAME_MESSAGE), 14)

    def test_message_has_no_comma_or_exclamation(self):
        self.assertNotIn(",", hello5.MESSAGE)
        self.assertNotIn("!", hello5.MESSAGE)

    def test_constants_are_distinct_strings(self):
        self.assertIsInstance(hello5.MESSAGE, str)
        self.assertIsInstance(hello5.NAME_MESSAGE, str)
        self.assertNotEqual(hello5.MESSAGE, hello5.NAME_MESSAGE)


class Hello5MainTest(unittest.TestCase):
    """Normal path + boundary: main() writes exactly two lines to stdout."""

    def test_main_prints_exactly_two_lines_in_order(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            hello5.main()
        self.assertEqual(buf.getvalue(), EXPECTED_STDOUT)

    def test_main_prints_two_newlines(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            hello5.main()
        self.assertEqual(buf.getvalue().count("\n"), 2)
        self.assertEqual(buf.getvalue().splitlines(), [EXPECTED_MESSAGE, EXPECTED_NAME])

    def test_main_returns_none(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            result = hello5.main()
        self.assertIsNone(result)

    def test_main_is_idempotent_across_repeated_calls(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            hello5.main()
            hello5.main()
        self.assertEqual(buf.getvalue(), EXPECTED_STDOUT * 2)

    def test_main_writes_to_stdout_only(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            hello5.main()
        self.assertEqual(out.getvalue(), EXPECTED_STDOUT)
        self.assertEqual(err.getvalue(), "")


class Hello5ImportTest(unittest.TestCase):
    """Boundary: importing the module must not print anything (design 4.2)."""

    def test_import_has_no_side_effect(self):
        # Run in a subprocess so the already-imported module in this process
        # cannot mask the behaviour of a fresh import.
        proc = subprocess.run(
            [sys.executable, "-c", "import hello5"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout, "")
        self.assertEqual(proc.stderr, "")

    def test_module_exposes_main_and_constants(self):
        self.assertTrue(callable(hello5.main))
        self.assertIsInstance(hello5.MESSAGE, str)
        self.assertIsInstance(hello5.NAME_MESSAGE, str)

    def test_module_docstring_mentions_requirement_id(self):
        # Requirement 4.1: the module docstring must identify the requirement.
        self.assertIn("REQ-0005", hello5.__doc__ or "")


class Hello5ScriptTest(unittest.TestCase):
    """End-to-end: running the script as a CLI (design 4.2)."""

    def test_script_exit_code_and_stdout(self):
        # text=True enables universal newlines so Windows "\r\n" folds back to "\n".
        proc = subprocess.run(
            [sys.executable, "hello5.py"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout, EXPECTED_STDOUT)
        self.assertEqual(proc.stderr, "")

    def test_script_stdout_has_no_extra_blank_lines(self):
        proc = subprocess.run(
            [sys.executable, "hello5.py"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.stdout.count("\n"), 2)
        self.assertEqual(proc.stdout.splitlines(), [EXPECTED_MESSAGE, EXPECTED_NAME])

    def test_script_lines_are_in_fixed_order(self):
        # Compare by index so that swapping the two print calls must fail.
        proc = subprocess.run(
            [sys.executable, "hello5.py"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        lines = proc.stdout.splitlines()
        self.assertEqual(lines[0], "Hello World 5")
        self.assertEqual(lines[1], "My name is Tan")

    def test_script_has_no_third_party_imports(self):
        # Requirement 4.1-5: only the standard library (in fact: no imports).
        with open(os.path.join(REPO_ROOT, "hello5.py"), encoding="utf-8") as fh:
            source = fh.read()
        for line in source.splitlines():
            stripped = line.strip()
            self.assertFalse(
                stripped.startswith("import ") or stripped.startswith("from "),
                "unexpected import statement: %r" % line,
            )

    def test_script_needs_no_stdin(self):
        # Requirement 4.2: the messages are fixed literals, so the script must
        # not call input(); with stdin at EOF it still has to succeed.
        proc = subprocess.run(
            [sys.executable, "hello5.py"],
            cwd=REPO_ROOT,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout, EXPECTED_STDOUT)

    def test_script_ignores_extra_command_line_arguments(self):
        # Requirement 4.2: no argv parsing, so extra arguments must be ignored.
        proc = subprocess.run(
            [sys.executable, "hello5.py", "--unexpected", "tan"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout, EXPECTED_STDOUT)
        self.assertEqual(proc.stderr, "")

    def test_script_output_is_stable_across_repeated_runs(self):
        outputs = [
            subprocess.run(
                [sys.executable, "hello5.py"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            ).stdout
            for _ in range(2)
        ]
        self.assertEqual(outputs[0], EXPECTED_STDOUT)
        self.assertEqual(outputs[0], outputs[1])


class Hello5ReadmeTest(unittest.TestCase):
    """Doc contract (requirement 4.4): README documents the two-line output."""

    README_PATH = os.path.join(REPO_ROOT, "README.md")

    def _readme_lines(self):
        with open(self.README_PATH, encoding="utf-8") as fh:
            return fh.read().splitlines()

    def _hello5_expected_block(self):
        lines = self._readme_lines()
        self.assertIn("## Hello5 期望输出", lines)
        start = lines.index("## Hello5 期望输出")
        block, in_fence = [], False
        for line in lines[start + 1:]:
            if line.startswith("```"):
                if in_fence:
                    break
                in_fence = True
                continue
            if in_fence:
                block.append(line)
        return block

    def test_readme_has_exactly_one_hello5_section_pair(self):
        lines = self._readme_lines()
        self.assertEqual(lines.count("## 运行 Hello5"), 1)
        self.assertEqual(lines.count("## Hello5 期望输出"), 1)

    def test_readme_hello5_run_command_matches_script_name(self):
        lines = self._readme_lines()
        start = lines.index("## 运行 Hello5")
        self.assertIn("python hello5.py", lines[start + 1:])

    def test_readme_hello5_expected_block_matches_script_output(self):
        # The documented block must be exactly the two output lines, in order.
        self.assertEqual(self._hello5_expected_block(), [EXPECTED_MESSAGE, EXPECTED_NAME])


class Hello5CoexistenceTest(unittest.TestCase):
    """Regression: hello.py must keep working untouched next to hello5.py."""

    def test_hello_message_unchanged(self):
        self.assertEqual(hello.MESSAGE, "Hello, World!")

    def test_hello_and_hello5_messages_do_not_interfere(self):
        self.assertEqual(hello5.MESSAGE, EXPECTED_MESSAGE)
        self.assertEqual(hello5.NAME_MESSAGE, EXPECTED_NAME)
        self.assertNotEqual(hello.MESSAGE, hello5.MESSAGE)
        self.assertNotEqual(hello.MESSAGE, hello5.NAME_MESSAGE)

    def test_hello_script_still_prints_original_greeting(self):
        proc = subprocess.run(
            [sys.executable, "hello.py"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout, "Hello, World!\n")


if __name__ == "__main__":
    unittest.main()
