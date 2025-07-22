import os
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QGridLayout, QFrame, QFormLayout, \
    QGraphicsOpacityEffect

from package import resources

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

        center = (win.posX + win.x()) - sSizeX / 2
        if center >= 0:
            win.screenSide = "Right"
        elif center <= 0:
            win.screenSide = "Left"

    def talk_function(win):
        if win.screenSide == "Right":
            if win.a_scale >= 1:
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
        else:
            if win.a_scale >= 1:
                varX = (10 * win.a_scale) + 2.5
                varY = (20 * win.a_scale) + 2.5
            elif win.a_scale >= 2:
                varX = (20 * win.a_scale) + 2.5
                varY = (60 * win.a_scale) + 2.5
            elif win.a_scale >= 3:
                varX = (40 * win.a_scale) + 2.5
                varY = (70 * win.a_scale) + 2.5
            elif win.a_scale >= 4:
                varX = (50 * win.a_scale) + 2.5
                varY = (80 * win.a_scale) + 2.5
            else:
                varX = (5 * win.a_scale) + 2.5
                varY = 20 + 2.5

        if not win.talk:
            win.talkWidget.show()
            win.talk = True

        win.dialogCloseTimer.start(7000)
        win.talkWidget.move(win.twmXR, win.twmY)

        if win.screenSide == "Right":
            if win.character_name == "Neptune":
                win.talkImage = os.path.join(
                    resources.RESOURCES_DIRECTORY, "images/talk/neptune_talk.svg")
            elif win.character_name == "Purple Heart":
                win.talkImage = os.path.join(
                    resources.RESOURCES_DIRECTORY, "images/talk/purple_heart_talk.svg")
            elif win.character_name == "Noire":
                win.talkImage = os.path.join(
                    resources.RESOURCES_DIRECTORY, "images/talk/noire_talk.svg")
            elif win.character_name == "Black Heart":
                win.talkImage = os.path.join(
                    resources.RESOURCES_DIRECTORY, "images/talk/black_heart_talk.svg")
            elif win.character_name == "Blanc":
                win.talkImage = os.path.join(
                    resources.RESOURCES_DIRECTORY, "images/talk/blanc_talk.svg")
            elif win.character_name == "White Heart":
                win.talkImage = os.path.join(
                    resources.RESOURCES_DIRECTORY, "images/talk/white_heart_talk.svg")
            elif win.character_name == "Vert":
                win.talkImage = os.path.join(
                    resources.RESOURCES_DIRECTORY, "images/talk/vert_talk.svg")
            elif win.character_name == "Green Heart":
                win.talkImage = os.path.join(
                    resources.RESOURCES_DIRECTORY, "images/talk/green_heart_talk.svg")
            elif win.character_name == "NepGear":
                win.talkImage = os.path.join(
                    resources.RESOURCES_DIRECTORY, "images/talk/nepgear_talk.svg")
            elif win.character_name == "Purple Sister":
                win.talkImage = os.path.join(
                    resources.RESOURCES_DIRECTORY, "images/talk/purple_sister_talk.svg")
            elif win.character_name == "Uni":
                win.talkImage = os.path.join(
                    resources.RESOURCES_DIRECTORY, "images/talk/uni_talk.svg")
            elif win.character_name == "Black Sister":
                win.talkImage = os.path.join(
                    resources.RESOURCES_DIRECTORY, "images/talk/black_sister_talk.svg")
            elif win.character_name == "Rom":
                win.talkImage = os.path.join(
                    resources.RESOURCES_DIRECTORY, "images/talk/rom_talk.svg")
            elif win.character_name == "White Sister Rom":
                win.talkImage = os.path.join(
                    resources.RESOURCES_DIRECTORY, "images/talk/white_sister_rom_talk.svg")
            elif win.character_name == "Ram":
                win.talkImage = os.path.join(
                    resources.RESOURCES_DIRECTORY, "images/talk/ram_talk.svg")
            elif win.character_name == "White Sister Ram":
                win.talkImage = os.path.join(
                    resources.RESOURCES_DIRECTORY, "images/talk/white_sister_ram_talk.svg")
            elif win.character_name == "Histoire":
                win.talkImage = os.path.join(
                    resources.RESOURCES_DIRECTORY, "images/talk/histoire_talk.svg")
            else:
                win.talkImage = os.path.join(
                    resources.RESOURCES_DIRECTORY, "images/talk/talk.svg")
            win.talkWidget.move(win.twmXR, win.twmY)
        elif win.screenSide == "Left":
            if win.character_name == "Neptune":
                win.talkImage = os.path.join(
                    resources.RESOURCES_DIRECTORY, "images/talk_mirrored/neptune_talk_mirrored.svg")
            elif win.character_name == "Purple Heart":
                win.talkImage = os.path.join(
                    resources.RESOURCES_DIRECTORY, "images/talk_mirrored/purple_heart_talk_mirrored.svg")
            elif win.character_name == "Noire":
                win.talkImage = os.path.join(
                    resources.RESOURCES_DIRECTORY, "images/talk_mirrored/noire_talk_mirrored.svg")
            elif win.character_name == "Black Heart":
                win.talkImage = os.path.join(
                    resources.RESOURCES_DIRECTORY, "images/talk_mirrored/black_heart_talk_mirrored.svg")
            elif win.character_name == "Blanc":
                win.talkImage = os.path.join(
                    resources.RESOURCES_DIRECTORY, "images/talk_mirrored/blanc_talk_mirrored.svg")
            elif win.character_name == "White Heart":
                win.talkImage = os.path.join(
                    resources.RESOURCES_DIRECTORY, "images/talk_mirrored/white_heart_talk_mirrored.svg")
            elif win.character_name == "Vert":
                win.talkImage = os.path.join(
                    resources.RESOURCES_DIRECTORY, "images/talk_mirrored/vert_talk_mirrored.svg")
            elif win.character_name == "Green Heart":
                win.talkImage = os.path.join(
                    resources.RESOURCES_DIRECTORY, "images/talk_mirrored/green_heart_talk_mirrored.svg")
            elif win.character_name == "NepGear":
                win.talkImage = os.path.join(
                    resources.RESOURCES_DIRECTORY, "images/talk_mirrored/nepgear_talk_mirrored.svg")
            elif win.character_name == "Purple Sister":
                win.talkImage = os.path.join(
                    resources.RESOURCES_DIRECTORY, "images/talk_mirrored/purple_sister_talk_mirrored.svg")
            elif win.character_name == "Uni":
                win.talkImage = os.path.join(
                    resources.RESOURCES_DIRECTORY, "images/talk_mirrored/uni_talk_mirrored.svg")
            elif win.character_name == "Black Sister":
                win.talkImage = os.path.join(
                    resources.RESOURCES_DIRECTORY, "images/talk_mirrored/black_sister_talk_mirrored.svg")
            elif win.character_name == "Rom":
                win.talkImage = os.path.join(
                    resources.RESOURCES_DIRECTORY, "images/talk_mirrored/rom_talk_mirrored.svg")
            elif win.character_name == "White Sister Rom":
                win.talkImage = os.path.join(
                    resources.RESOURCES_DIRECTORY, "images/talk_mirrored/white_sister_rom_talk_mirrored.svg")
            elif win.character_name == "Ram":
                win.talkImage = os.path.join(
                    resources.RESOURCES_DIRECTORY, "images/talk_mirrored/ram_talk_mirrored.svg")
            elif win.character_name == "White Sister Ram":
                win.talkImage = os.path.join(
                    resources.RESOURCES_DIRECTORY, "images/talk_mirrored/white_sister_ram_talk_mirrored.svg")
            elif win.character_name == "Histoire":
                win.talkImage = os.path.join(
                    resources.RESOURCES_DIRECTORY, "images/talk_mirrored/histoire_talk_mirrored.svg")
            else:
                win.talkImage = os.path.join(
                    resources.RESOURCES_DIRECTORY, "images/talk_mirrored/talk_mirrored.svg")
            win.talkWidget.move(win.twmXR + win.twmXL, win.twmY+10)
            varX = 0

        win.talkPixmap = QPixmap(win.talkImage).scaled(QSize((win.talkX + 15) * win.a_scale * win.models_scale,
                                                             (win.talkY + 5) * win.a_scale * win.models_scale),
                                                       Qt.KeepAspectRatio, Qt.SmoothTransformation)
        win.talkImageLabel.setPixmap(win.talkPixmap)

        win.talkImageLabelOpacity = QGraphicsOpacityEffect()
        win.talkImageLabelOpacity.setOpacity(0.9)

        win.talkImageLabel.setGraphicsEffect(win.talkImageLabelOpacity)

        win.frameLayout.addWidget(win.talkImageLabel)
        win.textSubWidget.move(varX * win.a_scale * win.models_scale,
                               - varY * win.a_scale * win.models_scale)
        win.talkFont = QFont("Segoe Print", win.talkFontSize * win.a_scale * win.models_scale)
        win.talkFont.setBold(True)
        win.talkTextLabel.setText(win.name + ": " + win.text + "\n" + win.kaomoji)
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
        win.text = win.lang['Talk']['Taking']
        win.kaomoji = "ε=┌( >_<)┘?"
        print(win.name + ": " + win.text + win.kaomoji)
        win.textUpdate()

    def dialogClose(win):
        win.talk = False
        win.talkWidget.close()
        win.dialogCloseTimer.stop()
        win.talkTextLabel.repaint()
        QApplication.processEvents()
        if win.tired_anim.condition == "Sleep":
            win.tired_anim.sleep_func()

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
        win.text = win.lang['MiscellaneousTalk']['SettingsApplied']
        win.kaomoji = "(⌐■_■)"
        win.talkTextLabel.setText(win.name + ": " + win.text + "\n" + win.kaomoji)
        win.talk_function()

    def hello(win):
        win.goodByeTimer.stop()
        win.dialogClose()
        win.models_manager.update_model(win)
        win.text = win.lang['Talk']['Hello']
        win.kaomoji = "(^~^)/"
        win.model.SetExpression("Smile")
        win.fadeoutTimer.start(10000)
        print(win.name + ": " + win.text + win.kaomoji)
        win.textUpdate()
        win.talkUpd = True

    def goodBye(win):
        win.goodByeTimer.start(3000)
        win.text = win.lang['Talk']['Goodbye']
        win.kaomoji = "(-_-)>"
        print(win.name + ": " + win.text + win.kaomoji)
        win.textUpdate()
        if win.tired_anim.condition == "Sleep":
            win.tired_anim.wake_up_func()
        win.talkUpd = False