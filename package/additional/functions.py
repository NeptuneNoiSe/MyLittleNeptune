import os
from PySide6 import QtCore
from PySide6.QtCore import QTimerEvent, Qt, QTimer, QSize, QPropertyAnimation, QEasingCurve, QPointF
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPixmap, QMovie, QCursor

from package import resources
from package.additional.animations import AnimationsManager
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
        return smooth_pos

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
    def loadResource(win):
        # Transform Animations Resource
        win.t_anim_in = os.path.join(
            resources.RESOURCES_DIRECTORY, "animations/transform_in.webp")
        win.t_anim_out = os.path.join(
            resources.RESOURCES_DIRECTORY, "animations/transform_out.webp")
        win.transformMovie = QMovie(win.t_anim_in)
        win.transformLabel.setMovie(win.transformMovie)

        win.en = os.path.join(
            resources.RESOURCES_DIRECTORY, "lang/en.json")
        win.ru = os.path.join(
            resources.RESOURCES_DIRECTORY, "lang/ru.json")

    def external_anim_init(win):
        # Load Extra Motions
        drag_down_path = os.path.join(resources.RESOURCES_DIRECTORY,
                                      "v3/external_motions/drag_down.motion3.json")
        side_touch_head_path = os.path.join(resources.RESOURCES_DIRECTORY,
                                            "v3/external_motions/side_touch_head.motion3.json")
        touch_body_path = os.path.join(resources.RESOURCES_DIRECTORY,
                                       "v3/external_motions/touch_body.motion3.json")
        touch_body2_path = os.path.join(resources.RESOURCES_DIRECTORY,
                                        "v3/external_motions/touch_body2.motion3.json")
        touch_body3_path = os.path.join(resources.RESOURCES_DIRECTORY,
                                        "v3/external_motions/touch_body3.motion3.json")
        touch_bra_path = os.path.join(resources.RESOURCES_DIRECTORY,
                                      "v3/external_motions/touch_bra.motion3.json")
        touch_bra1_path = os.path.join(resources.RESOURCES_DIRECTORY,
                                      "v3/external_motions/touch_bra1.motion3.json")
        touch_bra2_path = os.path.join(resources.RESOURCES_DIRECTORY,
                                       "v3/external_motions/touch_bra2.motion3.json")
        touch_bra3_path = os.path.join(resources.RESOURCES_DIRECTORY,
                                       "v3/external_motions/touch_bra3.motion3.json")
        touch_head_path = os.path.join(resources.RESOURCES_DIRECTORY,
                                       "v3/external_motions/touch_head.motion3.json")
        touch_head2_path = os.path.join(resources.RESOURCES_DIRECTORY,
                                        "v3/external_motions/touch_head2.motion3.json")
        touch_hl_path = os.path.join(resources.RESOURCES_DIRECTORY,
                                     "v3/external_motions/touch_hl.motion3.json")
        touch_hl1_path = os.path.join(resources.RESOURCES_DIRECTORY,
                                      "v3/external_motions/touch_hl1.motion3.json")
        touch_hl2_path = os.path.join(resources.RESOURCES_DIRECTORY,
                                      "v3/external_motions/touch_hl2.motion3.json")
        touch_hr_path = os.path.join(resources.RESOURCES_DIRECTORY,
                                     "v3/external_motions/touch_hr.motion3.json")
        touch_hr1_path = os.path.join(resources.RESOURCES_DIRECTORY,
                                      "v3/external_motions/touch_hr1.motion3.json")
        touch_hr2_path = os.path.join(resources.RESOURCES_DIRECTORY,
                                      "v3/external_motions/touch_hr2.motion3.json")
        touch_leg_path = os.path.join(resources.RESOURCES_DIRECTORY,
                                      "v3/external_motions/touch_leg.motion3.json")
        touch_leg1_path = os.path.join(resources.RESOURCES_DIRECTORY,
                                       "v3/external_motions/touch_leg1.motion3.json")
        touch_leg2_path = os.path.join(resources.RESOURCES_DIRECTORY,
                                      "v3/external_motions/touch_leg2.motion3.json")
        touch_leg3_path = os.path.join(resources.RESOURCES_DIRECTORY,
                                       "v3/external_motions/touch_leg3.motion3.json")

        win.model.LoadExtraMotion("Extra", 0, drag_down_path)
        win.model.LoadExtraMotion("Extra", 1, side_touch_head_path)
        win.model.LoadExtraMotion("Extra", 2, touch_body_path)
        win.model.LoadExtraMotion("Extra", 3, touch_body2_path)
        win.model.LoadExtraMotion("Extra", 4, touch_body3_path)
        win.model.LoadExtraMotion("Extra", 5, touch_bra_path)
        win.model.LoadExtraMotion("Extra", 6, touch_bra1_path)
        win.model.LoadExtraMotion("Extra", 7, touch_bra2_path)
        win.model.LoadExtraMotion("Extra", 8, touch_bra3_path)
        win.model.LoadExtraMotion("Extra", 9, touch_head_path)
        win.model.LoadExtraMotion("Extra", 10, touch_head2_path)
        win.model.LoadExtraMotion("Extra", 11, touch_hl_path)
        win.model.LoadExtraMotion("Extra", 12, touch_hl1_path)
        win.model.LoadExtraMotion("Extra", 13, touch_hl2_path)
        win.model.LoadExtraMotion("Extra", 14, touch_hr_path)
        win.model.LoadExtraMotion("Extra", 15, touch_hr1_path)
        win.model.LoadExtraMotion("Extra", 16, touch_hr2_path)
        win.model.LoadExtraMotion("Extra", 17, touch_leg_path)
        win.model.LoadExtraMotion("Extra", 18, touch_leg1_path)
        win.model.LoadExtraMotion("Extra", 19, touch_leg2_path)
        win.model.LoadExtraMotion("Extra", 20, touch_leg3_path)

    def setLanguage(win):
        if win.language == "English":
            with open(win.en, 'r', encoding='utf-8') as file:
                win.lang = json.load(file)
        elif win.language == "Russian":
            with open(win.ru, 'r', encoding='utf-8') as file:
                win.lang = json.load(file)

    def savePng(win, fName):
        data = gl.glReadPixels(0, 0, win.width(), win.height(), gl.GL_RGBA, gl.GL_UNSIGNED_BYTE)
        data = np.frombuffer(data, dtype=np.uint8).reshape(win.height(), win.width(), 4)
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

    def initializeAnimations(win):
        win.external_anim_init()
        win.anim_manager = AnimationsManager(win.model)
        win.change_character(win.character_name)
        win.anim_manager.set_logging(win.callbacks_log)

    def change_character(win, name: str):
        """Set character name in Animation Manager """
        win.anim_manager.character_name = name

    def add_random_expression(win, drop_last=False):
        if drop_last:
            win.model.RemoveExpression(win.lastExpressionId)

        expressions = win.model.GetExpressions()
        expId = random.choice(expressions)
        win.model.AddExpression(expId)

        win.lastExpressionId = expId
        win.activeExpressions.append(expId)
        win.fadeoutTimer.start(7000)
        return expId

    def update_idle_counter(win):
        """Update the idle counter"""
        if not win.mouse_tracker.mouse_move:
            #win.mouse_tracker.idle_timer.start()
            pass

    def update_mouse_tracking(win):
        """Main mouse tracking update method"""
        if win.mouse_tracker.update_state():
            if (win.model is not None
                    and not win.mouse_tracker.is_animating
                    and win.tracking_mouse
                    and win.tracking_mouse_switch):
                smooth_pos = win.mouse_tracker.get_smoothed_coords()
                if win.model:
                    win.model.Drag(smooth_pos.x(), smooth_pos.y())
                    if win.mouse_tracking_log:
                        log_x = int(smooth_pos.x()) if smooth_pos.x().is_integer() else round(smooth_pos.x())
                        log_y = int(smooth_pos.y()) if smooth_pos.y().is_integer() else round(smooth_pos.y())
                        print(f"Mouse moving: X={log_x} Y={log_y}")

    def handle_mouse_idle(win):
        """Mouse inactivity handler"""
        if win.mouse_tracker.is_animating:
            return

        if win.mouse_tracking_log:
            print("Mouse is steady")

        target_x = 0 - win.frmX * -0.25
        target_y = 0 - win.frmY * -0.5

        def update_position(pos):
            win.posX = pos.x()
            win.posY = pos.y()
            if hasattr(win, 'model') and win.model is not None:
                win.model.Drag(win.posX, win.posY)

        win.mouse_tracker.start_reset_animation(target_x, target_y, update_position)

    def transparent_input(win):
        win.setWindowFlags(win.windowFlags() & ~QtCore.Qt.WindowTransparentForInput)
        win.show()
        win.mouse_input_timer.stop()

    def idle_timer(win) -> None:
        # Timer Diagnostic Log
        if win.timer_log:
            print(win.t_count, "-", win.condition, "Condition")
        win.t_count += 1
        if win.t_count <= win.sad_v:
            win.condition = "Idle"
        if win.t_count <= win.sleep_v and win.idle_switch == True:
            win.idle_anim = True
        if win.t_count >= 5:
            win.set_icon = True
        if win.t_count >= 10 and win.sleep_switch == False:
            win.t_count = 1
        if win.t_count == win.sad_v:
            win.condition = "Sad"
            win.model.SetExpression("Sad")
            win.text = win.lang['Talk']['Sad']
            win.kaomoji = "(´•ω•̥`)"
            print(win.name + ": " + win.text + win.kaomoji)
            win.textUpdate()
        if win.t_count == win.tired_v and win.sleep_switch == True:
            win.condition = "Tired"
            win.model.SetExpression("Tired")
            win.text = win.lang['Talk']['Tired']
            win.kaomoji = "(๑•﹏•)"
            print(win.name + ": " + win.text + win.kaomoji)
            win.textUpdate()
        if win.t_count == win.sleep_v and win.sleep_switch == True:
            if win.tracking_mouse_switch:
                win.tracking_mouse = False
                win.handle_mouse_idle()
                win.mouse_tracker.set_sleep_state(True)
            win.condition = "Sleep"
            win.text = win.lang['Talk']['Sleep']
            win.kaomoji = "(ᴗ˳ᴗ)ｚｚＺ"
            print(win.name + ": " + win.text + win.kaomoji)
            win.textUpdate()
        if win.t_count == win.wake_up_v and win.sleep_switch == True:
            win.model.ResetAllParameters()
            # win.wake_up_func()
            win.anim_manager.set_sleep_state(False)
            win.model.ResetExpressions()
            win.model.SetExpression("Star")
            win.model.SetExpression("Serious")
            win.fadeoutTimer.start(10000)
            win.t_count = 0
            win.idle_anim = True
            win.wake_up = True
            win.sleep = False
            win.mouse_tracker.set_sleep_state(False)
            win.tracking_mouse = True
            win.text = win.lang['Talk']['WakeUp']
            win.kaomoji = "(O_~)/"
            print(win.name + ":", "I'm WakeUp (O_~)/")
            win.textUpdate()

    def sleep_func(win):
        # win.setSleepParams()
        # Model is not rotate now
        # win.model.Rotate(win.modelRotate)
        # win.sleepLabel = QLabel(win)
        # win.cloud = os.path.join(
        #    resources.RESOURCES_DIRECTORY, "images/cloud.webp")
        # win.cloudPixmap = QPixmap(win.cloud).scaled(QSize(win.w_resize, win.h_resize),
        #                                            Qt.KeepAspectRatio, Qt.SmoothTransformation)
        # win.sleepLabel.setPixmap(win.cloudPixmap)
        # win.sleepLabel.move(0, win.sleepMoveY * win.a_scale * win.models_scale)
        # win.sleepLabel.show()
        win.anim_manager.set_sleep_state(True)
        win.idle_anim = False
        win.wake_up = False
        win.sleep = True
        win.model.SetExpression("ClosedEyes")
        # win.sleepMove = False
        # if win.x() >= win.SrcSize.width() - win.width() or  win.x() >= win.vSize.width() - win.width():
        #    win.move(win.x() - win.w_resize / 3.5, win.y() + win.h_resize / 4)
        #    win.sleepMove = True
        #    win.sleepSide = "Right"
        # elif win.x() <= 0 + win.width() or win.x() <= win.SrcSize.width() - win.vSize.width() + win.width():
        #    win.move(win.x() + win.w_resize / 4, win.y() + win.h_resize / 4)
        #    win.sleepMove = True
        #    win.sleepSide = "Left"

    def wake_up_func(win):
        pass
        # Legacy Function ( may be removed )
        #win.sleepLabel.close()
        #win.model.Rotate(0)
        #if win.sleepMove and win.sleepSide == "Right":
        #    win.move(win.x() + win.w_resize / 3.5, win.y() - win.h_resize / 4)
        #elif win.sleepMove and win.sleepSide == "Left":
        #    win.move(win.x() - win.w_resize / 4, win.y() - win.h_resize / 4)
        # win.sleepMove = False
        #win.sleepSide = None

    def timers_init(win) -> None:
        # Idle timer
        win.timer = QTimer()
        win.timer.timeout.connect(win.idle_timer)
        win.timer.start(int(6000 / win.time_scale))

        # Mouse tracking timer
        win.mouse_tracker.idle_timer.timeout.connect(win.handle_mouse_idle)

        #Main tracking update timer
        win.update_timer = QTimer()
        win.update_timer.timeout.connect(win.update_mouse_tracking)
        win.update_timer.start(10)  # Update every 10 ms

        # Update idle counter timer
        win.idle_counter_timer = QTimer()
        win.idle_counter_timer.timeout.connect(win.update_idle_counter)
        win.idle_counter_timer.start(10)  # Update every 10 ms

        # Input release timer
        win.mouse_input_timer = QTimer()
        win.mouse_input_timer.timeout.connect(win.transparent_input)

        # Dialog close timer
        win.dialogCloseTimer = QTimer()
        win.dialogCloseTimer.timeout.connect(win.dialogClose)

        # GoodBye timer
        win.goodByeTimer = QTimer()
        win.goodByeTimer.timeout.connect(win.hello)

        # Quit timer
        win.quitTimer = QTimer()
        win.quitTimer.timeout.connect(win.quitFunction)

        # Talk Delay timer
        win.talkDelayTimer = QTimer()
        win.talkDelayTimer.timeout.connect(win.takingTalk)

        # Sleep Move timer
        win.sleepInputTimer = QTimer()
        win.sleepInputTimer.timeout.connect(win.takingSleep)

        # Fadeout timer
        win.fadeoutTimer = QTimer()
        win.fadeoutTimer.timeout.connect(win.resetExp)

    def takingSleep(win):
        # win.sleepMove = True
        win.sleepInputTimer.stop()

    def resetExp(win):
        win.model.ResetExpressions()
        win.fadeoutTimer.stop()

    def quitFunction(win):
        win.quitTimer.stop()
        exit(0)