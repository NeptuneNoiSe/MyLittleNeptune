import random
import time
import math
import live2d.v3 as live2d

class AnimationsManager:
    def __init__(self, model):
        self._model = model
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
        self._setup_animation_groups()


    @property
    def model(self):
        if self._model is None:
            raise RuntimeError("Model not initialize")
        return self._model

    def set_logging(self, enabled: bool):
        """on/off logs callback's"""
        self._log_callbacks = enabled

    def autoBlink(self, last_update_time):
        """Main AutoBlink Function"""
        if not self.blink_enabled:  # If Blink disabled
            # Force open eyes (in case of interrupted blinking)
            #self.model.SetParameterValueById("ParamEyeLOpen", 1.0)
            #self.model.SetParameterValueById("ParamEyeROpen", 1.0)
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

        # Blink animation (unchanged)
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

    def play_animation(self, model, anim_type: str, group_or_id, no=None, priority=None,
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
                str(group_or_id),  # Группа анимаций (str)
                priority,
                onStart=callbacks['start'],
                onFinish=callbacks['finish']
            )
        elif anim_type == 'Motion':
            model.StartMotion(
                str(group_or_id),  # Группа (str)
                int(no),  # Номер анимации (int)
                int(priority),  # Приоритет (int)
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

    def _setup_animation_groups(self):
        """Initialization of animation groups and click zones"""
        self.ANIMATION_PROFILES = {
            'HAIR': {
                'hit_zones': {'FrontHair'},
                'anim_type': 'Motion',
                'group': 'Extra',
                'options': 1,
                'priority': live2d.MotionPriority.FORCE
            },
            'HEAD': {
                'hit_zones': {'Part61'},
                'anim_type': 'Motion',
                'group': 'Extra',
                'options': [6, 7],
                'priority': live2d.MotionPriority.FORCE
            },
            'HANDS': {
                'hit_zones': {'ude_Normal'},
                'anim_type': 'Motion',
                'group': 'Extra',
                'options': [8, 9, 10, 11, 12, 13],
                'priority': live2d.MotionPriority.FORCE
            },
            'LEFT LEG': {
                'hit_zones': {'Part63'},
                'anim_type': 'Motion',
                'group': 'Extra',
                'options': 14,
                'priority': live2d.MotionPriority.FORCE
            },
            'RIGHT LEG': {
                'hit_zones': {'Part64'},
                'anim_type': 'Motion',
                'group': 'Extra',
                'options': 15,
                'priority': live2d.MotionPriority.FORCE
            },
        }

        # Default animation for unknown parts
        self.DEFAULT_PROFILE = {
            'anim_type': 'RandomMotion',
            'group': 'TapBody',
            'priority': live2d.MotionPriority.FORCE
        }

    def handle_hit(self, hit_parts) -> bool:
        """Processing hits by parts of the model"""
        hit_parts_set = set(hit_parts) if not isinstance(hit_parts, set) else hit_parts

        # First we check the known zones
        for profile in self.ANIMATION_PROFILES.values():
            if hit_parts_set & profile['hit_zones']:
                self._play_profile_animation(profile)
                return True

        # If the zone is not found, we start the default animation.
        if hit_parts_set:  # If there is at least some part
            self._play_profile_animation(self.DEFAULT_PROFILE)
            return True

        return False

    def _play_profile_animation(self, profile: dict):
        """Playing animations based on a profile"""
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