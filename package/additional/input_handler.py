import os
from PySide6 import QtCore
from PySide6.QtCore import QTimerEvent, Qt, QTimer, QSize, QPropertyAnimation, QEasingCurve,QPoint, QPointF, QElapsedTimer
from PySide6.QtGui import QPixmap, QMovie, QCursor

import numpy as np
import random
import time
import math
from PIL import Image


class InputHandler:
    def __init__(self, win, model):
        self.win = win
        self.model = model
        self.sleep_move = False
        self.place_this = False
        self.input_lock = False
        self.mouse_press_timer = QElapsedTimer()
        self.hold_timer = QTimer()
        self.hold_timer.setSingleShot(True)
        self.hold_timer.timeout.connect(self.mouse_long_press)

        self.start_pos = QPoint(0, 0)
        self.last_pos = QPoint(0, 0)
        self.drag_direction_x = 0
        self.drag_direction_y = 0
        self.drag_intensity = 0  # drag force (0-1)
        self.angle = 0
        self.drag_threshold = 200  # Minimum distance to start animation
        self.direction_threshold = 10  # The threshold for determining the direction
        self.distance_normalizer = 500  # Divider for intensity
        self._smooth_pos = QPointF()
        self._current_pos = QPoint()
        self.smooth_factor = 0.3

        # Input release timer
        self.mouse_input_timer = QTimer()
        self.mouse_input_timer.setSingleShot(True)
        self.mouse_input_timer.timeout.connect(self.transparent_input_disable)

        # Main tracking update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_mouse_tracking)
        self.update_timer.start(10)  # Update every 10 ms

        # Sleep Move timer
        self.sleepInputTimer = QTimer()
        self.sleepInputTimer.setSingleShot(True)
        self.sleepInputTimer.timeout.connect(self.takingSleep)

    def transparent_input_disable(self):
        """Disable transparent input"""
        self.win.setWindowFlags(self.win.windowFlags() & ~QtCore.Qt.WindowTransparentForInput)
        self.win.show()
        self.mouse_input_timer.stop()

    def set_transparent_input(self):
        """Set transperent input if user click on trasparent area"""
        self.win.setWindowFlags(self.win.windowFlags() | QtCore.Qt.WindowTransparentForInput)
        self.win.show()
        self.mouse_input_timer.start(5000)

    def update_idle_counter(self):
        """Update the idle counter"""
        if not self.win.mouse_tracker.mouse_move:
            #win.mouse_tracker.idle_timer.start()
            pass

    def update_mouse_tracking(self):
        """Main mouse tracking update method"""
        if self.win.mouse_tracker.update_state():
            if (self.win.model is not None
                    and not self.win.mouse_tracker.is_animating
                    and self.win.tracking_mouse
                    and self.win.tracking_mouse_switch):
                self._smooth_pos = self.win.mouse_tracker.get_smoothed_coords()
                if self.win.model:
                    self.win.model.Drag(self._smooth_pos.x(), self._smooth_pos.y())
                    if self.win.mouse_tracking_log:
                        log_x = int(self._smooth_pos.x()) if self._smooth_pos.x().is_integer() else round(self._smooth_pos.x())
                        log_y = int(self._smooth_pos.y()) if self._smooth_pos.y().is_integer() else round(self._smooth_pos.y())
                        print(f"Mouse moving: X={log_x} Y={log_y}")

    def handle_mouse_idle(self):
        """Mouse inactivity handler"""
        if self.win.mouse_tracker.is_animating:
            return

        if self.win.mouse_tracking_log:
            print("Mouse is steady")

        target_x = 0 - self.win.frmX * -0.25
        target_y = 0 - self.win.h_resize * -0.5

        def update_position(pos):
            self.win.posX = pos.x()
            self.win.posY = pos.y()
            if hasattr(self, 'model') and self.win.model is not None:
                self.win.model.Drag(self.win.posX, self.win.posY)

        self.win.mouse_tracker.start_reset_animation(target_x, target_y, update_position)

    def mouse_press_handler(self):
        """Mouse press handler"""
        if not self.win.character.tired_controller.sleep and not self.input_lock:
            self.win.model.ResetExpressions()
            self.mouse_press_timer.start()
            self.hold_timer.start(1500)  # 3 секунды

        if self.win.character.tired_controller.sleep and not self.input_lock:
            self.sleepInputTimer.start(500)

    def mouse_long_press(self):
        """Is called after 3 seconds of holding"""
        # function()
        pass

    def mouse_release_handler(self):
        """Mouse release handler"""
        # Main Reset
        self.win.clickInLA = False
        self.win.tap_body_anim = True
        self.sleepInputTimer.stop()
        self.reset_drag_state()

        # Defining the type of interaction
        was_dragging = self.place_this
        self.place_this = False
        if not self.sleep_move:
            self.win.character.tired_controller.timer_count = 1

        # Drag processing
        if hasattr(self, 'start_pos'):
            del self.start_pos

        if was_dragging:
            if not self.win.character.tired_controller.sleep and not self.input_lock:
                if self.win.isInLA:
                    self.win.character.state.set_stay_state()
                else:
                    self.win.character.state.set_lost_state()
            self.win.talk_widget.dialog_animation = True
            self.sleep_move = False
            return

        if (self.win.character.tired_controller.sleep and
                not self.input_lock and
                not self.sleep_move):
            # print("DEBUG: Correct wake up from click!")
            self.win.character.state.set_woke_up_state()
            return

        if not self.sleep_move:
            if self.win.tap_body_switch and not self.sleep_move:
                self.win.character.movements.process_body_hit()
                if not self.input_lock:
                    self.win.character.state.set_random_state()
        # Reset
        self.sleep_move = False

    def mouse_move_handler(self, global_pos):
        """Mouse move handler with X and Y axis support"""
        try:
            # Conversion to integer coordinates
            if hasattr(global_pos, 'toPoint'):
                self._current_pos = global_pos.toPoint()
            else:
                try:
                    x = int(round(global_pos.x()))
                    y = int(round(global_pos.y()))
                    self._current_pos = QPoint(x, y)
                except (AttributeError, TypeError):
                    print(f"Invalid pos: {global_pos}")
                    return

            # The first call is initialization
            if self.last_pos.isNull():
                self.start_pos = self._current_pos
                self.last_pos = self._current_pos
                return

            # Calculate deltas for both axes
            distance = (self._current_pos - self.start_pos).manhattanLength()
            delta_x = self._current_pos.x() - self.last_pos.x()
            delta_y = self._current_pos.y() - self.last_pos.y()

            # Determine primary movement direction
            abs_delta_x = abs(delta_x)
            abs_delta_y = abs(delta_y)

            # Horizontal movement (X axis)
            if abs_delta_x > self.direction_threshold and abs_delta_x > abs_delta_y:
                direction = 1 if delta_x > 0 else -1
                self.drag_direction_x = round((0.7 * self.drag_direction_x + 0.3 * direction), 2)
                self.drag_direction_y = 0  # Reset vertical direction

            # Vertical movement (Y axis)
            elif abs_delta_y > (self.direction_threshold/2) and abs_delta_y > abs_delta_x:
                direction = 1 if delta_y > 0 else -1
                self.drag_direction_y = round((0.7 * self.drag_direction_y + 0.3 * direction), 4)
                self.drag_direction_x = 0  # Reset horizontal direction


            # Normalization of intensity
            self.drag_intensity = min(distance / self.distance_normalizer, 1.0)

            # Checking for exceeding the threshold
            if distance > self.drag_threshold:
                # Horizontal movement - apply tilt and animation
                if abs(self.drag_direction_x) > 0.25:
                    self.win.animation_manager.drag_animator.update_angle(
                        self.drag_direction_x, self.drag_intensity
                    )
                    self._trigger_drag_animation(self.drag_direction_x, "horizontal")

                # Vertical movement - only animation, no tilt
                elif abs(self.drag_direction_y) > 0.25:
                    self.win.animation_manager.drag_animator.update_vertical_movement(
                        self.drag_direction_y, self.drag_intensity
                    )
                    self._trigger_drag_animation(self.drag_direction_y, "vertical")

            self.last_pos = self._current_pos
            self.win.animation_manager.drag_animator.drag_intensity = self.drag_intensity

        except Exception as e:
            print(f"Move error: {type(e).__name__}: {str(e)}")

    def _trigger_drag_animation(self, direction_value, axis):
        """Activation of animation based on movement axis"""
        if (not self.win.character.tired_controller.sleep and not self.input_lock):
            try:
                self.win.character.state.set_drag_state()
                self.place_this = True

                # Determine direction key based on axis
                if axis == "horizontal":
                    direction_key = "right" if direction_value > 0 else "left"
                else:  # vertical
                    direction_key = "down" if direction_value > 0 else "up"

                if hasattr(self.win.talk_widget, 'dialog_animation'):
                    self.win.talk_widget.dialog_animation = False

                # Update animation only (no tilt for vertical)
                if axis == "horizontal":
                    self.win.animation_manager.update_drag_animation()
                self.win.animation_manager.drag_animator.start_drag_animation(direction_key)

            except AttributeError as e:
                print(f"Animation error: {e}")

    def reset_drag_state(self):
        """Full reset state"""
        self.win.animation_manager.drag_animator.stop_animation()
        self.start_pos = QPoint()
        self.last_pos = QPoint()
        self.drag_direction_x = 0
        self.drag_direction_y = 0
        self.drag_intensity = 0
        self.win.animation_manager.drag_animator.angle = 0
        self.win.animation_manager.drag_animator.apply_rotation()

    def takingSleep(self):
        self.sleep_move = True
        self.sleepInputTimer.stop()

