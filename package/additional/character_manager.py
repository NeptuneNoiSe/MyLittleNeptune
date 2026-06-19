import sys
from datetime import datetime, date, timedelta
from time import sleep

from PySide6.QtCore import QTimer, QThread, QPropertyAnimation, QEasingCurve, QVariantAnimation
import random

class CharacterManager:
    def __init__(self, win):
        self.win = win
        self.text_key = None
        self.audio_key = None
        self.kaomoji = None
        self.transform_text_show = False
        self.transform_exp_show = False
        self.play_drag_audio = False
        self.state = CharacterStateManager(self)
        self.tired_controller = CharacterTiredController(self)
        self.tired_state = CharacterTiredStateManager(self)
        self.expressions = CharacterExpressionManager(self)
        self.character_text = CharacterTextManager(self)
        self.movements = CharacterMovementsManager(self)
        self.audio = CharacterAudioManager(self)

    @property
    def model(self):
        """Always returns the current model"""
        return self.win.model

    @property
    def name(self):
        """Always returns the current name"""
        return self.win.character_name

    @property
    def text(self):
        """Always returns the current text"""
        return self.win.lang

    @property
    def tracking_mouse_switch(self):
        return self.win.tracking_mouse_switch

    @property
    def tracking_mouse(self):
        return self.win.tracking_mouse

    @tracking_mouse.setter
    def tracking_mouse(self, value: bool) -> None:
        self.win.tracking_mouse = value

    @property
    def current_event(self):
        if hasattr(self.win, 'event_manager') and self.win.event_manager:
            return self.win.event_manager.current_event
        return None  # или "default"

    @property
    def show_event_greeting(self):
        if hasattr(self.win, 'event_manager') and self.win.event_manager:
            return self.win.event_manager.show_event_greeting
        return None  # или "default"

    @property
    def delay_congratulation_after_greeting(self):
        if hasattr(self.win, 'event_manager') and self.win.event_manager:
            return self.win.event_manager.delay_congratulation_after_greeting
        return None  # или "default"


    @property
    def special_stage(self):
        if hasattr(self.win, 'event_manager') and self.win.event_manager:
            return self.win.event_manager.special_stage
        return None  # или "default"

    @property
    def app_config(self):
        return self.win.app_config

