from PySide6.QtCore import QTimer, QThread
import random

class CharacterManager:
    def __init__(self, win):
        self.win = win
        self.text_key = None
        self.kaomoji = None
        self.transform_text_show = False
        self.transform_exp_show = False
        self.state = CharacterStateManager(self)
        self.tired_controller = CharacterTiredController(self)
        self.tired_state = CharacterTiredStateManager(self)
        self.expressions = CharacterExpressionManager(self)
        self.character_text = CharacterTextManager(self)
        self.movements = CharacterMovementsManager(self)
        #self.reactions = CharacterReactionHandler(self)
        #self.animation = CharacterAnimationController(win.model)

        # GoodBye timer
        self.goodByeTimer = QTimer()
        self.goodByeTimer.setSingleShot(True)
        self.goodByeTimer.timeout.connect(self.set_new_character)

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

    def set_new_character(self):
        """Set new character"""
        self.goodByeTimer.stop()
        self.win.talk_widget.close_dialog()

        if hasattr(self.win, 'models_manager'):
            self.win.models_manager.update_model(self.win)
        self.set_greeting_state()
        self.win.talk_widget.talk_update = True

    def set_greeting_state(self):
        """Character say hello"""
        self.expressions.set_smile_expression(fade_out=7000)
        self.character_text.set_greeting_text()

    def set_goodbye_state(self):
        """Character say goodbye"""
        self.goodByeTimer.start(3000)
        self.character_text.set_goodbye_text()

        # WakeUp if character sleep
        if hasattr(self, 'tired_state') and self.tired_state.condition == "Sleep":
            self.tired_controller.wake_up_function()

        self.win.talk_widget.talk_update = False

    def set_drag_state(self):
        """Set drag state"""
        #if self.state.is_sleeping:
        #    return
        self.expressions.set_drag_expression()
        self.character_text.set_drag_text()

    def set_stay_state(self):
        """Set stay state"""
        self.model.ResetExpressions()
        self.expressions.set_smile_expression(fade_out=7000)
        self.character_text.set_stay_text()

    def set_lost_state(self):
        """Set lost state"""
        self.expressions.set_lost_expression(fade_out=7000)
        self.character_text.set_lost_text()

    def set_woke_state(self):
        """Set wake up state"""
        self.tired_controller.sleep = False
        self.model.ResetAllParameters()
        self.model.ResetExpressions()
        self.tired_controller.wake_up_function()
        self.expressions.set_surprised_expression(fade_out=10000)
        self.character_text.set_woke_text()

    def set_crying_state(self):
        """Set crying state"""
        self.expressions.set_cry_expression()


    def set_part_hit(self):
        """Processing body parts"""
        #self.model.ResetExpressions()
        #self.expressions.set_stay_expression()
        #self.character_text.set_stay_text()
        self.movements.process_body_hit()

    def set_random_state(self):
       self.expressions.set_random_expression(fade_out=7000)
       self.character_text.set_aux_text(group_name='Talk', text_key=self.text_key, kaomoji=self.kaomoji)

    def set_transform_state(self):
        self.expressions.fadeoutTimer.stop()
        if not self.win.hdd_form:
            self.expressions.set_tranform_to_hdd_expression()
            self.character_text.set_transform_to_hdd_text()
        else:
            self.expressions.set_funny_expression(fade_out=14000)
            self.character_text.set_transform_to_normal_text()

    def set_transform_failure_state(self):
        """Processing an unsuccessful transformation"""
        self.expressions.fadeoutTimer.stop()
        self.expressions.set_sad_expression(fade_out=10000)
        self.character_text.set_transform_failure_text()

    def set_transformed_state(self):
        if self.transform_exp_show:
            self.expressions.set_funny_expression(fade_out=7000)

        if self.transform_text_show:
            if self.win.hdd_form:
                self.character_text.set_transformed_hdd_text()
            else:
                self.character_text.set_transformed_normal_text()
            self.transform_text_show = False
            self.transform_exp_show = False

    def set_settings_state(self, text_key: str | None = None,) -> None:
        self.character_text.set_settings_text(text_key)

    def set_quit_state(self, quit: str):
        if quit == 'Yes':
            self.expressions.set_cry_expression()
            self.character_text.set_quit_text()
        elif quit == 'No':
            self.expressions.set_happy_expression(fade_out=5000)
            self.character_text.set_aux_text(group_name='Talk',text_key='Happy',kaomoji=":(^~^):")

