import math
import os
import sys
import time
import resources
import OpenGL.GL as gl
import numpy as np

from PIL import Image
from PySide6.QtCore import QTimerEvent, Qt, QTimer, QRect
from PySide6.QtGui import QGuiApplication, QMouseEvent, QCursor, QScreen, QAction, QIcon, QPalette, QPixmap
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QMenu, QMessageBox, QLabel, QVBoxLayout, QStyleFactory, QApplication, QProgressBar, \
    QWidget

import live2d.v3 as live2d
from live2d.utils.canvas import Canvas
from live2d.utils.lipsync import WavHandler
# from live2d.v3 import StandardParams
# import live2d.v2 as live2d

from additional import (
    AppConfig, ModelsManager, CharacterManager,
    InputHandler, MouseTracker, ResourceManager,
    AnimationsManager, ImageManager, EventManager,
    AudioManager
)
from widgets import TalkWidget
from windows import ModelsWindow, ContextMenuOverlay, ParticleOverlayWindow, PositionWindowController
from platforms import FullScreenController

class MainWindow(QOpenGLWidget):
    def __init__(self, app, version) -> None:
        super().__init__()

        # LOGS:
        # l2d-py Main Log:
        live2d.enableLog(False)
        # Models Log
        self.models_log = False
        # l2d-py Area Log:
        self.l2d_area_log = False
        # Mouse Click Log:
        self.mouse_click_log = False
        # Mouse Tracking Log:
        self.mouse_tracking_log = False
        # Timer Diagnostic Log:
        self.timer_log = False
        # Callbacks Log:
        self.callbacks_log = False
        # Debug Audio System Log:
        self.debug_audio_system_log = False
        # Show Playing Audio Log:
        self.playing_audio_log = False
        # Show Characters Text in Console:
        self.show_text_in_console = False

        ##### MAIN FLAGS #####
        # Set False if you want use model.Draw()
        self.canvas_draw = True

        # Show Model Params
        self.show_model_params = False

        # Initialize functions
        self._init_window_flags()

        self._init_config()

        self._init_vars(app, version)

        self._init_ui()

        self._init_window_geometry()

        self._init_model_params()

        self._resize_model()

        self.position_window_controller.position_window()

        self._position_widget()

        self._init_animations()

        self._init_sound()

        self._init_overlay()

    def set_settings_window(self, settings_window):
        """Установить ссылку на окно настроек"""
        self.settings = settings_window

    def _init_window_flags(self):
        """Initialize Window Flags"""
        self.hintFlags: list[Qt.WindowType] = [
            Qt.WindowType.MSWindowsFixedSizeDialogHint,
            Qt.WindowType.X11BypassWindowManagerHint,
            Qt.WindowType.FramelessWindowHint,
            Qt.WindowType.NoDropShadowWindowHint,
            Qt.WindowType.WindowTitleHint,
            Qt.WindowType.WindowSystemMenuHint,
            Qt.WindowType.WindowMinimizeButtonHint,
            Qt.WindowType.WindowMaximizeButtonHint,
            Qt.WindowType.WindowCloseButtonHint,
            Qt.WindowType.WindowContextHelpButtonHint,
            Qt.WindowType.WindowShadeButtonHint,
            Qt.WindowType.WindowStaysOnTopHint,
            Qt.WindowType.WindowStaysOnBottomHint,
            Qt.WindowType.CustomizeWindowHint,
            Qt.WindowType.WindowTransparentForInput,
            Qt.WindowType.WindowType_Mask
        ]

    def _init_config(self):
        """Initialize config"""
        self.app_config = AppConfig()

        # Language:
        self.language = self.app_config.language

        # Theme:
        self.theme = ""
        self.display_to_style = {
            "Legacy": "windows",
            "Windows": "windows",
            "Windows Vista": "windowsvista",
            "Windows 11": "windows11",
            "Fusion": "fusion",
            "macOS": "macos",
            "GTK+": "gtk+",
            "Breeze": "breeze",
            "Adwaita": "adwaita",
            "Qt5 GTK2": "qt5gtk2",
            "CDE": "cde",
            "Motif": "motif",
            "CleanLooks": "cleanlooks"
        }

        # AutoScale: If True, the models is scaled based on the screen size
        self.auto_scale = self.app_config.auto_scale

        # Models Scale
        self.models_scale = self.app_config.models_scale

        # Sleep Animation Time Scale
        self.time_scale = self.app_config.time_scale

    def _init_vars(self, app, version):
        """Initialize Main Vars"""
        # Main Vars
        self.settings = None
        self.app = app
        self.version = version

        # Icons Vars
        self.ICON_COLOR_FOLDER = "black"
        self.color_icons = True

        # Geometry and positioning
        self.auto_scale_init = False
        self.w_correction = 0
        self.h_correction = 0
        self.a_scale = 1
        self.l2d_scale = 1
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.mx_param = 0
        self.my_param = 0
        self.frmX = 0
        self.frmY = 0
        self.trm_mx = -50
        self.trm_my = 5
        self.trm_cmx = 100
        self.trm_cmy = 5
        self.twmXR = 0
        self.twmXL = 0
        self.posXR = 0
        self.posXL = 0
        self.twmY = 0
        self.twsc = 0
        self.talkX = 180
        self.talkY = 150
        self.modelRotate = 0
        self.sleepMoveY = 0
        self.saved_position_x = 0
        self.saved_position_y = 0
        self.frame = 0

        # Model state
        self.transform = False
        self.hdd_form = False
        self.transform_state = False
        self.transform_lock = 0
        self.can_transform = False
        self.transform_text = True

        # Temporary variables
        self.last_update_time = 0
        self.offsetX = 0.0
        self.offsetY = 0.0
        self.scale = 1.0
        self.degrees = 0.0
        self.lastExpressionId = ""
        self.activeExpressions = []

        # UI elements
        self.transformLayout = QVBoxLayout()
        self.transformLabel = QLabel(self)

        # Text and display
        self.text = "Hello!"
        self.kaomoji = "(^~^)/"
        self.screenSide = "Right"
        self.talkFontSize = 10
        self.background_name = None

        # Audio Main Vars
        self.bgm_name = None
        self.bgm_group = "BGM"
        self.current_sing_song = None
        self.song_duration = 0

        # Status flags
        self.tracking_mouse = True
        self.mouse_move = False
        self.mouse_timer = None
        self.isInLA = False
        self.clickInLA = False
        self.click = False
        self.test = False
        self.read = False
        self.settings_update_state = False
        self.settings_lock = False
        self.character_lock = False
        self.model_move = False
        self.talk = True
        self.reset_expression = True
        self.frameless = False
        self.on_top = False
        self.background = False
        self.background_available = False
        self.first_run = True
        self.quit_box_active = False
        self.animation_status = False

        # Mouse position
        self.clickX = -1
        self.clickY = -1
        self.posX = -1
        self.posY = -1

        # Canvas Vars
        self.radius_per_frame = math.pi * 0.5 / 120
        self.total_radius = 0

        self.b_red = 0.0
        self.b_green = 0.0
        self.b_blue = 0.0
        self.b_alpha = 0.0

    def _init_ui(self):
        """Initialize UI Elements"""
        self.resource_manager = ResourceManager(resources.RESOURCES_DIRECTORY)
        self.position_window_controller = PositionWindowController(self)
        self.fullscreen_controller = FullScreenController(self)
        self.model: live2d.Model | None = None
        self.canvas: Canvas | None = None
        self.character = None
        self.talk_widget = None
        self.input_handler = InputHandler(self, self.model)
        self.animation_manager = None
        self.image_manager = None
        self.event_manager = None
        self.lang = None
        self.talk_update = None
        self.models_manager = ModelsManager(
            resources_dir=resources.RESOURCES_DIRECTORY)
        self.audio_manager = AudioManager(self, resources_dir=resources.RESOURCES_DIRECTORY)
        # Mouse Tracker Init
        self.mouse_tracker = MouseTracker(self)
        # Mouse tracking timer
        self.mouse_tracker.idle_timer.timeout.connect(self.input_handler.handle_mouse_idle)
        self.models_window = ModelsWindow(self)
        self.context_menu_overlay = None

    def _init_window_geometry(self):
        """Initialize the window geometry"""
        # self.app = QApplication.instance()
        self.systemScale = QGuiApplication.primaryScreen().devicePixelRatio()
        self.sc_height_size = self.screen().size().height() * self.screen().devicePixelRatio()
        self.sc_width_size = self.screen().size().width() * self.screen().devicePixelRatio()
        self.SrcSize = QScreen.availableGeometry(QApplication.primaryScreen())
        self.vSize = QScreen.availableVirtualGeometry(QApplication.primaryScreen())

        #Set screen size
        self.app_config.sc_width_size = self.sc_width_size
        self.app_config.sc_height_size = self.sc_height_size

        # Screen Size for AutoScale
        if self.auto_scale:
            self.a_scale = self.app_config.get_auto_scale(int(self.sc_height_size))
        if not self.auto_scale:
            self.a_scale = 1

        # Windows flags
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def _init_model_params(self):
        """Initialize Model Parameters"""
        # Character Name
        self.character_name = self.app_config.character_name
        self.name = self.character_name

        # Set Neptune Default Model parameters
        if self.name == "Neptune":
            self.app_config.update_model_params(
                x_param=600,
                y_param=600
            )

            # Calculating the derived parameters
            self.hdd_form = False
            self.can_transform = True

            self.mx_param = self.app_config.mx_param
            self.my_param = self.app_config.my_param

            scale_factor = self.a_scale * self.models_scale
            self.w_res = int(self.mx_param * scale_factor)
            self.h_res = int(self.my_param * scale_factor)

            self.l2d_scale = self.app_config.l2d_scale
            self.offset_x = self.app_config.offset_x
            self.offset_y = self.app_config.offset_y

            # Updating the remaining parameters
            self.app_config.update_model_params(
                l2d_scale=self.l2d_scale,
                offset_x=self.offset_x,
                offset_y=self.offset_y,
                w_resize=self.w_res,
                h_resize=self.h_res,
                w_correction=-70,
                h_correction=0,
                twm_xr=int(64 * scale_factor),
                twm_xl=int((self.mx_param / 2 - 32) * scale_factor),
                twm_y=int(-15 * scale_factor)
            )

    def _resize_model(self):
        """Resize the model with config"""
        # Model Resize
        self.w_resize = self.app_config.w_resize
        self.h_resize = self.app_config.h_resize
        if not self.app_config.FramelessWindowHint:
            self.clamp_window_size_to_screen()
        self.resize(int(self.w_resize), int(self.h_resize))
        self.w_correction = self.app_config.w_correction
        self.h_correction = self.app_config.h_correction

    def clamp_window_size_to_screen(self):
        screen = self.screen().availableGeometry()

        old_size = (self.w_resize, self.h_resize)
        #print(old_size, self.w_resize, self.h_resize)

        self.w_resize = min(self.w_resize, screen.width())
        self.h_resize = min(self.h_resize, screen.height())

        if self.mx_param == 0 or self.my_param == 0:
            self.mx_param = self.app_config.mx_param
            self.my_param = self.app_config.my_param

        max_scale = min(
            screen.width() / self.mx_param,
            screen.height() / self.my_param
        )

        self.safe_models_scale = min(
            self.models_scale,
            max_scale
        )

        self.w_resize = int(
            self.mx_param * self.safe_models_scale
        )

        self.h_resize = int(
            self.my_param * self.safe_models_scale
        )

        self.models_scale = self.safe_models_scale


        if old_size != (self.w_resize, self.h_resize) and self.models_log:
            print(
                f"Window size clamped: "
                f"safe_scale: {self.safe_models_scale} "
                f"{old_size} -> "
                f"{(self.w_resize, self.h_resize)}"
            )

    def _position_widget(self):
        """Position the widget"""
        # Widget Move Params
        self.twmXR = self.app_config.twmXR
        self.twmXL = self.app_config.twmXL
        self.twmY = self.app_config.twmY

    def _init_animations(self):
        """Initialize animations"""
        self.idle_anim = True
        self.on_mouse_anim = False
        self.tap_body_anim = False

        # Animation Switches
        self.idle_switch = self.app_config.idle_switch
        self.on_mouse_switch = self.app_config.on_mouse_switch
        self.tap_body_switch = self.app_config.tap_body_switch
        self.sleep_switch = self.app_config.sleep_switch
        self.tracking_mouse_switch = self.app_config.tracking_mouse_switch

        self.lastUpdateTime = time.monotonic()

    def _init_sound(self):
        """Initialize sound"""
        self.wavHandler = WavHandler()
        self.lipSyncN = 3
        #self.audioPlayed = False

    def _init_overlay(self):
        self.particle_overlay = ParticleOverlayWindow(self, resources_dir=resources.RESOURCES_DIRECTORY)
        self.particle_overlay.show()

    def _update_overlay_position(self):
        """Update overlay window position"""
        if hasattr(self, 'particle_overlay'):
            self.particle_overlay.followMainWindow(self.geometry())

    def setLanguage(self):
        """Set App Localization"""
        # List of supported languages (key: value for load_language)
        supported_languages = {
            "Russian": "russian",
            "English": "english",
            # "Key in the interface": "file_name.json"
        }
        # Choose a language or fallback (english)
        language_key = supported_languages.get(self.language, "english")
        self.lang = self.resource_manager.load_language(language_key)

    def savePng(self, fName):
        """Screenshot function"""
        data = gl.glReadPixels(0, 0, self.width(), self.height(), gl.GL_RGBA, gl.GL_UNSIGNED_BYTE)
        data = np.frombuffer(data, dtype=np.uint8).reshape(self.height(), self.width(), 4)
        data = np.flipud(data)
        new_data = np.zeros_like(data)
        for rid, row in enumerate(data):
            for cid, col in enumerate(row):
                color = None
                new_data[rid][cid] = col
                if cid > 0 and data[rid][cid - 1][3] == 0 and col[3] != 0:
                    color = new_data[rid][cid - 1]
                elif cid > 0 and data[rid][cid - 1][3] != 0 and col[3] == 0:
                    color = new_data[rid][cid]
                if color is not None:
                    color[0] = 0 # 255
                    color[1] = 0
                    color[2] = 0
                    color[3] = 0 # 255
                color = None
                if rid > 0:
                    if data[rid - 1][cid][3] == 0 and col[3] != 0:
                        color = new_data[rid - 1][cid]
                    elif data[rid - 1][cid][3] != 0 and col[3] == 0:
                        color = new_data[rid][cid]
                elif col[3] != 0:
                    color = new_data[rid][cid]
                if color is not None:
                    color[0] = 0 #255
                    color[1] = 0
                    color[2] = 0
                    color[3] = 0 # 255
        img = Image.fromarray(new_data, 'RGBA')
        img.save(fName)

    def change_character(self, name: str):
        """Set character name in Animation Manager """
        self.animation_manager.character_name = name

    def apply_character_config(self, character_name: str) -> None:
        """proxy method"""
        self.models_manager.apply_character_config(self, character_name)

    def initializeGL(self) -> None:
        """Initialize GL"""
        self.makeCurrent()
        live2d.glInit()
        self.model = live2d.Model()

        use_random_character = self.app_config.random_character
        if use_random_character:
            self.models_manager.load_random_character(self)

        self.model = self.resource_manager.get_model(self.character_name)
        self.apply_character_config(self.character_name)
        self.canvas = Canvas()
        self.target_fps = 60  # Сохраняем значение FPS
        self.startTimer(int(1000 / self.target_fps))
        self.setLanguage()
        self.model.CreateRenderer(2)
        self.canvas.SetOutputOpacity(0)
        self.init_classes()
        self.init_logs()
        self.last_update_time = time.monotonic()
        self.character = CharacterManager(self)
        self.talk_widget = TalkWidget(self)

    def showEvent(self, event):
        super().showEvent(event)

        if self.first_run:
            self.talk_widget.talk_image_label_opacity.setOpacity(0)
            QTimer.singleShot(self.target_fps * 10, self._after_first_show)

    def _after_first_show(self):
        self.talk_widget.show_talk()

        self.character.state.set_greeting_state(
            is_first_run=True
        )
        self.input_handler.input_lock = True

        # self.position_window_controller.position_window()

        self.first_run = False

    def init_classes(self):
        """Initialize classes"""
        self.event_manager = EventManager(self)
        self.animation_manager = AnimationsManager(self)
        self.image_manager = ImageManager(self)
        self.animation_manager.set_target_fps(self.target_fps)
        self.change_character(self.character_name)

    def init_logs(self):
        """Initialize logs"""
        self.animation_manager.set_logging(self.callbacks_log)
        self.mouse_tracker.set_perfomance_logging(self.mouse_tracking_log)
        self.resource_manager.set_debug_audio_system_logging(self.debug_audio_system_log)

    def resizeGL(self, w: int, h: int) -> None:
        """Resize GL"""
        if self.model:
            self.model.Resize(w, h)
            self.canvas.SetSize(w, h)
            self.model.SetScale(self.l2d_scale)
            self.model.SetOffset(self.offset_x, self.offset_y)

    def on_draw(self):
        """Canvas draw method"""
        live2d.clearBuffer(self.b_red, self.b_green, self.b_blue, self.b_alpha)
        if self.background:
            self.image_manager.set_background_image(self.background_name)
        self.model.Draw()
        if self.background:
            self.event_manager.draw_text_on_model()

    def verify_startup_geometry(self):
        expected = (self.w_resize, self.h_resize)
        actual = (self.width(), self.height())

        #if expected != actual:
            #print(
            #    f"Startup geometry mismatch. "
            #    f"Expected {expected}, got {actual}"
            #)
            #self.restart_application()

    def paintGL(self) -> None:
        """Paint GL"""
        #self.verify_startup_geometry()
        #vp = gl.glGetIntegerv(gl.GL_VIEWPORT)
        #print("viewport:", vp)
        if self.model:
            live2d.clearBuffer()
            if self.canvas_draw:
                self.canvas.Draw(self.on_draw)
            else:
                # Direct rendering of the model bypassing the "live2d Canvas"
                self.model.Draw()

        if not self.model:
            return

        try:
            # TODO: Fix lost mouse drag and model update with windows resume after sleep
            ct = time.monotonic()
            delta_secs = max(0.0001, ct - self.last_update_time)
            self.last_update_time = ct

            # Main Params load
            self.model.LoadParameters()

            # Safe Animation Update
            motion_updated = False
            if not self.model.IsMotionFinished():
                try:
                    motion_updated = self.model.UpdateMotion(delta_secs)
                except Exception as e:
                    # print(f"Motion update failed: {e}")
                    motion_updated = False

            auto_blink = self.app_config.auto_blink
            self.animation_manager.blink_animator.set_blink_enabled(auto_blink)
            self.animation_manager.blink_animator.update_blink(delta_secs) if auto_blink else None

            # Save Params
            self.model.SaveParameters()

            self.model.UpdateBreath(delta_secs) if self.app_config.auto_breath else None

            #self.model.Update(delta_secs)

            self.model.UpdateExpression(delta_secs)
            self.model.UpdateDrag(delta_secs)
            self.model.UpdatePhysics(delta_secs)
            self.model.UpdatePose(delta_secs)

            if self.wavHandler.Update():  # Get next audio frame, returns False when audio ends Apply mouth animation based on audio volume
                self.model.SetParameterValueById("ParamMouthOpenY", self.wavHandler.GetRms() * self.lipSyncN)

            self.set_app_title()

        except Exception as e:
            print(f"Model update crashed: {e}")
            # Try Reload Model
            self.model.ResetExpressions()
        finally:
            self.update()

        if not self.read:
            if not self.canvas_draw:
                self.savePng('screenshot.png')
            self.read = True

    def set_app_title(self):
        """Set app title and icon"""
        self.setWindowTitle("My Little Neptune")
        self.setWindowIcon(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/app_icon.ico")))

    def set_theme(self):
        """Set app theme"""
        #app.setStyle(self.theme if self.theme != "Default" else "")  # Default = empty line
        style_key = self.display_to_style.get(self.theme, "")  # if theme on a dictionary → Default ("")

        # 2. Set Style
        if style_key:
            self.app.setStyle(QStyleFactory.create(style_key))  # For Windows 11, Fusion and more.
        else:
            self.app.setStyle("")  # System Style (Default)

    def get_system_theme(self):
        """
        Defines the theme of the system and the color of the icons.
                Priorities:
                1. If color_icons=True, always color icons.
                2. Special styles (for example, WindowsVista)
                3. System theme (Dark/Light)
        """
        #self.app = QGuiApplication.instance()
        if not self.app:
            return "unknown"

        # Priority 1: Forced color icons
        if getattr(self, 'color_icons', False):
            self.ICON_COLOR_FOLDER = "color"
            return "color_theme"  # Special value for color mode

        current_style = self.app.style().name().lower()

        # Priority 2: Special styles
        SPECIAL_STYLES = {
            "windowsvista": ("black", "vista"),
            #"windows": ("black", "legacy"),
            "motif": ("black", "motif")
        }

        if current_style in SPECIAL_STYLES:
            self.ICON_COLOR_FOLDER, theme_name = SPECIAL_STYLES[current_style]
            return theme_name

        # Priority 3: System Theme
        scheme = self.app.styleHints().colorScheme()
        if scheme == Qt.ColorScheme.Dark:
            self.ICON_COLOR_FOLDER = "white"
            return "dark"

        # All other cases (Light/Unknown)
        self.ICON_COLOR_FOLDER = "black"
        return "light"

    def get_color_scheme(self):
        """Returns actual system theme without any overrides"""
        #self.app = QGuiApplication.instance()
        if not self.app:
            return "unknown"

        current_style = self.app.style().name().lower()

        if current_style == "windowsvista":
            return "light"
        elif current_style == "motif":
            return "light"

        scheme = self.app.styleHints().colorScheme()
        if scheme == Qt.ColorScheme.Dark:
            return "dark"
        elif scheme == Qt.ColorScheme.Light:
            return "light"
        else:
            return "unknown"

    def get_icon(self, icon_name):
        """Dynamically loads the icon based on the current theme."""
        icon_path = os.path.join(
            resources.RESOURCES_DIRECTORY,
            "icons",
            self.ICON_COLOR_FOLDER,
            f"{icon_name}.svg"
        )
        return QIcon(icon_path)

    def timerEvent(self, a0: QTimerEvent | None) -> None:
        """Timer event"""
        if not self.isVisible():
            return
        if self.settings_update_state:
            self.settings.updateSettings()

        self.frame = (self.frame + 1) % 60

        if self.frame == 0:
            self.get_system_theme()
            # print(self.theme)

        if self.frame % 6 == 0:
            self.fullscreen_controller.check_fullscreen()

        self.input_handler.checkCursor()
        self._update_overlay_position()

        # Test canvas opacity
        #self.total_radius += self.radius_per_frame
        #v = abs(math.cos(self.total_radius))
        # change opacity
        #self.canvas.SetOutputOpacity(v)

        cursor = QCursor.pos()

        local_x = cursor.x() - self.x()
        local_y = cursor.y() - self.y()

        # Check idle_animation
        self.idle_anim = self.character.tired_controller.should_enable_idle_anim()

        if self.idle_switch and self.idle_anim:
            current_time = time.monotonic()
            self.animation_manager.update_idle(current_time)

        if not self.first_run:
            self.talk_widget.change_talk_widget_side()

        if self.isInL2DArea(local_x, local_y):
            self.isInLA = True
            self.clickInLA = True

            # Check on_mouse_animation
            self.on_mouse_anim = self.character.tired_controller.should_enable_mouse_anim()

            if self.on_mouse_anim and self.on_mouse_switch == True:
                self.animation_manager.play_animation(
                    anim_type='RandomMotion',
                    group_or_id="OnMouse",
                    priority=live2d.MotionPriority.NORMAL
                )
                self.on_mouse_anim = True

            if self.l2d_area_log:
                print("in l2d area")
        else:
            self.isInLA = False
            self.clickInLA = False
            if self.l2d_area_log:
                print("out of l2d area")
        self.update()

    def isInL2DArea(self, click_x, click_y):
        """Mouse in model area"""
        h = self.height()
        alpha = gl.glReadPixels(click_x * self.systemScale, (h - click_y) * self.systemScale, 1, 1, gl.GL_RGBA,
                                gl.GL_UNSIGNED_BYTE)[3]
        return alpha > 0

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handling mouse button press"""
        if event.button() == Qt.LeftButton and not self.input_handler.input_lock:
            x, y = event.scenePosition().x(), event.scenePosition().y()
            self.posX, self.posY = event.scenePosition().x(), event.scenePosition().y()
            self.input_handler.start_pos = event.scenePosition()
            if not self.clickInLA:
                pass
                #self.input_handler.set_transparent_input()
            if self.isInL2DArea(x, y):
                self.clickInLA = True
                self.clickX, self.clickY = x, y
                # self.audio_manager.play_audio("Neptune", "default", True)
                # Get Params from model
                if self.show_model_params:
                    partIds = self.model.GetParameterIds()
                    print(partIds)
                self.input_handler.mouse_press_handler()
                if self.mouse_click_log:
                    print("Left Button Pressed")

    def mouseReleaseEvent(self, event):
        """Handling mouse button release"""
        if event.button() != Qt.LeftButton or self.input_handler.input_lock:
            return

        pos = event.scenePosition()
        self.posX, self.posY = pos.x(), pos.y()

        self.input_handler.mouse_release_handler()

        self.position_window_controller.save_window_position()

        if self.mouse_click_log:
            print("Left Button Released")

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Mouse mouse move event"""
        if event.buttons() & Qt.RightButton:
            return
        if self.clickInLA and not self.input_handler.input_lock:
            global_pos = event.globalPosition().toPoint()
            self.move(global_pos.x() - self.clickX - 10,
                      global_pos.y() - self.clickY - 10)

        self.input_handler.mouse_move_handler(event.globalPosition())

    def setSettings(self, flags: Qt.WindowType, update_model = False) -> None:
        """Set Settings from Settings Window"""
        if self.talk_widget:
            self.talk_widget.close_dialog_after_animation()

        self.hide()
        self.setWindowFlags(flags | Qt.WindowType.WindowCloseButtonHint | Qt.WindowType.WindowMinimizeButtonHint)

        windowType = flags & Qt.WindowType.WindowType_Mask

        text = windowType.name

        for hintFlag in self.hintFlags:
            if flags & hintFlag:
                text += f"\n| Qt.{hintFlag.name}"

        self.show()

        need_update = False

        if self.auto_scale_init:
            if self.auto_scale:
                self.a_scale = self.app_config.get_auto_scale(
                    int(self.sc_height_size)
                )
            else:
                self.a_scale = 1

            need_update = True

        if not self.frameless:
            self.clamp_window_size_to_screen()
            need_update = True

        if need_update and update_model:
            self.models_manager.update_model(self)
            self.position_window_controller.save_window_position(reset=True)

        self.auto_scale_init = True

        self.setLanguage()
        self.set_theme()
        self.apply_character_config(self.character_name)
        if update_model:
            self.position_window_controller.position_window(ignore_saved_position=True)
        self.models_window.set_language()

    def settings_show(self):
        """Show Settings Window"""
        self.settings.show()
        self.settings_update_state = True

    def settings_close(self):
        """Close Settings Window"""
        self.settings.close()
        self.settings_update_state = False

    def models_window_show(self):
        self.models_window.show()

    def models_window_close(self):
        self.models_window.hide()

    # Context Menu
    def contextMenuEvent(self, e):
        """Context Menu Event with Overlay"""
        if self.context_menu_overlay:
            self.context_menu_overlay.close()
        self.context_menu_overlay = ContextMenuOverlay(self, win=self)
        self._build_context_menu(self.context_menu_overlay)
        self.context_menu_overlay.show_at_position(e.globalPos())

    def _build_context_menu(self, context_menu: QMenu):
        # File menu
        #file_menu = QMenu(self.get_icon("file"), self.lang['Actions']['File'], context_menu)
        #context_menu.addMenu(file_menu)

        # Window Submenu
        #submenu_window = QMenu(self.get_icon("window"), self.lang['Actions']['Window'], context_menu)
        #action_minimize = submenu_window.addAction(self.get_icon("window_min"), self.lang['Actions']['Minimize'])
        #action_minimize.triggered.connect(self.showMinimized)
        #action_normal = submenu_window.addAction(self.get_icon("window_restore"), self.lang['Actions']['Normal'])
        #action_normal.triggered.connect(self.showNormal)
        #context_menu.addMenu(submenu_window)
        #context_menu.addSeparator()

        # Sing Song Action
        sing_song_action = QAction(self.get_icon("song"), self.lang['Actions']['SingSong'], context_menu)
        if not self.input_handler.input_lock:
            sing_song_action.triggered.connect(self.character.state.set_sing_song_state)
        if self.current_sing_song:
            context_menu.addAction(sing_song_action)
            context_menu.addSeparator()

        # Transform Action
        transform_action = QAction(self.get_icon("transform"), self.lang['Actions']['Transform'], context_menu)
        if not self.input_handler.input_lock:
            transform_action.triggered.connect(self.character.state.set_transform_state)
        context_menu.addAction(transform_action)
        context_menu.addSeparator()

        # Model Changer Action
        set_characters_action = QAction(self.get_icon("character"), self.lang['Actions']['Characters'], context_menu)
        if not self.input_handler.input_lock:
            set_characters_action.triggered.connect(self.models_window_show)
        context_menu.addAction(set_characters_action)
        context_menu.addSeparator()

        # Settings Action
        settings_action = QAction(self.get_icon("settings"), self.lang['Actions']['Settings'], context_menu)
        if not self.input_handler.input_lock:
            settings_action.triggered.connect(self.settings_show)
        context_menu.addAction(settings_action)
        context_menu.addSeparator()

        # About Action
        about_action = QAction(self.get_icon("about"), self.lang['Actions']['About'], context_menu)
        about_action.triggered.connect(self.about)
        context_menu.addAction(about_action)
        context_menu.addSeparator()

        # Exit Action
        exit_action = QAction(self.get_icon("exit"), self.lang['Actions']['Quit'], context_menu)
        if not self.input_handler.input_lock:
            exit_action.triggered.connect(self.close)
        context_menu.addAction(exit_action)

        context_menu.aboutToHide.connect(self._on_context_menu_closed)

    def _on_context_menu_closed(self):
        if self.context_menu_overlay:
            self.context_menu_overlay.deleteLater()
            self.context_menu_overlay = None

    def about(self):
        self.context_menu_overlay.context_menu_close()
        about_box = QMessageBox(self)
        about_box.setWindowTitle(self.lang['Actions']['AboutAlt'])
        about_box.setText(f"My Little Neptune\n{self.lang['Actions']['Version']}{self.version}\n{self.lang['Actions']['AboutText']}")
        about_box.setIcon(QMessageBox.Icon.Information)

        pixmap = QPixmap(self.resource_manager.load_msg_box_image("about")).scaled(
            128, 128,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        about_box.setIconPixmap(pixmap)
        about_box.setStandardButtons(QMessageBox.StandardButton.Ok)

        about_box.exec()

    @staticmethod
    def show_question_with_timer(
            parent,
            title: str,
            question: str,
            timeout_seconds: int = 10,
            default_button: QMessageBox.StandardButton = QMessageBox.StandardButton.No,
            custom_timeout_message: str = None,
            cancel_button=False,
            color_start=None,
            color_end=None,
            bg_color=None,
            icon_path=None,
            custom_image_path=None
    ) -> QMessageBox.StandardButton:
        """
        Shows a dialog with an auto-response timer

        Args:
            parent: parent widget
            title: dialog title
            question: question text
            timeout_seconds: time until auto-response (seconds)
            default_button: button that will be pressed automatically
            custom_timeout_message: custom timeout message (if None, default is used)
            cancel_button: additional cancel button(if None, not used),
            color_start= set custom color for progress bar(if None, used system color),
            color_end=set custom color for progress bar(if None, used system color),
            bg_color=set custom color for progress bar(if None, used system color),
            icon_path=custom icon for message box(if None, default is used),
            custom_image_path=custom image for message box(if None, default is used)

        Returns:
            the pressed button (or default_button on timeout)
        """

        if cancel_button:
            msg_box = QMessageBox(
                QMessageBox.Icon.Question,
                title,
                question,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                parent
            )
        else:
            msg_box = QMessageBox(
                QMessageBox.Icon.Question,
                title,
                question,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                parent
            )

        if custom_image_path:
            pixmap = QPixmap(custom_image_path).scaled(128, 128,
                                                       Qt.AspectRatioMode.KeepAspectRatio,
                                                       Qt.TransformationMode.SmoothTransformation)
            msg_box.setIconPixmap(pixmap)
        elif icon_path:
            msg_box.setIconPixmap(QPixmap(icon_path))

        if hasattr(parent, 'mainWindow') and parent.mainWindow and hasattr(parent.mainWindow, 'lang'):
            button_text = parent.mainWindow.lang["Buttons"]
        elif hasattr(parent, 'win') and parent.win and hasattr(parent.win, 'lang'):
            button_text = parent.win.lang["Buttons"]
        elif hasattr(parent, 'lang'):
            button_text = parent.lang["Buttons"]
        else:
            button_text = {"Yes": "Yes", "No": "No", "Cancel": "Cancel"}

        yes_button = msg_box.button(QMessageBox.StandardButton.Yes)
        yes_button.setText(button_text["Yes"])

        no_button = msg_box.button(QMessageBox.StandardButton.No)
        no_button.setText(button_text["No"])

        if cancel_button:
            cancel_button = msg_box.button(QMessageBox.StandardButton.Cancel)
            cancel_button.setText(button_text["Cancel"])

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 10, 0, 0)

        progress_bar = QProgressBar()
        progress_bar.setRange(0, 10)
        progress_bar.setValue(10)
        progress_bar.setFormat("%v sec")
        progress_bar.setRange(0, timeout_seconds)
        progress_bar.setValue(timeout_seconds)
        progress_bar.setTextVisible(False)
        progress_bar.setFixedHeight(6)
        text_color = "#FF6B6B"

        if color_start and color_end:
            style = """
                        QProgressBar {{
                            border: none;
                            border-radius: 3px;
                            background-color: {bg_color};
                        }}
                        QProgressBar::chunk {{
                            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 {color_start}, stop:1 {color_end});
                            border-radius: 3px;
                        }}
                    """.format(bg_color=bg_color,
                               color_start=color_start,
                               color_end=color_end)
            text_color = color_start
        else:
            palette = QApplication.palette()
            accent_color = palette.color(QPalette.ColorRole.Highlight)

            # Создаём градиент на основе акцентного цвета
            lighter_accent = accent_color.lighter(120)
            style = """
                        QProgressBar {{
                            border: none;
                            border-radius: 3px;
                            background-color: {bg_color};
                        }}
                        QProgressBar::chunk {{
                            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 {color_start}, stop:1 {color_end});
                            border-radius: 3px;
                        }}
                    """.format(bg_color=accent_color.lighter(220).name(),
                               color_start=accent_color.name(),
                               color_end=lighter_accent.name())
            text_color = accent_color.name()

        progress_bar.setStyleSheet(style)

        timer_label = QLabel()
        timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timer_label.setStyleSheet(f"color: {text_color}; margin-top: 5px; font-weight: bold;")

        container_layout.addWidget(progress_bar)
        container_layout.addWidget(timer_label)

        layout = msg_box.layout()
        if layout:
            layout.addWidget(container, layout.rowCount(), 0, 1, layout.columnCount())

        time_left = timeout_seconds

        def update_timer():
            nonlocal time_left
            time_left -= 1
            progress_bar.setValue(time_left)

            if custom_timeout_message:
                timer_label.setText(custom_timeout_message.format(seconds=time_left))
            else:
                timer_label.setText(f"⏱️ Automatic closing via {time_left} sec.")

            if time_left <= 0:
                timer.stop()
                msg_box.done(default_button)

        timer = QTimer()
        timer.timeout.connect(update_timer)
        timer.start(1000)

        if custom_timeout_message:
            timer_label.setText(custom_timeout_message.format(seconds=timeout_seconds))
        else:
            timer_label.setText(f"⏱️ Automatic closing via {timeout_seconds} sec.")

        reply = msg_box.exec()

        if timer.isActive():
            timer.stop()

        return reply

    def closeEvent(self, event):
        if hasattr(self, 'quit_box_active') and self.quit_box_active:
            event.accept()
            return

        if self.character.tired_state.condition == "Sleep":
            self.character.tired_controller.wake_up_function()

        self.models_window.close()
        self.settings_close()

        if event.spontaneous():
            # QApplication.quit()
            sys.exit(0)
            #self.character.state.set_quit_state(quit='Yes')
            event.accept()
        else:
            self.show_quit_dialog()
            event.ignore()

    def show_quit_dialog(self):
        """Show quit dialog"""
        self.context_menu_overlay.context_menu_close()
        self.character.expressions.set_cry_expression()
        self.character.audio.set_really_quit_audio()
        self.kaomoji = "(o;TωT)o"
        self.quit_box_active = True

        answer = self.show_question_with_timer(
            parent=self,
            title=self.lang['Actions']['Quit'],
            question=f"{self.lang['Talk']['Quit']} {self.kaomoji}",
            timeout_seconds=10,
            default_button=QMessageBox.StandardButton.Yes,
            custom_timeout_message=f"⏱️ {self.lang['Settings']['AutoCloseMessage']}",
            custom_image_path=self.resource_manager.load_msg_box_image("quit")
        )

        if answer == QMessageBox.StandardButton.Yes:
            self.character.state.set_quit_state(quit='Yes')
            # QApplication.quit()
        else:
            self.character.tired_controller.timer_count = 1
            self.character.state.set_quit_state(quit='No')
        self.quit_box_active = False