class CharacterStateManager:
    def __init__(self, character):
        self.character = character
        self.current_state = None

        # GoodBye timer
        self.goodByeTimer = QTimer()
        self.goodByeTimer.setSingleShot(True)
        self.goodByeTimer.timeout.connect(self.set_new_character)

    @property
    def win(self):
        """Actual window link"""
        return self.character.win

    def set_new_character(self):
        """Set new character"""
        self.goodByeTimer.stop()
        self.character.win.talk_widget.close_dialog()
        self.win.animation_manager.opacity_animator.animate_opacity(
            source=self.win.image_manager.background_image,
            start=0.9,
            end=0,
            duration=500,
            easing="out_quad"),

        self.win.animation_manager.opacity_animator.animate_opacity(
            source=self.win.canvas,
            start=1.0,
            end=0.0,
            duration=500,
            easing="out_quad",
            on_finished= self._after_animation_fade_out_callback)

    def already_changed_character(self):
        """Change current character"""
        self.character.movements.set_motion(group_name="Special", id=3)
        self.character.expressions.set_smile_expression(fade_out=7000)
        self.character.character_text.set_already_changed_text()
        self.character.audio.set_current_character_audio()

    def _after_animation_fade_out_callback(self):
        """Runs after the animation is completed"""
        if hasattr(self.win, 'models_manager'):
            self.win.models_manager.update_model(self.win)
        self.set_greeting_state()
        self.win.talk_widget.talk_update = True

    def set_greeting_state(self, is_first_run: bool = False) -> None:
        """Starts the animation of the character's appearance with a callback only for repeated launches.
        Args:
            is_first_run: If True, the callback is not called (for the first character display).
            example: on_finished=None if is_first_run else self._after_animation_fade_in_callback
        """
        self.current_state = "Greeting"
        if self.character.current_event and self.character.show_event_greeting:
            current_event_group = self.character.current_event.replace(" ", "") + "Event"
            if self.character.special_stage:
                key = self.character.special_stage.replace(" ", "")
                print(key)
            else:
                key = "Greeting"
            self.character.character_text.set_event_greeting_text(group_name=current_event_group, text_key=key)
        else:
            self.character.character_text.set_greeting_text()

        if self.character.delay_congratulation_after_greeting:
            delay_ms = self.character.delay_congratulation_after_greeting
            # event_name = self.character.current_event if self.win.birthday_active else None
            self.set_event_congratulation_state(delay_ms= delay_ms,
                                                duration = 10000,
                                                event_name= self.character.current_event,
                                                event_key= self.character.special_stage)

        self.win.image_manager.background_image.background_opacity = 0

        self.win.animation_manager.opacity_animator.animate_opacity(
            source=self.win.image_manager.background_image,
            start=0,
            end=0.9,
            duration=500,
            easing="in_quad")

        self.win.animation_manager.opacity_animator.animate_opacity(
            source=self.win.canvas,
            start=0.0,
            end=1.0,
            duration=1500,
            easing="in_quad",
            on_finished=self._after_animation_fade_in_callback)

    def _after_animation_fade_in_callback(self):
        """Runs after the animation is completed"""
        if self.character.current_event:
            if self.character.special_stage and self.character.show_event_greeting:
                key = self.character.special_stage.replace(" ", "_")
            else:
                key = "Greeting"
            format_key = self.character.current_event.replace(" ", "_") + "_" + key
            # print(format_key)
            #self.character.audio.set_event_background_audio()
            self.character.audio.set_event_greeting_audio(audio_key = format_key)
        else:
            self.character.audio.set_greeting_audio()
        self.character.expressions.set_smile_expression(fade_out=7000)
        self.character.movements.set_motion(group_name="Special", id=19)
        self.win.input_handler.input_lock = False
        self.win.character_lock = False

    def set_goodbye_state(self):
        """Character say goodbye"""
        self.current_state = "Goodbye"
        self.win.input_handler.input_lock = True
        self.win.character_lock = True
        self.goodByeTimer.start(3000)
        self.character.audio.set_goodbye_audio()
        self.character.movements.set_motion(group_name="Special", id=1)
        self.character.character_text.set_goodbye_text()

        # WakeUp if character sleep
        if hasattr(self, 'tired_state') and self.character.tired_state.condition == "Sleep":
            self.character.tired_controller.wake_up_function()

        self.character.win.talk_widget.talk_update = False
        self.cancel_congratulation_timer()

    def set_drag_state(self):
        """Set drag state"""
        #self.current_state = "Draging"
        self.character.audio.set_drag_audio()
        self.character.expressions.set_drag_expression()
        self.character.character_text.set_drag_text()

    def set_stay_state(self):
        """Set stay state"""
        self.character.model.ResetExpressions()
        self.character.audio.set_stay_audio()
        self.character.movements.set_motion(group_name="Special", id=13)
        self.character.expressions.set_smile_expression(fade_out=7000)
        self.character.character_text.set_stay_text()

    def set_lost_state(self):
        """Set lost state"""
        self.character.audio.set_lost_audio()
        self.character.movements.set_motion(group_name="Special", id=14)
        self.character.expressions.set_lost_expression(fade_out=7000)
        self.character.character_text.set_lost_text()

    def set_random_state(self):
        """Set random state"""
        self.character.expressions.set_random_expression(fade_out=7000)
        self.character.character_text.set_aux_text(group_name='Talk',
                                                  text_key=self.character.text_key,
                                                  kaomoji=self.character.kaomoji)

    def set_transform_state(self):
        """Transform state"""
        self.win.model_move = False
        self.cancel_congratulation_timer()
        if not self.win.can_transform or self.win.settings_lock:
            if self.character.tired_state.condition != "Sleep":
                self.set_transform_failure_state()
            return

        if self.character.tired_state.condition == "Sleep":
            return

        self.win.animation_manager.transform_animation_start()
        self.character.tired_controller.timer_count = 1
        #self.win.settings_close()
        self.win.models_window.close()
        self.win.animation_status = True

        self.character.expressions.fadeoutTimer.stop()
        self.character.audio.set_transform_audio()
        transform_mode = self.win.resource_manager.get_transform_mode(self.character.name)
        if not self.win.hdd_form:
            self.character.expressions.set_transform_to_hdd_expression(transform_mode=transform_mode)
            self.character.character_text.set_transform_to_hdd_text(transform_mode=transform_mode)
        else:
            self.character.expressions.set_funny_expression(fade_out=14000)
            self.character.character_text.set_transform_to_normal_text(transform_mode=transform_mode)

    def set_transform_failure_state(self):
        """Processing an unsuccessful transformation"""
        self.character.expressions.fadeoutTimer.stop()
        self.character.audio.set_transform_failure_audio()
        self.character.movements.set_motion(group_name="Special", id=7)
        self.win.animation_manager.play_random_flicker_shape(stop_after_ms=3000)
        # self.win.animation_manager.play_color_pulse(r=255, g=0, b=0, pulse_shape="broken_bulb",stop_after_ms=7000)
        self.character.expressions.set_sad_expression(fade_out=10000)
        self.character.character_text.set_transform_failure_text()

    def set_transformed_state(self):
        """Transformed State"""
        if self.character.transform_exp_show:
            self.character.audio.set_transformed_audio()
            self.character.expressions.set_funny_expression(fade_out=7000)

        transform_mode = self.win.resource_manager.get_transform_mode(self.character.name)

        if self.character.transform_text_show:
            if self.win.hdd_form:
                self.character.character_text.set_transformed_hdd_text(transform_mode=transform_mode)
            else:
                self.character.character_text.set_transformed_normal_text(transform_mode=transform_mode)
            self.character.transform_text_show = False
            self.character.transform_exp_show = False
            self.win.animation_status = False

    def set_settings_state(self, text_key: str | None = None,) -> None:
        """Update Settings state"""
        self.cancel_congratulation_timer()
        #self.character.win.talk_widget.talk_update = True
        self.character.audio.set_settings_audio()
        self.character.movements.set_motion(group_name="Special", id=6)
        self.character.character_text.set_settings_text(text_key)

    def set_character_lock_state(self):
        self.character.expressions.set_sad_expression()
        self.character.character_text.set_character_lock_text()
        self.character.movements.set_no_motion()
        self.character.audio.set_no_audio()

    def set_quit_state(self, quit: str):
        """Quiting state"""
        self.cancel_congratulation_timer()
        if quit == 'Yes':
            self.character.audio.set_quit_audio()
            self.character.expressions.set_cry_expression()
            self.character.character_text.set_quit_text()
            self.win.talk_widget.is_quitting = True
            self.character.movements.set_motion(group_name="Special", id=1)
            QTimer.singleShot(3000, lambda: (
                self.win.talk_widget.close_dialog(),
                self.win.animation_manager.opacity_animator.animate_opacity(
                    source=self.win.image_manager.background_image,
                    start=0.9,
                    end=0,
                    duration=500,
                    easing="out_quad"),

                self.win.animation_manager.opacity_animator.animate_opacity(
                    source=self.win.canvas,
                    start=1.0,
                    end=0.0,
                    duration=500,
                    easing="out_quad",
                    on_finished=lambda: sys.exit(0))))

        elif quit == 'No':
            self.character.audio.set_happy_audio()
            self.character.movements.set_motion(group_name="Special", id=19)
            self.character.expressions.set_happy_expression(fade_out=5000)
            self.character.character_text.set_aux_text(group_name='Talk',text_key='Happy',kaomoji=":(^~^):")

    def set_crying_state(self):
        """Set crying state"""
        self.cancel_congratulation_timer()
        self.character.movements.set_motion(group_name="Special", id=7)
        self.character.expressions.set_cry_expression()

    def set_event_congratulation_state(self, delay_ms=0, duration=10000, event_name: str | None = None,
                                       event_key: str | None = None) -> None:
        """Character say congratulation"""
        if (self.win.settings_lock
                or self.win.quit_box_active
                or self.current_state == "Goodbye"
                or self.goodByeTimer.isActive()):
            return

        self.timer_congratulate = QTimer()
        self.timer_congratulate.setSingleShot(True)

        def start_congratulation():
            if (self.win.input_handler.input_lock
                    or self.win.settings_lock
                    or self.win.quit_box_active
                    or self.current_state == "Goodbye"
                    or self.goodByeTimer.isActive()):
                if hasattr(self, 'timer_congratulate'):
                    self.timer_congratulate.stop()
                    self.timer_congratulate.deleteLater()
                    del self.timer_congratulate
                return

            self.win.input_handler.input_lock = True
            self.win.animation_status = True
            #self.win.input_handler.set_transparent_input(delay=duration)

            audio_key = event_name.replace(" ", "_") + "_" + event_key
            self.character.audio.set_event_congratulation_audio(audio_key=audio_key)

            self.character.expressions.set_happy_expression(fade_out=duration)
            self.character.expressions.set_star_expression(fade_out=duration)

            self.character.movements.set_motion(group_name="Special", id=3)

            self.win.event_manager.congratulate_event(duration=duration)

            text_group = event_name.replace(" ", "") + "Event"
            if text_group == "ValentinesDayEvent":
                self.character.character_text.set_event_congratulation_text(
                    group_name=text_group,
                    text_key=event_key,
                    kaomoji="❤~(//◠‿◠//)"
                )
            else:
                self.character.character_text.set_event_congratulation_text(
                    group_name=text_group,
                    text_key=event_key
                )

            QTimer.singleShot(duration, end_congratulation)

        def end_congratulation():
            self.win.input_handler.input_lock = False
            self.win.animation_status = False
            if hasattr(self, 'timer_congratulate'):
                self.timer_congratulate.stop()
                self.timer_congratulate.deleteLater()
                del self.timer_congratulate

        self.timer_congratulate.timeout.connect(start_congratulation)
        self.timer_congratulate.start(delay_ms)

    def cancel_congratulation_timer(self):
        """Force cancel congratulation timer"""
        if hasattr(self, 'timer_congratulate'):
            self.timer_congratulate.stop()
            self.timer_congratulate.deleteLater()
            del self.timer_congratulate


    def set_sing_song_state(self):
        """Character sings a song"""
        self.cancel_congratulation_timer()
        self.win.audio_manager.play_song()
        self.character.movements.set_motion(group_name="Special", id=3)
        self.character.expressions.set_smile_expression(fade_out=self.win.song_duration)
        self.character.character_text.set_sing_song_text()

    def set_event_hint_state(self, hint_type):
        event_name = self.character.current_event.replace(" ", "") + "Event"
        if not self.character.tired_state.condition == "sleep":
            self.character.character_text.set_event_hint_text(event_name, hint_type)

