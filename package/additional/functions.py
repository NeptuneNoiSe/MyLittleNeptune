from PySide6 import QtCore
from PySide6.QtCore import QTimerEvent, Qt, QTimer

from package import resources
from package.additional.config_module import *

class Functions:
    def mouse_tracking(win):
        win.tracking_mouse = False
        if win.posX <= 0 or win.posY <= 0:
            win.posX = 0 + win.frmX * 0.15
            win.posY = 0 + win.h_resize * 0.25

        if win.mouse_tracking_log:
            print("Mouse is steady", win.tracking_mouse, win.posX, win.posY)

        try:
            win.model.Drag(win.posX, win.posY)
        except AttributeError:
            pass

    def transparent_input(win):
        win.setWindowFlags(win.windowFlags() & ~QtCore.Qt.WindowTransparentForInput)
        win.show()
        win.mouse_input_timer.stop()

    def idle_timer(win) -> None:
        try:
            # Timer Diagnostic Log
            if win.timer_log:
                print(win.t_count, "-", win.condition, "Condition")
            win.t_count += 1
            if win.t_count <= win.sad_v:
                win.condition = "Idle"
            if win.t_count <= win.sleep_v and win.idle_switch == True:
                win.idle_anim = True
            if win.t_count >= 10 and win.sleep_switch == False:
                win.t_count = 1
            if win.t_count == win.sad_v:
                win.condition = "Sad"
                win.model.SetExpression("Sad")
                win.text = "I'm Sad"
                win.kaomoji = "(´•ω•̥`)"
                print(win.character_name + ": " + win.text + win.kaomoji)
                win.textUpdate()
            if win.t_count == win.tired_v and win.sleep_switch == True:
                win.condition = "Tired"
                win.model.SetExpression("Tired")
                win.text = "I'm Tired"
                win.kaomoji = "(๑•﹏•)"
                print(win.character_name + ": " + win.text + win.kaomoji)
                win.textUpdate()
            if win.t_count == win.sleep_v and win.sleep_switch == True:
                win.condition = "Sleep"
                win.model.SetExpression("ClosedEyes")
                if win.tracking_mouse_switch:
                    win.tracking_mouse = False
                win.idle_anim = False
                win.sleep = True
                win.wake_up = False
                win.text = "I'm Sleep"
                win.kaomoji = "(ᴗ˳ᴗ)ｚｚＺ"
                print(win.character_name + ": " + win.text + win.kaomoji)
                win.textUpdate()
            if win.t_count == win.wake_up_v and win.sleep_switch == True:
                win.model.ResetExpression()
                win.model.SetExpression("Star", fadeout=10000)
                win.model.SetExpression("Serious", fadeout=10000)
                win.t_count = 0
                win.idle_anim = True
                win.wake_up = True
                win.text = "I'm WakeUp"
                win.kaomoji = "(O_~)/"
                print(win.character_name + ":", "I'm WakeUp (O_~)/")
                win.textUpdate()
        except AttributeError:
            pass

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

    def quitFunction(win):
        win.quitTimer.stop()
        exit(0)