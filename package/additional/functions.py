from package import resources
from package.additional.resource_manager import ResourceManager
import OpenGL.GL as gl
import numpy as np
from PIL import Image

class Functions:
    def __init__(self, win, model):
        self.model = model
        self.win = win
        self.resource_manager = ResourceManager(resources.RESOURCES_DIRECTORY)
        self.anim_manager = None

    def setLanguage(self):
        """Set App Localization"""
        # List of supported languages (key: value for load_language)
        supported_languages = {
            "Russian": "russian",
            "English": "english",
            # "Key in the interface": "file_name.json"
        }
        # Choose a language or fallback (english)
        language_key = supported_languages.get(self.win.language, "english")
        self.win.lang = self.resource_manager.load_language(language_key)

    def savePng(self, fName):
        """Screenshot function"""
        data = gl.glReadPixels(0, 0, self.win.width(), self.win.height(), gl.GL_RGBA, gl.GL_UNSIGNED_BYTE)
        data = np.frombuffer(data, dtype=np.uint8).reshape(self.win.height(), self.win.width(), 4)
        data = np.flipud(data)
        new_data = np.zeros_like(data)
        for rid, row in enumerate(data):
            for cid, col in enumerate(row):
                color = None
                new_data[rid][cid] = col
                if cid > 0 and data[rid][cid - 1][3] == 0 and col[3] != 0:
                    color = new_data[rid][cid - 1]
                elif cid > 0 and data[rid][cid - 1][3] != 0 and col[3] == 0:
                    color = new_data[rid][cid]
                if color is not None:
                    color[0] = 0 # 255
                    color[1] = 0
                    color[2] = 0
                    color[3] = 0 # 255
                color = None
                if rid > 0:
                    if data[rid - 1][cid][3] == 0 and col[3] != 0:
                        color = new_data[rid - 1][cid]
                    elif data[rid - 1][cid][3] != 0 and col[3] == 0:
                        color = new_data[rid][cid]
                elif col[3] != 0:
                    color = new_data[rid][cid]
                if color is not None:
                    color[0] = 0 #255
                    color[1] = 0
                    color[2] = 0
                    color[3] = 0 # 255
        img = Image.fromarray(new_data, 'RGBA')
        img.save(fName)