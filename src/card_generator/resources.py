import sys
from pathlib import Path
from typing import Optional


def get_resource_path(relative_path: Optional[Path] = None) -> Path:
    """Get absolute path to resource, works for python packages and for PyInstaller executables."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = Path(sys._MEIPASS)
    except Exception:
        base_path = Path(__file__).parent

    if relative_path is None:
        return (base_path / 'data').resolve()
    else:
        return (base_path / 'data' / relative_path).resolve()
