import os
import OpenGL.GL as gl
import numpy as np
from PIL import Image
from PySide6.QtCore import QTimerEvent, Qt, QTimer
from PySide6.QtGui import QMouseEvent, QCursor, QScreen, QSurfaceFormat
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QGuiApplication

import live2d.v3 as live2d
from live2d.utils.lipsync import WavHandler
from live2d.v3 import StandardParams
#import live2d.v2 as live2d
import resources

def callback():
    print("motion end")

class Win(QOpenGLWidget):
    def __init__(self) -> None:
        super().__init__()
        # Models Switch:
        self.models_switch = 0
            # Neptune = 0
            # Purple Heart = 1
            # Noire = 2

        # AutoScale: If True, the models is scaled based on the screen size
        self.auto_scale = True

        # Models Scale
        self.models_scale = 1

        # Init Vars
        self.w_correction = 0
        self.h_correction = 0
        self.a_scale = 1
        self.isInLA = False
        self.clickInLA = False
        self.click = False
        self.a = 0
        self.read = False
        self.clickX = -1
        self.clickY = -1
        self.model: live2d.LAppModel | None = None
        self.systemScale = QGuiApplication.primaryScreen().devicePixelRatio()
        self.sc_height_size = self.screen().size().height() * self.screen().devicePixelRatio()
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

        # Models switch parameters
        if self.models_switch == 0:
            # Neptune
            self.w_resize = 350 * self.a_scale * self.models_scale
            self.h_resize = 600 * self.a_scale * self.models_scale
        elif self.models_switch == 1:
            # Purple Heart
            self.w_resize = 700 * self.a_scale * self.models_scale
            self.h_resize = 650 * self.a_scale * self.models_scale
        elif self.models_switch == 2:
            # Noire
            self.w_resize = 470 * self.a_scale * self.models_scale
            self.h_resize = 660 * self.a_scale * self.models_scale

        self.setWindowFlags(self.windowFlags()
                            | Qt.WindowType.X11BypassWindowManagerHint
                            | Qt.WindowType.FramelessWindowHint
                            #| Qt.WindowType.WindowTransparentForInput
                            | Qt.WindowType.WindowStaysOnTopHint
                            | Qt.WindowType.WindowType_Mask)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.wavHandler = WavHandler()
        self.lipSyncN = 2.5
        self.audioPlayed = False

        # Animation Vars
        self.tired = 1
        self.sleep = False

        # Tired Animation Time Scale
        self.time_scale = 1

        # Init Animation
        self.idle_anim = True
        self.on_mouse_anim = False
        self.tap_body_anim = False

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

        # Fadeout timer
        self.fadeout_t = QTimer()
        self.fadeout_t.timeout.connect(self.reset_expression)

    def reset_expression(self):
        print("Reset Expression")
        self.fadeout_t.stop()
        self.model.ResetExpression()

    def idle_timer(self):
        self.tired += 1
        if self.tired <=60:
            self.idle_anim = True
        print(self.tired)
        if self.tired == 30:
            self.model.SetExpression("Sad")
            print("I'm Sad")
        if self.tired == 40:
            self.model.SetExpression("Bitterness")
            print("I'm Tired")
        if self.tired == 60:
            self.model.SetExpression("CloseEyes")
            self.idle_anim = False
            self.sleep = True
            print("I'm Sleep")
        if self.tired == 120:
            self.model.ResetExpression()
            self.model.SetExpression("Star", fadeout=10000)
            self.model.SetExpression("Serious", fadeout=10000)
            self.tired = 0
            self.idle_anim = True
            print("I'm WakeUp")

    def initializeGL(self) -> None:
        self.makeCurrent()

        if live2d.LIVE2D_VERSION == 3:
            live2d.glewInit()

        self.model = live2d.LAppModel()

        if live2d.LIVE2D_VERSION == 3:
            if self.models_switch == 0:
                self.model.LoadModelJson(os.path.join(
                    resources.RESOURCES_DIRECTORY, "v3/Neptune/Neptune.model3.json"))

            elif self.models_switch == 1:
                self.model.LoadModelJson(os.path.join(
                    resources.RESOURCES_DIRECTORY, "v3/PurpleHeart/PurpleHeart.model3.json"))

            elif self.models_switch == 2:
                self.model.LoadModelJson(os.path.join(
                    resources.RESOURCES_DIRECTORY, "v3/Noire/Noire.model3.json"))
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

        if self.on_mouse_anim:
            self.model.StartRandomMotion("OnMouse", live2d.MotionPriority.NORMAL, onFinishMotionHandler=callback)
            self.on_mouse_anim = False

        local_x, local_y = QCursor.pos().x() - self.x(), QCursor.pos().y() - self.y()
        if self.isInL2DArea(local_x, local_y):
            self.isInLA = True
            self.clickInLA = True
            if not self.sleep: # False
                self.on_mouse_anim = True
            #print("in l2d area")
        else:
            self.isInLA = False
            self.clickInLA = False
            #print("out of l2d area")

        self.update()

    def isInL2DArea(self, click_x, click_y):
        h = self.height()
        alpha = gl.glReadPixels(click_x * self.systemScale, (h - click_y) * self.systemScale, 1, 1, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE)[3]
        return alpha > 0

    def mousePressEvent(self, event: QMouseEvent) -> None:
        x, y = event.scenePosition().x(), event.scenePosition().y()
        if self.isInL2DArea(x, y):
            self.clickInLA = True
            self.clickX, self.clickY = x, y
            self.model.StopAllMotions()
            if not self.sleep: # False
                self.model.SetExpression("Funny")
            if self.sleep: # True
                self.model.SetExpression("Surprised")
            print("pressed")

    def mouseReleaseEvent(self, event):
        x, y = event.scenePosition().x(), event.scenePosition().y()
        # if self.isInL2DArea(x, y):
        if self.isInLA:
            self.model.Touch(x, y)
            self.clickInLA = False
            self.tap_body_anim = True
            if self.tap_body_anim:
                self.model.StartRandomMotion("TapBody",live2d.MotionPriority.FORCE, onFinishMotionHandler=callback)
                self.tap_body_anim = False
                if not self.sleep: # False
                    self.model.SetRandomExpression()
                    self.fadeout_t.start(3500)
                    self.tired = 1
                if self.sleep: # True
                    self.model.ResetExpression()
                    self.model.SetExpression("Distaste", fadeout=10000)
                    self.tired = 1
                    self.sleep = False
            print("released")

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        x, y = event.scenePosition().x(), event.scenePosition().y()
        if self.clickInLA:
            self.move(int(self.x() + x - self.clickX), int(self.y() + y - self.clickY))


if __name__ == "__main__":
    import sys

    live2d.init()
    format = QSurfaceFormat.defaultFormat()
    format.setSwapInterval(0)
    QSurfaceFormat.setDefaultFormat(format)

    app = QApplication(sys.argv)
    win = Win()
    win.setWindowTitle("Nep Assistant")
    win.show()
    app.exec()

    live2d.dispose()
