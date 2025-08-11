import os
from PySide6.QtCore import Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QGridLayout, QFrame, QFormLayout, \
    QGraphicsOpacityEffect

from package import resources
from package.additional.resource_manager import ResourceManager

class TalkWidget:
    def __init__(self, win):
        self.win = win
        self.widget = QWidget(win)
        self.init_ui()
        self.resource_manager = ResourceManager(resources.RESOURCES_DIRECTORY)
        self.talk_update = True
        self.dialog_animation = True
        self.exp_fade_out_var = 7000
        self.is_quitting = True

    # Dialog close timer
    def dialog_timer(self, interval: int | None = None) -> None:
        """Запускает/обновляет таймер закрытия диалога"""
        # Стандартный интервал по умолчанию
        std_interval = 7000
        # Создаём таймер только если его нет
        if not hasattr(self, 'dialogCloseTimer'):
            self.dialogCloseTimer = QTimer()
            self.dialogCloseTimer.setSingleShot(True)
            self.dialogCloseTimer.timeout.connect(self.close_dialog)

        # Определяем актуальный интервал
        if interval == None:
            current_interval = self.exp_fade_out_var if self.exp_fade_out_var != std_interval else std_interval
        elif self.is_quitting:
            current_interval = 3000
        else:
            current_interval = interval

        # Останавливаем и перезапускаем с новым интервалом
        self.dialogCloseTimer.stop()
        self.dialogCloseTimer.start(int(current_interval))

        # Для отладки
        # Logging
        if self.win.timer_log:
            print(f"[Timer] Started with {current_interval}ms (Fade-out: {self.exp_fade_out_var})")

    def init_ui(self):
        """Initializing UI elements"""
        self.grid_layout = QGridLayout(self.widget)
        self.talk_frame = QFrame(self.widget)
        self.frame_layout = QVBoxLayout(self.talk_frame)

        self.talk_image_label = QLabel()
        self.text_sub_widget = QWidget(self.talk_image_label)
        self.talk_form_layout = QFormLayout(self.text_sub_widget)
        self.talk_text_label = QLabel()

        self.grid_layout.addWidget(self.talk_frame, 1, 0, 1, 1)

    @property
    def character_name(self):
        return self.win.character_name

    @property
    def a_scale(self):
        return self.win.a_scale

    @property
    def models_scale(self):
        return self.win.models_scale

    @property
    def name(self):
        return self.win.name

    @property
    def text(self):
        return self.win.text

    @property
    def kaomoji(self):
        return self.win.kaomoji

    @property
    def lang(self):
        return self.win.lang

    @property
    def screenSide(self):
        return self.win.screenSide

    @screenSide.setter
    def screenSide(self, value):
        self.win.screenSide = value

    @property
    def talk(self):
        return self.win.talk

    @talk.setter
    def talk(self, value):
        self.win.talk = value

    @property
    def talkX(self):
        return self.win.talkX

    @property
    def talkY(self):
        return self.win.talkY

    @property
    def talkFontSize(self):
        return self.win.talkFontSize

    @property
    def twmXR(self):
        return self.win.twmXR

    @property
    def twmXL(self):
        return self.win.twmXL

    @property
    def twmY(self):
        return self.win.twmY

    @property
    def posX(self):
        return self.win.posX

    @property
    def x(self):
        return self.win.x()

    @property
    def vSize(self):
        return self.win.vSize

    @property
    def SrcSize(self):
        return self.win.SrcSize

    def change_talk_widget_side(self):
        """Defines the side of the screen for displaying the widget"""
        vSizeX = self.vSize.width()
        sSizeX = self.SrcSize.width()

        center = (self.posX + self.x) - sSizeX / 2
        if center >= 0:
            self.screenSide = "Right"
        elif center <= 0:
            self.screenSide = "Left"

    def show_appearance_animation(self):
        """Show widget Animation"""
        # Setting up transparency with animation
        self.talk_image_label_opacity = QGraphicsOpacityEffect()
        self.talk_image_label_opacity.setOpacity(0.0)  # Начальное значение прозрачности
        self.talk_image_label.setGraphicsEffect(self.talk_image_label_opacity)

        # Создаем анимацию
        self.opacity_animation = QPropertyAnimation(self.talk_image_label_opacity, b"opacity")
        self.opacity_animation.setDuration(250)  # Длительность анимации в миллисекундаха
        self.opacity_animation.setStartValue(0.0)  # Начальное значение
        self.opacity_animation.setEndValue(0.9)  # Конечное значение
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)  # Плавность анимации

        # Добавляем анимацию в очередь (чтобы не блокировать основной поток)
        QTimer.singleShot(0, self.opacity_animation.start)

    def show_talk(self):
        """Shows a widget with the text"""
        if not self.talk:
            self.widget.show()
            self.talk = True

        self.dialog_timer()

        # Get image from ResourceManager
        is_mirrored = self.screenSide == "Left"
        talk_image = self.resource_manager.get_talk_image(
            self.character_name,
            is_mirrored
        )

        # Set Image
        self.talk_image = talk_image
        self._setup_talk_image()

        # Widget positioning
        if is_mirrored:
            self.widget.move(self.twmXR + self.twmXL, self.twmY + 10 * self.models_scale)
        else:
            self.widget.move(self.twmXR, self.twmY + 10 * self.models_scale)

        # Calculating the positioning
        varX, varY = self._calculate_position()

        if self.dialog_animation:
            self.show_appearance_animation()

        # Adding an image to the layout
        self.frame_layout.addWidget(self.talk_image_label)

        # Positioning the subwidget with the text
        self.text_sub_widget.move(
            varX * self.a_scale * self.models_scale,
            -varY * self.a_scale * self.models_scale)

        # Customize font and text
        talk_font = QFont("Segoe Print", self.talkFontSize * self.a_scale * self.models_scale)
        talk_font.setBold(True)

        self.talk_text_label.setText(f"{self.name}: {self.text}\n{self.kaomoji}")
        self.talk_text_label.setFont(talk_font)
        self.talk_text_label.setStyleSheet("color: gray")
        self.talk_text_label.setWordWrap(True)
        self.talk_text_label.setFixedWidth(int((self.talkX - 25) * self.a_scale * self.models_scale))
        self.talk_text_label.setFixedHeight(int((self.talkY - 5) * self.a_scale * self.models_scale))

        self.talk_form_layout.setWidget(0, QFormLayout.LabelRole, self.talk_text_label)

        print(f"{self.name}: {self.text}\n{self.kaomoji}")

    def _setup_talk_image(self):
        """Adjusts the image in the widget"""
        if not os.path.exists(self.talk_image):
            print(f"Warning: Talk image not found at {self.talk_image}")
            return

        pixmap = QPixmap(self.talk_image)
        if pixmap.isNull():
            print(f"Error: Failed to load talk image at {self.talk_image}")
            return

        scaled_pixmap = pixmap.scaled(
            int((self.talkX + 15) * self.a_scale * self.models_scale),
            int((self.talkY + 5) * self.a_scale * self.models_scale),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.talk_image_label.setPixmap(scaled_pixmap)

    def _calculate_position(self):
        """
        Full position calculation with intelligent correction for both axes
        Features:
        - Automatic X and Y correction at any scale
        - Reduction of the correction step at scale > 1.5
        - Separate settings for the right/left sides
        - Optimized formulas for smoothness
        """

        CONFIG = {
            'Right': {
                # Basic offsets
                'base_offset_x': 0,
                'base_offset_y': 20,

                # Correction X
                'x_power': 1.2,
                'base_x_step': 0.25,
                'x_high_scale_factor': 1.5,
                'x_high_scale_multiplier': -0.5,

                # Correction Y
                'y_power': 1.5,
                'base_y_step': 0.4,
                'y_high_scale_factor': 1.5,
                'y_high_scale_multiplier': -0.25,

                # Additional parameters
                'extra_offset_x': 0,
                'image_padding': 15,
                'x_scale_factors':  {4: 50, 3: 40, 2: 20, 1: 10, 0: 5}
            },
            'Left': {
                'base_offset_x': -25.5,
                'base_offset_y': 20,
                'x_power': 1.3,
                'base_x_step': 0.35,
                'x_high_scale_factor': 1.5,
                'x_high_scale_multiplier': -0.3,
                'y_power': 1.8,
                'base_y_step': 0.35,
                'y_high_scale_factor': 1.5,
                'y_high_scale_multiplier': -0.2,
                'extra_offset_x': 15,
                'image_padding': 30,
                'x_scale_factors':  {4: 50, 3: 40, 2: 20, 1: 10, 0: 5}
            }
        }

        side = 'Left' if self.screenSide == "Left" else 'Right'
        cfg = CONFIG[side]
        total_scale = self.a_scale * self.models_scale
        extra_offset_x = cfg['extra_offset_x']
        if total_scale > 1:
            extra_offset_x += (total_scale * 2)

        # Calculate Basic offsets X
        current_scale = next(
            key for key in sorted(cfg['x_scale_factors'].keys(), reverse=True)
            if self.a_scale >= key
        )
        base_x = cfg['x_scale_factors'][current_scale] * total_scale

        # Correction X
        if total_scale != 1:
            x_step = cfg['base_x_step']
            if total_scale > cfg['x_high_scale_factor']:
                x_step *= cfg['x_high_scale_multiplier']

            x_diff = abs(total_scale - 1.0)
            x_direction = 1 if total_scale > 1.0 else -1
            x_adjust = (x_diff ** cfg['x_power']) * x_step * base_x * x_direction
            base_x += x_adjust

        if total_scale < 1 and side == 'Right':
            offset_x = base_x + (cfg['base_offset_x'] + 5) * total_scale
        else:
            offset_x = base_x + cfg['base_offset_x'] * total_scale

        # Additional X for Left side
        if side == 'Left':
            offset_x += extra_offset_x * total_scale
            image_width = (self.talkX + cfg['image_padding']) * total_scale
            text_width = (self.talkX - 25) * total_scale
            free_space = image_width - text_width - abs(offset_x)
            if free_space < 0:
                offset_x += free_space * 0.4  # Soft Correction

        # Calculate and Correction Y
        base_y = cfg['base_offset_y']
        y_adjust = 0

        if total_scale != 1.0:
            y_step = cfg['base_y_step']
            if total_scale > cfg['y_high_scale_factor']:
                y_step *= cfg['y_high_scale_multiplier']

            y_diff = abs(total_scale - 1.0)
            y_direction = 1 if total_scale > 1.0 else -1
            if total_scale == 0.5:
                base_y += 10
            y_adjust = (y_diff ** cfg['y_power']) * y_step * base_y * y_direction

        offset_y = base_y + y_adjust

        # Debug Return
        if False:
            pass

        return offset_x, offset_y

    def close_dialog(self):
        """Close dialog box with Animation"""
        self.dialogCloseTimer.stop()
        if self.dialog_animation:
            self.opacity_animation = QPropertyAnimation(self.talk_image_label_opacity, b"opacity")
            self.opacity_animation.setDuration(500)
            self.opacity_animation.setStartValue(0.9)
            self.opacity_animation.setEndValue(0.0)
            self.opacity_animation.setEasingCurve(QEasingCurve.Type.OutInQuad)  # Плавность анимации
            self.opacity_animation.finished.connect(self.close_dialog_after_animation)  # Скрыть после анимации
            QTimer.singleShot(0, self.opacity_animation.start)
        else:
            self.close_dialog_after_animation()

    def close_dialog_after_animation(self):
        """Closes the dialog box after animation"""
        self.talk = False
        self.widget.close()
        self.talk_text_label.repaint()

        # If you need to process Qt events
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()

        # Sleep state processing
        if hasattr(self.win.character, 'tired_state') and self.win.character.tired_state.condition == "Sleep":
            self.win.character.tired_controller.sleep_function()

    def update_text(self):
        """Updates the text in the widget"""
        self.talk_text_label.repaint()
        self.talk_frame.repaint()

        # If you need to process Qt events
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()

        self.show_talk()

    def update_widget(self):
        """Updates the widget (for example, after changing settings)"""
        try:
            self.talk = True
            # self.screenSide = "Right"

            # Completely cleaning the old widget
            self._clear_widget()

            # Reinitializing the UI (without creating new widgets)
            self._reinit_ui()

            # Updating content
            self.widget.updateGeometry()
            self.win.character.state.set_settings_state(text_key='SettingsApplied')
            # print("Widget updated successfully")

        except Exception as e:
            print(f"Update error: {str(e)}")

    def _clear_widget(self):
        """Careful cleaning of the widget"""
        # Deleting all child elements
        for child in self.widget.findChildren(QWidget):
            child.deleteLater()

        # Clear layout
        if self.widget.layout():
            QWidget().setLayout(self.widget.layout())

        self.widget.hide()

    def _reinit_ui(self):
        """Secure reinitialization of the UI"""
        # Saving the parent widget
        parent = self.widget.parentWidget()

        # Creating a new widget (the old one will be deleted by the garbage collector)
        self.widget = QWidget(parent)
        self.init_ui()  # The main initialization method