# TODO: Fix Sleep and WakeUp with Schedule
class CharacterTiredController:
    def __init__(self, character):
        self.character = character
        self.sleep = False
        self.wake_up = False
        self.timer_count = 1
        self.sad_v = 600
        self.tired_v = 800
        self.sleep_v = 1000
        self.wake_up_v = 1600
        self.wake_up = False
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_state)
        self.start_timer()
        self.schedule_state = "NORMAL"  # NORMAL, SCHEDULE_SLEEPING, SCHEDULE_IDLE
        self.last_schedule_check = datetime.now()
        self.schedule_timer = QTimer()
        self.schedule_timer.timeout.connect(self._check_schedule_state)
        self.schedule_timer.start(10000)
        self._check_schedule_state()
        self.sleep_again_timer = QTimer()
        self._schedule_wake_up_done = False

    @property
    def sleep_move(self):
        return self.character.win.input_handler.sleep_move

    @sleep_move.setter
    def sleep_move(self, value: bool) -> None:
        self.character.win.input_handler.sleep_move = value

    @property
    def time_scale(self):
        return self.character.win.time_scale

    @property
    def timer_log(self):
        return self.character.win.timer_log

    @property
    def idle_switch(self):
        return self.character.win.idle_switch

    @property
    def sleep_switch(self):
        return self.character.win.sleep_switch

    @property
    def idle_anim(self):
        return self.character.win.idle_anim

    @idle_anim.setter
    def idle_anim(self, value: bool) -> None:
        self.character.win.idle_anim = value

    @property
    def on_mouse_anim(self):
        return self.character.win.on_mouse_anim

    @idle_anim.setter
    def on_mouse_anim(self, value: bool) -> None:
        self.character.win.on_mouse_anim = value

    @property
    def time_schedule(self):
        return self.character.app_config.time_schedule

    @property
    def sleep_h(self):
        return self.character.app_config.sleep_h

    @property
    def sleep_m(self):
        return self.character.app_config.sleep_m

    @property
    def wake_h(self):
        return self.character.app_config.wake_h

    @property
    def wake_m(self):
        return self.character.app_config.wake_m

    def _timer_logging(self):
        if not self.time_schedule:
            timer_mode = "NORMAL"
        else:
            timer_mode = self.schedule_state
        state = self.character.tired_state.condition
        print(f"[TIRED TIMER]"
              f" | Active: {self.timer.isActive()}"
              f" | Mode: {timer_mode}"
              f" | Count: {self.timer_count}"
              f" | Condition: {state}"
              f" | Thread: {QThread.currentThread()}")

    def _check_schedule_state(self):
        """Check schedule State"""
        if not self.time_schedule:
            self.schedule_state = "NORMAL"
            return

        now = datetime.now()
        current_minutes = now.hour * 60 + now.minute
        sleep_minutes = self.sleep_h * 60 + self.sleep_m
        wake_minutes = self.wake_h * 60 + self.wake_m

        if sleep_minutes <= wake_minutes:
            if sleep_minutes <= current_minutes < wake_minutes:
                self.schedule_state = "SCHEDULE_SLEEPING"
            else:
                self.schedule_state = "SCHEDULE_IDLE"
                self._schedule_wake_up_done = False
        else:
            if current_minutes >= sleep_minutes or current_minutes < wake_minutes:
                self.schedule_state = "SCHEDULE_SLEEPING"
            else:
                self.schedule_state = "SCHEDULE_IDLE"
                self._schedule_wake_up_done = False

        self.last_schedule_check = now

    def should_enable_idle_anim(self) -> bool:
        """Checks whether idle animation can be enabled."""
        return self.timer_count < self.sleep_v

    def should_enable_mouse_anim(self) -> bool:
        """Checks whether animation can be enabled on mouse hover."""
        return self.timer_count < self.sleep_v

    def _should_wake_up_by_schedule(self, now=None):
        """Checks if the scheduled wake-up time has arrived"""
        if self._schedule_wake_up_done:
            return False

        if now is None:
            now = datetime.now()

        current_minutes = now.hour * 60 + now.minute
        wake_minutes = self.wake_h * 60 + self.wake_m

        return current_minutes >= wake_minutes

    def _wake_up_by_schedule(self):
        """Forced wake up by schedule"""
        if self._schedule_wake_up_done:
            return

        if self.timer_log:
            print(f"[SCHEDULE_WAKEUP] Time to wake up! ({self.wake_h:02d}:{self.wake_m:02d})")

        self._schedule_wake_up_done = True
        self.character.tired_state.set_wake_up_state()

        if hasattr(self, '_sleep_function_called'):
            self._sleep_function_called = False

    def wake_up_function(self, short_wake_up=False):
        """Run if character wake_up"""
        self.character.model.ResetAllParameters()
        self.character.model.ResetExpressions()

        if not short_wake_up:
            self.reset_timer_with_reload()
            self.timer_count = 0
            self.character.tired_state.condition = None
            self.character.tired_state.set_idle_state()

        self.character.win.animation_manager.set_sleep_state(False)
        self.idle_anim = True
        self.wake_up = True
        self.sleep = False
        self.sleep_move = False
        self.character.win.mouse_tracker.set_sleep_state(False)
        self.character.tracking_mouse = True

    def sleep_function(self):
        """Run if character sleep"""
        self.character.win.animation_manager.set_sleep_state(True)
        self.idle_anim = False
        self.wake_up = False
        self.sleep = True
        self.character.audio.set_sleep_audio()
        self.character.expressions.set_sleep_expression()
        self.character.model.SetAndSaveParameterValueById("ParamAngleY", -30.0, 1.0)
        self.character.model.SetAndSaveParameterValueById("ParamAngleZ", -10.0, 1.0)

    def _update_state(self):
        """Update character state"""
        if not self.sleep_switch:
            return

        self.timer_count += 1
        now = datetime.now()
        # Logging
        if self.timer_log:
            self._timer_logging()
        if self.time_schedule:
            if self.schedule_state == "SCHEDULE_IDLE":
                self._handle_schedule_idle_mode()
                return
            elif self.schedule_state == "SCHEDULE_SLEEPING":
                self._handle_schedule_sleeping_mode()
                return

        self._handle_normal_mode()

    def _handle_schedule_idle_mode(self):
        self.timer_count = min(self.timer_count, self.sad_v - 1)
        self.character.tired_state.set_idle_state()

        if self.idle_switch:
            self.idle_anim = True

        if self.timer_log and self.timer_count % 300 == 0:
            print(f"[SCHEDULE_IDLE] Outside sleep range - forced idle")

    def _handle_schedule_sleeping_mode(self):
        """Sleep schedule handler"""
        now = datetime.now()

        if not self._schedule_wake_up_done and self._should_wake_up_by_schedule(now):
            self._wake_up_by_schedule()
            return

        if self._schedule_wake_up_done:
            self._handle_schedule_idle_mode()
        else:
            self._modified_normal_logic()

    def _handle_normal_mode(self):
        """Normal mode withou schedule"""
        # Processing states
        if self.timer_count <= self.sad_v:
            self.character.tired_state.set_idle_state()

        if self.timer_count <= self.sleep_v and self.idle_switch:
            self.idle_anim = True

        if self.timer_count >= 10 and not self.sleep_switch:
            self.timer_count = 1

        # Checking specific states
        if self.timer_count == self.sad_v:
            self.character.tired_state.set_sad_state()

        elif self.timer_count == self.tired_v and self.sleep_switch:
            self.character.tired_state.set_tired_state()

        elif self.timer_count == self.sleep_v and self.sleep_switch:
            self.character.tired_state.set_sleep_state()

        elif self.timer_count == self.wake_up_v and self.sleep_switch:
            self.character.tired_state.set_wake_up_state()

    def _modified_normal_logic(self):
        """Modified normal logic with State machine"""
        target_state = self._get_target_sleep_state()

        if target_state == "Sleep" and self.character.tired_state.condition == "Sleep":
            self.timer_count = self.sleep_v
            return

        if self.character.tired_state.condition == target_state:
            return

        if target_state == "Idle":
            self.character.tired_state.set_idle_state()
        elif target_state == "Sad":
            self.character.tired_state.set_sad_state()
        elif target_state == "Tired":
            self.character.tired_state.set_tired_state()
        elif target_state == "Sleep":
            self.character.tired_state.set_sleep_state()

    def _get_target_sleep_state(self):
        """Get target sleep state"""
        if self.timer_count < self.sad_v:
            return "Idle"
        elif self.sad_v <= self.timer_count < self.tired_v:
            return "Sad"
        elif self.tired_v <= self.timer_count < self.sleep_v:
            return "Tired"
        else:  # self.timer_count >= self.sleep_v
            return "Sleep"

    # Timer Control
    def reset_timer(self):
        """Timer reset"""
        self.timer.stop()
        self.timer_count = 1
        if self.timer_log:
            print("Timer reset")

    def reset_timer_with_reload(self, delay_ms=10000, reason=""):
        self.timer.stop()
        #self.sleep_again_timer.stop()
        if self.timer_log and reason:
            print(f"[TIMER_RESET] {reason}")

        QTimer.singleShot(delay_ms, self.start_timer)

    def reload_timer(self):
        """Timer reload"""
        self.start_timer()

    def start_timer(self):
        """Start timer"""
        self.reset_timer()
        self.timer.start(int(1000 / self.time_scale))

