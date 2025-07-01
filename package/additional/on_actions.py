from PySide6.QtWidgets import QMessageBox

class OnActions:
    def on_action_normal(win):
        win.showNormal()

    def on_action_minimize(win):
        win.showMinimized()

    def on_action_maximize(win):
        win.showMaximized()

    # Context Menu Actions
    def on_action_transform(win):
        win.model_move = False
        if not win.can_transform:
            if win.condition != "Sleep":
                win.anim_manager.handle_transform_failure(win)
            return

        if win.condition == "Sleep":
            return

        win.anim_manager.play_transform_animation(win)
        win.t_count = 1

        # Setting the transformation text
        text_key = 'TransformToNormal' if win.goodness_form else 'TransformToGodness'
        win.text = win.lang['Talk'][text_key]
        win.kaomoji = "(/￣ー￣)/" if win.goodness_form else "(/￣ー￣)/~~☆"
        win.settings_close()
        win.textUpdate()

    # Characters Actions
    def on_action_neptune(win):
        win.talkUpd = False
        if not win.transform:
            win.model_move = True
            win.goodBye()
        win.character_name = "Neptune"
        if win.transform:
            win.models_manager.update_model(win)

    def on_action_purple_heart(win):
        win.talkUpd = False
        if not win.transform:
            win.model_move = True
            win.goodBye()
        win.character_name = "Purple Heart"
        if win.transform:
            win.models_manager.update_model(win)

    def on_action_noire(win):
        win.talkUpd = False
        if not win.transform:
            win.model_move = True
            win.goodBye()
        win.character_name = "Noire"
        if win.transform:
            win.models_manager.update_model(win)

    def on_action_black_heart(win):
        win.talkUpd = False
        if not win.transform:
            win.model_move = True
            win.goodBye()
        win.character_name = "Black Heart"
        if win.transform:
            win.models_manager.update_model(win)

    def on_action_blanc(win):
        win.talkUpd = False
        if not win.transform:
            win.model_move = True
            win.goodBye()
        win.character_name = "Blanc"
        if win.transform:
            win.models_manager.update_model(win)

    def on_action_white_heart(win):
        win.talkUpd = False
        if not win.transform:
            win.model_move = True
            win.goodBye()
        win.character_name = "White Heart"
        if win.transform:
            win.models_manager.update_model(win)

    def on_action_vert(win):
        win.talkUpd = False
        if not win.transform:
            win.model_move = True
            win.goodBye()
        win.character_name = "Vert"
        if win.transform:
            win.models_manager.update_model(win)

    def on_action_green_heart(win):
        win.talkUpd = False
        if not win.transform:
            win.model_move = True
            win.goodBye()
        win.character_name = "Green Heart"
        if win.transform:
            win.models_manager.update_model(win)

    def on_action_nepgear(win):
        win.talkUpd = False
        if not win.transform:
            win.model_move = True
            win.goodBye()
        win.character_name = "NepGear"
        if win.transform:
            win.models_manager.update_model(win)

    def on_action_purple_sister(win):
        win.talkUpd = False
        if not win.transform:
            win.model_move = True
            win.goodBye()
        win.character_name = "Purple Sister"
        if win.transform:
            win.models_manager.update_model(win)

    def on_action_uni(win):
        win.talkUpd = False
        if not win.transform:
            win.model_move = True
            win.goodBye()
        win.character_name = "Uni"
        if win.transform:
            win.models_manager.update_model(win)

    def on_action_black_sister(win):
        win.talkUpd = False
        if not win.transform:
            win.model_move = True
            win.goodBye()
        win.character_name = "Black Sister"
        if win.transform:
            win.models_manager.update_model(win)

    def on_action_rom(win):
        win.talkUpd = False
        if not win.transform:
            win.model_move = True
            win.goodBye()
        win.character_name = "Rom"
        if win.transform:
            win.models_manager.update_model(win)

    def on_action_white_sister_rom(win):
        win.talkUpd = False
        if not win.transform:
            win.model_move = True
            win.goodBye()
        win.character_name = "White Sister Rom"
        if win.transform:
            win.models_manager.update_model(win)

    def on_action_ram(win):
        win.talkUpd = False
        if not win.transform:
            win.model_move = True
            win.goodBye()
        win.character_name = "Ram"
        if win.transform:
            win.models_manager.update_model(win)

    def on_action_white_sister_ram(win):
        win.talkUpd = False
        if not win.transform:
            win.model_move = True
            win.goodBye()
        win.character_name = "White Sister Ram"
        if win.transform:
            win.models_manager.update_model(win)

    def on_action_histoire(win):
        win.talkUpd = False
        if not win.transform:
            win.model_move = True
            win.goodBye()
        win.character_name = "Histoire"
        if win.transform:
            win.models_manager.update_model(win)

    # Animations Actions
    def on_action_idle_true(win):
        # QMessageBox.information(self, "Message", f"Idle Animation: Enable")
        if win.condition == "Sleep":
            pass
        else:
            win.text = win.lang['MiscellaneousTalk']['IdleEnabled']
            win.kaomoji = "(⌐■_■)"
            print(win.name + ": " + win.text + win.kaomoji)
            win.textUpdate()

        win.config.set('Animations', 'idle_animation', 'True')
        with open('config.ini', 'w') as cfg:
            cfg: [str, int, tuple, object]
            win.config.write(cfg)
        win.idle_switch = True
        win.idle_anim = True

    def on_action_idle_false(win):
        # QMessageBox.information(self, "Message", f"Idle Animation: Disable")
        if win.condition == "Sleep":
            pass
        else:
            win.text = win.lang['MiscellaneousTalk']['IdleDisabled']
            win.kaomoji = "(⌐■_■)"
            print(win.name + ": " + win.text + win.kaomoji)
            win.textUpdate()

        win.config.set('Animations', 'idle_animation', 'False')
        with open('config.ini', 'w') as cfg:
            cfg: [str, int, tuple, object]
            win.config.write(cfg)
        win.idle_switch = False
        win.idle_anim = False

    def on_action_on_mouse_true(win):
        # QMessageBox.information(self, "Message", f"OnMouse Animation: Enable")
        if win.condition == "Sleep":
            pass
        else:
            win.text = win.lang['MiscellaneousTalk']['OnMouseEnabled']
            win.kaomoji = "(⌐■_■)"
            print(win.name + ": " + win.text + win.kaomoji)
            win.textUpdate()

        win.config.set('Animations', 'on_mouse_animation', 'True')
        with open('config.ini', 'w') as cfg:
            cfg: [str, int, tuple, object]
            win.config.write(cfg)
        win.on_mouse_switch = True
        win.on_mouse_anim = True

    def on_action_on_mouse_false(win):
        # QMessageBox.information(self, "Message", f"OnMouse Animation: Disable")
        if win.condition == "Sleep":
            pass
        else:
            win.text = win.lang['MiscellaneousTalk']['OnMouseDisabled']
            win.kaomoji = "(⌐■_■)"
            print(win.name + ": " + win.text + win.kaomoji)
            win.textUpdate()

        win.config.set('Animations', 'on_mouse_animation', 'False')
        with open('config.ini', 'w') as cfg:
            cfg: [str, int, tuple, object]
            win.config.write(cfg)
        win.on_mouse_switch = False
        win.on_mouse_anim = False

    def on_action_tap_body_true(win):
        # QMessageBox.information(self, "Message", f"Tap Body Animation: Enable")
        if win.condition == "Sleep":
            pass
        else:
            win.text = win.lang['MiscellaneousTalk']['TapBodyEnabled']
            win.kaomoji = "(⌐■_■)"
            print(win.name + ": " + win.text + win.kaomoji)
            win.textUpdate()

        win.config.set('Animations', 'tap_body_animation', 'True')
        with open('config.ini', 'w') as cfg:
            cfg: [str, int, tuple, object]
            win.config.write(cfg)
        win.tap_body_switch = True
        win.tap_body_anim = True

    def on_action_tap_body_false(win):
        # QMessageBox.information(self, "Message", f"Tap Body Animation: Disable")
        if win.condition == "Sleep":
            pass
        else:
            win.text = win.lang['MiscellaneousTalk']['TapBodyDisabled']
            win.kaomoji = "(⌐■_■)"
            print(win.name + ": " + win.text + win.kaomoji)
            win.textUpdate()

        win.config.set('Animations', 'tap_body_animation', 'False')
        with open('config.ini', 'w') as cfg:
            cfg: [str, int, tuple, object]
            win.config.write(cfg)
        win.tap_body_switch = False
        win.tap_body_anim = False

    def on_action_stop_all_motions(win):
        if win.condition == "Sleep":
            pass
        else:
            win.text = win.lang['MiscellaneousTalk']['StopMotions']
            win.kaomoji = "(⌐■_■)"
            print(win.name + ": " + win.text + win.kaomoji)
            win.textUpdate()

        win.model.StopAllMotions()

    # Settings Actions
    def on_action_settings(win):
        win.settings_show()

    def on_action_about(win):
        QMessageBox.information(win, win.lang['Actions']['AboutAlt'], win.lang['Actions']['AboutText'])

    def on_action_quit(win):
        win.model.SetExpression("Cry")
        if win.condition == "Sleep":
            win.wake_up_func()
        win.kaomoji = "(o;TωT)o"
        answer = QMessageBox.question(win,
                                      win.lang['Actions']['Quit'],
                                      win.name + ": " + win.lang['Talk']['Quit'] + " " + win.kaomoji,
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                      QMessageBox.StandardButton.No)
        if answer == QMessageBox.StandardButton.Yes:
            win.quitTimer.start(3000)
            win.text = win.lang['Talk']['QuitAlt']
            win.kaomoji = "(^3^)"
            print(win.name + ": " + win.text + win.kaomoji)
            win.textUpdate()

        else:
            win.t_count = 1
            win.model.ResetExpression()
            win.model.SetExpression("Happy")
            win.fadeoutTimer.start(5000)
            win.text = win.lang['Talk']['Star']
            win.kaomoji = ":(^~^):"
            print(win.name + ": " + win.text + win.kaomoji)
            win.textUpdate()