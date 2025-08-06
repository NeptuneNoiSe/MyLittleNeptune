import os
import json
from typing import Any, Union
from configparser import ConfigParser
from PySide6.QtCore import QObject, Signal

def main_config():
    config = ConfigParser()
    config.read('config.ini')
    if not config.has_section('Main'):
        config.add_section('Main')
        config.set('Main', 'language', 'English')
        config.set('Main', 'screen_width', '0')
        config.set('Main', 'screen_height', '0')

    if not config.has_section('WindowFlags'):
        config.add_section('WindowFlags')
        config.set('WindowFlags', 'X11BypassWindowManagerHint', 'True')
        config.set('WindowFlags', 'FramelessWindowHint', 'True')
        config.set('WindowFlags', 'WindowMinimizeButtonHint', 'True')
        config.set('WindowFlags', 'WindowMaximizeButtonHint', 'False')
        config.set('WindowFlags', 'WindowCloseButtonHint', 'True')
        config.set('WindowFlags', 'WindowTransparentForInput', 'False')
        config.set('WindowFlags', 'WindowType_Mask', 'False')
        config.set('WindowFlags', 'WindowStaysOnTopHint', 'True')
        config.set('WindowFlags', 'WindowStaysOnBottomHint', 'False')

    if not config.has_section('Scale'):
        config.add_section('Scale')
        config.set('Scale', 'auto_scale', 'True')
        config.set('Scale', 'models_scale', '1')

    if not config.has_section('Model'):
        config.add_section('Model')
        config.set('Model', 'character_name', 'Neptune')
        config.set('Model', 'selected_model', '0')
        config.set('Model', 'x_param', '0')
        config.set('Model', 'y_param', '0')
        config.set('Model', 'w_resize', '0')
        config.set('Model', 'h_resize', '0')
        config.set('Model', 'w_correction', '0')
        config.set('Model', 'h_correction', '0')

    if not config.has_section('Animations'):
        config.add_section('Animations')
        config.set('Animations', 'idle_animation', 'True')
        config.set('Animations', 'on_mouse_animation', 'True')
        config.set('Animations', 'tap_body_animation', 'True')

    if not config.has_section('Settings'):
        config.add_section('Settings')
        config.set('Settings', 'auto_blink', 'True')
        config.set('Settings', 'auto_breath', 'True')
        config.set('Settings', 'tracking_mouse', 'True')
        config.set('Settings', 'sleep', 'True')

    with open('config.ini', 'w') as cfg:
        cfg: [str, int, tuple, object]
        config.write(cfg)
    return config

def models_config(ms, cn, mx, my, wr, hr, wc, hc, twmxr, twmxl, twmy):
    config = ConfigParser()
    config.read('config.ini')
    models_select = ms
    character_name = cn
    mx_param = mx
    my_param = my
    w_resize = wr
    h_resize = hr
    w_correction = wc
    h_correction = hc
    twm_xr = twmxr
    twm_xl = twmxl
    twm_y = twmy
    config.set('Model', 'selected_model', str(models_select))
    config.set('Model', 'character_name', character_name)
    config.set('Model', 'x_param', str(mx_param))
    config.set('Model', 'y_param', str(my_param))
    config.set('Model', 'w_resize', str(w_resize))
    config.set('Model', 'h_resize', str(h_resize))
    config.set('Model', 'w_correction', str(w_correction))
    config.set('Model', 'h_correction', str(h_correction))
    config.set('Model', 'twmXR', str(twm_xr))
    config.set('Model', 'twmXL', str(twm_xl))
    config.set('Model', 'twmY', str(twm_y))
    with open('config.ini', 'w') as cfg:
        cfg: [str, int, tuple, object]
        config.write(cfg)
    # return

config_main = main_config()

