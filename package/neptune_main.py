import os
import argparse
import OpenGL.GL as gl
import numpy as np
from PIL import Image
from PySide6 import QtCore
from PySide6.QtCore import QTimerEvent, Qt, QTimer, QSize, Slot, Signal
from PySide6.QtGui import QMouseEvent, QCursor, QScreen, QSurfaceFormat, QAction, QIcon, QMovie, QPixmap, QFont
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QApplication, QMenu, QMessageBox, QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, \
    QGroupBox, QGridLayout, QCheckBox, QDoubleSpinBox, QRadioButton, QFrame, QFormLayout, QSpacerItem, QSizePolicy
from PySide6.QtGui import QGuiApplication
from configparser import ConfigParser

import live2d.v3 as live2d
# from live2d.utils.lipsync import WavHandler
# from live2d.v3 import StandardParams
# import live2d.v2 as live2d
import resources
from config_module import *
from text_widget import TextWidget

def callback():
    motion_end_log = False
    if motion_end_log:
        print("motion end")

class Win(QOpenGLWidget, TextWidget):
    def __init__(self) -> None:
        super().__init__()
        self.textShow = None
        self.hintFlags: list[Qt.WindowType] = [
            Qt.WindowType.MSWindowsFixedSizeDialogHint,
            Qt.WindowType.X11BypassWindowManagerHint,
            Qt.WindowType.FramelessWindowHint,
            Qt.WindowType.NoDropShadowWindowHint,
            Qt.WindowType.WindowTitleHint,
            Qt.WindowType.WindowSystemMenuHint,
            Qt.WindowType.WindowMinimizeButtonHint,
            Qt.WindowType.WindowMaximizeButtonHint,
            Qt.WindowType.WindowCloseButtonHint,
            Qt.WindowType.WindowContextHelpButtonHint,
            Qt.WindowType.WindowShadeButtonHint,
            Qt.WindowType.WindowStaysOnTopHint,
            Qt.WindowType.WindowStaysOnBottomHint,
            Qt.WindowType.CustomizeWindowHint,
            Qt.WindowType.WindowTransparentForInput,
            Qt.WindowType.WindowType_Mask
        ]

        self.config = config_main
        # LOGS:
        # l2d-py Main Log:
        live2d.setLogEnable(False)
        # l2d-py Area Log:
        self.l2d_area_log = False
        # Mouse Click Log:
        self.mouse_click_log = False
        # Mouse Tracking Log:
        self.mouse_tracking_log = False
        # Timer Diagnostic Log:
        self.timer_log = False

        # Models Switch:
        self.models_switch = self.config.getint('Model', 'selected_model')

        # AutoScale: If True, the models is scaled based on the screen size
        self.auto_scale = self.config.getboolean('Scale', 'auto_scale')

        # Models Scale
        self.models_scale = self.config.getfloat('Scale', 'models_scale')

        # Tracking the mouse position
        self.tracking_mouse = True

        # Init Vars
        self.w_correction = 0
        self.h_correction = 0
        self.a_scale = 1
        self.auto_scale_init = False
        self.mouse_move = False
        self.mouse_timer = None
        self.isInLA = False
        self.clickInLA = False
        self.click = False
        self.test = False
        self.read = False
        self.clickX = -1
        self.clickY = -1
        self.posX = -1
        self.posY = -1
        self.transformLayout = QVBoxLayout()
        self.transformLabel = QLabel(self)
        self.text = "Hello!"
        self.kaomoji = "(^~^)/"
        self.transform = False
        self.goodness_form = None
        self.transform_state = False
        self.transform_lock = 0
        self.input_lock = False
        self.can_transform = False
        self.transform_text = True
        self.trm_mx = -50
        self.trm_my = 5
        self.trm_cmx = 100
        self.trm_cmy = 5
        self.twmX = 0
        self.twmY = 0
        self.twsc = 0
        self.talkX = 160
        self.talkY = 130
        self.talkFontSize = 10
        self.talk = True
        self.talkUpd = True
        self.placeThis = False
        self.model: live2d.LAppModel | None = None
        self.systemScale = QGuiApplication.primaryScreen().devicePixelRatio()
        self.sc_height_size = self.screen().size().height() * self.screen().devicePixelRatio()
        self.sc_width_size = self.screen().size().width() * self.screen().devicePixelRatio()
        self.SrcSize = QScreen.availableGeometry(QApplication.primaryScreen())
        #Set screen size
        self.config.set('Main', 'screen_width', str(self.sc_width_size))
        self.config.set('Main', 'screen_height',str(self.sc_height_size))
        if self.models_switch == 0:
            self.config.set('Model', 'x_param', '600')
            self.config.set('Model', 'y_param', '600')
        with open('config.ini', 'w') as cfg:
            cfg: [str, int, tuple, object]
            self.config.write(cfg)

        # Screen Size for AutoScale
        if self.auto_scale:
            self.a_scale = auto_scale(self.sc_height_size)
        if not self.auto_scale:
            self.a_scale = 1

        # Character Name
        self.character_name = self.config.get('Model', 'character_name')

        # Neptune Model parameters
        if self.models_switch == 0:
            self.goodness_form = False
            self.can_transform = True
            self.mx_param = self.config.getint('Model', 'x_param')
            self.my_param = self.config.getint('Model', 'y_param')
            self.w_res = int(self.mx_param * self.a_scale * self.models_scale)
            self.h_res = int(self.my_param * self.a_scale * self.models_scale)
            self.config.set('Model', 'w_resize', str(self.w_res))
            self.config.set('Model', 'h_resize', str(self.h_res))
            self.config.set('Model', 'w_correction', '-70')
            self.config.set('Model', 'h_correction', '0')
            with open('config.ini', 'w') as cfg:
                cfg: [str, int, tuple, object]
                self.config.write(cfg)

        # Model Resize
        self.w_resize = self.config.getint('Model', 'w_resize')
        self.h_resize = self.config.getint('Model', 'h_resize')
        self.w_correction = self.config.getfloat('Model', 'w_correction')
        self.h_correction = self.config.getfloat('Model', 'h_correction')

        # Model Resize
        self.resize(int(self.w_resize), int(self.h_resize))

        # Center on Axis X
        self.frmX = (self.SrcSize.width() - self.width()) - self.w_correction
        # Center on Axis Y
        self.frmY = (self.SrcSize.height() - self.height()) - self.h_correction
        # Move window
        self.move(int(self.frmX), int(self.frmY))

        # Windows flags
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        #self.wavHandler = WavHandler()
        #self.lipSyncN = 2.5
        #self.audioPlayed = False

        # Animation Vars
        self.condition = "Idle"
        self.sleep = False
        self.t_count = 1
        self.sad_v = 60
        self.tired_v = 80
        self.sleep_v = 100
        self.wake_up_v = 160

        # Tired Animation Time Scale
        self.time_scale = 1

        # Init Animation
        self.idle_anim = True
        self.on_mouse_anim = False
        self.tap_body_anim = False

        # Animation Switches
        self.idle_switch = self.config.getboolean('Animations', 'idle_animation')
        self.on_mouse_switch = self.config.getboolean('Animations', 'on_mouse_animation')
        self.tap_body_switch = self.config.getboolean('Animations', 'tap_body_animation')
        self.sleep_switch = self.config.getboolean('Settings', 'sleep')
        self.tracking_mouse_switch = self.config.getboolean('Settings', 'tracking_mouse')

        # Transform Animations Resource
        self.t_anim_in = os.path.join(
            resources.RESOURCES_DIRECTORY, "animations/transform_in.webp")
        self.t_anim_out = os.path.join(
            resources.RESOURCES_DIRECTORY, "animations/transform_out.webp")
        self.transformMovie = QMovie(self.t_anim_in)
        self.transformLabel.setMovie(self.transformMovie)

    def quitFunction(self):
        self.quitTimer.stop()
        exit(0)

    def transform_initialize(self):
        self.input_lock = True
        if not self.goodness_form:
            if self.character_name == "Neptune":
                self.model.SetExpression("Star")
            elif self.character_name == "NepGear":
                self.model.SetExpression("Star")
            else:
                self.model.SetExpression("Serious")
        if self.goodness_form:
            self.model.SetExpression("Funny")
        self.transformMovie = QMovie(self.t_anim_in)
        self.transformLabel.setMovie(self.transformMovie)
        self.transformLabel.movie().setScaledSize(QSize(int(self.w_resize + self.trm_cmx * self.models_scale),
                                                        int(self.h_resize + self.trm_cmy * self.models_scale))
                                                  ), Qt.KeepAspectRatio, Qt.SmoothTransformation
        self.transformMovie.start()
        self.transformLabel.move(int(self.trm_mx * self.models_scale), int(self.trm_my * self.models_scale))
        self.transformLabel.show()
        self.transform = True
        self.transform_lock = 0

    def transform_complete(self):
        if not self.goodness_form and self.transform_lock == 0:
            self.transform_to_goodness_form()
            self.transform_lock = 1
        if self.goodness_form and self.transform_lock == 0:
            self.transform_to_regular_form()
            self.transform_lock = 1
        self.model.ResetExpression()
        self.model.SetExpression("Funny", fadeout = 10000)
        self.transformMovie = QMovie(self.t_anim_out)
        self.transformLabel.setMovie(self.transformMovie)
        self.transformLabel.movie().setScaledSize(QSize(int(self.w_resize + self.trm_cmx * self.models_scale),
                                                        int(self.h_resize + self.trm_cmy * self.models_scale))
                                                  ), Qt.KeepAspectRatio, Qt.SmoothTransformation
        self.transformMovie.start()
        self.transformLabel.move(int(self.trm_mx * self.models_scale), int(self.trm_my * self.models_scale))
        self.transformLabel.show()
        self.transform = False
        self.talkUpd = True

    def transform_to_goodness_form(self):
        # Transform to Goodness Form
        if self.character_name == "Neptune":
            self.on_action_purple_heart()
        if self.character_name == "Noire":
            self.on_action_black_heart()
        if self.character_name == "Blanc":
            self.on_action_white_heart()
        if self.character_name == "Vert":
            self.on_action_green_heart()
        if self.character_name == "NepGear":
            self.on_action_purple_sister()
        if self.character_name == "Uni":
            self.on_action_black_sister()

    def transform_to_regular_form(self):
        # Transform to Regular Form
        if self.character_name == "Purple Heart":
            self.on_action_neptune()
        if self.character_name == "Black Heart":
            self.on_action_noire()
        if self.character_name == "White Heart":
            self.on_action_blanc()
        if self.character_name == "Green Heart":
            self.on_action_vert()
        if self.character_name == "Purple Sister":
            self.on_action_nepgear()
        if self.character_name == "Black Sister":
            self.on_action_uni()

    def mouse_tracking(self):
        self.tracking_mouse = False
        if self.posX <= 0 or self.posY <= 0:
            self.posX = 0 + self.frmX * 0.15
            self.posY = 0 + self.h_resize * 0.25

        if self.mouse_tracking_log:
            print("Mouse is steady", self.tracking_mouse, self.posX,self.posY)

        try:
            self.model.Drag(self.posX,self.posY)
        except AttributeError:
            pass

    def transparent_input(self):
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowTransparentForInput)
        self.show()
        self.mouse_input_timer.stop()

    def idle_timer(self) -> None:
        try:
            # Timer Diagnostic Log
            if self.timer_log:
                print(self.t_count, "-", self.condition, "Condition")
            self.t_count += 1
            if self.t_count <= self.sad_v:
                self.condition = "Idle"
            if self.t_count <= self.sleep_v and self.idle_switch == True:
                self.idle_anim = True
            if self.t_count >= 10 and self.sleep_switch == False:
                self.t_count = 1
            if self.t_count == self.sad_v:
                self.condition = "Sad"
                self.model.SetExpression("Sad")
                self.text = "I'm Sad"
                self.kaomoji = "(-_;)"
                print(self.character_name + ": " + self.text + self.kaomoji)
                self.textUpdate()
            if self.t_count == self.tired_v and self.sleep_switch == True:
                self.condition = "Tired"
                self.model.SetExpression("Tired")
                self.text = "I'm Tired"
                self.kaomoji = "(~o~)"
                print(self.character_name + ": " + self.text + self.kaomoji)
                self.textUpdate()
            if self.t_count == self.sleep_v and self.sleep_switch == True:
                self.condition = "Sleep"
                self.model.SetExpression("ClosedEyes")
                if self.tracking_mouse_switch:
                    self.tracking_mouse = False
                self.idle_anim = False
                self.sleep = True
                self.text = "I'm Sleep"
                self.kaomoji = "(~_~)zZz"
                print(self.character_name + ": " + self.text + self.kaomoji)
                self.textUpdate()
            if self.t_count == self.wake_up_v and self.sleep_switch == True:
                self.model.ResetExpression()
                self.model.SetExpression("Star", fadeout=10000)
                self.model.SetExpression("Serious", fadeout=10000)
                self.t_count = 0
                self.idle_anim = True
                self.text = "I'm WakeUp"
                self.kaomoji = "(O_~)/"
                print(self.character_name + ":", "I'm WakeUp (O_~)/")
                self.textUpdate()
        except AttributeError:
            pass

    def timersInit(self) -> None:
        # Idle timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.idle_timer)
        self.timer.start(int(6000 / self.time_scale))

        # Mouse tracking timer
        self.mouse_t = QTimer()
        self.mouse_t.timeout.connect(self.mouse_tracking)
        if not self.mouse_move:
            self.tracking_mouse = False
            self.mouse_t.start(10000)

        # Input release timer
        self.mouse_input_timer = QTimer()
        self.mouse_input_timer.timeout.connect(self.transparent_input)

        # Dialog close timer
        self.dialogCloseTimer = QTimer()
        self.dialogCloseTimer.timeout.connect(self.dialogClose)

        # GoodBye timer
        self.goodByeTimer = QTimer()
        self.goodByeTimer.timeout.connect(self.hello)

        # Quit timer
        self.quitTimer = QTimer()
        self.quitTimer.timeout.connect(self.quitFunction)

        # Talk Delay timer
        self.talkDelayTimer = QTimer()
        self.talkDelayTimer.timeout.connect(self.takingTalk)

    def initializeGL(self) -> None:
        self.makeCurrent()
        live2d.glInit()
        self.model = live2d.LAppModel()
        if live2d.LIVE2D_VERSION == 3:
            self.text = "Hello!"
            self.kaomoji = "(^~^)/"
            if self.models_switch == 0:
                self.goodness_form = False
                self.can_transform = True
                print(self.character_name + ": " + self.text + self.kaomoji)
                self.model.LoadModelJson(os.path.join(
                    resources.RESOURCES_DIRECTORY, "v3/Neptune/Neptune.model3.json"))

            elif self.models_switch == 1:
                self.goodness_form = True
                self.can_transform = True
                print(self.character_name + ": " + self.text + self.kaomoji)
                self.model.LoadModelJson(os.path.join(
                    resources.RESOURCES_DIRECTORY, "v3/PurpleHeart/PurpleHeart.model3.json"))

            elif self.models_switch == 2:
                self.goodness_form = False
                self.can_transform = True
                print(self.character_name + ": " + self.text + self.kaomoji)
                self.model.LoadModelJson(os.path.join(
                    resources.RESOURCES_DIRECTORY, "v3/Noire/Noire.model3.json"))

            elif self.models_switch == 3:
                self.goodness_form = True
                self.can_transform = True
                print(self.character_name + ": " + self.text + self.kaomoji)
                self.model.LoadModelJson(os.path.join(
                    resources.RESOURCES_DIRECTORY, "v3/BlackHeart/BlackHeart.model3.json"))

            elif self.models_switch == 4:
                self.goodness_form = False
                self.can_transform = True
                print(self.character_name + ": " + self.text + self.kaomoji)
                self.model.LoadModelJson(os.path.join(
                    resources.RESOURCES_DIRECTORY, "v3/Blanc/Blanc.model3.json"))

            elif self.models_switch == 5:
                self.goodness_form = True
                self.can_transform = True
                print(self.character_name + ": " + self.text + self.kaomoji)
                self.model.LoadModelJson(os.path.join(
                    resources.RESOURCES_DIRECTORY, "v3/WhiteHeart/WhiteHeart.model3.json"))

            elif self.models_switch == 6:
                self.goodness_form = False
                self.can_transform = True
                print(self.character_name + ": " + self.text + self.kaomoji)
                self.model.LoadModelJson(os.path.join(
                    resources.RESOURCES_DIRECTORY, "v3/Vert/Vert.model3.json"))

            elif self.models_switch == 7:
                self.goodness_form = True
                self.can_transform = True
                print(self.character_name + ": " + self.text + self.kaomoji)
                self.model.LoadModelJson(os.path.join(
                    resources.RESOURCES_DIRECTORY, "v3/GreenHeart/GreenHeart.model3.json"))

            elif self.models_switch == 8:
                self.goodness_form = False
                self.can_transform = True
                print(self.character_name + ": " + self.text + self.kaomoji)
                self.model.LoadModelJson(os.path.join(
                    resources.RESOURCES_DIRECTORY, "v3/NepGear/NepGear.model3.json"))

            elif self.models_switch == 9:
                self.goodness_form = True
                self.can_transform = True
                print(self.character_name + ": " + self.text + self.kaomoji)
                self.model.LoadModelJson(os.path.join(
                    resources.RESOURCES_DIRECTORY, "v3/PurpleSister/PurpleSister.model3.json"))

            elif self.models_switch == 10:
                self.goodness_form = False
                self.can_transform = True
                print(self.character_name + ": " + self.text + self.kaomoji)
                self.model.LoadModelJson(os.path.join(
                    resources.RESOURCES_DIRECTORY, "v3/Uni/Uni.model3.json"))

            elif self.models_switch == 11:
                self.goodness_form = True
                self.can_transform = True
                print(self.character_name + ": " + self.text + self.kaomoji)
                self.model.LoadModelJson(os.path.join(
                    resources.RESOURCES_DIRECTORY, "v3/BlackSister/BlackSister.model3.json"))

        else:
            self.model.LoadModelJson(os.path.join(
                resources.RESOURCES_DIRECTORY, "v2/NeptuneHappinessSanta/neptune_m_model_c031.json"))

        # fps
        self.startTimer(int(1000 / 60))
        self.timersInit()
        self.talkWidgetInit()
        self.talk_function()

    def resizeGL(self, w: int, h: int) -> None:
        # 使模型的参数按窗口大小进行更新
        if self.model:
            self.model.Resize(w, h)

    def paintGL(self) -> None:
        live2d.clearBuffer()

        self.model.Update()

        self.model.Draw()

        if not self.read:
            self.savePng('screenshot.png')
            self.read = True

    def savePng(self, fName):
        data = gl.glReadPixels(0, 0, self.width(), self.height(), gl.GL_RGBA, gl.GL_UNSIGNED_BYTE)
        data = np.frombuffer(data, dtype=np.uint8).reshape(self.height(), self.width(), 4)
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

    def timerEvent(self, a0: QTimerEvent | None) -> None:
        if not self.isVisible():
            return

        auto_blink_param = self.config.getboolean('Settings', 'auto_blink')
        self.model.SetAutoBlinkEnable(auto_blink_param)
        auto_breath_param = self.config.getboolean('Settings', 'auto_breath')
        self.model.SetAutoBreathEnable(auto_breath_param)

        if self.idle_anim:
            self.model.StartRandomMotion("Idle", live2d.MotionPriority.IDLE, onFinishMotionHandler=callback)
            if self.t_count <= self.sleep_v:
                self.idle_anim = True
            else:
                self.idle_anim = False

        if self.transformMovie.currentFrameNumber() >= self.transformMovie.frameCount() - 3 and self.transform == True:
            self.transformLabel.movie().setScaledSize(QSize(int(1), int(1)))
            self.transformMovie.stop()
            self.transformLabel.close()
            self.transform_complete()

        if self.transformMovie.currentFrameNumber() >= self.transformMovie.frameCount() - 3 and self.transform == False:
            self.transformMovie.stop()
            self.transformLabel.close()
            self.input_lock = False
            if self.transform_text:
                self.text = "I'm Transformed"
                self.kaomoji = "(*~*)"
                self.textUpdate()
                self.transform_text = False

        if self.transformMovie.currentFrameNumber() >= self.transformMovie.frameCount() / 2 and self.transform == True:
            self.dialogClose()
            self.transform_text = True

        local_x, local_y = QCursor.pos().x() - self.x(), QCursor.pos().y() - self.y()

        # Mouse Triggers
        count = 0
        while True:
            saved_position = QCursor.pos().y()
            if count > 20 * 20:
                break
            current_position = QCursor.pos().y()
            if saved_position != current_position:
                if self.tracking_mouse_switch:
                    if self.mouse_tracking_log:
                        print("Mouse is moving", self.tracking_mouse, local_x, local_y)
                    if self.t_count >= self.sleep_v:
                        self.tracking_mouse = False
                        self.mouse_move = False
                    else:
                        self.tracking_mouse = True
                        self.mouse_move = True
            else:
                self.mouse_move = False
            count += 1

        # Tracking the mouse position
        if self.tracking_mouse:
            self.model.Drag(local_x, local_y)

        if self.isInL2DArea(local_x, local_y):
            self.isInLA = True
            self.clickInLA = True
            self.on_mouse_anim = True

            if self.t_count >= self.sleep_v:
                self.on_mouse_anim = False

            if self.on_mouse_anim and self.on_mouse_switch == True:
                self.model.StartRandomMotion("OnMouse", live2d.MotionPriority.NORMAL, onFinishMotionHandler=callback)
                self.on_mouse_anim = True

            if self.l2d_area_log:
                print("in l2d area")
        else:
            self.isInLA = False
            self.clickInLA = False
            if self.l2d_area_log:
                print("out of l2d area")
        self.update()

    def isInL2DArea(self, click_x, click_y):
        h = self.height()
        alpha = gl.glReadPixels(click_x * self.systemScale, (h - click_y) * self.systemScale, 1, 1, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE)[3]
        return alpha > 0

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton and not self.input_lock:
            x, y = event.scenePosition().x(), event.scenePosition().y()
            self.posX, self.posY = event.scenePosition().x(), event.scenePosition().y()
            if not self.clickInLA:
                self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowTransparentForInput)
                self.show()
                self.mouse_input_timer.start(5000)
            if self.isInL2DArea(x, y):
                self.clickInLA = True
                self.clickX, self.clickY = x, y
                if not self.sleep and self.input_lock == False:
                    self.talkDelayTimer.start(1500)
                    if self.character_name == "Purple Sister":
                        self.model.SetExpression("Smile")
                    if self.character_name == "Black Sister":
                        self.model.SetExpression("Smile")
                    else:
                        self.model.SetExpression("Funny")
                if self.sleep and self.input_lock == False:
                    self.model.SetExpression("Surprised")
                if self.mouse_click_log:
                    print("Left Button Pressed")

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and not self.input_lock:
            x, y = event.scenePosition().x(), event.scenePosition().y()
            self.posX, self.posY = event.scenePosition().x(), event.scenePosition().y()
            if self.isInLA:
                # self.model.Touch(x, y)
                self.clickInLA = False
                self.tap_body_anim = True
                if self.tap_body_switch:
                    self.model.StartRandomMotion("TapBody", live2d.MotionPriority.FORCE, onFinishMotionHandler=callback)
                    self.tap_body_anim = True
                    if not self.sleep and self.input_lock == False:
                        self.model.ResetExpression()
                        self.talkDelayTimer.stop()
                        expression = self.model.SetRandomExpression(fadeout=3500)
                        if self.placeThis:
                            self.placeThis = False
                            self.text = "Okay I'll stay here"
                            self.kaomoji = "(^~^)"
                        else:
                            if expression == "Normal":
                                self.text = "So What"
                                self.kaomoji = "(-_-)"
                            elif expression == "Happy":
                                self.text = "i'm Happy"
                                self.kaomoji = "(^_^)"
                            elif expression == "Angry":
                                self.text = "Don't touch me like that"
                                self.kaomoji = "(=_=)"
                            elif expression == "Sad":
                                self.text = "i'm Sad"
                                self.kaomoji = "(-_;)"
                            elif expression == "Smile":
                                self.text = "He He"
                                self.kaomoji = "(^~^)"
                            elif expression == "Tired":
                                self.text = "i'm Tired"
                                self.kaomoji = "(~o~)"
                            elif expression == "ClosedEyes":
                                self.text = "Hmm"
                                self.kaomoji = "(-_-)"
                            elif expression == "Cry":
                                self.text = "Whaah!"
                                self.kaomoji = "(T_T)"
                            elif expression == "Fear":
                                self.text = "Ugh"
                                self.kaomoji = "(:_:)"
                            elif expression == "Star":
                                self.text = "i'm Sooo Happy"
                                self.kaomoji = ";(^~^);"
                            elif expression == "Surprised":
                                self.text = "What?"
                                self.kaomoji = "(0_0)?"
                            elif expression == "Funny" and self.goodness_form == False:
                                self.text = "Yo!!!"
                                self.kaomoji = "(>_<)"
                            elif expression == "Funny" and self.goodness_form == True:
                                self.text = "I'm Godness"
                                self.kaomoji = "(@_@)"
                        print(self.character_name + ": " + self.text + self.kaomoji)
                        self.textUpdate()

                        self.t_count = 1
                if self.sleep and self.input_lock == False:
                    self.model.ResetExpression()
                    self.text = "You woke me up"
                    self.kaomoji = "(б~б)"
                    print(self.character_name + ": " + self.text + self.kaomoji)
                    self.textUpdate()
                    self.model.SetExpression("Fear", fadeout=10000)
                    self.t_count = 1
                    self.sleep = False
                if not self.tap_body_switch:
                    self.model.ResetExpression()
                    self.t_count = 1
                if self.mouse_click_log:
                    print("Left Button Released")

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        x, y = event.scenePosition().x(), event.scenePosition().y()
        if self.clickInLA and not self.input_lock:
            self.move(int(self.x() + x - self.clickX - 10), int(self.y() + y - self.clickY - 10))

    def setSettings(self, flags: Qt.WindowType) -> None:
        # print(f"setSettings flags: {flags}")
        self.setWindowFlags(flags)

        windowType = flags & Qt.WindowType.WindowType_Mask

        text = windowType.name

        for hintFlag in self.hintFlags:
            if flags & hintFlag:
                text += f"\n| Qt.{hintFlag.name}"


        if self.auto_scale and self.auto_scale_init:
            self.a_scale = auto_scale(self.sc_height_size)
            self.model_update()

        if not self.auto_scale and self.auto_scale_init:
            self.a_scale = 1
            self.model_update()

        self.auto_scale_init = True

    def model_update(self):
        # Update Params
        if self.character_name == "Neptune":
            self.character_name = "Neptune"
            self.models_switch = 0
            self.t_count = 1
            self.mx_param = 600
            self.my_param = 600
            self.w_correction = -70
            self.h_correction = 0

        if self.character_name == "Purple Heart":
            self.character_name = "Purple Heart"
            self.models_switch = 1
            self.t_count = 1
            self.mx_param = 700
            self.my_param = 700
            self.w_correction = -70
            self.h_correction = 0  # -15

        if self.character_name == "Noire":
            self.character_name = "Noire"
            self.models_switch = 2
            self.t_count = 1
            self.mx_param = 700
            self.my_param = 700
            self.w_correction = -70
            self.h_correction = 0  # -15

        if self.character_name == "Black Heart":
            self.character_name = "Black Heart"
            self.models_switch = 3
            self.t_count = 1
            self.mx_param = 700
            self.my_param = 700
            self.w_correction = -70
            self.h_correction = 0  # -25

        if self.character_name == "Blanc":
            self.character_name = "Blanc"
            self.models_switch = 4
            self.t_count = 1
            self.mx_param = 600
            self.my_param = 600
            self.w_correction = -70
            self.h_correction = 0

        if self.character_name == "White Heart":
            self.character_name = "White Heart"
            self.models_switch = 5
            self.t_count = 1
            self.mx_param = 700
            self.my_param = 700
            self.w_correction = -70
            self.h_correction = 0  # -10

        if self.character_name == "Vert":
            self.character_name = "Vert"
            self.models_switch = 6
            self.t_count = 1
            self.mx_param = 700
            self.my_param = 700
            self.w_correction = -70
            self.h_correction = 0  # -20

        if self.character_name == "Green Heart":
            self.character_name = "Green Heart"
            self.models_switch = 7
            self.t_count = 1
            self.mx_param = 700
            self.my_param = 700
            self.w_correction = -70
            self.h_correction = 0  # -40

        if self.character_name == "NepGear":
            self.character_name = "NepGear"
            self.models_switch = 8
            self.t_count = 1
            self.mx_param = 600
            self.my_param = 600
            self.w_correction = -70
            self.h_correction = 0

        if self.character_name == "Purple Sister":
            self.character_name = "Purple Sister"
            self.models_switch = 9
            self.t_count = 1
            self.mx_param = 650
            self.my_param = 650
            self.w_correction = -70
            self.h_correction = 0

        if self.character_name == "Uni":
            self.character_name = "Uni"
            self.models_switch = 10
            self.t_count = 1
            self.mx_param = 600
            self.my_param = 600
            self.w_correction = -70
            self.h_correction = 0

        if self.character_name == "Black Sister":
            self.character_name = "Black Sister"
            self.models_switch = 11
            self.t_count = 1
            self.mx_param = 650
            self.my_param = 650
            self.w_correction = -70
            self.h_correction = 0
        # Update Size and Position
        self.resize(1, 1)
        self.w_resize = int(self.mx_param * self.a_scale * self.models_scale)
        self.h_resize = int(self.my_param * self.a_scale * self.models_scale)
        self.resize(int(self.w_resize), int(self.h_resize))
        self.frmX = (self.SrcSize.width() - self.width()) - self.w_correction
        self.frmY = (self.SrcSize.height() - self.height()) - self.h_correction
        self.move(int(self.frmX), int(self.frmY))

        # ReInitialize Model
        self.model: live2d.LAppModel | None = None
        self.model = live2d.LAppModel()
        if self.character_name == "Neptune":
            self.model.LoadModelJson(os.path.join(
                resources.RESOURCES_DIRECTORY, "v3/Neptune/Neptune.model3.json"))
        if self.character_name == "Purple Heart":
            self.model.LoadModelJson(os.path.join(
                resources.RESOURCES_DIRECTORY, "v3/PurpleHeart/PurpleHeart.model3.json"))
        if self.character_name == "Noire":
            self.model.LoadModelJson(os.path.join(
                resources.RESOURCES_DIRECTORY, "v3/Noire/Noire.model3.json"))
        if self.character_name == "Black Heart":
            self.model.LoadModelJson(os.path.join(
                resources.RESOURCES_DIRECTORY, "v3/BlackHeart/BlackHeart.model3.json"))
        if self.character_name == "Blanc":
            self.model.LoadModelJson(os.path.join(
                resources.RESOURCES_DIRECTORY, "v3/Blanc/Blanc.model3.json"))
        if self.character_name == "White Heart":
            self.model.LoadModelJson(os.path.join(
                resources.RESOURCES_DIRECTORY, "v3/WhiteHeart/WhiteHeart.model3.json"))
        if self.character_name == "Vert":
            self.model.LoadModelJson(os.path.join(
                resources.RESOURCES_DIRECTORY, "v3/Vert/Vert.model3.json"))
        if self.character_name == "Green Heart":
            self.model.LoadModelJson(os.path.join(
                resources.RESOURCES_DIRECTORY, "v3/GreenHeart/GreenHeart.model3.json"))
        if self.character_name == "NepGear":
            self.model.LoadModelJson(os.path.join(
                resources.RESOURCES_DIRECTORY, "v3/NepGear/NepGear.model3.json"))
        if self.character_name == "Purple Sister":
            self.model.LoadModelJson(os.path.join(
                resources.RESOURCES_DIRECTORY, "v3/PurpleSister/PurpleSister.model3.json"))
        if self.character_name == "Uni":
            self.model.LoadModelJson(os.path.join(
                resources.RESOURCES_DIRECTORY, "v3/Uni/Uni.model3.json"))
        if self.character_name == "Black Sister":
            self.model.LoadModelJson(os.path.join(
                resources.RESOURCES_DIRECTORY, "v3/BlackSister/BlackSister.model3.json"))
        self.resizeGL(int(self.w_resize), int(self.h_resize))
        # Save Config
        models_config(self.models_switch, self.character_name, self.mx_param, self.my_param, self.w_resize,
                      self.h_resize, self.w_correction, self.h_correction)
        # live2d Update
        live2d.clearBuffer()
        self.model.Update()
        if self.talkUpd:
            self.talkWidgetUpdate()

    # Context Menu
    def contextMenuEvent(self, e):
        context_menu = QMenu(self).addMenu('&File')

        # Window Submenu
        submenu_window = QMenu(self).addMenu(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/window.svg")), '&Window')
        action_minimize = submenu_window.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/window_min.svg")), '&Minimize')
        action_minimize.triggered.connect(self.on_action_minimize)
        action_normal = submenu_window.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/window_restore.svg")), '&Normal')
        action_normal.triggered.connect(self.on_action_normal)
        context_menu.addMenu(submenu_window)
        context_menu.addSeparator()

        # Transform Action
        transform_action = QAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/transform.svg")), '&Transform', self)
        if not self.input_lock:
            transform_action.triggered.connect(self.on_action_transform)
        context_menu.addAction(transform_action)
        context_menu.addSeparator()

        # Character Submenu
        submenu_character = QMenu(self).addMenu(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/character.svg")), '&Characters')
        # Neptune
        action_neptune = submenu_character.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/neptune.ico")), '&Neptune')
        if not self.input_lock:
            action_neptune.triggered.connect(self.on_action_neptune)
        # Purple Heart
        action_purple_heart = submenu_character.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/purple_heart.ico")), '&Purple Heart')
        if not self.input_lock:
            action_purple_heart.triggered.connect(self.on_action_purple_heart)
        # Noire
        action_noire = submenu_character.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/noire.ico")), '&Noire')
        if not self.input_lock:
            action_noire.triggered.connect(self.on_action_noire)
        # Black Heart
        action_black_heart = submenu_character.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/black_heart.ico")), '&Black Heart')
        if not self.input_lock:
            action_black_heart.triggered.connect(self.on_action_black_heart)
        # Blanc
        action_blanc = submenu_character.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/blanc.ico")), '&Blanc')
        if not self.input_lock:
            action_blanc.triggered.connect(self.on_action_blanc)
        # White Heart
        action_white_heart = submenu_character.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/white_heart.ico")), '&White Heart')
        if not self.input_lock:
            action_white_heart.triggered.connect(self.on_action_white_heart)
        # Vert
        action_vert = submenu_character.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/vert.ico")), '&Vert')
        if not self.input_lock:
            action_vert.triggered.connect(self.on_action_vert)
        # Green Heart
        action_green_heart = submenu_character.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/green_heart.ico")), '&Green Heart')
        if not self.input_lock:
            action_green_heart.triggered.connect(self.on_action_green_heart)
        # NepGear
        action_nepgear = submenu_character.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/nepgear.ico")), '&NepGear')
        if not self.input_lock:
            action_nepgear.triggered.connect(self.on_action_nepgear)
        # Purple Sister
        action_purple_sister = submenu_character.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/purple_sister.ico")), '&Purple Sister')
        if not self.input_lock:
            action_purple_sister.triggered.connect(self.on_action_purple_sister)
        # Uni
        action_uni = submenu_character.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/uni.ico")), '&Uni')
        if not self.input_lock:
            action_uni.triggered.connect(self.on_action_uni)
        # Black Sister
        action_black_sister = submenu_character.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/black_sister.ico")), '&Black Sister')
        if not self.input_lock:
            action_black_sister.triggered.connect(self.on_action_black_sister)

        context_menu.addMenu(submenu_character)

        # Animations Submenu
        submenu_animations = QMenu(self).addMenu(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/animation.svg")), '&Animations')

        # Idle Animation CheckBox
        action_checked_idle = submenu_animations.addAction('Idle Animation')
        action_checked_idle.setCheckable(True)
        action_checked_idle.setChecked(self.idle_switch)
        if action_checked_idle.isChecked():
            action_checked_idle.triggered.connect(self.on_action_idle_false)
        else:
            action_checked_idle.triggered.connect(self.on_action_idle_true)

        # OnMouse Animation CheckBox
        action_checked_on_mouse = submenu_animations.addAction('OnMouse Animation')
        action_checked_on_mouse.setCheckable(True)
        action_checked_on_mouse.setChecked(self.on_mouse_switch)
        if action_checked_on_mouse.isChecked():
            action_checked_on_mouse.triggered.connect(self.on_action_on_mouse_false)
        else:
            action_checked_on_mouse.triggered.connect(self.on_action_on_mouse_true)

        # Tap Body Animation CheckBox
        action_checked_tap_body = submenu_animations.addAction('Tap Body Animation')
        action_checked_tap_body.setCheckable(True)
        action_checked_tap_body.setChecked(self.tap_body_switch)
        if action_checked_tap_body.isChecked():
            action_checked_tap_body.triggered.connect(self.on_action_tap_body_false)
        else:
            action_checked_tap_body.triggered.connect(self.on_action_tap_body_true)

        # Stop All Motions
        submenu_animations.addSeparator()
        action_stop_all_motions = submenu_animations.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/stop.svg")), '&Stop All Motions')
        action_stop_all_motions.triggered.connect(self.on_action_stop_all_motions)

        context_menu.addMenu(submenu_animations)
        context_menu.addSeparator()

        # Settings Action
        settings_action = QAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/settings.svg")), '&Settings', self)
        if not self.input_lock:
            settings_action.triggered.connect(self.on_action_settings)
        context_menu.addAction(settings_action)
        context_menu.addSeparator()

        # About Action
        about_action = QAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/about.svg")), '&About', self)
        about_action.triggered.connect(self.on_action_about)
        context_menu.addAction(about_action)

        # Exit Action
        exit_action = QAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/exit.svg")), '&Quit', self)
        exit_action.triggered.connect(self.on_action_quit)
        context_menu.addAction(exit_action)

        context_menu.exec(e.globalPos())

    # Windows Actions
    def on_action_normal(self):
        self.showNormal()

    def on_action_minimize(self):
        self.showMinimized()

    def on_action_maximize(self):
        self.showMaximized()

    # Context Menu Actions
    def on_action_transform(self):
        if self.can_transform:
            self.transform_initialize()
            self.t_count = 1
            self.text = "I'm Transform"
            self.kaomoji = "(*_~)"
            settings.close()
            self.textUpdate()
        if not self.can_transform:
            self.model.SetExpression("Sad", fadeout=10000)
            self.text = "I'm Can't Transform"
            self.kaomoji = "(T_T)"
            print(self.character_name + ": " + self.text + self.kaomoji)
            self.textUpdate()

    # Characters Actions
    def on_action_neptune(self):
        self.goodness_form = False
        self.can_transform = True
        self.talkUpd = False
        if not self.transform:
            self.goodBye()
        self.character_name = "Neptune"
        self.models_switch = 0
        if self.transform:
            self.model_update()

    def on_action_purple_heart(self):
        self.goodness_form = True
        self.can_transform = True
        self.talkUpd = False
        if not self.transform:
            self.goodBye()
        self.character_name = "Purple Heart"
        self.models_switch = 1
        if self.transform:
            self.model_update()

    def on_action_noire(self):
        self.goodness_form = False
        self.can_transform = True
        self.talkUpd = False
        if not self.transform:
            self.goodBye()
        self.character_name = "Noire"
        self.models_switch = 2
        if self.transform:
            self.model_update()

    def on_action_black_heart(self):
        self.goodness_form = True
        self.can_transform = True
        self.talkUpd = False
        if not self.transform:
            self.goodBye()
        self.character_name = "Black Heart"
        self.models_switch = 3
        if self.transform:
            self.model_update()

    def on_action_blanc(self):
        self.goodness_form = False
        self.can_transform = True
        self.talkUpd = False
        if not self.transform:
            self.goodBye()
        self.character_name = "Blanc"
        self.models_switch = 4
        if self.transform:
            self.model_update()

    def on_action_white_heart(self):
        self.goodness_form = True
        self.can_transform = True
        self.talkUpd = False
        if not self.transform:
            self.goodBye()
        self.character_name = "White Heart"
        self.models_switch = 5
        if self.transform:
            self.model_update()

    def on_action_vert(self):
        self.goodness_form = False
        self.can_transform = True
        self.talkUpd = False
        if not self.transform:
            self.goodBye()
        self.character_name = "Vert"
        self.models_switch = 6
        if self.transform:
            self.model_update()

    def on_action_green_heart(self):
        self.goodness_form = True
        self.can_transform = True
        self.talkUpd = False
        if not self.transform:
            self.goodBye()
        self.character_name = "Green Heart"
        self.models_switch = 7
        if self.transform:
            self.model_update()

    def on_action_nepgear(self):
        self.goodness_form = False
        self.can_transform = True
        self.talkUpd = False
        if not self.transform:
            self.goodBye()
        self.character_name = "NepGear"
        self.models_switch = 8
        if self.transform:
            self.model_update()

    def on_action_purple_sister(self):
        self.goodness_form = True
        self.can_transform = True
        self.talkUpd = False
        if not self.transform:
            self.goodBye()
        self.character_name = "Purple Sister"
        self.models_switch = 9
        if self.transform:
            self.model_update()

    def on_action_uni(self):
        self.goodness_form = False
        self.can_transform = True
        self.talkUpd = False
        if not self.transform:
            self.goodBye()
        self.character_name = "Uni"
        self.models_switch = 10
        if self.transform:
            self.model_update()

    def on_action_black_sister(self):
        self.goodness_form = True
        self.can_transform = True
        self.talkUpd = False
        if not self.transform:
            self.goodBye()
        self.character_name = "Black Sister"
        self.models_switch = 11
        if self.transform:
            self.model_update()

    # Animations Actions
    def on_action_idle_true(self):
        # QMessageBox.information(self, "Message", f"Idle Animation: Enable")
        self.text = "You have enabled the Idle Animation"
        self.kaomoji = "(@_@)"
        print(self.character_name + ": " + self.text + self.kaomoji)
        self.textUpdate()
        self.config.set('Animations', 'idle_animation', 'True')
        with open('config.ini', 'w') as cfg:
            cfg: [str, int, tuple, object]
            self.config.write(cfg)
        self.idle_switch = True
        self.idle_anim = True

    def on_action_idle_false(self):
        # QMessageBox.information(self, "Message", f"Idle Animation: Disable")
        self.text = "You have disabled the Idle Animation"
        self.kaomoji = "(@_@)"
        print(self.character_name + ": " + self.text + self.kaomoji)
        self.textUpdate()
        self.config.set('Animations', 'idle_animation', 'False')
        with open('config.ini', 'w') as cfg:
            cfg: [str, int, tuple, object]
            self.config.write(cfg)
        self.idle_switch = False
        self.idle_anim = False

    def on_action_on_mouse_true(self):
        # QMessageBox.information(self, "Message", f"OnMouse Animation: Enable")
        self.text = "You have enabled the OnMouse Animation"
        self.kaomoji = "(@_@)"
        print(self.character_name + ": " + self.text + self.kaomoji)
        self.textUpdate()
        self.config.set('Animations', 'on_mouse_animation', 'True')
        with open('config.ini', 'w') as cfg:
            cfg: [str, int, tuple, object]
            self.config.write(cfg)
        self.on_mouse_switch = True
        self.on_mouse_anim = True

    def on_action_on_mouse_false(self):
        # QMessageBox.information(self, "Message", f"OnMouse Animation: Disable")
        self.text = "You have disabled the OnMouse Animation"
        self.kaomoji = "(@_@)"
        print(self.character_name + ": " + self.text + self.kaomoji)
        self.textUpdate()
        self.config.set('Animations', 'on_mouse_animation', 'False')
        with open('config.ini', 'w') as cfg:
            cfg: [str, int, tuple, object]
            self.config.write(cfg)
        self.on_mouse_switch = False
        self.on_mouse_anim = False

    def on_action_tap_body_true(self):
        # QMessageBox.information(self, "Message", f"Tap Body Animation: Enable")
        self.text = "You have enabled the TapBody Animation"
        self.kaomoji = "(@_@)"
        print(self.character_name + ": " + self.text + self.kaomoji)
        self.textUpdate()
        self.config.set('Animations', 'tap_body_animation', 'True')
        with open('config.ini', 'w') as cfg:
            cfg: [str, int, tuple, object]
            self.config.write(cfg)
        self.tap_body_switch = True
        self.tap_body_anim = True

    def on_action_tap_body_false(self):
        # QMessageBox.information(self, "Message", f"Tap Body Animation: Disable")
        self.text = "You have disabled the TapBody Animation"
        self.kaomoji = "(@_@)"
        print(self.character_name + ": " + self.text + self.kaomoji)
        self.textUpdate()
        self.config.set('Animations', 'tap_body_animation', 'False')
        with open('config.ini', 'w') as cfg:
            cfg: [str, int, tuple, object]
            self.config.write(cfg)
        self.tap_body_switch = False
        self.tap_body_anim = False

    def on_action_stop_all_motions(self):
        self.text = "You stop all motions"
        self.kaomoji = "(@_@)"
        print(self.character_name + ": " + self.text + self.kaomoji)
        self.textUpdate()
        self.model.StopAllMotions()

    # Settings Actions
    def on_action_settings(self):
        settings.show()

    def on_action_about(self):
        QMessageBox.information(self, "About Me", "My Little Neptune\n"
                                                  "\nThe assistant application on your desktop,"
                                                  "\nwhich pleases you with its appearance every day:)\n"
                                                  "\nDeveloper: Neptune NoiSe"
                                                  "\n(https://github.com/NeptuneNoiSe)\n"
                                                  "\nThe application is based on:"
                                                  "\nPython 3.12"
                                                  "\nPySide6"
                                                  "\nlive2d-py by Arkueid (https://github.com/Arkueid/live2d-py)"
                                                  "\nCompile Heart / Idea Factory Live2D Models\n\n"
                                                  "\n© 2025")

    def on_action_quit(self):
        self.model.SetExpression("Cry")
        answer = QMessageBox.question(self,
                                      'Quit',
                                      self.character_name + ": " + "Do you really want to leave? T_T",
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                      QMessageBox.StandardButton.No)
        if answer == QMessageBox.StandardButton.Yes:
            print(self.character_name + ":", "GoodBye (^3^)")
            self.quitTimer.start(3000)
            self.text = "GoodBye! See you again!"
            self.kaomoji = "(^3^)"
            print(self.character_name + ": " + self.text + self.kaomoji)
            self.textUpdate()

        else:
            self.t_count = 1
            self.model.ResetExpression()
            self.model.SetExpression("Happy",5000)
            self.text = "I'm Sooo Happy!"
            self.kaomoji = ":(^~^):"
            print(self.character_name + ": " + self.text + self.kaomoji)
            self.textUpdate()

    def closeEvent(self, event):
        self.model.SetExpression("Cry")
        settings.close()
        answer = QMessageBox.question(self,
                                      'Quit',
                                      self.character_name + ": " + "Do you really want to leave? T_T",
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                      QMessageBox.StandardButton.No)
        if answer == QMessageBox.StandardButton.Yes:
            event.accept()
            print(self.character_name + ":", "GoodBye (^3^)")
        else:
            self.t_count = 1
            self.model.ResetExpression()
            self.model.SetExpression("Happy", 5000)
            self.text = "I'm Sooo Happy!"
            self.kaomoji = ":(^~^):"
            print(self.character_name + ": " + self.text + self.kaomoji)
            self.textUpdate()
            event.ignore()

class SettingsWindow(QWidget):
    def __init__(self, pythonic_window_registration: bool = False):
        super().__init__()
        self.config = config_main
        self.getWindowFlag_FramelessWindowHint = self.config.getboolean('WindowFlags', 'FramelessWindowHint')
        self.getWindowFlag_WindowMinimizeButtonHint = self.config.getboolean('WindowFlags', 'WindowMinimizeButtonHint')
        self.getWindowFlag_WindowCloseButtonHint = self.config.getboolean('WindowFlags', 'WindowCloseButtonHint')
        self.getWindowFlag_WindowStaysOnTopHint = self.config.getboolean('WindowFlags', 'WindowStaysOnTopHint')
        self.getWindowFlag_WindowStaysOnBottomHint = self.config.getboolean('WindowFlags', 'WindowStaysOnBottomHint')
        self.getWindowFlag_WindowTransparentForInput = self.config.getboolean('WindowFlags', 'WindowTransparentForInput')
        self.getWindowFlag_WindowType_Mask = self.config.getboolean('WindowFlags', 'WindowType_Mask')

        self.auto_scale = self.config.getboolean('Scale', 'auto_scale')
        self.models_scale = self.config.getfloat('Scale', 'models_scale')
        self.auto_blink = self.config.getboolean('Settings', 'auto_blink')
        self.auto_breath = self.config.getboolean('Settings', 'auto_breath')
        self.tracking_mouse = self.config.getboolean('Settings', 'tracking_mouse')
        self.sleep = self.config.getboolean('Settings', 'sleep')

        self.pythonic_reg = pythonic_window_registration
        self.mainWindow = Win()

        self.createHintsGroupBox()
        self.createScaleGroupBox()
        self.createOtherGroupBox()

        # Windows Flags Control
        self.framelessWindowCheckBox.setChecked(self.getWindowFlag_FramelessWindowHint)
        self.windowStaysOnTopCheckBox.setChecked(self.getWindowFlag_WindowStaysOnTopHint)
        self.windowStaysOnBottomCheckBox.setChecked(self.getWindowFlag_WindowStaysOnBottomHint)

        # Settings Control
        self.autoScaleCheckBox.setChecked(self.auto_scale)
        self.autoBlinkCheckBox.setChecked(self.auto_blink)
        self.autoBreathCheckBox.setChecked(self.auto_breath)
        self.trackingMouseCheckBox.setChecked(self.tracking_mouse)
        self.sleepCheckBox.setChecked(self.sleep)

        quitButton = QPushButton("&Force Quit")
        quitButton.clicked.connect(qApp.quit) # type: ignore[name-defined,attr-defined] # pylint: disable=undefined-variable

        bottomLayout = QHBoxLayout()
        bottomLayout.addStretch()
        bottomLayout.addWidget(quitButton)

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.hintsGroupBox)
        mainLayout.addWidget(self.scaleGroupBox)
        mainLayout.addWidget(self.otherGroupBox)

        mainLayout.addLayout(bottomLayout)
        self.setLayout(mainLayout)
        self.setWindowTitle("Settings")
        self.mainWindow.setWindowTitle("My Little Neptune")
        self.mainWindow.setWindowIcon(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/nep_main.ico")))
        self.updateMainWindow()

    @Slot()
    def updateMainWindow(self) -> None:
        flags = Qt.WindowType()
        if self.getWindowFlag_WindowMinimizeButtonHint:
            flags = flags | Qt.WindowType.WindowMinimizeButtonHint

        if self.getWindowFlag_WindowCloseButtonHint:
            flags = flags | Qt.WindowType.WindowCloseButtonHint

        if self.getWindowFlag_WindowTransparentForInput:
            flags = flags | Qt.WindowType.WindowTransparentForInput

        if self.getWindowFlag_WindowType_Mask:
            flags = flags | Qt.WindowType.WindowType_Mask

        if self.pythonic_reg:
            for checkBox, flag in self.hintFlagWidgets:
                if checkBox.isChecked():
                    flags = flags | flag
        else:
            if self.framelessWindowCheckBox.isChecked():
                flags = flags | Qt.WindowType.FramelessWindowHint
                self.config.set('WindowFlags', 'FramelessWindowHint', 'True')
                self.framelessWindowCheckBox.setChecked(True)
            else:
                self.config.set('WindowFlags', 'FramelessWindowHint', 'False')
                self.framelessWindowCheckBox.setChecked(False)

            if self.windowStaysOnTopCheckBox.isChecked():
                flags = flags | Qt.WindowType.WindowStaysOnTopHint
                self.config.set('WindowFlags', 'WindowStaysOnTopHint', 'True')
                self.windowStaysOnTopCheckBox.setChecked(True)
                self.config.set('WindowFlags', 'WindowStaysOnBottomHint', 'False')
                self.windowStaysOnBottomCheckBox.setChecked(False)
            else:
                self.config.set('WindowFlags', 'WindowStaysOnTopHint', 'False')
                self.windowStaysOnTopCheckBox.setChecked(False)
                self.config.set('WindowFlags', 'WindowStaysOnBottomHint', 'True')
                self.windowStaysOnBottomCheckBox.setChecked(True)

            if self.windowStaysOnBottomCheckBox.isChecked():
                flags = flags | Qt.WindowType.WindowStaysOnBottomHint
                self.config.set('WindowFlags', 'WindowStaysOnBottomHint', 'True')
                self.windowStaysOnBottomCheckBox.setChecked(True)
                self.config.set('WindowFlags', 'WindowStaysOnTopHint', 'False')
                self.windowStaysOnTopCheckBox.setChecked(False)
            else:
                self.config.set('WindowFlags', 'WindowStaysOnBottomHint', 'False')
                self.windowStaysOnBottomCheckBox.setChecked(False)
                self.config.set('WindowFlags', 'WindowStaysOnTopHint', 'True')
                self.windowStaysOnTopCheckBox.setChecked(True)

            if self.autoScaleCheckBox.isChecked():
                self.config.set('Scale', 'auto_scale', 'True')
                self.autoScaleCheckBox.setChecked(True)
                self.modelScaleBox.setReadOnly(True)
                self.mainWindow.auto_scale = True
                self.mainWindow.models_scale = 1
                self.modelScaleBox.setValue(1)
                self.config.set('Scale', 'models_scale', '1')
            else:
                self.config.set('Scale', 'auto_scale', 'False')
                self.autoScaleCheckBox.setChecked(False)
                self.modelScaleBox.setReadOnly(False)
                self.mainWindow.auto_scale = False
                scale_value = self.modelScaleBox.value()
                self.mainWindow.models_scale = scale_value
                self.config.set('Scale', 'models_scale', str(scale_value))

            if self.autoBlinkCheckBox.isChecked():
                self.config.set('Settings', 'auto_blink', 'True')
                self.autoBlinkCheckBox.setChecked(True)
            else:
                self.config.set('Settings', 'auto_blink', 'False')
                self.autoBlinkCheckBox.setChecked(False)

            if self.autoBreathCheckBox.isChecked():
                self.config.set('Settings', 'auto_breath', 'True')
                self.autoBreathCheckBox.setChecked(True)
            else:
                self.config.set('Settings', 'auto_breath', 'False')
                self.autoBreathCheckBox.setChecked(False)

            if self.trackingMouseCheckBox.isChecked():
                self.config.set('Settings', 'tracking_mouse', 'True')
                self.trackingMouseCheckBox.setChecked(True)
                self.mainWindow.tracking_mouse_switch = True
            else:
                self.config.set('Settings', 'tracking_mouse', 'False')
                self.trackingMouseCheckBox.setChecked(False)
                self.mainWindow.tracking_mouse_switch = False

            if self.sleepCheckBox.isChecked():
                self.config.set('Settings', 'sleep', 'True')
                self.sleepCheckBox.setChecked(True)
                self.mainWindow.sleep_switch = True
            else:
                self.config.set('Settings', 'sleep', 'False')
                self.sleepCheckBox.setChecked(False)
                self.mainWindow.sleep_switch = False

        with open('config.ini', 'w') as cfg:
            cfg: [str, int, tuple, object]
            self.config.write(cfg)

        self.mainWindow.setSettings(flags)
        self.mainWindow.show()

    def createHintsGroupBox(self) -> None:
        self.hintsGroupBox = QGroupBox("Window")
        layout = QGridLayout()

        if self.pythonic_reg:
            self.hintFlagWidgets: list[tuple[QCheckBox, Qt.WindowType]] = [
                (self.createCheckBox(flag.name), flag) for flag in
                self.mainWindow.hintFlags
            ]

            for i, (checkBox, _) in enumerate(self.hintFlagWidgets):
                layout.addWidget(checkBox, i%3, int(i/3))

            self.typeFlagWidgets[0][0].setChecked(True)
        else:
            self.framelessWindowCheckBox = self.createCheckBox("Frameless window")
            self.windowStaysOnTopCheckBox = self.createCheckBox("Window stays on top")
            self.windowStaysOnBottomCheckBox = self.createCheckBox("Window stays on bottom")

            layout.addWidget(self.framelessWindowCheckBox, 0, 0)
            layout.addWidget(self.windowStaysOnTopCheckBox, 1, 0)
            layout.addWidget(self.windowStaysOnBottomCheckBox, 2, 0)
        self.hintsGroupBox.setLayout(layout)

    def createScaleGroupBox(self) -> None:
        self.scaleGroupBox = QGroupBox("Scale")
        layout = QGridLayout()
        self.modelFlagWidgets = QCheckBox()
        self.modelScaleBox = QDoubleSpinBox()
        self.text = QLabel("Scale multiplier:")
        self.modelScaleBox.setMinimum(0.1)
        self.modelScaleBox.setMaximum(10)
        self.modelScaleBox.setSingleStep(0.5)
        self.modelScaleBox.setValue(self.models_scale)

        self.modelFlagWidgets.setChecked(True)

        self.autoScaleCheckBox = self.createCheckBox("AutoScale")

        layout.addWidget(self.autoScaleCheckBox)
        layout.addWidget(self.text)
        layout.addWidget(self.modelScaleBox)

        self.modelFlagWidgets.clicked.connect(self.updateMainWindow)
        self.modelScaleBox.valueChanged.connect(self.updateMainWindow)

        self.scaleGroupBox.setLayout(layout)

    def createOtherGroupBox(self) -> None:
        self.otherGroupBox = QGroupBox("Other")
        layout = QGridLayout()
        self.otherFlagWidgets = QCheckBox()
        self.otherFlagWidgets.setChecked(True)
        self.autoBlinkCheckBox = self.createCheckBox("Auto Blink")
        self.autoBreathCheckBox = self.createCheckBox("Auto Breath")
        self.trackingMouseCheckBox = self.createCheckBox("Tracking Mouse Position")
        self.sleepCheckBox = self.createCheckBox("Sleep")

        self.autoBlinkCheckBox.setIcon(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/eye_closed.svg")))
        self.autoBreathCheckBox.setIcon(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/breath.svg")))
        self.trackingMouseCheckBox.setIcon(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/mouse.svg")))
        self.sleepCheckBox.setIcon(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/sleep.svg")))

        layout.addWidget(self.autoBlinkCheckBox)
        layout.addWidget(self.autoBreathCheckBox)
        layout.addWidget(self.trackingMouseCheckBox)
        layout.addWidget(self.sleepCheckBox)

        self.otherFlagWidgets.clicked.connect(self.updateMainWindow)
        self.otherGroupBox.setLayout(layout)

    def createCheckBox(self, text: str) -> QCheckBox:
        checkBox = QCheckBox(text)
        checkBox.clicked.connect(self.updateMainWindow) # type: ignore[attr-defined]
        return checkBox

if __name__ == "__main__":
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pythonic", action='store_true',
                        help="Create and register widgets pythonically.")
    args = parser.parse_args()

    live2d.init()
    format = QSurfaceFormat.defaultFormat()
    format.setSwapInterval(0)
    QSurfaceFormat.setDefaultFormat(format)

    app = QApplication(sys.argv)
    win = Win()

    settings = SettingsWindow(args.pythonic)
    settings.setWindowIcon(QIcon(os.path.join(
        resources.RESOURCES_DIRECTORY, "icons/settings.svg")))
    app.exec()

    live2d.dispose()
