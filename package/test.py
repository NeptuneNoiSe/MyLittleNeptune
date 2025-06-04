import sys
import os
import random
import time
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
from PySide6.QtCore import QTimer, Qt, QElapsedTimer
from PySide6.QtGui import QMouseEvent, QKeyEvent, QSurfaceFormat
from PySide6.QtOpenGLWidgets import QOpenGLWidget

# Импорт Live2D (убедитесь что библиотека совместима с Qt)
import live2d.v3 as live2d
import resources  # ваш модуль с ресурсами


class Live2DWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.last_update_time = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_model)
        self.offsetX = 0.0
        self.offsetY = 0.0
        self.scale = 1.0
        self.degrees = 0.0
        self.lastExpressionId = ""
        self.activeExpressions = []

        # Настройка OpenGL контекста
        fmt = QSurfaceFormat()
        fmt.setSamples(4)  # мультисэмплинг
        self.setFormat(fmt)

    def initializeGL(self):
        # Инициализация Live2D
        live2d.init()

        # Создание и загрузка модели
        self.model = live2d.Model()
        model_path = os.path.join(resources.RESOURCES_DIRECTORY, "v3/Haru/Haru.model3.json")
        self.model.LoadModelJson(model_path)

        # Загрузка дополнительных анимаций
        drag_down_path = os.path.join(resources.RESOURCES_DIRECTORY, "v3/public_motions/drag_down.motion3.json")
        touch_head_path = os.path.join(resources.RESOURCES_DIRECTORY, "v3/public_motions/touch_head.motion3.json")

        self.model.LoadExtraMotion("extra", 0, drag_down_path)
        self.model.LoadExtraMotion("extra", 1, touch_head_path)

        # Инициализация рендерера
        live2d.glInit()
        self.model.CreateRenderer(2)  # maskBufferCount=2

        # Начальные параметры
        self.last_update_time = time.time()
        self.timer.start(16)  # ~60 FPS

    def resizeGL(self, w, h):
        if self.model:
            self.model.Resize(w, h)

    def paintGL(self):
        if self.model:
            live2d.clearBuffer()
            self.model.Draw()

    def update_model(self):
        if not self.model:
            return

        ct = time.time()
        delta_secs = max(0.0001, ct - self.last_update_time)
        self.last_update_time = ct

        # Обновление модели (аналогично оригинальному коду)
        motion_updated = False
        self.model.LoadParameters()

        if not self.model.IsMotionFinished():
            motion_updated = self.model.UpdateMotion(delta_secs)

        self.model.SaveParameters()

        if not motion_updated:
            self.model.UpdateBlink(delta_secs)

        self.model.UpdateExpression(delta_secs)
        self.model.UpdateDrag(delta_secs)
        self.model.UpdateBreath(delta_secs)
        self.model.UpdatePhysics(delta_secs)
        self.model.UpdatePose(delta_secs)

        self.update()  # запрос перерисовки

    def add_random_expression(self, drop_last=False):
        if drop_last:
            self.model.RemoveExpression(self.lastExpressionId)

        expressions = self.model.GetExpressions()
        expId = random.choice(expressions)
        self.model.AddExpression(expId)

        self.lastExpressionId = expId
        self.activeExpressions.append(expId)
        return expId

    # --- Обработчики событий ---
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.model.StartRandomMotion(
                onStart=lambda group, no: print(f"{group} {no} started"),
                onFinish=lambda group, no: print(f"{group} {no} finished"),
            )

    def mouseMoveEvent(self, event: QMouseEvent):
        pos = event.position()
        self.model.Drag(pos.x(), pos.y())

    def wheelEvent(self, event):
        pos = event.position()
        x, y = pos.x(), pos.y()

        # Hit-тестирование
        hit_drawable_ids = self.model.HitDrawable(x, y, True)
        print("hit drawables:", hit_drawable_ids)

        hit_part_ids = self.model.HitPart(x, y, True)
        print("hit parts:", hit_part_ids)

        if self.model.IsAreaHit("Head", x, y):
            print("add expression:", self.add_random_expression())

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()

        if key == Qt.Key_Up:
            self.offsetY += 0.1
        elif key == Qt.Key_Down:
            self.offsetY -= 0.1
        elif key == Qt.Key_Left:
            self.offsetX -= 0.1
        elif key == Qt.Key_Right:
            self.offsetX += 0.1
        elif key == Qt.Key_U:
            self.scale -= 0.1
        elif key == Qt.Key_I:
            self.scale += 0.1
        elif key == Qt.Key_BracketRight:  # ]
            self.degrees -= 5
        elif key == Qt.Key_BracketLeft:  # [
            self.degrees += 5
        elif key == Qt.Key_E:
            self.model.StartMotion(
                "extra", 0, 3,
                onStart=lambda group, no: print(f"{group} {no} started"),
                onFinish=lambda group, no: print(f"{group} {no} finished"),
            )
        elif key == Qt.Key_R:
            self.model.ResetExpressions()
        elif key == Qt.Key_T:
            print("set expression:", self.model.SetRandomExpression())
        elif key == Qt.Key_Q:
            self.model.ResetExpression()
        else:
            return  # пропускаем необрабатываемые клавиши

        # Применяем трансформации
        if key in {Qt.Key_Up, Qt.Key_Down, Qt.Key_Left, Qt.Key_Right}:
            self.model.SetOffset(self.offsetX, self.offsetY)
        elif key in {Qt.Key_U, Qt.Key_I}:
            self.model.SetScale(self.scale)
        elif key in {Qt.Key_BracketLeft, Qt.Key_BracketRight}:
            self.model.Rotate(self.degrees)

        self.update()

    def cleanup(self):
        """Очистка ресурсов при закрытии"""
        if self.model:
            live2d.dispose()
            self.model = None


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Live2D Viewer")
        self.setGeometry(100, 100, 500, 700)

        self.live2d_widget = Live2DWidget(self)
        self.setCentralWidget(self.live2d_widget)

    def closeEvent(self, event):
        """Гарантированная очистка ресурсов при закрытии окна"""
        self.live2d_widget.cleanup()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())