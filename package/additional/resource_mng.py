import os
from typing import Dict, Optional, Any
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

    def _load_character_configs(self) -> Dict[str, Dict]:
        """Loads character configs from a JSON file"""
        config_path = os.path.join(self.resources_dir, "configs/model_configs.json")
        with open(config_path, encoding="utf-8") as f:
            return json.load(f)

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