from PySide6.QtCore import Qt, QRectF, Property, QPropertyAnimation, QEasingCurve, QObject, QTimer, QPoint, \
    QSequentialAnimationGroup
from PySide6.QtGui import QPainter, QPixmap, QPainterPath
from PySide6.QtWidgets import QGraphicsOpacityEffect, QLabel
import time
import math

from package import resources
from package.additional.resource_manager import ResourceManager

class ImageManager:
    def __init__(self, win):
        self.win = win
        self.background_image = BackgroundImage(self)
        self.item_image = ItemImage(self)
        self.resource_manager = ResourceManager(resources.RESOURCES_DIRECTORY)

    def set_background_image(self, image) -> None:
        self.background_image.set_background(image)

    def set_item_image(self, image) -> None:
        self.item_image.set_item(image)

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

class ItemImage(QObject):
    def __init__(self, image_manager):
        super().__init__()
        self.image_manager = image_manager
        self._win = None

        self.label = QLabel()
        #self.label.setAttribute(Qt.WA_TransparentForMouseEvents)
        #self.label.setStyleSheet("background: transparent; border: none;")

        self.opacity_effect = QGraphicsOpacityEffect()
        self.opacity_effect.setOpacity(1.0)
        self.label.setGraphicsEffect(self.opacity_effect)

        self.position_animation = None

        # Animations Store
        self._animations = []
        self._animation_groups = []

        # Default Vars
        self._item_opacity = 1.0
        self._scale = 1.0
        self._anim_scale = 1.0
        self._position_x = 0
        self._position_y = 0
        self._alignment = Qt.AlignmentFlag.AlignCenter
        self._keep_aspect_ratio = True
        self._smooth_transformation = True

        self.current_image_name = None
        self.original_pixmap = None
        self.scaled_pixmap = None

        QTimer.singleShot(0, self._setup_label)

    def SetOutputOpacity(self, value):
        """Opacity control"""
        self.item_opacity = value

    def _setup_label(self):
        """Setup the label"""
        if self.win:
            self.label.setParent(self.win)
            self.label.lower()
            self.label.hide()

    def _cleanup_animations(self):
        """Clean up animations"""
        self._animations = [a for a in self._animations if a]
        self._animation_groups = [g for g in self._animation_groups if g]

    def get_anim_scale(self):
        """Scale Getter"""
        return self._anim_scale

    def set_anim_scale(self, value):
        """Scale Setter"""
        self._anim_scale = value
        self._scale = value
        self._update_pixmap()

    anim_scale = Property(float, get_anim_scale, set_anim_scale)

    @property
    def win(self):
        return self.image_manager.win

    @property
    def item_opacity(self):
        return self._item_opacity

    @item_opacity.setter
    def item_opacity(self, value):
        self._item_opacity = max(0.0, min(1.0, value))
        self.opacity_effect.setOpacity(self._item_opacity)
        self.label.update()

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value):
        self._scale = max(0.1, min(5.0, value))  # Ограничиваем масштаб
        self._update_pixmap()

    @property
    def position(self):
        return (self._position_x, self._position_y)

    @position.setter
    def position(self, pos_tuple):
        x, y = pos_tuple
        self._position_x = x
        self._position_y = y
        self._update_position()

    @property
    def alignment(self):
        return self._alignment

    @alignment.setter
    def alignment(self, align):
        self._alignment = align
        self._update_position()

    def set_item(self, image_name, show=True, **kwargs):
        """Set item image"""
        self.current_image_name = image_name

        if not image_name:
            self.hide()
            return

        image_path = self.image_manager.resource_manager.load_item_image(image_name)
        self.original_pixmap = QPixmap(image_path)

        if self.original_pixmap.isNull():
            print(f"Warning: Failed to load image: {image_name}")
            return

        if 'scale' in kwargs:
            self._scale = max(0.1, min(5.0, kwargs['scale']))
        if 'position' in kwargs:
            self._position_x, self._position_y = kwargs['position']
        if 'opacity' in kwargs:
            self._item_opacity = max(0.0, min(1.0, kwargs['opacity']))

        self._update_pixmap()

        if show:
            self.show()
            self.opacity_effect.setOpacity(self._item_opacity)
        else:
            self.hide()

    def _update_pixmap(self):
        if not self.original_pixmap or not self.win:
            return

        scaled_size = self.original_pixmap.size() * self._scale

        self.scaled_pixmap = self.original_pixmap.scaled(
            scaled_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.label.setPixmap(self.scaled_pixmap)
        self._update_position()

    def _update_position(self):
        if not self.scaled_pixmap or not self.win:
            return

        pixmap_width = self.scaled_pixmap.width()
        pixmap_height = self.scaled_pixmap.height()
        win_width = self.win.width()
        win_height = self.win.height()

        x = (win_width - pixmap_width) // 2 + self._position_x
        y = (win_height - pixmap_height) // 2 + self._position_y - (self.win.height() / 100)

        self.label.setGeometry(int(x), int(y), pixmap_width, pixmap_height)

    def set_size(self, width=None, height=None, keep_aspect=True):
        """Set Size"""
        if not self.original_pixmap:
            return

        if width is None and height is None:
            return

        current_size = self.original_pixmap.size()

        if width is None:
            width = current_size.width() * (height / current_size.height())
        elif height is None:
            height = current_size.height() * (width / current_size.width())

        # Масштабируем
        self.scaled_pixmap = self.original_pixmap.scaled(
            int(width), int(height),
            Qt.AspectRatioMode.KeepAspectRatio if keep_aspect else Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation if self._smooth_transformation
            else Qt.TransformationMode.FastTransformation
        )

        self.label.setPixmap(self.scaled_pixmap)
        self._update_position()

    def set_percentage_size(self, width_percent=None, height_percent=None, relative_to_model=False):
        """Set size in percentage"""
        if not self.win:
            return

        if relative_to_model:
            win_width = self.win.w_resize
            win_height = self.win.h_resize
        else:
            win_width = self.win.width()
            win_height = self.win.height()

        width = win_width * (width_percent / 100) if width_percent is not None else None
        height = win_height * (height_percent / 100) if height_percent is not None else None

        #print(f"Setting size relative to {mode}: {width_percent}% → {width}px, {height_percent}% → {height}px")
        self.set_size(width, height)

    def set_relative_position(self, x_percent=0, y_percent=0):
        """Set position in percent"""
        if not self.win:
            return

        self._position_x = int(self.win.width() * (x_percent / 100))
        self._position_y = int(self.win.height() * (y_percent / 100))
        self._update_position()

    def set_alignment(self, horizontal='center', vertical='center'):
        """Set Alignment"""
        align_map = {
            'left': Qt.AlignLeft,
            'right': Qt.AlignRight,
            'center': Qt.AlignHCenter,
            'top': Qt.AlignTop,
            'bottom': Qt.AlignBottom,
            'middle': Qt.AlignVCenter
        }

        h_align = align_map.get(horizontal, Qt.AlignHCenter)
        v_align = align_map.get(vertical, Qt.AlignVCenter)

        self._alignment = h_align | v_align
        self._update_position()

    def animate_position(self, target_x, target_y, duration=1000):
        """Default Position Animation"""
        if not self.label:
            return None

        self._cleanup_animations()

        self.position_animation = QPropertyAnimation(self.label, b"pos")
        self._animations.append(self.position_animation)  # Сохраняем!

        self.position_animation.setDuration(duration)
        self.position_animation.setStartValue(self.label.pos())
        self.position_animation.setEndValue(QPoint(target_x, target_y))
        self.position_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

        def cleanup():
            if self.position_animation in self._animations:
                self._animations.remove(self.position_animation)

        self.position_animation.finished.connect(cleanup)

        QTimer.singleShot(0, self.position_animation.start)

        return self.position_animation

    def animate_scale_bounce(self, start_scale, end_scale, duration=300):
        """Scale bounce Animation"""
        if not self.label:
            return None

        self._cleanup_animations()

        self._original_scale_before_animation = self._scale

        self.animation_group = QSequentialAnimationGroup()
        self._animation_groups.append(self.animation_group)

        scale_up = QPropertyAnimation(self, b"anim_scale")
        scale_up.setDuration(duration // 2)
        scale_up.setStartValue(start_scale)
        scale_up.setEndValue(end_scale)
        scale_up.setEasingCurve(QEasingCurve.Type.OutQuad)

        scale_down = QPropertyAnimation(self, b"anim_scale")
        scale_down.setDuration(duration // 2)
        scale_down.setStartValue(end_scale)
        scale_down.setEndValue(start_scale)
        scale_down.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self.animation_group.addAnimation(scale_up)
        self.animation_group.addAnimation(scale_down)

        def cleanup_group():
            if self.animation_group in self._animation_groups:
                self._animation_groups.remove(self.animation_group)
            # self._scale = self._original_scale_before_animation
            # self._update_pixmap()

        self.animation_group.finished.connect(cleanup_group)

        QTimer.singleShot(0, self.animation_group.start)
        return self.animation_group

    def reset_transform(self):
        """Reset all transformations to default values"""
        self._scale = 1.0
        self._position_x = 0
        self._position_y = 0
        self._alignment = Qt.AlignCenter
        self._item_opacity = 1.0

        self._update_pixmap()
        self._apply_opacity()

    def show(self):
        """Show Label"""
        if self.label:
            self.label.show()
            self.label.raise_()

    def hide(self):
        """Hide Label"""
        if self.label:
            self.label.hide()

    def toggle(self):
        """Toggle Label"""
        if self.label.isVisible():
            self.hide()
        else:
            self.show()

    def is_visible(self):
        """Check if Label is Visible"""
        return self.label.isVisible() if self.label else False