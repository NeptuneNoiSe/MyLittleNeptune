import math
import os
import time
import OpenGL.GL as gl
from PySide6.QtCore import QTimerEvent, Qt, Slot, QSize
from PySide6.QtGui import QMouseEvent, QCursor, QScreen, QSurfaceFormat, QAction, QIcon, QPixmap, QFont
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QMenu, QMessageBox, QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, \
    QGroupBox, QGridLayout, QCheckBox, QDoubleSpinBox, QComboBox, QStyleFactory, QTabWidget, QDialogButtonBox, QDial, \
    QFrame
from PySide6.QtGui import QGuiApplication

import live2d.v3 as live2d
from live2d.utils.canvas import Canvas
from live2d.utils.lipsync import WavHandler
# from live2d.v3 import StandardParams
# import live2d.v2 as live2d

from widgets.talk_widget import TalkWidget
from additional.config_manager import AppConfig
from additional.models_manager import ModelsManager
from additional.character_manager import CharacterManager
from additional.action_handler import ActionHandler
from additional.functions import Functions
from additional.functions import PowerOfTwoSpinBox
from additional.input_handler import InputHandler
from additional.input_handler import MouseTracker
from additional.resource_manager import ResourceManager
from package.additional.animation_manager import AnimationsManager
from package.additional.image_manager import ImageManager
from package.additional.event_manager import EventManager
from package.additional.audio_manager import AudioManager

