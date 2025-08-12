from typing import Optional
from configparser import ConfigParser
from PySide6.QtCore import QObject, Signal

class AppConfig(QObject):
    """A class for managing application settings."""
    config_changed = Signal(str, str, str)  # section, key, value

    def __init__(self):
        super().__init__()
        self._config = self._load_or_create_config()

    def _load_or_create_config(self) -> ConfigParser:
        """Loads the config or creates a new one with default values"""
        config = ConfigParser()
        config.read('config.ini')

        if not self._check_config_sections(config):
            self._create_default_config(config)
            self._save_full_config(config)

        return config

    def _check_config_sections(self, config: ConfigParser) -> bool:
        """Checking the availability of all necessary sections"""
        required_sections = {
            'Main', 'WindowFlags', 'Scale',
            'Model', 'Animations', 'Settings'
        }
        return all(config.has_section(section) for section in required_sections)

    def _create_default_config(self, config: ConfigParser):
        """Fills the config with default values"""
        # Main section
        if not config.has_section('Main'):
            config.add_section('Main')
            config.set('Main', 'language', 'English')
            config.set('Main', 'color_icons', 'False')
            config.set('Main', 'theme', '')
            config.set('Main', 'screen_width', '0')
            config.set('Main', 'screen_height', '0')

        # WindowFlags section
        if not config.has_section('WindowFlags'):
            config.add_section('WindowFlags')
            window_flags = {
                'X11BypassWindowManagerHint': 'True',
                'FramelessWindowHint': 'True',
                'WindowMinimizeButtonHint': 'True',
                'WindowMaximizeButtonHint': 'False',
                'WindowCloseButtonHint': 'True',
                'WindowTransparentForInput': 'False',
                'WindowType_Mask': 'False',
                'WindowStaysOnTopHint': 'True',
                'WindowStaysOnBottomHint': 'False'
            }
            for flag, value in window_flags.items():
                config.set('WindowFlags', flag, value)

        # Other sections
        sections = {
            'Scale': {
                'auto_scale': 'True',
                'models_scale': '1'
            },
            'Model': {
                'character_name': 'Neptune',
                'selected_model': '0',
                'x_param': '0',
                'y_param': '0',
                'w_resize': '0',
                'h_resize': '0',
                'w_correction': '0',
                'h_correction': '0'
            },
            'Animations': {
                'idle_animation': 'True',
                'on_mouse_animation': 'True',
                'tap_body_animation': 'True'
            },
            'Settings': {
                'auto_blink': 'True',
                'auto_breath': 'True',
                'tracking_mouse': 'True',
                'sleep': 'True'
            }
        }

        for section, options in sections.items():
            if not config.has_section(section):
                config.add_section(section)
                for key, value in options.items():
                    config.set(section, key, value)

    def _save_full_config(self, config: ConfigParser):
        """Saves the entire config with the notification"""
        with open('config.ini', 'w') as cfg:
            config.write(cfg)
        # Notification of changes to all sections
        for section in config.sections():
            self.config_changed.emit(section, 'section_updated', 'true')

    # Window Flags config
    @property
    def FramelessWindowHint(self) -> bool:
        return self._config.getboolean('WindowFlags', 'FramelessWindowHint')

    @FramelessWindowHint.setter
    def FramelessWindowHint(self, value: bool):
        self._config.set('WindowFlags', 'FramelessWindowHint', str(value))
        self._save_and_notify('WindowFlags', 'FramelessWindowHint', str(value))

    @property
    def WindowStaysOnTopHint(self) -> bool:
        return self._config.getboolean('WindowFlags', 'WindowStaysOnTopHint')

    @WindowStaysOnTopHint.setter
    def WindowStaysOnTopHint(self, value: bool):
        self._config.set('WindowFlags', 'WindowStaysOnTopHint', str(value))
        self._save_and_notify('WindowFlags', 'WindowStaysOnTopHint', str(value))

    @property
    def WindowMinimizeButtonHint(self) -> bool:
        return self._config.getboolean('WindowFlags', 'WindowMinimizeButtonHint')

    @WindowMinimizeButtonHint.setter
    def WindowMinimizeButtonHint(self, value: bool):
        self._config.set('WindowFlags', 'WindowMinimizeButtonHint', str(value))
        self._save_and_notify('WindowFlags', 'WindowMinimizeButtonHint', str(value))

    @property
    def WindowCloseButtonHint(self) -> bool:
        return self._config.getboolean('WindowFlags', 'WindowCloseButtonHint')

    @WindowCloseButtonHint.setter
    def WindowCloseButtonHint(self, value: bool):
        self._config.set('WindowFlags', 'WindowCloseButtonHint', str(value))
        self._save_and_notify('WindowFlags', 'WindowCloseButtonHint', str(value))

    @property
    def WindowStaysOnBottomHint(self) -> bool:
        return self._config.getboolean('WindowFlags', 'WindowStaysOnBottomHint')

    @WindowStaysOnBottomHint.setter
    def WindowStaysOnBottomHint(self, value: bool):
        self._config.set('WindowFlags', 'WindowStaysOnBottomHint', str(value))
        self._save_and_notify('WindowFlags', 'WindowStaysOnBottomHint', str(value))

    @property
    def WindowTransparentForInput(self) -> bool:
        return self._config.getboolean('WindowFlags', 'WindowTransparentForInput')

    @WindowTransparentForInput.setter
    def WindowTransparentForInput(self, value: bool):
        self._config.set('WindowFlags', 'WindowTransparentForInput', str(value))
        self._save_and_notify('WindowFlags', 'WindowTransparentForInput', str(value))

    @property
    def WindowType_Mask(self) -> bool:
        return self._config.getboolean('WindowFlags', 'WindowType_Mask')

    @WindowType_Mask.setter
    def WindowType_Mask(self, value: bool):
        self._config.set('WindowFlags', 'WindowType_Mask', str(value))
        self._save_and_notify('WindowFlags', 'WindowType_Mask', str(value))

    # Screen config
    @property
    def sc_width_size(self) -> int:
        return self._config.getint('Main', 'screen_width')

    @sc_width_size.setter
    def sc_width_size(self, value: int):
        self._config.set('Main', 'screen_width', str(value))
        self._save_and_notify('Main', 'screen_width', str(value))

    @property
    def sc_height_size(self) -> int:
        return self._config.getint('Main', 'screen_height')

    @sc_height_size.setter
    def sc_height_size(self, value: int):
        self._config.set('Main', 'screen_height', str(value))
        self._save_and_notify('Main', 'screen_height', str(value))

    # Auto scale config
    @staticmethod
    def get_auto_scale(height: int) -> float:
        """An optimized version of auto_scale using a dictionary."""
        scale_map = {
            120: 0.111, 160: 0.148, 192: 0.178, 240: 0.222, 272: 0.252, 320: 0.296, 360: 0.333, 384: 0.355, 480: 0.444,
            540: 0.5, 576: 0.533, 600: 0.555, 640: 0.592, 720: 0.666, 768: 0.711, 800: 0.741, 810: 0.75, 864: 0.8,
            900: 0.833, 960: 0.888, 1024: 0.948, 1050: 0.972, 1080: 1, 1152: 1.066, 1200: 1.111, 1280: 1.185,
            1350: 1.25, 1440: 1.333, 1536: 1.422, 1600: 1.481, 1620: 1.5, 1800: 1.666, 2048: 1.896, 2160: 2,
            2400: 2.222, 2560: 2.370, 2880: 2.666, 3072: 2.844, 3200: 2.963, 3240: 3, 3384: 3.133, 4096: 3.793,
            4320: 4, 4800: 4.444, 8640: 5
        }
        return scale_map.get(height, 1.0)  # 1.0 - Default Scale

    @property
    def auto_scale(self) -> bool:
        return self._config.getboolean('Scale', 'auto_scale')

    @auto_scale.setter
    def auto_scale(self, value: bool):
        self._config.set('Scale', 'auto_scale', str(value))
        self._save_and_notify('Scale', 'auto_scale', str(value))

    # Language config
    @property
    def language(self) -> str:
        return self._config.get('Main', 'language')

    @language.setter
    def language(self, value: str):
        self._config.set('Main', 'language', value)
        self._save_and_notify('Main', 'language', value)

    @property
    def color_icons(self) -> bool:
        return self._config.getboolean('Main', 'color_icons')

    @color_icons.setter
    def color_icons(self, value: bool):
        self._config.set('Main', 'color_icons', str(value))
        self._save_and_notify('Main', 'color_icons', str(value))

    # Theme config
    @property
    def theme(self) -> str:
        return self._config.get('Main', 'theme')

    @theme.setter
    def theme(self, value: str):
        self._config.set('Main', 'theme', value)
        self._save_and_notify('Main', 'theme', value)

    # Models config
    @property
    def models_scale(self) -> float:
        return self._config.getfloat('Scale', 'models_scale')

    @models_scale.setter
    def models_scale(self, value: float):
        self._config.set('Scale', 'models_scale', str(value))
        self._save_and_notify('Scale', 'models_scale', str(value))

    @property
    def models_switch(self) -> int:
        return self._config.getint('Model', 'selected_model')

    @models_switch.setter
    def models_switch(self, value: int):
        self._config.set('Model', 'selected_model', str(value))
        self._save_and_notify('Model', 'selected_model', str(value))

    def update_model_params(
            self,
            model_id: Optional[int] = None,
            character_name: Optional[str] = None,
            x_param: Optional[int] = None,
            y_param: Optional[int] = None,
            w_resize: Optional[int] = None,
            h_resize: Optional[int] = None,
            w_correction: Optional[float] = None,
            h_correction: Optional[float] = None,
            twm_xr: Optional[float] = None,
            twm_xl: Optional[float] = None,
            twm_y: Optional[float] = None
    ):
        """Updates the model parameters (all parameters are optional)"""
        if model_id is not None:
            self._config.set('Model', 'selected_model', str(model_id))
        if character_name is not None:
            self._config.set('Model', 'character_name', character_name)
        if x_param is not None:
            self._config.set('Model', 'x_param', str(x_param))
        if y_param is not None:
            self._config.set('Model', 'y_param', str(y_param))
        if w_resize is not None:
            self._config.set('Model', 'w_resize', str(w_resize))
        if h_resize is not None:
            self._config.set('Model', 'h_resize', str(h_resize))
        if w_correction is not None:
            self._config.set('Model', 'w_correction', str(w_correction))
        if h_correction is not None:
            self._config.set('Model', 'h_correction', str(h_correction))
        if twm_xr is not None:
            self._config.set('Model', 'twmXR', str(twm_xr))
        if twm_xl is not None:
            self._config.set('Model', 'twmXL', str(twm_xl))
        if twm_y is not None:
            self._config.set('Model', 'twmY', str(twm_y))

        self._save_and_notify('Model', 'params_updated', 'true')

    @property
    def mx_param(self) -> int:
        return self._config.getint('Model', 'x_param')

    @mx_param.setter
    def mx_param(self, value: int):
        self._config.set('Model', 'x_param', str(value))
        self._save_and_notify('Model', 'x_param', str(value))

    @property
    def my_param(self) -> int:
        return self._config.getint('Model', 'y_param')

    @my_param.setter
    def my_param(self, value: int):
        self._config.set('Model', 'y_param', str(value))
        self._save_and_notify('Model', 'y_param', str(value))

    @property
    def w_resize(self) -> int:
        return self._config.getint('Model', 'w_resize')

    @w_resize.setter
    def w_resize(self, value: int):
        self._config.set('Model', 'w_resize', str(value))
        self._save_and_notify('Model', 'w_resize', str(value))

    @property
    def h_resize(self) -> int:
        return self._config.getint('Model', 'h_resize')

    @h_resize.setter
    def h_resize(self, value: int):
        self._config.set('Model', 'h_resize', str(value))
        self._save_and_notify('Model', 'h_resize', str(value))

    # Character position correction
    @property
    def w_correction(self) -> int:
        return self._config.getint('Model', 'w_correction')

    @property
    def h_correction(self) -> int:
        return self._config.getint('Model', 'h_correction')

    # Talk Widget position
    @property
    def twmXR(self) -> float:
        return self._config.getint('Model', 'twmXR')

    @twmXR.setter
    def twmXR(self, value: float):
        self._config.set('Model', 'twmXR', str(value))
        self._save_and_notify('Model', 'twmXR', str(value))

    @property
    def twmXL(self) -> float:
        return self._config.getfloat('Model', 'twmXL')

    @twmXL.setter
    def twmXL(self, value: float):
        self._config.set('Model', 'twmXL', str(value))
        self._save_and_notify('Model', 'twmXL', str(value))

    @property
    def twmY(self) -> float:
        return self._config.getfloat('Model', 'twmY')

    @twmY.setter
    def twmY(self, value: float):
        self._config.set('Model', 'twmY', str(value))
        self._save_and_notify('Model', 'twmY', str(value))

    @property
    def character_name(self) -> str:
        return self._config.get('Model', 'character_name')

    @character_name.setter
    def character_name(self, value: str):
        self._config.set('Model', 'character_name', str(value))
        self._save_and_notify('Model', 'character_name', str(value))

    # Animation switches config
    @property
    def idle_switch(self) -> bool:
        return self._config.getboolean('Animations', 'idle_animation')

    @idle_switch.setter
    def idle_switch(self, value: bool):
        self._config.set('Animations', 'idle_animation', str(value))
        self._save_and_notify('Animations', 'idle_animation', str(value))

    @property
    def on_mouse_switch(self) -> bool:
        return self._config.getboolean('Animations', 'on_mouse_animation')

    @on_mouse_switch.setter
    def on_mouse_switch(self, value: bool):
        self._config.set('Animations', 'on_mouse_animation', str(value))
        self._save_and_notify('Animations', 'on_mouse_animation', str(value))

    @property
    def tap_body_switch(self) -> bool:
        return self._config.getboolean('Animations', 'tap_body_animation')

    @tap_body_switch.setter
    def tap_body_switch(self, value: bool):
        self._config.set('Animations', 'tap_body_animation', str(value))
        self._save_and_notify('Animations', 'tap_body_animation', str(value))

    @property
    def sleep_switch(self) -> bool:
        return self._config.getboolean('Settings', 'sleep')

    @sleep_switch.setter
    def sleep_switch(self, value: bool):
        self._config.set('Settings', 'sleep', str(value))
        self._save_and_notify('Settings', 'sleep', str(value))

    @property
    def tracking_mouse_switch(self) -> bool:
        return self._config.getboolean('Settings', 'tracking_mouse')

    @tracking_mouse_switch.setter
    def tracking_mouse_switch(self, value: bool):
        self._config.set('Settings', 'tracking_mouse', str(value))
        self._save_and_notify('Settings', 'tracking_mouse', str(value))

    @property
    def auto_blink(self) -> bool:
        return self._config.getboolean('Settings', 'auto_blink')

    @auto_blink.setter
    def auto_blink(self, value: bool):
        self._config.set('Settings', 'auto_blink', str(value))
        self._save_and_notify('Settings', 'auto_blink', str(value))

    @property
    def auto_breath(self) -> bool:
        return self._config.getboolean('Settings', 'auto_breath')

    @auto_breath.setter
    def auto_breath(self, value: bool):
        self._config.set('Settings', 'auto_breath', str(value))
        self._save_and_notify('Settings', 'auto_breath', str(value))


    # Save configs
    def _save_and_notify(self, section: str, key: str, value: str):
        """Saves the config and sends a change signal."""
        with open('config.ini', 'w') as cfg:
            self._config.write(cfg)
        self.config_changed.emit(section, key, value)