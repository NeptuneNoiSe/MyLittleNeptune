import os
from typing import Dict, Any
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import QSize

import live2d.v3 as live2d

import json

class ResourceManager:
    def __init__(self, resources_dir: str):
        self.resources_dir = resources_dir
        self.loaded_models: Dict[str, live2d.Model] = {}
        self.loaded_animations: Dict[str, Dict] = {}
        self.ui_labels: Dict[str, QLabel] = {}
        self.character_configs: Dict[str, Dict] = self._load_character_configs()
        self.languages: Dict[str, Dict] = {}
        self.animation_files: Dict[str, str] = {}
        self.extra_motions: Dict[str, str] = {}
        self._talk_images: Dict[str, str] = {}
        self._mirrored_talk_images: Dict[str, str] = {}

    def _load_character_configs(self) -> Dict[str, Dict]:
        """Loads character configs from a JSON file"""
        config_path = os.path.join(self.resources_dir, "configs/model_configs.json")
        with open(config_path, encoding="utf-8") as f:
            return json.load(f)

    def load_language(self, language: str) -> Dict[str, Any]:
        """Loads language file"""
        if language not in self.languages:
            lang_path = os.path.join(self.resources_dir, f"lang/{language.lower()}.json")
            with open(lang_path, encoding="utf-8") as f:
                self.languages[language] = json.load(f)
        return self.languages[language]

    def load_animation(self, anim_name: str) -> str:
        """Returns animation path"""
        if anim_name not in self.animation_files:
            self.animation_files[anim_name] = os.path.join(
                self.resources_dir, f"animations/{anim_name}.webp"
            )
        return self.animation_files[anim_name]

    def load_extra_motions(self) -> Dict[str, str]:
        """Loads all extra animations"""
        if not self.extra_motions:
            motions_dir = os.path.join(self.resources_dir, "v3/external_motions")
            motion_files = {
                "drag_down": "drag_down.motion3.json",
                "side_touch_head": "side_touch_head.motion3.json",
                "touch_body": "touch_body.motion3.json",
                "touch_body2": "touch_body2.motion3.json",
                "touch_body3": "touch_body3.motion3.json",
                "touch_bra": "touch_bra.motion3.json",
                "touch_bra1": "touch_bra1.motion3.json",
                "touch_bra2": "touch_bra2.motion3.json",
                "touch_bra3": "touch_bra3.motion3.json",
                "touch_head": "touch_head.motion3.json",
                "touch_head2": "touch_head2.motion3.json",
                "touch_hl": "touch_hl.motion3.json",
                "touch_hl1": "touch_hl1.motion3.json",
                "touch_hl2": "touch_hl2.motion3.json",
                "touch_hr": "touch_hr.motion3.json",
                "touch_hr1": "touch_hr1.motion3.json",
                "touch_hr2": "touch_hr2.motion3.json",
                "touch_leg": "touch_leg.motion3.json",
                "touch_leg1": "touch_leg1.motion3.json",
                "touch_leg2": "touch_leg2.motion3.json",
                "touch_leg3": "touch_leg3.motion3.json",
            }
            self.extra_motions = {
                name: os.path.join(motions_dir, filename)
                for name, filename in motion_files.items()
            }
        return self.extra_motions

    def load_talk_images(self) -> [Dict[str, str], Dict[str, str]]:
        """Loads all images for speech widgets"""
        if self._talk_images is not None:
            talk_dir = os.path.join(self.resources_dir, "images/talk")
            mirrored_dir = os.path.join(self.resources_dir, "images/talk_mirrored")

            # File names for all characters
            image_files = {
                "Neptune": "neptune_talk.svg",
                "Purple Heart": "purple_heart_talk.svg",
                "Noire": "noire_talk.svg",
                "Black Heart": "black_heart_talk.svg",
                "Blanc": "blanc_talk.svg",
                "White Heart": "white_heart_talk.svg",
                "Vert": "vert_talk.svg",
                "Green Heart": "green_heart_talk.svg",
                "NepGear": "nepgear_talk.svg",
                "Purple Sister": "purple_sister_talk.svg",
                "Uni": "uni_talk.svg",
                "Black Sister": "black_sister_talk.svg",
                "Rom": "rom_talk.svg",
                "White Sister Rom": "white_sister_rom_talk.svg",
                "Ram": "ram_talk.svg",
                "White Sister Ram": "white_sister_ram_talk.svg",
                "Histoire": "histoire_talk.svg",
                "default": "talk.svg"
            }

            # Creating paths for normal and mirror images
            self._talk_images = {
                name: os.path.join(talk_dir, filename)
                for name, filename in image_files.items()
            }

            self._mirrored_talk_images = {
                name: os.path.join(mirrored_dir, filename.replace('.svg', '_mirrored.svg'))
                for name, filename in image_files.items()
            }

        return self._talk_images, self._mirrored_talk_images

    def get_talk_image(self, character_name: str, mirrored: bool = False) -> str:
        """Returns the path to the image for the specified character"""
        talk_images, mirrored_images = self.load_talk_images()
        image_map = mirrored_images if mirrored else talk_images
        return image_map.get(character_name, image_map["default"])

    def get_character_config(self, character_name: str) -> Dict[str, Any]:
        """Returns the configuration of the character by name"""
        return self.character_configs.get(character_name, {})

    def get_model(self, character_name: str) -> live2d.Model:
        """Returns the character model, loading it if necessary"""
        if character_name not in self.loaded_models:
            model_path = os.path.join(
                self.resources_dir,
                self.character_configs[character_name]["model_path"]
            )
            model = live2d.Model()
            model.LoadModelJson(model_path)
            self.loaded_models[character_name] = model
        return self.loaded_models[character_name]

    def get_label(self, label_name: str, text: str = "", size: QSize = None) -> QLabel:
        """Creates or returns an existing QLabel"""
        if label_name not in self.ui_labels:
            label = QLabel(text)
            if size:
                label.setFixedSize(size)
            self.ui_labels[label_name] = label
        return self.ui_labels[label_name]

    def unload_model(self, character_name: str) -> None:
        """Unloads the model from memory"""
        if character_name in self.loaded_models:
            self.loaded_models.pop(character_name)

    def clear_cache(self) -> None:
        """Clears all cached resources"""
        self.loaded_models.clear()
        self.ui_labels.clear()