# TODO: [WIP] Класс в активной разработке. Требуется:
#       Полное тестирование после переноса всех функций
class AppConfig(QObject):
    """Класс для управления настройками приложения."""

    config_changed = Signal(str, str, str)  # section, key, value

    def __init__(self):
        super().__init__()
        self._config = config_main  # Используем ваш существующий config_main
        #self._models_config = self._load_models_json("model_configs.json")
        #self._setup_defaults()

    def _load_models_json(self, path: str) -> dict:
        """Loads character configs from a JSON file"""
        config_path = os.path.join(self.resources_dir, "configs/models_config.json")
        with open(config_path, encoding="utf-8") as f:
            return json.load(f)

    def _setup_defaults(self):
        """Проверяет и добавляет отсутствующие секции/ключи."""
        # Можно оставить ваш текущий код из main_config() или адаптировать его здесь
        pass

    @property
    def sc_width_size(self) -> float:
        return self._config.getfloat('Main', 'screen_width')

    @sc_width_size.setter
    def sc_width_size(self, value: float):
        self._config.set('Main', 'screen_width', str(value))
        self._save_and_notify('Main', 'screen_width', str(value))

    @property
    def sc_height_size(self) -> float:
        return self._config.getfloat('Main', 'screen_height')

    @sc_height_size.setter
    def sc_height_size(self, value: float):
        self._config.set('Main', 'screen_height', str(value))
        self._save_and_notify('Main', 'screen_height', str(value))

    @staticmethod
    def get_auto_scale(height: int) -> float:
        """Оптимизированный вариант auto_scale с использованием словаря."""
        scale_map = {
            120: 0.111, 160: 0.148, 192: 0.178, 240: 0.222, 272: 0.252, 320: 0.296, 360: 0.333, 384: 0.355, 480: 0.444,
            540: 0.5, 576: 0.533, 600: 0.555, 640: 0.592, 720: 0.666, 768: 0.711, 800: 0.741, 810: 0.75, 864: 0.8,
            900: 0.833, 960: 0.888, 1024: 0.948, 1050: 0.972, 1080: 1, 1152: 1.066, 1200: 1.111, 1280: 1.185,
            1350: 1.25, 1440: 1.333, 1536: 1.422, 1600: 1.481, 1620: 1.5, 1800: 1.666, 2048: 1.896, 2160: 2,
            2400: 2.222, 2560: 2.370, 2880: 2.666, 3072: 2.844, 3200: 2.963, 3240: 3, 3384: 3.133, 4096: 3.793,
            4320: 4, 4800: 4.444, 8640: 5
        }
        return scale_map.get(height, 1.0)  # 1.0 - значение по умолчанию

    @property
    def auto_scale(self) -> bool:
        return self._config.getboolean('Scale', 'auto_scale')

    @auto_scale.setter
    def auto_scale(self, value: bool):
        self._config.set('Scale', 'auto_scale', str(value))
        self._save_and_notify('Scale', 'auto_scale', str(value))

    @property
    def models_scale(self) -> float:
        return self._config.getfloat('Scale', 'models_scale')

    @models_scale.setter
    def models_scale(self, value: float):
        self._config.set('Scale', 'models_scale', str(value))
        self._save_and_notify('Scale', 'models_scale', str(value))

    @property
    def models_switch(self) -> int:
        return self._config.getfloat('Model', 'selected_model')

    @models_switch.setter
    def models_switch(self, value: int):
        self._config.set('Model', 'selected_model', str(value))
        self._save_and_notify('Model', 'selected_model', str(value))

    @property
    def language(self) -> str:
        return self._config.get('Main', 'language')

    @language.setter
    def language(self, value: str):
        self._config.set('Main', 'language', value)
        self._save_and_notify('Main', 'language', value)



    @property
    def character_name(self) -> str:
        return self._config.get('Model', 'character_name')

    @character_name.setter
    def character_name(self, value: str):
        self._config.set('Model', 'character_name', str(value))
        self._save_and_notify('Model', 'character_name', str(value))


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

    def _save_and_notify(self, section: str, key: str, value: str):
        """Сохраняет конфиг и отправляет сигнал об изменении."""
        with open('config.ini', 'w') as cfg:
            self._config.write(cfg)
        self.config_changed.emit(section, key, value)


