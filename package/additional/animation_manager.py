from PySide6.QtCore import QSize, QObject, QTimer, QPropertyAnimation, QEasingCurve, QVariantAnimation, \
    QParallelAnimationGroup, QSequentialAnimationGroup, QPoint
from PySide6.QtGui import QMovie, Qt
from PySide6.QtWidgets import QWidget, QApplication, QGraphicsOpacityEffect

from package import resources
import weakref
import uuid
import warnings
import random
import time
import math
import json
import os
import live2d.v3 as live2d
from .models_manager import ModelsManager
from .resource_manager import ResourceManager

class AnimationsManager:
    """Main Animation Manager"""
    def __init__(self, win):
        # self.model = self.win.model
        self.win = win
        # LOGS
        self._log_callbacks = False

        # Init animators
        self.animation_player = AnimationPlayer(self)
        self.transform_animator = TransformAnimator(self)
        self.blink_animator = BlinkAnimator(self)
        self.opacity_animator = OpacityAnimator(self)
        self.bounce_animator = BounceAnimator(self)
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

        for name, path in motions.items():
            try:
                motion_index = self.win.model.LoadExtraMotion("Extra", path)

                # Save motion index
                if not hasattr(self, '_extra_motion_indices'):
                    self._extra_motion_indices = {}
                self._extra_motion_indices[name] = motion_index

                if self.win.callbacks_log:
                    print(f"[Motion] Loaded extra motion '{name}' with index {motion_index} from {path}")

            except Exception as e:
                print(f"[Error] Failed to load extra motion '{name}': {e}")

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
    def play_animation(self, anim_type: str, group_or_id, no=None, priority=None,
                       custom_start=None, custom_finish=None):
        """
        Proxy-Method for AnimationPlayer.play_animation
        """
        if isinstance(priority, str):
            PRIORITY_MAP = {
                "FORCE": live2d.MotionPriority.FORCE,
                "NORMAL": live2d.MotionPriority.NORMAL,
                "IDLE": live2d.MotionPriority.IDLE
            }
            priority = PRIORITY_MAP.get(priority.upper(), priority)

        return self.animation_player.play_animation(
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

    def play_random_flicker_shape(self, stop_after_ms=7000):
        """Play random flicker color pulsation"""
        random_shape = self.color_animator.get_random_flicker_shape()
        self.color_animator.set_pulsating_color(
            r=random.randint(100, 255),
            g=random.randint(100, 255),
            b=random.randint(100, 255),
            pulse_shape=random_shape,
            pulse_duration=random.randint(1000, 4000),
            stop_after_ms=stop_after_ms,
            unique_id=f"random_flicker_{int(time.time())}"
        )

    def play_color_pulse(self, r, g, b,
                         pulse_duration=2000,
                         min_brightness=0.3,
                         max_brightness=1.0,
                         pulse_shape="sine",
                         fade_in_duration=500,
                         infinite=True,
                         pulse_count=None,
                         stop_after_ms=None,
                         stop_fade_out=True,
                         stop_fade_duration=500,
                         unique_id=None,
                         **extra_kwargs):
        """
            Proxy method for set_pulsating_color.

            All parameters are passed to color_animator.set_pulsating_color()

            Args:
                r, g, b: RGB base color (0-255 or 0.0-1.0)
                pulse_duration: Duration of one pulsation cycle in ms
                min_brightness: Minimum color brightness (0.0 - 1.0)
                max_brightness: Maximum color brightness (0.0 - 1.0)
                pulse_shape: Pulse shape
                fade_in_duration: Smooth start of pulse (0 for instant)
                infinite: Endless ripple
                pulse_count: Number of pulse (if not infinite)
                stop_after_ms: Automatically stop after X milliseconds
                stop_fade_out: Smooth stop when autostop
                stop_fade_duration: Duration of attenuation when autostop
                unique_id: A unique identifier for management
            """

        params = {
            'r': r, 'g': g, 'b': b,
            'pulse_duration': pulse_duration,
            'min_brightness': min_brightness,
            'max_brightness': max_brightness,
            'pulse_shape': pulse_shape,
            'fade_in_duration': fade_in_duration,
            'infinite': infinite,
            'pulse_count': pulse_count,
            'stop_after_ms': stop_after_ms,
            'stop_fade_out': stop_fade_out,
            'stop_fade_duration': stop_fade_duration,
            'unique_id': unique_id,
            **extra_kwargs
        }

        return self.color_animator.set_pulsating_color(**params)

    def modify_color_pulse(self, pulse_id, pulse_duration=500, pulse_shape="triangle", max_brightness=1.0):
        """Change color pulse Params"""
        self.color_animator.modify_pulse(
            pulse_id=pulse_id,
            pulse_duration=pulse_duration, # Ускорить пульсацию
            pulse_shape=pulse_shape, # Изменить форму
            max_brightness=max_brightness) # Увеличить максимальную яркость

    def stop_color_pulse(self):
        """Stop color pulse"""
        self.color_animator.stop_pulse()

    def stop_specific_color_pulse(self, pulse_id, fade_out=True, fade_duration=1000):
        """Stop specific color pulse on id"""
        self.color_animator.stop_pulse(pulse_id=pulse_id,
                                       fade_out=fade_out,
                                       fade_duration=fade_duration)

    def animate_bounce_continuous(self, target, **kwargs):
        return self.bounce_animator.animate_bounce_continuous(target, **kwargs)

    def animate_bounce(self, target, **kwargs):
        return self.bounce_animator.animate_bounce(target, **kwargs)

    def animate_scale_bounce(self, target, **kwargs):
        return self.bounce_animator.animate_scale_bounce(target, **kwargs)

    def stop_scale_bounce(self, target):
        self.bounce_animator.stop_scale_bounce(target)

    def stop_bounce(self, target):
        self.bounce_animator.stop_bounce(target)

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

    def play_animation(self, anim_type: str, group_or_id, no=None, priority=None,
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
            self.win.model.StartRandomMotion(
                str(group_or_id),  # Group (str)
                priority,
                onStart=callbacks['start'],
                onFinish=callbacks['finish']
            )
        elif anim_type == 'Motion':
            self.win.model.StartMotion(
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
            # For Special animations, replace no with "id + name"
            if group == "Special":
                anim_name = self._get_special_animation_name(no)
                display_no = f"{no} ({anim_name})"
            else:
                display_no = no

            print(f"Animation {group} {display_no} start - blink off")

        self.animation_manager.blink_animator.set_blink_enabled(False)

    def _handle_motion_finish(self, group, no):
        """Callback with Animation Finish"""
        if not self.animation_manager.transform_animator.transform:
            self.win.model.ResetAllParameters()
        if group != "Idle":  # If the NON-idle animation has ended
            self._reset_idle_state()
            self.animation_manager.blink_animator.set_blink_enabled(True)
        if self._log_callbacks:
            # For Special animations, replace no with "id + name"
            if group == "Special":
                anim_name = self._get_special_animation_name(no)
                display_no = f"{no} ({anim_name})"
            else:
                display_no = no
            print(f"Animation {group} {display_no} finish - blink on")

        # Additionally: reset the eyes to the open state
        #self.model.SetParameterValueById("ParamEyeLOpen", 1.0)
        #self.model.SetParameterValueById("ParamEyeROpen", 1.0)
        #self.model.SetParameterValueById("ParamMouthOpenY", 0)

    def _get_special_animation_name(self, no: int) -> str:
        """Get Special animation name by number"""
        special_animations = {
            0: "Aah", 1: "Bye", 2: "Fun", 3: "Joy", 4: "Love", 5: "Menace",
            6: "Muscle", 7: "Sad", 8: "Sigh", 9: "Sleep", 10: "Sleepy",
            11: "Sleepy Alt", 12: "Sleepy Talk", 13: "Stagger", 14: "Surprised",
            15: "Walk", 16: "What", 17: "Yawn", 18: "Yawn Alt", 19: "Yeah"
        }
        return special_animations.get(no, f"Unknown")

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
        self.win.model.StartRandomMotion("Idle", live2d.MotionPriority.IDLE,
                                     onStart=lambda g, n: self._handle_idle_start(g, n),
                                     onFinish=lambda g, n: self._handle_idle_finish(g, n)
                                     )
        self._is_idle_playing = True
        self._last_idle_time = time.monotonic()
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
                anim_type='Motion',
                group_or_id=profile['group'],
                no=anim_id,
                priority=profile.get('priority', live2d.MotionPriority.FORCE)
            )
        else:
            self.play_animation(
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
            'last_blink': time.monotonic(),
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
            if time.monotonic() - self._blink_state['last_blink'] > self._blink_state['next_delay']:
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
            self.win.model.SetParameterValueById("ParamEyeLOpen",
                                                               base_value * random.uniform(0.95, 1.0))
            self.win.model.SetParameterValueById("ParamEyeROpen",
                                                               base_value * random.uniform(0.98, 1.0))

    def _start_new_blink(self):
        """Initialize new blink"""
        self._blink_state.update({
            'is_active': True,
            'progress': 0.0,
            'last_blink': time.monotonic(),
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

        self.animations = {}

    @property
    def win(self):
        """Actual window link"""
        return self.animation_manager.win

    def get_anim_for_object(self, obj):
        """Returns a unique animator for the object"""
        obj_id = id(obj)
        if obj_id not in self.animations:
            self.animations[obj_id] = QVariantAnimation()
        return self.animations[obj_id]

    def animate_opacity(self, source, start, end, duration=500, easing="linear", on_finished=None):
        """Animation of character transparency via QVariantAnimation"""
        # Set base params
        self.anim = self.get_anim_for_object(source)
        self.anim.stop()

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            try:
                self.anim.valueChanged.disconnect()
            except (RuntimeError, TypeError):
                pass
            try:
                self.anim.finished.disconnect()
            except (RuntimeError, TypeError):
                pass

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
        self.anim.setEasingCurve(easing_curve)

        self.anim.valueChanged.connect(source.SetOutputOpacity)

        if callable(on_finished):
            self.anim.finished.connect(on_finished)

        self.anim.start()

class BounceAnimator:
    """Universal bouncing animator for any object"""
    def __init__(self, animation_manager):
        self.animation_manager = animation_manager
        self.bounce_loops = {}
        self.bounce_animations = {}


        self.easing_curves = {
            "linear": QEasingCurve.Linear,
            "out_quad": QEasingCurve.OutQuad,
            "out_bounce": QEasingCurve.OutBounce,
            "out_cubic": QEasingCurve.OutCubic,
            "in_out_quad": QEasingCurve.InOutQuad,
        }

    def _get_easing(self, name):
        """get easing curve on name"""
        return self.easing_curves.get(name, QEasingCurve.Linear)

    def _get_widget(self, target):
        """Universal widget retrieval from any object"""

        if isinstance(target, QWidget):
            return target

        if hasattr(target, 'label') and isinstance(target.label, QWidget):
            return target.label

        if hasattr(target, 'get_target_widget') and callable(target.get_target_widget):
            widget = target.get_target_widget()
            if isinstance(widget, QWidget):
                return widget

        if hasattr(target, 'widget') and isinstance(target.widget, QWidget):
            return target.widget

        return None

    def _cleanup_animation(self, anim_id):
        """Clearing a completed animation"""
        if anim_id in self.bounce_animations:
            del self.bounce_animations[anim_id]

    # ============= Public Methods =============

    def animate_bounce(self, target, height=30, duration=800,
                       easing_up="out_quad", easing_down="out_bounce",
                       on_finished=None):
        """Single bounce animation"""
        widget = self._get_widget(target)
        if not widget:
            print(f"Warning: Cannot get widget from {target}")
            return None

        try:
            start_pos = widget.pos()
            group = QSequentialAnimationGroup()

            # Вверх
            anim_up = QPropertyAnimation(widget, b"pos")
            anim_up.setDuration(duration // 2)
            anim_up.setStartValue(start_pos)
            anim_up.setEndValue(QPoint(start_pos.x(), start_pos.y() - height))
            anim_up.setEasingCurve(self._get_easing(easing_up))

            # Вниз
            anim_down = QPropertyAnimation(widget, b"pos")
            anim_down.setDuration(duration // 2)
            anim_down.setStartValue(QPoint(start_pos.x(), start_pos.y() - height))
            anim_down.setEndValue(start_pos)
            anim_down.setEasingCurve(self._get_easing(easing_down))

            group.addAnimation(anim_up)
            group.addAnimation(anim_down)

            # Уникальный ID
            anim_id = f"bounce_{id(target)}_{id(widget)}_{int(time.time() * 1000)}"

            self.bounce_animations[anim_id] = {
                'target': weakref.ref(target) if hasattr(target, '__class__') else target,
                'widget': weakref.ref(widget),
                'animation': group
            }

            if on_finished:
                group.finished.connect(on_finished)

            group.finished.connect(lambda: self._cleanup_animation(anim_id))

            QTimer.singleShot(0, group.start)
            return anim_id

        except Exception as e:
            print(f"Error in animate_bounce: {e}")
            return None

    def animate_bounce_continuous(self, target,
                                  height=30,
                                  bounce_duration=800,
                                  bounces=3,
                                  total_duration=10000,
                                  on_finished=None):
        """
        Continuous bounce animation

        Args:
            target: target object
            height: jump height
            bounce_duration: jump duration
            bounces: the number of jumps in one iteration
            total_duration: animation duration
            on_finished: callback when animation is finished
        """

        widget = self._get_widget(target)
        if not widget:
            return None

        loop_id = f"bounce_loop_{id(target)}_{int(time.time() * 1000)}"

        end_time = time.time() + (total_duration / 1000.0)

        def bounce_iteration():
            if loop_id not in self.bounce_loops:
                return

            if time.time() >= end_time:
                # Завершаем
                if loop_id in self.bounce_loops:
                    del self.bounce_loops[loop_id]
                if on_finished:
                    on_finished()
                return

            self.animate_bounce_multiple(
                target=target,
                height=height,
                duration=bounce_duration,
                bounces=bounces,
                on_finished=lambda: QTimer.singleShot(50, bounce_iteration)
            )

        self.bounce_loops[loop_id] = {
            'target_id': id(target),
            'end_time': end_time
        }

        QTimer.singleShot(0, bounce_iteration)

        return loop_id

    def animate_bounce_multiple(self, target, height=30, duration=800,
                                bounces=3, damping=0.7, on_finished=None):
        """Multiple bouncing with attenuation"""

        widget = self._get_widget(target)
        if not widget:
            return None

        try:
            start_pos = widget.pos()
            group = QSequentialAnimationGroup()

            for i in range(bounces):
                current_height = height * (damping ** i)

                anim_up = QPropertyAnimation(widget, b"pos")
                anim_up.setDuration(duration // 2)
                anim_up.setStartValue(widget.pos() if i == 0 else widget.pos())
                anim_up.setEndValue(QPoint(start_pos.x(), start_pos.y() - int(current_height)))
                anim_up.setEasingCurve(self._get_easing("out_quad"))

                anim_down = QPropertyAnimation(widget, b"pos")
                anim_down.setDuration(duration // 2)
                anim_down.setStartValue(QPoint(start_pos.x(), start_pos.y() - int(current_height)))
                anim_down.setEndValue(start_pos)
                anim_down.setEasingCurve(self._get_easing("out_bounce"))

                group.addAnimation(anim_up)
                group.addAnimation(anim_down)

            anim_id = f"bounce_multi_{id(target)}_{int(time.time() * 1000)}"

            self.bounce_animations[anim_id] = {
                'target': weakref.ref(target) if hasattr(target, '__class__') else target,
                'widget': weakref.ref(widget),
                'animation': group
            }

            if on_finished:
                group.finished.connect(on_finished)

            group.finished.connect(lambda: self._cleanup_animation(anim_id))

            QTimer.singleShot(0, group.start)
            return anim_id

        except Exception as e:
            print(f"Error in animate_bounce_multiple: {e}")
            return None

    def animate_scale_bounce(self, target, start_scale=1.0, end_scale=1.2,
                             duration=300, easing_up="out_quad", easing_down="in_out_quad",
                             on_finished=None):
        """
        Bounce scale animation for any object with the scale property

            Args:
                target: the object to animate (must have the scale and anim_scale properties)
                start_scale: the initial scale
                end_scale: the final scale (peak)
                duration: the duration of the animation in ms
                easing_up: the curve for increasing
                easing_down: the curve for decreasing
                on_finished: the callback when the animation is complete
        """

        if not hasattr(target, 'anim_scale') or not hasattr(target, 'scale'):
            print(f"Warning: Target {target} must have 'anim_scale' property")
            return None

        try:
            if not hasattr(self, '_original_scales'):
                self._original_scales = {}

            target_id = id(target)
            self._original_scales[target_id] = getattr(target, 'scale', start_scale)

            group = QSequentialAnimationGroup()

            scale_up = QPropertyAnimation(target, b"anim_scale")
            scale_up.setDuration(duration // 2)
            scale_up.setStartValue(start_scale)
            scale_up.setEndValue(end_scale)
            scale_up.setEasingCurve(self._get_easing(easing_up))

            scale_down = QPropertyAnimation(target, b"anim_scale")
            scale_down.setDuration(duration // 2)
            scale_down.setStartValue(end_scale)
            scale_down.setEndValue(start_scale)
            scale_down.setEasingCurve(self._get_easing(easing_down))

            group.addAnimation(scale_up)
            group.addAnimation(scale_down)

            anim_id = f"scale_bounce_{target_id}_{int(time.time() * 1000)}"

            if not hasattr(self, 'scale_animations'):
                self.scale_animations = {}

            self.scale_animations[anim_id] = {
                'target': weakref.ref(target) if hasattr(target, '__class__') else target,
                'target_id': target_id,
                'animation': group,
                'original_scale': start_scale
            }

            if on_finished:
                group.finished.connect(on_finished)

            def cleanup():
                if anim_id in self.scale_animations:
                    # Восстанавливаем оригинальный масштаб если нужно
                    # target.scale = self._original_scales.get(target_id, start_scale)
                    del self.scale_animations[anim_id]
                if target_id in self._original_scales:
                    del self._original_scales[target_id]

            group.finished.connect(cleanup)

            QTimer.singleShot(0, group.start)
            return anim_id

        except Exception as e:
            print(f"Error in animate_scale_bounce: {e}")
            import traceback
            traceback.print_exc()
            return None

    def stop_scale_bounce(self, target):
        """Stop the zoom animation for an object"""
        target_id = id(target)

        if hasattr(self, 'scale_animations'):
            to_delete = []
            for anim_id, anim_data in self.scale_animations.items():
                if anim_data.get('target_id') == target_id:
                    if 'animation' in anim_data:
                        anim_data['animation'].stop()
                    to_delete.append(anim_id)

            for anim_id in to_delete:
                del self.scale_animations[anim_id]

    def stop_bounce(self, target):
        """Stop bounce animations for an object"""
        target_id = id(target)

        to_delete = []
        for anim_id, anim_data in self.bounce_animations.items():
            if anim_data.get('target_id') == target_id or \
                    (hasattr(anim_data.get('target'), 'id') and anim_data['target']() is target):
                if 'animation' in anim_data:
                    anim_data['animation'].stop()
                to_delete.append(anim_id)

        for anim_id in to_delete:
            del self.bounce_animations[anim_id]

        to_delete = []
        for loop_id, loop_data in self.bounce_loops.items():
            if loop_data.get('target_id') == target_id:
                to_delete.append(loop_id)

        for loop_id in to_delete:
            del self.bounce_loops[loop_id]

    def stop_all_bounces(self):
        """Stop all bounce animations"""
        for anim_data in self.bounce_animations.values():
            if 'animation' in anim_data:
                anim_data['animation'].stop()

        self.bounce_animations.clear()
        self.bounce_loops.clear()

class TransformAnimator:
    """Character transformation animation management"""
    def __init__(self, animation_manager):
        self.animation_manager = animation_manager

        self._win = None

        self.win.transformMovie = QMovie()

        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._on_animation_tick)

        # Transform Animation State
        self.transform_text = False
        self.transform = False
        self.current_animation_win = None
        self.animation_phase = 0  # 0-idle, 1-fade out, 2-model swap, 3-fade in

        self._current_transform_in = None
        self._current_transform_out = None

        # Сustom mode transformation state
        self.transform_mode = None
        self._custom_mode = False
        self._custom_timer = QTimer()
        self._custom_timer.timeout.connect(self._on_custom_tick)
        self._custom_phase = 0
        self._custom_elapsed = 0
        self._custom_fade_out_duration = 5000
        self._custom_fade_in_duration = 5000
        self._custom_swap_delay = 500

    @property
    def win(self):
        """Actual window link"""
        return self.animation_manager.win

    def _cleanup_current_movies(self):
        try:
            if self._current_transform_in:
                self._current_transform_in.stop()
                self._current_transform_in.deleteLater()
                self._current_transform_in = None

            if self._current_transform_out:
                self._current_transform_out.stop()
                self._current_transform_out.deleteLater()
                self._current_transform_out = None

            if hasattr(self.win, 'transformLabel') and self.win.transformLabel:
                old_movie = self.win.transformLabel.movie()
                if old_movie:
                    old_movie.stop()
                    old_movie.deleteLater()
                self.win.transformLabel.setMovie(None)
                self.win.transformLabel.clear()

        except Exception as e:
            print(f"Error cleaning up movies: {e}")

    # Transform Animations
    def play_transform_animation(self):
        """Start full transformation sequence"""
        if self.animation_phase != 0:
            return

        transform_mode = self.win.resource_manager.get_transform_mode(self.win.character_name)

        self._cleanup_current_movies()
        self.current_animation_win = self.win
        self.animation_phase = 1
        self.win.input_handler.input_lock = True
        self.win.transform = True
        self.win.canvas.SetOutputOpacity(1.0)

        if transform_mode == "Normal":
            self._custom_mode = False
            self.animation_manager.start_rainbow_effect(speed=2.0)
            self.win.particle_overlay.particle_presets.transform(name=self.win.character_name)
            self.win.particle_overlay.particle_presets.transform_fairy_dust(particle_duration=0.75)
            anim_index = 0

            movie_path = self.animation_manager.resource_manager.load_animation("transform_in")
            self._current_transform_in = QMovie(movie_path)
            self._current_transform_in.setCacheMode(QMovie.CacheAll)

            self.win.transformLabel.setMovie(self._current_transform_in)
            self.win.transformLabel.raise_()
            self.win.transformLabel.movie().setScaledSize(self._calculate_animation_size())
            self.win.transformLabel.move(int(self.win.trm_mx * self.win.models_scale),
                                         int(self.win.trm_my * self.win.models_scale))
            self._current_transform_in.start()
            self.win.transformLabel.show()

            self.animation_timer.start(16)  # 60 FPS

        elif transform_mode == "Evil":
            self._custom_mode = True
            self.animation_manager.play_color_pulse(r=255, g=0, b=0, pulse_shape="torch")
            self.win.particle_overlay.particle_presets.evil_transform()
            #self.win.particle_overlay.particle_presets.transform_fairy_dust(particle_duration=0.75)
            anim_index = 1

            # Start custom mode timer
            self._custom_phase = 1  # fade out phase
            self._custom_elapsed = 0
            self._custom_timer.start(16)  # 60 FPS for smooth opacity
        # Setup transform_in animation
        self._play_model_animation(anim_index)

    def _on_custom_tick(self):
        """Handle Custom mode transformation using regular timer"""
        if not self.current_animation_win:
            self._custom_timer.stop()
            return

        self._win = self.current_animation_win
        self._custom_elapsed += 16  # Increment by timer interval (16ms)

        if self._custom_phase == 1:
            # Fade out phase
            self._process_custom_fade_out()
        elif self._custom_phase == 2:
            # Swap phase - wait a bit then execute swap
            self._process_custom_swap()
        elif self._custom_phase == 3:
            # Fade in phase
            self._process_custom_fade_in()

    def _process_custom_fade_out(self):
        """Handle fade out for Custom mode"""
        progress = min(self._custom_elapsed / self._custom_fade_out_duration, 1.0)
        self.win.canvas.SetOutputOpacity(1.0 - progress)

        # Close dialog at half fade
        if self._custom_elapsed >= self._custom_fade_out_duration / 2:
            self.win.talk_widget.close_dialog_after_animation()

        # Complete fade out
        if self._custom_elapsed >= self._custom_fade_out_duration:
            self._custom_phase = 2
            self._custom_elapsed = 0

    def _process_custom_swap(self):
        """Handle model swap for Custom mode"""
        transform_mode = self.win.resource_manager.get_transform_mode(self.win.character_name)
        # Wait for swap delay
        if self._custom_elapsed >= self._custom_swap_delay:
            # Execute model swap
            self._execute_model_swap_no_animation()

            # Prepare for fade in
            self.win.canvas.SetOutputOpacity(0.0)
            if transform_mode == "Evil":
                self._custom_mode = True
                #self.win.particle_overlay.particle_presets.transform_fairy_dust(particle_duration=0.75)
            #self.win.particle_overlay.particle_presets.transform(name=self.win.character_name, reverse=True)

            self._custom_phase = 3
            self._custom_elapsed = 0

    def _process_custom_fade_in(self):
        """Handle fade in for Custom mode"""
        progress = min(self._custom_elapsed / self._custom_fade_in_duration, 1.0)
        self.win.canvas.SetOutputOpacity(progress)

        # Complete fade in
        if self._custom_elapsed >= self._custom_fade_in_duration:
            self._finalize_custom_transformation()

    def _execute_model_swap_no_animation(self):
        """Execute model transformation without QMovie animations"""
        try:
            target_name = self.win.resource_manager.get_alt_form_name(self.win.character_name)
            if not target_name:
                return
            self.win.talk_widget.talk_update = False
            self.win.character_name = target_name
            self.win.models_manager.update_model(self.win)

            self.win.character.transform_exp_show = True
            self.win.character.transform_text_show = True
            self.win.character.expressions.set_funny_expression(fade_out=30000)
        except Exception as e:
            print(f"Error in custom mode swap: {e}")

    def _finalize_custom_transformation(self):
        """Cleanup after Custom transformation"""
        try:
            self._custom_timer.stop()
            self._custom_phase = 0
            self._custom_elapsed = 0
            self._custom_mode = False

            self.win.canvas.SetOutputOpacity(1.0)
            self.win.input_handler.input_lock = False
            self.win.transform_lock = False
            self.win.talk_widget.talk_update = True
            self.transform = self.win.transform = False
            self.win.character.state.set_transformed_state()

            self.win.character.transform_exp_show = False
            self.win.character.transform_text_show = False

        finally:
            self.win.particle_overlay.stop_particle_system()
            self.animation_manager.stop_color_pulse()
            self.current_animation_win = None
            self.animation_phase = 0

    def _on_animation_tick(self):
        """Animation phases (Normal mode only)"""
        if not self.current_animation_win or self._custom_mode:
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
        if not self._current_transform_in:
            return

        current_frame = self._current_transform_in.currentFrameNumber()
        total_frames = self._current_transform_in.frameCount()

        fade_start = int(total_frames * 0.70)
        if current_frame >= fade_start:
            progress = (current_frame - fade_start) / (total_frames - fade_start)
            self.win.canvas.SetOutputOpacity(1.0 - progress)

        if current_frame >= total_frames - 3:
            self._current_transform_in.stop()
            self.animation_phase = 2

        if current_frame >= (total_frames - 3) / 2:
            self.win.talk_widget.close_dialog_after_animation()

    def _execute_model_swap(self):
        """Execute model transformation using your existing methods"""
        try:
            self._transform_change()
        finally:
            self._transform_animation_reset()

    def _transform_animation_reset(self):
        """Reset animation"""
        if self._current_transform_in:
            self._current_transform_in.stop()
            self._current_transform_in.deleteLater()
            self._current_transform_in = None

        self.win.transformLabel.movie().setScaledSize(QSize(1, 1))
        self.win.transformLabel.close()

    def _init_fade_in(self):
        """Initialize transform_out animation"""
        if self._current_transform_out:
            self._current_transform_out.stop()
            self._current_transform_out.deleteLater()
            self._current_transform_out = None

        movie_path = self.animation_manager.resource_manager.load_animation("transform_out")
        self._current_transform_out = QMovie(movie_path)
        self._current_transform_out.setCacheMode(QMovie.CacheAll)

        self.win.transformLabel.setMovie(self._current_transform_out)
        self.win.transformLabel.movie().setScaledSize(
            self._calculate_animation_size()
        )
        self._current_transform_out.start()
        self.win.transformLabel.move(int(self.win.trm_mx * self.win.models_scale),
                                     int(self.win.trm_my * self.win.models_scale))
        self.win.transformLabel.show()

        self.win.canvas.SetOutputOpacity(0.0)
        self.win.particle_overlay.particle_presets.transform(name=self.win.character_name, reverse=True)

    def _process_fade_in(self):
        """Handle transform_out animation with delayed opacity restore"""
        if not self._current_transform_out:
            return

        current_frame = self._current_transform_out.currentFrameNumber()
        total_frames = self._current_transform_out.frameCount()

        fade_start = int(total_frames * 0.15)
        fade_end = int(total_frames * 0.7)

        if current_frame < fade_start:
            self.win.canvas.SetOutputOpacity(0.0)
        elif fade_start <= current_frame <= fade_end:
            progress = (current_frame - fade_start) / (fade_end - fade_start)
            self.win.canvas.SetOutputOpacity(progress)
        else:
            self.win.canvas.SetOutputOpacity(1.0)

        if current_frame >= total_frames - 3:
            self._finalize_transformation()

    def _finalize_transformation(self):
        """Cleanup after transformation"""
        try:
            if self._current_transform_out:
                self._current_transform_out.stop()
                self._current_transform_out.deleteLater()
                self._current_transform_out = None

            self.win.transformMovie.stop()
            self.win.transformLabel.close()
            self.win.canvas.SetOutputOpacity(1.0)
            self.win.input_handler.input_lock = False
            self.win.transform_lock = False
            self.win.talk_widget.talk_update = True
            self.transform = self.win.transform = False
            self.win.character.state.set_transformed_state()

            self.animation_manager.stop_rainbow_effect()

            self.win.character.transform_exp_show = False
            self.win.character.transform_text_show = False

            self._cleanup_current_movies()

        finally:
            self.win.particle_overlay.stop_particle_system()
            self.animation_timer.stop()
            self.current_animation_win = None
            self.animation_phase = 0

    def _play_model_animation(self, anim_index = 0):
        """Model animation playback"""
        if not self.win.hdd_form:
            self.animation_manager.play_animation(
                anim_type='Motion',
                group_or_id="Unique",
                no=anim_index,
                priority="FORCE",
            )

    def _calculate_animation_size(self):
        """Calculate animation size"""
        return QSize(
            int(self.win.w_resize + self.win.trm_cmx * self.win.models_scale),
            int(self.win.h_resize + self.win.trm_cmy * self.win.models_scale)
        )

    def _transform_change(self):
        target_name = self.win.resource_manager.get_alt_form_name(self.win.character_name)
        if not target_name:
            return
        self.win.talk_widget.talk_update = False
        self.win.character_name = target_name
        self.win.models_manager.update_model(self.win)

        self.win.character.transform_exp_show = True
        self.win.character.transform_text_show = True
        self.win.character.expressions.set_funny_expression(fade_out=30000)

    def stop_all_animations(self):
        """Method for an external call when closing"""
        self._cleanup_current_movies()
        self.animation_timer.stop()
        self._custom_timer.stop()
        self.animation_phase = 0
        self._custom_phase = 0
        self._custom_elapsed = 0
        self._custom_mode = False
        self._animation_active = False

class BodyPartAnimator:
    def __init__(self, animation_manager):
        self.animation_manager = animation_manager
        self.active_parts = {}
        self.body_part_timer = QTimer()
        self.body_part_timer.timeout.connect(self._update_parts)
        self.body_part_timer.setInterval(1)
        self.last_time = time.perf_counter()

    @property
    def win(self):
        return self.animation_manager.win

    @property
    def target_fps(self):
        return self.animation_manager.target_fps

    def add_animation(self, part_id, range=(0, 10), speed=0.1,easing='linear'):
        """Add Body Animation"""
        # Leading to the correct types
        range = (float(range[0]), float(range[1]))
        speed = float(speed)

        if part_id not in self.active_parts:
            # New Animation
            self.active_parts[part_id] = {
                'range': range,
                'speed': speed,
                'value': range[0],
                'direction': 1,
                'easing': easing,
                'active': True,
            }
        else:
            # Update current Animation
            config = self.active_parts[part_id]
            config['range'] = range
            config['speed'] = speed
            config['active'] = True
            config['reset_requested'] = False

            # Smooth transition to new parameters
            if config['value'] < range[0]:
                config['value'] = range[0]
            elif config['value'] > range[1]:
                config['value'] = range[1]

        if not self.body_part_timer.isActive():
            self.last_time = time.perf_counter()
            self.body_part_timer.start()

    def stop_all(self):
        """Stop Animation"""
        for part_id in list(self.active_parts.keys()):
            self.win.model.SetParameterValueById(part_id, 0)
        self.active_parts.clear()
        self.body_part_timer.stop()

    def _update_parts(self):
        """Update Part Values"""
        current_time = time.perf_counter()
        delta_time = current_time - self.last_time
        self.last_time = current_time

        # ANOMALY PROTECTION:
        delta_time = min(delta_time, 0.1)  # Max 100ms (if the window was minimized)
        delta_time = max(delta_time, 0.001)  # Minimum 1ms (error protection)

        # Normalization to target FPS
        normalized_delta = delta_time * self.target_fps

        # Update active animations
        parts_to_remove = []
        for part_id, config in self.active_parts.items():
            try:
                if not config['active']:
                    continue

                # Smooth value change
                new_value = config['value'] + config['direction'] * config['speed'] * normalized_delta

                # Range limitation
                if new_value >= config['range'][1]:
                    new_value = config['range'][1]
                    config['direction'] = -1
                elif new_value <= config['range'][0]:
                    new_value = config['range'][0]
                    config['direction'] = 1

                self.win.model.SetParameterValueById(part_id, new_value)
                config['value'] = new_value

            except Exception as e:
                print(f"Animation error for {part_id}: {e}")
                parts_to_remove.append(part_id)

        # Deleting completed animations
        for part_id in parts_to_remove:
            self._safe_remove_part(part_id)

        if not self.active_parts:
            self.body_part_timer.stop()

    def _safe_remove_part(self, part_id):
        """Safely deleting a part from active_parts"""
        if part_id in self.active_parts:
            try:
                self.win.model.SetParameterValueById(part_id, 0)
            except:
                pass
            del self.active_parts[part_id]

class DragAnimator:
    def __init__(self, animation_manager):
        self.animation_manager = animation_manager
        self.part_animator = BodyPartAnimator(animation_manager)

        self.angle = 0.0
        self.max_angle = 15.0
        self.return_delay = 500  # Delay before return (ms)
        self.return_speed = 0.5  # Return rate (0.1-0.9)
        self.drag_direction_x = 0  # Horizontal direction (-1 to 1)
        self.drag_direction_y = 0  # Vertical direction (-1 to 1)
        self.drag_intensity = 0
        self.max_angle = 10
        self.last_animation_time = 0

        self.vertical_intensity = 0.0  # Adding vertical intensity tracking
        self.return_threshold = 0.1    # Stop threshold for all animations

        # Таймеры
        self.return_timer = QTimer()
        self.return_timer.setSingleShot(True)
        self.return_timer.timeout.connect(self.start_return_animation)

        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_return_animation)

    @property
    def win(self):
        return self.animation_manager.win

    @property
    def profiles(self):
        return self.animation_manager.profiles

    @property
    def current_character(self):
        return self.animation_manager._current_character

    @property
    def frame_delay(self):
        return self.animation_manager.frame_delay

    def start_drag_animation(self, direction_key):
        """Start animation for any direction"""
        profile = self.profiles.get(self.current_character, {})
        drag_config = profile.get('drag_animations', {}).get(direction_key, {})
        animation_speed = round((self.drag_intensity/4),2)
        # print(f"Drag config for {direction_key}: {drag_config}")  # What is contained in the config

        for part_config in drag_config.get('parts', []):
            # print(f"Drag config for {direction_key}, Processing part: {part_config}")  # Output of the current configuration
            try:
                self.part_animator.add_animation(
                    part_id=part_config['part'],
                    range=part_config.get('range', [0, 10]),
                    speed=part_config.get('speed', animation_speed)
                )
            except Exception as e:
                print(f"Animation error for {part_config['part']}: {e}")

    def stop_drag_animation(self):
        """Stop all animations"""
        self.part_animator.stop_all()

    def update_vertical_movement(self, direction_y, intensity):
        """A separate method for vertical movement"""
        self.drag_direction_y = direction_y
        self.drag_intensity = intensity
        # We do not use the tilt angle for vertical movement!
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
            self.animation_timer.setInterval(self.frame_delay)
            self.animation_timer.start()

    def _update_return_animation(self):
        """Smooth return for all types of animations"""
        # Checking ALL the stop conditions
        should_stop = (
                abs(self.angle) < self.return_threshold and  # Horizontal tilt
                abs(self.drag_direction_y) < self.return_threshold and  # Vertical movement
                self.drag_intensity < self.return_threshold  # Overall intensity
        )

        if should_stop:
            # Full stop only when EVERYTHING is completed
            self.angle = 0
            self.drag_direction_y = 0
            self.animation_timer.stop()
            self.part_animator.stop_all()
        else:
            # Smooth horizontal tilt reset
            if abs(self.angle) > self.return_threshold:
                progress = abs(self.angle) / self.max_angle
                slowdown_factor = 0.5 + (1 - progress) * 0.5
                self.angle *= self.return_speed * slowdown_factor

            # Smooth reset of vertical intensity
            if abs(self.drag_direction_y) > self.return_threshold:
                self.drag_direction_y *= self.return_speed

            # Smooth relief of overall intensity
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
        """Stopping all animations with priority"""
        # First, smoothly reset the parameters
        self.angle = 0
        self.drag_direction_y = 0
        self.drag_intensity = 0
        self.apply_rotation()

        # Then we stop animations of body parts
        self.part_animator.stop_all()

        # Stop the timers
        self.animation_timer.stop()
        self.return_timer.stop()

class ColorAnimator(QObject):
    """Color Animation"""
    def __init__(self, animation_manager):
        super().__init__()
        self.animation_manager = animation_manager
        self.color_timer = QTimer()
        self.color_timer.timeout.connect(self.update_colors)

        # Animation Settings
        self.speed = 1.0
        self.is_running = False
        self.current_hue = random.uniform(0, 360)  # 0-360 degress
        self.target_rgb = (0.0, 0.0, 0.0)  # Color range 0-1

        # Pulse Vars
        self.pulse_animations = {}  # Dictionary for storing active pulsations
        self.pulse_timers = {}  # To track the time
        self.pulse_counter = 0  # Counter for unique IDs

        # Timer for cleaning old pulsations
        self.cleanup_timer = QTimer()
        self.cleanup_timer.setInterval(60000)  # Once a minute
        self.cleanup_timer.timeout.connect(self._cleanup_old_pulses)
        self.cleanup_timer.start()

    @property
    def win(self):
        """Actual window link"""
        return self.animation_manager.win

    @property
    def frame_delay(self):
        return self.animation_manager.frame_delay

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
        self.color_timer.start(self.frame_delay)  # ~60 FPS

    def stop(self, smooth=True):
        """Stop animation"""
        self.is_running = False
        self.target_rgb = (0.0, 0.0, 0.0)
        if not smooth:
            self._reset_colors()
            self.color_timer.stop()

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
            self.color_timer.stop()

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

    def _cleanup_old_pulses(self):
        """Clearing pulse that have been hanging for too long"""
        current_time = time.time()
        pulses_to_remove = []

        for pulse_id, pulse_data in self.pulse_animations.items():
            # If the pulsation is hanging for more than 5 minutes, we kill it.
            if current_time - pulse_data['start_time'] > 300:  # 300 sec = 5 min.
                pulses_to_remove.append(pulse_id)
                print(f"⚠️ Clean old pulse complette: {pulse_id}")

        for pulse_id in pulses_to_remove:
            self.stop_pulse(pulse_id, fade_out=False)

    def set_pulsating_color(self, r, g, b,
                            pulse_duration=2000,    # Duration of one cycle in ms
                            min_brightness=0.3,     # Minimum brightness (0.0-1.0)
                            max_brightness=1.0,     # Maximum brightness (0.0-1.0)
                            pulse_shape="sine",     # Pulse shape
                            fade_in_duration=500,   # Gradual onset of pulsation
                            infinite=True,          # Infinite pulsation
                            pulse_count=None,       # Number of pulsations
                            stop_after_ms=None,     # Auto-stop after X ms
                            stop_fade_out=True,     # Smooth stop
                            stop_fade_duration=500, # Attenuation duration
                            unique_id=None):
        """Set pulse collor"""

        # Convert color in 0.0-1.0
        if isinstance(r, int):
            r = r / 255.0
            g = g / 255.0
            b = b / 255.0

        # Generate Unical ID if None
        if unique_id is None:
            unique_id = f"pulse_{self.pulse_counter}"
            self.pulse_counter += 1

        # Stop the previous pulsation with the same ID if there is
        if unique_id in self.pulse_animations:
            self.stop_pulse(unique_id, fade_out=False)

        # Save pulse params
        pulse_data = {
            'base_r': r,
            'base_g': g,
            'base_b': b,
            'pulse_duration': pulse_duration,
            'min_brightness': min_brightness,
            'max_brightness': max_brightness,
            'pulse_shape': pulse_shape,
            'start_time': time.time(),
            'pulse_count': pulse_count,
            'current_pulse': 0,
            'fade_in_progress': fade_in_duration > 0,
            'fade_in_duration': fade_in_duration,
            'fade_in_start': time.time(),
            'infinite': infinite,
            'stop_after_ms': stop_after_ms,
            'stop_fade_out': stop_fade_out,
            'stop_fade_duration': stop_fade_duration,
            'stop_timer': None  # For AutoStop Timer
        }

        # Creating a timer to update the pulse
        timer = QTimer()
        timer.timeout.connect(lambda: self._update_pulse(unique_id))
        timer.start(16)  # ~60 FPS

        # If the auto-stop time is specified, create a timer
        if stop_after_ms and stop_after_ms > 0:
            stop_timer = QTimer()
            stop_timer.setSingleShot(True)
            stop_timer.setInterval(stop_after_ms)
            stop_timer.timeout.connect(lambda: self._auto_stop_pulse(unique_id))
            stop_timer.start()
            pulse_data['stop_timer'] = stop_timer

        self.pulse_timers[unique_id] = timer
        self.pulse_animations[unique_id] = pulse_data

        # If need smooth init
        if fade_in_duration > 0:
            self.win.b_red = 0
            self.win.b_green = 0
            self.win.b_blue = 0
        else:
            # Set initial color
            self._apply_pulse_color(unique_id, 0)

        return unique_id

    def _update_pulse(self, pulse_id):
        """Update color pulse"""
        if pulse_id not in self.pulse_animations:
            return

        pulse_data = self.pulse_animations[pulse_id]
        current_time = time.time()
        elapsed = current_time - pulse_data['start_time']

        # Check smooth start
        if pulse_data['fade_in_progress']:
            fade_elapsed = current_time - pulse_data['fade_in_start']
            fade_progress = min(1.0, fade_elapsed * 1000 / pulse_data['fade_in_duration'])

            if fade_progress >= 1.0:
                pulse_data['fade_in_progress'] = False
                fade_factor = 1.0
            else:
                # Smooth increase in amplitude
                fade_factor = fade_progress
        else:
            fade_factor = 1.0

        # Calculating the progress in the current cycle
        cycle_progress = (elapsed * 1000) % pulse_data['pulse_duration']
        normalized_progress = cycle_progress / pulse_data['pulse_duration']

        # Get the pulse value depending on the shape
        pulse_value = self._get_pulse_value(normalized_progress, pulse_data['pulse_shape'])

        # Check smooth start if need
        if pulse_data['fade_in_progress']:
            pulse_value *= fade_factor

        # Apply collor
        self._apply_pulse_color(pulse_id, pulse_value)

        # We check the number of pulsations (if not infinite)
        if not pulse_data['infinite'] and pulse_data['pulse_count'] is not None:
            completed_cycles = int(elapsed * 1000 // pulse_data['pulse_duration'])
            if completed_cycles >= pulse_data['pulse_count']:
                self.stop_pulse(pulse_id, fade_out=True)

    def _get_pulse_value(self, progress, shape):
        """Return Pulse Value (0.0-1.0) for current form"""
        if shape == "sine":
            # Sinusoid: smooth rise and fall
            return (math.sin(progress * 2 * math.pi - math.pi / 2) + 1) / 2

        elif shape == "triangle":
            # Triangular: linear rise and fall
            if progress < 0.5:
                return progress * 2  # Rise
            else:
                return 2 - progress * 2  # Fall

        elif shape == "sawtooth":
            # Sawtooth: linear growth, sharp decline
            return progress

        elif shape == "reverse_sawtooth":
            # Reverse saw: sharp rise, linear decline
            return 1 - progress

        elif shape == "heartbeat":
            # Heartbeat: two quick beats
            if progress < 0.25:
                return progress * 4  # First beat
            elif progress < 0.3:
                return 1.0  # Pause
            elif progress < 0.55:
                return (progress - 0.3) * 4  # Second beat
            else:
                return max(0, 1 - (progress - 0.55) * 2.2)  # Long Pause

        elif shape == "breath":
            # Breathing: slow inhale, quick exhale
            if progress < 0.7:
                return progress / 0.7  # Slow inhale
            else:
                return 1 - (progress - 0.7) / 0.3  # Qick exhale

        elif shape == "flicker":
            # Flickering lamp effect
            flicker = math.sin(progress * 20 * math.pi) * 0.1 + 0.9
            noise = (math.sin(progress * 37 * math.pi) + 1) * 0.05
            return max(0.3, min(1.0, flicker + noise))

        elif shape == "flicker_zero":
            # Flicker effect with full fade at 0
            import random

            # The frequency of flickering (the more, the more often)
            frequency = 15

            # Basic sinusoidal flicker
            base = math.sin(progress * frequency * math.pi) * 0.5 + 0.5

            # Random "falls" to 0
            if random.random() < 0.15:  # 15% dip change
                # Duration of the dip
                if progress % 0.1 < 0.02:  # dip duration ~2% of the cycle
                    return 0.0

            # Little noise
            noise = random.uniform(-0.1, 0.1)

            return max(0.0, min(1.0, base + noise))

        elif shape == "dip_flicker":
            # Deterministic flicker with regular dips (without random)

            # Main frequency
            base = math.sin(progress * 10 * math.pi) * 0.2 + 0.7

            # Regular dips every 0.2 progress
            dip_frequency = 5  # 5 failures per cycle
            dip_pos = (progress * dip_frequency) % 1.0

            # Form of dip - smooth attenuation and recovery
            if dip_pos < 0.3:
                # Smooth fade
                fade = 1.0 - (dip_pos / 0.3)
                return base * fade * 0.3
            elif dip_pos < 0.6:
                # At the bottom of the dip
                return 0.0
            else:
                # Restore
                recovery = (dip_pos - 0.6) / 0.4
                return base * recovery

            return max(0.0, min(1.0, base))

        elif shape == "sync_flicker":
            # Synchronized flicker with controlled dips
            import random

            # Divide the progress into segments
            segment_count = 8
            segment = int(progress * segment_count)
            segment_progress = (progress * segment_count) % 1.0

            # Predictable seed for the segment
            segment_seed = hash(f"{segment}_{int(progress * 10)}") % 1000
            random.seed(segment_seed)

            # Decide for this segment: will there be a dip?
            has_dip = random.random() < 0.25  # 25% of segments have a dip

            if has_dip:
                # There is a dip in this segment
                dip_position = random.uniform(0.2, 0.8)  # Where in the segment will the dip occur
                dip_width = random.uniform(0.05, 0.2)  # dip width

                if abs(segment_progress - dip_position) < dip_width / 2:
                    # In dip
                    dip_depth = 1.0 - (abs(segment_progress - dip_position) * 2 / dip_width)
                    return dip_depth * random.uniform(0.0, 0.3)  # get to 0
                else:
                    # Outside the gap, there is a normal glow.
                    base = math.sin(progress * 15 * math.pi) * 0.1 + 0.8
                    return max(0.5, min(1.0, base))
            else:
                # The usual flicker without dips
                base = math.sin(progress * 12 * math.pi) * 0.15 + 0.8
                noise = random.uniform(-0.1, 0.1)
                return max(0.6, min(1.0, base + noise))

        elif shape == "wave":
            # Wave Pulse
            wave1 = math.sin(progress * 2 * math.pi) * 0.5 + 0.5
            wave2 = math.sin(progress * 4 * math.pi + math.pi / 3) * 0.3
            return max(0.0, min(1.0, wave1 + wave2))

        elif shape == "torch":
            # Flame/torch effect with sudden drops
            import random

            # The main pulsation frequency
            base_freq = progress * 8 * math.pi
            base_value = (math.sin(base_freq) + 1) * 0.3

            # The main pulsation frequency
            high_freq = progress * 50 * math.pi
            high_value = math.sin(high_freq) * 0.2

            # Random bursts
            spike_chance = math.sin(progress * 6 * math.pi) * 0.5 + 0.5
            if random.random() < spike_chance * 0.3:
                spike = random.uniform(0.5, 1.0)
                # Rapid rise and fall
                spike_duration = 0.05
                local_progress = (progress % spike_duration) / spike_duration
                spike_value = spike * (1 - abs(local_progress - 0.5) * 2)
                high_value += spike_value

            # Sometimes complete fading
            if random.random() < 0.08:  # 8% chance
                fade_duration = 0.03
                if (progress * 100) % 1 < fade_duration:
                    return 0.0

            result = base_value + high_value
            return max(0.0, min(1.0, result))

        elif shape == "broken_bulb":
            # The effect of a faulty light bulb
            import random
            import time

            # Use time for more predictable "random" behavior.
            time_seed = int(time.time() * 10)
            random.seed(time_seed + int(progress * 1000))

            # Basic state: 0 - off, 1 - on, 2 - flicker
            state_progress = progress * 3  # 3 seconds for a full cycle of states

            if state_progress < 1.0:
                # Normal gorenje with slight flicker
                flicker = math.sin(progress * 30 * math.pi) * 0.05 + 0.9
                return max(0.8, min(1.0, flicker))

            elif state_progress < 1.5:
                # Begin to flicker
                if random.random() < 0.7:  # Burn 70% of the time
                    flicker = random.uniform(0.6, 1.0)
                    # A quick flicker
                    if int(progress * 100) % 2 == 0:
                        return flicker
                    else:
                        return flicker * 0.3
                else:
                    return 0.0  # Complete shutdown

            else:
                # A series of rapid flickers and a complete shutdown
                rapid_flicker = int(progress * 50) % 10
                if rapid_flicker < 6:
                    return random.uniform(0.2, 0.8)
                elif rapid_flicker < 8:
                    return 0.0  # Shutdown
                else:
                    return 0.1  # A barely noticeable glow

        elif shape == "broken_bulb_enhanced":
            # Improved version of broken_bulb with smoother transitions
            import random
            import time

            # Use a sine for smooth transitions between states.
            time_factor = time.time() * 0.5  # Slow change over time

            # Smooth switching between modes
            mode_blend = (math.sin(time_factor) + 1) * 0.5  # 0.0-1.0

            if mode_blend < 0.3:
                # Mode 1: Normal gorenje with a slight flicker
                base = 0.85 + math.sin(progress * 25 * math.pi) * 0.1
                # Random micro-dip
                if random.random() < 0.1:
                    micro_dip = math.sin(progress * 100 * math.pi) * 0.3
                    base = max(0.7, base + micro_dip)
                return base

            elif mode_blend < 0.7:
                # Mode 2: Active flicker
                flicker_speed = 40 + math.sin(time_factor * 2) * 20
                flicker = math.sin(progress * flicker_speed * math.pi) * 0.4 + 0.5

                # Periodic deep dips
                deep_dip_freq = progress * 5  # 5 deep dips per cycle
                if (deep_dip_freq % 1.0) < 0.1:  # 10% of the time in deep failure
                    dip_depth = 1.0 - ((deep_dip_freq % 1.0) * 10)  # 1.0 -> 0.0
                    return flicker * dip_depth * 0.3

                return flicker

            else:
                # Mode 3: Light bulb Agony (rapid flashes)
                rapid = int(progress * 60) % 15  # 4 вспышки в секунду

                if rapid < 3:
                    # A short bright flash
                    flash_progress = rapid / 3.0
                    brightness = 1.0 - abs(flash_progress - 0.5) * 2  # Пирамида
                    return brightness * 0.9 + 0.1
                elif rapid < 5:
                    # Medium flash
                    return random.uniform(0.3, 0.6)
                elif rapid < 7:
                    # low flash
                    return random.uniform(0.1, 0.3)
                else:
                    # Dark
                    return 0.0

        elif shape == "old_tv":
            # The effect of an old TV/walkie-talkie
            import random

            # Static Noises
            static = random.uniform(-0.2, 0.2)

            # Periodic "signal fades"
            signal_fade = math.sin(progress * 3 * math.pi)  # Slow Noises

            # Fast Noise
            fast_noise = math.sin(progress * 50 * math.pi) * 0.1

            # Sudden complete shutdowns
            if random.random() < 0.05:  # 5% chance
                # Shutdown for a short time
                if (progress * 100) % 1 < 0.1:
                    return 0.0

            # Basic signal level
            base = 0.7 + signal_fade * 0.2

            result = base + static + fast_noise
            return max(0.0, min(1.0, result))

        elif shape == "breath_with_gaps":
            # Breathing with periodic delays/skips
            import random

            # Main Breath
            breath = (math.sin(progress * 2 * math.pi - math.pi / 2) + 1) / 2

            # Sometimes we "forget" to inhale
            skip_chance = 0.15  # 15% chance of missing a cycle
            cycle_num = int(progress * 2)  # Every 0.5 progress is a new cycle

            random.seed(cycle_num)  # For predictability
            if random.random() < skip_chance:
                # Skip this cycle and stay on the exhale.
                return 0.0
            else:
                # Normal breathing
                return breath

        elif shape == "random":
            # Random pulse (for the flicker effect)
            import random
            return random.uniform(0.3, 1.0)

        else:
            return (math.sin(progress * 2 * math.pi - math.pi / 2) + 1) / 2  # Sinus as default

    def get_random_flicker_shape(self):
        """Returns a random flicker shape"""
        flicker_shapes = [
            "flicker_zero",
            "broken_bulb",
            "broken_bulb_enhanced"
            "sync_flicker",
            "dip_flicker",
            "old_tv"
        ]
        import random
        return random.choice(flicker_shapes)

    def _apply_pulse_color(self, pulse_id, pulse_value):
        """Applies color based on ripple"""
        pulse_data = self.pulse_animations[pulse_id]

        # Interpolate the brightness
        brightness_range = pulse_data['max_brightness'] - pulse_data['min_brightness']
        current_brightness = pulse_data['min_brightness'] + pulse_value * brightness_range

        # Apply color
        self.win.b_red = pulse_data['base_r'] * current_brightness
        self.win.b_green = pulse_data['base_g'] * current_brightness
        self.win.b_blue = pulse_data['base_b'] * current_brightness

    def _auto_stop_pulse(self, pulse_id):
        """Automatic timer pulse stop"""
        if pulse_id in self.pulse_animations:
            pulse_data = self.pulse_animations[pulse_id]
            self.stop_pulse(
                pulse_id,
                fade_out=pulse_data['stop_fade_out'],
                fade_duration=pulse_data['stop_fade_duration']
            )

    def stop_pulse(self, pulse_id=None, fade_out=True, fade_duration=500):
        """Stopping the pulsation with the ability to turn off the auto-stop timer"""
        if pulse_id is None:
            # Stop all pulse
            for pid in list(self.pulse_timers.keys()):
                self._stop_single_pulse(pid, fade_out, fade_duration)
        elif pulse_id in self.pulse_timers:
            self._stop_single_pulse(pulse_id, fade_out, fade_duration)

    def _stop_single_pulse(self, pulse_id, fade_out, fade_duration):
        """Stop single pulse"""
        # Stop the auto-stop timer if there is one
        if pulse_id in self.pulse_animations:
            pulse_data = self.pulse_animations[pulse_id]
            if pulse_data.get('stop_timer'):
                pulse_data['stop_timer'].stop()

        if fade_out and fade_duration > 0:
            # Smooth fade
            current_r = self.win.b_red
            current_g = self.win.b_green
            current_b = self.win.b_blue

            # Create fade animation
            fade_anim = QVariantAnimation()
            fade_anim.setDuration(fade_duration)
            fade_anim.setStartValue(1.0)
            fade_anim.setEndValue(0.0)

            def update_fade(value):
                self.win.b_red = current_r * value
                self.win.b_green = current_g * value
                self.win.b_blue = current_b * value

            fade_anim.valueChanged.connect(update_fade)

            def cleanup():
                fade_anim.stop()
                self._cleanup_pulse(pulse_id)

            fade_anim.finished.connect(cleanup)
            fade_anim.start()
        else:
            # Force stop
            self._cleanup_pulse(pulse_id)

    def _cleanup_pulse(self, pulse_id):
        """Clean pulse resource"""
        if pulse_id in self.pulse_timers:
            self.pulse_timers[pulse_id].stop()
            del self.pulse_timers[pulse_id]

        if pulse_id in self.pulse_animations:
            # Stop the auto-stop timer
            pulse_data = self.pulse_animations[pulse_id]
            if pulse_data.get('stop_timer'):
                pulse_data['stop_timer'].stop()
            del self.pulse_animations[pulse_id]

    def modify_pulse(self, pulse_id, **kwargs):
        """Modify the parameters of an existing pulse"""
        if pulse_id in self.pulse_animations:
            pulse_data = self.pulse_animations[pulse_id]

            # Updating only the transmitted parameters
            for key, value in kwargs.items():
                if key in pulse_data:
                    pulse_data[key] = value

            # Resetting the time for a smooth transition
            if 'pulse_duration' in kwargs or 'pulse_shape' in kwargs:
                pulse_data['start_time'] = time.time()

    def get_pulse_info(self, pulse_id):
        """Get pulse info"""
        if pulse_id in self.pulse_animations:
            return self.pulse_animations[pulse_id].copy()
        return None

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