import os
from PySide6 import QtCore
from PySide6.QtCore import QTimerEvent, Qt, QTimer, QSize
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPixmap, QMovie

from package import resources
from package.additional.config_module import *
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
            win.text = win.lang['sad']
            win.kaomoji = "(´•ω•̥`)"
            print(win.name + ": " + win.text + win.kaomoji)
            win.textUpdate()
        if win.t_count == win.tired_v and win.sleep_switch == True:
            win.condition = "Tired"
            win.model.SetExpression("Tired")
            win.text = win.lang['tired']
            win.kaomoji = "(๑•﹏•)"
            print(win.name + ": " + win.text + win.kaomoji)
            win.textUpdate()
        if win.t_count == win.sleep_v and win.sleep_switch == True:
            win.condition = "Sleep"
            win.text = win.lang['sleep']
            win.kaomoji = "(ᴗ˳ᴗ)ｚｚＺ"
            print(win.name + ": " + win.text + win.kaomoji)
            win.textUpdate()
        if win.t_count == win.wake_up_v and win.sleep_switch == True:
            win.wake_up_func()
            win.model.ResetExpression()
            win.model.SetExpression("Star", fadeout=10000)
            win.model.SetExpression("Serious", fadeout=10000)
            win.t_count = 0
            win.idle_anim = True
            win.wake_up = True
            win.sleep = False
            win.text = win.lang['wake_up']
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
        win.model.ResetParameters()
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

    def takingSleep(win):
        win.sleepMove = True
        win.sleepInputTimer.stop()

    def quitFunction(win):
        win.quitTimer.stop()
        exit(0)