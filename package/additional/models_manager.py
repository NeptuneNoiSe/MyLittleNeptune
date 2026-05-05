import os
import random
import live2d.v3 as live2d
from live2d.v3 import Parameter
from package.additional.resource_manager import ResourceManager

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
        """Update window params with size-aware position compensation"""
        # Save the current dimensions and position
        old_width = win.width()
        old_height = win.height()
        current_pos = win.pos()
        current_bottom = current_pos.y() + old_height

        # Updating the parameters from the config
        for param, value in config.items():
            if hasattr(win, param):
                setattr(win, param, value)

        win.name = self.get_character_name(win, config)
        scale_factor = win.a_scale * win.models_scale

        # Calculation of new parameters
        win.posXL = (win.mx_param / 2) - win.posXR / 2
        win.twmXR = int(win.posXR * scale_factor)
        win.twmXL = int(win.posXL * scale_factor)
        win.twmY = int(-10 * scale_factor) if win.a_scale <= 2 else 0

        # Calculation of new scale
        new_width = int(win.mx_param * scale_factor)
        new_height = int(win.my_param * scale_factor)

        # Set resize
        win.resize(1, 1)  # reset size
        win.w_resize = new_width
        win.h_resize = new_height
        win.resize(new_width, new_height)

        # Position correction
        if win.model_move:
            win.position_window()
            win.model_move = False
        else:
            # Fixing the lower bound (new position Y = current bottom - new height)
            new_y = current_bottom - new_height

            # Centering horizontally
            new_x = current_pos.x() - (new_width - old_width) // 2

            # Protection from going beyond the boundaries of the screen
            window_width = win.width()
            screen_geom = win.screen().availableGeometry()
            if window_width > screen_geom.width():
                new_x = screen_geom.left() - (window_width - screen_geom.width()) // 2
            else:
                new_x = max(screen_geom.left(), min(new_x, screen_geom.right() - new_width))

            new_y = max(screen_geom.top(), min(new_y, screen_geom.bottom() - new_height))

            win.move(new_x, new_y)

        # Save config
        win.app_config.update_model_params(character_name=win.character_name,
                                           l2d_scale=win.l2d_scale,
                                           offset_x=win.offset_x,
                                           offset_y=win.offset_y,
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
            live2d.Model.DestroyRenderer(win.model)
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
        fallback_path = os.path.join(self.resources_dir, "models/Neptune/Neptune.model3.json")
        win.model = live2d.Model()
        win.model.LoadModelJson(fallback_path)

    def getModelParams(self, win):
        """Get model parameters"""
        for i in range(win.model.GetParameterCount()):
            param: Parameter = win.model.GetParameter(i)
            print(param.id, param.type, param.value, param.max, param.min, param.default)

    def load_random_character(self, win):
        """Load Random Character"""
        self.random_hdd = win.app_config.random_character_hdd
        base_characters = self.resource_manager.get_base_character_names()
        hdd_characters = self.resource_manager.get_hdd_character_names()
        all_characters = self.resource_manager.get_all_character_names()

        if self.random_hdd:
            selected_character = random.choice(base_characters + hdd_characters)
        else:
            selected_character = random.choice(base_characters)

        win.character_name = selected_character
        startup_config = win.resource_manager.get_character_config(selected_character)

        # Update window params
        self._update_win_params(win, startup_config)

        if win.models_log:
            print(f"[Random Character] Selected: {selected_character} (index: {win.models_switch})")