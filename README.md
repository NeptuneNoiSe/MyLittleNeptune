<div align="center" style="padding-top: 10px">
    <img src="./docs/nep.svg" alt="nep" width="100px" height="100px">
    <img src="./docs/nep_logo.svg" alt="my_little_neptune" height="60px">
</div>
<p align="center" style="font-family: 'Roboto', sans-serif; font-size: 1em; color: #555;">
    <br>
    <img title="Python Version" src="https://img.shields.io/badge/Python-3.13-blue" alt="Python Version" style="margin: 0 10px;">
    <img title="PySide6 Version" src="https://img.shields.io/badge/PySide6-6.8.3-green" alt="PySide6 Version" style="margin: 0 10px;">
    <img title="live2d-py Version" src="https://img.shields.io/badge/live2d-0.6.1-orange" alt="live2d-py Version" style="margin: 0 10px;">
    <img title="App Version" src="https://img.shields.io/badge/app_version-0.2.9.8-D362C4" alt="App Version" style="margin: 0 10px;">
    <img title="DeepSeek AI" src="https://img.shields.io/badge/DeepSeek-Best_Friend-0056D2" alt="DeepSeek AI" style="margin: 0 10px;">
</p>

## The assistant application on your desktop, which pleases you with its appearance every day:)

## The application is based on:
* Python 3.13
* PySide6
* [live2d-py by Arkueid](https://github.com/Arkueid/live2d-py)
* [Particle Engine Supreme by jjkitch](https://github.com/jjkitch/Particle-Engine-Supreme)
* Compile Heart / Idea Factory Live2D Models and Sounds
* [DeepSeek AI](https://www.deepseek.com) - not just a tool, but a true coding partner that provided inspiration, debugging help, and countless hours of thoughtful discussion throughout development ❤️🚀

## Available languages:
* English
* Russian

## Install:
1. Clone or Download Project on your desktop
2. Install requirements `python -m pip install -r requirements.txt`

## Usage:
### Run:
`python launcher.py`

### Configuration file:
The configuration file is created at the first startup, as config.ini

### Models Select:
Neptune model as default

You can change character from the context menu while the application is running

### Auto Scale:
If Auto-scale function on, models is scaled based on the screen size

### Models Scale:
Edit Scale multiplier parameter in settings window, to manual scale model

### Logs:
If you want, you can enable logging to the console, Edit parameter to `True`.
 * l2d-py Main Log: `live2d.enableLog(False)`
 * l2d-py Area Log: `self.l2d_area_log = False`
 * Models Log: `self.models_log = False`
 * Mouse Click Log: `self.mouse_click_log = False`
 * Mouse Tracking Log: `self.mouse_tracking_log = False`
 * Timer Diagnostic Log: `self.timer_log = False`
 * Motion Callbacks Log: `self.callbacks_log = False`
 * Debug Audio System Log: `self.debug_audio_system_log = False`
 * Show Playing Audio Log: `self.playing_audio_log = False`
 * Show Characters Text in Console: `self.show_text_in_console = False`

## Models Available:
<div align="left" style="padding-top: 10px">
    <img src="./docs/model_preview/neptune.svg" alt="neptune" width="250px" height="100px">
    <img src="./docs/model_preview/purple_heart.svg" alt="purple_heart" width="250px" height="100px">
</div>
<div align="left" style="padding-top: 10px">
    <img src="./docs/model_preview/noire.svg" alt="noire" width="250px" height="100px">
    <img src="./docs/model_preview/black_heart.svg" alt="black_heart" width="250px" height="100px">
</div>
<div align="left" style="padding-top: 10px">
    <img src="./docs/model_preview/blanc.svg" alt="blanc" width="250px" height="100px">
    <img src="./docs/model_preview/white_heart.svg" alt="white_heart" width="250px" height="100px">
</div>
<div align="left" style="padding-top: 10px">
    <img src="./docs/model_preview/vert.svg" alt="vert" width="250px" height="100px">
    <img src="./docs/model_preview/green_heart.svg" alt="green_heart" width="250px" height="100px">
</div>
<div align="left" style="padding-top: 10px">
    <img src="./docs/model_preview/nepgear.svg" alt="nepgear" width="250px" height="100px">
    <img src="./docs/model_preview/purple_sister.svg" alt="purple_sister" width="250px" height="100px">
</div>
<div align="left" style="padding-top: 10px">
    <img src="./docs/model_preview/uni.svg" alt="uni" width="250px" height="100px">
    <img src="./docs/model_preview/black_sister.svg" alt="black_sister" width="250px" height="100px">
</div>
<div align="left" style="padding-top: 10px">
    <img src="./docs/model_preview/rom.svg" alt="rom" width="250px" height="100px">
    <img src="./docs/model_preview/white_sister_rom.svg" alt="white_sister_rom" width="250px" height="100px">
</div>
<div align="left" style="padding-top: 10px">
    <img src="./docs/model_preview/ram.svg" alt="rom" width="250px" height="100px">
    <img src="./docs/model_preview/white_sister_ram.svg" alt="white_sister_rom" width="250px" height="100px">
</div>
<div align="left" style="padding-top: 10px">
    <img src="./docs/model_preview/histoire.svg" alt="histoire" width="250px" height="100px">
</div>
<div align="left" style="padding-top: 10px">
    <img src="./docs/model_preview/maho.svg" alt="maho" width="250px" height="100px">
    <img src="./docs/model_preview/grey_sister.svg" alt="grey_sister" width="250px" height="100px">
</div>
<div align="left" style="padding-top: 10px">
    <img src="./docs/model_preview/anri.svg" alt="anri" width="250px" height="100px">
</div>

## Important to read:
<div align="left" style="padding-left: 1px">
    <img src="./docs/work_in_progress.svg" alt="work_in_progress" width="150px" height="150px">
</div>

1. The application is at an early stage of development and may have bugs.
2. The animations need to be improved.
3. In the next stages of development, it is planned to work on the GUI,add functions based on AI model and compile the application into an .exe file.

### Legal Disclaimer & Fair Use Notice:
> This application is a non-commercial, fan-made project created solely for personal, educational, and demonstrative purposes.
>
> - **Live2D models, audio, character names, and likenesses** are the property of their respective copyright holders, such as Compile Heart, Idea Factory, and other related companies. I do not claim any ownership over this content.
> - The use of this content in the project is believed to be permissible under the **Fair Use** (U.S.) and **Fair Dealing** (other jurisdictions) doctrines of copyright law, which allow for limited use of copyrighted material without permission from the rights holders for purposes such as criticism, comment, news reporting, teaching, scholarship, and research.
> - This project is **non-commercial**, does not harm the market value of the original content, and does not purport to be an official product. The goal is to showcase technical implementation, not to infringe on intellectual property rights.
> - If you are a copyright holder and believe that your content is being used in a way that falls outside the bounds of Fair Use, please contact me so we can address the issue.

### A Note of Gratitude:
> I would like to extend my sincere thanks to Compile Heart and Idea Factory for creating the wonderful universe of Neptunia.
> The characters and stories of this series have been a tremendous source of inspiration and motivation for me to work on this project.
> **Thank you for this amazing world!**

Please specify me when using my code in your projects.
