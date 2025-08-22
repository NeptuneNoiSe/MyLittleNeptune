from PySide6.QtCore import QSize, QObject, QTimer, QPropertyAnimation, QEasingCurve, QVariantAnimation, \
    QParallelAnimationGroup
from PySide6.QtGui import QMovie, Qt
from PySide6.QtWidgets import QApplication, QGraphicsOpacityEffect

from package import resources
import random
import time
import math
import json
import os
import live2d.v3 as live2d
from package.additional.models_manager import ModelsManager
from package.additional.resource_manager import ResourceManager

class AnimationsManager:
    """Main Animation Manager"""
    def __init__(self, win, model):
        self.model = model
        self.win = win
        # LOGS
        self._log_callbacks = False

        # Init animators
        self.animation_player = AnimationPlayer(self)
        self.transform_animator = TransformAnimator(self)
        self.blink_animator = BlinkAnimator(self)
        self.opacity_animator = OpacityAnimator(self)
        self.drag_animator = DragAnimator(self)
        self.color_animator = ColorAnimator(self)
        self.resource_manager = ResourceManager(resources.RESOURCES_DIRECTORY)
        self.models_manager = ModelsManager

        # Set FPS
        self.target_fps = 60  # Default FPS Set
        self.frame_delay = int(1000 / 60)  # Auto Calculate

        # Load Profiles and Motions
        self.profiles = self._load_profiles()
        self._current_character = None
        self._active_model = None
        self._load_extra_motions()

    @property
    def character_name(self):
        return self._current_character

    @character_name.setter
    def character_name(self, name: str):
        """Automatic name set when changing a character"""
        if name in self.profiles and name != self._current_character:
            self._current_character = name
            data = self.profiles[name]

    def set_logging(self, enabled: bool):
        """Logging management"""
        self._log_callbacks = enabled

        self.animation_player._log_callbacks = enabled

    def set_target_fps(self, fps):
        """Update animation FPS"""
        self.target_fps = fps
        self.frame_delay = int(1000 / fps)  # 16.67 ms for 60 FPS
        if self.transform_animator.animation_timer.isActive():
            self.transform_animator.animation_timer.setInterval(self.frame_delay)

    def transform_animation_start(self):
        """Activate Transform Animation"""
        self.transform_animator.play_transform_animation()

    def _load_extra_motions(self):
        """Loads extra motions"""
        motions = self.resource_manager.load_extra_motions()
        for i, (name, path) in enumerate(motions.items()):
            self.model.LoadExtraMotion("Extra", i, path)

    def _load_profiles(self) -> dict:
        """Load a single config for all characters"""
        with open(os.path.join(
            resources.RESOURCES_DIRECTORY, "configs/animation_profiles.json"), 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Converting lists to sets for hit_zones
            for char in data.values():
                char['hit_zones'] = {k: set(v) for k, v in char['hit_zones'].items()}
            return data

    def set_sleep_state(self, is_sleeping: bool):
        """Sleep state Management"""
        if is_sleeping:
            self.animation_player._reset_idle_state()
        self._sleep_mode = is_sleeping  # It can be used for special sleep animations.

    # Proxy-methods for AnimationPlayer
    def play_animation(self, model, anim_type: str, group_or_id, no=None, priority=None,
                       custom_start=None, custom_finish=None):
        """
        Proxy-Method for AnimationPlayer.play_animation
        """
        return self.animation_player.play_animation(
            model=model,
            anim_type=anim_type,
            group_or_id=group_or_id,
            no=no,
            priority=priority,
            custom_start=custom_start,
            custom_finish=custom_finish
        )

    def handle_hit(self, hit_parts: set):
        """Proxy method for processing clicks"""
        return self.animation_player.handle_hit(hit_parts)

    def update_idle(self, current_time: float) -> bool:
        """Proxy method for updating idle animations"""
        return self.animation_player.update_idle(current_time)

    def update_drag_animation(self):
        """Updates the drag animation"""
        self.drag_animator.update_drag_animation()

    def reset_drag_animation(self):
        """Initiates the return to the starting position"""
        self.drag_animator.start_return_animation()

    #Color Animations
    def start_rainbow_effect(self, speed=1.0):
        """Start rainbow backlight effect"""
        self.color_animator.start(speed)

    def stop_rainbow_effect(self, smooth=True):
        """Stop rainbow backlight effect"""
        self.color_animator.stop(smooth)

    def set_solid_color(self, r, g, b, fade_duration = 0):
        """Set static backlight effect"""
        self.color_animator.set_solid_color(r, g, b, fade_duration)

    def play_fade_to_zero(self, duration: int | None = None) -> None:
        """Start fade to zero color backlight effect"""
        self.color_animator.fade_to_zero(duration)

    def play_fade_to_color(self,
                           r: int | None = 0 ,
                           g: int | None = 0,
                           b: int | None = 0,
                           duration: int | None = 1000) -> None:
        """Start fade to color backlight effect"""
        self.color_animator.fade_to_color(r,g,b,duration)

class AnimationPlayer:
    """Animation Player"""
    def __init__(self, animation_manager):
        self.animation_manager = animation_manager
        self._is_idle_playing = False
        self._last_idle_time = 0.0
        self._next_idle_delay = 0.0
        self._log_callbacks = False

    @property
    def win(self):
        return self.animation_manager.win

    @property
    def model(self):
        return self.animation_manager.model

    @property
    def profiles(self):
        return self.animation_manager.profiles

    @property
    def current_character(self):
        return self.animation_manager._current_character

    @property
    def _log_callbacks(self):
        """Access to the logging flag from AnimationManager"""
        return self.animation_manager._log_callbacks

    @_log_callbacks.setter
    def _log_callbacks(self, value):
        """Prohibit direct modification, only through AnimationManager"""
        pass  # Or you can allow it if necessary:
        # self.animation_manager._log_callbacks = value

    def play_animation(self,model, anim_type: str, group_or_id, no=None, priority=None,
                       custom_start=None, custom_finish=None):
        """
        A universal method for starting animations
        :param anim_type: 'RandomMotion' or 'Motion'
        :param group_or_id: For RandomMotion - group name (str), for Motion - group number (str)
        :param no: For Motion only - animation number (int)
        :param priority: Animation priority
        """
        callbacks = {
            'start': custom_start or self._handle_motion_start,
            'finish': custom_finish or self._handle_motion_finish
        }

        if anim_type == 'RandomMotion':
            model.StartRandomMotion(
                str(group_or_id),  # Group (str)
                priority,
                onStart=callbacks['start'],
                onFinish=callbacks['finish']
            )
        elif anim_type == 'Motion':
            model.StartMotion(
                str(group_or_id),  # Group (str)
                int(no),  # Animation number (int)
                int(priority),  # Live2d priority (int)
                onStart=callbacks['start'],
                onFinish=callbacks['finish']
            )
        else:
            raise ValueError(f"Unknown animation type: {anim_type}")

    def _handle_motion_start(self, group, no):
        """Callback with Animation Start"""
        if self._log_callbacks:
            print(f"Animation {group} {no} start - blink off")
        self.animation_manager.blink_animator.set_blink_enabled(False)  # Using our previously created method

    def _handle_motion_finish(self, group, no):
        """Callback with Animation Finish"""
        if not self.animation_manager.transform_animator.transform:
            self.model.ResetAllParameters()
        if group != "Idle":  # If the NON-idle animation has ended
            self._reset_idle_state()
            self.animation_manager.blink_animator.set_blink_enabled(True)
        if self._log_callbacks:
            print(f"Animation {group} {no} finish - blink on")

        # Additionally: reset the eyes to the open state
        #self.model.SetParameterValueById("ParamEyeLOpen", 1.0)
        #self.model.SetParameterValueById("ParamEyeROpen", 1.0)
        #self.model.SetParameterValueById("ParamMouthOpenY", 0)

    def _random_delay(self):
        """Generate Random Interval"""
        return random.uniform(5.0, 50.0) if random.random() < 0.7 else random.uniform(10.0, 100.0)

    def update_idle(self, current_time: float) -> bool:
        """Update state idle-animation. Return True, if animation Start"""

        if not self._is_idle_playing and current_time - self._last_idle_time > self._next_idle_delay:
            self._play_idle_animation()
            return True
        return False

    def _play_idle_animation(self):
        """Running animations with timer updates"""
        self.model.StartRandomMotion("Idle", live2d.MotionPriority.IDLE,
                                     onStart=lambda g, n: self._handle_idle_start(g, n),
                                     onFinish=lambda g, n: self._handle_idle_finish(g, n)
                                     )
        self._is_idle_playing = True
        self._last_idle_time = time.time()
        self._next_idle_delay = random.uniform(5.0, 15.0)  # Pause 5-15 sec

    def _handle_idle_start(self, group, no):
        """Callback Animation Start"""
        self._is_idle_playing = True
        if self._log_callbacks:
            print(f"Animation {group} {no} start - blink off")

    def _handle_idle_finish(self, group, no):
        """Callback Animation Finish"""
        self._is_idle_playing = False
        # self.model.ResetExpressions()
        if self._log_callbacks:
            print(f"Animation {group} {no} finish - blink on")

    def _reset_idle_state(self):
        """Reset with Sleep"""
        self._is_idle_playing = False
        self._last_idle_time = 0

    def _play_profile_animation(self, profile: dict):
        """Playing animations based on a JSON-profiles"""
        if profile.get('priority', 0) > live2d.MotionPriority.IDLE:
            self._reset_idle_state()

        if profile['anim_type'] == 'Motion':
            # Processing options as a number OR as a list
            options = profile['options']
            anim_id = random.choice([options] if isinstance(options, int) else options)
            self.play_animation(
                model=self.model,
                anim_type='Motion',
                group_or_id=profile['group'],
                no=anim_id,
                priority=profile.get('priority', live2d.MotionPriority.FORCE)
            )
        else:
            self.play_animation(
                model=self.model,
                anim_type='RandomMotion',
                group_or_id=profile['group'],
                priority=profile['priority']
            )

    def handle_hit(self, hit_parts: set):
        """Click processing with automatic profile selection"""
        if not self.current_character:
            return False
        # print(hit_parts)
        profile = self.profiles[self.current_character]
        for zone, parts in profile['hit_zones'].items():
            if hit_parts & parts:
                self._play_profile_animation(profile['animations'][zone])
                return True

        # Default Animation
        self._play_profile_animation(profile['animations']['default'])
        return True

class BlinkAnimator:
    """Auto Blink Animator"""
    def __init__(self, animation_manager):
        self.animation_manager = animation_manager

        self.blink_enabled = True
        self.last_update_time = 0
        self.blinkProgress = 0.0
        self.nextBlinkInterval = 0.0
        self.lastBlinkTime = 0.0
        self.isBlinking = True

        self._blink_state = {
            'enabled': True,
            'is_active': False,
            'progress': 0.0,
            'last_blink': time.time(),
            'next_delay': self._random_blink_delay(),
            'override_blink': True  # A critical flag
        }

    @property
    def win(self):
        """Actual window link"""
        return self.animation_manager.win

    def update_blink(self, delta_time: float):
        """Main Blink Logic"""
        if not self._blink_state['enabled']:
            self._reset_blink_state()
            return

        # Run new blink logic
        if not self._blink_state['is_active']:
            if time.time() - self._blink_state['last_blink'] > self._blink_state['next_delay']:
                self._start_new_blink()

        # Blink animation
        if self._blink_state['is_active']:
            self._update_blink_animation(delta_time)

    def _update_blink_animation(self, delta_time):
        """Update blink progress"""
        state = self._blink_state
        state['progress'] += delta_time * 0.5

        if state['progress'] >= 1.0:
            self._reset_blink_state()
        else:
            # Sinusoidal animation
            if state['progress'] < 0.4:
                eye_open = 1.0 - math.sin(state['progress'] * math.pi * 0.25)
            else:
                eye_open = math.sin((state['progress'] - 0.4) * math.pi * 0.833)

            # Apply it with a small spread
            self._set_eye_params(eye_open)

    def _set_eye_params(self, base_value: float):
        """Save apply eyes parameters"""
        if self._blink_state['override_blink']:
            self.animation_manager.model.SetParameterValueById("ParamEyeLOpen",
                                                               base_value * random.uniform(0.95, 1.0))
            self.animation_manager.model.SetParameterValueById("ParamEyeROpen",
                                                               base_value * random.uniform(0.98, 1.0))

    def _start_new_blink(self):
        """Initialize new blink"""
        self._blink_state.update({
            'is_active': True,
            'progress': 0.0,
            'last_blink': time.time(),
            'next_delay': self._random_blink_delay()
        })

    def _reset_blink_state(self):
        """Full Reset State"""
        self._blink_state.update({
            'is_active': False,
            'progress': 0.0
        })
        # if not self._blink_state['enabled']:
        #    self._set_eye_params(1.0)  # Force eyes open

    def set_blink_enabled(self, enabled: bool):
        """Blink system switch"""
        self._blink_state['enabled'] = enabled
        if not enabled:
            self._reset_blink_state()

    def _random_blink_delay(self):
        """Generate Random Interval"""
        return random.uniform(2.0, 5.0) if random.random() < 0.7 else random.uniform(6.0, 10.0)

class OpacityAnimator:
    """Managing transparency animations"""
    def __init__(self, animation_manager):
        self.animation_manager = animation_manager

        self.anim = QVariantAnimation()

    @property
    def win(self):
        """Actual window link"""
        return self.animation_manager.win

    def animate_opacity(self, win, start, end, duration=500, easing="linear", on_finished=None):
        """Animation of character transparency via QVariantAnimation"""
        # Set base params
        self.anim.setDuration(duration)
        self.anim.setStartValue(float(start))
        self.anim.setEndValue(float(end))

        # Process easing curve
        if not hasattr(self, 'EASING_TYPES'):
            self.EASING_TYPES = {
                "linear": QEasingCurve.Linear,
                "in_quad": QEasingCurve.InQuad,
                "out_quad": QEasingCurve.OutQuad,
                "in_out_quad": QEasingCurve.InOutQuad,
            }

        easing_curve = self.EASING_TYPES.get(easing, QEasingCurve.Linear)

        # Set Var SetOutputOpacity
        self.anim.valueChanged.connect(win.canvas.SetOutputOpacity)

        #  on_finished connect
        if hasattr(self, "_last_finished_slot"):
            try:
                self.anim.finished.disconnect(self._last_finished_slot)
            except RuntimeError:
                pass

        if callable(on_finished):
            self.anim.finished.connect(on_finished)
            self._last_finished_slot = on_finished  # Сохраняем для будущего отключения

        self.anim.start()

class TransformAnimator:
    """Character transformation animation management"""
    def __init__(self, animation_manager):
        self.animation_manager = animation_manager

        self._win = None

        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._on_animation_tick)

        # Transform Animation State
        self.transform_text = False
        self.transform = False
        self.current_animation_win = None
        self.animation_phase = 0   # 0-idle, 1-fade out, 2-model swap, 3-fade in
        self.transform_lock = False

    @property
    def win(self):
        """Actual window link"""
        return self.animation_manager.win

    # Transform Animations
    def play_transform_animation(self):
        """Start full transformation sequence"""
        if self.animation_phase != 0:
            return

        self.current_animation_win = self.win
        self.animation_phase = 1
        self.win.input_handler.input_lock = True
        self.transform = self.win.transform = True
        self.win.canvas.SetOutputOpacity(1.0)

        self.animation_manager.start_rainbow_effect(speed=2.0)

        # Setup transform_in animation
        self._play_model_animation()
        self.win.transformMovie = QMovie(self.animation_manager.resource_manager.load_animation("transform_in"))
        self.win.transformLabel.setMovie(self.win.transformMovie)
        self.win.transformMovie.setCacheMode(QMovie.CacheAll)
        self.win.transformLabel.raise_()
        self.win.transformLabel.movie().setScaledSize(self._calculate_animation_size())
        self.win.transformLabel.move(int(self.win.trm_mx * self.win.models_scale), int(self.win.trm_my * self.win.models_scale))
        self.win.transformMovie.start()
        self.win.transformLabel.show()

        self.animation_timer.start(16)  # 60 FPS

    def _on_animation_tick(self):
        """Animation phases"""
        if not self.current_animation_win:
            self.animation_timer.stop()
            return

        self._win = self.current_animation_win

        if self.animation_phase == 1:
            self._process_fade_out()
        elif self.animation_phase == 2:
            self._execute_model_swap()
            self.animation_phase = 3
            self._init_fade_in()
        elif self.animation_phase == 3:
            self._process_fade_in()

    def _process_fade_out(self):
        """Handle transform_in animation and opacity fade"""
        current_frame = self.win.transformMovie.currentFrameNumber()
        total_frames = self.win.transformMovie.frameCount()

        # Smooth fade from 70% to 100% animation
        fade_start = int(total_frames * 0.70)
        if current_frame >= fade_start:
            progress = (current_frame - fade_start) / (total_frames - fade_start)
            self.win.canvas.SetOutputOpacity(1.0 - progress)

        # When fade out completes, move to model swap
        if current_frame >= total_frames - 3:
            self.win.transformMovie.stop()
            self.animation_phase = 2
         # Close dialog
        if current_frame >= (total_frames - 3) / 2:
            self.win.talk_widget.close_dialog_after_animation()

    def _execute_model_swap(self):
        """Execute model transformation using your existing methods"""
        try:
            if not self.win.hdd_form:
                self._transform_to_hdd()  # Your HDD transformation
            else:
                self._transform_to_regular()  # Your regular transformation
        finally:
            self._transform_animation_reset()

    def _transform_animation_reset(self):
        """Reset animation"""
        self.win.transformLabel.movie().setScaledSize(QSize(1, 1))
        self.win.transformMovie.stop()
        self.win.transformLabel.close()

    def _init_fade_in(self):
        """Initialize transform_out animation"""
        self.win.transformMovie = QMovie(self.animation_manager.resource_manager.load_animation("transform_out"))
        self.win.transformLabel.setMovie(self.win.transformMovie)
        self.win.transformMovie.setCacheMode(QMovie.CacheAll)
        self.win.transformLabel.movie().setScaledSize(
            self._calculate_animation_size()
        )
        self.win.transformMovie.start()
        self.win.transformLabel.move(int(self.win.trm_mx * self.win.models_scale), int(self.win.trm_my * self.win.models_scale))
        self.win.transformLabel.show()

        self.win.canvas.SetOutputOpacity(0.0)  # Start fully transparent

    def _process_fade_in(self):
        """Handle transform_out animation with delayed opacity restore"""
        current_frame = self.win.transformMovie.currentFrameNumber()
        total_frames = self.win.transformMovie.frameCount()

        # Starting the appearance with 15% animation
        fade_start = int(total_frames * 0.15)
        fade_end = int(total_frames * 0.7)  # Finalize on 70%

        if current_frame < fade_start:
            # Transparency Delay from 0% to 25% of the animation
            self.win.canvas.SetOutputOpacity(0.0)
        elif fade_start <= current_frame <= fade_end:
            # Smooth appearance from 25% to 70%
            progress = (current_frame - fade_start) / (fade_end - fade_start)
            self. win.canvas.SetOutputOpacity(progress)
        else:
            # After 70%, set 100% transparency
            self.win.canvas.SetOutputOpacity(1.0)

        # Final Animation with end
        if current_frame >= total_frames - 3:
            self._finalize_transformation()

    def _finalize_transformation(self):
        """Cleanup after transformation"""
        try:
            self.win.transformMovie.stop()
            self.win.transformLabel.close()
            self.win.canvas.SetOutputOpacity(1.0)  # Ensure full visibility
            self.win.input_handler.input_lock = False
            self.win.transform_lock = False
            self.win.talk_widget.talk_update = True
            self.transform = self.win.transform = False
            self.win.character.state.set_transformed_state()

            self.animation_manager.stop_rainbow_effect()

            # Reset transformation flags
            self.win.character.transform_exp_show = False
            self.win.character.transform_text_show = False
        finally:
            self.animation_timer.stop()
            self.current_animation_win = None
            self.animation_phase = 0

    def _play_model_animation(self):
        """Model animation playback"""
        # Regular form processing (hdd_form=False)
        if not self.win.hdd_form:
            # Playing the transformation animation
            self.animation_manager.play_animation(
                model=self.win.model,
                anim_type='Motion',
                group_or_id="Unique",
                no=0,
                priority=live2d.MotionPriority.FORCE,
            )

    def _calculate_animation_size(self):
        """Calculate animation size"""
        return QSize(
            int(self.win.w_resize + self.win.trm_cmx * self.win.models_scale),
            int(self.win.h_resize + self.win.trm_cmy * self.win.models_scale)
        )

    def _transform_to_hdd(self):
        """Transformation to hdd form"""
        transformations = {
            "Neptune": self.win.action_handler.on_action_purple_heart,
            "Noire": self.win.action_handler.on_action_black_heart,
            "Blanc": self.win.action_handler.on_action_white_heart,
            "Vert": self.win.action_handler.on_action_green_heart,
            "NepGear": self.win.action_handler.on_action_purple_sister,
            "Uni": self.win.action_handler.on_action_black_sister,
            "Rom": self.win.action_handler.on_action_white_sister_rom,
            "Ram": self.win.action_handler.on_action_white_sister_ram,
        }
        if self.win.character_name in transformations:
            transformations[self.win.character_name]()
        self.transform_lock = 1
        self.win.character.transform_exp_show = True
        self.win.character.transform_text_show = True
        self.win.character.expressions.set_funny_expression(fade_out=30000)

    def _transform_to_regular(self):
        """Transformation to regular form"""
        transformations = {
            "Purple Heart": self.win.action_handler.on_action_neptune,
            "Black Heart": self.win.action_handler.on_action_noire,
            "White Heart": self.win.action_handler.on_action_blanc,
            "Green Heart": self.win.action_handler.on_action_vert,
            "Purple Sister": self.win.action_handler.on_action_nepgear,
            "Black Sister": self.win.action_handler.on_action_uni,
            "White Sister Rom": self.win.action_handler.on_action_rom,
            "White Sister Ram": self.win.action_handler.on_action_ram,
        }
        if self.win.character_name in transformations:
            transformations[self.win.character_name]()
        self.transform_lock = 1
        self.win.character.transform_exp_show = True
        self.win.character.transform_text_show = True
        self.win.character.expressions.set_funny_expression(fade_out=30000)

