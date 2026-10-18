"""Unit tests for hello2.py (REQ-0002).

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
# so the repo root must be added explicitly before importing hello2.
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import hello  # noqa: E402  (import after sys.path fix-up, used by coexistence test)
import hello2  # noqa: E402  (import after sys.path fix-up)

EXPECTED_MESSAGE = "Hello World2"


class Hello2MessageTest(unittest.TestCase):
    """Normal path + boundary: the greeting string itself (design 4.2)."""

    def test_message_constant_equals_expected_literal(self):
        self.assertEqual(hello2.MESSAGE, EXPECTED_MESSAGE)

    def test_message_is_plain_ascii_without_surrounding_whitespace(self):
        self.assertTrue(hello2.MESSAGE.isascii())
        self.assertEqual(hello2.MESSAGE, hello2.MESSAGE.strip())
        self.assertNotIn("\n", hello2.MESSAGE)

    def test_message_length_is_twelve(self):
        self.assertEqual(len(hello2.MESSAGE), 12)

    def test_message_has_no_comma_or_exclamation(self):
        # Guards against "helpfully" rewriting it to "Hello, World! 2".
        self.assertNotIn(",", hello2.MESSAGE)
        self.assertNotIn("!", hello2.MESSAGE)


class Hello2MainTest(unittest.TestCase):
    """Normal path + boundary: main() writes exactly one line to stdout (design 4.3)."""

    def test_main_prints_exactly_one_line(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            hello2.main()
        self.assertEqual(buf.getvalue(), EXPECTED_MESSAGE + "\n")

    def test_main_returns_none(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            result = hello2.main()
        self.assertIsNone(result)

    def test_main_is_idempotent_across_repeated_calls(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            hello2.main()
            hello2.main()
        self.assertEqual(buf.getvalue(), (EXPECTED_MESSAGE + "\n") * 2)

    def test_main_writes_to_stdout_only(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            hello2.main()
        self.assertEqual(out.getvalue(), EXPECTED_MESSAGE + "\n")
        self.assertEqual(err.getvalue(), "")


class Hello2ImportTest(unittest.TestCase):
    """Boundary: importing the module must not print anything (design 4.4)."""

    def test_import_has_no_side_effect(self):
        # Run in a subprocess so the already-imported module in this process
        # cannot mask the behaviour of a fresh import.
        proc = subprocess.run(
            [sys.executable, "-c", "import hello2"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout, "")
        self.assertEqual(proc.stderr, "")

    def test_module_exposes_main_and_message(self):
        self.assertTrue(callable(hello2.main))
        self.assertIsInstance(hello2.MESSAGE, str)


class Hello2ScriptTest(unittest.TestCase):
    """End-to-end: running the script as a CLI (design 4.1)."""

    def test_script_exit_code_and_stdout(self):
        proc = subprocess.run(
            [sys.executable, "hello2.py"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout, EXPECTED_MESSAGE + "\n")
        self.assertEqual(proc.stderr, "")

    def test_script_stdout_has_no_extra_blank_lines(self):
        proc = subprocess.run(
            [sys.executable, "hello2.py"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.stdout.count("\n"), 1)
        self.assertEqual(proc.stdout.splitlines(), [EXPECTED_MESSAGE])

    def test_script_has_no_third_party_imports(self):
        # Requirement 4.1-4: only the standard library (in fact: no imports).
        with open(os.path.join(REPO_ROOT, "hello2.py"), encoding="utf-8") as fh:
            source = fh.read()
        for line in source.splitlines():
            stripped = line.strip()
            self.assertFalse(
                stripped.startswith("import ") or stripped.startswith("from "),
                "unexpected import statement: %r" % line,
            )


class Hello2CoexistenceTest(unittest.TestCase):
    """Regression: hello and hello2 must not interfere with each other (design 4.5)."""

    def test_hello_and_hello2_messages_do_not_interfere(self):
        self.assertEqual(hello.MESSAGE, "Hello, World!")
        self.assertEqual(hello2.MESSAGE, EXPECTED_MESSAGE)


if __name__ == "__main__":
    unittest.main()
