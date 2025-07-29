import os
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QGridLayout, QFrame, QFormLayout, \
    QGraphicsOpacityEffect

from package import resources
from package.additional.characters import CharacterManager

from PySide6.QtWidgets import (QWidget, QGridLayout, QFrame, QVBoxLayout,
                               QLabel, QFormLayout, QGraphicsOpacityEffect)
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import QSize, Qt
import os

class TalkWidget:
    def __init__(self, win):
        self.win = win
        self.widget = QWidget(win)
        self.init_ui()
        self.character = CharacterManager(self)
        self.talk_update = True

        # Dialog close timer
        self.dialogCloseTimer = QTimer()
        self.dialogCloseTimer.timeout.connect(self.close_dialog)

        self.fadeoutTimer = self.character.expressions.fadeoutTimer

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

    def show_talk(self):
        """Shows a widget with the text"""
        if not self.talk:
            self.widget.show()
            self.talk = True

        self.dialogCloseTimer.start(7000)
        self.widget.move(self.twmXR, self.twmY)

        # We define the image depending on the side and location of the character
        talk_dir = "talk" if self.screenSide == "Right" else "talk_mirrored"
        suffix = "" if self.screenSide == "Right" else "_mirrored"

        character_images = {
            "Neptune": f"neptune_talk{suffix}.svg",
            "Purple Heart": f"purple_heart_talk{suffix}.svg",
            "Noire": f"noire_talk{suffix}.svg",
            "Black Heart": f"black_heart_talk{suffix}.svg",
            "Blanc": f"blanc_talk{suffix}.svg",
            "White Heart": f"white_heart_talk{suffix}.svg",
            "Vert": f"vert_talk{suffix}.svg",
            "Green Heart": f"green_heart_talk{suffix}.svg",
            "NepGear": f"nepgear_talk{suffix}.svg",
            "Purple Sister": f"purple_sister_talk{suffix}.svg",
            "Uni": f"uni_talk{suffix}.svg",
            "Black Sister": f"black_sister_talk{suffix}.svg",
            "Rom": f"rom_talk{suffix}.svg",
            "White Sister Rom": f"white_sister_rom_talk{suffix}.svg",
            "Ram": f"ram_talk{suffix}.svg",
            "White Sister Ram": f"white_sister_ram_talk{suffix}.svg",
            "Histoire": f"histoire_talk{suffix}.svg"
        }

        image_name = character_images.get(self.character_name, f"talk{suffix}.svg")
        self.talk_image = os.path.join(
            resources.RESOURCES_DIRECTORY, f"images/{talk_dir}/{image_name}")

        if self.screenSide == "Left":
            self.widget.move(self.twmXR + self.twmXL, self.twmY + 10)

        # Calculating the positioning
        varX, varY = self._calculate_position()

        # Настраиваем изображение
        talk_pixmap = QPixmap(self.talk_image).scaled(
            QSize((self.talkX + 15) * self.a_scale * self.models_scale,
                  (self.talkY + 5) * self.a_scale * self.models_scale),
            Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.talk_image_label.setPixmap(talk_pixmap)

        # Setting up transparency
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0.9)
        self.talk_image_label.setGraphicsEffect(opacity_effect)

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

    def _calculate_position(self):
        """Precise text positioning taking into account all zoom factors"""
        # Configuration for different sides (in pixels at a base scale of 1.0)
        CONFIG = {
            'Right': {
                'base_offset_x': 0,
                'base_offset_y': 0,
                'extra_offset_x': 0,
                'image_padding': 15  # Indentation inside the image
            },
            'Left': {
                'base_offset_x': -25.5,
                'base_offset_y': 0,
                'extra_offset_x': 15,
                'image_padding': 30  # Increased indentation for the mirrored version
            }
        }

        # Defining the current configuration
        side = 'Left' if self.screenSide == "Left" else 'Right'
        cfg = CONFIG[side]

        # Calculating the overall scale
        total_scale = self.a_scale * self.models_scale

        # Text offset coefficients (selected experimentally)
        scale_factors = {
            4: {'x': 50, 'y': 80},
            3: {'x': 40, 'y': 70},
            2: {'x': 20, 'y': 60},
            1: {'x': 10, 'y': 20},
            0: {'x': 5, 'y': 20}
        }

        # Finding a suitable scale level
        current_scale = next(
            key for key in sorted(scale_factors.keys(), reverse=True)
            if self.a_scale >= key
        )

        # Calculating the base offsets
        base_x = scale_factors[current_scale]['x'] * total_scale
        base_y = scale_factors[current_scale]['y'] * total_scale

        # Adjusting based on configuration
        offset_x = base_x + cfg['base_offset_x'] * total_scale
        offset_y = base_y + cfg['base_offset_y'] * total_scale

        # Additional correction for the left side
        if side == 'Left':
            offset_x += cfg['extra_offset_x'] * total_scale

            # Automatic correction based on image size
            image_width = (self.talkX + cfg['image_padding']) * total_scale
            text_width = (self.talkX - 25) * total_scale

            # Calculating the free space
            free_space = image_width - text_width - abs(offset_x)
            if free_space < 0:
                offset_x += free_space * 0.5  # Smooth correction

        return offset_x, offset_y

    def close_dialog(self):
        """Closes the dialog box"""
        self.talk = False
        self.widget.close()
        self.dialogCloseTimer.stop()
        self.talk_text_label.repaint()

        # If you need to process Qt events
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()

        # Sleep state processing
        if hasattr(self.win, 'tired_anim') and self.win.tired_anim.condition == "Sleep":
            self.win.tired_anim.sleep_func()

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
            self.screenSide = "Right"

            # Completely cleaning the old widget
            self._clear_widget()

            # Reinitializing the UI (without creating new widgets)
            self._reinit_ui()

            # Updating content
            self.widget.updateGeometry()
            self.win.character.set_settings_state(text_key='SettingsApplied')
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