import os
import argparse
import OpenGL.GL as gl
import numpy as np
from PIL import Image
from PySide6 import QtCore
from PySide6.QtCore import QTimerEvent, Qt, QSize, Slot
from PySide6.QtGui import QMouseEvent, QCursor, QScreen, QSurfaceFormat, QAction, QIcon, QMovie
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QApplication, QMenu, QMessageBox, QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, \
    QGroupBox, QGridLayout, QCheckBox, QDoubleSpinBox, QComboBox
from PySide6.QtGui import QGuiApplication

import live2d.v3 as live2d
# from live2d.v3 import StandardParams
# from live2d.utils.lipsync import WavHandler
# import live2d.v2 as live2d
import resources
import json
from widgets.talk_widget import TalkWidgetMain
from additional.config_module import *
from additional.callbacks import *
from additional.models import Models
from additional.on_actions import OnActions
from additional.functions import Functions

class Win(QOpenGLWidget, Functions, Models, OnActions, TalkWidgetMain):
    def __init__(self) -> None:
        super().__init__()
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

        # Language:
        self.language = self.config.get('Main', 'language')

        # Models Switch:
        self.models_switch = self.config.getint('Model', 'selected_model')

        # AutoScale: If True, the models is scaled based on the screen size
        self.auto_scale = self.config.getboolean('Scale', 'auto_scale')

        # Models Scale
        self.models_scale = self.config.getfloat('Scale', 'models_scale')

        # Tracking the mouse position
        self.tracking_mouse = True

        # Sleep Animation Time Scale
        self.time_scale = 1

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
        self.set_icon = False
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
        self.screenSide = "Right"
        self.modelRotate = 0
        self.sleepMoveY = 0
        self.talk = True
        self.talkUpd = True
        self.placeThis = False
        self.sleepMove = False
        self.expression = None
        self.model: live2d.LAppModel | None = None
        self.app = QApplication.instance()
        self.systemScale = QGuiApplication.primaryScreen().devicePixelRatio()
        self.sc_height_size = self.screen().size().height() * self.screen().devicePixelRatio()
        self.sc_width_size = self.screen().size().width() * self.screen().devicePixelRatio()
        self.SrcSize = QScreen.availableGeometry(QApplication.primaryScreen())
        self.vSize = QScreen.availableVirtualGeometry(QApplication.primaryScreen())

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
            self.twmX = int(85 * self.a_scale * self.models_scale)
            self.twmY = int(-15 * self.a_scale * self.models_scale)
            self.config.set('Model', 'w_resize', str(self.w_res))
            self.config.set('Model', 'h_resize', str(self.h_res))
            self.config.set('Model', 'w_correction', '-70')
            self.config.set('Model', 'h_correction', '0')
            self.config.set('Model', 'twmX', str(self.twmX))
            self.config.set('Model', 'twmY', str(self.twmY))
            with open('config.ini', 'w') as cfg:
                cfg: [str, int, tuple, object]
                self.config.write(cfg)

        # Model Resize
        self.w_resize = self.config.getint('Model', 'w_resize')
        self.h_resize = self.config.getint('Model', 'h_resize')
        self.w_correction = self.config.getfloat('Model', 'w_correction')
        self.h_correction = self.config.getfloat('Model', 'h_correction')
        self.twmX = self.config.getfloat('Model', 'twmX')
        self.twmY = self.config.getfloat('Model', 'twmY')

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
        self.wake_up = False
        self.t_count = 1
        self.sad_v = 60
        self.tired_v = 80
        self.sleep_v = 100
        self.wake_up_v = 160

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

        self.en = os.path.join(
            resources.RESOURCES_DIRECTORY, "lang/en.json")
        self.ru = os.path.join(
            resources.RESOURCES_DIRECTORY, "lang/ru.json")

    def lang_set(self):
        if self.language == "English":
            with open(self.en, 'r',encoding='utf-8') as file:
                self.lang = json.load(file)
        elif self.language == "Russian":
            with open(self.ru, 'r',encoding='utf-8') as file:
                self.lang = json.load(file)

    def initializeGL(self) -> None:
        self.makeCurrent()
        live2d.glInit()
        self.model = live2d.LAppModel()
        if live2d.LIVE2D_VERSION == 3:
            self.text = self.lang['hello']
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

            elif self.models_switch == 12:
                self.goodness_form = False
                self.can_transform = True
                print(self.character_name + ": " + self.text + self.kaomoji)
                self.model.LoadModelJson(os.path.join(
                    resources.RESOURCES_DIRECTORY, "v3/Rom/Rom.model3.json"))

            elif self.models_switch == 13:
                self.goodness_form = True
                self.can_transform = True
                print(self.character_name + ": " + self.text + self.kaomoji)
                self.model.LoadModelJson(os.path.join(
                    resources.RESOURCES_DIRECTORY, "v3/WhiteSisterRom/WhiteSisterRom.model3.json"))

            elif self.models_switch == 14:
                self.goodness_form = False
                self.can_transform = False
                print(self.character_name + ": " + self.text + self.kaomoji)
                self.model.LoadModelJson(os.path.join(
                    resources.RESOURCES_DIRECTORY, "v3/Ram/Ram.model3.json"))

        else:
            self.model.LoadModelJson(os.path.join(
                resources.RESOURCES_DIRECTORY, "v2/NeptuneHappinessSanta/neptune_m_model_c031.json"))

        # fps
        self.startTimer(int(1000 / 60))
        self.timers_init()
        self.talkWidgetInit()
        self.talk_function()
        self.lang_set()

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

        if not self.set_icon:
            self.setWindowTitle("My Little Neptune")
            self.setWindowIcon(QIcon(os.path.join(
                resources.RESOURCES_DIRECTORY, "icons/nep_main.ico")))

        auto_blink_param = self.config.getboolean('Settings', 'auto_blink')
        self.model.SetAutoBlinkEnable(auto_blink_param)
        auto_breath_param = self.config.getboolean('Settings', 'auto_breath')
        self.model.SetAutoBreathEnable(auto_breath_param)

        local_x, local_y = QCursor.pos().x() - self.x(), QCursor.pos().y() - self.y()

        if self.idle_anim and self.idle_switch == True:
            self.model.StartRandomMotion("Idle", live2d.MotionPriority.IDLE, onFinishMotionHandler=idle_callback)
            if self.t_count <= self.sleep_v:
                self.idle_anim = True
            else:
                self.idle_anim = False

        self.transformMovieTriggers()

        self.changeTalkWidgetSide()

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
                self.model.StartRandomMotion("OnMouse", live2d.MotionPriority.NORMAL, onFinishMotionHandler=on_mouse_callback)
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
                # Get Model Params
                # self.getModelParams()
                self.clickInLA = True
                self.clickX, self.clickY = x, y
                if not self.sleep and self.input_lock == False:
                    self.talkDelayTimer.start(500)
                    if self.character_name == "Purple Sister":
                        self.model.SetExpression("Smile")
                    if self.character_name == "Black Sister":
                        self.model.SetExpression("Smile")
                    else:
                        self.model.SetExpression("Funny")
                if self.sleep and self.input_lock == False:
                    self.sleepInputTimer.start(500)
                    # self.model.SetExpression("Surprised")
                if self.mouse_click_log:
                    print("Left Button Pressed")

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and not self.input_lock:
            x, y = event.scenePosition().x(), event.scenePosition().y()
            self.posX, self.posY = event.scenePosition().x(), event.scenePosition().y()
            if self.isInLA:
                self.clickInLA = False
                self.tap_body_anim = True
                if self.tap_body_switch and self.sleepMove == False:
                    self.model.StartRandomMotion("TapBody", live2d.MotionPriority.FORCE, onFinishMotionHandler=tap_body_callback)
                    self.tap_body_anim = True
                    if not self.sleep and self.input_lock == False:
                        self.model.ResetExpression()
                        self.talkDelayTimer.stop()
                        self.expression = self.model.SetRandomExpression(fadeout=7000)
                        if self.placeThis:
                            self.placeThis = False
                            self.text = self.lang['stay']
                            self.kaomoji = "(^~^)"
                        else:
                            if self.expression == "Normal":
                                self.text = self.lang['normal']
                                self.kaomoji = "(o_o)"
                            elif self.expression == "Happy":
                                self.text = self.lang['happy']
                                self.kaomoji = "(^_^)"
                            elif self.expression == "Angry":
                                self.text = self.lang['angry']
                                self.kaomoji = "(⇀‸↼‶)"
                            elif self.expression == "Sad":
                                self.text = self.lang['sad']
                                self.kaomoji = "(´•ω•̥`)"
                            elif self.expression == "Smile":
                                self.text = self.lang['smile']
                                self.kaomoji = "(^~^)"
                            elif self.expression == "Tired":
                                self.text = self.lang['tired']
                                self.kaomoji = "(๑•﹏•)"
                            elif self.expression == "ClosedEyes":
                                self.text = self.lang['closed_eyes']
                                self.kaomoji = "(-_-)"
                            elif self.expression == "Cry":
                                self.text = self.lang['cry']
                                self.kaomoji = "(o;TωT)o"
                            elif self.expression == "Fear":
                                if self.character_name == "White Heart":
                                    self.text = self.lang['fear_wh']
                                    self.kaomoji = "(0﹏\‶)"
                                else:
                                    self.text = self.lang['fear']
                                    self.kaomoji = "(｡ŏ_ŏ)"
                            elif self.expression == "Star":
                                self.text = self.lang['star']
                                self.kaomoji = "(✩ω✩)"
                            elif self.expression == "Surprised":
                                self.text = self.lang['surprised']
                                self.kaomoji = "(0_0)?"
                            elif self.expression == "Funny" and self.goodness_form == False:
                                if self.character_name == "Blanc":
                                    self.text = self.lang['funny_bl']
                                    self.kaomoji = "(‶/﹏0)"
                                else:
                                    self.text = self.lang['funny']
                                    self.kaomoji = "(>_<)"
                            elif self.expression == "Funny" and self.goodness_form == True:
                                self.text = self.lang['funny_god']
                                self.kaomoji = "(◕‿◕)"
                        print(self.character_name + ": " + self.text + self.kaomoji)
                        self.textUpdate()
                        self.expression = None
                        self.t_count = 1
                if self.sleep and self.input_lock == False:
                    # self.model.SetExpression("Surprised")
                    self.sleepInputTimer.stop()
                    if not self.wake_up and self.sleepMove == False:
                        self.model.ResetExpression()
                        self.wake_up_func()
                        self.sleep = False
                        self.text = self.lang['woke']
                        self.kaomoji = "(⊙_⊙)✿"
                        print(self.character_name + ": " + self.text + self.kaomoji)
                        self.textUpdate()
                        self.model.SetExpression("Fear", fadeout=10000)
                        self.t_count = 1
                        self.sleep = False
                if not self.tap_body_switch and self.sleepMove == False:
                    self.model.ResetExpression()
                    self.t_count = 1
                self.sleepMove = False
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

        self.lang_set()

    def settings_close(self):
        settings.close()

    def settings_show(self):
        settings.show()

    # Context Menu
    def contextMenuEvent(self, e):
        context_menu = QMenu(self).addMenu('&File')

        # Window Submenu
        submenu_window = QMenu(self).addMenu(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/window.svg")), self.lang['a_window'])
        action_minimize = submenu_window.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/window_min.svg")), self.lang['a_minimize'])
        action_minimize.triggered.connect(self.on_action_minimize)
        action_normal = submenu_window.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/window_restore.svg")), self.lang['a_normal'])
        action_normal.triggered.connect(self.on_action_normal)
        context_menu.addMenu(submenu_window)
        context_menu.addSeparator()

        # Transform Action
        transform_action = QAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/transform.svg")), self.lang['a_transform'], self)
        if not self.input_lock:
            transform_action.triggered.connect(self.on_action_transform)
        context_menu.addAction(transform_action)
        context_menu.addSeparator()

        # Character Submenu
        submenu_character = QMenu(self).addMenu(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/character.svg")), self.lang['a_characters'])
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
        # Rom
        action_rom = submenu_character.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/rom.ico")), '&Rom')
        if not self.input_lock:
            action_rom.triggered.connect(self.on_action_rom)
        # White Sister Rom
        action_white_sister_rom = submenu_character.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/white_sister_rom.ico")), '&White Sister Rom')
        if not self.input_lock:
            action_white_sister_rom.triggered.connect(self.on_action_white_sister_rom)
        # Ram
        action_ram = submenu_character.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/ram.ico")), '&Ram')
        if not self.input_lock:
            action_ram.triggered.connect(self.on_action_ram)

        context_menu.addMenu(submenu_character)

        # Animations Submenu
        submenu_animations = QMenu(self).addMenu(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/animation.svg")), self.lang['a_animations'])

        # Idle Animation CheckBox
        action_checked_idle = submenu_animations.addAction(self.lang['a_idle'])
        action_checked_idle.setCheckable(True)
        action_checked_idle.setChecked(self.idle_switch)
        if action_checked_idle.isChecked():
            action_checked_idle.triggered.connect(self.on_action_idle_false)
        else:
            action_checked_idle.triggered.connect(self.on_action_idle_true)

        # OnMouse Animation CheckBox
        action_checked_on_mouse = submenu_animations.addAction(self.lang['a_on_mouse'])
        action_checked_on_mouse.setCheckable(True)
        action_checked_on_mouse.setChecked(self.on_mouse_switch)
        if action_checked_on_mouse.isChecked():
            action_checked_on_mouse.triggered.connect(self.on_action_on_mouse_false)
        else:
            action_checked_on_mouse.triggered.connect(self.on_action_on_mouse_true)

        # Tap Body Animation CheckBox
        action_checked_tap_body = submenu_animations.addAction(self.lang['a_tap_body'])
        action_checked_tap_body.setCheckable(True)
        action_checked_tap_body.setChecked(self.tap_body_switch)
        if action_checked_tap_body.isChecked():
            action_checked_tap_body.triggered.connect(self.on_action_tap_body_false)
        else:
            action_checked_tap_body.triggered.connect(self.on_action_tap_body_true)

        # Stop All Motions
        submenu_animations.addSeparator()
        action_stop_all_motions = submenu_animations.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/stop.svg")), self.lang['a_stop_motions'])
        action_stop_all_motions.triggered.connect(self.on_action_stop_all_motions)

        context_menu.addMenu(submenu_animations)
        context_menu.addSeparator()

        # Settings Action
        settings_action = QAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/settings.svg")), self.lang['a_settings'], self)
        if not self.input_lock:
            settings_action.triggered.connect(self.on_action_settings)
        context_menu.addAction(settings_action)
        context_menu.addSeparator()

        # About Action
        about_action = QAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/about.svg")), self.lang['a_about'], self)
        about_action.triggered.connect(self.on_action_about)
        context_menu.addAction(about_action)

        # Exit Action
        exit_action = QAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/exit.svg")), self.lang['a_quit'], self)
        exit_action.triggered.connect(self.on_action_quit)
        context_menu.addAction(exit_action)

        context_menu.exec(e.globalPos())

    def closeEvent(self, event):
        self.model.SetExpression("Cry")
        settings.close()
        if self.condition == "Sleep":
            self.wake_up_func()
        self.kaomoji = "(o;TωT)o"
        answer = QMessageBox.question(self,
                                      self.lang['a_quit_alt'],
                                      self.character_name + ": " + self.lang['quit'] + " " + self.kaomoji,
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                      QMessageBox.StandardButton.No)
        if answer == QMessageBox.StandardButton.Yes:
            event.accept()
            self.kaomoji = "(^3^)"
            print(self.character_name + ":", self.lang['goodbye'] + self.kaomoji)
        else:
            self.t_count = 1
            self.model.ResetExpression()
            self.model.SetExpression("Happy", 5000)
            self.text = self.lang['star']
            self.kaomoji = ":(^~^):"
            print(self.character_name + ": " + self.text + self.kaomoji)
            self.textUpdate()
            event.ignore()

class SettingsWindow(QWidget):
    def __init__(self, pythonic_window_registration: bool = False):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.config = config_main
        self.getWindowFlag_FramelessWindowHint = self.config.getboolean('WindowFlags', 'FramelessWindowHint')
        self.getWindowFlag_WindowMinimizeButtonHint = self.config.getboolean('WindowFlags', 'WindowMinimizeButtonHint')
        self.getWindowFlag_WindowCloseButtonHint = self.config.getboolean('WindowFlags', 'WindowCloseButtonHint')
        self.getWindowFlag_WindowStaysOnTopHint = self.config.getboolean('WindowFlags', 'WindowStaysOnTopHint')
        self.getWindowFlag_WindowStaysOnBottomHint = self.config.getboolean('WindowFlags', 'WindowStaysOnBottomHint')
        self.getWindowFlag_WindowTransparentForInput = self.config.getboolean('WindowFlags', 'WindowTransparentForInput')
        self.getWindowFlag_WindowType_Mask = self.config.getboolean('WindowFlags', 'WindowType_Mask')

        self.language = self.config.get('Main', 'language')
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

        # Settings Control
        self.autoScaleCheckBox.setChecked(self.auto_scale)
        self.autoBlinkCheckBox.setChecked(self.auto_blink)
        self.autoBreathCheckBox.setChecked(self.auto_breath)
        self.trackingMouseCheckBox.setChecked(self.tracking_mouse)
        self.sleepCheckBox.setChecked(self.sleep)

        quitButton = QPushButton("&App Quit")
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
            else:
                self.config.set('WindowFlags', 'WindowStaysOnTopHint', 'False')
                self.windowStaysOnTopCheckBox.setChecked(False)
                self.config.set('WindowFlags', 'WindowStaysOnBottomHint', 'True')

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

            language = self.langComboBox.currentText()
            self.config.set('Main', 'language', str(language))
            self.mainWindow.language = language

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
                layout.addWidget(checkBox, i%2, int(i/2))

            self.typeFlagWidgets[0][0].setChecked(True)
        else:
            self.framelessWindowCheckBox = self.createCheckBox("Frameless window")
            self.windowStaysOnTopCheckBox = self.createCheckBox("Window stays on top")
            self.langText = QLabel("Language:")
            self.langComboBox = QComboBox()
            self.langComboBox.addItems(["English", "Russian"])
            self.langComboBox.setCurrentText(self.language)

            layout.addWidget(self.framelessWindowCheckBox, 0, 0)
            layout.addWidget(self.windowStaysOnTopCheckBox, 1, 0)
            layout.addWidget(self.langText, 3, 0)
            layout.addWidget(self.langComboBox, 4, 0)
            self.langComboBox.currentTextChanged.connect(self.updateMainWindow)
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