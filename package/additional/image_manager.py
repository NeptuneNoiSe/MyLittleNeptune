from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QPixmap, QPainterPath

from package import resources
from package.additional.resource_manager import ResourceManager


class ImageManager:
    def __init__(self, win):
        self.win = win
        self.background_image = BackgroundImage(self)
        self.resource_manager = ResourceManager(resources.RESOURCES_DIRECTORY)

    def set_background_image(self, image, opacity):
        self.background_image.set_background(image, opacity)

class BackgroundImage:
    def __init__(self, image_manager):
        self.image_manager = image_manager
        self._win = None

    @property
    def win(self):
        """Actual window link"""
        return self.image_manager.win

    def set_background(self, image_name, opacity: float = 1.0):
        """Установить новое фоновое изображение с контролем прозрачности

        Args:
            image_name: Название изображения
            opacity: Прозрачность от 0.0 (полностью прозрачно) до 1.0 (полностью непрозрачно)
        """
        painter = QPainter(self.win)

        # Сохраняем прозрачность в self переменную
        self.background_opacity = max(0.0, min(1.0, opacity))  # Ограничиваем 0.0-1.0

        # Применяем прозрачность
        painter.setOpacity(self.background_opacity)

        self.pixmap = QPixmap(self.image_manager.resource_manager.load_background_image(image_name))

        self.corner_radius = 100


        scaled_pixmap = self.pixmap.scaled(
            self.win.w_resize, self.win.h_resize,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        )

        # Центрируем изображение
        x = (self.win.width() - scaled_pixmap.width())
        y = (self.win.height() - scaled_pixmap.height()) - (self.win.height() / 100)

        painter.setRenderHint(QPainter.Antialiasing)  # Включаем сглаживание!

        # Создаем путь со скругленными углами
        path = QPainterPath()
        rect = QRectF(0, 0, self.win.width(), self.win.height())
        path.addRoundedRect(rect, self.corner_radius, self.corner_radius)

        # Обрезаем painter по этому пути

        if self.win.frameless:
            painter.setClipPath(path)

        painter.drawPixmap(x, y, scaled_pixmap)

        self.win.event_manager.draw_event_text(painter)

        painter.end()

    def fade_background(self, target_opacity: float, duration: int = 1000):
        """Плавное изменение прозрачности фона

        Args:
            target_opacity: Целевая прозрачность (0.0-1.0)
            duration: Длительность анимации в миллисекундах
        """
        if not hasattr(self, 'background_opacity'):
            self.background_opacity = 1.0

        # Создаем анимацию
        from PySide6.QtCore import QPropertyAnimation, QEasingCurve

        self.animation = QPropertyAnimation(self.win, b"background_opacity")
        self.animation.setDuration(duration)
        self.animation.setStartValue(self.background_opacity)
        self.animation.setEndValue(max(0.0, min(1.0, target_opacity)))
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.valueChanged.connect(self.win.update)  # Перерисовываем при изменении
        self.animation.start()

    def get_background_opacity(self) -> float:
        """Получить текущую прозрачность фона"""
        return getattr(self, 'background_opacity', 1.0)

    def set_background_opacity(self, opacity: float):
        """Установить прозрачность фона напрямую"""
        # Ограничиваем значение 0.0-1.0
        self.background_opacity = max(0.0, min(1.0, opacity))
        self.win.update()  # Принудительная перерисовка