class CharacterTiredStateManager:
    def __init__(self, character):
        self.character = character
        self.condition = "idle"
        #self._setup_timers()

    def set_idle_state(self):
        self.condition = "Idle"

    def set_sad_state(self):
        self.condition = "Sad"
        self.character.audio.set_sad_audio()
        self.character.movements.set_motion(group_name="Special", id=8)
        self.character.expressions.set_sad_expression()
        self.character.character_text.set_sad_text()

    def set_tired_state(self):
        self.condition = "Tired"
        self.character.audio.set_tired_audio()
        self.character.movements.set_yawn_motion()
        self.character.expressions.set_tired_expression()
        self.character.character_text.set_tired_text()

    def set_sleep_state(self, sleep_again = False):
        self.condition = "Sleep"
        self.character.audio.set_pre_sleep_audio()
        self.character.movements.set_sleep_motion()
        if self.character.tracking_mouse_switch:
            self.character.tracking_mouse = False
            self.character.win.input_handler.handle_mouse_idle()
            self.character.win.mouse_tracker.set_sleep_state(True)
        if not sleep_again:
            self.character.character_text.set_sleep_text()
        else:
            self.character.character_text.set_sleep_again_text()

    def set_wake_up_state(self):
        self.character.tired_controller.wake_up_function()
        self.character.tired_controller.sleep_again_timer.stop()
        self.character.audio.set_wake_up_audio()
        self.character.movements.set_motion(group_name="Special", id=19)
        self.character.expressions.set_wake_up_expression(fade_out=10000)
        self.character.character_text.set_wake_up_text()

    def set_woke_up_state(self):
        """Set woke up state"""
        short_woke_up = False
        if self.character.tired_controller.time_schedule:
            short_woke_up = True
        self.character.tired_controller.sleep = False
        self.character.model.ResetAllParameters()
        self.character.model.ResetExpressions()
        self.character.tired_controller.wake_up_function(short_wake_up=short_woke_up)
        self.character.audio.set_woke_audio()
        self.character.movements.set_motion(group_name="Special", id=14)
        s_interval = 10000
        self.character.expressions.set_surprised_expression(fade_out=s_interval)
        self.character.character_text.set_woke_up_text()
        if short_woke_up:
            self.character.tired_controller.sleep_again_timer.singleShot(s_interval, lambda: self.set_sleep_state(sleep_again=True))

