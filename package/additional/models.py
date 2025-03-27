import os
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QMovie

import live2d.v3 as live2d
# from live2d.utils.lipsync import WavHandler
# from live2d.v3 import StandardParams
# import live2d.v2 as live2d
from package import resources
from package.additional.config_module import *

class Models:
    def transform_initialize(win):
        win.input_lock = True
        if not win.goodness_form:
            if win.character_name == "Neptune":
                win.model.SetExpression("Star")
            elif win.character_name == "NepGear":
                win.model.SetExpression("Star")
            else:
                win.model.SetExpression("Serious")
        if win.goodness_form:
            win.model.SetExpression("Funny")
        win.transformMovie = QMovie(win.t_anim_in)
        win.transformLabel.setMovie(win.transformMovie)
        win.transformLabel.movie().setScaledSize(QSize(int(win.w_resize + win.trm_cmx * win.models_scale),
                                                       int(win.h_resize + win.trm_cmy * win.models_scale))
                                                 ), Qt.KeepAspectRatio, Qt.SmoothTransformation
        win.transformMovie.start()
        win.transformLabel.move(int(win.trm_mx * win.models_scale), int(win.trm_my * win.models_scale))
        win.transformLabel.show()
        win.transform = True
        win.transform_lock = 0

    def transform_complete(win):
        if not win.goodness_form and win.transform_lock == 0:
            win.transform_to_goodness_form()
            win.transform_lock = 1
        if win.goodness_form and win.transform_lock == 0:
            win.transform_to_regular_form()
            win.transform_lock = 1
        win.model.ResetExpression()
        win.model.SetExpression("Funny", fadeout=10000)
        win.transformMovie = QMovie(win.t_anim_out)
        win.transformLabel.setMovie(win.transformMovie)
        win.transformLabel.movie().setScaledSize(QSize(int(win.w_resize + win.trm_cmx * win.models_scale),
                                                       int(win.h_resize + win.trm_cmy * win.models_scale))
                                                 ), Qt.KeepAspectRatio, Qt.SmoothTransformation
        win.transformMovie.start()
        win.transformLabel.move(int(win.trm_mx * win.models_scale), int(win.trm_my * win.models_scale))
        win.transformLabel.show()
        win.transform = False
        win.talkUpd = True

    def transform_to_goodness_form(win):
        # Transform to Goodness Form
        if win.character_name == "Neptune":
            win.on_action_purple_heart()
        if win.character_name == "Noire":
            win.on_action_black_heart()
        if win.character_name == "Blanc":
            win.on_action_white_heart()
        if win.character_name == "Vert":
            win.on_action_green_heart()
        if win.character_name == "NepGear":
            win.on_action_purple_sister()
        if win.character_name == "Uni":
            win.on_action_black_sister()
        if win.character_name == "Rom":
            win.on_action_white_sister_rom()

    def transform_to_regular_form(win):
        # Transform to Regular Form
        if win.character_name == "Purple Heart":
            win.on_action_neptune()
        if win.character_name == "Black Heart":
            win.on_action_noire()
        if win.character_name == "White Heart":
            win.on_action_blanc()
        if win.character_name == "Green Heart":
            win.on_action_vert()
        if win.character_name == "Purple Sister":
            win.on_action_nepgear()
        if win.character_name == "Black Sister":
            win.on_action_uni()
        if win.character_name == "White Sister Rom":
            win.on_action_rom()

    def transformMovieTriggers(win):
        if win.transformMovie.currentFrameNumber() >= win.transformMovie.frameCount() - 3 and win.transform == True:
            win.transformLabel.movie().setScaledSize(QSize(int(1), int(1)))
            win.transformMovie.stop()
            win.transformLabel.close()
            win.transform_complete()

        if win.transformMovie.currentFrameNumber() >= win.transformMovie.frameCount() - 3 and win.transform == False:
            win.transformMovie.stop()
            win.transformLabel.close()
            win.input_lock = False
            if win.transform_text:
                if win.goodness_form:
                    win.text = "I'm Transformed"
                    win.kaomoji = "╰(☆ ͡° ͜ʖ ͡° ☆)つ"
                else:
                    win.text = "I'm back to my normal form."
                    win.kaomoji = "(> ͜ʖ <)"
                win.textUpdate()
                win.transform_text = False

        if win.transformMovie.currentFrameNumber() >= win.transformMovie.frameCount() / 2 and win.transform == True:
            win.dialogClose()
            win.transform_text = True

    def model_update(win):
        # Update Params
        if win.character_name == "Neptune":
            win.character_name = "Neptune"
            win.models_switch = 0
            win.t_count = 1
            win.mx_param = 600
            win.my_param = 600
            win.w_correction = -70
            win.h_correction = 0
            win.twmX = int(85 * win.a_scale * win.models_scale)
            if win.a_scale <= 2:
                win.twmY = int(-10 * win.a_scale * win.models_scale)
            else:
                win.twmY = int(0 * win.a_scale * win.models_scale)

        if win.character_name == "Purple Heart":
            win.character_name = "Purple Heart"
            win.models_switch = 1
            win.t_count = 1
            win.mx_param = 700
            win.my_param = 700
            win.w_correction = -70
            win.h_correction = 0
            win.twmX = int(100 * win.a_scale * win.models_scale)
            if win.a_scale <= 2:
                win.twmY = int(-10 * win.a_scale * win.models_scale)
            else:
                win.twmY = int(0 * win.a_scale * win.models_scale)

        if win.character_name == "Noire":
            win.character_name = "Noire"
            win.models_switch = 2
            win.t_count = 1
            win.mx_param = 700
            win.my_param = 700
            win.w_correction = -70
            win.h_correction = 0
            win.twmX = int(125 * win.a_scale * win.models_scale)
            if win.a_scale <= 2:
                win.twmY = int(-10 * win.a_scale * win.models_scale)
            else:
                win.twmY = int(0 * win.a_scale * win.models_scale)

        if win.character_name == "Black Heart":
            win.character_name = "Black Heart"
            win.models_switch = 3
            win.t_count = 1
            win.mx_param = 700
            win.my_param = 700
            win.w_correction = -70
            win.h_correction = 0
            win.twmX = int(125 * win.a_scale * win.models_scale)
            if win.a_scale <= 2:
                win.twmY = int(-10 * win.a_scale * win.models_scale)
            else:
                win.twmY = int(0 * win.a_scale * win.models_scale)

        if win.character_name == "Blanc":
            win.character_name = "Blanc"
            win.models_switch = 4
            win.t_count = 1
            win.mx_param = 600
            win.my_param = 600
            win.w_correction = -70
            win.h_correction = 0
            win.twmX = int(85 * win.a_scale * win.models_scale)
            if win.a_scale <= 2:
                win.twmY = int(-10 * win.a_scale * win.models_scale)
            else:
                win.twmY = int(0 * win.a_scale * win.models_scale)

        if win.character_name == "White Heart":
            win.character_name = "White Heart"
            win.models_switch = 5
            win.t_count = 1
            win.mx_param = 700
            win.my_param = 700
            win.w_correction = -70
            win.h_correction = 0
            win.twmX = int(125 * win.a_scale * win.models_scale)
            if win.a_scale <= 2:
                win.twmY = int(-10 * win.a_scale * win.models_scale)
            else:
                win.twmY = int(0 * win.a_scale * win.models_scale)

        if win.character_name == "Vert":
            win.character_name = "Vert"
            win.models_switch = 6
            win.t_count = 1
            win.mx_param = 700
            win.my_param = 700
            win.w_correction = -70
            win.h_correction = 0
            win.twmX = int(145 * win.a_scale * win.models_scale)
            if win.a_scale <= 2:
                win.twmY = int(-10 * win.a_scale * win.models_scale)
            else:
                win.twmY = int(0 * win.a_scale * win.models_scale)

        if win.character_name == "Green Heart":
            win.character_name = "Green Heart"
            win.models_switch = 7
            win.t_count = 1
            win.mx_param = 700
            win.my_param = 700
            win.w_correction = -70
            win.h_correction = 0
            win.twmX = int(125 * win.a_scale * win.models_scale)
            if win.a_scale <= 2:
                win.twmY = int(-10 * win.a_scale * win.models_scale)
            else:
                win.twmY = int(0 * win.a_scale * win.models_scale)

        if win.character_name == "NepGear":
            win.character_name = "NepGear"
            win.models_switch = 8
            win.t_count = 1
            win.mx_param = 600
            win.my_param = 600
            win.w_correction = -70
            win.h_correction = 0
            win.twmX = int(100 * win.a_scale * win.models_scale)
            if win.a_scale <= 2:
                win.twmY = int(-10 * win.a_scale * win.models_scale)
            else:
                win.twmY = int(0 * win.a_scale * win.models_scale)

        if win.character_name == "Purple Sister":
            win.character_name = "Purple Sister"
            win.models_switch = 9
            win.t_count = 1
            win.mx_param = 650
            win.my_param = 650
            win.w_correction = -70
            win.h_correction = 0
            win.twmX = int(100 * win.a_scale * win.models_scale)
            if win.a_scale <= 2:
                win.twmY = int(-10 * win.a_scale * win.models_scale)
            else:
                win.twmY = int(0 * win.a_scale * win.models_scale)

        if win.character_name == "Uni":
            win.character_name = "Uni"
            win.models_switch = 10
            win.t_count = 1
            win.mx_param = 600
            win.my_param = 600
            win.w_correction = -70
            win.h_correction = 0
            win.twmX = int(100 * win.a_scale * win.models_scale)
            if win.a_scale <= 2:
                win.twmY = int(-10 * win.a_scale * win.models_scale)
            else:
                win.twmY = int(0 * win.a_scale * win.models_scale)

        if win.character_name == "Black Sister":
            win.character_name = "Black Sister"
            win.models_switch = 11
            win.t_count = 1
            win.mx_param = 650
            win.my_param = 650
            win.w_correction = -70
            win.h_correction = 0
            win.twmX = int(125 * win.a_scale * win.models_scale)
            if win.a_scale <= 2:
                win.twmY = int(-10 * win.a_scale * win.models_scale)
            else:
                win.twmY = int(0 * win.a_scale * win.models_scale)

        if win.character_name == "Rom":
            win.character_name = "Rom"
            win.models_switch = 12
            win.t_count = 1
            win.mx_param = 600
            win.my_param = 600
            win.w_correction = -70
            win.h_correction = 0
            win.twmX = int(100 * win.a_scale * win.models_scale)
            if win.a_scale <= 2:
                win.twmY = int(-10 * win.a_scale * win.models_scale)
            else:
                win.twmY = int(0 * win.a_scale * win.models_scale)

        if win.character_name == "White Sister Rom":
            win.character_name = "White Sister Rom"
            win.models_switch = 13
            win.t_count = 1
            win.mx_param = 650
            win.my_param = 650
            win.w_correction = -70
            win.h_correction = 0
            win.twmX = int(125 * win.a_scale * win.models_scale)
            if win.a_scale <= 2:
                win.twmY = int(-10 * win.a_scale * win.models_scale)
            else:
                win.twmY = int(0 * win.a_scale * win.models_scale)
        # Update Size and Position
        win.resize(1, 1)
        win.w_resize = int(win.mx_param * win.a_scale * win.models_scale)
        win.h_resize = int(win.my_param * win.a_scale * win.models_scale)
        win.resize(int(win.w_resize), int(win.h_resize))
        win.frmX = (win.SrcSize.width() - win.width()) - win.w_correction
        win.frmY = (win.SrcSize.height() - win.height()) - win.h_correction
        win.move(int(win.frmX), int(win.frmY))

        # ReInitialize Model
        win.model: live2d.LAppModel | None = None
        win.model = live2d.LAppModel()
        if win.character_name == "Neptune":
            win.model.LoadModelJson(os.path.join(
                resources.RESOURCES_DIRECTORY, "v3/Neptune/Neptune.model3.json"))
        if win.character_name == "Purple Heart":
            win.model.LoadModelJson(os.path.join(
                resources.RESOURCES_DIRECTORY, "v3/PurpleHeart/PurpleHeart.model3.json"))
        if win.character_name == "Noire":
            win.model.LoadModelJson(os.path.join(
                resources.RESOURCES_DIRECTORY, "v3/Noire/Noire.model3.json"))
        if win.character_name == "Black Heart":
            win.model.LoadModelJson(os.path.join(
                resources.RESOURCES_DIRECTORY, "v3/BlackHeart/BlackHeart.model3.json"))
        if win.character_name == "Blanc":
            win.model.LoadModelJson(os.path.join(
                resources.RESOURCES_DIRECTORY, "v3/Blanc/Blanc.model3.json"))
        if win.character_name == "White Heart":
            win.model.LoadModelJson(os.path.join(
                resources.RESOURCES_DIRECTORY, "v3/WhiteHeart/WhiteHeart.model3.json"))
        if win.character_name == "Vert":
            win.model.LoadModelJson(os.path.join(
                resources.RESOURCES_DIRECTORY, "v3/Vert/Vert.model3.json"))
        if win.character_name == "Green Heart":
            win.model.LoadModelJson(os.path.join(
                resources.RESOURCES_DIRECTORY, "v3/GreenHeart/GreenHeart.model3.json"))
        if win.character_name == "NepGear":
            win.model.LoadModelJson(os.path.join(
                resources.RESOURCES_DIRECTORY, "v3/NepGear/NepGear.model3.json"))
        if win.character_name == "Purple Sister":
            win.model.LoadModelJson(os.path.join(
                resources.RESOURCES_DIRECTORY, "v3/PurpleSister/PurpleSister.model3.json"))
        if win.character_name == "Uni":
            win.model.LoadModelJson(os.path.join(
                resources.RESOURCES_DIRECTORY, "v3/Uni/Uni.model3.json"))
        if win.character_name == "Black Sister":
            win.model.LoadModelJson(os.path.join(
                resources.RESOURCES_DIRECTORY, "v3/BlackSister/BlackSister.model3.json"))
        if win.character_name == "Rom":
            win.model.LoadModelJson(os.path.join(
                resources.RESOURCES_DIRECTORY, "v3/Rom/Rom.model3.json"))
        if win.character_name == "White Sister Rom":
            win.model.LoadModelJson(os.path.join(
                resources.RESOURCES_DIRECTORY, "v3/WhiteSisterRom/WhiteSisterRom.model3.json"))
        win.resizeGL(int(win.w_resize), int(win.h_resize))
        # Save Config
        models_config(win.models_switch, win.character_name, win.mx_param, win.my_param, win.w_resize,
                      win.h_resize, win.w_correction, win.h_correction, win.twmX, win.twmY)
        # live2d Update
        live2d.clearBuffer()
        win.model.Update()
        if win.talkUpd:
            win.talkWidgetUpdate()

    def setSleepParams(win):
        win.model.SetParameterValue("ParamAngleX", 15, 100)
        win.model.SetParameterValue("ParamAngleY", -20, 100)
        win.model.SetParameterValue("ParamAngleZ", 20, 100)
        win.model.SetParameterValue("ParamBodyAngleX", 10, 100)
        win.model.SetParameterValue("ParamBodyAngleZ", 10, 100)
        if win.character_name == "Neptune":
            win.model.SetParameterValue("ParamAngleX", 25, 100)
            win.model.SetParameterValue("ParamAngleY", -25, 100)
            win.model.SetParameterValue("Param27", 10, 100)
            win.model.SetParameterValue("Param32", 3, 1)
            win.model.SetParameterValue("Param28", 8, 1)
        elif win.character_name == "Purple Heart":
            win.model.SetParameterValue("ParamAngleZ", 0, 100)
        elif win.character_name == "Noire":
            win.model.SetParameterValue("Param4", 30, 100)
            win.model.SetParameterValue("Param54", 1, 100)
            win.model.SetParameterValue("Param57", 30, 100)
            win.model.SetParameterValue("Param56", 30, 100)
        elif win.character_name == "Black Heart":
            pass
        elif win.character_name == "Blanc":
            win.model.SetParameterValue("ParamBodyAngleZ", 5, 100)
            win.model.SetParameterValue("Param6", 30, 100)
            win.model.SetParameterValue("Param7", -30, 100)
            win.model.SetParameterValue("Param14", -300, 100)
            win.model.SetParameterValue("Param8", 30, 100)
            win.model.SetParameterValue("Param", 30, 100)
            win.model.SetParameterValue("Param11", -30, 100)
        elif win.character_name == "White Heart":
            win.model.SetParameterValue("Param12", -30, 100)
            win.model.SetParameterValue("Param11", 30, 100)
            win.model.SetParameterValue("Param13", -30, 100)
            win.model.SetParameterValue("Param14", 30, 100)
            win.model.SetParameterValue("Param29", 30, 100)
            win.model.SetParameterValue("Param41", -30, 100)
        elif win.character_name == "Vert":
            win.model.SetParameterValue("Param", 30, 100)
            win.model.SetParameterValue("Param2", 30, 100)
            win.model.SetParameterValue("Param3", 30, 100)
            win.model.SetParameterValue("Param4", 30, 100)
            win.model.SetParameterValue("Param5", 30, 100)
            win.model.SetParameterValue("Param6", 30, 100)
        elif win.character_name == "Green Heart":
            pass
        elif win.character_name == "NepGear":
            win.model.SetParameterValue("Param", 30, 100)
            win.model.SetParameterValue("Param2", 30, 100)
            win.model.SetParameterValue("Param3", 30, 100)
            win.model.SetParameterValue("Param4", -30, 100)
            win.model.SetParameterValue("Param5", -30, 100)
            win.model.SetParameterValue("Param24", 0.600, 100)
            win.model.SetParameterValue("Param25", 0, 100)
            win.model.SetParameterValue("Param12", 0, 100)
            win.model.SetParameterValue("Param18", 1, 100)
        elif win.character_name == "Purple Sister":
            win.model.SetParameterValue("ParamBodyAngleZ", -10, 100)
            win.model.SetParameterValue("Param", 30, 100)
            win.model.SetParameterValue("Param2", 1, 100)
            win.model.SetParameterValue("Param3", 1, 100)
            win.model.SetParameterValue("Param4", -30, 100)
        elif win.character_name == "Uni":
            win.model.SetParameterValue("Param", 30, 100)
            win.model.SetParameterValue("Param4", -30, 100)
            win.model.SetParameterValue("Param55", 0.55, 1)
        elif win.character_name == "Black Sister":
            win.model.SetParameterValue("Param", 30, 100)
            win.model.SetParameterValue("Param2", 0.2, 100)
            win.model.SetParameterValue("Param3", 1, 100)
            win.model.SetParameterValue("Param55", 1, 100)
            win.model.SetParameterValue("Param38", 5, 100)
            win.model.SetParameterValue("Param39", 10, 100)
            win.model.SetParameterValue("Param40", 10, 100)
            win.model.SetParameterValue("Param41", 10, 100)
        elif win.character_name == "Rom":
            win.model.SetParameterValue("Param55", 0.2, 1)
        elif win.character_name == "White Sister Rom":
            win.model.SetParameterValue("Param", 30, 100)
            win.model.SetParameterValue("Param2", 30, 100)
            win.model.SetParameterValue("Param3", 20, 1)
            win.model.SetParameterValue("Param4", -30, 100)
            win.model.SetParameterValue("Param5", 30, 100)
            win.model.SetParameterValue("Param6", 30, 100)
            win.model.SetParameterValue("Param40", 10, 100)
            win.model.SetParameterValue("Param41", 10, 100)