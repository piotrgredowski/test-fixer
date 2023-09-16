import json
import pathlib
import shutil
import tempfile

import pytest

from test_fixer import fix_tests


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as dir_name:
        yield pathlib.Path(dir_name)


def _run_tests(directory: pathlib.Path):
    import subprocess

    cmd = f"python -m pytest {directory.name!s}"
    result = subprocess.run(
        cmd.split(" "),
        cwd=directory.parent,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    return result.returncode


@pytest.fixture
def mock_chat(mocker):
    class Message:
        content = json.dumps(
            {
                "type": "fix",
                "patch": 'diff --git a/src/sum.py b/src/sum.py\nindex 78015e5..978f4ac 100644\n--- a/src/sum.py\n+++ b/src/sum.py\n@@ -1,4 +1,4 @@\n def sum_printer(*args: list[int]):\n     sum_ = sum(args)\n \n-    return " + ".join([str(a) for a in args]) + f" = {sum_ * 2}"\n+    return " + ".join([str(a) for a in args]) + f" = {sum_}"\n',
            }
        )

    class Choice:
        message = Message()

    class MockedResponse:
        choices = [Choice()]

    mocker.patch("test_fixer.openai.ChatCompletion.create", return_value=MockedResponse)


@pytest.mark.functional
def test_simple(temp_dir: pathlib.Path, mock_chat):
    src_dir = (pathlib.Path(__file__).parent / "examples").resolve()

    dest_dir = temp_dir / "examples"

    shutil.copytree(
        src_dir,
        dest_dir,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"),
    )
    tests_result = _run_tests(dest_dir)
    shutil.rmtree(dest_dir)

    shutil.copytree(
        src_dir,
        dest_dir,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"),
    )
    assert tests_result == pytest.ExitCode.TESTS_FAILED

    tests_output_file = pathlib.Path(__file__).parent / "examples_tests_output.txt"
    fix_tests(directory=dest_dir, tests_output_file=tests_output_file)

    tests_result = _run_tests(dest_dir)

    assert tests_result == pytest.ExitCode.OK
