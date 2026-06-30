import sys

if sys.platform == "win32":
    from .winapi import FullscreenController
elif sys.platform.startswith("linux"):
    from .linux import FullscreenController
elif sys.platform == "darwin":
    from .macos import FullscreenController
else:
    raise NotImplementedError(f"Unsupported platform: {sys.platform}")