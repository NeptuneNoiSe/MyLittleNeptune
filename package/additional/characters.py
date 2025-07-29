from PySide6.QtCore import QTimer
import random

class CharacterManager:
    def __init__(self, win):
        self.win = win
        self._win = win
        self.text_key = None
        self.kaomoji = None
        self.transform_text_show = False
        self.transform_exp_show = False
        #self.character = win.character_name
        #self.model = win.model
        self.state = CharacterStateManager(self)
        self.expressions = CharacterExpressionManager(self)
        self.character_text = CharacterTextManager(self)
        self.movements = CharacterMovementsManager(self)
        #self.reactions = CharacterReactionHandler(self)
        #self.animation = CharacterAnimationController(win.model)

        # GoodBye timer
        self.goodByeTimer = QTimer()
        self.goodByeTimer.timeout.connect(self.set_new_character)

    @property
    def model(self):
        """Always returns the current model"""
        return self._win.model

    @property
    def name(self):
        """Always returns the current name"""
        return self._win.character_name

    @property
    def text(self):
        """Always returns the current text"""
        return self._win.lang

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
        self.character_text.set_greeting_text()
        self.expressions.set_smile_expression(fade_out=7000)

    def set_goodbye_state(self):
        """Character say goodbye"""
        self.goodByeTimer.start(3000)
        self.character_text.set_goodbye_text()

        # WakeUp if character sleep
        if hasattr(self.win, 'tired_anim') and self.win.tired_anim.condition == "Sleep":
            self.win.tired_anim.wake_up_func()

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

    def set_wake_up_state(self):
        """Set wake up state"""
        self.win.tired_anim.sleep = False
        self.model.ResetAllParameters()
        self.model.ResetExpressions()
        self.win.tired_anim.wake_up_func()
        self.expressions.set_surprised_expression(fade_out=10000)
        self.character_text.set_wake_up_text()

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
        self.expressions.fadeoutTimer.stop()
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
            self.character_text.set_aux_text(group_name='Talk',text_key='Star',kaomoji=":(^~^):")


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

    def set_wake_up_text(self):
        self.text = ['Talk', 'Woke']
        self.kaomoji = "(⊙_⊙)✿"
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
        self.fadeoutTimer.timeout.connect(self.reset_expression)

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

    def set_drag_expression(self, fade_out: int | None = None) -> None:
        if self.character.name in ["Purple Sister", "Black Sister"]:
            self._apply_expression("Smile", fade_out)
        else:
            self._apply_expression("Funny", fade_out)

        # Additional dragging actions
        if hasattr(self.character, 'on_drag_start'):
            self.character.on_drag_start()

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
        self.character.model.SetExpression(exp_id)
        if hasattr(self, 'fadeoutTimer') and fade_out is not None:
            self.fadeoutTimer.start(fade_out)

    def reset_expression(self):
        # win.model.ResetAllParameters()
        self.character.model.ResetExpressions()
        self.fadeoutTimer.stop()

