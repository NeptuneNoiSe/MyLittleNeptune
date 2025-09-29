import os


class AudioManager:
    def __init__(self,win, resources_dir: str):
        self.win = win
        self.resources_dir = resources_dir
        self._init_pygame_mixer()

    @property
    def wavHandler(self):
        """Доступ к wavHandler через главное окно"""
        if self.win and hasattr(self.win, 'wavHandler'):
            return self.win.wavHandler
        return None

    def _init_pygame_mixer(self):
        """Инициализация только звукового модуля pygame"""
        try:
            # Убираем приветственное сообщение
            os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
            import pygame.mixer

            # Инициализируем ТОЛЬКО mixer
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

        except ImportError:
            print("✗ Pygame not available")

    def play_audio(self, character_name: str, audio_source: str = None, enable_lipsync: bool = False,) -> bool:
        """
        Умное воспроизведение аудио - понимает оба формата

        Примеры:
            play_audio("audio/nep_nep.wav")           # Путь к файлу
            play_audio("greeting")                     # Тип аудио для текущего персонажа
            play_audio("sleep", character_name="Noire") # Тип аудио для конкретного персонажа
        """
        try:
            import pygame.mixer

            # Определяем character_name если не указан
            if character_name is None:
                character_name = getattr(self.win, 'character_name', "default")

            # АВТОМАТИЧЕСКОЕ ОПРЕДЕЛЕНИЕ ТИПА
            if (audio_source.endswith('.wav') or
                    audio_source.startswith('audio/') or
                    os.path.isabs(audio_source)):
                # ЭТО ПУТЬ К ФАЙЛУ
                if not os.path.isabs(audio_source):
                    audio_file = os.path.join(self.resources_dir, audio_source)
                else:
                    audio_file = audio_source

                source_info = f"file: {os.path.basename(audio_file)}"

            else:
                # ЭТО ТИП АУДИО
                audio_file = self.win.resource_manager.get_audio(character_name, audio_source)
                source_info = f"type: {audio_source} for {character_name}"

            if not audio_file or not os.path.exists(audio_file):
                print(f"✗ Audio file not found: {source_info}")
                return False

            # Воспроизведение
            pygame.mixer.music.stop()
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()

            # LipSync
            if enable_lipsync and self.wavHandler:
                self.wavHandler.Start(audio_file)

            print(f"🔊 Playing: {source_info}")
            return True

        except Exception as e:
            print(f"✗ Audio playback error: {e}")
            return False