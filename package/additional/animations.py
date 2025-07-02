from PySide6.QtCore import QSize
from PySide6.QtGui import QMovie, Qt

from package import resources
import random
import time
import math
import json
import os
import live2d.v3 as live2d
from package.additional.models import ModelsManager

class AnimationsManager:
    def __init__(self, model):
        self.model = model
        self._log_callbacks = False
        self.blink_enabled = True
        self.last_update_time = 0
        self.blinkProgress = 0.0
        self.nextBlinkInterval = 0.0
        self.lastBlinkTime = 0.0
        self.isBlinking = True
        self._is_idle_playing = False
        self._last_idle_time = 0.0
        self._next_idle_delay = 0.0
        self.profiles = self._load_profiles()
        self._current_character = None
        self._active_model = None
        self._blink_state = {
            'enabled': True,
            'is_active': False,
            'progress': 0.0,
            'last_blink': time.time(),
            'next_delay': self._random_blink_delay(),
            'override_blink': True  # A critical flag
        }
        self.models_manager = ModelsManager
        self.transform_lock = False
        self.transform_text = False
        self.transform = False

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
        """on/off logs callback's"""
        self._log_callbacks = enabled

    def _load_profiles(self) -> dict:
        """Load a single config for all characters"""
        with open(os.path.join(
            resources.RESOURCES_DIRECTORY, "configs/anim_profiles.json"), 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Converting lists to sets for hit_zones
            for char in data.values():
                char['hit_zones'] = {k: set(v) for k, v in char['hit_zones'].items()}
            return data

    # AutoBlink Function
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

            # We apply it with a small spread
            self._set_eye_params(eye_open)

    def _set_eye_params(self, base_value: float):
        """Save apply eyes parameters"""
        if self._blink_state['override_blink']:
            self.model.SetParameterValueById("ParamEyeLOpen",
                                             base_value * random.uniform(0.95, 1.0))
            self.model.SetParameterValueById("ParamEyeROpen",
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

    def set_sleep_state(self, is_sleeping: bool):
        """Sleep state Management"""
        if is_sleeping:
            self._reset_idle_state()
        self._sleep_mode = is_sleeping  # It can be used for special sleep animations.

    def _handle_motion_start(self, group, no):
        """Callback with Animation Start"""
        if self._log_callbacks:
            print(f"Animation {group} {no} start - blink off")
        self.set_blink_enabled(False)  # Using our previously created method

    def _handle_motion_finish(self, group, no):
        """Callback with Animation Finish"""
        if not self.transform:
            self.model.ResetExpressions()
            self.model.ResetAllParameters()
        if group != "Idle":  # If the NON-idle animation has ended
            self._reset_idle_state()
            self.set_blink_enabled(True)
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
        self.model.ResetExpressions()
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
        if not self._current_character:
            return False
        # print(hit_parts)
        profile = self.profiles[self._current_character]
        for zone, parts in profile['hit_zones'].items():
            if hit_parts & parts:
                self._play_profile_animation(profile['animations'][zone])
                return True

        # Default Animation
        self._play_profile_animation(profile['animations']['default'])
        return True

    # Transform Animations
    def check_animation_progress(self, win):
        """Checking animation progress"""
        if hasattr(win, 'transformMovie'):
            if (win.transformMovie.currentFrameNumber() >=
                    win.transformMovie.frameCount() - 3):

                if win.transform:
                    win.transformLabel.movie().setScaledSize(QSize(int(1), int(1)))
                    win.transformMovie.stop()
                    win.transformLabel.close()
                    self.handle_transform_completion(win)
                else:
                    self._finalize_animation(win)

    def _finalize_animation(self, win):
        """Animation completion"""
        win.transformMovie.stop()
        win.transformLabel.close()
        win.transformLabel.clear()
        win.input_lock = False
        # self.transformMovie = None

        if win.transform_text:
            text_key = 'TransformedHDD' if win.hdd_form else 'TransformedNormal'
            win.text = win.lang['Talk'][text_key]
            win.kaomoji = "╰(☆ ͡° ͜ʖ ͡° ☆)つ" if win.hdd_form else "(> ͜ʖ <)"
            win.textUpdate()
            win.transform_text = False

    def handle_transform_failure(self, win):
        """Processing an unsuccessful transformation"""
        if hasattr(win, 'model'):
            win.model.SetExpression("Sad")

        win.fadeoutTimer.start(10000)
        win.text = win.lang['Talk']['TransformNot']
        win.kaomoji = "(ﾉ>ω<)ﾉ :｡･"
        print(f"{win.name}: {win.text}{win.kaomoji}")
        win.textUpdate()

    def play_transform_animation(self, win):
        """Starting the transformation animation"""
        win.input_lock = True

        # Setting up Live2D animations
        self._play_model_animation(win)

        # Init QMovie
        win.transformMovie = QMovie(win.t_anim_in)
        win.transformLabel.setMovie(win.transformMovie)
        win.transformLabel.movie().setScaledSize(
            self._calculate_animation_size(win)
        ), Qt.KeepAspectRatio, Qt.SmoothTransformation
        win.transformMovie.start()
        win.transformLabel.move(int(win.trm_mx * win.models_scale), int(win.trm_my * win.models_scale))
        win.transformLabel.show()
        self.transform = win.transform = True
        self.transform_lock = 0

    def handle_transform_completion(self, win):
        """Ending the transformation animation"""
        if not win.hdd_form and self.transform_lock == 0:
            self._transform_to_hdd(win)
        elif win.hdd_form and self.transform_lock == 0:
            self._transform_to_regular(win)

        # Starting the reverse animation
        win.transformMovie = None
        win.transformMovie = QMovie(win.t_anim_out)
        win.transformLabel.setMovie(win.transformMovie)
        win.transformLabel.movie().setScaledSize(
            self._calculate_animation_size(win)
        ), Qt.KeepAspectRatio, Qt.SmoothTransformation
        win.transformMovie.start()
        win.transformLabel.move(int(win.trm_mx * win.models_scale), int(win.trm_my * win.models_scale))
        win.transformLabel.show()
        self.transform = win.transform = False
        win.talkUpd = True

    def _play_model_animation(self, win):
        """Model animation playback"""
        # Regular form processing (hdd_form=False)
        if not win.hdd_form:
            # Playing the transformation animation
            win.anim_manager.play_animation(
                model=win.model,
                anim_type='Motion',
                group_or_id="Unique",
                no=0,
                priority=live2d.MotionPriority.FORCE,
            )

            # Setting the default expression for a regular form
            default_expression = "Serious"
            expressions = {
                "Neptune": "Star",
                "Vert": "Smile",
                "NepGear": "Star"
            }
            win.model.SetExpression(expressions.get(win.character_name, default_expression))
        # HDD form processing (hdd_form=True)
        else:
            # Special treatment for reverse transformation
            win.model.SetExpression("Funny")

    def _calculate_animation_size(self, win):
        """Calculate animation size"""
        return QSize(
            int(win.w_resize + win.trm_cmx * win.models_scale),
            int(win.h_resize + win.trm_cmy * win.models_scale)
        )

    def _transform_to_hdd(self, win):
        """Transformation to hdd form"""
        transformations = {
            "Neptune": win.on_action_purple_heart,
            "Noire": win.on_action_black_heart,
            "Blanc": win.on_action_white_heart,
            "Vert": win.on_action_green_heart,
            "NepGear": win.on_action_purple_sister,
            "Uni": win.on_action_black_sister,
            "Rom": win.on_action_white_sister_rom,
            "Ram": win.on_action_white_sister_ram,
        }
        if win.character_name in transformations:
            transformations[win.character_name]()
        self._transform_end_exp(win)

    def _transform_to_regular(self, win):
        """Transformation to regular form"""
        transformations = {
            "Purple Heart": win.on_action_neptune,
            "Black Heart": win.on_action_noire,
            "White Heart": win.on_action_blanc,
            "Green Heart": win.on_action_vert,
            "Purple Sister": win.on_action_nepgear,
            "Black Sister": win.on_action_uni,
            "White Sister Rom": win.on_action_rom,
            "White Sister Ram": win.on_action_ram,
        }
        if win.character_name in transformations:
            transformations[win.character_name]()
        self._transform_end_exp(win)

    def _transform_end_exp(self, win):
        self.transform_lock = 1
        win.model.ResetAllParameters()
        win.model.ResetExpressions()
        win.model.SetExpression("Funny")
        win.fadeoutTimer.start(7000)
        win.transform_text = True