import os
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QGridLayout, QFrame, QFormLayout
import resources

class TalkWidgetMain:
    def talkWidgetInit(win) -> None:
        win.talkWidget = QWidget(win)
        win.talkGridLayout = QGridLayout(win.talkWidget)
        win.talkFrame = QFrame(win.talkWidget)
        win.frameLayout = QVBoxLayout(win.talkFrame)
        win.talkImageLabel = QLabel()
        win.textSubWidget = QWidget(win.talkImageLabel)
        win.talkFormLayout = QFormLayout(win.textSubWidget)
        win.talkTextLabel = QLabel()
        win.talkGridLayout.addWidget(win.talkFrame, 1, 0, 1, 1)

    def changeTalkWidgetSide(win):
        vSizeX = win.vSize.width()
        sSizeX = win.SrcSize.width()

        screens = win.app.screens()
        center = (win.posX + win.x()) - sSizeX / 2
        if center >= 0:
            win.screenSide = "Right"
        elif center <= 0:
            win.screenSide = "Left"

    def talk_function(win):
        if win.a_scale >=1:
            varX = 10 * win.a_scale
            varY = 20 * win.a_scale
        elif win.a_scale >= 2:
            varX = 20 * win.a_scale
            varY = 60 * win.a_scale
        elif win.a_scale >= 3:
            varX = 40 * win.a_scale
            varY = 70 * win.a_scale
        elif win.a_scale >= 4:
            varX = 50 * win.a_scale
            varY = 80 * win.a_scale
        else:
            varX = 5 * win.a_scale
            varY = 20

        if not win.talk:
            win.talkWidget.show()
            win.talk = True

        win.dialogCloseTimer.start(10000)
        win.talkWidget.move(win.twmX, win.twmY)

        if win.screenSide == "Right":
            win.talkImage = os.path.join(
                resources.RESOURCES_DIRECTORY, "images/talk.svg")
            win.talkWidget.move(win.twmX, win.twmY)
        elif win.screenSide == "Left":
            win.talkImage = os.path.join(
                resources.RESOURCES_DIRECTORY, "images/talk_mirrored.svg")
            win.talkWidget.move(win.twmX + (250 * win.a_scale * win.models_scale), win.twmY+10)
            varX = 0

        win.talkPixmap = QPixmap(win.talkImage).scaled(QSize((win.talkX + 15) * win.a_scale * win.models_scale,
                                                             (win.talkY + 5) * win.a_scale * win.models_scale),
                                                       Qt.KeepAspectRatio, Qt.SmoothTransformation)
        win.talkImageLabel.setPixmap(win.talkPixmap)

        win.frameLayout.addWidget(win.talkImageLabel)

        win.textSubWidget.move(varX * win.a_scale * win.models_scale,
                               - varY * win.a_scale * win.models_scale)
        win.talkFont = QFont("Segoe Print", win.talkFontSize * win.a_scale * win.models_scale)
        win.talkFont.setBold(True)
        win.talkTextLabel.setText(win.character_name + ": " + win.text + "\n" + win.kaomoji)
        win.talkTextLabel.setFont(win.talkFont)
        win.talkTextLabel.setStyleSheet("color: gray")
        win.talkTextLabel.setWordWrap(True)
        win.talkTextLabel.setFixedWidth(int((win.talkX - 25) * win.a_scale * win.models_scale))
        win.talkTextLabel.setFixedHeight(int((win.talkY - 5) * win.a_scale * win.models_scale))

        win.talkFormLayout.setWidget(0, QFormLayout.LabelRole, win.talkTextLabel)
        # self.verticalSpacer = QSpacerItem(float(self.talkX * self.a_scale * self.models_scale), 0, QSizePolicy.Minimum, QSizePolicy.Fixed)
        # self.talkFormLayout.setItem(0, QFormLayout.LabelRole, self.verticalSpacer)

    def takingTalk(win):
        win.placeThis = True
        win.talkDelayTimer.stop()
        win.text = "Hey, where are you taking me?"
        win.kaomoji = "ε=┌( >_<)┘?"
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
        win.screenSide = "Right"
        win.talkWidget.close()
        win.talkWidgetInit()
        win.text = "The settings are applied"
        win.kaomoji = "(⌐■_■)"
        win.talkTextLabel.setText(win.character_name + ": " + win.text + "\n" + win.kaomoji)
        win.talk_function()

    def hello(win):
        win.goodByeTimer.stop()
        win.dialogClose()
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