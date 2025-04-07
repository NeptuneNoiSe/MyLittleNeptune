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
        if win.can_transform:
            if win.condition == "Sleep":
                pass
            else:
                win.transform_initialize()
                win.t_count = 1
                if win.goodness_form:
                    win.text = "I'm going back to my normal form"
                    win.kaomoji = "(/￣ー￣)/"
                else:
                    win.text = "I'm Transform"
                    win.kaomoji = "(/￣ー￣)/~~☆"
                win.settings_close()
                win.textUpdate()
        if not win.can_transform:
            if win.condition == "Sleep":
                pass
            else:
                win.model.SetExpression("Sad", fadeout=10000)
                win.text = "I'm Can't Transform"
                win.kaomoji = "(ﾉ>ω<)ﾉ :｡･"
                print(win.character_name + ": " + win.text + win.kaomoji)
                win.textUpdate()

    # Characters Actions
    def on_action_neptune(win):
        win.goodness_form = False
        win.can_transform = True
        win.talkUpd = False
        if not win.transform:
            win.goodBye()
        win.character_name = "Neptune"
        win.models_switch = 0
        if win.transform:
            win.model_update()

    def on_action_purple_heart(win):
        win.goodness_form = True
        win.can_transform = True
        win.talkUpd = False
        if not win.transform:
            win.goodBye()
        win.character_name = "Purple Heart"
        win.models_switch = 1
        if win.transform:
            win.model_update()

    def on_action_noire(win):
        win.goodness_form = False
        win.can_transform = True
        win.talkUpd = False
        if not win.transform:
            win.goodBye()
        win.character_name = "Noire"
        win.models_switch = 2
        if win.transform:
            win.model_update()

    def on_action_black_heart(win):
        win.goodness_form = True
        win.can_transform = True
        win.talkUpd = False
        if not win.transform:
            win.goodBye()
        win.character_name = "Black Heart"
        win.models_switch = 3
        if win.transform:
            win.model_update()

    def on_action_blanc(win):
        win.goodness_form = False
        win.can_transform = True
        win.talkUpd = False
        if not win.transform:
            win.goodBye()
        win.character_name = "Blanc"
        win.models_switch = 4
        if win.transform:
            win.model_update()

    def on_action_white_heart(win):
        win.goodness_form = True
        win.can_transform = True
        win.talkUpd = False
        if not win.transform:
            win.goodBye()
        win.character_name = "White Heart"
        win.models_switch = 5
        if win.transform:
            win.model_update()

    def on_action_vert(win):
        win.goodness_form = False
        win.can_transform = True
        win.talkUpd = False
        if not win.transform:
            win.goodBye()
        win.character_name = "Vert"
        win.models_switch = 6
        if win.transform:
            win.model_update()

    def on_action_green_heart(win):
        win.goodness_form = True
        win.can_transform = True
        win.talkUpd = False
        if not win.transform:
            win.goodBye()
        win.character_name = "Green Heart"
        win.models_switch = 7
        if win.transform:
            win.model_update()

    def on_action_nepgear(win):
        win.goodness_form = False
        win.can_transform = True
        win.talkUpd = False
        if not win.transform:
            win.goodBye()
        win.character_name = "NepGear"
        win.models_switch = 8
        if win.transform:
            win.model_update()

    def on_action_purple_sister(win):
        win.goodness_form = True
        win.can_transform = True
        win.talkUpd = False
        if not win.transform:
            win.goodBye()
        win.character_name = "Purple Sister"
        win.models_switch = 9
        if win.transform:
            win.model_update()

    def on_action_uni(win):
        win.goodness_form = False
        win.can_transform = True
        win.talkUpd = False
        if not win.transform:
            win.goodBye()
        win.character_name = "Uni"
        win.models_switch = 10
        if win.transform:
            win.model_update()

    def on_action_black_sister(win):
        win.goodness_form = True
        win.can_transform = True
        win.talkUpd = False
        if not win.transform:
            win.goodBye()
        win.character_name = "Black Sister"
        win.models_switch = 11
        if win.transform:
            win.model_update()

    def on_action_rom(win):
        win.goodness_form = False
        win.can_transform = True
        win.talkUpd = False
        if not win.transform:
            win.goodBye()
        win.character_name = "Rom"
        win.models_switch = 12
        if win.transform:
            win.model_update()

    def on_action_white_sister_rom(win):
        win.goodness_form = True
        win.can_transform = True
        win.talkUpd = False
        if not win.transform:
            win.goodBye()
        win.character_name = "White Sister Rom"
        win.models_switch = 13
        if win.transform:
            win.model_update()

    # Animations Actions
    def on_action_idle_true(win):
        # QMessageBox.information(self, "Message", f"Idle Animation: Enable")
        if win.condition == "Sleep":
            pass
        else:
            win.text = "You have enabled the Idle Animation"
            win.kaomoji = "(⌐■_■)"
            print(win.character_name + ": " + win.text + win.kaomoji)
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
            win.text = "You have disabled the Idle Animation"
            win.kaomoji = "(⌐■_■)"
            print(win.character_name + ": " + win.text + win.kaomoji)
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
            win.text = "You have enabled the OnMouse Animation"
            win.kaomoji = "(⌐■_■)"
            print(win.character_name + ": " + win.text + win.kaomoji)
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
            win.text = "You have disabled the OnMouse Animation"
            win.kaomoji = "(⌐■_■)"
            print(win.character_name + ": " + win.text + win.kaomoji)
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
            win.text = "You have enabled the TapBody Animation"
            win.kaomoji = "(⌐■_■)"
            print(win.character_name + ": " + win.text + win.kaomoji)
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
            win.text = "You have disabled the TapBody Animation"
            win.kaomoji = "(⌐■_■)"
            print(win.character_name + ": " + win.text + win.kaomoji)
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
            win.text = "You stop all motions"
            win.kaomoji = "(⌐■_■)"
            print(win.character_name + ": " + win.text + win.kaomoji)
            win.textUpdate()

        win.model.StopAllMotions()

    # Settings Actions
    def on_action_settings(win):
        win.settings_show()

    def on_action_about(win):
        QMessageBox.information(win, "About Me", "My Little Neptune\n"
                                                  "\nThe assistant application on your desktop,"
                                                  "\nwhich pleases you with its appearance every day:)\n"
                                                  "\nDeveloper: Neptune NoiSe"
                                                  "\n(https://github.com/NeptuneNoiSe)\n"
                                                  "\nThe application is based on:"
                                                  "\nPython 3.12"
                                                  "\nPySide6"
                                                  "\nlive2d-py by Arkueid (https://github.com/Arkueid/live2d-py)"
                                                  "\nCompile Heart / Idea Factory Live2D Models\n\n"
                                                  "\n© 2025")

    def on_action_quit(win):
        win.model.SetExpression("Cry")
        if win.condition == "Sleep":
            win.wake_up_func()
        answer = QMessageBox.question(win,
                                      'Quit',
                                      win.character_name + ": " + "Do you really want to leave? T_T",
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                      QMessageBox.StandardButton.No)
        if answer == QMessageBox.StandardButton.Yes:
            print(win.character_name + ":", "GoodBye (^3^)")
            win.quitTimer.start(3000)
            win.text = "GoodBye! See you again!"
            win.kaomoji = "(^3^)"
            print(win.character_name + ": " + win.text + win.kaomoji)
            win.textUpdate()

        else:
            win.t_count = 1
            win.model.ResetExpression()
            win.model.SetExpression("Happy", 5000)
            win.text = "I'm Sooo Happy!"
            win.kaomoji = ":(^~^):"
            print(win.character_name + ": " + win.text + win.kaomoji)
            win.textUpdate()