import os
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QMovie

import live2d.v3 as live2d
from live2d.v3 import Parameter

from package.additional.config_module import *
from package.additional.resource_mng import ResourceManager

class ModelsManager:
    def __init__(self, resources_dir: str):
        self.resources_dir = resources_dir
        self.resource_manager = ResourceManager(resources_dir)

    def apply_character_config(self, win, character_name: str) -> None:
        """Applies the character configuration to the window"""
        config = self.resource_manager.get_character_config(character_name)

        # Update window attribute
        for key, value in config.items():
            if hasattr(win, key):
                setattr(win, key, value)

        # Name update
        name_key = config.get('name_key', character_name.replace(' ', ''))
        win.name = win.lang['Names'].get(name_key, character_name)

    def update_model(self, win) -> None:
        """Model update"""
        try:
            # Load config
            new_config = win.resource_manager.get_character_config(win.character_name)
            if win.models_log:
                print(f"Config load for: {win.character_name}: {new_config}")

            # Update window params
            self._update_win_params(win, new_config)

            # Work with model
            self._reload_model(win, new_config)

            # Finalize
            self._finalize_update(win)
            if win.models_log:
                print("The model has been successfully updated!")

        except Exception as e:
            if win.models_log:
                print(f"Update Error: {str(e)}")
            self._load_fallback_model(win)

    def _update_win_params(self, win, config: dict) -> None:
        """Update window params"""
        for param, value in config.items():
            if hasattr(win, param):
                setattr(win, param, value)

        name_key = config.get('name_key', win.character_name.replace(' ', ''))
        win.name = win.lang['Names'].get(name_key, win.character_name)

        win.posXL = (win.mx_param / 2) - win.posXR / 2
        win.twmXR = int(win.posXR * win.a_scale * win.models_scale)
        win.twmXL = int(win.posXL * win.a_scale * win.models_scale)
        win.twmY = int(-10 * win.a_scale * win.models_scale) if win.a_scale <= 2 else 0

        # Calculating position
        win.resize(1, 1)
        win.w_resize = int(win.mx_param * win.a_scale * win.models_scale)
        win.h_resize = int(win.my_param * win.a_scale * win.models_scale)
        win.resize(int(win.w_resize), int(win.h_resize))

        if win.model_move:
            win.frmX = (win.SrcSize.width() - win.width()) - win.w_correction
            win.frmY = (win.SrcSize.height() - win.height()) - win.h_correction
            win.move(int(win.frmX), int(win.frmY))
            win.model_move = False
        else:
            pass

        # Save Config
        models_config(win.models_switch, win.character_name, win.mx_param, win.my_param, win.w_resize,
                      win.h_resize, win.w_correction, win.h_correction, win.twmXR, win.twmXL, win.twmY)

    def _reload_model(self, win, config: dict) -> None:
        """Reload Live2D model"""
        if hasattr(win, 'model'):
            del win.model
            win.model = None

        win.model = live2d.Model()
        model_path = os.path.join(self.resources_dir, config['model_path'])

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"The model file was not found: {model_path}")

        win.model.LoadModelJson(model_path)
        win.resizeGL(int(win.w_resize), int(win.h_resize))

    def _finalize_update(self, win) -> None:
        """Final operations"""
        live2d.clearBuffer()
        win.model.CreateRenderer(2)
        win.initializeAnimations()

        if win.talkUpd:
            win.talkWidgetUpdate()

    def _load_fallback_model(self, win) -> None:
        """Backup option for errors"""
        fallback_path = os.path.join(self.resources_dir, "v3/Neptune/Neptune.model3.json")
        win.model = live2d.Model()
        win.model.LoadModelJson(fallback_path)