class CharacterExpressionManager:
    def __init__(self, character):
        self.character = character

        # Fadeout timer
        self.fadeoutTimer = QTimer()
        self.fadeoutTimer.setSingleShot(True)
        self.fadeoutTimer.timeout.connect(self.reset_expression)

    @property
    def exp_fade_out_var(self):
        return self.character.win.talk_widget.exp_fade_out_var

    @exp_fade_out_var.setter
    def exp_fade_out_var(self, value):
        self.character.win.talk_widget.exp_fade_out_var = value

    def set_happy_expression(self, fade_out: int | None = None) -> None:
        self._apply_expression("Happy", fade_out)

    def set_star_expression(self, fade_out: int | None = None) -> None:
        self._apply_expression("Star", fade_out)

    def set_sad_expression(self, fade_out: int | None = None) -> None:
        self._apply_expression("Sad", fade_out)

    def set_smile_expression(self, fade_out: int | None = None) -> None:
        self._apply_expression("Smile", fade_out)

    def set_cry_expression(self, fade_out: int | None = None) -> None:
        self._apply_expression("Cry", fade_out)

    def set_surprised_expression(self, fade_out: int | None = None) -> None:
        self._apply_expression("Surprised", fade_out)

    def set_funny_expression(self, fade_out: int | None = None) -> None:
        self._apply_expression("Funny", fade_out)

    def set_tired_expression(self, fade_out: int | None = None) -> None:
        self._apply_expression("Tired", fade_out)

    def set_sleep_expression(self, fade_out: int | None = None) -> None:
        self._apply_expression("ClosedEyes", fade_out)

    def set_wake_up_expression(self, fade_out: int | None = None) -> None:
        self._apply_expression("Star", fade_out)
        self._apply_expression("Serious", fade_out)

    def set_drag_expression(self, fade_out: int | None = None) -> None:
        if self.character.name in ["Purple Sister", "Black Sister"]:
            self._apply_expression("Smile", fade_out)
        else:
            self._apply_expression("Funny", fade_out)

        # Additional dragging actions
        if hasattr(self.character, 'on_drag_start'):
            self.character.on_drag_start()

    def set_lost_expression(self, fade_out: int | None = None) -> None:
        if self.character.name == "Black Sister":
            self._apply_expression("Fear", fade_out)
        else:
            self._apply_expression("Surprised", fade_out)

    def set_transform_to_hdd_expression(self, fade_out: int | None = None, transform_mode = "Normal") -> None:
        # Setting the default expression for a regular form
        if transform_mode == "Normal":
            if self.character.name in ["Neptune", "NepGear", "Maho"]:
                self._apply_expression("Star", fade_out)
            elif self.character.name in ["Vert"]:
                self._apply_expression("Smile", fade_out)
            else:
                self._apply_expression("Serious", fade_out)
        elif transform_mode == "Evil":
            self._apply_expression("Angry", fade_out)

    def set_transform_end_expression(self, fade_out: int | None = None) -> None:
        self.character.model.ResetAllParameters()
        self.character.model.ResetExpressions()
        self._apply_expression("Funny", fade_out)

    def add_random_expression(self,drop_last=False):
        if drop_last:
            self.character.model.RemoveExpression(self.character.win.lastExpressionId)

        expressions = self.character.model.GetExpressions()
        expId = random.choice(expressions)
        self.character.model.AddExpression(expId)

        self.character.win.lastExpressionId = expId
        self.character.win.activeExpressions.append(expId)
        return expId

    def set_random_expression(self, fade_out: int | None = None) -> None:
        """Set random character expression"""
        self.character.model.ResetExpressions()
        self.add_random_expression()

        # Setting the expression and text
        expression_config = {
            "Normal": ("Normal", "(o_o)"),
            "Happy": ("Happy", "(^_^)"),
            "Angry": ("Angry", "(⇀‸↼‶)"),
            "Sad": ("Sad", "(´•ω•̥`)"),
            "Smile": ("Smile", "(^~^)"),
            "Serious": ("Serious", "(一‸一)"),
            "Horny": ("Horny", "(￣‿¡￣)"),
            "Tired": ("Tired", "(๑•﹏•)"),
            "ClosedEyes": ("ClosedEyes", "(-_-)"),
            "Cry": ("Cry", "(o;TωT)o"),
            "Fear": ("Fear", "(｡ŏ_ŏ)"),
            "Incredulous":("Incredulous", "(￢_￢)?"),
            "Star": ("Star", "(✩ω✩)"),
            "Surprised": ("Surprised", "(0_0)?"),
            "Funny": ("Funny", "(>_<)"),
            # Maho Spesial Expressions
            "Normal_Alt": ("Normal_Maho", "(•ิ_•ิ)?"),
            "Happy_Alt": ("Happy_Maho", "(￣▽￣*)"),
            "Angry_Alt": ("Angry_Maho", "(ﾒ｀ﾛ´)/"),
            "Sad_Alt": ("Sad_Maho", "(；一_一)"),
            "Smile_Alt": ("Smile_Maho", "（¬‿¬）"),
            "Tired_Alt": ("Tired_Maho", "(´〜｀*)"),
            "ClosedEyes_Alt": ("ClosedEyes_Maho", "(￣ー￣)"),
            "Cry_Alt": ("Cry_Maho", "(╯︵╰,)"),
            "Fear_Alt": ("Fear_Maho", "(￣へ￣｡)"),
            "Incredulous_Alt": ("Incredulous_Maho", "(눈_눈)"),
            "Star_Alt": ("Star_Maho", "(☆^▽^☆)"),
            "Surprised_Alt": ("Surprised_Maho", "(°ロ°)?"),
            "Funny_Alt": ("Funny_Maho", "(ﾉ>△<)ﾉ"),
        }

        # Special case handling
        if self.character.win.lastExpressionId == "Fear":
            if self.character.name == "White Heart":
                text_key, kaomoji = "FearWH", "(0﹏\‶)"
            else:
                text_key, kaomoji = "Fear", "(｡ŏ_ŏ)"
        elif self.character.win.lastExpressionId == "Funny":
            if self.character.win.hdd_form:
                text_key, kaomoji = "FunnyHDD", "(◕‿◕)"
            else:
                if self.character.name == "Blanc":
                    text_key, kaomoji = "FunnyBl", "(‶/﹏0)"
                else:
                    text_key, kaomoji = "Funny", "(>_<)"
        else:
            text_key, kaomoji = expression_config.get(
                self.character.win.lastExpressionId,
                ("Normal", "(o_o)")
            )

        self._apply_expression(text_key, fade_out)
        self.character.audio.set_aux_audio(text_key)
        self.character.text_key = text_key
        self.character.kaomoji = kaomoji

    def _apply_expression(self, exp_id: str, fade_out: int | None) -> None:
        # print(exp_id)
        self.character.model.SetExpression(exp_id)
        if hasattr(self, 'fadeoutTimer') and fade_out is not None:
            self.fadeoutTimer.start(fade_out)
            self.exp_fade_out_var = fade_out

    def reset_expression(self):
        # win.model.ResetAllParameters()
        # print("reset")
        self.character.model.ResetExpressions()
        self.fadeoutTimer.stop()

