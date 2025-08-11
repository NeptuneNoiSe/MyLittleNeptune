import os
from PySide6 import QtCore
from PySide6.QtCore import QTimerEvent, Qt, QTimer, QSize, QPropertyAnimation, QEasingCurve,QPoint, QPointF, QElapsedTimer
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
# TODO: [WIP] Новый класс анимации перетаскивания Требуется:
#           1. Тестирование и отладка
#           2. Перенос класса в AnimationPlayer
class DragAnimator:
    def __init__(self, input_handler):
        self.input_handler = input_handler
        self.angle = 0.0
        self.return_timer = QTimer()
        self.return_timer.timeout.connect(self._update_return_animation)
        self.return_timer.setInterval(16)  # ~60 FPS

    def update_drag_animation(self):
        """Обновление анимации наклона"""
        try:
            self.angle = self.input_handler.drag_direction * self.input_handler.drag_intensity * 10
            if hasattr(self.input_handler.win, 'model'):
                self.input_handler.win.model.Rotate(int(self.angle))
        except Exception as e:
            print(f"Rotation error: {e}")

    def start_return_animation(self):
        """Запуск плавного возврата"""
        if not self.return_timer.isActive():
            self.return_timer.start()

    def _update_return_animation(self):
        """Кадр анимации возврата"""
        if abs(self.angle) < 0.1:  # Порог завершения
            self.angle = 0
            self.return_timer.stop()
        else:
            self.angle *= 0.7  # Коэффициент плавности

        if hasattr(self.input_handler.win, 'model'):
            self.input_handler.win.model.Rotate(int(self.angle))

class InputHandler:
    def __init__(self, win, model):
        self.win = win
        self.model = model
        self.drag_animator = DragAnimator(self)
        self.sleep_move = False
        self.place_this = False
        self.input_lock = False
        self.mouse_press_timer = QElapsedTimer()
        self.hold_timer = QTimer()
        self.hold_timer.setSingleShot(True)
        self.hold_timer.timeout.connect(self.mouse_long_press)

        self.start_pos = QPoint(0, 0)  # Явная инициализация
        self.last_pos = QPoint(0, 0)  # с целыми числами
        self.drag_direction = 0  # -1 влево, 0 нейтрально, 1 вправо
        self.drag_intensity = 0  # сила покачивания (0-1)
        self.angle = 0

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
        """Гарантированно корректная обработка координат"""
        try:
            # Преобразование в целочисленные координаты
            if hasattr(global_pos, 'toPoint'):
                current_pos = global_pos.toPoint()
            else:
                try:
                    x = int(round(global_pos.x()))
                    y = int(round(global_pos.y()))
                    current_pos = QPoint(x, y)
                except (AttributeError, TypeError):
                    print(f"Invalid pos: {global_pos}")
                    return

            # Первый вызов - инициализация
            if self.last_pos.isNull():
                self.start_pos = current_pos
                self.last_pos = current_pos
                return

            # Вычисление delta с проверкой
            delta_x = current_pos.x() - self.last_pos.x()
            print(f"Pos: {current_pos.x()},{current_pos.y()} | "
                  f"Last: {self.last_pos.x()},{self.last_pos.y()} | "
                  f"Delta: {delta_x}")

            # Обновление параметров drag
            if abs(delta_x) > 2:
                direction = 1 if delta_x > 0 else -1
                self.drag_direction = 0.9 * self.drag_direction + 0.1 * direction
                self.drag_intensity = min(
                    (current_pos - self.start_pos).manhattanLength() / 100,
                    1.0
                )
                self._trigger_drag_animation()

            # Всегда обновляем last_pos
            self.last_pos = current_pos

        except Exception as e:
            print(f"Move error: {type(e).__name__}: {str(e)}")

    def _trigger_drag_animation(self):
        """Активация анимации с проверками"""
        if (not self.win.character.tired_controller.sleep
                and not self.input_lock):
            try:
                self.win.character.state.set_drag_state()
                if hasattr(self.win.talk_widget, 'dialog_animation'):
                    self.win.talk_widget.dialog_animation = False
                self.update_drag_animation()
            except AttributeError as e:
                print(f"Animation error: {e}")

    def reset_drag_animation(self):
        """Инициирует возврат в исходное положение"""
        self.drag_animator.start_return_animation()

    def update_drag_animation(self):
        """Обновляет анимацию перетаскивания"""
        self.drag_animator.update_drag_animation()

    def reset_drag_state(self):
        """Сбрасывает состояние перетаскивания"""
        self.start_pos = QPoint()
        self.last_pos = QPoint()
        self.drag_direction = 0
        self.drag_intensity = 0
        self.reset_drag_animation()


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