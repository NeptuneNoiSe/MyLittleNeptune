import os
import live2d.v3 as live2d
from live2d.v3 import Parameter

from package.additional.config_module import AppConfig
from package.additional.resource_manager import ResourceManager

class ModelsManager:
    def __init__(self, resources_dir: str):
        self.resources_dir = resources_dir
        self.resource_manager = ResourceManager(resources_dir)
        self.app_config = AppConfig()

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

        scale_factor = win.a_scale * win.models_scale

        win.posXL = (win.mx_param / 2) - win.posXR / 2
        win.twmXR = int(win.posXR * scale_factor)
        win.twmXL = int(win.posXL * scale_factor)
        win.twmY = int(-10 * scale_factor) if win.a_scale <= 2 else 0

        # Calculating position
        win.resize(1, 1)
        win.w_resize = int(win.mx_param * scale_factor)
        win.h_resize = int(win.my_param * scale_factor)
        win.resize(int(win.w_resize), int(win.h_resize))

        if win.model_move:
            win.position_window()
            win.model_move = False
        else:
            pass

        # Save Config
        win.app_config.update_model_params(model_id=win.models_switch,
                                           character_name=win.character_name,
                                           x_param=win.mx_param,
                                           y_param=win.my_param,
                                           w_resize=win.w_resize,
                                           h_resize=win.h_resize,
                                           w_correction=win.w_correction,
                                           h_correction=win.h_correction,
                                           twm_xr=win.twmXR,
                                           twm_xl=win.twmXL,
                                           twm_y=win.twmY)

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
        win.init_classes()
        win.character.tired_controller.reload_timer()

        if win.talk_widget.talk_update:
            win.talk_widget.update_widget()

    def _load_fallback_model(self, win) -> None:
        """Backup option for errors"""
        fallback_path = os.path.join(self.resources_dir, "v3/Neptune/Neptune.model3.json")
        win.model = live2d.Model()
        win.model.LoadModelJson(fallback_path)

    def getModelParams(self, win):
        for i in range(win.model.GetParameterCount()):
            param: Parameter = win.model.GetParameter(i)
            print(param.id, param.type, param.value, param.max, param.min, param.default)