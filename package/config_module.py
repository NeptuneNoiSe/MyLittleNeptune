import os
import argparse
import sys
from configparser import ConfigParser
import resources

def main_config():
    config = ConfigParser()
    config.read('config.ini')
    if not config.has_section('Main'):
        config.add_section('Main')
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

def models_config(ms, cn, mx, my, wr, hr, wc, hc):
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
    config.set('Model', 'selected_model', str(models_select))
    config.set('Model', 'character_name', character_name)
    config.set('Model', 'x_param', str(mx_param))
    config.set('Model', 'y_param', str(my_param))
    config.set('Model', 'w_resize', str(w_resize))
    config.set('Model', 'h_resize', str(h_resize))
    config.set('Model', 'w_correction', str(w_correction))
    config.set('Model', 'h_correction', str(h_correction))
    with open('config.ini', 'w') as cfg:
        cfg: [str, int, tuple, object]
        config.write(cfg)
    # return

config_main = main_config()