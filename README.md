<div align="center" style="padding-top: 10px">
    <img src="./docs/nep.svg" alt="nep" width="100px" height="100px">
    <img src="./docs/nep_logo.svg" alt="my_little_neptune" height="60px">
</div>
<p align="center" style="font-family: 'Roboto', sans-serif; font-size: 1em; color: #555;">
    <br>
    <img title="Python Version" src="https://img.shields.io/badge/Python-3.12.0-blue" alt="Python Version" style="margin: 0 10px;">
    <img title="PySide6 Version" src="https://img.shields.io/badge/PySide6-6.8.1.1-green" alt="PySide6 Version" style="margin: 0 10px;">
    <img title="live2d-py Version" src="https://img.shields.io/badge/live2d-0.3.5-orange" alt="live2d-py Version" style="margin: 0 10px;">
    <img title="App Version" src="https://img.shields.io/badge/version-0.1.7-purple" alt="App Version" style="margin: 0 10px;">
</p>

## The assistant application on your desktop, which pleases you with its appearance every day:)

## The application is based on:
* Python 3.12.0
* PySide6
* [live2d-py by Arkueid](https://github.com/Arkueid/live2d-py)
* Compile Heart / Idea Factory Live2D Models

## Install:
1. Clone or Download Project on your desktop
2. Install requirements `python -m pip install -r requirements.txt`

## Usage:
### Run:
`python package/neptune_main.py`

### Configuration file
The configuration file is created at the first startup, as config.ini

### Models Select:
Neptune model as default

You can change character from the context menu while the application is running

### Auto Scale:
If `auto_scale = True` parameter in config.ini file is `True`, models is scaled based on the screen size

To disable the auto-scale function, change the parameter to `False`

### Models Scale:
Edit `models_scale = 1` parameter in config.ini file, to manual scale model

### Tracking the mouse position:
Tracking the mouse position On as default

If you want Off this function as default:

Change this parameter from the context menu while the application is running.

### Logs:
If you want, you can enable logging to the console, Edit parameter to `True`.
 * l2d-py Main Log: `live2d.setLogEnable(False)`
 * l2d-py Area Log: `self.l2d_area_log = False`
 * Mouse Click Log: `self.mouse_click_log = False`
 * Mouse Tracking Log: `self.mouse_tracking_log = False`
 * Timer Diagnostic Log: `self.timer_log = False`

## Models Available:
<div align="center" style="padding-top: 10px">
    <img src="./docs/model_preview/neptune.svg" alt="neptune" width="310px" height="310px">
    <img src="./docs/model_preview/purple_heart.svg" alt="purple_heart" width="330px" height="330px">
</div>
<div align="center" style="padding-top: 50px">
    <img src="./docs/model_preview/noire.svg" alt="noire" width="320px" height="320px">
    <img src="./docs/model_preview/black_heart.svg" alt="black_heart" width="330px" height="330px">
</div>
<div align="center" style="padding-top: 50px">
    <img src="./docs/model_preview/blanc.svg" alt="blanc" width="310px" height="310px">
    <img src="./docs/model_preview/white_heart.svg" alt="white_heart" width="340px" height="340px">
</div>
<div align="center" style="padding-top: 50px">
    <img src="./docs/model_preview/vert.svg" alt="vert" width="320px" height="320px">
</div>

## Important to read:
<div align="left" style="padding-left: 1px">
    <img src="./docs/work_in_progress.svg" alt="work_in_progress" width="150px" height="150px">
</div>

#### 1. The application is at an early stage of development and may have bugs.
#### 2. The animations need to be improved
#### 3. In the next stages of development, it is planned to work on the GUI, AI assistant base on GPT model and compile the application into an .exe file
### Please specify me, when using my code in your projects
## Thanks for your attention!
