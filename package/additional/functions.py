import os
from PySide6 import QtCore
from PySide6.QtCore import QTimerEvent, Qt, QTimer, QSize
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPixmap, QMovie

from package import resources
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

    def setLanguage(win):
        if win.language == "English":
            with open(win.en, 'r', encoding='utf-8') as file:
                win.lang = json.load(file)
        elif win.language == "Russian":
            with open(win.ru, 'r', encoding='utf-8') as file:
                win.lang = json.load(file)

    def _play_idle_animation(win):
        """Running animations with timer updates"""
        win.model.StartRandomMotion("Id"
                                    "le",live2d.MotionPriority.IDLE,
                                    onStart=lambda g, n: win._handle_idle_start(g, n),
                                    onFinish=lambda g, n: win._handle_idle_finish(g, n)
        )
        win._is_idle_playing = True
        win._last_idle_time = time.time()
        win._next_idle_delay = random.uniform(5.0, 15.0)  # Pause 5-15 sec

    def _handle_idle_start(win, group, no):
        """Callback Animation Start"""
        win._is_idle_playing = True
        # print(f"Idle started: {group}-{no}")

    def _handle_idle_finish(win, group, no):
        """Callback Animation Finish"""
        win._is_idle_playing = False
        win.model.ResetExpressions()
        # print(f"Idle finished: {group}-{no}")

    def _reset_idle_state(win):
        """Reset with Sleep"""
        win._is_idle_playing = False
        win._last_idle_time = 0

    def _handle_motion_start(win, group, no):
        """Callback with Animation Start"""
        if win.callbacks_log:
            print(f"Animation {group} {no} start - blink off")
        win.setBlinkEnabled(False)  # Using our previously created method

    def _handle_motion_finish(win, group, no):
        """Callback with Animation Finish"""
        win.model.ResetExpressions()
        if win.callbacks_log:
            print(f"Animation {group} {no} finish - blink on")
        win.setBlinkEnabled(True)
        # Additionally: reset the eyes to the open state
        win.model.SetParameterValueById("ParamEyeLOpen", 1.0)
        win.model.SetParameterValueById("ParamEyeROpen", 1.0)
        win.model.SetParameterValueById("ParamMouthOpenY", 0)

    def autoBlink(win) -> None:
        if not win.blink_enabled:  # If Blink disabled
            # Force open eyes (in case of interrupted blinking)
            #self.model.SetParameterValueById("ParamEyeLOpen", 1.0)
            #self.model.SetParameterValueById("ParamEyeROpen", 1.0)
            win.isBlinking = False
            return
        current_time = time.time()
        delta_time = current_time - win.last_update_time

        # Generating a new blink only if the eyes are fully open
        if not win.isBlinking and win.blinkProgress == 0.0:
            if current_time - win.lastBlinkTime > win.nextBlinkInterval / 1000.0:
                # Two randomization modes:
                if random.random() < 0.7:  # 70% chance - regular Blink mode
                    win.isBlinking = True
                    win.nextBlinkInterval = random.randint(2000, 5000)  # 2-5 секунд
                else:  # 30% chance - long pause mode (The character is "lost in thought")
                    win.nextBlinkInterval = random.randint(6000, 10000)  # 6-10 секунд
                win.lastBlinkTime = current_time

        # Blink animation (unchanged)
        if win.isBlinking:
            win.blinkProgress += delta_time * 4.0
            if win.blinkProgress >= 1.0:
                win.isBlinking = False
                win.blinkProgress = 0.0
            else:
                if win.blinkProgress < 0.4:
                    eye_open = 1.0 - math.sin(win.blinkProgress * math.pi * 1.25)
                else:
                    eye_open = math.sin((win.blinkProgress - 0.4) * math.pi * 0.833)

                # Adding micro-randomness for the right/left eye
                win.model.SetParameterValueById("ParamEyeLOpen", eye_open * random.uniform(0.98, 1.0))
                win.model.SetParameterValueById("ParamEyeROpen", eye_open * random.uniform(0.98, 1.0))

    def setBlinkEnabled(win, enabled: bool):
        """Blink Switch"""
        win.blink_enabled = enabled

        if enabled:
            if win.callbacks_log:
                print("Автоморгание включено")
        else:
            if win.callbacks_log:
                print("Автоморгание отключено")
            # Reset Blink Params
            win.isBlinking = False
            win.blinkProgress = 0.0
            # self.model.SetParameterValueById("ParamEyeLOpen", 1.0)
            # self.model.SetParameterValueById("ParamEyeROpen", 1.0)

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

    def mouse_tracking(win):
        win.tracking_mouse = False
        if win.posX <= 0 or win.posY <= 0:
            win.posX = 0 + win.frmX * 0.15
            win.posY = 0 + win.h_resize * 0.25

        if win.mouse_tracking_log:
            print("Mouse is steady", win.tracking_mouse, win.posX, win.posY)

        win.model.Drag(win.posX, win.posY)

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
            win.condition = "Sleep"
            win.text = win.lang['Talk']['Sleep']
            win.kaomoji = "(ᴗ˳ᴗ)ｚｚＺ"
            print(win.name + ": " + win.text + win.kaomoji)
            win.textUpdate()
        if win.t_count == win.wake_up_v and win.sleep_switch == True:
            win.wake_up_func()
            win.model.ResetExpressions()
            win.model.SetExpression("Star")
            win.model.SetExpression("Serious")
            win.fadeoutTimer.start(10000)
            win.t_count = 0
            win.idle_anim = True
            win.wake_up = True
            win.sleep = False
            win.setBlinkEnabled(True)
            win.text = win.lang['Talk']['WakeUp']
            win.kaomoji = "(O_~)/"
            print(win.name + ":", "I'm WakeUp (O_~)/")
            win.textUpdate()

    def sleep_func(win):
        win.setSleepParams()
        win.model.Rotate(win.modelRotate)
        win.sleepLabel = QLabel(win)
        win.cloud = os.path.join(
            resources.RESOURCES_DIRECTORY, "images/cloud.webp")
        win.cloudPixmap = QPixmap(win.cloud).scaled(QSize(win.w_resize, win.h_resize),
                                                    Qt.KeepAspectRatio, Qt.SmoothTransformation)
        win.sleepLabel.setPixmap(win.cloudPixmap)
        win.sleepLabel.move(0, win.sleepMoveY * win.a_scale * win.models_scale)
        win.sleepLabel.show()
        if win.tracking_mouse_switch:
            win.tracking_mouse = False
        win.idle_anim = False
        win.wake_up = False
        win.sleepMove = False
        win.sleep = True
        win.setBlinkEnabled(False)
        win.model.SetExpression("ClosedEyes")
        if win.x() >= win.SrcSize.width() - win.width() or  win.x() >= win.vSize.width() - win.width():
            win.move(win.x() - win.w_resize / 3.5, win.y() + win.h_resize / 4)
            win.sleepMove = True
            win.sleepSide = "Right"
        elif win.x() <= 0 + win.width() or win.x() <= win.SrcSize.width() - win.vSize.width() + win.width():
            win.move(win.x() + win.w_resize / 4, win.y() + win.h_resize / 4)
            win.sleepMove = True
            win.sleepSide = "Left"

    def wake_up_func(win):
        win.sleepLabel.close()
        win.model.ResetAllParameters()
        win.model.Rotate(0)
        if win.sleepMove and win.sleepSide == "Right":
            win.move(win.x() + win.w_resize / 3.5, win.y() - win.h_resize / 4)
        elif win.sleepMove and win.sleepSide == "Left":
            win.move(win.x() - win.w_resize / 4, win.y() - win.h_resize / 4)
        win.sleepMove = False
        win.sleepSide = None

    def timers_init(win) -> None:
        # Idle timer
        win.timer = QTimer()
        win.timer.timeout.connect(win.idle_timer)
        win.timer.start(int(6000 / win.time_scale))

        # Mouse tracking timer
        win.mouse_t = QTimer()
        win.mouse_t.timeout.connect(win.mouse_tracking)
        if not win.mouse_move:
            win.tracking_mouse = False
            win.mouse_t.start(10000)

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
        win.sleepMove = True
        win.sleepInputTimer.stop()

    def resetExp(win):
        win.model.ResetExpressions()
        win.fadeoutTimer.stop()

    def quitFunction(win):
        win.quitTimer.stop()
        exit(0)