class CharacterTextManager:
    def __init__(self, character):
        self.character = character

    @property
    def text(self):
        return self.character.win.text

    @text.setter
    def text(self, value):
        if isinstance(value, list):  # Если передали ['Talk', 'Taking']
            result = self.character.win.lang
            for key in value:
                result = result[key]
            self.character.win.text = result
        else:
            self.character.win.text = value

    @property
    def kaomoji(self):
        return self.character.win.kaomoji

    @kaomoji.setter
    def kaomoji(self, value):
        self.character.win.kaomoji = value

    def set_aux_text(self,
                     group_name: str | None = None,
                     text_key: str | None = None,
                     kaomoji: str | None = None) -> None:
        self.text = [group_name, text_key]
        self.kaomoji = kaomoji
        self.update()

    def set_already_changed_text(self):
        self.text = ['Talk', 'Already']
        self.kaomoji = "(^~^)"
        self.update()

    def set_character_lock_text(self):
        self.text = ['Talk', 'Cant_now']
        self.kaomoji = "(´•ω•̥`)"
        self.update()

    def set_settings_text(self, text_key):
        self.text = ['MiscellaneousTalk', text_key]
        self.kaomoji = "(⌐■_■)"
        self.update()

    def set_greeting_text(self):
        self.text = ['Talk', 'Hello']
        self.kaomoji = "(^~^)/"
        self.update()

    def set_event_greeting_text(self, group_name, text_key = "Greeting", kaomoji = "*(^.^)*"):
        self.text = [group_name, text_key]
        self.kaomoji = kaomoji
        self.update()

    def set_event_congratulation_text(self, group_name, text_key = "Greeting", kaomoji = "★~(◠‿◕✿)"):
        self.text = [group_name, text_key]
        self.kaomoji = kaomoji
        self.update()

    def set_goodbye_text(self):
        self.text = ['Talk', 'Goodbye']
        self.kaomoji = "(-_-)>"
        self.update()

    def set_drag_text(self):
        self.text = ['Talk', 'Taking']
        self.kaomoji = "ε=┌( >_<)┘"
        self.update()

    def set_stay_text(self):
        self.text = ['Talk', 'Stay']
        self.kaomoji = "(^~^)"
        self.update()

    def set_lost_text(self):
        self.text = ['Talk', 'Lost']
        self.kaomoji = "(D*D)?"
        self.update()

    def set_sad_text(self):
        self.text = ['Talk', 'Sad']
        self.kaomoji = "(´•ω•̥`)"
        self.update()

    def set_tired_text(self):
        self.text = ['Talk', 'Tired']
        self.kaomoji = "(๑•﹏•)"
        self.update()

    def set_sleep_text(self):
        self.text = ['Talk', 'Sleep']
        self.kaomoji = "(ᴗ˳ᴗ)ｚｚＺ"
        self.update()

    def set_sleep_again_text(self):
        self.text = ['Talk', 'SleepAgain']
        self.kaomoji = "(ᴗ˳ᴗ)ｚｚＺ"
        self.update()

    def set_woke_up_text(self):
        self.text = ['Talk', 'Woke']
        self.kaomoji = "(⊙_⊙)✿"
        self.update()

    def set_wake_up_text(self):
        self.text = ['Talk', 'WakeUp']
        self.kaomoji = "(O_~)/"
        self.update()

    def set_transform_to_hdd_text(self, transform_mode="Normal"):
        if transform_mode == "Normal":
            self.text = ['Talk', 'TransformToHDD']
            self.kaomoji = "(/￣ー￣)/~~☆"
        elif transform_mode == "Evil":
            self.text = ['Talk', 'TransformToHDD_Evil']
            self.kaomoji = "(►__◄)/~~☆"
        self.update()

    def set_transform_to_normal_text(self, transform_mode="Normal"):
        if transform_mode == "Normal":
            self.text = ['Talk', 'TransformToNormal']
            self.kaomoji = "(/￣ー￣)/"
        elif transform_mode == "Evil":
            self.text = ['Talk', 'TransformToNormal']
            self.kaomoji = "(/►__◄)/"
        self.update()

    def set_transformed_hdd_text(self, transform_mode="Normal"):
        if transform_mode == "Normal":
            self.text = ['Talk', 'TransformedHDD']
            self.kaomoji = "╰(☆ ͡° ͜ʖ ͡° ☆)つ"
        elif transform_mode == "Evil":
            self.text = ['Talk', 'TransformedHDD_Evil']
            self.kaomoji = "╰(* ►__◄ *)つ"
        self.update()

    def set_transformed_normal_text(self, transform_mode="Normal"):
        if transform_mode == "Normal":
            self.text = ['Talk', 'TransformedNormal']
            self.kaomoji = "(> ͜ʖ <)"
        elif transform_mode == "Evil":
            self.text = ['Talk', 'TransformedNormal']
            self.kaomoji = "(> ͜ʖ <)"
        self.update()

    def set_transform_failure_text(self):
        self.text = ['Talk', 'TransformNot']
        self.kaomoji = "(ﾉ>ω<)ﾉ :｡･"
        self.update()

    def set_quit_text(self):
        self.text = ['Talk', 'QuitAlt']
        self.kaomoji = "(^3^)"
        self.update()

    def set_sing_song_text(self):
        self.text = "♫♫♫"
        self.kaomoji = "ヽ(⌒▽⌒)ﾉ ♪"
        self.update()

    def set_event_hint_text(self, event_name, hint_type):
        self.text = [event_name, hint_type]
        self.kaomoji = "(⌐■_■)"
        self.update()

    def update(self):
        self.character.win.talk_widget.show_talk()

