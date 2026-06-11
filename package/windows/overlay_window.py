import os
import random

from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtWidgets import QWidget, QMenu, QApplication

class ContextMenuOverlay(QMenu):
    """Overlay context menu on OpenGL"""
    def __init__(self, parent=None, win = None):
        super().__init__(parent)
        self.win = win
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool |
            Qt.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        QApplication.instance().installEventFilter(self)

        self._apply_theme_colors()

        if self.win and hasattr(self.win, 'theme_changed'):
            self.win.theme_changed.connect(self._on_theme_changed)

    def _on_theme_changed(self):
        """Slot for the theme changed event"""
        self._apply_theme_colors()
        self.update()

    def _apply_theme_colors(self):
        """Apply context menu theme color"""
        if not self.win:
            return

        theme = self.win.get_color_scheme()
        # print(f"Current system theme: {theme}")

        if theme == "dark":
            self.setStyleSheet("""
                QMenu {
                    background-color: rgba(40, 40, 40, 240);
                    border: 1px solid rgba(80, 80, 80, 255);
                    border-radius: 5px;
                    padding: 5px;
                }
                QMenu::item {
                    padding: 5px 25px;
                    color: white;
                }
                QMenu::item:selected {
                    background-color: rgba(100, 100, 200, 200);
                }
                QMenu::separator {
                    height: 1px;
                    background-color: rgba(80, 80, 80, 100);
                    margin: 5px;
                }
            """)
        elif theme == "light":
            self.setStyleSheet("""
                QMenu {
                    background-color: rgba(245, 245, 245, 240);
                    border: 1px solid rgba(200, 200, 200, 255);
                    border-radius: 5px;
                    padding: 5px;
                }
                QMenu::item {
                    padding: 5px 25px;
                    color: black;
                }
                QMenu::item:selected {
                    background-color: rgba(100, 100, 200, 200);
                    color: black;
                }
                QMenu::separator {
                    height: 1px;
                    background-color: rgba(200, 200, 200, 100);
                    margin: 5px;
                }
            """)
        else:
            self.setStyleSheet("""
                QMenu {
                    background-color: rgba(40, 40, 40, 240);
                    border: 1px solid rgba(80, 80, 80, 255);
                    border-radius: 5px;
                    padding: 5px;
                }
                QMenu::item {
                    padding: 5px 25px;
                    color: white;
                }
                QMenu::item:selected {
                    background-color: rgba(100, 100, 200, 200);
                }
            """)

    def show_at_position(self, pos: QPoint):
        """Set context menu position"""
        self.move(pos)
        self.show()
        self.raise_()
        self.activateWindow()

    def eventFilter(self, obj, event):
        """Global Event Filter"""
        if not self.isVisible():
            return super().eventFilter(obj, event)

        if event.type() == event.Type.MouseButtonPress:
            if event.button() == Qt.LeftButton:
                click_pos = event.globalPos()
                if not self.geometry().contains(click_pos):
                    self.close()
                    return True

        return super().eventFilter(obj, event)

    def closeEvent(self, event):
        QApplication.instance().removeEventFilter(self)
        super().closeEvent(event)

    def addAction(self, action):
        action.triggered.connect(self._on_action_triggered)
        return super().addAction(action)

    def addMenu(self, menu):
        menu.aboutToShow.connect(lambda: self._on_submenu_shown(menu))
        return super().addMenu(menu)

    def _on_action_triggered(self):
        self.close()

    def _on_submenu_shown(self, submenu):
        for action in submenu.actions():
            if not action.menu():
                action.triggered.connect(self.close)

    def context_menu_close(self):
        self.close()

