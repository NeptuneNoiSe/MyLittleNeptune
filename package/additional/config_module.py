from configparser import ConfigParser

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

def models_config(ms, cn, mx, my, wr, hr, wc, hc, twmx, twmy):
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
    twm_x = twmx
    twm_y = twmy
    config.set('Model', 'selected_model', str(models_select))
    config.set('Model', 'character_name', character_name)
    config.set('Model', 'x_param', str(mx_param))
    config.set('Model', 'y_param', str(my_param))
    config.set('Model', 'w_resize', str(w_resize))
    config.set('Model', 'h_resize', str(h_resize))
    config.set('Model', 'w_correction', str(w_correction))
    config.set('Model', 'h_correction', str(h_correction))
    config.set('Model', 'twmX', str(twm_x))
    config.set('Model', 'twmY', str(twm_y))
    with open('config.ini', 'w') as cfg:
        cfg: [str, int, tuple, object]
        config.write(cfg)
    # return

def auto_scale(height):
    sc_height_size = height
    if sc_height_size == 120:
        a_scale = 0.111
    if sc_height_size == 160:
        a_scale = 0.148
    if sc_height_size == 192:
        a_scale = 0.178
    if sc_height_size == 240:
        a_scale = 0.222
    if sc_height_size == 272:
        a_scale = 0.252
    if sc_height_size == 320:
        a_scale = 0.296
    if sc_height_size == 360:
        a_scale = 0.333
    if sc_height_size == 384:
        a_scale = 0.355
    if sc_height_size == 480:
        a_scale = 0.444
    if sc_height_size == 540:
        a_scale = 0.5
    if sc_height_size == 576:
        a_scale = 0.533
    if sc_height_size == 600:
        a_scale = 0.555
    if sc_height_size == 640:
        a_scale = 0.592
    if sc_height_size == 720:
        a_scale = 0.666
    if sc_height_size == 768:
        a_scale = 0.711
    if sc_height_size == 800:
        a_scale = 0.741
    if sc_height_size == 810:
        a_scale = 0.75
    if sc_height_size == 864:
        a_scale = 0.8
    if sc_height_size == 900:
        a_scale = 0.833
    if sc_height_size == 960:
        a_scale = 0.888
    if sc_height_size == 1024:
        a_scale = 0.948
    if sc_height_size == 1050:
        a_scale = 0.972
    if sc_height_size == 1080:
        a_scale = 1
    if sc_height_size == 1152:
        a_scale = 1.066
    if sc_height_size == 1200:
        a_scale = 1.111
    if sc_height_size == 1280:
        a_scale = 1.185
    if sc_height_size == 1350:
        a_scale = 1.25
    if sc_height_size == 1440:
        a_scale = 1.333
    if sc_height_size == 1536:
        a_scale = 1.422
    if sc_height_size == 1600:
        a_scale = 1.481
    if sc_height_size == 1620:
        a_scale = 1.5
    if sc_height_size == 1800:
        a_scale = 1.666
    if sc_height_size == 2048:
        a_scale = 1.896
    if sc_height_size == 2160:
        a_scale = 2
    if sc_height_size == 2400:
        a_scale = 2.222
    if sc_height_size == 2560:
        a_scale = 2.370
    if sc_height_size == 2880:
        a_scale = 2.666
    if sc_height_size == 3072:
        a_scale = 2.844
    if sc_height_size == 3200:
        a_scale = 2.963
    if sc_height_size == 3240:
        a_scale = 3
    if sc_height_size == 3384:
        a_scale = 3.133
    if sc_height_size == 4096:
        a_scale = 3.793
    if sc_height_size == 4320:
        a_scale = 4
    if sc_height_size == 4800:
        a_scale = 4.444
    if sc_height_size == 8640:
        a_scale = 8
    return a_scale

config_main = main_config()