# TODO: [WIP] Класс в активной разработке. Требуется:
#       1. Полное тестирование после переноса всех функций
#       2. Проверка состояний сон/бодроствование персонажа
#       3. Анализ взаимодействия со всеми связанными классами и основным окном
#       WARNING: Возможны нестабильности и критические баги!
class CharacterTiredController:
    def __init__(self, character):
        self.character = character
        self.sleep = False
        self.wake_up = False
        self.timer_count = 1
        self.sad_v = 60
        self.tired_v = 80
        self.sleep_v = 100
        self.wake_up_v = 160
        self.wake_up = False
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_state)
        self._start_timer()

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

    def reset_timer(self):
        self.timer.stop()
        self.timer_count = 1
        if self.timer_log:
            print("Timer reset")

    def _start_timer(self):
        self.reset_timer()  # Сброс перед запуском
        self.timer.start(int(6000 / self.time_scale))

    def _update_state(self):
        self.timer_count += 1
        state = self.character.tired_state.condition

        # Logging
        if self.timer_log:
            print(f"[TIRED TIMER]"
                  f" | Active: {self.timer.isActive()}"
                  f" | Count: {self.timer_count}"
                  f" | Condition: {state}"
                  f" | Thread: {QThread.currentThread()}")

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

    def reload_timer(self):
        self._start_timer()

    def sleep_function(self):
        self.character.win.anim_manager.set_sleep_state(True)
        self.idle_anim = False
        self.wake_up = False
        self.sleep = True
        self.character.expressions.set_sleep_expression()
        self.character.model.SetAndSaveParameterValueById("ParamAngleY", -30.0, 1.0)
        self.character.model.SetAndSaveParameterValueById("ParamAngleZ", -10.0, 1.0)

    def wake_up_function(self):
        self.character.model.ResetAllParameters()
        self.character.model.ResetExpressions()
        self.timer_count = 0
        self.character.tired_state.condition = None
        self.character.tired_state.set_idle_state()
        self.character.win.anim_manager.set_sleep_state(False)
        self.idle_anim = True
        self.wake_up = True
        self.sleep = False
        self.sleep_move = False
        self.character.win.mouse_tracker.set_sleep_state(False)
        self.character.tracking_mouse = True

class CharacterTiredStateManager:
    def __init__(self, character):
        self.character = character
        self.condition = "idle"
        #self._setup_timers()

    def set_idle_state(self):
        self.condition = "Idle"

    def set_sad_state(self):
        self.condition = "Sad"
        self.character.expressions.set_sad_expression()
        self.character.character_text.set_sad_text()

    def set_tired_state(self):
        self.condition = "Tired"
        self.character.expressions.set_tired_expression()
        self.character.character_text.set_tired_text()

    def set_sleep_state(self):
        self.condition = "Sleep"
        if self.character.tracking_mouse_switch:
            self.character.tracking_mouse = False
            self.character.win.input_handler.handle_mouse_idle()
            self.character.win.mouse_tracker.set_sleep_state(True)
        self.character.character_text.set_sleep_text()

    def set_wake_up_state(self):
        self.character.tired_controller.wake_up_function()
        self.character.expressions.set_wake_up_expression(fade_out=10000)
        self.character.character_text.set_wake_up_text()

class CharacterStateManager:
    def __init__(self, character):
        self.character = character
        self.condition = "idle"
        #self._setup_timers()

class CharacterMovementsManager:
    def __init__(self, character):
        self.character = character

    def process_body_hit(self):
        """Processing interactions with body parts"""
        hit_parts = {
            part for part in self.character.model.HitPart(self.character.win.posX, self.character.win.posY, True) or []
            if part  # Filtering None values
        }
        self.character.win.anim_manager.handle_hit(hit_parts)

        #if not self.tired_anim.sleep and not self.character.win.input_lock:
        #    self._update_character_expression()

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

    def set_settings_text(self, text_key):
        self.text = ['MiscellaneousTalk', text_key]
        self.kaomoji = "(⌐■_■)"
        self.update()

    def set_greeting_text(self):
        self.text = ['Talk', 'Hello']
        self.kaomoji = "(^~^)/"
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

    def set_woke_text(self):
        self.text = ['Talk', 'Woke']
        self.kaomoji = "(⊙_⊙)✿"
        self.update()

    def set_wake_up_text(self):
        self.text = ['Talk', 'WakeUp']
        self.kaomoji = "(O_~)/"
        self.update()

    def set_transform_to_hdd_text(self):
        self.text = ['Talk', 'TransformToHDD']
        self.kaomoji = "(/￣ー￣)/~~☆"
        self.update()

    def set_transform_to_normal_text(self):
        self.text = ['Talk', 'TransformToNormal']
        self.kaomoji = "(/￣ー￣)/"
        self.update()

    def set_transformed_hdd_text(self):
        self.text = ['Talk', 'TransformedHDD']
        self.kaomoji = "╰(☆ ͡° ͜ʖ ͡° ☆)つ"
        self.update()

    def set_transformed_normal_text(self):
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

    def update(self):
        self.character.win.talk_widget.show_talk()

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

    def set_tranform_to_hdd_expression(self, fade_out: int | None = None) -> None:
        # Setting the default expression for a regular form
        if self.character.name in ["Neptune", "NepGear"]:
            self._apply_expression("Star", fade_out)
        elif self.character.name in ["Vert"]:
            self._apply_expression("Smile", fade_out)
        else:
            self._apply_expression("Serious", fade_out)

    def set_tranform_end_expression(self, fade_out: int | None = None) -> None:
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
            "Tired": ("Tired", "(๑•﹏•)"),
            "ClosedEyes": ("ClosedEyes", "(-_-)"),
            "Cry": ("Cry", "(o;TωT)o"),
            "Fear": ("Fear", "(｡ŏ_ŏ)"),
            "Star": ("Star", "(✩ω✩)"),
            "Surprised": ("Surprised", "(0_0)?"),
            "Funny": ("Funny", "(>_<)"),
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