# TODO: [WIP] Класс Аниматор движения частей тела. Требуется тестирование и отладка
class BodyPartAnimator:
    def __init__(self, animation_manager):
        self.animation_manager = animation_manager
        self.active_parts = {}
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_parts)
        self.timer.setInterval(1)  # 60 FPS
        self.last_time = time.perf_counter()

    @property
    def model(self):
        return self.animation_manager.model

    def add_animation(self, part_id, range=(0, 10), speed=0.1,easing='linear'):
        # Приводим к правильным типам
        range = (float(range[0]), float(range[1]))
        speed = float(speed)

        if part_id not in self.active_parts:
            # Новая анимация
            self.active_parts[part_id] = {
                'range': range,
                'speed': speed,
                'value': range[0],
                'direction': 1,
                'easing': easing,
                'active': True,
            }
        else:
            # Обновление существующей анимации
            config = self.active_parts[part_id]
            config['range'] = range
            config['speed'] = speed
            config['active'] = True
            config['reset_requested'] = False

            # Плавный переход к новым параметрам
            if config['value'] < range[0]:
                config['value'] = range[0]
            elif config['value'] > range[1]:
                config['value'] = range[1]

        if not self.timer.isActive():
            self.last_time = time.perf_counter()
            self.timer.start()

    def stop_all(self):
        """Мгновенная остановка (использовать только при необходимости)"""
        for part_id in list(self.active_parts.keys()):
            self.model.SetParameterValueById(part_id, 0)
        self.active_parts.clear()
        self.timer.stop()


    def _update_parts(self):
        current_time = time.perf_counter()
        delta_time = current_time - self.last_time
        self.last_time = current_time

        # 1. Обновляем активные анимации
        parts_to_remove = []
        for part_id, config in self.active_parts.items():
            try:
                if not config['active']:
                    continue

                # Плавное изменение значения
                new_value = config['value'] + config['direction'] * config['speed'] * delta_time * 60

                # Ограничение диапазона
                if new_value >= config['range'][1]:
                    new_value = config['range'][1]
                    config['direction'] = -1
                elif new_value <= config['range'][0]:
                    new_value = config['range'][0]
                    config['direction'] = 1

                self.model.SetParameterValueById(part_id, new_value)
                config['value'] = new_value

            except Exception as e:
                print(f"Animation error for {part_id}: {e}")
                parts_to_remove.append(part_id)

        # Удаляем завершенные анимации
        for part_id in parts_to_remove:
            self._safe_remove_part(part_id)

        if not self.active_parts:
            self.timer.stop()

    def _safe_remove_part(self, part_id):
        """Безопасное удаление части из active_parts"""
        if part_id in self.active_parts:
            try:
                self.model.SetParameterValueById(part_id, 0)
            except:
                pass
            del self.active_parts[part_id]

