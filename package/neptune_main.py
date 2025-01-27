import os
import OpenGL.GL as gl
import numpy as np
from PIL import Image
from PySide6.QtCore import QTimerEvent, Qt, QTimer, QEvent
from PySide6.QtGui import QMouseEvent, QCursor, QScreen, QSurfaceFormat, QAction, QIcon
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QApplication, QMenu, QMessageBox
from PySide6.QtGui import QGuiApplication

import live2d.v3 as live2d
from live2d.utils.lipsync import WavHandler
from live2d.v3 import StandardParams
#import live2d.v2 as live2d
import resources

motion_end_log = False

def callback():
    if motion_end_log:
        print("motion end")

class Win(QOpenGLWidget):
    def __init__(self) -> None:
        super().__init__()
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
        self.models_switch = 0
            # Neptune = 0
            # Purple Heart = 1
            # Noire = 2
            # Black Heart = 3
            # Blanc = 4
            # White Heart = 5

        # AutoScale: If True, the models is scaled based on the screen size
        self.auto_scale = True

        # Models Scale
        self.models_scale = 1

        # Tracking the mouse position
        self.tracking_mouse = True

        # Init Vars
        self.w_correction = 0
        self.h_correction = 0
        self.a_scale = 1
        self.mouse_move = False
        self.mouse_timer = None
        self.isInLA = False
        self.clickInLA = False
        self.click = False
        self.a = 0
        self.test = False
        self.read = False
        self.clickX = -1
        self.clickY = -1
        self.posX = -1
        self.posY = -1
        self.model: live2d.LAppModel | None = None
        self.systemScale = QGuiApplication.primaryScreen().devicePixelRatio()
        self.sc_height_size = self.screen().size().height() * self.screen().devicePixelRatio()
        self.sc_width_size = self.screen().size().width() * self.screen().devicePixelRatio()
        self.SrcSize = QScreen.availableGeometry(QApplication.primaryScreen())

        # Screens Size for AutoScale
        if self.auto_scale:
            if self.sc_height_size == 120:
                self.a_scale = 0.111
            if self.sc_height_size == 160:
                self.a_scale = 0.148
            if self.sc_height_size == 192:
                self.a_scale = 0.178
            if self.sc_height_size == 240:
                self.a_scale = 0.222
            if self.sc_height_size == 272:
                self.a_scale = 0.252
            if self.sc_height_size == 320:
                self.a_scale = 0.296
            if self.sc_height_size == 360:
                self.a_scale = 0.333
            if self.sc_height_size == 384:
                self.a_scale = 0.355
            if self.sc_height_size == 480:
                self.a_scale = 0.444
            if self.sc_height_size == 540:
                self.a_scale = 0.5
            if self.sc_height_size == 576:
                self.a_scale = 0.533
            if self.sc_height_size == 600:
                self.a_scale = 0.555
            if self.sc_height_size == 640:
                self.a_scale = 0.592
            if self.sc_height_size == 720:
                self.a_scale = 0.666
            if self.sc_height_size == 768:
                self.a_scale = 0.711
            if self.sc_height_size == 800:
                self.a_scale = 0.741
            if self.sc_height_size == 810:
                self.a_scale = 0.75
            if self.sc_height_size == 864:
                self.a_scale = 0.8
            if self.sc_height_size == 900:
                self.a_scale = 0.833
            if self.sc_height_size == 960:
                self.a_scale = 0.888
            if self.sc_height_size == 1024:
                self.a_scale = 0.948
            if self.sc_height_size == 1050:
                self.a_scale = 0.972
            if self.sc_height_size == 1080:
                self.a_scale = 1
            if self.sc_height_size == 1152:
                self.a_scale = 1.066
            if self.sc_height_size == 1200:
                self.a_scale = 1.111
            if self.sc_height_size == 1280:
                self.a_scale = 1.185
            if self.sc_height_size == 1350:
                self.a_scale = 1.25
            if self.sc_height_size == 1440:
                self.a_scale = 1.333
            if self.sc_height_size == 1536:
                self.a_scale = 1.422
            if self.sc_height_size == 1600:
                self.a_scale = 1.481
            if self.sc_height_size == 1620:
                self.a_scale = 1.5
            if self.sc_height_size == 1800:
                self.a_scale = 1.666
            if self.sc_height_size == 2048:
                self.a_scale = 1.896
            if self.sc_height_size == 2160:
                self.a_scale = 2
            if self.sc_height_size == 2400:
                self.a_scale = 2.222
            if self.sc_height_size == 2560:
                self.a_scale = 2.370
            if self.sc_height_size == 2880:
                self.a_scale = 2.666
            if self.sc_height_size == 3072:
                self.a_scale = 2.844
            if self.sc_height_size == 3200:
                self.a_scale = 2.963
            if self.sc_height_size == 3240:
                self.a_scale = 3
            if self.sc_height_size == 3384:
                self.a_scale = 3.133
            if self.sc_height_size == 4096:
                self.a_scale = 3.793
            if self.sc_height_size == 4320:
                self.a_scale = 4
            if self.sc_height_size == 4800:
                self.a_scale = 4.444
            if self.sc_height_size == 8640:
                self.a_scale = 8

        # Character Name
        self.character_name = None

        # Models switch parameters
        if self.models_switch == 0:
            self.character_name = "Neptune"
            self.w_resize = 350 * self.a_scale * self.models_scale
            self.h_resize = 600 * self.a_scale * self.models_scale
            self.w_correction = 10
            self.h_correction = 0
        elif self.models_switch == 1:
            self.character_name = "Purple Heart"
            self.w_resize = 800 * self.a_scale * self.models_scale
            self.h_resize = 720 * self.a_scale * self.models_scale
            self.w_correction = -125
            self.h_correction = 0
        elif self.models_switch == 2:
            self.character_name = "Noire"
            self.w_resize = 420 * self.a_scale * self.models_scale
            self.h_resize = 700 * self.a_scale * self.models_scale
            self.w_correction = 10
            self.h_correction = 0
        elif self.models_switch == 3:
            self.character_name = "Black Heart"
            self.w_resize = 430 * self.a_scale * self.models_scale
            self.h_resize = 700 * self.a_scale * self.models_scale
            self.w_correction = 10
            self.h_correction = 0
        elif self.models_switch == 4:
            self.character_name = "Blanc"
            self.w_resize = 440 * self.a_scale * self.models_scale
            self.h_resize = 600 * self.a_scale * self.models_scale
            self.w_correction = 10
            self.h_correction = 0
        elif self.models_switch == 5:
            self.character_name = "White Heart"
            self.w_resize = 390 * self.a_scale * self.models_scale
            self.h_resize = 650 * self.a_scale * self.models_scale
            self.w_correction = 10
            self.h_correction = 0

        self.setWindowFlags(self.windowFlags()
                            | Qt.WindowType.X11BypassWindowManagerHint
                            | Qt.WindowType.FramelessWindowHint
                            #| Qt.WindowType.WindowTransparentForInput
                            | Qt.WindowType.WindowType_Mask
                            | Qt.WindowType.WindowStaysOnTopHint)

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
        self.idle_switch = True
        self.on_mouse_switch = True
        self.tap_body_switch = True
        self.sleep_switch = True
        self.tracking_mouse_switch = True

        # Model Resize
        self.resize(int(self.w_resize), int(self.h_resize))

        # Center on Axis X
        self.frmX = (self.SrcSize.width() - self.width()) - self.w_correction
        # Center on Axis Y
        self.frmY = (self.SrcSize.height() - self.height()) - self.h_correction
        # Move window
        self.move(int(self.frmX), int(self.frmY))

        # Init idle timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.idle_timer)
        self.timer.start(int(6000 / self.time_scale))

        # Mouse tracking timer
        self.mouse_t = QTimer()
        self.mouse_t.timeout.connect(self.mouse_tracking)
        if not self.mouse_move:
            self.tracking_mouse = False
            self.mouse_t.start(10000)

    def mouse_tracking(self):
        self.tracking_mouse = False
        if self.posX <= 0 or self.posY <= 0:
            self.posX = 0 + self.frmX * 0.15
            self.posY = 0 + self.h_resize * 0.25

        if self.mouse_tracking_log:
            print("Mouse is steady", self.tracking_mouse, self.posX,self.posY)
        self.model.Drag(self.posX,self.posY)

    def idle_timer(self):
        # Timer Diagnostic Log
        if self.timer_log:
            print(self.t_count, "-", self.condition, "Condition")
        self.t_count += 1
        if self.t_count <= self.sad_v:
            self.condition = "Idle"
        if self.t_count <=self.sleep_v and self.idle_switch == True:
            self.idle_anim = True
        if self.t_count >=10 and self.sleep_switch == False:
            self.t_count = 1
        if self.t_count == self.sad_v:
            self.condition = "Sad"
            self.model.SetExpression("Sad")
            print(self.character_name + ":", "I'm Sad")
        if self.t_count == self.tired_v and self.sleep_switch == True:
            self.condition = "Tired"
            self.model.SetExpression("Tired")
            print(self.character_name + ":", "I'm Tired")
        if self.t_count == self.sleep_v and self.sleep_switch == True:
            self.condition = "Sleep"
            self.model.SetExpression("ClosedEyes")
            if self.tracking_mouse_switch:
                self.tracking_mouse = False
            self.idle_anim = False
            self.sleep = True
            print(self.character_name + ":", "I'm Sleep")
        if self.t_count == self.wake_up_v and self.sleep_switch == True:
            self.model.ResetExpression()
            self.model.SetExpression("Star", fadeout=10000)
            self.model.SetExpression("Serious", fadeout=10000)
            self.t_count = 0
            self.idle_anim = True
            print(self.character_name + ":", "I'm WakeUp")

    def initializeGL(self) -> None:
        self.makeCurrent()

        if live2d.LIVE2D_VERSION == 3:
            live2d.glewInit()

        self.model = live2d.LAppModel()

        if live2d.LIVE2D_VERSION == 3:
            if self.models_switch == 0:
                print(self.character_name + ":", "Hello! (^~^)/")
                self.model.LoadModelJson(os.path.join(
                    resources.RESOURCES_DIRECTORY, "v3/Neptune/Neptune.model3.json"))

            elif self.models_switch == 1:
                print(self.character_name + ":", "Hello! (^~^)/")
                self.model.LoadModelJson(os.path.join(
                    resources.RESOURCES_DIRECTORY, "v3/PurpleHeart/PurpleHeart.model3.json"))

            elif self.models_switch == 2:
                print(self.character_name + ":", "Hello! (^~^)/")
                self.model.LoadModelJson(os.path.join(
                    resources.RESOURCES_DIRECTORY, "v3/Noire/Noire.model3.json"))

            elif self.models_switch == 3:
                print(self.character_name + ":", "Hello! (^~^)/")
                self.model.LoadModelJson(os.path.join(
                    resources.RESOURCES_DIRECTORY, "v3/BlackHeart/BlackHeart.model3.json"))

            elif self.models_switch == 4:
                print(self.character_name + ":", "Hello! (^~^)/")
                self.model.LoadModelJson(os.path.join(
                    resources.RESOURCES_DIRECTORY, "v3/Blanc/Blanc.model3.json"))

            elif self.models_switch == 5:
                print(self.character_name + ":", "Hello! (^~^)/")
                self.model.LoadModelJson(os.path.join(
                    resources.RESOURCES_DIRECTORY, "v3/WhiteHeart/WhiteHeart.model3.json"))

        else:
            self.model.LoadModelJson(os.path.join(
                resources.RESOURCES_DIRECTORY, "v2/NeptuneHappinessSanta/neptune_m_model_c031.json"))

        # fps = 30
        self.startTimer(int(1000 / 30))

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

        if self.idle_anim:
            self.model.StartRandomMotion("Idle", live2d.MotionPriority.IDLE, onFinishMotionHandler=callback)
            self.idle_anim = False

        if self.on_mouse_anim and self.on_mouse_switch == True:
            self.model.StartRandomMotion("OnMouse", live2d.MotionPriority.NORMAL, onFinishMotionHandler=callback)
            self.on_mouse_anim = False

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
        if event.button() == Qt.LeftButton:
            x, y = event.scenePosition().x(), event.scenePosition().y()
            self.posX, self.posY = event.scenePosition().x(), event.scenePosition().y()
            if self.isInL2DArea(x, y):
                self.clickInLA = True
                self.clickX, self.clickY = x, y
                if not self.sleep:  # False
                    self.model.SetExpression("Funny")
                if self.sleep:  # True
                    self.model.SetExpression("Surprised")
                if self.mouse_click_log:
                    print("Left Button Pressed")

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            x, y = event.scenePosition().x(), event.scenePosition().y()
            self.posX, self.posY = event.scenePosition().x(), event.scenePosition().y()
            if self.isInLA:
                self.model.Touch(x, y)
                self.clickInLA = False
                self.tap_body_anim = True
                if self.tap_body_switch:
                    self.model.StartRandomMotion("TapBody", live2d.MotionPriority.FORCE, onFinishMotionHandler=callback)
                    self.tap_body_anim = False
                    if not self.sleep:
                        self.model.ResetExpression()
                        self.model.SetRandomExpression(fadeout=3500)
                        self.t_count = 1
                if self.sleep:
                    self.model.ResetExpression()
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
        if self.clickInLA:
            self.move(int(self.x() + x - self.clickX), int(self.y() + y - self.clickY))

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
        action_maximize = submenu_window.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/window_max.svg")), '&Maximize')
        action_maximize.triggered.connect(self.on_action_maximize)
        context_menu.addMenu(submenu_window)
        context_menu.addSeparator()

        # Character Submenu
        submenu_character = QMenu(self).addMenu(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/character.svg")), '&Characters')
        # Neptune
        action_neptune = submenu_character.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/character.svg")), '&Neptune')
        action_neptune.triggered.connect(self.on_action_neptune)
        # Purple Heart
        action_purple_heart = submenu_character.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/character.svg")), '&Purple Heart')
        action_purple_heart.triggered.connect(self.on_action_purple_heart)
        # Noire
        action_noire = submenu_character.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/character.svg")), '&Noire')
        action_noire.triggered.connect(self.on_action_noire)
        # Black Heart
        action_black_heart = submenu_character.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/character.svg")), '&Black Heart')
        action_black_heart.triggered.connect(self.on_action_black_heart)
        # Blanc
        action_blanc = submenu_character.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/character.svg")), '&Blanc')
        action_blanc.triggered.connect(self.on_action_blanc)
        # White Heart
        action_white_heart = submenu_character.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/character.svg")), '&White Heart')
        action_white_heart.triggered.connect(self.on_action_white_heart)
        context_menu.addMenu(submenu_character)

        # Animations Submenu
        submenu_animations = QMenu(self).addMenu(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/animation.svg")), '&Animations')

        # Idle Animation Submenu
        submenu_idle = QMenu(self).addMenu(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/idle_w.svg")), '&Idle Animation')
        submenu_animations.addMenu(submenu_idle)
        action_idle_true = submenu_idle.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/check.svg")), '&Enable')
        action_idle_true.triggered.connect(self.on_action_idle_true)
        action_idle_false = submenu_idle.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/cross.svg")), '&Disable')
        action_idle_false.triggered.connect(self.on_action_idle_false)

        # On Mouse Animation Submenu
        submenu_on_mouse = QMenu(self).addMenu(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/pointer.svg")), '&On Mouse Animation')
        submenu_animations.addMenu(submenu_on_mouse)
        action_on_mouse_true = submenu_on_mouse.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/check.svg")), '&Enable')
        action_on_mouse_true.triggered.connect(self.on_action_on_mouse_true)
        action_on_mouse_false = submenu_on_mouse.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/cross.svg")), '&Disable')
        action_on_mouse_false.triggered.connect(self.on_action_on_mouse_false)

        # Tap Body Animation Submenu
        submenu_tap_body = QMenu(self).addMenu(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/tap.svg")), '&Tap Body Animation')
        submenu_animations.addMenu(submenu_tap_body)
        action_tap_body_true = submenu_tap_body.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/check.svg")), '&Enable')
        action_tap_body_true.triggered.connect(self.on_action_tap_body_true)
        action_tap_body_false = submenu_tap_body.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/cross.svg")), '&Disable')
        action_tap_body_false.triggered.connect(self.on_action_tap_body_false)

        # Stop All Motions
        submenu_animations.addSeparator()
        action_stop_all_motions = submenu_animations.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/stop.svg")), '&Stop All Motions')
        action_stop_all_motions.triggered.connect(self.on_action_stop_all_motions)

        context_menu.addMenu(submenu_animations)
        context_menu.addSeparator()

        # Settings Submenu
        submenu_settings = QMenu(self).addMenu(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/settings.svg")), '&Settings')

        # Auto Blink Submenu
        submenu_auto_blink = QMenu(self).addMenu(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/eye_closed.svg")), '&Auto Blink')
        submenu_settings.addMenu(submenu_auto_blink)
        action_auto_blink_true = submenu_auto_blink.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/check.svg")), '&Enable')
        action_auto_blink_true.triggered.connect(self.on_action_auto_blink_true)
        action_auto_blink_false = submenu_auto_blink.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/cross.svg")), '&Disable')
        action_auto_blink_false.triggered.connect(self.on_action_auto_blink_false)

        # Auto Breath Submenu
        submenu_auto_breath = QMenu(self).addMenu(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/breath.svg")), '&Auto Breath')
        submenu_settings.addMenu(submenu_auto_breath)
        action_auto_breath_true = submenu_auto_breath.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/check.svg")), '&Enable')
        action_auto_breath_true.triggered.connect(self.on_action_auto_breath_true)
        action_auto_breath_false = submenu_auto_breath.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/cross.svg")), '&Disable')
        action_auto_breath_false.triggered.connect(self.on_action_auto_breath_false)

        # Tracking Mouse Submenu
        submenu_tracking_mouse = QMenu(self).addMenu(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/mouse.svg")), '&Tracking Mouse Position')
        submenu_settings.addMenu(submenu_tracking_mouse)
        action_tracking_mouse_true = submenu_tracking_mouse.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/check.svg")), '&Enable')
        action_tracking_mouse_true.triggered.connect(self.on_action_tracking_mouse_true)
        action_tracking_mouse_false = submenu_tracking_mouse.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/cross.svg")), '&Disable')
        action_tracking_mouse_false.triggered.connect(self.on_action_tracking_mouse_false)

        # Sleep Submenu
        submenu_sleep = QMenu(self).addMenu(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/sleep.svg")), '&Sleep')
        submenu_settings.addMenu(submenu_sleep)
        action_sleep_true = submenu_sleep.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/check.svg")), '&Enable')
        action_sleep_true.triggered.connect(self.on_action_sleep_true)
        action_sleep_false = submenu_sleep.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/cross.svg")), '&Disable')
        action_sleep_false.triggered.connect(self.on_action_sleep_false)

        context_menu.addMenu(submenu_settings)
        context_menu.addSeparator()

        # About Action
        about_action = QAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/about.svg")), '&About', self)
        about_action.triggered.connect(self.on_action_about)
        context_menu.addAction(about_action)
        #context_menu.addSeparator()

        # Exit Action
        exit_action = QAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/exit.svg")), '&Exit', self)
        exit_action.triggered.connect(self.on_action_quit)
        context_menu.addAction(exit_action)

        context_menu.exec(e.globalPos())

    # Context Menu Actions
    # Windows Actions
    def on_action_normal(self):
        self.showNormal()

    def on_action_minimize(self):
        self.showMinimized()

    def on_action_maximize(self):
        self.showMaximized()

    # Characters Actions
    def on_action_neptune(self):
        print(self.character_name + ":", "GoodBye (^3^)")
        self.resize(1, 1)
        self.character_name = "Neptune"
        self.models_switch = 0
        self.t_count = 1
        self.w_resize = 350 * self.a_scale * self.models_scale
        self.h_resize = 600 * self.a_scale * self.models_scale
        self.w_correction = 10
        self.h_correction = 0
        self.resize(int(self.w_resize), int(self.h_resize))
        self.frmX = (self.SrcSize.width() - self.width()) - self.w_correction
        self.frmY = (self.SrcSize.height() - self.height()) - self.h_correction
        self.move(int(self.frmX), int(self.frmY))
        self.model: live2d.LAppModel | None = None
        self.model = live2d.LAppModel()
        self.model.LoadModelJson(os.path.join(
            resources.RESOURCES_DIRECTORY, "v3/Neptune/Neptune.model3.json"))
        self.resizeGL(int(self.w_resize),int(self.h_resize))
        live2d.clearBuffer()
        self.model.Update()
        print(self.character_name + ":", "Hello! (^~^)/")

    def on_action_purple_heart(self):
        print(self.character_name + ":", "GoodBye (^3^)")
        self.resize(1, 1)
        self.character_name = "Purple Heart"
        self.models_switch = 1
        self.t_count = 1
        self.w_resize = 800 * self.a_scale * self.models_scale
        self.h_resize = 720 * self.a_scale * self.models_scale
        self.w_correction = -125
        self.h_correction = 0
        self.resize(int(self.w_resize), int(self.h_resize))
        self.frmX = (self.SrcSize.width() - self.width()) - self.w_correction
        self.frmY = (self.SrcSize.height() - self.height()) - self.h_correction
        self.move(int(self.frmX), int(self.frmY))
        self.model: live2d.LAppModel | None = None
        self.model = live2d.LAppModel()
        self.model.LoadModelJson(os.path.join(
            resources.RESOURCES_DIRECTORY, "v3/PurpleHeart/PurpleHeart.model3.json"))
        self.resizeGL(int(self.w_resize),int(self.h_resize))
        live2d.clearBuffer()
        self.model.Update()
        print(self.character_name + ":", "Hello! (^~^)/")

    def on_action_noire(self):
        print(self.character_name + ":", "GoodBye (^3^)")
        self.resize(1, 1)
        self.character_name = "Noire"
        self.models_switch = 2
        self.t_count = 1
        self.w_resize = 420 * self.a_scale * self.models_scale
        self.h_resize = 700 * self.a_scale * self.models_scale
        self.w_correction = 10
        self.h_correction = 0
        self.resize(int(self.w_resize), int(self.h_resize))
        self.frmX = (self.SrcSize.width() - self.width()) - self.w_correction
        self.frmY = (self.SrcSize.height() - self.height()) - self.h_correction
        self.move(int(self.frmX), int(self.frmY))
        self.model: live2d.LAppModel | None = None
        self.model = live2d.LAppModel()
        self.model.LoadModelJson(os.path.join(
            resources.RESOURCES_DIRECTORY, "v3/Noire/Noire.model3.json"))
        self.resizeGL(int(self.w_resize),int(self.h_resize))
        live2d.clearBuffer()
        self.model.Update()
        print(self.character_name + ":", "Hello! (^~^)/")

    def on_action_black_heart(self):
        print(self.character_name + ":", "GoodBye (^3^)")
        self.resize(1, 1)
        self.character_name = "Black Heart"
        self.models_switch = 3
        self.t_count = 1
        self.w_resize = 430 * self.a_scale * self.models_scale
        self.h_resize = 700 * self.a_scale * self.models_scale
        self.w_correction = 10
        self.h_correction = 0
        self.resize(int(self.w_resize), int(self.h_resize))
        self.frmX = (self.SrcSize.width() - self.width()) - self.w_correction
        self.frmY = (self.SrcSize.height() - self.height()) - self.h_correction
        self.move(int(self.frmX), int(self.frmY))
        self.model: live2d.LAppModel | None = None
        self.model = live2d.LAppModel()
        self.model.LoadModelJson(os.path.join(
            resources.RESOURCES_DIRECTORY, "v3/BlackHeart/BlackHeart.model3.json"))
        self.resizeGL(int(self.w_resize),int(self.h_resize))
        live2d.clearBuffer()
        self.model.Update()
        print(self.character_name + ":", "Hello! (^~^)/")

    def on_action_blanc(self):
        print(self.character_name + ":", "GoodBye (^3^)")
        self.resize(1, 1)
        self.character_name = "Blanc"
        self.models_switch = 4
        self.t_count = 1
        self.w_resize = 440 * self.a_scale * self.models_scale
        self.h_resize = 600 * self.a_scale * self.models_scale
        self.w_correction = 10
        self.h_correction = 0
        self.resize(int(self.w_resize), int(self.h_resize))
        self.frmX = (self.SrcSize.width() - self.width()) - self.w_correction
        self.frmY = (self.SrcSize.height() - self.height()) - self.h_correction
        self.move(int(self.frmX), int(self.frmY))
        self.model: live2d.LAppModel | None = None
        self.model = live2d.LAppModel()
        self.model.LoadModelJson(os.path.join(
            resources.RESOURCES_DIRECTORY, "v3/Blanc/Blanc.model3.json"))
        self.resizeGL(int(self.w_resize),int(self.h_resize))
        live2d.clearBuffer()
        self.model.Update()
        print(self.character_name + ":", "Hello! (^~^)/")

    def on_action_white_heart(self):
        print(self.character_name + ":", "GoodBye (^3^)")
        self.resize(1, 1)
        self.character_name = "White Heart"
        self.models_switch = 5
        self.t_count = 1
        self.w_resize = 390 * self.a_scale * self.models_scale
        self.h_resize = 650 * self.a_scale * self.models_scale
        self.w_correction = 10
        self.h_correction = 0
        self.resize(int(self.w_resize), int(self.h_resize))
        self.frmX = (self.SrcSize.width() - self.width()) - self.w_correction
        self.frmY = (self.SrcSize.height() - self.height()) - self.h_correction
        self.move(int(self.frmX), int(self.frmY))
        self.model: live2d.LAppModel | None = None
        self.model = live2d.LAppModel()
        self.model.LoadModelJson(os.path.join(
            resources.RESOURCES_DIRECTORY, "v3/WhiteHeart/WhiteHeart.model3.json"))
        self.resizeGL(int(self.w_resize),int(self.h_resize))
        live2d.clearBuffer()
        self.model.Update()
        print(self.character_name + ":", "Hello! (^~^)/")

    # Animations Actions
    def on_action_idle_true(self):
        self.idle_switch = True
        self.idle_anim = True

    def on_action_idle_false(self):
        self.idle_switch = False
        self.idle_anim = False

    def on_action_on_mouse_true(self):
        self.on_mouse_switch = True
        self.on_mouse_anim = True

    def on_action_on_mouse_false(self):
        self.on_mouse_switch = False
        self.on_mouse_anim = False

    def on_action_tap_body_true(self):
        self.tap_body_switch = True
        self.tap_body_anim = True

    def on_action_tap_body_false(self):
        self.tap_body_switch = False
        self.tap_body_anim = False

    def on_action_stop_all_motions(self):
        self.model.StopAllMotions()

    # Settings Actions
    def on_action_auto_blink_true(self):
        self.model.SetAutoBlinkEnable(True)

    def on_action_auto_blink_false(self):
        self.model.SetAutoBlinkEnable(False)

    def on_action_auto_breath_true(self):
        self.model.SetAutoBreathEnable(True)

    def on_action_auto_breath_false(self):
        self.model.SetAutoBreathEnable(False)

    def on_action_tracking_mouse_true(self):
        self.tracking_mouse_switch = True

    def on_action_tracking_mouse_false(self):
        self.tracking_mouse_switch = False

    def on_action_sleep_true(self):
        self.sleep_switch = True
        self.t_count = 1

    def on_action_sleep_false(self):
        self.sleep_switch = False
        self.sleep = False
        self.t_count = 1

    def on_action_about(self):
        QMessageBox.information(self, "About Me", "My Little Neptune\n"
                                                  "\nThe assistant application on your desktop,"
                                                  "\nwhich pleases you with its appearance every day:)\n"
                                                  "\nDeveloper: Neptune NoiSe"
                                                  "\n(https://github.com/NeptuneNoiSe)\n"
                                                  "\nThe application is based on:"
                                                  "\nPython 3.12.0"
                                                  "\nPySide6"
                                                  "\nlive2d-py by Arkueid (https://github.com/Arkueid/live2d-py)"
                                                  "\nCompile Heart / Idea Factory Live2D Models\n\n"
                                                  "\n© 2025")

    def on_action_quit(self):
        print(self.character_name + ":", "GoodBye (^3^)")
        exit(0)

if __name__ == "__main__":
    import sys

    live2d.init()
    format = QSurfaceFormat.defaultFormat()
    format.setSwapInterval(0)
    QSurfaceFormat.setDefaultFormat(format)

    app = QApplication(sys.argv)
    win = Win()
    win.setWindowTitle("My Little Neptune")
    win.setWindowIcon(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/Chell_Logo")))

    win.show()
    app.exec()

    live2d.dispose()