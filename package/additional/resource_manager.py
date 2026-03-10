import os
from typing import Dict, Any, Optional, List
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
        self.base_characters: Dict[str, Dict] = {}
        self.hdd_characters: Dict[str, Dict] = {}
        self._categorize_characters()
        self.languages: Dict[str, Dict] = {}
        self.background_images: Dict[str, str] = {}
        self.item_images: Dict[str, str] = {}
        self.animation_files: Dict[str, str] = {}
        self.extra_motions: Dict[str, str] = {}
        self._talk_images: Dict[str, str] = {}
        self._mirrored_talk_images: Dict[str, str] = {}
        self._audio_files: Dict[str, str] = {}
        self.audio_files = None
        self._logging_audio_system = False

    def load_language(self, language: str) -> Dict[str, Any]:
        """Loads language file"""
        if language not in self.languages:
            lang_path = os.path.join(self.resources_dir, f"lang/{language.lower()}.json")
            with open(lang_path, encoding="utf-8") as f:
                self.languages[language] = json.load(f)
        return self.languages[language]

    def _load_character_configs(self) -> Dict[str, Dict]:
        """Loads character configs from a JSON file"""
        config_path = os.path.join(self.resources_dir, "configs/models_config.json")
        with open(config_path, encoding="utf-8") as f:
            return json.load(f)

    def get_character_config(self, character_name: str) -> Dict[str, Any]:
        """Returns the configuration of the character by name"""

        return self.character_configs.get(character_name, {})

    def load_background_image(self, image_name: str)-> str:
        if image_name not in self.background_images:
            self.background_images[image_name] = os.path.join(
                self.resources_dir, f"images/bgs/{image_name}.png"
            )
        return self.background_images[image_name]

    def load_item_image(self, image_name: str)-> str:
        if image_name not in self.item_images:
            self.item_images[image_name] = os.path.join(
                self.resources_dir, f"images/items/{image_name}.png"
            )
        return self.item_images[image_name]

    def load_animation(self, anim_name: str) -> str:
        """Returns animation path"""
        if anim_name not in self.animation_files:
            self.animation_files[anim_name] = os.path.join(
                self.resources_dir, f"animations/{anim_name}.webp"
            )
        return self.animation_files[anim_name]

    def load_extra_motions(self) -> Dict[str, str]:
        """Loads all extra animations by scanning the directory"""
        if not self.extra_motions:
            motions_dir = os.path.join(self.resources_dir, "external_motions")
            if not os.path.exists(motions_dir):
                print(f"[Warning] Extra motions directory not found: {motions_dir}")
                return {}

            self.extra_motions = {}

            # Scan files in directory
            for filename in os.listdir(motions_dir):
                if filename.endswith('.motion3.json'):
                    name = filename.replace('.motion3.json', '')
                    full_path = os.path.join(motions_dir, filename)
                    self.extra_motions[name] = full_path
                    # print(f"[Info] Loaded motion: {name}")

            if not self.extra_motions:
                print(f"[Warning] No motion files found in {motions_dir}")
        return self.extra_motions

    def get_character_image_path(self, name):
        character = name.replace(" ", "_").lower()
        path = os.path.join(self.resources_dir, f"images/characters/{character}.png")
        return path

    def load_talk_images(self) -> [Dict[str, str], Dict[str, str]]:
        """Loads all images for speech widgets by scanning directories"""
        if self._talk_images is not None:
            talk_dir = os.path.join(self.resources_dir, "images/talk")
            mirrored_dir = os.path.join(self.resources_dir, "images/talk_mirrored")

            # Check directory
            if not os.path.exists(talk_dir):
                print(f"[Warning] Talk images directory not found: {talk_dir}")
                return {}, {}

            self._talk_images = {}
            self._mirrored_talk_images = {}

            for filename in os.listdir(talk_dir):
                if filename.endswith('.svg'):
                    # Get name from file
                    # "name_talk.svg" -> "Name"
                    name = filename.replace('_talk.svg', '').replace('.svg', '')

                    formatted_name = name.title().replace('_', ' ')

                    # Save path
                    full_path = os.path.join(talk_dir, filename)
                    self._talk_images[formatted_name] = full_path

                    # Find mirrored image
                    mirrored_filename = filename.replace('.svg', '_mirrored.svg')
                    mirrored_path = os.path.join(mirrored_dir, mirrored_filename)

                    if os.path.exists(mirrored_path):
                        self._mirrored_talk_images[formatted_name] = mirrored_path
                    else:
                        self._mirrored_talk_images[formatted_name] = full_path
                        print(f"[Warning] Mirrored image not found for {filename}, using original")

            default_path = os.path.join(talk_dir, "talk.svg")
            if os.path.exists(default_path):
                self._talk_images["default"] = default_path

                default_mirrored = os.path.join(mirrored_dir, "talk_mirrored.svg")
                if os.path.exists(default_mirrored):
                    self._mirrored_talk_images["default"] = default_mirrored
                else:
                    self._mirrored_talk_images["default"] = default_path

            # print(f"[Info] Loaded {len(self._talk_images)} talk image(s) from {talk_dir}")

        return self._talk_images, self._mirrored_talk_images

    def get_talk_image(self, character_name: str, mirrored: bool = False) -> str:
        """Returns the path to the image for the specified character"""
        talk_images, mirrored_images = self.load_talk_images()
        image_map = mirrored_images if mirrored else talk_images

        #print(f"[Debug] Available keys: {list(image_map.keys())}")
        #print(f"[Debug] Looking for: '{character_name}'")

        if character_name in image_map:
            return image_map[character_name]

        variants = [
            character_name,
            character_name.lower(),
            character_name.lower().replace(' ', '_'),
            character_name.replace(' ', '_'),
            character_name.title(),
            character_name.replace(' ', ''),
        ]

        for variant in variants:
            if variant in image_map:
                print(f"[Info] Found match using variant: '{variant}'")
                return image_map[variant]

        print(f"[Warning] Image not found for character: {character_name}, using default")
        return image_map.get("default", "")

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

    def unload_model(self, character_name: str) -> None:
        """Unloads the model from memory"""
        if character_name in self.loaded_models:
            self.loaded_models.pop(character_name)

    def clear_cache(self) -> None:
        """Clears all cached resources"""
        self.loaded_models.clear()
        self.ui_labels.clear()

    def get_label(self, label_name: str, text: str = "", size: QSize = None) -> QLabel:
        """Creates or returns an existing QLabel"""
        if label_name not in self.ui_labels:
            label = QLabel(text)
            if size:
                label.setFixedSize(size)
            self.ui_labels[label_name] = label
        return self.ui_labels[label_name]

    def get_base_character_names(self) -> List[str]:
        """Returns the names of base characters"""
        return list(self.base_characters.keys())

    def get_hdd_character_names(self) -> List[str]:
        """Returns the names of HDD characters"""
        return list(self.hdd_characters.keys())

    def get_all_character_names(self, include_hdd: bool = True) -> List[str]:
        """Returns the names of all characters"""
        if include_hdd:
            return self.get_base_character_names() + self.get_hdd_character_names()
        return self.get_base_character_names()

    def get_alt_form_name(self, character_name: str) -> str:
        config = self.character_configs.get(character_name)
        alt_form_key = None
        if config:
            alt_form_key = config.get('alt_form_key')
        return alt_form_key

    def _categorize_characters(self):
        """Categorize characters (base/hdd)"""
        for char_name, config in self.character_configs.items():
            display_name = config.get('name_key', char_name)

            is_hdd = config.get('hdd_form', False)

            if is_hdd:
                self.hdd_characters[display_name] = config
            else:
                self.base_characters[display_name] = config

        # Logs:
        # print(f"[ResourceManager] Categorized characters:")
        # print(f"  Base: {list(self.base_characters.keys())}")
        # print(f"  HDD: {list(self.hdd_characters.keys())}")
        # print(f"  Total: {len(self.character_configs)} characters")

    def set_debug_audio_system_logging(self, enabled: bool):
        """Logging management"""
        self._logging_audio_system = enabled

        # self.animation_player._log_callbacks = enabled

    def _character_to_folder_name(self, character_name: str) -> str:
        """Converts the character's name to a folder name (removes spaces)"""
        return character_name.replace(" ", "")

    def load_audio_files(self) -> Dict[str, Dict[str, str]]:
        """Loads all audio files with fallback to root audio folder"""
        if not self._audio_files:
            audio_dir = os.path.join(self.resources_dir, "audio")

            # Load JSON config
            audio_config_path = os.path.join(self.resources_dir, "configs/audio_config.json")
            try:
                with open(audio_config_path, 'r', encoding='utf-8') as f:
                    audio_structure = json.load(f)
            except FileNotFoundError:
                print(f" Audio config not found: {audio_config_path}")
                return {}
            except json.JSONDecodeError as e:
                print(f" Error parsing audio config: {e}")
                return {}

            self._audio_files = {}

            for character_name, audio in audio_structure.items():
                # Convert the name to a folder
                folder_name = self._character_to_folder_name(character_name)
                character_dir = os.path.join(audio_dir, folder_name)

                character_dict = {}
                for sound_type, filename in audio.items():
                    # Try to find a character in the folder
                    character_file = os.path.join(character_dir, filename)

                    if os.path.exists(character_file):
                        character_dict[sound_type] = character_file
                    else:
                        # Fallback: search for audio at the root
                        root_file = os.path.join(audio_dir, filename)
                        if os.path.exists(root_file):
                            character_dict[sound_type] = root_file
                        else:
                            # Final fallback: use default_sound from the root
                            default_root = os.path.join(audio_dir, "default_sound.wav")
                            if os.path.exists(default_root):
                                character_dict[sound_type] = default_root
                            else:
                                # Ultimate fallback: leave the path, but there is no file
                                character_dict[sound_type] = character_file

                self._audio_files[character_name] = character_dict
            # Audio System Diagnostic
            if self._logging_audio_system:
                self.debug_audio_structure()
                print(f"✅ Audio files loaded with root fallback: {list(self._audio_files.keys())}")

        return self._audio_files

    def get_audio(self, character_name: str, audio_type: str = "default") -> Optional[str]:
        """Gets audio file"""
        audio_files = self.load_audio_files()

        search_paths = [
            (character_name, audio_type),
            #(character_name, "default"),
            #("default", audio_type),
            # ("default", "default")
        ]

        for search_char, search_type in search_paths:  # ← Более понятные имена
            if search_char in audio_files and search_type in audio_files[search_char]:
                audio_file = audio_files[search_char][search_type]
                if os.path.exists(audio_file):
                    if search_char == character_name and search_type == audio_type:
                        if self._logging_audio_system:
                            print(f"✓ Exact match: {character_name} - {audio_type}")
                    else:
                        if self._logging_audio_system:
                            print(f"⚠ Fallback: {search_char} - {search_type} for {character_name} - {audio_type}")
                    return audio_file

        if self._logging_audio_system:
            print(f"✗ No audio found for {character_name} - {audio_type}")
        return None

    def debug_audio_structure(self):
        """Detailed audio system diagnostics"""
        print("\n" + "=" * 50)
        print("AUDIO SYSTEM DEBUG")
        print("=" * 50)

        # Check the basic paths
        audio_dir = os.path.join(self.resources_dir, "audio")
        print(f"1. Resources dir: {self.resources_dir}")
        print(f"2. audio dir: {audio_dir}")
        print(f"3. audio dir exists: {os.path.exists(audio_dir)}")

        if os.path.exists(audio_dir):
            print(f"4. Files in audio directory:")
            for file in os.listdir(audio_dir):
                if file.endswith('.wav'):
                    print(f"   ✓ {file}")
                else:
                    print(f"   - {file} (not wav)")
        else:
            print("4. ❌ audio directory not found!")

        # Check the download of audio files
        print("\n5. Loading audio files...")
        audio_files = self.load_audio_files()
        print(f"6. Audio structure keys: {list(audio_files.keys())}")

        # Detailed view of the structure
        print("\n7. Detailed audio structure:")
        for character, audio in audio_files.items():
            print(f"   {character}:")
            for sound_type, filepath in audio.items():
                exists = "✓" if os.path.exists(filepath) else "❌"
                print(f"     {sound_type}: {exists} {filepath}")

        # 4. Test Search for Maho
        #print(f"\n8. Testing get_audio for Maho:")
        #result = self.get_audio("Maho", "default")
        #print(f"   Result: {result}")
        #if result:
        #    print(f"   File exists: {os.path.exists(result)}")

        print("=" * 50)