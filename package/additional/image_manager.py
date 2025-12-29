from PySide6.QtCore import Qt, QRectF, Property, QPropertyAnimation, QEasingCurve, QObject, QTimer
from PySide6.QtGui import QPainter, QPixmap, QPainterPath
from PySide6.QtWidgets import QGraphicsOpacityEffect

from package import resources
from package.additional.resource_manager import ResourceManager


class ImageManager:
    def __init__(self, win):
        self.win = win
        self.background_image = BackgroundImage(self)
        self.resource_manager = ResourceManager(resources.RESOURCES_DIRECTORY)

    def set_background_image(self, image) -> None:
        self.background_image.set_background(image)

class BackgroundImage(QObject):
    def __init__(self, image_manager):
        super().__init__()
        self.image_manager = image_manager
        self._win = None
        self.pixmap = None
        self.corner_radius = 100
        self._background_opacity = 1.0

    def SetOutputOpacity(self, value):
        """Метод для установки прозрачности (нужен для аниматора)"""
        self.background_opacity = value

    @property
    def background_opacity(self):
        return self._background_opacity

    @background_opacity.setter
    def background_opacity(self, value):
        self._background_opacity = max(0.0, min(1.0, value))
        #self.win.update()  # Перерисовываем окно

    @property
    def win(self):
        """Actual window link"""
        return self.image_manager.win

    def set_background(self, image_name):
        """Set a new background image with transparency control"""
        #opacity = 0.9 if opacity is None else opacity
        painter = QPainter(self.win)

        # Save opacity
        #self.background_opacity = max(0.0, min(1.0, opacity))  # Limit 0.0-1.0

        # Apply opacity
        painter.setOpacity(self.background_opacity)

        self.pixmap = QPixmap(self.image_manager.resource_manager.load_background_image(image_name))

        self.corner_radius = 100


        scaled_pixmap = self.pixmap.scaled(
            self.win.w_resize, self.win.h_resize,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        )

        # Center Image
        x = (self.win.width() - scaled_pixmap.width())
        y = (self.win.height() - scaled_pixmap.height()) - (self.win.height() / 100)

        painter.setRenderHint(QPainter.Antialiasing)  # Antialiasing ON!

        # Create a path with rounded corners
        path = QPainterPath()
        rect = QRectF(0, 0, self.win.width(), self.win.height())
        path.addRoundedRect(rect, self.corner_radius, self.corner_radius)

        # Trim the painter along this path
        if self.win.frameless:
            painter.setClipPath(path)

        painter.drawPixmap(x, y, scaled_pixmap)

        self.win.event_manager.draw_event_text(painter)

        painter.end()

    def get_background_opacity(self) -> float:
        """Get the opacity of the background image"""
        return getattr(self, 'background_opacity', 1.0)

    def set_background_opacity(self, opacity: float):
        """Set the opacity of the background image"""
        # Limit 0.0-1.0
        self.background_opacity = max(0.0, min(1.0, opacity))
        self.win.update()  # Force redraw