class DragAnimator:
    def __init__(self, animation_manager):
        self.animation_manager = animation_manager
        self.part_animator = BodyPartAnimator(self)

        self.angle = 0.0
        self.max_angle = 15.0
        self.return_delay = 500  # Delay before return (ms)
        self.return_speed = 0.5  # Return rate (0.1-0.9)
        self.drag_direction_x = 0  # Horizontal direction (-1 to 1)
        self.drag_direction_y = 0  # Vertical direction (-1 to 1)
        self.drag_intensity = 0
        self.max_angle = 10
        self.last_animation_time = 0

        self.vertical_intensity = 0.0  # Добавляем отслеживание вертикальной интенсивности
        self.return_threshold = 0.1    # Порог остановки для всех анимаций

        # Таймеры
        self.return_timer = QTimer()
        self.return_timer.setSingleShot(True)
        self.return_timer.timeout.connect(self.start_return_animation)

        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_return_animation)
        self.animation_timer.setInterval(16)  # 60 FPS

    @property
    def win(self):
        return self.animation_manager.win

    @property
    def model(self):
        return self.animation_manager.model

    @property
    def profiles(self):
        return self.animation_manager.profiles

    @property
    def current_character(self):
        return self.animation_manager._current_character

    @property
    def _log_callbacks(self):
        """Access to the logging flag from AnimationManager"""
        return self.animation_manager._log_callbacks

    # TODO: [WIP] Анимация движения частей тела при перетаскивании. Требуется тестирование и отладка
    def start_drag_animation(self, direction_key):
        """Start animation for any direction"""
        if not hasattr(self, 'last_animation_time'):
            self.last_animation_time = 0

        # Защита от слишком частых перезапусков
        current_time = time.time()
        if current_time - self.last_animation_time < 0.1:  # Не чаще 10 раз в секунду
            return

        self.last_animation_time = current_time

        profile = self.profiles.get(self.current_character, {})
        drag_config = profile.get('drag_animations', {}).get(direction_key, {})
        # print(f"Drag config for {direction_key}: {drag_config}")  # Что содержится в конфиге

        for part_config in drag_config.get('parts', []):
            # print(f"Drag config for {direction_key}, Processing part: {part_config}")  # Вывод текущей конфигурации
            try:
                self.part_animator.add_animation(
                    part_id=part_config['part'],
                    range=part_config.get('range', [0, 10]),
                    speed=part_config.get('speed', self.drag_intensity/2)
                )
            except Exception as e:
                print(f"Animation error for {part_config['part']}: {e}")

    def stop_drag_animation(self):
        self.part_animator.stop_all()

    def update_vertical_movement(self, direction_y, intensity):
        """Отдельный метод для вертикального движения"""
        self.drag_direction_y = direction_y
        self.drag_intensity = intensity
        # Для вертикального движения не применяем угол наклона!
        self.return_timer.stop()
        self.return_timer.start(self.return_delay)

    def update_angle(self, direction, intensity):
        """Update tilt angle only for horizontal movement"""
        self.drag_direction_x = direction
        self.drag_intensity = intensity

        # Only apply tilt for horizontal movement
        target_angle = direction * intensity * self.max_angle
        self.angle = 0.3 * target_angle + 0.7 * self.angle

        # self.win.model.Rotate(int(self.angle))

    def update_drag_animation(self):
        """Only for horizontal movement - vertical doesn't tilt"""
        if abs(self.drag_direction_x) > 0.1:  # Only if significant horizontal movement
            target_angle = self.drag_direction_x * self.drag_intensity * self.max_angle
            self.angle = 0.3 * target_angle + 0.7 * self.angle
            self.win.model.Rotate(int(self.angle))

        # Restart the delay timer for both axes
        self.return_timer.stop()
        self.return_timer.start(self.return_delay)

    def start_return_animation(self):
        """Starting the return animation"""
        if not self.animation_timer.isActive():
            self.animation_timer.start()

    def _update_return_animation(self):
        """Плавный возврат для всех типов анимаций"""
        # Проверяем ВСЕ условия остановки
        should_stop = (
                abs(self.angle) < self.return_threshold and  # Горизонтальный наклон
                abs(self.drag_direction_y) < self.return_threshold and  # Вертикальное движение
                self.drag_intensity < self.return_threshold  # Общая интенсивность
        )

        if should_stop:
            # Полная остановка только когда ВСЁ завершено
            self.angle = 0
            self.drag_direction_y = 0
            self.animation_timer.stop()
            self.part_animator.stop_all()
        else:
            # Плавный сброс горизонтального наклона
            if abs(self.angle) > self.return_threshold:
                progress = abs(self.angle) / self.max_angle
                slowdown_factor = 0.5 + (1 - progress) * 0.5
                self.angle *= self.return_speed * slowdown_factor

            # Плавный сброс вертикальной интенсивности
            if abs(self.drag_direction_y) > self.return_threshold:
                self.drag_direction_y *= self.return_speed

            # Плавный сброс общей интенсивности
            if self.drag_intensity > self.return_threshold:
                self.drag_intensity *= self.return_speed

        self.apply_rotation()

    def apply_rotation(self):
        """Applies the current angle to the model"""
        try:
            if hasattr(self.win, 'model'):
                self.win.model.Rotate(int(self.angle))
        except Exception as e:
            print(f"Rotation error: {e}")

    def stop_animation(self):
        """Остановка всех анимаций с приоритетом"""
        # Сначала плавно сбрасываем параметры
        self.angle = 0
        self.drag_direction_y = 0
        self.drag_intensity = 0
        self.apply_rotation()

        # Затем останавливаем анимации частей тела
        self.part_animator.stop_all()

        # Останавливаем таймеры
        self.animation_timer.stop()
        self.return_timer.stop()