class ParticleOverlayWindow(QWidget):
    """Overlay window for particles."""
    def __init__(self, parent=None, resources_dir: str = None):
        super().__init__(None)

        self.particle_presets = ParticlePresets(self)

        self.image_path = os.path.join(resources_dir, "sprites")

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        #self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.width_offset = 0
        self.height_offset = 0

        from package.particle_engine_supreme import GlobalEffectOverlay

        self.particle_system = GlobalEffectOverlay(self, use_physics=True)

    def followMainWindow(self, main_window_geometry):
        """Updates the window position and size"""
        main_width = main_window_geometry.width()
        main_height = main_window_geometry.height()

        overlay_width = main_width + self.width_offset
        overlay_height = main_height + self.height_offset

        x = main_window_geometry.x() + (main_width - overlay_width) // 2
        y = main_window_geometry.y() + (main_height - overlay_height) // 2

        self.setGeometry(x, y, overlay_width, overlay_height)
        self.particle_system.setGeometry(0, 0, overlay_width, overlay_height)

    def set_width_reduction(self, reduction):
        """Sets the width reduction (positive number - reduction)"""
        self.width_offset = -reduction
        if self.parent():
            self.followMainWindow(self.parent().geometry())

    def add_particle_preset(self, preset_name = "", *args, **kwargs):
        preset = preset_name

    def stop_particle_system(self, duration=0):
        QTimer.singleShot(duration, lambda: self.particle_system.clear_effects())
        self.set_width_reduction(0)

class ParticlePresets:
    def __init__(self, overlay_window):
        self.overlay_window = overlay_window

    def _random_range(self, a , b):
        """Generate Random Range"""
        return random.uniform(a, b)

    def rain(self, duration=0, count=3):
        self.overlay_window.particle_system.clear_effects()
        self.overlay_window.particle_system.add_global_effect("rain", count=count)
        if duration > 0:
            self.overlay_window.stop_particle_system(duration)


    def snow(self, duration=0, count=3):
        self.overlay_window.particle_system.clear_effects()
        snow_dir = os.path.join(self.overlay_window.image_path, "snow.png")
        self.overlay_window.particle_system.add_global_effect("snow",
                                               image_path=snow_dir,
                                               count=count,
                                               size_min=1,
                                               size_max=10)
        if duration > 0:
            self.overlay_window.stop_particle_system(duration)

    def confetti(self, duration=1000, count=1):
        self.overlay_window.particle_system.clear_effects()
        particle_duration = int(duration / 10000)
        self.overlay_window.particle_system.add_global_effect("confetti",
                                                              duration=particle_duration,
                                                              count=3 * count,
                                                              shape="star",
                                                              interval=5)
        self.overlay_window.particle_system.add_global_effect("confetti",duration=particle_duration,count=2 * count,shape="line",interval=4)
        self.overlay_window.particle_system.add_global_effect("confetti",duration=particle_duration,count=1 * count,nterval=3)
        self.overlay_window.stop_particle_system(duration)

    def transform_fairy_dust(self, particle_duration: float = -1):
        self.overlay_window.particle_system.add_global_effect("fairy_dust", duration= particle_duration)

    def transform(self, duration=1000, count=1, name = "", reverse=False):
        self.overlay_window.particle_system.clear_effects()
        self.overlay_window.set_width_reduction(150)
        if reverse:
            angle_min = 90
            angle_max = 90
            gravity = 0.2
        else:
            angle_min = -90
            angle_max = -90
            gravity = -0.2

        self.overlay_window.particle_system.add_global_effect("matrix",
                                                              angle_min = angle_min,
                                                              angle_max = angle_max,
                                                              gravity = gravity,
                                                              color = ["#ff0000", "#00ff00", "#0000ff", "#ffff00", "#ff00ff"],
                                                              text_chars = f'{name.upper()}01010101010101010101',
                                                              color_curve = None,
                                                              life_max = 120,
                                                              life_min=60,
                                                              count= 2 * count,
                                                              interval= 5)
        self.overlay_window.particle_system.add_global_effect("rain",
                                                              angle_min=angle_min,
                                                              angle_max=angle_max,
                                                              gravity=gravity,
                                                              color=["#ff0000", "#00ff00", "#0000ff", "#ffff00",
                                                                     "#ff00ff"],
                                                              color_curve=None,
                                                              life_max=12,
                                                              life_min=6,
                                                              count=2 * count,
                                                              interval=5)


