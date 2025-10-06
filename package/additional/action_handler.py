from PySide6.QtWidgets import QMessageBox


class ActionHandler:
    """OnActions Handler"""
    def __init__(self, win):
        self.win = win

    #Actions
    def on_action_normal(self):
        self.win.showNormal()

    def on_action_minimize(self):
        self.win.showMinimized()

    def on_action_maximize(self):
        self.win.showMaximized()

    # Context Menu Actions
    def on_action_transform(self):
        self.win.model_move = False
        if not self.win.can_transform:
            if self.win.character.tired_state.condition != "Sleep":
                self.win.character.state.set_transform_failure_state()
            return

        if self.win.character.tired_state.condition == "Sleep":
            return

        self.win.animation_manager.transform_animation_start()
        self.win.character.tired_controller.timer_count = 1
        self.win.settings_close()
        self.win.character.state.set_transform_state()

    # Characters Actions
    def _change_character(self, character_name):
        # Check if the current name matches the selected one
        if hasattr(self.win, 'character_name') and self.win.character_name == character_name:
            self.win.character.state.alredy_changed_character()
            return  # Interrupt the function because the character has already been selected
        self.win.talk_widget.talk_update = False
        if not self.win.transform:
            self.win.model_move = True
            self.win.character.state.set_goodbye_state()
        self.win.character_name = character_name
        if self.win.transform:
            self.win.models_manager.update_model(self.win)

    def on_action_neptune(self):
        self._change_character("Neptune")

    def on_action_purple_heart(self):
        self._change_character("Purple Heart")

    def on_action_noire(self):
        self._change_character("Noire")

    def on_action_black_heart(self):
        self._change_character("Black Heart")

    def on_action_blanc(self):
        self._change_character("Blanc")

    def on_action_white_heart(self):
        self._change_character("White Heart")

    def on_action_vert(self):
        self._change_character("Vert")

    def on_action_green_heart(self):
        self._change_character("Green Heart")

    def on_action_nepgear(self):
        self._change_character("NepGear")

    def on_action_purple_sister(self):
        self._change_character("Purple Sister")

    def on_action_uni(self):
        self._change_character("Uni")

    def on_action_black_sister(self):
        self._change_character("Black Sister")

    def on_action_rom(self):
        self._change_character("Rom")

    def on_action_white_sister_rom(self):
        self._change_character("White Sister Rom")

    def on_action_ram(self):
        self._change_character("Ram")

    def on_action_white_sister_ram(self):
        self._change_character("White Sister Ram")

    def on_action_histoire(self):
        self._change_character("Histoire")

    def on_action_maho(self):
        self._change_character("Maho")

    # Animations Actions
    def _toggle_animation_setting(self, config_key, switch_attr, anim_attr,
                                  enabled_text_key, disabled_text_key, enabled):
        # Обновляем конфиг (новое добавление)
        setattr(self.win.app_config, switch_attr, enabled)

        if self.win.character.tired_state.condition != "Sleep":
            text_key = enabled_text_key if enabled else disabled_text_key
            self.win.character.state.set_settings_state(text_key=text_key)

        setattr(self.win, switch_attr, enabled)
        setattr(self.win, anim_attr, enabled)

    def _create_toggle_handlers(self):
        """Generates handler pairs for different animation types"""
        handlers = {
            'idle': ('idle_animation', 'IdleEnabled', 'IdleDisabled'),
            'on_mouse': ('on_mouse_animation', 'OnMouseEnabled', 'OnMouseDisabled'),
            'tap_body': ('tap_body_animation', 'TapBodyEnabled', 'TapBodyDisabled'),
        }

        for prefix, (config_key, enabled_text, disabled_text) in handlers.items():
            # True handler
            def make_true_handler(prefix=prefix, config_key=config_key,
                                  enabled_text=enabled_text, disabled_text=disabled_text):
                return lambda: self._toggle_animation_setting(
                    config_key, f'{prefix}_switch', f'{prefix}_anim',
                    enabled_text, disabled_text, True
                )

            setattr(self, f'on_action_{prefix}_true', make_true_handler())

            # False handler
            def make_false_handler(prefix=prefix, config_key=config_key,
                                   enabled_text=enabled_text, disabled_text=disabled_text):
                return lambda: self._toggle_animation_setting(
                    config_key, f'{prefix}_switch', f'{prefix}_anim',
                    enabled_text, disabled_text, False
                )

            setattr(self, f'on_action_{prefix}_false', make_false_handler())

    def on_action_idle_true(self):
        self.win.app_config.idle_switch = True
        self._toggle_animation_setting(
            'idle_animation', 'idle_switch', 'idle_anim',
            'IdleEnabled', 'IdleDisabled', True
        )

    def on_action_idle_false(self):
        self.win.app_config.idle_switch = False
        self._toggle_animation_setting(
            'idle_animation', 'idle_switch', 'idle_anim',
            'IdleEnabled', 'IdleDisabled', False
        )

    def on_action_on_mouse_true(self):
        self.win.app_config.on_mouse_switch = True
        self._toggle_animation_setting(
            'on_mouse_animation', 'on_mouse_switch', 'on_mouse_anim',
            'OnMouseEnabled', 'OnMouseDisabled', True
        )

    def on_action_on_mouse_false(self):
        self.win.app_config.on_mouse_switch = True
        self._toggle_animation_setting(
            'on_mouse_animation', 'on_mouse_switch', 'on_mouse_anim',
            'OnMouseEnabled', 'OnMouseDisabled', False
        )

    def on_action_tap_body_true(self):
        self.win.app_config.tap_body_switch = True
        self._toggle_animation_setting(
            'tap_body_animation', 'tap_body_switch', 'tap_body_anim',
            'TapBodyEnabled', 'TapBodyDisabled', True
        )

    def on_action_tap_body_false(self):
        self.win.app_config.tap_body_switch = True
        self._toggle_animation_setting(
            'tap_body_animation', 'tap_body_switch', 'tap_body_anim',
            'TapBodyEnabled', 'TapBodyDisabled', False
        )

    def on_action_stop_all_motions(self):
        if self.win.character.tired_state.condition != "Sleep":
            self.win.character.state.set_settings_state(text_key='StopMotions')
        self.win.model.StopAllMotions()

    # Settings Actions
    def on_action_settings(self):
        self.win.settings_show()

    def on_action_about(self):
        QMessageBox.information(
            self.win,
            self.win.lang['Actions']['AboutAlt'],
            self.win.lang['Actions']['AboutText']
        )

    def on_action_quit(self):
        if self.win.character.tired_state.condition == "Sleep":
            self.win.character.tired_controller.wake_up_function()

        self.win.character.expressions.set_cry_expression()
        self.win.character.audio.set_really_quit_audio()
        self.win.kaomoji = "(o;TωT)o"

        answer = QMessageBox.question(
            self.win,
            self.win.lang['Actions']['Quit'],
            f"{self.win.name}: {self.win.lang['Talk']['Quit']} {self.win.kaomoji}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if answer == QMessageBox.StandardButton.Yes:
            self.win.character.state.set_quit_state(quit='Yes')
        else:
            self.win.character.tired_controller.timer_count = 1
            self.win.character.state.set_quit_state(quit='No')