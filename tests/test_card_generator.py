import subprocess
import sys

import pytest

PYTHON_EXE = sys.executable


def test_import_package():
    """Test basic import of package."""
    import card_generator  # noqa: F401


@pytest.mark.console
def test_console_help():
    """Calls help file of console script and tests for failure."""
    process = subprocess.run(
        [PYTHON_EXE, '-m', 'card_generator', '--help'],
        capture_output=True,
        universal_newlines=True,
    )
    assert process.returncode == 0, process.stderr


@pytest.mark.console
def test_console_noargs():
    """Runs console without arguments expecting to fail."""
    process = subprocess.run(
        [PYTHON_EXE, '-m', 'card_generator'],
        capture_output=True,
        universal_newlines=True,
    )
    assert process.returncode == 2, process.stderr
