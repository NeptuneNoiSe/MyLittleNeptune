import sys
from pathlib import Path
import os
import re

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

class Launcher:
    """A class for managing initialization"""
    @classmethod
    def initialize(cls):
        # --- Check critical files ---
        REQUIRED_FILES = {
            'README.md': PROJECT_ROOT / 'README.md',
            'version.py': PROJECT_ROOT / 'version.py',
            'resource': PROJECT_ROOT / 'resource',
            'package': PROJECT_ROOT / 'package'
        }

        for name, path in REQUIRED_FILES.items():
            if not path.exists():
                raise FileNotFoundError(f"Не найден критический файл: {name} ({path})")

        # --- Update README ---
        def update_readme():
            """Update App Version in README.md file"""
            readme = PROJECT_ROOT / 'README.md'
            content = readme.read_text(encoding='utf-8')
            updated = re.sub(r'app_version-[\d.]+', f'app_version-{__version__}', content)
            if updated != content:
                readme.write_text(updated, encoding='utf-8')
                print(f"Обновлена версия в README: {__version__}")
            else:
                print(f"Текущая версия в README: {__version__}")

        update_readme()

        live2d.init()
        format = QSurfaceFormat.defaultFormat()
        format.setSwapInterval(0)
        format.setAlphaBufferSize(8)
        format.setRenderableType(QSurfaceFormat.OpenGL)
        format.setSwapBehavior(QSurfaceFormat.DoubleBuffer)
        QSurfaceFormat.setDefaultFormat(format)

        cls.app = QApplication(sys.argv)
        win = MainWindow(cls.app)
        win.setFormat(format)
        settings = SettingsWindow(win)
        win.set_settings_window(settings)
        settings.setWindowIcon(QIcon(os.path.join(
            package.resources.RESOURCES_DIRECTORY, "icons/color/settings.svg")))

    @classmethod
    def run(cls):
        """Запуск приложения"""
        if cls.app is None:
            raise RuntimeError("The application has not been initialized. Call Launcher.initialize() first")
        cls.app.exec()
        live2d.dispose()

if __name__ == "__main__":
    Launcher.initialize()
    Launcher.run()