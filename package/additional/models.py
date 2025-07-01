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

    def get_character_name(self, win, config: dict) -> str:
        """Secure name acquisition with complex name processing"""
        if not config:
            return getattr(win, 'character_name', 'Unknown')

        # Get the original name with protection from None
        char_name = getattr(win, 'character_name', '').strip() or 'Unknown'

        # Try 3 key options by priority:
        # - The exact specified name_key from the config
        # - Option without spaces ("PurpleHeart")
        # - Original name with spaces ("Purple Heart")
        possible_keys = [
            config.get('name_key'),  # An explicitly specified key
            char_name.replace(' ', ''),  # Without spaces
            char_name  # Original name
        ]
        # Looking for the first suitable key in localization
        try:
            lang_names = win.lang.get('Names', {})
            for key in possible_keys:
                if key and key in lang_names:
                    return lang_names[key]
            return char_name
        except (AttributeError, TypeError):
            return char_name

    def apply_character_config(self, win, character_name: str) -> None:
        """Applies the character configuration to the window"""
        config = self.resource_manager.get_character_config(character_name)

        # Update window attribute
        for key, value in config.items():
            if hasattr(win, key):
                setattr(win, key, value)

        # Name update
        win.name = self.get_character_name(win, config)

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

        win.name = self.get_character_name(win, config)

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