"""Unit tests for hello.py (REQ-0001).

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
# so the repo root must be added explicitly before importing hello.
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import hello  # noqa: E402  (import after sys.path fix-up)

EXPECTED_MESSAGE = "Hello, World!"


class HelloMessageTest(unittest.TestCase):
    """Normal path: the greeting string itself."""

    def test_message_constant_equals_expected_literal(self):
        self.assertEqual(hello.MESSAGE, EXPECTED_MESSAGE)

    def test_message_is_plain_ascii_without_surrounding_whitespace(self):
        self.assertTrue(hello.MESSAGE.isascii())
        self.assertEqual(hello.MESSAGE, hello.MESSAGE.strip())
        self.assertNotIn("\n", hello.MESSAGE)


class HelloMainTest(unittest.TestCase):
    """Normal path + boundary: main() writes exactly one line to stdout."""

    def test_main_prints_exactly_one_line(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            hello.main()
        self.assertEqual(buf.getvalue(), EXPECTED_MESSAGE + "\n")

    def test_main_returns_none(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            result = hello.main()
        self.assertIsNone(result)

    def test_main_is_idempotent_across_repeated_calls(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            hello.main()
            hello.main()
        self.assertEqual(buf.getvalue(), (EXPECTED_MESSAGE + "\n") * 2)

    def test_main_writes_to_stdout_only(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            hello.main()
        self.assertEqual(out.getvalue(), EXPECTED_MESSAGE + "\n")
        self.assertEqual(err.getvalue(), "")


class HelloImportTest(unittest.TestCase):
    """Boundary: importing the module must not print anything (design 4.2)."""

    def test_import_has_no_side_effect(self):
        # Run in a subprocess so the already-imported module in this process
        # cannot mask the behaviour of a fresh import.
        proc = subprocess.run(
            [sys.executable, "-c", "import hello"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout, "")
        self.assertEqual(proc.stderr, "")

    def test_module_exposes_main_and_message(self):
        self.assertTrue(callable(hello.main))
        self.assertIsInstance(hello.MESSAGE, str)


class HelloScriptTest(unittest.TestCase):
    """End-to-end: running the script as a CLI (design 4.1)."""

    def test_script_exit_code_and_stdout(self):
        proc = subprocess.run(
            [sys.executable, "hello.py"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout, EXPECTED_MESSAGE + "\n")
        self.assertEqual(proc.stderr, "")

    def test_script_stdout_has_no_extra_blank_lines(self):
        proc = subprocess.run(
            [sys.executable, "hello.py"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.stdout.count("\n"), 1)
        self.assertEqual(proc.stdout.splitlines(), [EXPECTED_MESSAGE])

    def test_script_has_no_third_party_imports(self):
        # Requirement 4.1-5: only the standard library (in fact: no imports).
        with open(os.path.join(REPO_ROOT, "hello.py"), encoding="utf-8") as fh:
            source = fh.read()
        for line in source.splitlines():
            stripped = line.strip()
            self.assertFalse(
                stripped.startswith("import ") or stripped.startswith("from "),
                "unexpected import statement: %r" % line,
            )


if __name__ == "__main__":
    unittest.main()