class MouseTracker:
    def __init__(self, widget):
        self.widget = widget
        self.last_position = QCursor.pos()
        self.mouse_move = False
        self._sleep_mode = False

        # Adaptive buffer
        self.adaptive_buffer_size = self._calculate_optimal_buffer()
        self.position_buffer = [QPointF(0, 0)] * self.adaptive_buffer_size
        self.smoothed_position = QPointF(0, 0)
        self._smoothed_position = QPointF(0, 0)

        # Dinamic coef buffer
        self.smooth_factor = 0.3  # The basic coefficient
        self.high_perf_threshold = 0.1  # The threshold for powerful PCs

        self.idle_timer = QTimer()
        self.idle_timer.setInterval(5000)
        self.idle_timer.setSingleShot(True)

        self.animation = QPropertyAnimation()
        self.animation.setDuration(2500)
        self.animation.setEasingCurve(QEasingCurve.OutQuad)
        self.is_animating = False

    def get_local_coords(self):
        """Calculates the local coordinates relative to the widget"""
        global_pos = QCursor.pos()
        return self.widget.mapFromGlobal(global_pos)

    def _calculate_optimal_buffer(self):
        """Automatic buffer size selection based on performance"""
        test_cycles = 10000
        start = time.perf_counter()

        for _ in range(test_cycles):
            QPointF(0, 0).x()

        elapsed = (time.perf_counter() - start) * 1000  # ms

        # The logic of choosing the size
        if elapsed < 0.5:  # Power PCs
            return 15
        elif elapsed < 2.0:  # Medium PCs
            return 10
        else:  # Low PCs
            return 5

    def get_smoothed_coords(self):
        try:
            current_pos = self.widget.mapFromGlobal(QCursor.pos())

            # Update buffer
            self.position_buffer.pop(0)
            self.position_buffer.append(current_pos)

            # Adaptive avg
            avg_x = sum(p.x() for p in self.position_buffer) / self.adaptive_buffer_size
            avg_y = sum(p.y() for p in self.position_buffer) / self.adaptive_buffer_size

            # Dynamic smoothing
            if self._is_high_performance():
                # for Power PC - Agressive smooting
                self.smooth_factor = max(0.1, self.smooth_factor - 0.02)
            else:
                self.smooth_factor = min(0.4, self.smooth_factor + 0.02)

            self.smoothed_position = QPointF(
                self._smoothed_position.x() * (1 - self.smooth_factor) + avg_x * self.smooth_factor,
                self._smoothed_position.y() * (1 - self.smooth_factor) + avg_y * self.smooth_factor
            )

            return self.smoothed_position
        except AttributeError as e:
            pass

    def _is_high_performance(self):
        """Determines high performance in terms of processing time"""
        test_cycles = 1000
        start = time.perf_counter()

        for _ in range(test_cycles):
            QPointF(0, 0).x()

        return (time.perf_counter() - start) * 1000000 < 500  # мкс

    def update_state(self):
        """Updates the mouse state and returns True if there was movement"""
        smooth_pos = self.get_smoothed_coords()
        current_position = QCursor.pos()

        if current_position != self.last_position:
            self.last_position = current_position
            self.mouse_move = True
            self.idle_timer.start()
            return True
        else:
            self.mouse_move = False
            return False

    def start_reset_animation(self, target_x, target_y, callback):
        """Start reset position animation"""
        if self.is_animating:
            self.animation.stop()

        self.is_animating = True
        self.animation.setStartValue(QPointF(self.last_position.x(), self.last_position.y()))
        self.animation.setEndValue(QPointF(target_x, target_y))
        self.animation.valueChanged.connect(callback)
        self.animation.finished.connect(lambda: setattr(self, 'is_animating', False))

        if not self._sleep_mode:
            self.animation.start()

    def should_track_mouse(self):
        """Determines whether to track the mouse (depends only on sleep_mode)"""
        return not self._sleep_mode  # If you are not in sleep mode, we track it.

    def set_sleep_state(self, is_sleeping: bool):
        """Sleep state Management"""
        self._sleep_mode = is_sleeping
        if is_sleeping:
            pass
            #self.idle_timer.stop()  # Stopping the idle timer
        else:
            self.animation.start()