class CharacterMovementsManager:
    def __init__(self, character):
        self.character = character

    @property
    def model(self):
        """Always returns the current model"""
        return self.character.win.model

    def set_motion(self,
                   group_name: str | None = None,
                   id: int | None = None) -> None:

        self.character.win.animation_manager.play_animation(
            anim_type='Motion',
            group_or_id=group_name,
            no=id,
            priority="FORCE",
        )

    def set_sleep_motion(self):
        sleep_motion_id = random.choice([9, 10, 11, 12])
        self.set_motion(group_name="Special", id=sleep_motion_id)

    def set_yawn_motion(self):
        yawn_motion_id = random.choice([17, 18])
        self.set_motion(group_name="Special", id=yawn_motion_id)

    def set_no_motion(self):
        no_motion_id = random.randint(0, 7)
        self.set_motion(group_name="No", id=no_motion_id)

    def process_body_hit(self):
        """Processing interactions with body parts"""
        #self.model.ResetExpressions()
        #self.expressions.set_stay_expression()
        #self.character_text.set_stay_text()
        hit_parts = {
            part for part in self.character.model.HitPart(self.character.win.posX, self.character.win.posY, True) or []
            if part  # Filtering None values
        }
        self.character.win.animation_manager.handle_hit(hit_parts)

        #if not self.tired_anim.sleep and not self.character.win.input_lock:
        #    self._update_character_expression()

