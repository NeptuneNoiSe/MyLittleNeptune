import os
from typing import Dict, Any, Optional
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
        self._audio_files: Dict[str, str] = {}
        self.audio_files = None

    def _load_character_configs(self) -> Dict[str, Dict]:
        """Loads character configs from a JSON file"""
        config_path = os.path.join(self.resources_dir, "configs/models_config.json")
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
                "Maho": "maho_talk.svg",
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

    def load_audio_files(self) -> Dict[str, Dict[str, str]]:
        """Loads all audio files with fallback to root audio folder"""
        if not self._audio_files:
            audio_dir = os.path.join(self.resources_dir, "audio")

            audio_structure = {
                "Neptune": {
                    "greeting": "hello.wav",
                    "goodbye": "goodbye.wav",
                    "me": "me.wav",
                    "drag": "drag.wav",
                    "stay": "stay.wav",
                    "lost": "lost.wav",
                    "transform": "transform.wav",
                    "transformed": "transformed.wav",
                    "transform_fail": "transform_fail.wav",
                    "woke": "woke.wav",
                    "wake_up": "wake_up.wav",
                    "pre_sleep": "pre_sleep.wav",
                    "sleep": "sleep.wav",
                    "settings": "settings.wav",
                    "happy": "happy.wav",
                    "angry": "angry.wav",
                    "sad": "sad.wav",
                    "smile": "smile.wav",
                    "tired": "tired.wav",
                    "closedeyes": "closed_eyes.wav",
                    "cry": "cry.wav",
                    "fear": "fear.wav",
                    "star": "star.wav",
                    "surprised": "surprised.wav",
                    "funny": "funny.wav",
                    "really_quit": "really_quit.wav",
                    "quit": "quit.wav",
                    "normal": "normal.wav",
                    "default": "default.wav"
                },
                "Purple Heart": {
                    "greeting": "hello.wav",
                    "goodbye": "goodbye.wav",
                    "me": "me.wav",
                    "drag": "drag.wav",
                    "stay": "stay.wav",
                    "lost": "lost.wav",
                    "transform": "transform.wav",
                    "transformed": "transformed.wav",
                    "transform_fail": "transform_fail.wav",
                    "woke": "woke.wav",
                    "wake_up": "wake_up.wav",
                    "pre_sleep": "pre_sleep.wav",
                    "sleep": "sleep.wav",
                    "settings": "settings.wav",
                    "happy": "happy.wav",
                    "angry": "angry.wav",
                    "sad": "sad.wav",
                    "smile": "smile.wav",
                    "tired": "tired.wav",
                    "closedeyes": "closed_eyes.wav",
                    "cry": "cry.wav",
                    "fear": "fear.wav",
                    "surprised": "surprised.wav",
                    "funnyhdd": "funny.wav",
                    "really_quit": "really_quit.wav",
                    "quit": "quit.wav",
                    "normal": "normal.wav",
                    "default": "default.wav"
                },
                "Noire": {
                    "greeting": "hello.wav",
                    "goodbye": "goodbye.wav",
                    "me": "me.wav",
                    "drag": "drag.wav",
                    "stay": "stay.wav",
                    "lost": "lost.wav",
                    "transform": "transform.wav",
                    "transformed": "transformed.wav",
                    "transform_fail": "transform_fail.wav",
                    "woke": "woke.wav",
                    "wake_up": "wake_up.wav",
                    "pre_sleep": "pre_sleep.wav",
                    "sleep": "sleep.wav",
                    "settings": "settings.wav",
                    "happy": "happy.wav",
                    "angry": "angry.wav",
                    "sad": "sad.wav",
                    "smile": "smile.wav",
                    "tired": "tired.wav",
                    "closedeyes": "closed_eyes.wav",
                    "cry": "cry.wav",
                    "fear": "fear.wav",
                    "surprised": "surprised.wav",
                    "funny": "funny.wav",
                    "serious": "serious.wav",
                    "really_quit": "really_quit.wav",
                    "quit": "quit.wav",
                    "normal": "normal.wav",
                    "default": "default.wav"
                },
                "Black Heart": {
                    "greeting": "hello.wav",
                    "goodbye": "goodbye.wav",
                    "me": "me.wav",
                    "drag": "drag.wav",
                    "stay": "stay.wav",
                    "lost": "lost.wav",
                    "transform": "transform.wav",
                    "transformed": "transformed.wav",
                    "transform_fail": "transform_fail.wav",
                    "woke": "woke.wav",
                    "wake_up": "wake_up.wav",
                    "pre_sleep": "pre_sleep.wav",
                    "sleep": "sleep.wav",
                    "settings": "settings.wav",
                    "happy": "happy.wav",
                    "angry": "angry.wav",
                    "sad": "sad.wav",
                    "smile": "smile.wav",
                    "tired": "tired.wav",
                    "closedeyes": "closed_eyes.wav",
                    "cry": "cry.wav",
                    "fear": "fear.wav",
                    "surprised": "surprised.wav",
                    "funnyhdd": "funny.wav",
                    "really_quit": "really_quit.wav",
                    "quit": "quit.wav",
                    "normal": "normal.wav",
                    "default": "default.wav"
                },
                "Blanc": {
                    "greeting": "hello.wav",
                    "goodbye": "goodbye.wav",
                    "me": "me.wav",
                    "drag": "drag.wav",
                    "stay": "stay.wav",
                    "lost": "lost.wav",
                    "transform": "transform.wav",
                    "transformed": "transformed.wav",
                    "transform_fail": "transform_fail.wav",
                    "woke": "woke.wav",
                    "wake_up": "wake_up.wav",
                    "pre_sleep": "pre_sleep.wav",
                    "sleep": "sleep.wav",
                    "settings": "settings.wav",
                    "happy": "happy.wav",
                    "angry": "angry.wav",
                    "sad": "sad.wav",
                    "smile": "smile.wav",
                    "tired": "tired.wav",
                    "closedeyes": "closed_eyes.wav",
                    "cry": "cry.wav",
                    "fear": "fear.wav",
                    "surprised": "surprised.wav",
                    "funnybl": "funny.wav",
                    "serious": "serious.wav",
                    "really_quit": "really_quit.wav",
                    "quit": "quit.wav",
                    "normal": "normal.wav",
                    "default": "default.wav"
                },
                "White Heart": {
                    "greeting": "hello.wav",
                    "goodbye": "goodbye.wav",
                    "me": "me.wav",
                    "drag": "drag.wav",
                    "stay": "stay.wav",
                    "lost": "lost.wav",
                    "transform": "transform.wav",
                    "transformed": "transformed.wav",
                    "transform_fail": "transform_fail.wav",
                    "woke": "woke.wav",
                    "wake_up": "wake_up.wav",
                    "pre_sleep": "pre_sleep.wav",
                    "sleep": "sleep.wav",
                    "settings": "settings.wav",
                    "happy": "happy.wav",
                    "angry": "angry.wav",
                    "sad": "sad.wav",
                    "smile": "smile.wav",
                    "tired": "tired.wav",
                    "closedeyes": "closed_eyes.wav",
                    "cry": "cry.wav",
                    "fearwh": "fear.wav",
                    "surprised": "surprised.wav",
                    "funnyhdd": "funny.wav",
                    "really_quit": "really_quit.wav",
                    "quit": "quit.wav",
                    "normal": "normal.wav",
                    "default": "default.wav"
                },
                "Vert": {
                    "greeting": "hello.wav",
                    "goodbye": "goodbye.wav",
                    "me": "me.wav",
                    "drag": "drag.wav",
                    "stay": "stay.wav",
                    "lost": "lost.wav",
                    "transform": "transform.wav",
                    "transformed": "transformed.wav",
                    "transform_fail": "transform_fail.wav",
                    "woke": "woke.wav",
                    "wake_up": "wake_up.wav",
                    "pre_sleep": "pre_sleep.wav",
                    "sleep": "sleep.wav",
                    "settings": "settings.wav",
                    "happy": "happy.wav",
                    "angry": "angry.wav",
                    "sad": "sad.wav",
                    "smile": "smile.wav",
                    "tired": "tired.wav",
                    "closedeyes": "closed_eyes.wav",
                    "cry": "cry.wav",
                    "horny": "horny.wav",
                    "surprised": "surprised.wav",
                    "funny": "funny.wav",
                    "really_quit": "really_quit.wav",
                    "quit": "quit.wav",
                    "normal": "normal.wav",
                    "default": "default.wav"
                },
                "Green Heart": {
                    "greeting": "hello.wav",
                    "goodbye": "goodbye.wav",
                    "me": "me.wav",
                    "drag": "drag.wav",
                    "stay": "stay.wav",
                    "lost": "lost.wav",
                    "transform": "transform.wav",
                    "transformed": "transformed.wav",
                    "transform_fail": "transform_fail.wav",
                    "woke": "woke.wav",
                    "wake_up": "wake_up.wav",
                    "pre_sleep": "pre_sleep.wav",
                    "sleep": "sleep.wav",
                    "settings": "settings.wav",
                    "happy": "happy.wav",
                    "angry": "angry.wav",
                    "sad": "sad.wav",
                    "smile": "smile.wav",
                    "tired": "tired.wav",
                    "closedeyes": "closed_eyes.wav",
                    "surprised": "surprised.wav",
                    "funnyhdd": "funny.wav",
                    "really_quit": "really_quit.wav",
                    "quit": "quit.wav",
                    "normal": "normal.wav",
                    "default": "default.wav"
                },
                "NepGear": {
                    "greeting": "hello.wav",
                    "goodbye": "goodbye.wav",
                    "me": "me.wav",
                    "drag": "drag.wav",
                    "stay": "stay.wav",
                    "lost": "lost.wav",
                    "transform": "transform.wav",
                    "transformed": "transformed.wav",
                    "transform_fail": "transform_fail.wav",
                    "woke": "woke.wav",
                    "wake_up": "wake_up.wav",
                    "pre_sleep": "pre_sleep.wav",
                    "sleep": "sleep.wav",
                    "settings": "settings.wav",
                    "happy": "happy.wav",
                    "angry": "angry.wav",
                    "sad": "sad.wav",
                    "smile": "smile.wav",
                    "tired": "tired.wav",
                    "closedeyes": "closed_eyes.wav",
                    "cry": "cry.wav",
                    "fear": "fear.wav",
                    "star": "star.wav",
                    "surprised": "surprised.wav",
                    "funny": "funny.wav",
                    "really_quit": "really_quit.wav",
                    "quit": "quit.wav",
                    "normal": "normal.wav",
                    "default": "default.wav"
                },
                "Purple Sister": {
                    "greeting": "hello.wav",
                    "goodbye": "goodbye.wav",
                    "me": "me.wav",
                    "drag": "drag.wav",
                    "stay": "stay.wav",
                    "lost": "lost.wav",
                    "transform": "transform.wav",
                    "transformed": "transformed.wav",
                    "transform_fail": "transform_fail.wav",
                    "woke": "woke.wav",
                    "wake_up": "wake_up.wav",
                    "pre_sleep": "pre_sleep.wav",
                    "sleep": "sleep.wav",
                    "settings": "settings.wav",
                    "happy": "happy.wav",
                    "angry": "angry.wav",
                    "sad": "sad.wav",
                    "smile": "smile.wav",
                    "tired": "tired.wav",
                    "closedeyes": "closed_eyes.wav",
                    "cry": "cry.wav",
                    "fear": "fear.wav",
                    "surprised": "surprised.wav",
                    "really_quit": "really_quit.wav",
                    "quit": "quit.wav",
                    "normal": "normal.wav",
                    "default": "default.wav"
                },
                "Uni": {
                    "greeting": "hello.wav",
                    "goodbye": "goodbye.wav",
                    "me": "me.wav",
                    "drag": "drag.wav",
                    "stay": "stay.wav",
                    "lost": "lost.wav",
                    "transform": "transform.wav",
                    "transformed": "transformed.wav",
                    "transform_fail": "transform_fail.wav",
                    "woke": "woke.wav",
                    "wake_up": "wake_up.wav",
                    "pre_sleep": "pre_sleep.wav",
                    "sleep": "sleep.wav",
                    "settings": "settings.wav",
                    "happy": "happy.wav",
                    "angry": "angry.wav",
                    "sad": "sad.wav",
                    "smile": "smile.wav",
                    "tired": "tired.wav",
                    "closedeyes": "closed_eyes.wav",
                    "cry": "cry.wav",
                    "surprised": "surprised.wav",
                    "funny": "funny.wav",
                    "really_quit": "really_quit.wav",
                    "quit": "quit.wav",
                    "normal": "normal.wav",
                    "default": "default.wav"
                },
                "Black Sister": {
                    "greeting": "hello.wav",
                    "goodbye": "goodbye.wav",
                    "me": "me.wav",
                    "drag": "drag.wav",
                    "stay": "stay.wav",
                    "lost": "lost.wav",
                    "transform": "transform.wav",
                    "transformed": "transformed.wav",
                    "transform_fail": "transform_fail.wav",
                    "woke": "woke.wav",
                    "wake_up": "wake_up.wav",
                    "pre_sleep": "pre_sleep.wav",
                    "sleep": "sleep.wav",
                    "settings": "settings.wav",
                    "happy": "happy.wav",
                    "angry": "angry.wav",
                    "sad": "sad.wav",
                    "smile": "smile.wav",
                    "tired": "tired.wav",
                    "closedeyes": "closed_eyes.wav",
                    "cry": "cry.wav",
                    "fear": "fear.wav",
                    "really_quit": "really_quit.wav",
                    "quit": "quit.wav",
                    "normal": "normal.wav",
                    "default": "default.wav"
                },
                "default": {
                    "default": "nep_nep.wav"
                }
            }

            self._audio_files = {}

            for character_name, audio in audio_structure.items():
                # Преобразуем имя в папку
                folder_name = self._character_to_folder_name(character_name)
                character_dir = os.path.join(audio_dir, folder_name)

                character_dict = {}
                for sound_type, filename in audio.items():
                    # 1. Пытаемся найти в папке персонажа
                    character_file = os.path.join(character_dir, filename)

                    if os.path.exists(character_file):
                        character_dict[sound_type] = character_file
                    else:
                        # 2. Fallback: ищем в корне audio
                        root_file = os.path.join(audio_dir, filename)
                        if os.path.exists(root_file):
                            character_dict[sound_type] = root_file
                        else:
                            # 3. Final fallback: используем nep_nep.wav из корня
                            nep_nep_root = os.path.join(audio_dir, "nep.wav")
                            if os.path.exists(nep_nep_root):
                                character_dict[sound_type] = nep_nep_root
                            else:
                                # 4. Ultimate fallback: оставляем путь, но файла нет
                                character_dict[sound_type] = character_file

                self._audio_files[character_name] = character_dict
            # Audio System Diagnostic
            self.debug_audio_structure()
            print(f"✅ Audio files loaded with root fallback: {list(self._audio_files.keys())}")

        return self._audio_files

    def _character_to_folder_name(self, character_name: str) -> str:
        """Преобразует имя персонажа в имя папки (удаляет пробелы)"""
        return character_name.replace(" ", "")

    def get_audio(self, character_name: str, audio_type: str = "default") -> Optional[str]:
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
                        print(f"✓ Exact match: {character_name} - {audio_type}")
                    else:
                        print(f"⚠ Fallback: {search_char} - {search_type} for {character_name} - {audio_type}")
                    return audio_file

        print(f"✗ No audio found for {character_name} - {audio_type}")
        return None

    def debug_audio_structure(self):
        """Детальная диагностика аудио системы"""
        print("\n" + "=" * 50)
        print("AUDIO SYSTEM DEBUG")
        print("=" * 50)

        # 1. Проверяем базовые пути
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

        # 2. Проверяем загрузку аудио файлов
        print("\n5. Loading audio files...")
        audio_files = self.load_audio_files()
        print(f"6. Audio structure keys: {list(audio_files.keys())}")

        # 3. Детальный просмотр структуры
        print("\n7. Detailed audio structure:")
        for character, audio in audio_files.items():
            print(f"   {character}:")
            for sound_type, filepath in audio.items():
                exists = "✓" if os.path.exists(filepath) else "❌"
                print(f"     {sound_type}: {exists} {filepath}")

        # 4. Тестируем поиск для Maho
        #print(f"\n8. Testing get_audio for Maho:")
        #result = self.get_audio("Maho", "default")
        #print(f"   Result: {result}")
        #if result:
        #    print(f"   File exists: {os.path.exists(result)}")

        print("=" * 50)