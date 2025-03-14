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
import resources

class TextWidget:
    def talkWidgetInit(win) -> None:
        win.talkWidget = QWidget(win)
        win.talkGridLayout = QGridLayout(win.talkWidget)
        win.talkFrame = QFrame(win.talkWidget)
        win.frameLayout = QVBoxLayout(win.talkFrame)
        win.talkImageLabel = QLabel()
        win.talkSubWidget = QWidget(win.talkImageLabel)
        win.talkFormLayout = QFormLayout(win.talkSubWidget)
        win.talkTextLabel = QLabel()
        win.talkGridLayout.addWidget(win.talkFrame, 1, 0, 1, 1)

    def talk_function(win):
        # Talk Widget
        if not win.talk:
            win.talkWidget.show()
            win.talk = True

        win.dialogCloseTimer.start(10000)
        win.talkWidget.move(0, 0)

        win.talkImage = os.path.join(
            resources.RESOURCES_DIRECTORY, "images/talk.svg")

        win.talkPixmap = QPixmap(win.talkImage).scaled(win.talkX * win.a_scale * win.models_scale,
                                                       win.talkY * win.a_scale * win.models_scale)
        win.talkImageLabel.setPixmap(win.talkPixmap)

        win.frameLayout.addWidget(win.talkImageLabel)

        win.talkSubWidget.move(8 * win.a_scale * win.models_scale, -20 * win.a_scale * win.models_scale)
        win.talkFont = QFont("Segoe Print", win.talkFontSize * win.a_scale * win.models_scale)
        win.talkFont.setBold(True)
        win.talkTextLabel.setText(win.character_name + ": " + win.text + "\n" + win.kaomoji)
        win.talkTextLabel.setFont(win.talkFont)
        win.talkTextLabel.setStyleSheet("color: gray")
        win.talkTextLabel.setWordWrap(True)
        win.talkTextLabel.setFixedWidth(float((win.talkX - 25) * win.a_scale * win.models_scale))
        win.talkTextLabel.setFixedHeight(float((win.talkY - 5) * win.a_scale * win.models_scale))

        win.talkFormLayout.setWidget(0, QFormLayout.LabelRole, win.talkTextLabel)
        # self.verticalSpacer = QSpacerItem(float(self.talkX * self.a_scale * self.models_scale), 0, QSizePolicy.Minimum, QSizePolicy.Fixed)
        # self.talkFormLayout.setItem(0, QFormLayout.LabelRole, self.verticalSpacer)

    def takingTalk(win):
        win.placeThis = True
        win.talkDelayTimer.stop()
        win.text = "Hey, where are you taking me?"
        win.kaomoji = "(>-<)?"
        print(win.character_name + ": " + win.text + win.kaomoji)
        win.textUpdate()

    def dialogClose(win):
        win.talk = False
        win.talkWidget.close()
        win.dialogCloseTimer.stop()
        win.talkTextLabel.repaint()
        QApplication.processEvents()

    def textUpdate(win):
        win.talkTextLabel.repaint()
        win.talkFrame.repaint()
        QApplication.processEvents()
        win.talk_function()

    def talkWidgetUpdate(win):
        win.talk = True
        win.talkWidget.close()
        win.talkWidgetInit()
        win.text = "The settings are applied"
        win.kaomoji = "(@~@)"
        win.talkTextLabel.setText(win.character_name + ": " + win.text + "\n" + win.kaomoji)
        win.talk_function()

    def hello(win):
        win.goodByeTimer.stop()
        win.text = " "
        win.kaomoji = " "
        win.textUpdate()
        win.model_update()
        win.text = "Hello!"
        win.kaomoji = "(^~^)/"
        win.model.SetExpression("Smile", fadeout=10000)
        print(win.character_name + ": " + win.text + win.kaomoji)
        win.textUpdate()
        win.talkUpd = True

    def goodBye(win):
        win.goodByeTimer.start(3000)
        win.text = "GoodBye"
        win.kaomoji = "(-_-)>"
        print(win.character_name + ": " + win.text + win.kaomoji)
        win.textUpdate()
        win.talkUpd = False