import os
from typing import Optional
from configparser import ConfigParser
from PySide6.QtCore import QObject, Signal

class AppConfig(QObject):
    """A class for managing application settings."""
    config_changed = Signal(str, str, str)  # section, key, value

    DEFAULT_CONFIG = {
        'Main': {
            'language': 'English',
            'color_icons': 'False',
            'background': 'False',
            'theme': '',
            'screen_width': '0',
            'screen_height': '0'
        },
        'WindowFlags': {
            'X11BypassWindowManagerHint': 'True',
            'FramelessWindowHint': 'True',
            'WindowMinimizeButtonHint': 'True',
            'WindowMaximizeButtonHint': 'False',
            'WindowCloseButtonHint': 'True',
            'WindowTransparentForInput': 'False',
            'WindowType_Mask': 'False',
            'WindowStaysOnTopHint': 'True',
            'WindowStaysOnBottomHint': 'False'
        },
        'Model': {
            'auto_scale': 'True',
            'models_scale': '1',
            'random_character': 'False',
            'random_character_hdd': 'False',
            'random_character_evil_transformed': 'False',
            'character_name': 'Neptune',
            'l2d_scale': '1',
            'offset_x': '0',
            'offset_y': '0',
            'x_param': '0',
            'y_param': '0',
            'w_resize': '0',
            'h_resize': '0',
            'w_correction': '0',
            'h_correction': '0'
        },
        'Behavior': {
            'auto_blink': 'True',
            'auto_breath': 'True',
            'tracking_mouse': 'True',
            'sleep': 'True',
            'time_scale': '1',
            'time_schedule': 'False',
            'use_12h_format': 'False',
            'sleep_h': '23',
            'sleep_m': '0',
            'wake_h': '8',
            'wake_m': '0',
            'idle_animation': 'True',
            'on_mouse_animation': 'True',
            'tap_body_animation': 'True'
        },
        'Audio': {
            'audio_system': 'True',
            'master': '100',
            'voice': '100',
            'sfx': '90',
            'bgm': '60',
            'ambient': '50'
        },
        'Other': {
            'show_text_widget': 'True',
            'show_name': 'True',
            'show_kaomoji': 'True',
            'birthday_active': 'False',
            'birthday_year': '0',
            'birthday_month': '0',
            'birthday_day': '0'
        }
    }

    def __init__(self):
        super().__init__()
        self._config = self._load_or_create_config()

    def _load_or_create_config(self) -> ConfigParser:
        """Loads the config or creates a new one with default values"""
        config = ConfigParser()

        if os.path.exists('config.ini'):
            config.read('config.ini')
        self._validate_and_fix_config(config)

        return config

    def _validate_and_fix_config(self, config: ConfigParser):
        """Проверяет и создает недостающие секции и ключи"""
        config_changed = False

        for section, options in self.DEFAULT_CONFIG.items():
            if not config.has_section(section):
                config.add_section(section)
                config_changed = True

            for key, default_value in options.items():
                if not config.has_option(section, key):
                    config.set(section, key, default_value)
                    config_changed = True

        if config_changed:
            self._save_full_config(config)

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
        return self._config.getboolean('Model', 'auto_scale')

    @auto_scale.setter
    def auto_scale(self, value: bool):
        self._config.set('Model', 'auto_scale', str(value))
        self._save_and_notify('Model', 'auto_scale', str(value))

    # Language config
    @property
    def language(self) -> str:
        return self._config.get('Main', 'language')

    @language.setter
    def language(self, value: str):
        self._config.set('Main', 'language', value)
        self._save_and_notify('Main', 'language', value)

    # Color icons config
    @property
    def color_icons(self) -> bool:
        return self._config.getboolean('Main', 'color_icons')

    @color_icons.setter
    def color_icons(self, value: bool):
        self._config.set('Main', 'color_icons', str(value))
        self._save_and_notify('Main', 'color_icons', str(value))

    @property
    def background(self) -> bool:
        return self._config.getboolean('Main', 'background')

    @background.setter
    def background(self, value: bool):
        self._config.set('Main', 'background', str(value))
        self._save_and_notify('Main', 'background', str(value))

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
        return self._config.getfloat('Model', 'models_scale')

    @models_scale.setter
    def models_scale(self, value: float):
        self._config.set('Model', 'models_scale', str(value))
        self._save_and_notify('Model', 'models_scale', str(value))

    def update_model_params(
            self,
            character_name: Optional[str] = None,
            l2d_scale: Optional[float] = None,
            offset_x: Optional[float] = None,
            offset_y: Optional[float] = None,
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
        if character_name is not None:
            self._config.set('Model', 'character_name', character_name)
        if l2d_scale is not None:
            self._config.set('Model', 'l2d_scale', str(l2d_scale))
        if offset_x is not None:
            self._config.set('Model', 'offset_x', str(offset_x))
        if offset_y is not None:
            self._config.set('Model', 'offset_y', str(offset_y))
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
    def l2d_scale(self) -> float:
        return self._config.getfloat('Model', 'l2d_scale')

    @l2d_scale.setter
    def l2d_scale(self, value: float):
        self._config.set('Model', 'l2d_scale', str(value))
        self._save_and_notify('Model', 'l2d_scale', str(value))

    @property
    def offset_x(self) -> float:
        return self._config.getfloat('Model', 'offset_x')

    @offset_x.setter
    def offset_x(self, value: float):
        self._config.set('Model', 'offset_x', str(value))
        self._save_and_notify('Model', 'offset_x', str(value))

    @property
    def offset_y(self) -> float:
        return self._config.getfloat('Model', 'offset_y')

    @offset_y.setter
    def offset_y(self, value: float):
        self._config.set('Model', 'offset_y', str(value))
        self._save_and_notify('Model', 'offset_y', str(value))

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

    @property
    def random_character(self) -> bool:
        return self._config.getboolean('Model', 'random_character')

    @random_character.setter
    def random_character(self, value: bool):
        self._config.set('Model', 'random_character', str(value))
        self._save_and_notify('Model', 'random_character', str(value))

    @property
    def random_character_hdd(self) -> bool:
        return self._config.getboolean('Model', 'random_character_hdd')

    @random_character_hdd.setter
    def random_character_hdd(self, value: bool):
        self._config.set('Model', 'random_character_hdd', str(value))
        self._save_and_notify('Model', 'random_character_hdd', str(value))

    @property
    def random_character_evil_transformed(self) -> bool:
        return self._config.getboolean('Model', 'random_character_evil_transformed')

    @random_character_evil_transformed.setter
    def random_character_evil_transformed(self, value: bool):
        self._config.set('Model', 'random_character_evil_transformed', str(value))
        self._save_and_notify('Model', 'random_character_evil_transformed', str(value))

    # Animation switches config
    @property
    def idle_switch(self) -> bool:
        return self._config.getboolean('Behavior', 'idle_animation')

    @idle_switch.setter
    def idle_switch(self, value: bool):
        self._config.set('Behavior', 'idle_animation', str(value))
        self._save_and_notify('Behavior', 'idle_animation', str(value))

    @property
    def on_mouse_switch(self) -> bool:
        return self._config.getboolean('Behavior', 'on_mouse_animation')

    @on_mouse_switch.setter
    def on_mouse_switch(self, value: bool):
        self._config.set('Behavior', 'on_mouse_animation', str(value))
        self._save_and_notify('Behavior', 'on_mouse_animation', str(value))

    @property
    def tap_body_switch(self) -> bool:
        return self._config.getboolean('Behavior', 'tap_body_animation')

    @tap_body_switch.setter
    def tap_body_switch(self, value: bool):
        self._config.set('Behavior', 'tap_body_animation', str(value))
        self._save_and_notify('Behavior', 'tap_body_animation', str(value))

    @property
    def sleep_switch(self) -> bool:
        return self._config.getboolean('Behavior', 'sleep')

    @sleep_switch.setter
    def sleep_switch(self, value: bool):
        self._config.set('Behavior', 'sleep', str(value))
        self._save_and_notify('Behavior', 'sleep', str(value))

    @property
    def time_scale(self) -> float:
        return self._config.getfloat('Behavior', 'time_scale')

    @time_scale.setter
    def time_scale(self, value: float):
        self._config.set('Behavior', 'time_scale', str(value))
        self._save_and_notify('Behavior', 'time_scale', str(value))

    @property
    def time_schedule(self) -> bool:
        return self._config.getboolean('Behavior', 'time_schedule')

    @time_schedule.setter
    def time_schedule(self, value: bool):
        self._config.set('Behavior', 'time_schedule', str(value))
        self._save_and_notify('Behavior', 'time_schedule', str(value))

    @property
    def use_12h_format(self) -> bool:
        return self._config.getboolean('Behavior', 'use_12h_format')

    @use_12h_format.setter
    def use_12h_format(self, value: bool):
        self._config.set('Behavior', 'use_12h_format', str(value))
        self._save_and_notify('Behavior', 'use_12h_format', str(value))

    @property
    def sleep_h(self) -> int:
        return self._config.getint('Behavior', 'sleep_h')

    @sleep_h.setter
    def sleep_h(self, value: int):
        self._config.set('Behavior', 'sleep_h', str(value))
        self._save_and_notify('Behavior', 'sleep_h', str(value))

    @property
    def sleep_m(self) -> int:
        return self._config.getint('Behavior', 'sleep_m')

    @sleep_m.setter
    def sleep_m(self, value: int):
        self._config.set('Behavior', 'sleep_m', str(value))
        self._save_and_notify('Behavior', 'sleep_m', str(value))

    @property
    def wake_h(self) -> int:
        return self._config.getint('Behavior', 'wake_h')

    @wake_h.setter
    def wake_h(self, value: int):
        self._config.set('Behavior', 'wake_h', str(value))
        self._save_and_notify('Behavior', 'wake_h', str(value))

    @property
    def wake_m(self) -> int:
        return self._config.getint('Behavior', 'wake_m')

    @wake_m.setter
    def wake_m(self, value: int):
        self._config.set('Behavior', 'wake_m', str(value))
        self._save_and_notify('Behavior', 'wake_m', str(value))

    @property
    def tracking_mouse_switch(self) -> bool:
        return self._config.getboolean('Behavior', 'tracking_mouse')

    @tracking_mouse_switch.setter
    def tracking_mouse_switch(self, value: bool):
        self._config.set('Behavior', 'tracking_mouse', str(value))
        self._save_and_notify('Behavior', 'tracking_mouse', str(value))

    @property
    def auto_blink(self) -> bool:
        return self._config.getboolean('Behavior', 'auto_blink')

    @auto_blink.setter
    def auto_blink(self, value: bool):
        self._config.set('Behavior', 'auto_blink', str(value))
        self._save_and_notify('Behavior', 'auto_blink', str(value))

    @property
    def auto_breath(self) -> bool:
        return self._config.getboolean('Behavior', 'auto_breath')

    @auto_breath.setter
    def auto_breath(self, value: bool):
        self._config.set('Behavior', 'auto_breath', str(value))
        self._save_and_notify('Behavior', 'auto_breath', str(value))

    @property
    def audio_system(self) -> bool:
        return self._config.getboolean('Audio', 'audio_system')

    @audio_system.setter
    def audio_system(self, value: bool):
        self._config.set('Audio', 'audio_system', str(value))
        self._save_and_notify('Audio', 'audio_system', str(value))

    @property
    def master(self) -> int:
        return self._config.getint('Audio', 'master')

    @master.setter
    def master(self, value: int):
        self._config.set('Audio', 'master', str(value))
        self._save_and_notify('Audio', 'master', str(value))

    @property
    def voice(self) -> int:
        return self._config.getint('Audio', 'voice')

    @voice.setter
    def voice(self, value: int):
        self._config.set('Audio', 'voice', str(value))
        self._save_and_notify('Audio', 'voice', str(value))

    @property
    def sfx(self) -> float:
        return self._config.getint('Audio', 'sfx')

    @sfx.setter
    def sfx(self, value: int):
        self._config.set('Audio', 'sfx', str(value))
        self._save_and_notify('Audio', 'sfx', str(value))

    @property
    def bgm(self) -> float:
        return self._config.getint('Audio', 'bgm')

    @bgm.setter
    def bgm(self, value: int):
        self._config.set('Audio', 'bgm', str(value))
        self._save_and_notify('Audio', 'bgm', str(value))

    @property
    def ambient(self) -> int:
        return self._config.getint('Audio', 'ambient')

    @ambient.setter
    def ambient(self, value: int):
        self._config.set('Audio', 'ambient', str(value))
        self._save_and_notify('Audio', 'ambient', str(value))

    @property
    def show_text_widget(self) -> bool:
        return self._config.getboolean('Other', 'show_text_widget')

    @show_text_widget.setter
    def show_text_widget(self, value: bool):
        self._config.set('Other', 'show_text_widget', str(value))
        self._save_and_notify('Other', 'show_text_widget', str(value))

    @property
    def show_name(self) -> bool:
        return self._config.getboolean('Other', 'show_name')

    @show_name.setter
    def show_name(self, value: bool):
        self._config.set('Other', 'show_name', str(value))
        self._save_and_notify('Other', 'show_name', str(value))

    @property
    def show_kaomoji(self) -> bool:
        return self._config.getboolean('Other', 'show_kaomoji')

    @show_kaomoji.setter
    def show_kaomoji(self, value: bool):
        self._config.set('Other', 'show_kaomoji', str(value))
        self._save_and_notify('Other', 'show_kaomoji', str(value))

    @property
    def birthday_active(self) -> bool:
        return self._config.getboolean('Other', 'birthday_active')

    @birthday_active.setter
    def birthday_active(self, value: bool):
        self._config.set('Other', 'birthday_active', str(value))
        self._save_and_notify('Other', 'birthday_active', str(value))

    @property
    def birthday_year(self) -> int:
        return self._config.getint('Other', 'birthday_year')

    @birthday_year.setter
    def birthday_year(self, value: int):
        self._config.set('Other', 'birthday_year', str(value))
        self._save_and_notify('Other', 'birthday_year', str(value))

    @property
    def birthday_month(self) -> int:
        return self._config.getint('Other', 'birthday_month')

    @birthday_month.setter
    def birthday_month(self, value: int):
        self._config.set('Other', 'birthday_month', str(value))
        self._save_and_notify('Other', 'birthday_month', str(value))

    @property
    def birthday_day(self) -> int:
        return self._config.getint('Other', 'birthday_day')

    @birthday_day.setter
    def birthday_day(self, value: int):
        self._config.set('Other', 'birthday_day', str(value))
        self._save_and_notify('Other', 'birthday_day', str(value))

    # Save configs
    def _save_and_notify(self, section: str, key: str, value: str):
        """Saves the config and sends a change signal."""
        with open('config.ini', 'w') as cfg:
            self._config.write(cfg)
        self.config_changed.emit(section, key, value)