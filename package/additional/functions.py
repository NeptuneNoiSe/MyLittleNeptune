import os
from PySide6 import QtCore
from PySide6.QtCore import QTimerEvent, Qt, QTimer, QSize, QPropertyAnimation, QEasingCurve, QPointF
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPixmap, QMovie, QCursor

from package import resources
from package.additional.animations import AnimationsManager
from package.additional.animations import TiredAnimation
from package.additional.resource_mng import ResourceManager
from package.additional.config_module import *
import live2d.v3 as live2d
import OpenGL.GL as gl
import numpy as np
import random
import time
import math
from PIL import Image
import resources
import json

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

class Functions:
    def __init__(self, win, model):
        self.model = model
        self.win = win
        self.resource_manager = ResourceManager(resources.RESOURCES_DIRECTORY)
        self.anim_manager = None

        # Main tracking update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_mouse_tracking)
        self.update_timer.start(10)  # Update every 10 ms

        # Update idle counter timer
        self.idle_counter_timer = QTimer()
        self.idle_counter_timer.timeout.connect(self.update_idle_counter)
        self.idle_counter_timer.start(10)  # Update every 10 ms

        # Input release timer
        self.mouse_input_timer = QTimer()
        self.mouse_input_timer.timeout.connect(self.transparent_input)

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

    def initAnimations(self):
        self.win.tired_anim = TiredAnimation(self.win)
        self.win.anim_manager = AnimationsManager(self.win.model)
        self.change_character(self.win.character_name)
        self.win.anim_manager.set_logging(self.win.callbacks_log)

    def change_character(self, name: str):
        """Set character name in Animation Manager """
        self.win.anim_manager.character_name = name

    def add_random_expression(self,drop_last=False):
        if drop_last:
            self.win.model.RemoveExpression(self.win.lastExpressionId)

        expressions = self.win.model.GetExpressions()
        expId = random.choice(expressions)
        self.win.model.AddExpression(expId)

        self.win.lastExpressionId = expId
        self.win.activeExpressions.append(expId)
        self.win.fadeoutTimer.start(7000)
        return expId

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

    def transparent_input(self):
        self.win.setWindowFlags(self.win.windowFlags() & ~QtCore.Qt.WindowTransparentForInput)
        self.win.show()
        self.mouse_input_timer.stop()