class Models:
    def transform_initialize(win):
        win.input_lock = True
        if not win.goodness_form:
            win.anim_manager.play_animation(
                model=win.model,
                anim_type='Motion',
                group_or_id="Unique",  # Group (str)
                no=0,  # number animation (int)
                priority=live2d.MotionPriority.FORCE
            )
            if win.character_name == "Neptune":
                win.model.SetExpression("Star")
            elif win.character_name == "Vert":
                win.model.SetExpression("Smile")
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
        win.model.ResetExpressions()
        win.model.SetExpression("Funny")
        win.fadeoutTimer.start(7000)
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
        if win.character_name == "Ram":
            win.on_action_white_sister_ram()

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
        if win.character_name == "White Sister Ram":
            win.on_action_ram()

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
                    win.text = win.lang['Talk']['TransformedGodness']
                    win.kaomoji = "╰(☆ ͡° ͜ʖ ͡° ☆)つ"
                else:
                    win.text = win.lang['Talk']['TransformedNormal']
                    win.kaomoji = "(> ͜ʖ <)"
                win.textUpdate()
                win.transform_text = False

        if win.transformMovie.currentFrameNumber() >= win.transformMovie.frameCount() / 2 and win.transform == True:
            win.dialogClose()
            win.transform_text = True

    def name_update(win):
        # Update Params
        if win.character_name == "Neptune":
            win.name = win.lang['Names']['Neptune']

        if win.character_name == "Purple Heart":
            win.name = win.lang['Names']['PurpleHeart']

        if win.character_name == "Noire":
            win.name = win.lang['Names']['Noire']

        if win.character_name == "Black Heart":
            win.name = win.lang['Names']['BlackHeart']

        if win.character_name == "Blanc":
            win.name = win.lang['Names']['Blanc']

        if win.character_name == "White Heart":
            win.name = win.lang['Names']['WhiteHeart']

        if win.character_name == "Vert":
            win.name = win.lang['Names']['Vert']

        if win.character_name == "Green Heart":
            win.name = win.lang['Names']['GreenHeart']

        if win.character_name == "NepGear":
            win.name = win.lang['Names']['NepGear']

        if win.character_name == "Purple Sister":
            win.name = win.lang['Names']['PurpleSister']

        if win.character_name == "Uni":
            win.name = win.lang['Names']['Uni']

        if win.character_name == "Black Sister":
            win.name = win.lang['Names']['BlackSister']

        if win.character_name == "Rom":
            win.name = win.lang['Names']['Rom']

        if win.character_name == "White Sister Rom":
            win.name = win.lang['Names']['WhiteSisterRom']

        if win.character_name == "Ram":
            win.name = win.lang['Names']['Ram']

        if win.character_name == "White Sister Ram":
            win.name = win.lang['Names']['WhiteSisterRam']

        if win.character_name == "Histoire":
            win.name = win.lang['Names']['Histoire']

    # Legacy Function( May be removed )
    def setSleepParams(win):
        # Main Model Params
        win.modelRotate = -90
        win.sleepMoveY = 0
        win.model.SetParameterValueById("ParamAngleX", 15, 100)
        win.model.SetParameterValueById("ParamAngleY", -20, 100)
        win.model.SetParameterValueById("ParamAngleZ", -20, 100)
        win.model.SetParameterValueById("ParamBodyAngleX", 10, 100)
        win.model.SetParameterValueById("ParamBodyAngleZ", 30, 100)
        # Unic Params for characters
        if win.character_name == "Neptune":
            win.sleepMoveY = 25
            win.model.SetParameterValueById("ParamAngleY", -25, 100)
            win.model.SetParameterValueById("ParamAngleZ", -10, 100)
            #win.model.SetParameterValue("Param27", 10, 100)
            #win.model.SetParameterValue("Param32", 3, 1)
            win.model.SetParameterValueById("Param28", 9, 1)
        elif win.character_name == "Purple Heart":
            win.sleepMoveY = 0
        elif win.character_name == "Noire":
            win.sleepMoveY = 25
            win.model.SetParameterValueById("Param4", 30, 100)
            win.model.SetParameterValueById("Param54", 1, 100)
            win.model.SetParameterValueById("Param57", 30, 100)
            win.model.SetParameterValueById("Param56", 30, 100)
        elif win.character_name == "Black Heart":
            win.sleepMoveY = 20
        elif win.character_name == "Blanc":
            win.model.SetParameterValueById("ParamAngleZ",30 , 100)
            win.model.SetParameterValueById("ParamBodyAngleZ", 0, 100)
            win.model.SetParameterValueById("Param6", 30, 100)
            win.model.SetParameterValueById("Param7", -30, 100)
            win.model.SetParameterValueById("Param14", -300, 100)
            win.model.SetParameterValueById("Param8", 30, 100)
            win.model.SetParameterValueById("Param", 30, 100)
            win.model.SetParameterValueById("Param11", -30, 100)
        elif win.character_name == "White Heart":
            win.modelRotate = -95
            win.sleepMoveY = 25
            win.model.SetParameterValueById("Param12", -30, 100)
            win.model.SetParameterValueById("Param11", 30, 100)
            win.model.SetParameterValueById("Param13", -30, 100)
            win.model.SetParameterValueById("Param14", 30, 100)
            win.model.SetParameterValueById("Param29", 30, 100)
            win.model.SetParameterValueById("Param41", -30, 100)
        elif win.character_name == "Vert":
            win.sleepMoveY = 25
            win.model.SetParameterValueById("ParamAngleZ", 20, 100)
            win.model.SetParameterValueById("Param", 30, 100)
            win.model.SetParameterValueById("Param2", 30, 100)
            win.model.SetParameterValueById("Param3", 30, 100)
            win.model.SetParameterValueById("Param4", 30, 100)
            win.model.SetParameterValueById("Param5", 30, 100)
            win.model.SetParameterValueById("Param6", 30, 100)
        elif win.character_name == "Green Heart":
            win.sleepMoveY = 0
            win.model.SetParameterValueById("ParamAngleZ", 20, 100)
        elif win.character_name == "NepGear":
            win.sleepMoveY = 25
            win.model.SetParameterValueById("ParamAngleZ", -30, 100)
            win.model.SetParameterValueById("Param", 30, 100)
            win.model.SetParameterValueById("Param2", 30, 100)
            win.model.SetParameterValueById("Param3", 30, 100)
            win.model.SetParameterValueById("Param4", -30, 100)
            win.model.SetParameterValueById("Param5", -30, 100)
            win.model.SetParameterValueById("Param24", 0.600, 100)
            win.model.SetParameterValueById("Param25", 0, 100)
            win.model.SetParameterValueById("Param12", 0, 100)
            win.model.SetParameterValueById("Param18", 1, 100)
        elif win.character_name == "Purple Sister":
            win.modelRotate = -95
            win.sleepMoveY = 15
            win.model.SetParameterValueById("ParamAngleZ", 10, 100)
            win.model.SetParameterValueById("Param", 30, 100)
            win.model.SetParameterValueById("Param2", 1, 100)
            win.model.SetParameterValueById("Param3", 1, 100)
            win.model.SetParameterValueById("Param4", -30, 100)
        elif win.character_name == "Uni":
            win.sleepMoveY = 15
            win.modelRotate = -85
            win.model.SetParameterValueById("ParamAngleZ", 20, 100)
            win.model.SetParameterValueById("Param", 30, 100)
            win.model.SetParameterValueById("Param4", -30, 100)
            win.model.SetParameterValueById("Param55", 0.55, 1)
        elif win.character_name == "Black Sister":
            win.sleepMoveY = 30
            win.modelRotate = -85
            win.model.SetParameterValueById("Param", 30, 100)
            win.model.SetParameterValueById("Param2", 0.2, 100)
            win.model.SetParameterValueById("Param3", 1, 100)
            win.model.SetParameterValueById("Param55", 1, 100)
            win.model.SetParameterValueById("Param38", 5, 100)
            win.model.SetParameterValueById("Param39", 10, 100)
            win.model.SetParameterValueById("Param40", 10, 100)
            win.model.SetParameterValueById("Param41", 10, 100)
        elif win.character_name == "Rom":
            win.sleepMoveY = 25
            win.modelRotate = -85
            win.model.SetParameterValueById("ParamAngleZ", 20, 100)
            win.model.SetParameterValueById("Param55", 0.2, 1)
        elif win.character_name == "White Sister Rom":
            win.sleepMoveY = 65
            win.model.SetParameterValueById("Param", 30, 100)
            win.model.SetParameterValueById("Param2", 30, 100)
            win.model.SetParameterValueById("Param3", 20, 1)
            win.model.SetParameterValueById("Param4", -30, 100)
            win.model.SetParameterValueById("Param5", 30, 100)
            win.model.SetParameterValueById("Param6", 30, 100)
            win.model.SetParameterValueById("Param40", 10, 100)
            win.model.SetParameterValueById("Param41", 10, 100)
        elif win.character_name == "Ram":
            win.sleepMoveY = 25
            win.modelRotate = -85
            win.model.SetParameterValueById("ParamAngleZ", 20, 100)
            win.model.SetParameterValueById("Param", 30, 100)
            win.model.SetParameterValueById("Param2", 30, 100)
            win.model.SetParameterValueById("Param3", 30, 100)
            win.model.SetParameterValueById("Param4", -30, 100)
            win.model.SetParameterValueById("Param5", -30, 100)
            win.model.SetParameterValueById("Param6", -30, 100)
            win.model.SetParameterValueById("Param47", 10, 100)
            win.model.SetParameterValueById("Param46", 10, 100)
        elif win.character_name == "White Sister Ram":
            win.sleepMoveY = 15
            win.model.SetParameterValueById("Param", -30, 100)
            win.model.SetParameterValueById("Param2", -30, 100)
            win.model.SetParameterValueById("Param3", -20, 1)
            win.model.SetParameterValueById("Param4", 30, 100)
            win.model.SetParameterValueById("Param5", 30, 100)
            win.model.SetParameterValueById("Param6", 30, 100)

    def getModelParams(win):
        for i in range(win.model.GetParameterCount()):
            param: Parameter = win.model.GetParameter(i)
            print(param.id, param.type, param.value, param.max, param.min, param.default)