"""
Fullscreen detection is heuristic-based.

Windows doesn't provide an official API to determine whether
the foreground application is running in fullscreen mode.

The implementation compares the foreground window bounds with
the monitor bounds and filters known shell windows.
"""
import ctypes
from ctypes import wintypes

from PySide6.QtCore import Qt

user32 = ctypes.windll.user32
dwmapi = ctypes.windll.dwmapi

MONITOR_DEFAULTTONEAREST = 2
DWMWA_EXTENDED_FRAME_BOUNDS = 9

IGNORED_CLASSES = {
    "Progman",
    "WorkerW",
    "Shell_TrayWnd",
}


def is_window_fullscreen(hwnd):
    if get_window_class(hwnd) in IGNORED_CLASSES:
        return False

    if not user32.IsWindowVisible(hwnd):
        return False

    if user32.IsIconic(hwnd):
        return False

    rect = get_window_rect(hwnd)
    mon = get_monitor_rect(hwnd)

    tolerance = 2
    # print(hex(hwnd), get_window_class(hwnd))

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

def get_window_class(hwnd):
    buf = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, buf, 256)
    #print(buf.value)
    return buf.value

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

class FullScreenController:
    def __init__(self, win):
        self.win = win
        self.was_fullscreen = False

    def check_fullscreen(self):
        if not self.win.on_top:
            return
        is_fullscreen = self.is_fullscreen_window_active()

        if is_fullscreen and not self.was_fullscreen:
            #print(f"FullScreen App on: {self.win.screen().name()}")
            self.on_fullscreen_enter()
        elif not is_fullscreen and self.was_fullscreen:
            #print("Exit FullScreen App")
            self.on_fullscreen_exit()

        self.was_fullscreen = is_fullscreen

    def on_fullscreen_enter(self):
        """Actions when entering full-screen mode"""
        # IMPORTANT:
        # hide() must be called before showMinimized().
        # Reversing the order causes the OpenGL window to be destroyed.
        if self.win.windowFlags() & Qt.WindowType.WindowStaysOnTopHint:
            self.win.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
            self.win.hide()
            self.win.showMinimized()

    def on_fullscreen_exit(self):
        """Actions when exiting full-screen mode"""
        if not (self.win.windowFlags() & Qt.WindowType.WindowStaysOnTopHint):
            self.win.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
            self.win.show()
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