class ColorAnimator(QObject):
    """Color Animation"""
    def __init__(self, animation_manager):
        super().__init__()
        self.animation_manager = animation_manager
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_colors)

        # Animation Settings
        self.speed = 1.0
        self.is_running = False
        self.current_hue = random.uniform(0, 360)  # 0-360 degress
        self.target_rgb = (0.0, 0.0, 0.0)  # Color range 0-1

    @property
    def win(self):
        """Actual window link"""
        return self.animation_manager.win

    @property
    def red(self):
        return self.animation_manager.win.b_red

    @red.setter
    def red(self, value):
        self.animation_manager.win.b_red = max(0.0, min(1.0, value))

    @property
    def green(self):
        return self.animation_manager.win.b_green

    @green.setter
    def green(self, value):
        self.animation_manager.win.b_green = max(0.0, min(1.0, value))

    @property
    def blue(self):
        return self.animation_manager.win.b_blue

    @blue.setter
    def blue(self, value):
        self.animation_manager.win.b_blue = max(0.0, min(1.0, value))

    def start(self, speed=1.0):
        """Starting the animation at the specified speed"""
        self.speed = max(0.1, min(5.0, speed))  # Speed limit
        self.is_running = True
        self.timer.start(16)  # ~60 FPS

    def stop(self, smooth=True):
        """Stop animation"""
        self.is_running = False
        self.target_rgb = (0.0, 0.0, 0.0)
        if not smooth:
            self._reset_colors()
            self.timer.stop()

    def update_colors(self):
        """Updating color values"""
        if self.is_running:
            # Smooth shade change
            self.current_hue = (self.current_hue + 0.6 * self.speed) % 360
            self.target_rgb = self.hsv_to_rgb(self.current_hue, 1.0, 1.0)

        # Smooth interpolation
        self.win.b_red = round(self.lerp(self.win.b_red, self.target_rgb[0], 0.15), 4)
        self.win.b_green = round(self.lerp(self.win.b_green, self.target_rgb[1], 0.15), 4)
        self.win.b_blue = round(self.lerp(self.win.b_blue, self.target_rgb[2], 0.15), 4)

        # Checking animation completion
        if not self.is_running and all(c < 0.01 for c in (self.win.b_red, self.win.b_green, self.win.b_blue)):
            self._reset_colors()
            self.timer.stop()

    def _reset_colors(self):
        """Reset colors to 0"""
        self.win.b_red = 0.0
        self.win.b_green = 0.0
        self.win.b_blue = 0.0

    @staticmethod
    def hsv_to_rgb(h, s, v):
        """Converting HSV to RGB (returns 0.0-1.0)"""
        h /= 60.0
        i = math.floor(h)
        f = h - i
        p = v * (1 - s)
        q = v * (1 - s * f)
        t = v * (1 - s * (1 - f))

        if i == 0:
            return (v, t, p)
        elif i == 1:
            return (q, v, p)
        elif i == 2:
            return (p, v, t)
        elif i == 3:
            return (p, q, v)
        elif i == 4:
            return (t, p, v)
        else:
            return (v, p, q)

    @staticmethod
    def lerp(a, b, t):
        """Linear interpolation for values 0-1"""
        return a + (b - a) * t

    def set_solid_color(self, r, g, b, fade_duration=0):
        """Color setting with optional smooth transition"""
        if fade_duration > 0:
            # Smooth transition to a new color
            self.fade_to_color(r, g, b, fade_duration)
        else:
            # Instant installation
            self.stop(smooth=False)
            self.win.b_red = max(0.0, min(1.0, r))
            self.win.b_green = max(0.0, min(1.0, g))
            self.win.b_blue = max(0.0, min(1.0, b))

    def fade_to_color(self, r, g, b, duration=10000):
        """Smooth transition to a new color"""
        self.stop(smooth=False)

        self.anim_red = QPropertyAnimation(self, b"red")
        self.anim_green = QPropertyAnimation(self, b"green")
        self.anim_blue = QPropertyAnimation(self, b"blue")

        for anim, start, end in zip(
                [self.anim_red, self.anim_green, self.anim_blue],
                [self.red, self.green, self.blue],
                [r, g, b]
        ):
            anim.setDuration(duration)
            anim.setStartValue(start)
            anim.setEndValue(end)
            anim.setEasingCurve(QEasingCurve.InOutQuad)

        self.anim_group = QParallelAnimationGroup()
        for anim in [self.anim_red, self.anim_green, self.anim_blue]:
            self.anim_group.addAnimation(anim)

        self.anim_group.start()

    def fade_to_zero(self, duration=1000):
        """Smooth fading of the current color to zero"""
        self.stop(smooth=False)  # Stop the current animations

        # Creating animations for each channel
        self.anim_red = QPropertyAnimation(self, b"red")
        self.anim_green = QPropertyAnimation(self, b"green")
        self.anim_blue = QPropertyAnimation(self, b"blue")

        # Setting up animations
        for anim, start_val in zip(
                [self.anim_red, self.anim_green, self.anim_blue],
                [self.red, self.green, self.blue]):
            anim.setDuration(duration)
            anim.setStartValue(start_val)
            anim.setEndValue(0.0)
            anim.setEasingCurve(QEasingCurve.OutQuad)

        # All animations Start
        self.anim_group = QParallelAnimationGroup()
        for anim in [self.anim_red, self.anim_green, self.anim_blue]:
            self.anim_group.addAnimation(anim)

        self.anim_group.start()

    def enable_pulse(self, enable=True, speed=5):
        """Switching on/off the pulse"""
        if enable:
            def pulse_update():
                pulse_val = (math.sin(time.time() * speed) + 1) / 2  # 0-1
                self.win.b_red *= pulse_val
                self.win.b_green *= pulse_val
                self.win.b_blue *= pulse_val

            self.color_animator.timer.timeout.disconnect()
            self.color_animator.timer.timeout.connect(pulse_update)
        else:
            self.color_animator.timer.timeout.disconnect()
            self.color_animator.timer.timeout.connect(self.color_animator.update_colors)

    def enable_glow(self, intensity=0.3):
        """Adds a soft glow effect"""
        self.glow_intensity = max(0.1, min(1.0, intensity))

    def set_mood(self, mood):
        """Sets the color palette to suit your mood"""
        moods = {
            'happy': (1.0, 0.9, 0.5),  # Warm yellow
            'calm': (0.4, 0.7, 1.0),  # Blue
            'energy': (1.0, 0.2, 0.3),  # Bright red
            'magic': (0.7, 0.0, 1.0)  # Purple
        }
        self.color_anim.stop(smooth=False)
        self.win.b_red, self.win.b_green, self.win.b_blue = moods.get(mood, (0, 0, 0))

    def on_audio_peak(self, volume):
        """Called for audio clips"""
        if self.color_anim.is_running:
            self.win.b_red = min(1.0, self.win.b_red + volume * 0.2)
            self.win.b_blue = min(1.0, self.win.b_blue + volume * 0.1)