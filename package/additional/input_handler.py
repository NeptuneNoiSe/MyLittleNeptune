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

        self.last_state = None
        self.state_change_counter = 0
        self.state_change_threshold = 30

        # Main tracking update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_mouse_tracking)
        self.update_timer.start(10)  # Update every 10 ms

        # Sleep Move timer
        self.sleepInputTimer = QTimer()
        self.sleepInputTimer.setSingleShot(True)
        self.sleepInputTimer.timeout.connect(self.takingSleep)

    def checkCursor(self):
        global_pos = QCursor.pos()
        local_pos = self.win.mapFromGlobal(global_pos)

        if not self.win.rect().contains(local_pos):
            return

        is_on_character = self.win.isInL2DArea(local_pos.x(), local_pos.y())

        if is_on_character != self.last_state:
            self.state_change_counter += 1
            if self.state_change_counter >= self.state_change_threshold:
                self.change_input_state(is_on_character)
                self.state_change_counter = 0
                self.last_state = is_on_character
        else:
            self.state_change_counter = 0

    def change_input_state(self, is_on_character):
        self.win.hide()
        update_flags = (not self.win.on_top
                        and not self.win.quit_box_active
                        and not self.win.was_fullscreen)
        if update_flags:
            if is_on_character:
                flags = ((self.win.windowFlags() & ~QtCore.Qt.WindowTransparentForInput) |
                         Qt.WindowType.WindowStaysOnTopHint)
            else:
                flags = ((self.win.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint) |
                         QtCore.Qt.WindowTransparentForInput)
        else:
            if is_on_character:
                flags = self.win.windowFlags() & ~QtCore.Qt.WindowTransparentForInput
            else:
                flags = self.win.windowFlags() | QtCore.Qt.WindowTransparentForInput

        self.win.setWindowFlags(flags | Qt.WindowType.WindowCloseButtonHint)
        self.win.setAttribute(Qt.WA_TranslucentBackground)
        self.win.show()

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
            self.win.character.play_drag_audio = True
            self.hold_timer.start(1500)

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
        if not self.sleep_move and self.win.character.tired_controller.timer_count < self.win.character.tired_controller.sleep_v:
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
            self.win.character.tired_state.set_woke_up_state()

            #self.win.character.tired_controller.woke_up()
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
                    # Additional check on the string
                    if isinstance(global_pos, str):
                        print(f"Warning: global_pos is string: {global_pos}")
                        return

                    x = int(round(float(global_pos.x()))) if hasattr(global_pos, 'x') else 0
                    y = int(round(float(global_pos.y()))) if hasattr(global_pos, 'y') else 0
                    self._current_pos = QPoint(x, y)
                except (AttributeError, TypeError, ValueError) as e:
                    print(f"Invalid pos: {global_pos}, error: {e}")
                    return

            # Checking that self.start_pos and self.last_pos are correct
            if not isinstance(self._current_pos, QPoint):
                print(f"_current_pos is not QPoint: {type(self._current_pos)}")
                return

            # The first call is initialization
            if not hasattr(self, 'last_pos') or self.last_pos.isNull():
                self.start_pos = self._current_pos
                self.last_pos = self._current_pos
                return

            # Type checking before the subtraction operation
            if not isinstance(self.start_pos, QPoint):
                self.start_pos = self._current_pos
                self.last_pos = self._current_pos
                return

            # Calculate deltas for both axes
            try:
                # Secure distance calculation
                diff = self._current_pos - self.start_pos
                if isinstance(diff, QPoint):
                    distance = diff.manhattanLength()
                else:
                    # Fallback for when diff is not a QPoint
                    distance = abs(self._current_pos.x() - self.start_pos.x()) + \
                               abs(self._current_pos.y() - self.start_pos.y())
            except Exception as e:
                print(f"Distance calculation error: {e}")
                distance = 0

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
            elif abs_delta_y > (self.direction_threshold / 2) and abs_delta_y > abs_delta_x:
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
            if hasattr(self.win.animation_manager.drag_animator, 'drag_intensity'):
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
        self.performance_log = False

        # Adaptive buffer
        self.adaptive_buffer_size = self._calculate_optimal_buffer()
        self.position_buffer = [QPointF(0, 0)] * self.adaptive_buffer_size
        self.smoothed_position = QPointF(0, 0)
        self._smoothed_position = QPointF(0, 0)

        # Measure the initial performance
        self._initial_performance = self._measure_performance()

        # Static smoothing coefficient
        self.smooth_factor = self._calculate_optimal_smooth_factor(self._initial_performance)

        # Timer for rare performance checks
        self.performance_timer = QTimer()
        self.performance_timer.setInterval(10000)  # Check every 10 sec.
        self.performance_timer.timeout.connect(self._update_performance_settings)
        self.performance_timer.start()

        self.idle_timer = QTimer()
        self.idle_timer.setInterval(5000)
        self.idle_timer.setSingleShot(True)

        self.animation = QPropertyAnimation()
        self.animation.setDuration(2500)
        self.animation.setEasingCurve(QEasingCurve.OutQuad)
        self.is_animating = False

    def set_perfomance_logging(self, enabled: bool):
        self.performance_log = enabled

        if self.performance_log:
            print(f"🔧 Initial Performance: {self._initial_performance:.0f}мкс"
                  f" -> smooth={self.smooth_factor},"
                  f"buffer={self.adaptive_buffer_size}")

    def get_local_coords(self):
        """Calculates the local coordinates relative to the widget"""
        global_pos = QCursor.pos()
        return self.widget.mapFromGlobal(global_pos)

    def _measure_performance(self):
        """Measures performance in microseconds"""
        test_cycles = 1000
        start = time.perf_counter()

        for _ in range(test_cycles):
            QPointF(0, 0).x()

        return (time.perf_counter() - start) * 1000000  # мкс

    def _calculate_optimal_smooth_factor(self, elapsed_us):
        """COMPENSATION: the more powerful the PC, the LOWER the coefficient (MORE anti-aliasing)"""
        if elapsed_us < 200:  # Super Performance PC
            return 0.15  # Very strong anti-aliasing (compensating for high frequency)
        elif elapsed_us < 400:  # Performance PC
            return 0.2  # Strong anti-aliasing
        elif elapsed_us < 600:  # Mid PC
            return 0.25  # Middle anti-aliasing
        elif elapsed_us < 800:  # Slow PC
            return 0.3  # Low anti-aliasing
        else:  # Very slow PC
            return 0.035  # Minimum anti-aliasing

    def _calculate_optimal_buffer(self):
        """Automatic buffer size selection based on performance"""
        # Use performance measurement
        elapsed_us = self._measure_performance()

        if elapsed_us < 150:
            return 25    # Max buffer for super powerful PCs
        elif elapsed_us < 300:
            return 15    # Large buffer for powerful PCs
        elif elapsed_us < 500:
            return 10    # Middle buffer
        elif elapsed_us < 700:
            return 8     # A small buffer for weak PCs
        else:
            return 5     # Minimum buffer for very weak PCs

    def get_smoothed_coords(self):
        """Get smoothed coordinates with COMPENSATION"""
        try:
            current_pos = self.widget.mapFromGlobal(QCursor.pos())

            # Update the buffer
            self.position_buffer.pop(0)
            self.position_buffer.append(current_pos)

            # Weighted average (higher weight for the last positions)
            weights = list(range(1, len(self.position_buffer) + 1))
            total_weight = sum(weights)

            weighted_x = sum(p.x() * w for p, w in zip(self.position_buffer, weights)) / total_weight
            weighted_y = sum(p.y() * w for p, w in zip(self.position_buffer, weights)) / total_weight

            # Exponential smoothing
            self.smoothed_position = QPointF(
                self.smoothed_position.x() * (1 - self.smooth_factor) + weighted_x * self.smooth_factor,
                self.smoothed_position.y() * (1 - self.smooth_factor) + weighted_y * self.smooth_factor
            )

            return self.smoothed_position
        except Exception:
            return QPointF(0, 0)

    def _update_performance_settings(self):
        """Rare performance settings update"""

        # We measure the current performance
        current_performance = self._measure_performance()

        if self.performance_log:
            print(f"🔧 Current Performance: {current_performance:.0f}мкс "
                  f"-> smooth={self.smooth_factor}, "
                  f"buffer={self.adaptive_buffer_size}")

        # Only if the performance has changed a lot
        current_category = self._get_performance_category(current_performance)
        initial_category = self._get_performance_category(self._initial_performance)

        if current_category != initial_category:
            # Gently adapt the coefficient
            target_factor = self._get_target_smooth_factor(current_category)
            self.smooth_factor = target_factor

            self.adaptive_buffer_size = self._get_target_buffer_size(current_category)
            # Update buffer
            while len(self.position_buffer) < self.adaptive_buffer_size:
                self.position_buffer.append(QPointF(0, 0))
            while len(self.position_buffer) > self.adaptive_buffer_size:
                self.position_buffer.pop(0)

    def _get_performance_category(self, elapsed_us):
        """Defines the performance category"""
        if elapsed_us < 200:
            return "ultra"
        elif elapsed_us < 300:
            return "high"
        elif elapsed_us < 500:
            return "medium"
        else:
            return "low"

    def _get_target_smooth_factor(self, category):
        """Returns the smoothing coefficient for the category"""
        return {
            "ultra": 0.15,
            "high": 0.2,
            "medium": 0.25,
            "low": 0.3
        }[category]

    def _get_target_buffer_size(self, category):
        """Returns the buffer size for the category"""
        return {
            "ultra": 25,
            "high": 15,
            "medium": 10,
            "low": 5
        }[category]

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