class MainWindow(QOpenGLWidget):
    def __init__(self) -> None:
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

        # Set False if you want use model.Draw()
        self.canvas_draw = True

        # Initialize functions
        self._init_window_flags()

        self._init_config()

        self._init_vars()

        self._init_ui()

        self._init_window_geometry()

        self._init_model_params()

        self._resize_model()

        self.position_window()

        self._position_widget()

        self._init_animations()

        self._init_sound()

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

    def _init_vars(self):
        """Initialize Main Vars"""
        # Icons Vars
        self.ICON_COLOR_FOLDER = "black"
        self.color_icons = True

        # Geometry and positioning
        self.auto_scale_init = False
        self.w_correction = 0
        self.h_correction = 0
        self.a_scale = 1
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
        self.model_move = False
        self.talk = True
        self.reset_expression = True
        self.frameless = False
        self.background = False
        self.background_available = False
        self.first_run=True

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
        self.action_handler = ActionHandler(self)
        self.model: live2d.Model | None = None
        self.canvas: Canvas | None = None
        self.character = None
        self.talk_widget = None
        self.functions = Functions(self, self.model)
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

            self.mx_param = self.app_config.mx_param  # Через property
            self.my_param = self.app_config.my_param

            scale_factor = self.a_scale * self.models_scale
            self.w_res = int(self.mx_param * scale_factor)
            self.h_res = int(self.my_param * scale_factor)

            # Updating the remaining parameters
            self.app_config.update_model_params(
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
        self.resize(int(self.w_resize), int(self.h_resize))
        self.w_correction = self.app_config.w_correction
        self.h_correction = self.app_config.h_correction

    def position_window(self):
        """Set window position with conditions"""
        window_width = self.width()
        window_height = self.height()
        screen_geom = self.screen().availableGeometry()

        # Checking that the model is SMALLER or EQUAL to the screen size
        if (window_width <= screen_geom.width() and
                window_height <= screen_geom.height()):

            if self.frameless and not self.background:
                self.frmX = (self.SrcSize.width() - window_width) - self.w_correction
            else:
                self.frmX = (self.SrcSize.width() - window_width)

            self.frmY = (self.SrcSize.height() - window_height) - self.h_correction

            self.move(int(self.frmX), int(self.frmY))

        else:
            # Defensive logic for large models
            if window_width > screen_geom.width():
                safe_x = screen_geom.left() - (window_width - screen_geom.width()) // 2
            else:
                safe_x = (self.SrcSize.width() - window_width) - self.w_correction

            # Fix the upper limit, allow going beyond the bottom
            safe_y = max(screen_geom.top(),
                         (self.SrcSize.height() - window_height) - self.h_correction)

            self.move(int(safe_x), int(safe_y))

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

        self.lastUpdateTime = time.time()

    def _init_sound(self):
        """Initialize sound"""
        self.wavHandler = WavHandler()
        self.lipSyncN = 3
        #self.audioPlayed = False

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
        self.functions.setLanguage()
        self.model.CreateRenderer(2)
        self.canvas.SetOutputOpacity(0)
        self.init_classes()
        self.init_logs()
        self.last_update_time = time.time()
        self.character = CharacterManager(self)
        self.talk_widget = TalkWidget(self)
        self.talk_widget.show_talk()
        self.character.state.set_greeting_state(is_first_run=True)
        self.input_handler.input_lock = True
        self.first_run = False

    def init_classes(self):
        """Initialize classes"""
        self.event_manager = EventManager(self)
        self.animation_manager = AnimationsManager(self, self.model)
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

    def on_draw(self):
        """Canvas draw method"""
        live2d.clearBuffer(self.b_red, self.b_green, self.b_blue, self.b_alpha)
        if self.background:
            self.image_manager.set_background_image(self.background_name)
        self.model.Draw()
        if self.background:
            self.event_manager.draw_text_on_model()

    def paintGL(self) -> None:
        """Paint GL"""
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
            ct = time.time()
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
            self.functions.savePng('screenshot.png')
            self.read = True

    def set_app_title(self):
        """Set app title and icon"""
        self.setWindowTitle("My Little Neptune")
        self.setWindowIcon(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/nep_main.ico")))

    def set_theme(self):
        """Set app theme"""
        #app.setStyle(self.theme if self.theme != "Default" else "")  # Default = empty line
        style_key = self.display_to_style.get(self.theme, "")  # if theme on a dictionary → Default ("")

        # 2. Set Style
        if style_key:
            app.setStyle(QStyleFactory.create(style_key))  # For Windows 11, Fusion and more.
        else:
            app.setStyle("")  # System Style (Default)

    def get_system_theme(self):
        """
        Defines the theme of the system and the color of the icons.
                Priorities:
                1. If color_icons=True, always color icons.
                2. Special styles (for example, WindowsVista)
                3. System theme (Dark/Light)
        """
        app = QGuiApplication.instance()
        if not app:
            return "unknown"

        # Priority 1: Forced color icons
        if getattr(self, 'color_icons', False):
            self.ICON_COLOR_FOLDER = "color"
            return "color_theme"  # Special value for color mode

        current_style = app.style().name().lower()

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
        scheme = app.styleHints().colorScheme()
        if scheme == Qt.ColorScheme.Dark:
            self.ICON_COLOR_FOLDER = "white"
            return "dark"

        # All other cases (Light/Unknown)
        self.ICON_COLOR_FOLDER = "black"
        return "light"

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
            settings.updateSettings()

        # Check current system color scheme
        self.get_system_theme()

        # Test canvas opacity
        #self.total_radius += self.radius_per_frame
        #v = abs(math.cos(self.total_radius))
        # change opacity
        #self.canvas.SetOutputOpacity(v)
        #print(self.theme)

        local_x, local_y = QCursor.pos().x() - self.x(), QCursor.pos().y() - self.y()
        # Tired Timer check
        # Check idle_animation
        self.idle_anim = self.character.tired_controller.should_enable_idle_anim()

        if self.idle_switch and self.idle_anim:
            current_time = time.time()
            self.animation_manager.update_idle(current_time)

        self.talk_widget.change_talk_widget_side()

        if self.isInL2DArea(local_x, local_y):
            self.isInLA = True
            self.clickInLA = True

            # Check on_mouse_animation
            self.on_mouse_anim = self.character.tired_controller.should_enable_mouse_anim()

            if self.on_mouse_anim and self.on_mouse_switch == True:
                self.animation_manager.play_animation(
                    model=self.model,
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
                self.input_handler.set_transparent_input()
            if self.isInL2DArea(x, y):
                self.clickInLA = True
                self.clickX, self.clickY = x, y
                # self.audio_manager.play_audio("Neptune", "default", True)
                # Get Params from model
                # partIds = self.model.GetParameterIds()
                # print(partIds)
                self.input_handler.mouse_press_handler()
                if self.mouse_click_log:
                    print("Left Button Pressed")

    def mouseReleaseEvent(self, event):
        """Handling mouse button release"""
        if event.button() != Qt.LeftButton or self.input_handler.input_lock:
            return

        # Fixing the release position
        pos = event.scenePosition()
        self.posX, self.posY = pos.x(), pos.y()

        # Processing actions in the LA
        #if self.isInLA:
        self.input_handler.mouse_release_handler()

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

    def setSettings(self, flags: Qt.WindowType) -> None:
        """Set Settings from Settings Window"""
        # print(f"setSettings flags: {flags}")
        self.setWindowFlags(flags)

        windowType = flags & Qt.WindowType.WindowType_Mask

        text = windowType.name

        for hintFlag in self.hintFlags:
            if flags & hintFlag:
                text += f"\n| Qt.{hintFlag.name}"

        if self.auto_scale and self.auto_scale_init:
            self.a_scale = self.app_config.get_auto_scale(int(self.sc_height_size))
            self.models_manager.update_model(self)

        if not self.auto_scale and self.auto_scale_init:
            self.a_scale = 1
            self.models_manager.update_model(self)

        self.auto_scale_init = True

        self.functions.setLanguage()
        self.set_theme()
        # if self.talk_update:
        self.apply_character_config(self.character_name)

    def settings_show(self):
        """Show Settings Window"""
        settings.show()
        self.settings_update_state = True

    def settings_close(self):
        """Close Settings Window"""
        settings.close()
        self.settings_update_state = False

    # Context Menu
    def contextMenuEvent(self, e):
        """Context Menu Event"""
        context_menu = QMenu(self).addMenu('&File')

        # Window Submenu
        submenu_window = QMenu(self).addMenu(self.get_icon("window"), self.lang['Actions']['Window'])
        action_minimize = submenu_window.addAction(self.get_icon("window_min"), self.lang['Actions']['Minimize'])
        action_minimize.triggered.connect(self.action_handler.on_action_minimize)
        action_normal = submenu_window.addAction(self.get_icon("window_restore"), self.lang['Actions']['Normal'])
        action_normal.triggered.connect(self.action_handler.on_action_normal)
        context_menu.addMenu(submenu_window)
        context_menu.addSeparator()

        # Sing Song Action
        sing_song_action = QAction(self.get_icon("song"), self.lang['Actions']['SingSong'], self)
        if not self.input_handler.input_lock:
            sing_song_action.triggered.connect(self.action_handler.on_action_sing_song)
        if self.current_sing_song:
            context_menu.addAction(sing_song_action)
            context_menu.addSeparator()

        # Transform Action
        transform_action = QAction(self.get_icon("transform"), self.lang['Actions']['Transform'], self)
        if not self.input_handler.input_lock:
            transform_action.triggered.connect(self.action_handler.on_action_transform)
        context_menu.addAction(transform_action)
        context_menu.addSeparator()

        # Character Submenu
        submenu_character = QMenu(self).addMenu(self.get_icon("character"), self.lang['Actions']['Characters'])
        # Neptune
        action_neptune = submenu_character.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/characters/neptune.ico")), self.lang['NamesActions']['Neptune'])
        if not self.input_handler.input_lock:
            action_neptune.triggered.connect(self.action_handler.on_action_neptune)
        # Purple Heart
        action_purple_heart = submenu_character.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/characters/purple_heart.ico")), self.lang['NamesActions']['PurpleHeart'])
        if not self.input_handler.input_lock:
            action_purple_heart.triggered.connect(self.action_handler.on_action_purple_heart)
        # Noire
        action_noire = submenu_character.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/characters/noire.ico")), self.lang['NamesActions']['Noire'])
        if not self.input_handler.input_lock:
            action_noire.triggered.connect(self.action_handler.on_action_noire)
        # Black Heart
        action_black_heart = submenu_character.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/characters/black_heart.ico")), self.lang['NamesActions']['BlackHeart'])
        if not self.input_handler.input_lock:
            action_black_heart.triggered.connect(self.action_handler.on_action_black_heart)
        # Blanc
        action_blanc = submenu_character.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/characters/blanc.ico")), self.lang['NamesActions']['Blanc'])
        if not self.input_handler.input_lock:
            action_blanc.triggered.connect(self.action_handler.on_action_blanc)
        # White Heart
        action_white_heart = submenu_character.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/characters/white_heart.ico")), self.lang['NamesActions']['WhiteHeart'])
        if not self.input_handler.input_lock:
            action_white_heart.triggered.connect(self.action_handler.on_action_white_heart)
        # Vert
        action_vert = submenu_character.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/characters/vert.ico")), self.lang['NamesActions']['Vert'])
        if not self.input_handler.input_lock:
            action_vert.triggered.connect(self.action_handler.on_action_vert)
        # Green Heart
        action_green_heart = submenu_character.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/characters/green_heart.ico")), self.lang['NamesActions']['GreenHeart'])
        if not self.input_handler.input_lock:
            action_green_heart.triggered.connect(self.action_handler.on_action_green_heart)
        # NepGear
        action_nepgear = submenu_character.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/characters/nepgear.ico")), self.lang['NamesActions']['NepGear'])
        if not self.input_handler.input_lock:
            action_nepgear.triggered.connect(self.action_handler.on_action_nepgear)
        # Purple Sister
        action_purple_sister = submenu_character.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/characters/purple_sister.ico")), self.lang['NamesActions']['PurpleSister'])
        if not self.input_handler.input_lock:
            action_purple_sister.triggered.connect(self.action_handler.on_action_purple_sister)
        # Uni
        action_uni = submenu_character.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/characters/uni.ico")), self.lang['NamesActions']['Uni'])
        if not self.input_handler.input_lock:
            action_uni.triggered.connect(self.action_handler.on_action_uni)
        # Black Sister
        action_black_sister = submenu_character.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/characters/black_sister.ico")), self.lang['NamesActions']['BlackSister'])
        if not self.input_handler.input_lock:
            action_black_sister.triggered.connect(self.action_handler.on_action_black_sister)
        # Rom
        action_rom = submenu_character.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/characters/rom.ico")), self.lang['NamesActions']['Rom'])
        if not self.input_handler.input_lock:
            action_rom.triggered.connect(self.action_handler.on_action_rom)
        # White Sister Rom
        action_white_sister_rom = submenu_character.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/characters/white_sister_rom.ico")), self.lang['NamesActions']['WhiteSisterRom'])
        if not self.input_handler.input_lock:
            action_white_sister_rom.triggered.connect(self.action_handler.on_action_white_sister_rom)
        # Ram
        action_ram = submenu_character.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/characters/ram.ico")), self.lang['NamesActions']['Ram'])
        if not self.input_handler.input_lock:
            action_ram.triggered.connect(self.action_handler.on_action_ram)
        # White Sister Ram
        action_white_sister_ram = submenu_character.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/characters/white_sister_ram.ico")), self.lang['NamesActions']['WhiteSisterRam'])
        if not self.input_handler.input_lock:
            action_white_sister_ram.triggered.connect(self.action_handler.on_action_white_sister_ram)
        # Histoire
        action_histoire = submenu_character.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/characters/histoire.ico")), self.lang['NamesActions']['Histoire'])
        if not self.input_handler.input_lock:
            action_histoire.triggered.connect(self.action_handler.on_action_histoire)
        # Maho
        action_maho = submenu_character.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/characters/maho.ico")), self.lang['NamesActions']['Maho'])
        if not self.input_handler.input_lock:
            action_maho.triggered.connect(self.action_handler.on_action_maho)
        # Grey Sister
        action_grey_sister = submenu_character.addAction(QIcon(os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/characters/grey_sister.ico")), self.lang['NamesActions']['GreySister'])
        if not self.input_handler.input_lock:
            action_grey_sister.triggered.connect(self.action_handler.on_action_grey_sister)

        context_menu.addMenu(submenu_character)

        # Settings Action
        settings_action = QAction(self.get_icon("settings"), self.lang['Actions']['Settings'], self)
        if not self.input_handler.input_lock:
            settings_action.triggered.connect(self.action_handler.on_action_settings)
        context_menu.addAction(settings_action)
        context_menu.addSeparator()

        # About Action
        about_action = QAction(self.get_icon("about"), self.lang['Actions']['About'], self)
        about_action.triggered.connect(self.action_handler.on_action_about)
        context_menu.addAction(about_action)

        # Exit Action
        exit_action = QAction(self.get_icon("exit"), self.lang['Actions']['Quit'], self)
        if not self.input_handler.input_lock:
            exit_action.triggered.connect(self.action_handler.on_action_quit)
        context_menu.addAction(exit_action)

        context_menu.exec(e.globalPos())

    def closeEvent(self, event):
        """Close Event"""
        self.character.state.set_crying_state()
        self.character.audio.set_really_quit_audio()
        settings.close()
        if self.character.tired_state.condition == "Sleep":
            self.character.tired_controller.wake_up_function()
        self.kaomoji = "(o;TωT)o"
        answer = QMessageBox.question(self,
                                      self.lang['Actions']['Quit'],
                                      self.name + ": " + self.lang['Talk']['Quit'] + " " + self.kaomoji,
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                      QMessageBox.StandardButton.No)
        if answer == QMessageBox.StandardButton.Yes:
            event.accept()
            self.kaomoji = "(^3^)"
        else:
            self.character.tired_controller.timer_count = 1
            self.character.state.set_quit_state(quit='No')
            event.ignore()

class SettingsWindow(QWidget):
    """Settings Window Class"""
    def __init__(self, pythonic_window_registration: bool = False):
        super().__init__()
        self.pythonic_reg = pythonic_window_registration
        self.mainWindow = MainWindow()
        self.app_config = self.mainWindow.app_config
        self.settings_log= False

        # Flag for tracking changes
        self.unsaved_changes = False

        self.available_styles = self.get_available_styles()

        # Set fixed window size
        self.setMinimumHeight(440)
        self.setMaximumHeight(440)
        self.setMinimumWidth(600)
        self.setMaximumWidth(600)

        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.WindowCloseButtonHint)
        self.getWindowFlag_FramelessWindowHint = self.app_config.FramelessWindowHint
        self.getWindowFlag_WindowStaysOnTopHint = self.app_config.WindowStaysOnTopHint

        self.getWindowFlag_WindowMinimizeButtonHint = self.app_config.WindowMinimizeButtonHint
        self.getWindowFlag_WindowCloseButtonHint = self.app_config.WindowCloseButtonHint
        self.getWindowFlag_WindowStaysOnBottomHint = self.app_config.WindowStaysOnBottomHint
        self.getWindowFlag_WindowTransparentForInput = self.app_config.WindowTransparentForInput
        self.getWindowFlag_WindowType_Mask = self.app_config.WindowType_Mask

        # Init AppConfig vars
        self.language = self.app_config.language
        self.color_icons = self.app_config.color_icons
        self.theme = self.app_config.theme
        self.background = self.app_config.background
        self.auto_scale = self.app_config.auto_scale
        self.models_scale = self.app_config.models_scale
        self.random_character = self.app_config.random_character
        self.random_character_hdd = self.app_config.random_character_hdd
        self.auto_blink = self.app_config.auto_blink
        self.auto_breath = self.app_config.auto_breath
        self.tracking_mouse = self.app_config.tracking_mouse_switch
        self.sleep = self.app_config.sleep_switch
        self.time_scale = self.app_config.time_scale
        self.idle = self.app_config.idle_switch
        self.on_mouse = self.app_config.on_mouse_switch
        self.tap_body = self.app_config.tap_body_switch
        self.audio_system = self.app_config.audio_system
        self.master = self.app_config.master
        self.voice = self.app_config.voice
        self.sfx = self.app_config.sfx
        self.bgm = self.app_config.bgm
        self.ambient = self.app_config.ambient
        self.show_text_widget = self.app_config.show_text_widget
        self.show_name = self.app_config.show_name
        self.show_kaomoji = self.app_config.show_kaomoji

        #Init language
        self.language_set = None
        self.language_get = None

        # Save initial vars
        self.save_initial_values()

        # BLOCKING signals when creating elements
        self.block_signals_during_init = True

        # Creating buttons before creating tabs
        self.create_buttons()

        # Create main layout
        mainLayout = QHBoxLayout()

        # Create Tab Widget
        self.tab_widget = QTabWidget()

        # Create and Add Tabs
        self.create_appearance_tab()
        self.create_model_tab()
        self.create_behavior_tab()
        self.create_audio_tab()
        self.create_other_tab()

        # Add tabs in layout
        mainLayout.addWidget(self.tab_widget)

        # Create GroupBox for right panel
        self.right_group = QGroupBox("Controls")
        self.right_group.setFixedWidth(170)
        self.right_group.setAlignment(Qt.AlignmentFlag.AlignCenter)

        right_panel = QVBoxLayout(self.right_group)

        self.nepMainImage = os.path.join(
            resources.RESOURCES_DIRECTORY, "icons/nep_main.ico")
        self.nepLogoImage = os.path.join(
            resources.RESOURCES_DIRECTORY, "images/nep_logo.svg")

        self.nepImageLabel = QLabel()
        self.nepImageLabel.setPixmap(QPixmap(self.nepMainImage).scaled(QSize(225, 225),
                                                                       Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.nepImageLabel.setAlignment(Qt.AlignCenter)

        # Button fixed size
        button_width = 150

        self.resetPosButton.setFixedWidth(button_width)
        self.quitButton.setFixedWidth(button_width)
        self.apply_button.setFixedWidth(button_width)

        # Setting button_box
        self.button_box.setFixedWidth(button_width)
        self.button_box.setContentsMargins(0, 0, 0, 0)

        right_panel.addWidget(self.nepImageLabel, 0, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        # Stretchable space (the void between the image and the buttons)
        right_panel.addStretch(1)

        # Container for buttons (for grouping)
        buttons_container = QWidget()
        buttons_layout = QVBoxLayout(buttons_container)
        buttons_layout.setSpacing(8)  # The distance between the buttons
        buttons_layout.setContentsMargins(0, 0, 0, 0)

        buttons_layout.addWidget(self.resetPosButton)
        buttons_layout.addWidget(self.button_box)
        buttons_layout.addWidget(self.apply_button)
        buttons_layout.addWidget(self.quitButton)

        # Add button Container
        right_panel.addWidget(buttons_container)

        # A small indentation from the bottom
        right_panel.addSpacing(10)

        mainLayout.addWidget(self.right_group)

        self.setLayout(mainLayout)
        self.setWindowTitle("Settings")
        self.mainWindow.set_app_title()
        self.updateMainWindow()
        # UNBLOCKING the signals after initialization
        self.block_signals_during_init = False

    @property
    def icon_color_folder(self):
        return self.mainWindow.ICON_COLOR_FOLDER

    def save_initial_values(self):
        """Saves the initial settings values"""
        self.initial_values = {
            'frameless_window': self.getWindowFlag_FramelessWindowHint,
            'stays_on_top': self.getWindowFlag_WindowStaysOnTopHint,
            'color_icons': self.color_icons,
            'background': self.background,
            'language': self.language,
            'theme': self.theme,
            'auto_scale': self.auto_scale,
            'models_scale': self.models_scale,
            'random_character': self.random_character,
            'random_character_hdd': self.random_character_hdd,
            'auto_blink': self.auto_blink,
            'auto_breath': self.auto_breath,
            'tracking_mouse': self.tracking_mouse,
            'sleep': self.sleep,
            'time_scale': self.time_scale,
            'idle': self.idle,
            'on_mouse': self.on_mouse,
            'tap_body': self.tap_body,
            'audio_system': self.audio_system,
            'master': self.master,
            'voice': self.voice,
            'sfx': self.sfx,
            'bgm': self.bgm,
            'ambient': self.ambient,
            'show_text_widget': self.show_text_widget,
            'show_name': self.show_name,
            'show_kaomoji': self.show_kaomoji
        }

    def get_current_settings(self):
        """Return the initial settings values"""

        def get_dial_value(category):
            """Auxiliary function for getting the disk value"""
            dial_attr = f"{category}_dial"
            if hasattr(self, dial_attr):
                return getattr(self, dial_attr).value()
            return getattr(self, category, 0)

        return {
            'frameless_window': self.framelessWindowCheckBox.isChecked(),
            'stays_on_top': self.windowStaysOnTopCheckBox.isChecked(),
            'color_icons': self.colorIconsCheckBox.isChecked(),
            'background': self.backgroundImageCheckBox.isChecked(),
            'language': self.langComboBox.currentText(),
            'theme': self.themeComboBox.currentText(),
            'auto_scale': self.autoScaleCheckBox.isChecked(),
            'models_scale': self.modelScaleBox.value(),
            'random_character': self.randomCharacterCheckBox.isChecked(),
            'random_character_hdd': self.randomCharacterHDDCheckBox.isChecked(),
            'auto_blink': self.autoBlinkCheckBox.isChecked(),
            'auto_breath': self.autoBreathCheckBox.isChecked(),
            'tracking_mouse': self.trackingMouseCheckBox.isChecked(),
            'sleep': self.sleepCheckBox.isChecked(),
            'time_scale': self.timeScaleBox.value(),
            'idle': self.idleCheckBox.isChecked(),
            'on_mouse': self.onMouseCheckBox.isChecked(),
            'tap_body': self.tapBodyCheckBox.isChecked(),
            'audio_system': self.audioSystemCheckBox.isChecked(),
            'master': get_dial_value('master'),
            'voice': get_dial_value('voice'),
            'bgm': get_dial_value('bgm'),
            'sfx': get_dial_value('sfx'),
            'ambient': get_dial_value('ambient'),
            'show_text_widget': self.showTextWidgetCheckBox.isChecked(),
            'show_name': self.showNameCheckBox.isChecked(),
            'show_kaomoji': self.showKaomojiCheckBox.isChecked()
        }

    # Create Tabs
    def create_appearance_tab(self):
        """Creates an appearance settings tab"""
        tab = QWidget()
        layout = QGridLayout()

        # Window Flags
        self.framelessWindowCheckBox = QCheckBox("Frameless window")
        self.windowStaysOnTopCheckBox = QCheckBox("Window stays on top")

        # Appearance
        self.langText = QLabel("Language:")


        self.langComboBox = QComboBox()
        self.langComboBox.addItems(["English", "Русский"])
        self.setLanguageName()
        self.langComboBox.setCurrentText(self.language_set)

        self.themeText = QLabel("Theme:")
        self.themeComboBox = QComboBox()
        self.themeComboBox.addItems(self.available_styles)
        self.themeComboBox.setCurrentText(self.theme)

        self.colorIconsCheckBox = QCheckBox("Color icons")

        self.backgroundImageCheckBox = QCheckBox("Background image")

        # Placing the elements
        layout.addWidget(self.framelessWindowCheckBox, 0, 0, 1, 2)
        layout.addWidget(self.windowStaysOnTopCheckBox, 1, 0, 1, 2)
        layout.addWidget(self.langText, 2, 0)
        layout.addWidget(self.langComboBox, 2, 1)
        layout.addWidget(self.themeText, 3, 0)
        layout.addWidget(self.themeComboBox, 3, 1)
        layout.addWidget(self.colorIconsCheckBox, 4, 0, 1, 2)
        layout.addWidget(self.backgroundImageCheckBox, 5, 0, 1, 2)

        # Connecting change signals
        self.framelessWindowCheckBox.stateChanged.connect(self.on_setting_changed)
        self.windowStaysOnTopCheckBox.stateChanged.connect(self.on_setting_changed)
        self.langComboBox.currentTextChanged.connect(self.on_setting_changed)
        self.themeComboBox.currentTextChanged.connect(self.on_setting_changed)
        self.colorIconsCheckBox.stateChanged.connect(self.on_setting_changed)
        self.backgroundImageCheckBox.stateChanged.connect(self.on_setting_changed)

        # Setting the values
        self.framelessWindowCheckBox.setChecked(self.getWindowFlag_FramelessWindowHint)
        self.windowStaysOnTopCheckBox.setChecked(self.getWindowFlag_WindowStaysOnTopHint)
        self.colorIconsCheckBox.setChecked(self.color_icons)
        self.backgroundImageCheckBox.setChecked(self.background)
        self.backgroundImageCheckBox.setEnabled(self.mainWindow.background_available)

        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Appearance")

    def create_model_tab(self):
        """Creates a model settings tab"""
        tab = QWidget()
        layout = QGridLayout()

        self.modelScaleBox = QDoubleSpinBox()
        self.sc_mult_text = QLabel("Scale multiplier:")
        self.modelScaleBox.setMinimum(0.5)
        self.modelScaleBox.setMaximum(5)
        self.modelScaleBox.setSingleStep(0.25)
        self.modelScaleBox.setValue(self.models_scale)

        self.autoScaleCheckBox = QCheckBox("AutoScale")
        self.autoScaleCheckBox.setChecked(self.auto_scale)

        self.randomCharacterCheckBox = QCheckBox("Random Character")
        self.randomCharacterCheckBox.setChecked(self.random_character)

        self.randomCharacterHDDCheckBox = QCheckBox("Random Character With HDD")
        self.randomCharacterHDDCheckBox.setChecked(self.random_character_hdd)
        self.randomCharacterHDDCheckBox.setEnabled(self.random_character)

        # Setting the initial state based on styles
        self.sync_scale_box_with_checkbox()

        layout.addWidget(self.sc_mult_text, 0, 0)
        layout.addWidget(self.modelScaleBox, 0, 1)
        layout.addWidget(self.autoScaleCheckBox, 1, 0, 1, 2)
        layout.addWidget(self.randomCharacterCheckBox, 2, 0, 1, 2)
        layout.addWidget(self.randomCharacterHDDCheckBox, 3, 0, 1, 2)

        # Connecting signals
        self.autoScaleCheckBox.toggled.connect(self.sync_scale_box_with_checkbox)
        self.modelScaleBox.valueChanged.connect(self.on_setting_changed)
        self.randomCharacterCheckBox.stateChanged.connect(self.on_random_hdd_toggled)
        self.randomCharacterHDDCheckBox.toggled.connect(self.on_setting_changed)

        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Model")

    def on_random_hdd_toggled(self):
        """Toggled Random Character HDD Checkbox"""
        is_random_character = self.randomCharacterCheckBox.isChecked()
        if is_random_character:
            self.randomCharacterHDDCheckBox.setEnabled(True)
        else:
            self.randomCharacterHDDCheckBox.setEnabled(False)

        self.on_setting_changed()

    def sync_scale_box_with_checkbox(self):
        """Synchronizes the state of the spinbox with the checkbox"""
        is_auto_scale = self.autoScaleCheckBox.isChecked()

        # Blocking the signals so that setValue does not trigger on_setting_changed
        self.modelScaleBox.blockSignals(True)

        if is_auto_scale:
            # if auto scale on
            self.modelScaleBox.setReadOnly(True)
            self.modelScaleBox.setValue(1.0)

            # Applying a style to an inaccessible field
            if hasattr(self, 'mainWindow') and hasattr(self.mainWindow, 'theme'):
                if self.mainWindow.theme.lower() == 'fusion' or 'dark' in self.mainWindow.theme.lower():
                    # Dark Theme
                    self.modelScaleBox.setStyleSheet("""
                        QDoubleSpinBox:read-only {
                            background-color: #3a3a3a;
                            color: #888888;
                            border: 1px solid #555555;
                            border-radius: 3px;
                            padding: 2px;
                        }
                        QDoubleSpinBox::up-button:read-only, 
                        QDoubleSpinBox::down-button:read-only {
                            background-color: #3a3a3a;
                            border: 1px solid #555555;
                        }
                    """)
                else:
                    # Light Theme
                    self.modelScaleBox.setStyleSheet("""
                        QDoubleSpinBox:read-only {
                            background-color: #f5f5f5;
                            color: #888888;
                            border: 1px solid #cccccc;
                            border-radius: 3px;
                            padding: 2px;
                        }
                        QDoubleSpinBox::up-button:read-only, 
                        QDoubleSpinBox::down-button:read-only {
                            background-color: #f5f5f5;
                            border: 1px solid #cccccc;
                        }
                    """)
        else:
            # If auto scale on
            self.modelScaleBox.setReadOnly(False)
            # Reset Style
            self.modelScaleBox.setStyleSheet("")

        # Unblocking Signals
        self.modelScaleBox.blockSignals(False)

        self.on_setting_changed()

    def create_behavior_tab(self):
        """Creates a behavior settings tab"""
        tab = QWidget()
        layout = QGridLayout()

        self.autoBlinkCheckBox = QCheckBox("Auto Blink")
        self.autoBreathCheckBox = QCheckBox("Auto Breath")
        self.trackingMouseCheckBox = QCheckBox("Tracking Mouse Position")
        self.sleepCheckBox = QCheckBox("Sleep")

        self.timeScaleBox = PowerOfTwoSpinBox()
        self.sc_time_text = QLabel("Time Scale:")
        self.timeScaleBox.setValue(self.time_scale)

        self.idleCheckBox = QCheckBox("Idle")
        self.onMouseCheckBox = QCheckBox("On Mouse")
        self.tapBodyCheckBox = QCheckBox("Tap Body")

        # Settings the values
        self.autoBlinkCheckBox.setChecked(self.auto_blink)
        self.autoBreathCheckBox.setChecked(self.auto_breath)
        self.trackingMouseCheckBox.setChecked(self.tracking_mouse)
        self.sleepCheckBox.setChecked(self.sleep)
        self.idleCheckBox.setChecked(self.idle)
        self.onMouseCheckBox.setChecked(self.on_mouse)
        self.tapBodyCheckBox.setChecked(self.tap_body)

        # Connect change signals
        self.autoBlinkCheckBox.stateChanged.connect(self.on_setting_changed)
        self.autoBreathCheckBox.stateChanged.connect(self.on_setting_changed)
        self.trackingMouseCheckBox.stateChanged.connect(self.on_setting_changed)
        self.sleepCheckBox.stateChanged.connect(self.sync_time_scale_box_with_checkbox)
        self.timeScaleBox.valueChanged.connect(self.on_setting_changed)
        self.idleCheckBox.stateChanged.connect(self.on_setting_changed)
        self.onMouseCheckBox.stateChanged.connect(self.on_setting_changed)
        self.tapBodyCheckBox.stateChanged.connect(self.on_setting_changed)

        # Setting the initial state based on styles
        self.sync_time_scale_box_with_checkbox()

        layout.addWidget(self.autoBlinkCheckBox, 0, 0)
        layout.addWidget(self.autoBreathCheckBox, 1, 0)
        layout.addWidget(self.trackingMouseCheckBox, 2, 0)
        layout.addWidget(self.sleepCheckBox, 3, 0)
        layout.addWidget(self.sc_time_text, 3, 1)
        layout.addWidget(self.timeScaleBox, 3, 2)
        layout.addWidget(self.idleCheckBox, 4, 0)
        layout.addWidget(self.onMouseCheckBox, 5, 0)
        layout.addWidget(self.tapBodyCheckBox, 6, 0)

        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Behavior")

    def sync_time_scale_box_with_checkbox(self):
        """Synchronizes the state of the spinbox with the checkbox"""
        is_sleep = self.sleepCheckBox.isChecked()

        # Blocking the signals so that setValue does not trigger on_setting_changed
        self.timeScaleBox.blockSignals(True)

        if is_sleep:
            # If sleep on
            self.timeScaleBox.setReadOnly(False)
            # Reset Style
            self.timeScaleBox.setStyleSheet("")
        else:
            # if sleep of
            self.timeScaleBox.setReadOnly(True)
            self.timeScaleBox.setValue(1.0)

            # Applying a style to an inaccessible field
            if hasattr(self, 'mainWindow') and hasattr(self.mainWindow, 'theme'):
                if self.mainWindow.theme.lower() == 'fusion' or 'dark' in self.mainWindow.theme.lower():
                    # Dark Theme
                    self.timeScaleBox.setStyleSheet("""
                                    QDoubleSpinBox:read-only {
                                        background-color: #3a3a3a;
                                        color: #888888;
                                        border: 1px solid #555555;
                                        border-radius: 3px;
                                        padding: 2px;
                                    }
                                    QDoubleSpinBox::up-button:read-only, 
                                    QDoubleSpinBox::down-button:read-only {
                                        background-color: #3a3a3a;
                                        border: 1px solid #555555;
                                    }
                                """)
                else:
                    # Light Theme
                    self.timeScaleBox.setStyleSheet("""
                                    QDoubleSpinBox:read-only {
                                        background-color: #f5f5f5;
                                        color: #888888;
                                        border: 1px solid #cccccc;
                                        border-radius: 3px;
                                        padding: 2px;
                                    }
                                    QDoubleSpinBox::up-button:read-only, 
                                    QDoubleSpinBox::down-button:read-only {
                                        background-color: #f5f5f5;
                                        border: 1px solid #cccccc;
                                    }
                                """)


        # Unblocking Signals
        self.timeScaleBox.blockSignals(False)

        self.on_setting_changed()

    def create_audio_tab(self):
        """Creates a sound management tab with QDial"""
        tab = QWidget()
        # Basic layout with minimal margins
        main_layout = QVBoxLayout(tab)
        main_layout.setSpacing(2)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # CheckBox for disabling the audio system
        self.audioSystemCheckBox = QCheckBox("Enable Audio System")
        self.audioSystemCheckBox.setChecked(self.audio_system)
        self.audioSystemCheckBox.setStyleSheet("""
            QCheckBox {
                color: #ffffff;
                font-size: 12px;
                font-weight: bold;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #e84a4a;
                border-radius: 3px;
                background-color: transparent;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #4ae84a;
                border-radius: 3px;
                background-color: #4ae84a;
            }
        """)

        main_layout.addWidget(self.audioSystemCheckBox, 0, Qt.AlignLeft)

        # Add separator bottom checkbox
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.HLine)
        separator1.setFrameShadow(QFrame.Shadow.Sunken)
        separator1.setFixedHeight(1)
        separator1.setStyleSheet("""
            background-color: #4a86e8;
            margin: 5px 20px;
        """)
        main_layout.addWidget(separator1)

        # Main Dial Container with 5 Dials
        self.dials_container = QWidget()
        dials_layout = QHBoxLayout(self.dials_container)
        dials_layout.setSpacing(0)
        dials_layout.setContentsMargins(0, 0, 0, 0)

        # Left Panel (Voice, BGM)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(1)
        left_layout.setAlignment(Qt.AlignCenter)

        # Voice Dial
        voice_widget = self.create_category_dial("voice", 'Voice', 1.0)
        left_layout.addWidget(voice_widget)

        # BGM Dial
        bgm_widget = self.create_category_dial("bgm", 'BGM', 0.6)
        left_layout.addWidget(bgm_widget)

        # Center Panel Master Dial
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)
        center_layout.setSpacing(4)
        center_layout.setAlignment(Qt.AlignCenter)
        center_layout.setContentsMargins(0, 5, 0, 5)

        # Main QDial for master volume
        self.master_dial = QDial()
        self.master_dial.setMinimum(0)
        self.master_dial.setMaximum(100)
        self.master_dial.setValue(self.master)
        self.master_dial.setNotchesVisible(True)
        self.master_dial.setNotchTarget(8.0)
        self.master_dial.setWrapping(False)
        self.master_dial.setFixedSize(100, 100)

        # Stylize Main QDial
        self.update_dial_color(self.master_dial, self.master)

        self.master_label = QLabel("MASTER")
        self.master_label.setAlignment(Qt.AlignCenter)
        master_label_font = QFont()
        master_label_font.setPointSize(11)
        master_label_font.setBold(True)
        self.master_label.setFont(master_label_font)
        self.master_label.setStyleSheet("color: #2c5aa0;")

        # Current Value
        self.master_value_label = QLabel(f"{str(self.master)}%")
        self.master_value_label.setAlignment(Qt.AlignCenter)
        master_value_font = QFont()
        master_value_font.setPointSize(15)
        master_value_font.setBold(True)
        self.master_value_label.setFont(master_value_font)
        self.master_value_label.setStyleSheet("color: #4a86e8;")

        center_layout.addWidget(self.master_label, 0, Qt.AlignCenter)

        center_layout.addWidget(self.master_dial, 0, Qt.AlignCenter)

        center_layout.addWidget(self.master_value_label, 0, Qt.AlignCenter)

        # Right Panel (SFX, Ambient)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(1)
        right_layout.setAlignment(Qt.AlignCenter)

        # SFX dial
        sfx_widget = self.create_category_dial("sfx", 'SFX', 0.9)
        right_layout.addWidget(sfx_widget)

        # Ambient dial
        ambient_widget = self.create_category_dial("ambient", 'Ambient', 0.9)
        right_layout.addWidget(ambient_widget)

        # Add panels in main layout
        dials_layout.addWidget(left_panel)
        dials_layout.addWidget(center_panel)
        dials_layout.addWidget(right_panel)

        # Add container in layout
        main_layout.addWidget(self.dials_container)

        # Add Stretch
        main_layout.addStretch()

        # Control Buttons
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setSpacing(5)
        buttons_layout.setContentsMargins(0, 10, 0, 0)

        # Test Sound Button
        self.test_audio_button = QPushButton("Test Sound")
        self.test_audio_button.setIcon(self.mainWindow.get_icon("audio_test"))
        self.test_audio_button.setFixedSize(100, 30)
        self.test_audio_button.setStyleSheet("""
               QPushButton {
                   background-color: #4a86e8;
                   color: white;
                   border-radius: 5px;
                   padding: 8px;
                   font-weight: bold;
               }
               QPushButton:hover {
                   background-color: #5a96f8;
               }
               QPushButton:disabled {
                   background-color: #666666;
                   color: #aaaaaa;
               }
           """)

        # Reset Button
        self.reset_audio_button = QPushButton(" Reset")
        self.reset_audio_button.setIcon(self.mainWindow.get_icon("reset"))
        self.reset_audio_button.setFixedSize(100, 30)
        self.reset_audio_button.setStyleSheet("""
               QPushButton:disabled {
                   background-color: #666666;
                   color: #aaaaaa;
               }
           """)

        # Button mute/unmute
        self.mute_button = QPushButton(" Mute All")
        self.mute_button.setIcon(self.mainWindow.get_icon("mute"))
        self.mute_button.setFixedSize(100, 30)
        self.is_muted = False
        self.mute_button.setStyleSheet("""
               QPushButton:disabled {
                   background-color: #666666;
                   color: #aaaaaa;
               }
           """)

        # Placing buttons
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.test_audio_button)
        buttons_layout.addWidget(self.reset_audio_button)
        buttons_layout.addWidget(self.mute_button)
        buttons_layout.addStretch()

        # Interface assembly
        # Add Separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        separator2.setStyleSheet("""
               background-color: qlineargradient(
                   x1:0, y1:0, x2:1, y2:0,
                   stop:0 transparent,
                   stop:0.1 #cccccc,
                   stop:0.9 #cccccc,
                   stop:1 transparent
               );
               height: 1px;
               margin: 15px 30px;
           """)
        main_layout.addWidget(separator2)
        main_layout.addWidget(buttons_container)

        # Connect Signals
        self.connect_audio_signals()
        self.audioSystemCheckBox.stateChanged.connect(self.on_audio_system_toggled)

        # init State
        self.on_audio_system_toggled(state = True if self.audioSystemCheckBox.isChecked() else False)

        self.load_audio_dials()

        self.tab_widget.addTab(tab, "Audio")

    def create_other_tab(self):
        """Creates an advanced settings tab"""
        tab = QWidget()
        layout = QGridLayout()

        #info_label = QLabel("Additional settings will be added here.")
        #info_label.setAlignment(Qt.AlignCenter)
        #layout.addWidget(info_label)

        self.showTextWidgetCheckBox = QCheckBox("Show Text Widget")
        self.showNameCheckBox = QCheckBox("Show Name")
        self.showKaomojiCheckBox = QCheckBox("Show Kaomoji")

        self.showTextWidgetCheckBox.setChecked(self.show_text_widget)
        self.showNameCheckBox.setChecked(self.show_name)
        self.showNameCheckBox.setEnabled(self.show_text_widget)
        self.showKaomojiCheckBox.setChecked(self.show_kaomoji)
        self.showKaomojiCheckBox.setEnabled(self.show_text_widget)

        # Connect change signals
        self.showTextWidgetCheckBox.stateChanged.connect(self.on_text_widget_checkbox_toggled)
        self.showNameCheckBox.stateChanged.connect(self.on_setting_changed)
        self.showKaomojiCheckBox.stateChanged.connect(self.on_setting_changed)

        layout.addWidget(self.showTextWidgetCheckBox, 0, 0)
        layout.addWidget(self.showNameCheckBox, 1, 0)
        layout.addWidget(self.showKaomojiCheckBox, 2, 0)

        # Add icons
        self.update_icons()

        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Other")

    def on_text_widget_checkbox_toggled(self):
        """Toggled Text Widget CheckBoxes"""
        is_text_widget = self.showTextWidgetCheckBox.isChecked()
        if is_text_widget:
            self.showNameCheckBox.setEnabled(True)
            self.showKaomojiCheckBox.setEnabled(True)
        else:
            self.showNameCheckBox.setEnabled(False)
            self.showKaomojiCheckBox.setEnabled(False)
        self.on_setting_changed()

    def on_audio_system_toggled(self, state):
        """On/Off audio system"""
        audio_enabled = state

        # Save State
        self.audio_system_enabled = audio_enabled

        # Update checkBox text
        if audio_enabled:
            self.audioSystemCheckBox.setText("Audio System: ON")
            self.audioSystemCheckBox.setStyleSheet("""
                QCheckBox {
                    color: #4ae84a;
                    font-size: 12px;
                    font-weight: bold;
                    padding: 5px 0 5px 20px;  /* Отступ слева 10px */
                    spacing: 8px;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                }
                QCheckBox::indicator:checked {
                    border: 2px solid #4ae84a;
                    border-radius: 3px;
                    background-color: #4ae84a;
                }
            """)
        else:
            self.audioSystemCheckBox.setText("Audio System: OFF")
            self.audioSystemCheckBox.setStyleSheet("""
                QCheckBox {
                    color: #e84a4a;
                    font-size: 12px;
                    font-weight: bold;
                    padding: 5px 0 5px 20px;  /* Отступ слева 10px */
                    spacing: 8px;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                }
                QCheckBox::indicator:unchecked {
                    border: 2px solid #e84a4a;
                    border-radius: 3px;
                    background-color: transparent;
                }
            """)

        # Toggle control elements
        self.dials_container.setEnabled(audio_enabled)
        self.test_audio_button.setEnabled(audio_enabled)
        self.reset_audio_button.setEnabled(audio_enabled)
        self.mute_button.setEnabled(audio_enabled)

        self.on_setting_changed()

    def on_mute_all_changed(self):
        """Button handler Mute/Unmute (Volume Only)"""
        self.is_muted = not self.is_muted

        if self.is_muted:
            self.mute_button.setIcon(self.mainWindow.get_icon("unmute"))
            self.mute_button.setText(" Unmute All")
            # Set Volume: 0
            self.master_dial.setValue(0)
        else:
            self.mute_button.setIcon(self.mainWindow.get_icon("mute"))
            self.mute_button.setText(" Mute All")
            # Return previous volume
            self.master_dial.setValue(self.master)

    def create_category_dial(self, category, label, default_value):
        """Создает виджет с QDial для категории звука"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 5, 0, 5)

        # Stylization depending on the category
        colors = {
            "voice": "#e84a4a",
            "bgm": "#4ae84a",
            "sfx": "#e8e84a",
            "ambient": "#4a4ae8"
        }
        color = colors.get(category, "#4a86e8")

        # UPPER PART: Icon + Name
        top_container = QWidget()
        top_layout = QVBoxLayout(top_container)
        top_layout.setSpacing(2)
        top_layout.setContentsMargins(0, 0, 0, 0)

        # Category icon (small)
        icon_label = QLabel()
        icon_label.setFixedSize(16, 16)
        icon_label.setObjectName(f"{category}IconLabel")
        setattr(self, f"{category}IconLabel", icon_label)

        # Category Name
        text_label = QLabel(label)
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setObjectName(f"{category}TextLabel")
        text_label_font = QFont()
        text_label_font.setPointSize(9)
        text_label_font.setBold(True)
        text_label.setFont(text_label_font)
        text_label.setStyleSheet(f"color: {color};")
        setattr(self, f"{category}TextLabel", text_label)

        top_layout.addWidget(icon_label, 0, Qt.AlignCenter)
        top_layout.addWidget(text_label, 0, Qt.AlignCenter)

        # CENTRAL PART: Dial
        dial = QDial()
        dial.setMinimum(0)
        dial.setMaximum(100)
        dial.setValue(int(default_value * 100))
        dial.setNotchesVisible(True)
        dial.setNotchTarget(5.0)
        dial.setWrapping(False)
        dial.setFixedSize(60, 60)

        # Save Dial
        setattr(self, f"{category}_dial", dial)

        # BOTTOM PART: Percentages
        value_label = QLabel(f"{int(default_value * 100)}%")
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setObjectName(f"{category}ValueLabel")
        value_label_font = QFont()
        value_label_font.setPointSize(10)
        value_label_font.setBold(True)
        value_label.setFont(value_label_font)
        value_label.setStyleSheet(f"color: {color};")
        setattr(self, f"{category}ValueLabel", value_label)

        # Assembly Parts
        layout.addWidget(top_container, 0, Qt.AlignCenter)
        layout.addWidget(dial, 0, Qt.AlignCenter)
        layout.addWidget(value_label, 0, Qt.AlignCenter)

        # Init dial color
        self.update_dial_color(dial, int(default_value * 100), category)

        return widget

    def create_audio_control(self, category, label, default_value):
        """Creates a control widget for a sound category"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)

        # Small QDial for categories
        dial = QDial()
        dial.setMinimum(0)
        dial.setMaximum(100)
        dial.setValue(int(default_value * 100))
        dial.setNotchesVisible(True)
        dial.setWrapping(False)
        dial.setFixedSize(70, 70)

        # Stylize Dial
        dial.setStyleSheet(f"""
            QDial {{
                background-color: #f8f8f8;
                border-radius: 35px;
                border: 2px solid #cccccc;
            }}
            QDial::chunk {{
                background-color: qconicalgradient(cx:0.5, cy:0.5, angle:90, 
                                                   stop:0 #4a86e8, stop:1 #e0e0e0);
            }}
        """)

        # Save Dial
        setattr(self, f"{category}_dial", dial)

        return widget

    def load_audio_dials(self):
        """Loads values from the config to disks (if they are created)"""
        try:
            # Master Volume
            if hasattr(self, 'master_dial'):
                self.master_dial.setValue(self.master)
                if hasattr(self, 'master_value_label'):
                    self.master_value_label.setText(f"{self.master}%")

            # Categories
            for category in ['voice', 'bgm', 'sfx', 'ambient']:
                dial_attr = f"{category}_dial"
                if hasattr(self, dial_attr):
                    dial = getattr(self, dial_attr)
                    value = getattr(self, category)
                    dial.setValue(value)

                    # Update Label
                    label_attr = f"{category}ValueLabel"
                    if hasattr(self, label_attr):
                        value_label = getattr(self, label_attr)
                        value_label.setText(f"{value}%")

                    # Update Color
                    self.update_dial_color(dial, value, category)

        except Exception as e:
            print(f"Error loading audio dials: {e}")

    def connect_audio_signals(self):
        """Connects the signals of the audio controls"""
        # Master dial
        self.master_dial.valueChanged.connect(self.on_master_volume_changed)

        # Category dials
        for category in ["voice", "bgm", "sfx", "ambient"]:
            dial = getattr(self, f"{category}_dial")
            dial.valueChanged.connect(
                lambda value, cat=category: self.on_category_volume_changed(cat, value)
            )

        # Buttons
        self.test_audio_button.clicked.connect(self.test_audio)
        self.reset_audio_button.clicked.connect(self.reset_audio_to_default)
        self.mute_button.clicked.connect(self.toggle_mute)

    def on_master_volume_changed(self, value):
        """The main volume change handler"""
        # Update Label
        if hasattr(self, 'master_value_label'):
            self.master_value_label.setText(f"{value}%")

        # Update Color
        if hasattr(self, 'master_dial'):
            self.update_dial_color(self.master_dial, value)

        # Apply in audio_manager
        #if hasattr(self.mainWindow, 'audio_manager'):
        #    self.mainWindow.audio_manager.set_master_volume(value / 100.0)

        # Set the change in settings
        self.on_setting_changed()

    # Add this feature in future updates:
    def update_dial_color(self, dial, value, category=None):
        """Dynamically updates the disc color depending on the value"""
        # Defining the base color
        if category:
            colors = {
                "voice": "#e84a4a",
                "bgm": "#4ae84a",
                "sfx": "#e8e84a",
                "ambient": "#4a4ae8"
            }
            base_color = colors.get(category, "#4a86e8")
        else:
            # For Master Volume
            if value == 0:
                base_color = "#a0a0a0"  # Gray for mute
            elif value < 30:
                base_color = "#ff6666"  # Light Red for low
            elif value < 70:
                base_color = "#ffcc44"  # Orange-Yellow for middle
            else:
                base_color = "#66cc66"  # Light Green for High

        # The size of the disc determines the thickness of the border and the size of the handle
        dial_size = dial.width()

        # Different settings for large and small disks
        if dial_size >= 100:  # Big Master Dial
            border_width = 3
            handle_size = 18
            handle_radius = 9
        else:  # Small category dials
            border_width = 2
            handle_size = 14
            handle_radius = 7

        # Create Gradients
        dark_color = self.get_darker_color(base_color, 0.6)

        # APPLY Style (IMPORTANT)
        style = f"""
            QDial {{
                background-color: qradialgradient(
                    cx: 0.5, cy: 0.5, radius: 0.9,
                    fx: 0.3, fy: 0.3,
                    stop: 0 white,
                    stop: 0.7 #f0f0f0,
                    stop: 1 #e0e0e0
                );
                border-radius: {dial_size // 2}px;
                border: {border_width}px solid #cccccc;
            }}
            QDial::chunk {{
                background-color: qconicalgradient(
                    cx: 0.5, cy: 0.5, angle: 90,
                    stop: 0 {base_color},
                    stop: 0.3 {base_color},
                    stop: 0.7 {base_color},
                    stop: 1 {dark_color}
                );
            }}
            QDial::handle {{
                background-color: qradialgradient(
                    cx: 0.3, cy: 0.3, radius: 0.8,
                    stop: 0 white,
                    stop: 1 #f8f8f8
                );
                border: {border_width}px solid {base_color};
                border-radius: {handle_radius}px;
                width: {handle_size}px;
                height: {handle_size}px;
            }}
        """

        dial.setStyleSheet(style)

    def get_darker_color(self, hex_color, factor=0.6):
        """Returns a darker shade of the color"""
        from PySide6.QtGui import QColor

        color = QColor(hex_color)

        # Convert in HSL for darker color
        h = color.hue()
        s = color.saturation()
        l = max(30, color.lightness() * factor)  # Don't make it too dark

        darker = QColor.fromHsl(h, s, int(l))
        return darker.name()

    def on_category_volume_changed(self, category, value):
        """Handler for changing the volume of a category"""
        # Update Text
        if hasattr(self, f"{category}ValueLabel"):
            value_label = getattr(self, f"{category}ValueLabel")
            value_label.setText(f"{value}%")

            # Update Text Color (if change with mute)
            colors = {
                "voice": "#e84a4a",
                "bgm": "#4ae84a",
                "sfx": "#e8e84a",
                "ambient": "#4a4ae8"
            }
            color = colors.get(category, "#4a86e8")
            value_label.setStyleSheet(f"color: {color};")

        # Update color Dial
        if hasattr(self, f"{category}_dial"):
            dial = getattr(self, f"{category}_dial")
            self.update_dial_color(dial, value, category)

        # Set value
        self.on_setting_changed()

    def test_audio(self):
        """Test Sound"""
        try:
            if hasattr(self.mainWindow, 'audio_manager'):
                # Play test sound
                self.mainWindow.audio_manager.play_test_sound()

                # Show Message
                QMessageBox.information(self, self.mainWindow.lang['Settings']['TestSound'],
                                        self.mainWindow.lang['Settings']['TestSoundInfo'])
        except Exception as e:
            QMessageBox.warning(self, self.mainWindow.lang['Settings']['Error'],
                                self.mainWindow.lang['Settings']['TestSoundError'] + {str(e)})
            #QMessageBox.warning(self, "Error", f"Failed to play test sound: {str(e)}")

    def reset_audio_to_default(self):
        """Resets the sound settings to the default values."""
        reply = QMessageBox.question(
            self, "Reset Audio",
            "Reset all audio settings to default values?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Master Volume
            self.master_dial.setValue(100)
            self.update_dial_color(self.master_dial, 100)

            # Categories
            default_values = {
                "voice": 100,
                "bgm": 60,
                "sfx": 90,
                "ambient": 50
            }

            for category, value in default_values.items():
                dial = getattr(self, f"{category}_dial")
                dial.blockSignals(True)
                dial.setValue(value)
                dial.blockSignals(False)

                # Update label
                value_label = getattr(self, f"{category}ValueLabel")
                value_label.setText(f"{value}%")

                # Restoring the text color
                colors = {
                    "voice": "#e84a4a",
                    "bgm": "#4ae84a",
                    "sfx": "#e8e84a",
                    "ambient": "#4a4ae8"
                }
                color = colors.get(category, "#4a86e8")
                value_label.setStyleSheet(f"color: {color};")

                # Update dial color
                self.update_dial_color(dial, value, category)

            # Reset mute state
            if hasattr(self, 'is_muted') and self.is_muted:
                self.is_muted = False
                self.mute_button.setText(" Mute All")
                self.mute_button.setIcon(self.mainWindow.get_icon("mute"))

            # Set Changes
            self.on_setting_changed()

    def toggle_mute(self):
        """On/off All Sounds"""
        self.is_muted = not self.is_muted

        if self.is_muted:
            # Save current values
            self.saved_master_volume = self.master_dial.value()
            self.saved_category_volumes = {}

            for category in ["voice", "bgm", "sfx", "ambient"]:
                dial = getattr(self, f"{category}_dial")
                self.saved_category_volumes[category] = dial.value()

            # Set 0 for All Dials
            self.master_dial.setValue(0)
            for category in ["voice", "bgm", "sfx", "ambient"]:
                dial = getattr(self, f"{category}_dial")
                dial.setValue(0)

            # Update dials color
            self.update_dial_color(self.master_dial, 0)
            for category in ["voice", "bgm", "sfx", "ambient"]:
                dial = getattr(self, f"{category}_dial")
                self.update_dial_color(dial, 0, category)

            self.mute_button.setText(self.mainWindow.lang['Settings']['Unmute'])

            self.mute_button.setIcon(self.mainWindow.get_icon("unmute"))
            self.mute_button.setToolTip(self.mainWindow.lang['Settings']['Unmute'])
        else:
            # Restoring Values
            if hasattr(self, 'saved_master_volume'):
                self.master_dial.setValue(self.saved_master_volume)
                self.update_dial_color(self.master_dial, self.saved_master_volume)

            if hasattr(self, 'saved_category_volumes'):
                for category, value in self.saved_category_volumes.items():
                    dial = getattr(self, f"{category}_dial")
                    dial.setValue(value)
                    self.update_dial_color(dial, value, category)

            # self.mute_button.setText(" Mute All")
            self.mute_button.setText(self.mainWindow.lang['Settings']['Mute'])
            self.mute_button.setIcon(self.mainWindow.get_icon("mute"))
            self.mute_button.setToolTip(self.mainWindow.lang['Settings']['Mute'])

        self.apply_audio_settings()

    def apply_audio_settings(self):
        """Applies the current sound settings"""
        # Master volume
        master_volume = self.master_dial.value() / 100.0
        if hasattr(self.mainWindow, 'audio_manager'):
            self.mainWindow.audio_manager.set_master_volume(master_volume)

        # Category volumes
        for category in ["voice", "bgm", "sfx", "ambient"]:
            dial = getattr(self, f"{category}_dial")
            category_volume = dial.value() / 100.0
            if hasattr(self.mainWindow, 'audio_manager'):
                self.mainWindow.audio_manager.set_category_volume(category, category_volume)

    # Create Buttons
    def create_buttons(self):
        """Create settings buttons"""
        # Create Buttons
        self.resetPosButton = QPushButton("&Reset Position")
        self.resetPosButton.clicked.connect(self.reset_position)

        self.quitButton = QPushButton("&Quit")
        self.quitButton.clicked.connect(self.force_quit_app)
        # self.quitButton.clicked.connect(qApp.quit)  # type: ignore[name-defined,attr-defined] # pylint: disable=undefined-variable

        # Create Buttons Apply/OK/Cancel
        self.button_box = QDialogButtonBox()
        self.apply_button = QPushButton("Apply")
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")

        # Initially, the Apply and Cancel buttons are disabled
        self.apply_button.setEnabled(False)
        self.cancel_button.setEnabled(False)

        # Add buttons in button box
        #self.button_box.addButton(self.apply_button, QDialogButtonBox.ButtonRole.ApplyRole)
        self.button_box.addButton(self.ok_button, QDialogButtonBox.ButtonRole.AcceptRole)
        self.button_box.addButton(self.cancel_button, QDialogButtonBox.ButtonRole.RejectRole)

        # Connect signals
        self.apply_button.clicked.connect(self.apply_settings)
        self.ok_button.clicked.connect(self.ok_pressed)
        self.cancel_button.clicked.connect(self.cancel_pressed)

    def ok_pressed(self):
        """Handler OK Button"""
        if self.unsaved_changes:
            self.apply_settings()
        self.close()

    def cancel_pressed(self):
        """Handler Cancel Button"""
        if self.unsaved_changes:
            reply = QMessageBox.question(
                self, self.mainWindow.lang['Settings']['UnsavedChangesTitle'],
                self.mainWindow.lang['Settings']['DiscardChanges'],
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.revert_to_initial_values()
        else:
            pass

    def on_setting_changed(self, *args):
        """It is called when any setting is changed."""
        # Ignoring changes during initialization
        if hasattr(self, 'block_signals_during_init') and self.block_signals_during_init:
            return

        # Check create buttons
        if hasattr(self, 'apply_button'):
            self.unsaved_changes = True
            self.mainWindow.settings_lock = True
            self.apply_button.setEnabled(True)
            self.cancel_button.setEnabled(True)

    def apply_settings(self):
        """Apply current settings"""
        try:
            # Collecting the current values
            current_settings = {
                'frameless_window': self.framelessWindowCheckBox.isChecked(),
                'stays_on_top': self.windowStaysOnTopCheckBox.isChecked(),
                'color_icons': self.colorIconsCheckBox.isChecked(),
                'background': self.backgroundImageCheckBox.isChecked(),
                'language': self.langComboBox.currentText(),
                'theme': self.themeComboBox.currentText(),
                'auto_scale': self.autoScaleCheckBox.isChecked(),
                'models_scale': self.modelScaleBox.value(),
                'random_character': self.randomCharacterCheckBox.isChecked(),
                'random_character_hdd': self.randomCharacterHDDCheckBox.isChecked(),
                'auto_blink': self.autoBlinkCheckBox.isChecked(),
                'auto_breath': self.autoBreathCheckBox.isChecked(),
                'tracking_mouse': self.trackingMouseCheckBox.isChecked(),
                'sleep': self.sleepCheckBox.isChecked(),
                'time_scale': self.timeScaleBox.value(),
                'idle': self.idleCheckBox.isChecked(),
                'on_mouse': self.onMouseCheckBox.isChecked(),
                'tap_body': self.tapBodyCheckBox.isChecked(),
                'audio_system': self.audioSystemCheckBox.isChecked(),
                'master': self.master_dial.value(),
                'voice': getattr(self, 'voice_dial').value() if hasattr(self, 'voice_dial') else self.voice,
                'bgm': getattr(self, 'bgm_dial').value() if hasattr(self, 'bgm_dial') else self.bgm,
                'sfx': getattr(self, 'sfx_dial').value() if hasattr(self, 'sfx_dial') else self.sfx,
                'ambient': getattr(self, 'ambient_dial').value() if hasattr(self, 'ambient_dial') else self.ambient,
                'show_text_widget': self.showTextWidgetCheckBox.isChecked(),
                'show_name': self.showNameCheckBox.isChecked(),
                'show_kaomoji': self.showKaomojiCheckBox.isChecked()
            }

            # Apply window flags settings
            flags = Qt.WindowType()

            if current_settings['frameless_window']:
                flags = flags | Qt.WindowType.FramelessWindowHint
                self.app_config.FramelessWindowHint = True
                self.mainWindow.frameless = True
            else:
                self.app_config.FramelessWindowHint = False
                self.mainWindow.frameless = False

            if current_settings['stays_on_top']:
                flags = flags | Qt.WindowType.WindowStaysOnTopHint
                self.app_config.WindowStaysOnTopHint = True
            else:
                self.app_config.WindowStaysOnTopHint = False

            # Apply additional settings
            self.set_setting('color_icons', current_settings['color_icons'])
            self.set_setting('background', current_settings['background'])
            self.set_setting('auto_scale', current_settings['auto_scale'])
            self.set_setting('models_scale', current_settings['models_scale'])
            self.set_setting('random_character', current_settings['random_character'])
            self.set_setting('random_character_hdd', current_settings['random_character_hdd'])
            self.set_setting('auto_blink', current_settings['auto_blink'])
            self.set_setting('auto_breath', current_settings['auto_breath'])
            self.set_setting('tracking_mouse_switch', current_settings['tracking_mouse'])
            self.set_setting('sleep_switch', current_settings['sleep'])
            self.set_setting('time_scale', current_settings['time_scale'])
            self.set_setting('idle_switch', current_settings['idle'])
            self.set_setting('on_mouse_switch', current_settings['on_mouse'])
            self.set_setting('tap_body_switch', current_settings['tap_body'])
            self.set_setting('audio_system', current_settings['audio_system'])
            self.set_setting('show_text_widget', current_settings['show_text_widget'])
            self.set_setting('show_name', current_settings['show_name'])
            self.set_setting('show_kaomoji', current_settings['show_kaomoji'])

            # Audio settings
            if not self.is_muted:
                self.set_setting('master', current_settings['master'])
                self.set_setting('voice', current_settings['voice'])
                self.set_setting('bgm', current_settings['bgm'])
                self.set_setting('sfx', current_settings['sfx'])
                self.set_setting('ambient', current_settings['ambient'])

            # Language and theme
            self.language_org = current_settings['language']
            self.getLanguageName()
            self.theme = current_settings['theme']
            self.set_setting('language', str(self.language_get))
            self.set_setting('theme', str(self.theme))

            # Audio categories
            audio_categories = ['voice', 'bgm', 'sfx', 'ambient']
            for category in audio_categories:
                if not self.is_muted:
                    setattr(self.app_config, category, current_settings[category])
                    setattr(self.mainWindow, category, current_settings[category])
                    setattr(self, category, current_settings[category])

            if hasattr(self.mainWindow, 'audio_manager'):
                if self.audio_system_enabled:
                    # ON Audio System
                    # print("✓ Audio system enabled")
                    self.mainWindow.audio_manager.audio_switch = True
                else:
                    # OFF Audio System
                    # print("✗ Audio system disabled")
                    self.mainWindow.audio_manager.audio_switch = False

            # Update audio_manager
            if hasattr(self.mainWindow, 'audio_manager'):
                # Master Volume
                master_audio_value = current_settings['master'] / 100.0 if current_settings['master'] > 1.0 else \
                current_settings['master']
                self.mainWindow.audio_manager.set_master_volume(master_audio_value)

                # Categories
                for category in audio_categories:
                    audio_value = current_settings[category] / 100.0 if current_settings[category] > 1.0 else \
                    current_settings[category]
                    self.mainWindow.audio_manager.set_category_volume(category, audio_value)

            # Update Main Window
            self.mainWindow.setSettings(flags)
            self.mainWindow.show()
            self.mainWindow.model_move = True

            # Update Icons
            self.update_icons()

            # Saving the applied values as new initial values
            self.initial_values = current_settings.copy()

            # Reset changes flags
            self.unsaved_changes = False
            self.mainWindow.settings_lock = False
            self.apply_button.setEnabled(False)
            self.cancel_button.setEnabled(False)

            if self.settings_log:
                print("Settings applied successfully!")

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to apply settings: {str(e)}")

    def revert_to_initial_values(self):
        """Returns the settings to their initial values"""
        self.framelessWindowCheckBox.setChecked(self.initial_values['frameless_window'])
        self.windowStaysOnTopCheckBox.setChecked(self.initial_values['stays_on_top'])
        self.colorIconsCheckBox.setChecked(self.initial_values['color_icons'])
        self.backgroundImageCheckBox.setChecked(self.initial_values['background'])

        # language
        if self.initial_values['language'] == "Русский":
            self.language_set = "Русский"
        else:
            self.language_set = "English"
        self.langComboBox.setCurrentText(self.language_set)

        self.themeComboBox.setCurrentText(self.initial_values['theme'])
        self.autoScaleCheckBox.setChecked(self.initial_values['auto_scale'])
        self.modelScaleBox.setValue(self.initial_values['models_scale'])
        self.randomCharacterCheckBox.setChecked(self.initial_values['random_character'])
        self.randomCharacterHDDCheckBox.setChecked(self.initial_values['random_character_hdd'])
        self.autoBlinkCheckBox.setChecked(self.initial_values['auto_blink'])
        self.autoBreathCheckBox.setChecked(self.initial_values['auto_breath'])
        self.trackingMouseCheckBox.setChecked(self.initial_values['tracking_mouse'])
        self.sleepCheckBox.setChecked(self.initial_values['sleep'])
        self.timeScaleBox.setValue(self.initial_values['time_scale'])
        self.idleCheckBox.setChecked(self.initial_values['idle'])
        self.onMouseCheckBox.setChecked(self.initial_values['on_mouse'])
        self.tapBodyCheckBox.setChecked(self.initial_values['tap_body'])
        self.audioSystemCheckBox.setChecked(self.initial_values['audio_system'])

        if hasattr(self, 'master_dial'):
            self.master_dial.setValue(self.initial_values['master'])

            # Audio Category
        for category in ['voice', 'bgm', 'sfx', 'ambient']:
            dial_attr = f"{category}_dial"
            if hasattr(self, dial_attr):
                dial = getattr(self, dial_attr)
                dial.setValue(self.initial_values[category])

                # Update labels
                label_attr = f"{category}ValueLabel"
                if hasattr(self, label_attr):
                    value_label = getattr(self, label_attr)
                    value_label.setText(f"{self.initial_values[category]}%")

                # Update color
                self.update_dial_color(dial, self.initial_values[category], category)

        self.showTextWidgetCheckBox.setChecked(self.initial_values['show_text_widget'])
        self.showNameCheckBox.setChecked(self.initial_values['show_name'])
        self.showKaomojiCheckBox.setChecked(self.initial_values['show_kaomoji'])

        self.unsaved_changes = False
        self.mainWindow.settings_lock = False
        self.apply_button.setEnabled(False)
        self.cancel_button.setEnabled(False)

    def update_icons(self):
        """Update icons color in real time"""
        # Appearance
        self.framelessWindowCheckBox.setIcon(self.mainWindow.get_icon("frameless_window"))
        self.windowStaysOnTopCheckBox.setIcon(self.mainWindow.get_icon("stay_on_top"))
        self.colorIconsCheckBox.setIcon(self.mainWindow.get_icon("color"))
        self.backgroundImageCheckBox.setIcon(self.mainWindow.get_icon("background"))

        # Model
        self.autoScaleCheckBox.setIcon(self.mainWindow.get_icon("auto_scale"))
        self.randomCharacterCheckBox.setIcon(self.mainWindow.get_icon("random_character"))
        self.randomCharacterHDDCheckBox.setIcon(self.mainWindow.get_icon("random_character_hdd"))

        #Behavior
        self.autoBlinkCheckBox.setIcon(self.mainWindow.get_icon("eye_closed"))
        self.autoBreathCheckBox.setIcon(self.mainWindow.get_icon("breath"))
        self.trackingMouseCheckBox.setIcon(self.mainWindow.get_icon("pointer"))
        self.sleepCheckBox.setIcon(self.mainWindow.get_icon("sleep"))
        self.idleCheckBox.setIcon(self.mainWindow.get_icon("idle_w"))
        self.onMouseCheckBox.setIcon(self.mainWindow.get_icon("mouse"))
        self.tapBodyCheckBox.setIcon(self.mainWindow.get_icon("tap"))

        self.showTextWidgetCheckBox.setIcon(self.mainWindow.get_icon("text_widget"))
        self.showNameCheckBox.setIcon(self.mainWindow.get_icon("name"))
        self.showKaomojiCheckBox.setIcon(self.mainWindow.get_icon("kaomoji"))

    def get_available_styles(self):
        """Dynamically loads the icon based on the current theme."""
        style_names = {
            # Basic Qt Styles
            "legacy": "Windows",
            "windows": "Windows",
            "windowsvista": "Windows Vista",
            "windows11": "Windows 11",
            "fusion": "Fusion",
            "macos": "macOS",

            # Styles for Linux
            "gtk+": "GTK+",
            "breeze": "Breeze",
            "adwaita": "Adwaita",
            "qt5gtk2": "Qt5 GTK2",

            # Outdated/exotic styles
            "cde": "CDE",
            "motif": "Motif",
            "cleanlooks": "CleanLooks"
        }

        # Getting the current system style
        current_style = QApplication.style().objectName().lower()
        current_display_name = style_names.get(current_style, "System Default")

        # Creating a list where the first element is the current style
        available_styles = [current_display_name]  # The first element is the active style

        # Add the remaining available styles (excluding duplicates)
        for style_key in QStyleFactory.keys():
            if style_key != current_style:  # Do not add the current style again
                display_name = style_names.get(style_key, style_key.title())
                available_styles.append(display_name)

        return available_styles

    def reset_position(self):
        """Reset model position"""
        self.mainWindow.model_move = True
        self.updateMainWindow()

    def modelMoveOn(self):
        """Model Move Trigger On"""
        self.mainWindow.model_move = True

    def modelMoveOff(self):
        """Model Move Trigger Off"""
        self.mainWindow.model_move = False

    def set_setting(self, key, value):
        """Synchronize mainWindow and app_config vars"""
        setattr(self.app_config, key, value)
        setattr(self.mainWindow, key, value)
        setattr(self, key, value)

        # IF audio setting: update audio_manager
        if key in ['audio_system', 'master', 'voice', 'bgm', 'sfx', 'ambient']:
            if hasattr(self.mainWindow, 'audio_manager'):
                # convert in 0.0-1.0
                audio_value = value / 100.0 if value > 1.0 else value

                if key == 'audio_system':
                    self.mainWindow.audio_manager.audio_switch = value
                    if value == False:
                        self.mainWindow.audio_manager.stop_audio()
                        self.mainWindow.audio_manager.stop_category("bgm")
                    else:
                        self.mainWindow.audio_manager.play_bg_music()

                if key == 'master':
                    self.mainWindow.audio_manager.set_master_volume(audio_value)
                else:
                    self.mainWindow.audio_manager.set_category_volume(key, audio_value, True)

    def updateSettings(self):
        # Update tab names
        self.tab_widget.setTabText(0, self.mainWindow.lang['Settings']['Appearance'])
        self.tab_widget.setTabText(1, self.mainWindow.lang['Settings']['ModelTitle'])
        self.tab_widget.setTabText(2, self.mainWindow.lang['Settings']['Behavior'])
        self.tab_widget.setTabText(3, self.mainWindow.lang['Settings']['AudioTitle'])
        self.tab_widget.setTabText(4, self.mainWindow.lang['Settings']['OtherTitle'])

        if hasattr(self, 'right_group'):
            self.right_group.setTitle(self.mainWindow.lang['Settings']['Controls'])

        # Settings Main
        self.setWindowTitle(self.mainWindow.lang['Settings']['Settings'])
        self.resetPosButton.setText(self.mainWindow.lang['Settings']['ResetPosition'])
        self.quitButton.setText(self.mainWindow.lang['Settings']['Quit'])
        self.apply_button.setText(self.mainWindow.lang['Settings']['Apply'])
        self.ok_button.setText(self.mainWindow.lang['Settings']['OK'])
        self.cancel_button.setText(self.mainWindow.lang['Settings']['Cancel'])

        # Appearance Tab
        self.framelessWindowCheckBox.setText(self.mainWindow.lang['Settings']['FramelessWindow'])
        self.windowStaysOnTopCheckBox.setText(self.mainWindow.lang['Settings']['StaysOnTop'])
        self.langText.setText(self.mainWindow.lang['Settings']['Language'])
        self.colorIconsCheckBox.setText(self.mainWindow.lang['Settings']['ColorIcons'])
        self.backgroundImageCheckBox.setText(self.mainWindow.lang['Settings']['Background'])
        self.backgroundImageCheckBox.setEnabled(self.mainWindow.background_available)
        if not self.mainWindow.background_available:
            self.block_signals_during_init = True
            self.backgroundImageCheckBox.setChecked(False)
            self.block_signals_during_init = False
        self.themeText.setText(self.mainWindow.lang['Settings']['Theme'])

        # Model Tab
        self.autoScaleCheckBox.setText(self.mainWindow.lang['Settings']['AutoScale'])
        self.sc_mult_text.setText(self.mainWindow.lang['Settings']['ScaleMultiplier'])
        self.randomCharacterCheckBox.setText(self.mainWindow.lang['Settings']['RandomCharacter'])
        self.randomCharacterHDDCheckBox.setText(self.mainWindow.lang['Settings']['RandomCharacterHDD'])
        # self.randomCharacterHDDCheckBox.setEnabled(self.random_character)

        # Behavior Tab
        self.autoBlinkCheckBox.setText(self.mainWindow.lang['Settings']['AutoBlink'])
        self.autoBreathCheckBox.setText(self.mainWindow.lang['Settings']['AutoBreath'])
        self.trackingMouseCheckBox.setText(self.mainWindow.lang['Settings']['TrackingMouse'])
        self.sleepCheckBox.setText(self.mainWindow.lang['Settings']['Sleep'])
        self.sc_time_text.setText(self.mainWindow.lang['Settings']['TimeScale'])
        self.idleCheckBox.setText(self.mainWindow.lang['Settings']['Idle'])
        self.onMouseCheckBox.setText(self.mainWindow.lang['Settings']['OnMouse'])
        self.tapBodyCheckBox.setText(self.mainWindow.lang['Settings']['TapBody'])

        # Audio Tab
        self.test_audio_button.setText(self.mainWindow.lang['Settings']['TestSound'])
        self.reset_audio_button.setText(self.mainWindow.lang['Settings']['ResetSound'])

        if self.audio_system_enabled:
            self.audioSystemCheckBox.setText(self.mainWindow.lang['Settings']['AudioSystemON'])
        else:
            self.audioSystemCheckBox.setText(self.mainWindow.lang['Settings']['AudioSystemOFF'])

        self.master_label.setText(self.mainWindow.lang['Settings']['Master'])

        if hasattr(self, 'voiceTextLabel'):
            self.voiceTextLabel.setText(self.mainWindow.lang['Settings']['Voice'])
        if hasattr(self, 'bgmTextLabel'):
            self.bgmTextLabel.setText(self.mainWindow.lang['Settings']['BGM'])
        if hasattr(self, 'sfxTextLabel'):
            self.sfxTextLabel.setText(self.mainWindow.lang['Settings']['SFX'])
        if hasattr(self, 'ambientTextLabel'):
            self.ambientTextLabel.setText(self.mainWindow.lang['Settings']['Ambient'])
        if not self.is_muted:
            self.mute_button.setText(self.mainWindow.lang['Settings']['Mute'])
        else:
            self.mute_button.setText(self.mainWindow.lang['Settings']['Unmute'])

        # Other Tab
        self.showTextWidgetCheckBox.setText(self.mainWindow.lang['Settings']['ShowTextWidget'])
        self.showNameCheckBox.setText(self.mainWindow.lang['Settings']['ShowName'])
        # self.showNameCheckBox.setEnabled(self.show_text_widget)
        self.showKaomojiCheckBox.setText(self.mainWindow.lang['Settings']['ShowKaomoji'])
        # self.showKaomojiCheckBox.setEnabled(self.show_text_widget)

        # Update icons
        self.update_icons()

    @Slot()
    def updateMainWindow(self) -> None:
        """Update main window settings"""
        flags = Qt.WindowType()
        if self.getWindowFlag_WindowMinimizeButtonHint:
            flags = flags | Qt.WindowType.WindowMinimizeButtonHint

        if self.getWindowFlag_WindowCloseButtonHint:
            flags = flags | Qt.WindowType.WindowCloseButtonHint

        if self.getWindowFlag_WindowTransparentForInput:
            flags = flags | Qt.WindowType.WindowTransparentForInput

        if self.getWindowFlag_WindowType_Mask:
            flags = flags | Qt.WindowType.WindowType_Mask

        if self.pythonic_reg:
            for checkBox, flag in self.hintFlagWidgets:
                if checkBox.isChecked():
                    flags = flags | flag
        else:
            if self.framelessWindowCheckBox.isChecked():
                flags = flags | Qt.WindowType.FramelessWindowHint
                self.app_config.FramelessWindowHint = True
                self.mainWindow.frameless = True
                self.framelessWindowCheckBox.setChecked(True)
            else:
                self.app_config.FramelessWindowHint = False
                self.mainWindow.frameless = False
                self.framelessWindowCheckBox.setChecked(False)

            if self.windowStaysOnTopCheckBox.isChecked():
                flags = flags | Qt.WindowType.WindowStaysOnTopHint
                self.app_config.WindowStaysOnTopHint = True
                self.windowStaysOnTopCheckBox.setChecked(True)
            else:
                self.app_config.WindowStaysOnTopHint = False
                self.windowStaysOnTopCheckBox.setChecked(False)
                self.app_config.WindowStaysOnBottomHint = True

            if self.colorIconsCheckBox.isChecked():
                self.set_setting('color_icons', True)
                self.colorIconsCheckBox.setChecked(True)
            else:
                self.set_setting('color_icons', False)
                self.colorIconsCheckBox.setChecked(False)

            if self.backgroundImageCheckBox.isChecked():
                self.set_setting('background', True)
                self.backgroundImageCheckBox.setChecked(True)
            else:
                self.set_setting('background', False)
                self.backgroundImageCheckBox.setChecked(False)

            if self.autoScaleCheckBox.isChecked():
                self.autoScaleCheckBox.setChecked(True)
                self.autoScaleCheckBox.stateChanged.connect(self.modelMoveOn)
                self.modelScaleBox.setReadOnly(True)
                self.set_setting('auto_scale', True)
                self.set_setting('models_scale', 1)
                self.modelScaleBox.setValue(1)
            else:
                self.autoScaleCheckBox.setChecked(False)
                self.modelScaleBox.setReadOnly(False)
                self.autoScaleCheckBox.stateChanged.connect(self.modelMoveOn)
                scale_value = self.modelScaleBox.value()
                self.set_setting('auto_scale', False)
                self.set_setting('models_scale', scale_value)

            if self.randomCharacterCheckBox.isChecked():
                self.randomCharacterCheckBox.setChecked(True)
                self.set_setting('random_character', True)
            else:
                self.randomCharacterCheckBox.setChecked(False)
                self.set_setting('random_character', False)

            if self.randomCharacterHDDCheckBox.isChecked():
                self.randomCharacterHDDCheckBox.setChecked(True)
                self.set_setting('random_character_hdd', True)
            else:
                self.randomCharacterHDDCheckBox.setChecked(False)
                self.set_setting('random_character_hdd', False)

            if self.autoBlinkCheckBox.isChecked():
                self.autoBlinkCheckBox.setChecked(True)
                self.app_config.auto_blink = True
            else:
                self.autoBlinkCheckBox.setChecked(False)
                self.app_config.auto_blink = False

            if self.autoBreathCheckBox.isChecked():
                self.autoBreathCheckBox.setChecked(True)
                self.app_config.auto_breath = True
            else:
                self.autoBreathCheckBox.setChecked(False)
                self.app_config.auto_breath = False

            if self.trackingMouseCheckBox.isChecked():
                self.trackingMouseCheckBox.setChecked(True)
                self.set_setting('tracking_mouse_switch', True)
            else:
                self.trackingMouseCheckBox.setChecked(False)
                self.set_setting('tracking_mouse_switch', False)

            if self.sleepCheckBox.isChecked():
                self.sleepCheckBox.setChecked(True)
                self.set_setting('sleep_switch', True)
                self.timeScaleBox.setReadOnly(False)
                scale_value = self.timeScaleBox.value()
                self.set_setting('time_scale', scale_value)

            else:
                self.sleepCheckBox.setChecked(False)
                self.set_setting('sleep_switch', False)
                self.timeScaleBox.setReadOnly(True)
                self.set_setting('time_scale', 1)
                self.timeScaleBox.setValue(1)

            if self.idleCheckBox.isChecked():
                self.idleCheckBox.setChecked(True)
                self.set_setting('idle_switch', True)
            else:
                self.idleCheckBox.setChecked(False)
                self.set_setting('idle_switch', False)

            if self.onMouseCheckBox.isChecked():
                self.onMouseCheckBox.setChecked(True)
                self.set_setting('on_mouse_switch', True)
            else:
                self.onMouseCheckBox.setChecked(False)
                self.set_setting('on_mouse_switch', False)

            if self.tapBodyCheckBox.isChecked():
                self.tapBodyCheckBox.setChecked(True)
                self.set_setting('tap_body_switch', True)
            else:
                self.tapBodyCheckBox.setChecked(False)
                self.set_setting('tap_body_switch', False)

            if self.audioSystemCheckBox.isChecked():
                self.audioSystemCheckBox.setChecked(True)
                self.set_setting('audio_system', True)
            else:
                self.audioSystemCheckBox.setChecked(False)
                self.set_setting('audio_system', False)

            if self.showTextWidgetCheckBox.isChecked():
                self.showTextWidgetCheckBox.setChecked(True)
                self.set_setting('show_text_widget', True)
            else:
                self.showTextWidgetCheckBox.setChecked(False)
                self.set_setting('show_text_widget', False)

            if self.showNameCheckBox.isChecked():
                self.showNameCheckBox.setChecked(True)
                self.set_setting('show_name', True)
            else:
                self.showNameCheckBox.setChecked(False)
                self.set_setting('show_name', False)

            if self.showKaomojiCheckBox.isChecked():
                self.showKaomojiCheckBox.setChecked(True)
                self.set_setting('show_kaomoji', True)
            else:
                self.showKaomojiCheckBox.setChecked(False)
                self.set_setting('show_kaomoji', False)

            self.language_org = self.langComboBox.currentText()
            self.getLanguageName()
            self.theme = self.themeComboBox.currentText()
            self.set_setting('language', str(self.language_get))
            self.set_setting('theme', str(self.theme))
            #self.mainWindow.app_config.language = str(self.language_get)
            #print(self.themeComboBox.currentText())

        self.mainWindow.setSettings(flags)
        self.mainWindow.show()

    def createCheckBox(self, text: str) -> QCheckBox:
        """Create CheckBox"""
        checkBox = QCheckBox(text)
        checkBox.clicked.connect(self.updateMainWindow)  # type: ignore[attr-defined]
        return checkBox

    def getLanguageName(self):
        """Get language name"""
        if self.language_org == "Русский":
            self.language_get = "Russian"
        else:
            self.language_get = "English"

    def setLanguageName(self):
        """Set language name"""
        if self.language == "Russian":
            self.language_set = "Русский"
        else:
            self.language_set = "English"

    def closeEvent(self, event):
        """Close Window Handler"""

        if self.unsaved_changes:
            reply = QMessageBox.question(
                self, self.mainWindow.lang['Settings']['UnsavedChangesTitle'],
                self.mainWindow.lang['Settings']['ApplyBeforeClosing'],
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Yes
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.apply_settings()
                event.accept()
            elif reply == QMessageBox.StandardButton.No:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def force_quit_app(self):
        """Force Close Window"""
        # Сохраняем текущее состояние окна настроек
        self.unsaved_changes = False
        self.mainWindow.settings_lock = False

        # Закрываем окно настроек
        self.close()

        # Принудительно закрываем всё приложение
        os._exit(0)

# Additional classes


if __name__ == "__main__":
    import sys
    from pathlib import Path
    import re
    import argparse
    from PySide6.QtWidgets import QApplication

    # --- SET PROJECT ROOT DIRECTORY ---
    PROJECT_ROOT = Path(__file__).parent.parent if not getattr(sys, 'frozen', False) else Path(sys.executable).parent
    os.chdir(PROJECT_ROOT)
    sys.path.append(str(PROJECT_ROOT))  # Add in PYTHON PATH

    # --- Check critical files ---
    REQUIRED_FILES = {
        'README.md': PROJECT_ROOT / 'README.md',
        'version.py': PROJECT_ROOT / 'version.py',
        'resource': PROJECT_ROOT / 'resource'
    }

    for name, path in REQUIRED_FILES.items():
        if not path.exists():
            raise FileNotFoundError(f"Не найден критический файл: {name} ({path})")

    # --- Imports after set paths ---
    from version import __version__
    import resources


    # --- Update README ---
    def update_readme():
        """Update App Version in README.md file"""
        readme = PROJECT_ROOT / 'README.md'
        content = readme.read_text(encoding='utf-8')
        updated = re.sub(r'app_version-[\d.]+', f'app_version-{__version__}', content)
        if updated != content:
            readme.write_text(updated, encoding='utf-8')
            print(f"Обновлена версия в README: {__version__}")
        else:
            print(f"Текущая версия в README: {__version__}")


    update_readme()

    #parser = argparse.ArgumentParser()
    #parser.add_argument("-p", "--pythonic", action='store_true')
    #args = parser.parse_args()

    live2d.init()
    format = QSurfaceFormat.defaultFormat()
    format.setSwapInterval(0)
    format.setAlphaBufferSize(8)
    format.setRenderableType(QSurfaceFormat.OpenGL)
    format.setSwapBehavior(QSurfaceFormat.DoubleBuffer)
    QSurfaceFormat.setDefaultFormat(format)

    app = QApplication(sys.argv)
    win = MainWindow()
    win.setFormat(format)
    settings = SettingsWindow()
    settings.setWindowIcon(QIcon(os.path.join(
        resources.RESOURCES_DIRECTORY, "icons/color/settings.svg")))

    app.exec()
    live2d.dispose()