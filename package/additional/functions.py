from PySide6.QtWidgets import QDoubleSpinBox

from package import resources
from package.additional.resource_manager import ResourceManager
import OpenGL.GL as gl
import numpy as np
from PIL import Image

class Functions:
    def __init__(self, win, model):
        self.model = model
        self.win = win
        self.resource_manager = ResourceManager(resources.RESOURCES_DIRECTORY)
        self.anim_manager = None

    def setLanguage(self):
        """Set App Localization"""
        # List of supported languages (key: value for load_language)
        supported_languages = {
            "Russian": "russian",
            "English": "english",
            # "Key in the interface": "file_name.json"
        }
        # Choose a language or fallback (english)
        language_key = supported_languages.get(self.win.language, "english")
        self.win.lang = self.resource_manager.load_language(language_key)

    def savePng(self, fName):
        """Screenshot function"""
        data = gl.glReadPixels(0, 0, self.win.width(), self.win.height(), gl.GL_RGBA, gl.GL_UNSIGNED_BYTE)
        data = np.frombuffer(data, dtype=np.uint8).reshape(self.win.height(), self.win.width(), 4)
        data = np.flipud(data)
        new_data = np.zeros_like(data)
        for rid, row in enumerate(data):
            for cid, col in enumerate(row):
                color = None
                new_data[rid][cid] = col
                if cid > 0 and data[rid][cid - 1][3] == 0 and col[3] != 0:
                    color = new_data[rid][cid - 1]
                elif cid > 0 and data[rid][cid - 1][3] != 0 and col[3] == 0:
                    color = new_data[rid][cid]
                if color is not None:
                    color[0] = 0 # 255
                    color[1] = 0
                    color[2] = 0
                    color[3] = 0 # 255
                color = None
                if rid > 0:
                    if data[rid - 1][cid][3] == 0 and col[3] != 0:
                        color = new_data[rid - 1][cid]
                    elif data[rid - 1][cid][3] != 0 and col[3] == 0:
                        color = new_data[rid][cid]
                elif col[3] != 0:
                    color = new_data[rid][cid]
                if color is not None:
                    color[0] = 0 #255
                    color[1] = 0
                    color[2] = 0
                    color[3] = 0 # 255
        img = Image.fromarray(new_data, 'RGBA')
        img.save(fName)

class PowerOfTwoSpinBox(QDoubleSpinBox):
    """SpinBox для степеней двойки без лишних нулей"""

    POWERS = [0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(0.25, 16.0)
        self.setDecimals(3)  # Для точного отображения 0.25 и 0.5

    def stepBy(self, steps):
        """Переопределяем стандартное поведение шага"""
        current = self.value()
        current_idx = self._find_power_index(current)

        new_idx = current_idx + steps
        new_idx = max(0, min(len(self.POWERS) - 1, new_idx))

        self.setValue(self.POWERS[new_idx])

    def _find_power_index(self, value):
        """Находит индекс в массиве степеней"""
        for i, power in enumerate(self.POWERS):
            if abs(power - value) < 0.001:
                return i

        # Fallback: находим ближайшую
        closest_idx = 0
        min_diff = abs(value - self.POWERS[0])

        for i, power in enumerate(self.POWERS[1:], 1):
            diff = abs(value - power)
            if diff < min_diff:
                min_diff = diff
                closest_idx = i

        return closest_idx

    def textFromValue(self, value):
        """Форматируем значение без лишних нулей"""
        # Убираем .0 и .00 для целых чисел
        if value.is_integer():
            return f"{int(value):d}X"
        else:
            # Для дробных показываем максимум 2 знака
            formatted = f"{value:.2f}".rstrip('0').rstrip('.')
            return f"{formatted}X"