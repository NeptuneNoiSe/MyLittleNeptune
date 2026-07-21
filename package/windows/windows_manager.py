from PySide6.QtCore import QRect
from PySide6.QtGui import QGuiApplication


class PositionWindowController:
    def __init__(self,win):
        self.win = win
        self.app_config = self.win.app_config
        self.saved_position_x = self.app_config.saved_position_x
        self.saved_position_y = self.app_config.saved_position_y

    def _get_total_screens_geometry(self):
        """Get combined geometry of all screens"""
        screens = QGuiApplication.screens()
        if not screens:
            return self.win.screen().availableGeometry()

        total_rect = screens[0].availableGeometry()
        for screen in screens[1:]:
            total_rect = total_rect.united(screen.availableGeometry())

        return total_rect

    def _clamp_y_to_screen(self, y, window_h, screen_geom=None):
        """Correction Y position to screen geometry"""
        total_geom = self._get_total_screens_geometry()

        if window_h > total_geom.height():
            return total_geom.top()

        return max(
            total_geom.top(),
            min(y, total_geom.bottom() - window_h)
        )

    def _clamp_y_to_screen_overlap(self, y, window_h):
        """
        Experimental alternative implementation.

        Instead of clamping against the united desktop geometry,
        chooses the screen with the greatest vertical overlap.
        """
        top = y
        bottom = y + window_h

        best_y = y
        max_overlap = 0

        for screen in QGuiApplication.screens():
            g = screen.availableGeometry()
            overlap = max(
                0,
                min(bottom, g.bottom() + 1) - max(top, g.top())
            )

            if overlap >= window_h:
                return y

            if overlap > max_overlap:
                max_overlap = overlap
                if window_h <= g.height():
                    best_y = max(g.top(), min(y, g.bottom() - window_h))
                else:
                    best_y = g.top()

        return best_y

    def _is_x_visible_on_any_screen(self, x, width):
        """Check 50% width visibility on any screen"""
        left = x
        right = x + width

        for screen in QGuiApplication.screens():
            g = screen.availableGeometry()

            overlap = min(right, g.right() + 1) - max(left, g.left())

            if overlap >= width / 2:
                return True

        return False

    def _calculate_safe_x(self, default_x, window_w, screen_geom):
        """Calculate safe position on X"""
        if window_w > screen_geom.width():
            return screen_geom.left() - (window_w - screen_geom.width()) // 2
        return max(screen_geom.left(), min(default_x, screen_geom.right() - window_w))

    def _calculate_safe_position(self, default_x, default_y, window_w, window_h, screen_geom):
        """Calculate safe position, handling windows larger than screen"""
        # X position
        if window_w > screen_geom.width():
            safe_x = screen_geom.left() - (window_w - screen_geom.width()) // 2
        else:
            safe_x = max(screen_geom.left(), min(default_x, screen_geom.right() - window_w))

        # Y position - keep title bar accessible, allow extending below
        safe_y = max(screen_geom.top(), default_y)

        return safe_x, safe_y

    def _is_position_visible_on_any_screen(self, x, y, width, height):
        """Check if window is visible on any connected screen"""
        if not self.app_config.save_position:
            return False

        if x == 0 and y == 0:
            return False

        window_rect = QRect(int(x), int(y), width, height)
        screens = QGuiApplication.screens()

        for screen in screens:
            screen_geom = screen.availableGeometry()
            intersection = screen_geom.intersected(window_rect)

            x_visible = intersection.width() >= width / 2

            y_fully_visible = intersection.height() == height

            self.need_y_correction = not y_fully_visible

            if x_visible:
                return True

        return False

    def position_window(self, ignore_saved_position=False):
        """Set window position with conditions"""
        window_width = self.win.width()
        window_height = self.win.height()
        screen_geom = self.win.screen().availableGeometry()
        self.saved_position_x = self.app_config.saved_position_x
        self.saved_position_y = self.app_config.saved_position_y

        # Calculate default position
        if self.win.frameless and not self.win.background:
            default_x = (self.win.SrcSize.width() - window_width) - self.win.w_correction
        else:
            default_x = (self.win.SrcSize.width() - window_width)

        default_y = (self.win.SrcSize.height() - window_height) - self.win.h_correction
        if self.win.first_run:
            default_y -= 25

        if self.saved_position_x == 0 and self.saved_position_y == 0 and self.app_config.save_position:
            final_x, final_y = self._calculate_safe_position(
                default_x, default_y, window_width, window_height, screen_geom)
            self.win.move(int(final_x), int(final_y))
            return

        if not ignore_saved_position and self.app_config.save_position:
            x_valid = self._is_x_visible_on_any_screen(
                self.saved_position_x, window_width
            )

            if x_valid:
                final_x = self.saved_position_x
            else:
                final_x = self._calculate_safe_x(default_x, window_width, screen_geom)

            final_y = self._clamp_y_to_screen(
                self.saved_position_y, window_height, screen_geom
            )
        else:
            final_x, final_y = self._calculate_safe_position(
                default_x, default_y, window_width, window_height, screen_geom
            )

        self.win.move(int(final_x), int(final_y))

    def save_window_position(self, reset=False):
        self.app_config.saved_position_x = int(self.win.x())
        self.app_config.saved_position_y = int(self.win.y())
        if reset:
            self.app_config.saved_position_x = 0
            self.app_config.saved_position_y = 0
