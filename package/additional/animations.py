from package import resources
import random
import time
import math
import json
import os
import live2d.v3 as live2d

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
            resources.RESOURCES_DIRECTORY, "anim_cfg/anim_profiles.json"), 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Converting lists to sets for hit_zones
            for char in data.values():
                char['hit_zones'] = {k: set(v) for k, v in char['hit_zones'].items()}
            return data

    def autoBlink(self, last_update_time):
        """Main AutoBlink Function"""
        if not self.blink_enabled:  # If Blink disabled
            # Force open eyes (in case of interrupted blinking)
            # self.model.SetParameterValueById("ParamEyeLOpen", 1.0)
            # self.model.SetParameterValueById("ParamEyeROpen", 1.0)
            self.isBlinking = False
            return
        current_time = time.time()
        self.last_update_time = last_update_time
        delta_time = current_time - self.last_update_time

        # Generating a new blink only if the eyes are fully open
        if not self.isBlinking and self.blinkProgress == 0.0:
            if current_time - self.lastBlinkTime > self.nextBlinkInterval / 1000.0:
                # Two randomization modes:
                if random.random() < 0.7:  # 70% chance - regular Blink mode
                    self.isBlinking = True
                    self.nextBlinkInterval = random.randint(2000, 5000)  # 2-5 sec
                else:  # 30% chance - long pause mode (The character is "lost in thought")
                    self.nextBlinkInterval = random.randint(6000, 10000)  # 6-10 sec
                self.lastBlinkTime = current_time

        # Blink animation
        if self.isBlinking:
            self.blinkProgress += delta_time * 4.0
            if self.blinkProgress >= 1.0:
                self.isBlinking = False
                self.blinkProgress = 0.0
            else:
                if self.blinkProgress < 0.4:
                    eye_open = 1.0 - math.sin(self.blinkProgress * math.pi * 1.25)
                else:
                    eye_open = math.sin((self.blinkProgress - 0.4) * math.pi * 0.833)

                # Adding micro-randomness for the right/left eye
                self.model.SetParameterValueById("ParamEyeLOpen", eye_open * random.uniform(0.98, 1.0))
                self.model.SetParameterValueById("ParamEyeROpen", eye_open * random.uniform(0.98, 1.0))

    def setBlinkEnabled(self, enabled: bool):
        """Blink Switch"""
        self.blink_enabled = enabled

        if enabled:
            if self._log_callbacks:
                # print("Blink On")
                pass
        else:
            if self._log_callbacks:
                # print("Blink Off")
                pass
            # Reset Blink Params
            self.isBlinking = False
            self.blinkProgress = 0.0
            # self.model.SetParameterValueById("ParamEyeLOpen", 1.0)
            # self.model.SetParameterValueById("ParamEyeROpen", 1.0)

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
        self.setBlinkEnabled(True)  # Using our previously created method

    def _handle_motion_finish(self, group, no):
        """Callback with Animation Finish"""
        self.model.ResetExpressions()
        self.model.ResetAllParameters()
        if group != "Idle":  # If the NON-idle animation has ended
            self._reset_idle_state()
        if self._log_callbacks:
            print(f"Animation {group} {no} finish - blink on")
        self.setBlinkEnabled(True)
        # Additionally: reset the eyes to the open state
        self.model.SetParameterValueById("ParamEyeLOpen", 1.0)
        self.model.SetParameterValueById("ParamEyeROpen", 1.0)
        self.model.SetParameterValueById("ParamMouthOpenY", 0)

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