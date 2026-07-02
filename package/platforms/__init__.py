import sys

if sys.platform == "win32":
    from .winapi import FullScreenController
elif sys.platform.startswith("linux"):
    from .linux import FullScreenController
elif sys.platform == "darwin":
    from .macos import FullScreenController
else:
    raise NotImplementedError(f"Unsupported platform: {sys.platform}")