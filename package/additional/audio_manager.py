import os

from PySide6.QtCore import QTimer, QDateTime


class AudioManager:
    def __init__(self, win, resources_dir: str):
        self.win = win
        self.resources_dir = resources_dir
        self.audio_switch = True

        # self.master_volume = (self.win.app_config.master/100)  # Main Volume (0.0 - 1.0)

        self._defaults = {
            'master': 1.0,    # 100%
            'voice': 1.0,     # 100%
            'sfx': 0.9,       # 90%
            'bgm': 0.6,       # 60%
            'ambient': 0.5    # 50%
        }

        self._init_pygame_mixer()
        self.current_sounds = {}  # Dictionary for tracking active sounds
        self.sound_categories = {}  # To group sounds by category
        self.category_volumes = {}
        self.load_config()

        self.previous_bgm_name = ""  # Storing the previous value

        self.bg_music_timer = QTimer()
        self.bg_music_timer.timeout.connect(self.check_bgm_change)
        self.bg_music_timer.start(1000)  # Check every second

    @property
    def bgm_name(self):
        return self.win.bgm_name

    @property
    def bgm_group(self):
        return self.win.bgm_group

    @property
    def current_sing_song(self):
        return self.win.current_sing_song

    @property
    def song_duration(self):
       return self.win.song_duration

    @song_duration.setter
    def song_duration(self, value: int):
        self.win.song_duration = value

    def check_bgm_change(self):
        """Check the bgm_name change every second"""
        if self.previous_bgm_name != self.bgm_name:
            # print(f"🎵 BGM change: {self.previous_bgm_name} -> {self.bgm_name}")
            self.previous_bgm_name = self.bgm_name
            if not self.bgm_name:
                self.stop_category("bgm")
            else:
                self.play_bg_music()

    def set_bgm_name(self, value):
        """Set bgm_name method"""
        self.bgm_name = value
        # Force Set
        self.play_bg_music()

    def load_config(self):
        """Loads or reloads the settings from the config"""
        # Master Volume
        self.master_volume = self._get_config_value('master')

        # Categories
        self.category_volumes = {
            "voice": self._get_config_value('voice'),
            "sfx": self._get_config_value('sfx'),
            "bgm": self._get_config_value('bgm'),
            "ambient": self._get_config_value('ambient')
        }

        # Force Apply
        #self.apply_all_volumes()

    def _get_config_value(self, key):
        """Safely gets the value from the config"""
        try:
            value = getattr(self.win.app_config, key, self._defaults[key] * 100)
            # If value > 1, its percent, convert
            if value > 1.0:
                return value / 100.0
            return value
        except:
            return self._defaults[key]

    def reload_config(self):
        """Public method for reloading the config"""
        self.load_config()

    @property
    def wavHandler(self):
        """Access to wavHandler through the main window"""
        if self.win and hasattr(self.win, 'wavHandler'):
            return self.win.wavHandler
        return None

    def _init_pygame_mixer(self):
        """Initializing the pygame sound module only"""
        try:
            # Remove greeting message
            os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
            import pygame.mixer

            # Initialize ONLY the mixer with a large number of channels
            pygame.mixer.init(frequency=44100, size=-16, channels=16, buffer=512)

        except ImportError:
            print("✗ Pygame not available")

    #  Volume Control Methods
    def set_master_volume(self, volume: float, update_existing: bool = True):
        """Set Masater Volume (0.0 - 1.0)"""
        self.master_volume = max(0.0, min(1.0, volume))

        if update_existing:
            # Update volume
            self._update_all_volumes()

    def set_category_volume(self, category: str, volume: float, update_existing: bool = True):
        """Set volume for categories (0.0 - 1.0)"""
        if category in self.category_volumes:
            self.category_volumes[category] = max(0.0, min(1.0, volume))

            if update_existing:
                # Updating the volume of all sounds in this category
                self._update_category_volumes(category)

    def get_category_volume(self, category: str) -> float:
        """Get volume for categories"""
        return self.category_volumes.get(category, 1.0)

    def get_effective_volume(self, category: str) -> float:
        """Get the total volume for a category based on master_volume"""
        category_vol = self.category_volumes.get(category, 1.0)
        return self.master_volume * category_vol

    def _update_all_volumes(self):
        """Update the volume of all current sounds"""
        for sound_id, sound_data in self.current_sounds.items():
            category = sound_data['category']
            effective_volume = self.get_effective_volume(category)
            sound_data['sound'].set_volume(effective_volume)

    def _update_category_volumes(self, category: str):
        """Update the volume of all sounds of a certain category"""
        effective_volume = self.get_effective_volume(category)

        if category in self.sound_categories:
            for sound_id in self.sound_categories[category]:
                if sound_id in self.current_sounds:
                    self.current_sounds[sound_id]['sound'].set_volume(effective_volume)

    def play_test_sound(self):
        self.play_audio(self.win.character_name, "default", enable_lipsync=True,
                                      stop_audio=True)

    def play_song(self):
        """Playing a song with automatic background music reduction"""
        # Get audio file
        self.win.input_handler.input_lock = True
        song_name = self.current_sing_song

        # Save the current BGM volume
        self.original_bgm_volume = self.get_category_volume("bgm")

        # Turn down the BGM volume
        self.set_category_volume("bgm", 0.1, update_existing=True)

        # Play song
        sound_id = self.play_audio(
            "Songs", song_name,
            category="voice",
            enable_lipsync=True,
            stop_audio=True,
            sound_id=f"song_{song_name}"  # unique Id
        )

        if sound_id:
            # Timer to restore volume
            self.resume_bgm_timer = QTimer()
            self.resume_bgm_timer.setSingleShot(True)
            self.resume_bgm_timer.timeout.connect(self.restore_bgm_volume)
            self.resume_bgm_timer.start(self.song_duration)

            # Save information about the current song
            duration = self.song_duration
            self.current_sing_song_save = {
                'id': sound_id,
                'name': song_name,
                'duration': duration,
                'start_time': QDateTime.currentDateTime()
            }

            return True

        return False

    def restore_bgm_volume(self):
        """Restores the original BGM volume"""
        self.win.input_handler.input_lock = False
        if hasattr(self, 'original_bgm_volume'):
            self.set_category_volume("bgm", self.original_bgm_volume, update_existing=True)
            delattr(self, 'original_bgm_volume')

        if hasattr(self, 'resume_bgm_timer'):
            self.resume_bgm_timer.stop()
            delattr(self, 'resume_bgm_timer')


    def play_bg_music(self):
        """Play BG Music """
        if not self.bgm_name:
            return
        if self.bgm_group:
            audio_source = self.bgm_group
        #else:
        #    audio_source = self.win.character_name

        self.play_audio(audio_source, self.bgm_name, category="bgm", stop_audio=True)


    def play_audio(self, character_name: str, audio_source: str = None,
                   enable_lipsync: bool = False,
                   stop_audio: bool = False,
                   sound_id: str = None,
                   category: str = "voice",
                   volume_override: float = None) -> bool:
        """
        Audio playback with volume support

        Args:
            character_name: Character name or "Effects" for effects
            audio_source: Audio type or file path
            enable_lipsync: Whether to enable lip sync
            stop_audio: Stops playback of the previous audio file
            sound_id: unique audio identifier (optional)
            category: audio category - "voice" (speech), "sfx" (effects),
            volume_override: Volume override (0.0-1.0), None - use system settings
        """
        if not self.audio_switch:
            return False

        if stop_audio:
            # Only stop sounds of a certain category.
            self.stop_category(category) #  exclude_categories=["bgm", "sfx"]

        try:
            import pygame.mixer

            # Define character_name if not specified
            if character_name is None:
                character_name = getattr(self.win, 'character_name', "default")

            # Automatically create a sound_id if not specified
            if sound_id is None:
                sound_id = f"{character_name}_{audio_source}"

            # AUTOMATIC TYPE DETECTION
            if (audio_source.endswith('.wav') or
                    audio_source.startswith('audio/') or
                    os.path.isabs(audio_source)):
                # FILE PATH:
                if not os.path.isabs(audio_source):
                    audio_file = os.path.join(self.resources_dir, audio_source)
                else:
                    audio_file = audio_source
                source_info = f"file: {os.path.basename(audio_file)}"
            else:
                # AUDIO TYPE:
                audio_file = self.win.resource_manager.get_audio(character_name, audio_source)
                source_info = f"type: {audio_source} for {character_name}"

            if not audio_file or not os.path.exists(audio_file):
                if self.win.playing_audio_log:
                    print(f"✗ Audio file not found: {source_info}")
                return False

            # Create Sound object
            sound = pygame.mixer.Sound(audio_file)

            # Get audio duration
            self.song_duration = int(sound.get_length() * 1000)

            # Play based on the category
            if category == "bgm":
                # Background music - play on endless repeat
                channel = sound.play(loops=-1)
                loop_info = " (BGM, looped)"
            else:
                # Normal sound - play it once
                channel = sound.play()
                loop_info = ""

            # Set volume
            if volume_override is not None:
                # Use redefinition
                final_volume = max(0.0, min(1.0, volume_override))
            else:
                # Use the system settings
                final_volume = self.get_effective_volume(category)

            sound.set_volume(final_volume)

            # Play
            channel = sound.play()

            # Save info
            sound_data = {
                'sound': sound,
                'channel': channel,
                'file': audio_file,
                'category': category,
                'volume': final_volume,
                'volume_override': volume_override
            }

            self.current_sounds[sound_id] = sound_data

            # Add it to the grouping by category
            if category not in self.sound_categories:
                self.sound_categories[category] = []
            self.sound_categories[category].append(sound_id)

            # LipSync
            if enable_lipsync and self.wavHandler:
                self.wavHandler.Start(audio_file)

            if self.win.playing_audio_log:
                volume_percent = int(final_volume * 100)
                print(f"🔊 Playing [{category}] at {volume_percent}%: {source_info}")
            return True

        except Exception as e:
            print(f"✗ Audio playback error: {e}")
            return False

    def stop_audio(self, character_name: str = None, audio_source: str = None,
                   sound_id: str = None, category: str = None):
        """Stop the sound according to various criteria"""
        import pygame.mixer

        # Stop by sound_id (highest priority)
        if sound_id:
            if sound_id in self.current_sounds:
                self._stop_sound_by_id(sound_id)
            return

        # Stop by character_name + audio_source
        elif character_name and audio_source:
            sound_key = f"{character_name}_{audio_source}"
            if sound_key in self.current_sounds:
                self._stop_sound_by_id(sound_key)
            return

        # 3. Stop by category
        elif category:
            self.stop_category(category)
            return

        # 4. Stop all (as default)
        else:
            # Stop except music
            self.stop_all_except(["bgm"])

    def stop_category(self, category: str, exclude_categories: list = None):
        """Stop all sounds of a certain category"""
        if exclude_categories is None:
            exclude_categories = []

        if category in self.sound_categories:
            sound_ids_to_remove = []
            for sound_id in self.sound_categories[category]:
                if sound_id in self.current_sounds:
                    # Check except
                    sound_category = self.current_sounds[sound_id]['category']
                    if sound_category not in exclude_categories:
                        self.current_sounds[sound_id]['sound'].stop()
                        sound_ids_to_remove.append(sound_id)

            # Remove stopped sounds from dictionaries
            for sound_id in sound_ids_to_remove:
                del self.current_sounds[sound_id]
                self.sound_categories[category].remove(sound_id)

            if not self.sound_categories[category]:
                del self.sound_categories[category]

    def stop_all_except(self, exclude_categories: list = None):
        """Stop all sounds except for the specified categories"""
        if exclude_categories is None:
            exclude_categories = ["bgm"]  # As defaault not stop

        # Create a list of sounds to stop
        sound_ids_to_stop = []
        for sound_id, sound_data in self.current_sounds.items():
            if sound_data['category'] not in exclude_categories:
                sound_ids_to_stop.append(sound_id)

        # Stop sounds
        for sound_id in sound_ids_to_stop:
            self._stop_sound_by_id(sound_id)

    def _stop_sound_by_id(self, sound_id: str):
        """Internal method for stopping audio by ID"""
        if sound_id in self.current_sounds:
            sound_data = self.current_sounds[sound_id]
            sound_data['sound'].stop()

            # Remove it from the categories
            category = sound_data['category']
            if category in self.sound_categories and sound_id in self.sound_categories[category]:
                self.sound_categories[category].remove(sound_id)
                if not self.sound_categories[category]:
                    del self.sound_categories[category]

            # Remove it from the current sounds
            del self.current_sounds[sound_id]

    # Additional Methods
    def fade_out(self, sound_id: str = None, category: str = None,
                 duration_ms: int = 1000):
        """Smooth volume reduction to 0"""
        import pygame.mixer
        from PySide6.QtCore import QTimer, QElapsedTimer

        def fade_sound(sound_obj, fade_time):
            """Smooth fading of a single sound"""
            start_volume = sound_obj.get_volume()
            timer = QTimer()
            elapsed = QElapsedTimer()
            elapsed.start()

            def update():
                progress = min(1.0, elapsed.elapsed() / fade_time)
                current_volume = start_volume * (1.0 - progress)
                sound_obj.set_volume(current_volume)

                if progress >= 1.0:
                    timer.stop()
                    sound_obj.stop()

            timer.timeout.connect(update)
            timer.start(16)  # ~60 FPS

        if sound_id:
            if sound_id in self.current_sounds:
                fade_sound(self.current_sounds[sound_id]['sound'], duration_ms)
                # Remove stopped sounds from dictionaries
                QTimer.singleShot(duration_ms + 100,
                                  lambda: self._stop_sound_by_id(sound_id))

        elif category:
            if category in self.sound_categories:
                for sound_id in self.sound_categories[category].copy():
                    if sound_id in self.current_sounds:
                        fade_sound(self.current_sounds[sound_id]['sound'], duration_ms)
                # Remove it after completion
                QTimer.singleShot(duration_ms + 100,
                                  lambda: self.stop_category(category))

    def set_sound_volume(self, sound_id: str, volume: float):
        """Set the volume of a specific sound"""
        if sound_id in self.current_sounds:
            sound_data = self.current_sounds[sound_id]
            final_volume = max(0.0, min(1.0, volume))
            sound_data['sound'].set_volume(final_volume)
            sound_data['volume'] = final_volume
            sound_data['volume_override'] = volume  # Mark it as redefined
            return True
        return False

    def get_sound_info(self, sound_id: str) -> dict:
        """Get information about the sound"""
        if sound_id in self.current_sounds:
            data = self.current_sounds[sound_id].copy()
            data['effective_volume'] = data['sound'].get_volume()
            return data
        return {}

    def get_active_sounds_by_category(self) -> dict:
        """Get a list of active sounds by category"""
        result = {}
        for category, sound_ids in self.sound_categories.items():
            result[category] = []
            for sound_id in sound_ids:
                if sound_id in self.current_sounds:
                    info = {
                        'id': sound_id,
                        'volume': self.current_sounds[sound_id]['volume'],
                        'category': category
                    }
                    result[category].append(info)
        return result