from pathlib import Path
import sys


def get_resource_path(relative_path: str = "") -> Path:
    """Universal resource search"""
    resource_name = "resource"

    if getattr(sys, 'frozen', False):
        exe_dir = Path(sys.executable).parent

        if (exe_dir / resource_name).exists():
            base = exe_dir / resource_name
        elif hasattr(sys, '_MEIPASS') and (Path(sys._MEIPASS) / resource_name).exists():
            base = Path(sys._MEIPASS) / resource_name
        elif hasattr(sys, '_MEIPASS'):
            base = Path(sys._MEIPASS)
        else:
            base = exe_dir
    else:
        base = Path(__file__).resolve().parent.parent / resource_name

    return base / relative_path if relative_path else base


RESOURCES_DIRECTORY = get_resource_path()