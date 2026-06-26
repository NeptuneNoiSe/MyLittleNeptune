import sys
from pathlib import Path
import os
import re
from typing import Optional
import subprocess

if getattr(sys, 'frozen', False):
    PROJECT_ROOT = Path(sys.executable).parent
else:
    PROJECT_ROOT = Path(__file__).parent

os.chdir(PROJECT_ROOT)
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / 'package'))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon, QSurfaceFormat
import live2d.v3 as live2d

import package.resources
from package.neptune_main import MainWindow
from package.windows.settings_window import SettingsWindow
from version import __version__

def prepare_build():
    """Preparing files before build"""
    # Generate version_info.txt
    subprocess.run([sys.executable, 'version_info.py'])

def get_project_root() -> Path:
    """Get project root folder"""
    if getattr(sys, 'frozen', False):
        if hasattr(sys, '_MEIPASS'):
            return Path(sys._MEIPASS)
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent


def get_resource_path(relative_path: str = "") -> Path:
    """Get resource path
    Приоритет поиска:
    1. Next to the exe (for onedir and development)
    2. In _MEIPASS (for onefile)
    3. In the project root (for development)
    """
    resource_name = "resource"

    if getattr(sys, 'frozen', False):
        exe_dir = Path(sys.executable).parent
        onedir_path = exe_dir / resource_name
        if onedir_path.exists():
            return onedir_path / relative_path if relative_path else onedir_path

        if hasattr(sys, '_MEIPASS'):
            meipass_path = Path(sys._MEIPASS) / resource_name
            if meipass_path.exists():
                return meipass_path / relative_path if relative_path else meipass_path

        if hasattr(sys, '_MEIPASS'):
            return Path(sys._MEIPASS) / relative_path if relative_path else Path(sys._MEIPASS)

    project_root = Path(__file__).resolve().parent
    dev_path = project_root / resource_name
    if dev_path.exists():
        return dev_path / relative_path if relative_path else dev_path

    return project_root / resource_name / relative_path

PROJECT_ROOT = get_project_root()
RESOURCE_PATH = get_resource_path()


def setup_import_paths():
    """Setup import paths for all modes."""
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    package_dir = PROJECT_ROOT / 'package'
    if package_dir.exists() and str(package_dir) not in sys.path:
        sys.path.insert(0, str(package_dir))


def get_version() -> str:
    """Get App version"""
    try:
        from version import __version__
        return __version__
    except ImportError:
        return "unknown"


def update_readme(version: str):
    """Update the version in README.md (only in development mode)"""
    if getattr(sys, 'frozen', False):
        return

    prepare_build()

    readme = PROJECT_ROOT / 'README.md'
    if not readme.exists():
        return
    try:
        content = readme.read_text(encoding='utf-8')
        updated = re.sub(
            r'app_version-[\d.]+',
            f'app_version-{version}',
            content
        )
        if updated != content:
            readme.write_text(updated, encoding='utf-8')
            print(f"[INFO]  [PASS] Updated version in the README: {version}")
    except Exception as e:
        print(f"[ERROR] Couldn't update README: {e}")


class Launcher:
    """Control of application initialization and launch"""
    _instance: Optional['Launcher'] = None

    def __init__(self):
        self.app = None
        self.main_window = None
        self.settings_window = None
        Launcher._instance = self

    @classmethod
    def get_instance(cls) -> 'Launcher':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def initialize(self):
        """Initialization of all application components"""
        # Setup paths
        setup_import_paths()

        version = get_version()

        # Check Resource path
        if not RESOURCE_PATH.exists():
            print(f"[FATAL ERROR] Attention: The resource folder was not found at the following path: {RESOURCE_PATH}")
            print(f"[INFO] Project Root: {PROJECT_ROOT}")
            print(f"[INFO] Path to exe: {Path(sys.executable).parent if getattr(sys, 'frozen', False) else 'N/A'}")
            if hasattr(sys, '_MEIPASS'):
                print(f"  _MEIPASS: {sys._MEIPASS}")
        else:
            print(f"[INFO] Resource found: {RESOURCE_PATH}")

        update_readme(version)
        live2d.init()

        gl_format = QSurfaceFormat.defaultFormat()
        gl_format.setSwapInterval(0)
        gl_format.setAlphaBufferSize(8)
        gl_format.setRenderableType(QSurfaceFormat.OpenGL)
        gl_format.setSwapBehavior(QSurfaceFormat.DoubleBuffer)
        QSurfaceFormat.setDefaultFormat(gl_format)

        self.app = QApplication(sys.argv)

        self.main_window = MainWindow(self.app, version)
        self.main_window.setFormat(gl_format)

        self.settings_window = SettingsWindow(self.main_window)
        self.main_window.set_settings_window(self.settings_window)

        self._set_window_icon()

        print("─────────────────────────────────────────────────────────────")
        print(f"[INFO] My Little Neptune (v{version}) is initialized")

        # print(live2d.__file__)
        # print(MainWindow.__module__)

    def _set_window_icon(self):
        """Setting the settings window icon"""
        try:
            import resources
            icon_path = RESOURCE_PATH / "icons/color/settings.svg"
            if icon_path.exists():
                from PySide6.QtGui import QIcon
                self.settings_window.setWindowIcon(QIcon(str(icon_path)))
        except Exception as e:
            print(f"[ERROR] Couldn't install the icon: {e}")

    def run(self):
        """Run the main application cycle"""
        if self.app is None:
            raise RuntimeError(
                "[FATAL ERROR] The application is not initialized. "
            )

        try:
            print("[INFO] Launching the application...")
            sys.exit(self.app.exec())
        finally:
            self._cleanup()

    def _cleanup(self):
        """Resource cleanup at exit"""
        try:
            live2d.dispose()
        except Exception as e:
            print(f"[ERROR] Error cleanup Live2D: {e}")


if __name__ == "__main__":
    launcher = Launcher()
    launcher.initialize()
    launcher.run()