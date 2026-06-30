import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32
dwmapi = ctypes.windll.dwmapi

MONITOR_DEFAULTTONEAREST = 2
DWMWA_EXTENDED_FRAME_BOUNDS = 9

def is_window_fullscreen(hwnd):
    if not user32.IsWindowVisible(hwnd):
        return False

    if user32.IsIconic(hwnd):
        return False

    rect = get_window_rect(hwnd)
    mon = get_monitor_rect(hwnd)

    tolerance = 2

    return (
            abs(rect.left - mon.left) <= tolerance and
            abs(rect.top - mon.top) <= tolerance and
            abs(rect.right - mon.right) <= tolerance and
            abs(rect.bottom - mon.bottom) <= tolerance
    )

def get_window_rect(hwnd):
    rect = RECT()

    if dwmapi.DwmGetWindowAttribute(
            hwnd,
            DWMWA_EXTENDED_FRAME_BOUNDS,
            ctypes.byref(rect),
            ctypes.sizeof(rect)) == 0:
        return rect

    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    return rect

def get_monitor_rect(hwnd):
    monitor = user32.MonitorFromWindow(hwnd, MONITOR_DEFAULTTONEAREST)

    info = MONITORINFO()
    info.cbSize = ctypes.sizeof(info)

    user32.GetMonitorInfoW(monitor, ctypes.byref(info))

    return info.rcMonitor

class RECT(ctypes.Structure):
    _fields_ = [
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG),
    ]

class MONITORINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("rcMonitor", RECT),
        ("rcWork", RECT),
        ("dwFlags", wintypes.DWORD),
    ]

class FullscreenController:
    def __init__(self, win):
        self.win = win
        self.was_fullscreen = False

    def check_fullscreen(self):
        if not self.win.on_top:
            return
        is_fullscreen = self.is_fullscreen_window_active()

        if is_fullscreen and not self.was_fullscreen:
            # print(f"FullScreen App on: {self.screen().name()}")
            self.on_fullscreen_enter()
        elif not is_fullscreen and self.was_fullscreen:
            # print("Exit FullScreen App")
            self.on_fullscreen_exit()

        self.was_fullscreen = is_fullscreen

    def on_fullscreen_enter(self):
        """Actions when entering full-screen mode"""
        self.win.showMinimized()

    def on_fullscreen_exit(self):
        """Actions when exiting full-screen mode"""
        self.win.showNormal()

    def is_fullscreen_window_active(self):
        hwnd = user32.GetForegroundWindow()

        # if hwnd == int(self.winId()):
        #    return False
        my_hwnd = self.win.windowHandle().winId()

        if hwnd == my_hwnd:
            return False

        my_monitor = user32.MonitorFromWindow(
            int(self.win.winId()),
            MONITOR_DEFAULTTONEAREST
        )

        other_monitor = user32.MonitorFromWindow(
            hwnd,
            MONITOR_DEFAULTTONEAREST
        )

        if my_monitor != other_monitor:
            return False

        return is_window_fullscreen(hwnd)