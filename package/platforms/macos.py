class FullScreenController:
    def __init__(self, win):
        self.win = win
        self.was_fullscreen = False

    def check_fullscreen(self):
        return False

    def on_fullscreen_enter(self):
        """Actions when entering full-screen mode"""
        pass

    def on_fullscreen_exit(self):
        """Actions when exiting full-screen mode"""
        pass

    def is_fullscreen_window_active(self):
        return False