class CharacterAudioManager:
    def __init__(self, character):
        self.character = character

    @property
    def audio_manager(self):
        return self.character.win.audio_manager

    def set_aux_audio(self, audio_key: str | None = None) -> None:
        audio_key_lower = audio_key.lower() if audio_key else None
        self.audio_manager.play_audio(self.character.name, audio_key_lower, enable_lipsync=True, category="voice",
                              stop_audio=True)

    def set_event_greeting_audio(self, audio_key= "greeting"):
        audio_key_lower = audio_key.lower()
        # Пробуем воспроизвести аудио
        success = self.audio_manager.play_audio(
            self.character.name,
            audio_key_lower,
            enable_lipsync=True,
            category="voice",
            stop_audio=True
        )

        if not success:
            self.set_greeting_audio()

    def set_event_congratulation_audio(self, audio_key= "happy"):
        audio_key_lower = audio_key.lower()
        # Пробуем воспроизвести аудио
        success = self.audio_manager.play_audio(
            self.character.name,
            audio_key_lower,
            enable_lipsync=True,
            category="voice",
            stop_audio=True
        )

        if not success:
            self.set_happy_audio()

    def set_sing_song_audio(self):
        self.audio_manager.play_song()

    def set_greeting_audio(self):
        self.audio_manager.play_audio(self.character.name, "greeting", enable_lipsync=True, category="voice",
                              stop_audio=True)

    def set_goodbye_audio(self):
        self.audio_manager.play_audio(self.character.name, "goodbye", enable_lipsync=True, category="voice",
                              stop_audio=True)

    def set_current_character_audio(self):
        self.audio_manager.play_audio(self.character.name, "me", enable_lipsync=True, category="voice",
                              stop_audio=True)

    def set_no_audio(self):
        self.audio_manager.play_audio(self.character.name, "no", enable_lipsync=True, category="voice",
                              stop_audio=True)

    def set_yes_audio(self):
        self.audio_manager.play_audio(self.character.name, "yes", enable_lipsync=True, category="voice",
                              stop_audio=True)

    def set_drag_audio(self):
        if self.character.play_drag_audio:
            self.audio_manager.play_audio(self.character.name, "drag", enable_lipsync=True, category="voice",
                              stop_audio=True)
            self.character.play_drag_audio = False

    def set_stay_audio(self):
        self.audio_manager.play_audio(self.character.name, "stay", enable_lipsync=True, category="voice",
                              stop_audio=True)

    def set_lost_audio(self):
        self.audio_manager.play_audio(self.character.name, "lost", enable_lipsync=True, category="voice",
                              stop_audio=True)

    def set_woke_audio(self):
        self.audio_manager.play_audio(self.character.name, "woke", enable_lipsync=True, category="voice",
                              stop_audio=True)

    def set_wake_up_audio(self):
        self.audio_manager.play_audio(self.character.name, "wake_up", enable_lipsync=True, category="voice",
                              stop_audio=True)

    def set_transform_audio(self):
        self.audio_manager.play_audio(self.character.name, "transform", enable_lipsync=True, category="voice",
                              stop_audio=True)
        self.audio_manager.play_audio("Effects", "transform_start", enable_lipsync=False, category="sfx",
                              stop_audio=False)

    def set_transformed_audio(self):
        self.audio_manager.play_audio(self.character.name, "transformed", enable_lipsync=True, category="voice",
                              stop_audio=True)
        self.audio_manager.stop_audio("Effects", "transform_start")

        self.audio_manager.play_audio("Effects", "transform_finish", enable_lipsync=False, category="sfx",
                              stop_audio=False)

    def set_transform_failure_audio(self):
        self.audio_manager.play_audio(self.character.name, "transform_fail", enable_lipsync=True, category="voice",
                              stop_audio=True)

    def set_settings_audio(self):
        self.audio_manager.play_audio(self.character.name, "settings", enable_lipsync=True, category="voice",
                              stop_audio=True)

    def set_happy_audio(self):
        self.audio_manager.play_audio(self.character.name, "happy", enable_lipsync=True, category="voice",
                              stop_audio=True)

    def set_sad_audio(self):
        self.audio_manager.play_audio(self.character.name, "sad", enable_lipsync=True, category="voice",
                              stop_audio=True)

    def set_tired_audio(self):
        self.audio_manager.play_audio(self.character.name, "tired", enable_lipsync=True, category="voice",
                              stop_audio=True)

    def set_pre_sleep_audio(self):
        self.audio_manager.play_audio(self.character.name, "pre_sleep", enable_lipsync=True, category="voice",
                              stop_audio=True)

    def set_sleep_audio(self):
        self.audio_manager.play_audio(self.character.name, "sleep", enable_lipsync=True, category="voice",
                              stop_audio=True)

    def set_really_quit_audio(self):
        self.audio_manager.play_audio(self.character.name, "really_quit", enable_lipsync=True, category="voice",
                              stop_audio=True)

    def set_quit_audio(self):
        self.audio_manager.play_audio(self.character.name, "quit", enable_lipsync=True, category="voice",
                              stop_audio=True)