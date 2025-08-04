import os
from PySide6 import QtCore
from PySide6.QtCore import QTimerEvent, Qt, QTimer, QSize, QPropertyAnimation, QEasingCurve, QPointF, QElapsedTimer
from PySide6.QtGui import QPixmap, QMovie, QCursor

# from package import resources
# from package.additional.animations import AnimationsManager
# from package.additional.animations import TiredAnimation
# from package.additional.resource_mng import ResourceManager
# from package.additional.config_module import *
# import live2d.v3 as live2d
# import OpenGL.GL as gl
import numpy as np
import random
import time
import math
from PIL import Image
# import resources
# import json


class InputHandler:
    def __init__(self, win, model):
        self.win = win
        self.model = model
        self.sleep_move = False
        self.place_this = False
        self.start_pos = None
        self.input_lock = False
        self.mouse_press_timer = QElapsedTimer()
        self.hold_timer = QTimer()
        self.hold_timer.setSingleShot(True)
        self.hold_timer.timeout.connect(self.mouse_long_press)

        # Input release timer
        self.mouse_input_timer = QTimer()
        self.mouse_input_timer.setSingleShot(True)
        self.mouse_input_timer.timeout.connect(self.transparent_input_disable)

        # Main tracking update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_mouse_tracking)
        self.update_timer.start(10)  # Update every 10 ms

        # Talk Delay timer
        self.talkDelayTimer = QTimer()
        self.talkDelayTimer.setSingleShot(True)
        self.talkDelayTimer.timeout.connect(self.takingTalk)

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
                smooth_pos = self.win.mouse_tracker.get_smoothed_coords()
                if self.win.model:
                    self.win.model.Drag(smooth_pos.x(), smooth_pos.y())
                    if self.win.mouse_tracking_log:
                        log_x = int(smooth_pos.x()) if smooth_pos.x().is_integer() else round(smooth_pos.x())
                        log_y = int(smooth_pos.y()) if smooth_pos.y().is_integer() else round(smooth_pos.y())
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
            self.mouse_press_timer.start()
            self.hold_timer.start(1500)  # 3 секунды
            self.talkDelayTimer.start(500)

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
        self.talkDelayTimer.stop()
        self.sleepInputTimer.stop()

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
        """Mouse move handler"""
        try:
            # Проверяем состояние перетаскивания даже если курсор вышел за границы
            if not hasattr(self, 'start_pos'):
                self.start_pos = global_pos

            distance = (global_pos - self.start_pos).manhattanLength()

            if (distance > 10
                    and not self.win.character.tired_controller.sleep
                    and not self.input_lock
                    and QCursor().pos() is not None):  # Дополнительная проверка

                self.win.character.state.set_drag_state()

        except Exception as e:
            print(f"Move handler error: {e}")
            self.win.talk_widget.close_dialog()

    def takingTalk(self):
        self.place_this = True
        self.talkDelayTimer.stop()

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
            self.smoothed_position.x() * (1 - self.smooth_factor) + avg_x * self.smooth_factor,
            self.smoothed_position.y() * (1 - self.smooth_factor) + avg_y * self.smooth_factor
        )

        return self.smoothed_position

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