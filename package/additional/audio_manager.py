import os


class AudioManager:
    def __init__(self, win, resources_dir: str):
        self.win = win
        self.resources_dir = resources_dir
        self._init_pygame_mixer()
        self.current_sounds = {}  # Словарь для отслеживания активных звуков

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

            # Инициализируем ТОЛЬКО mixer с большим количеством каналов
            pygame.mixer.init(frequency=44100, size=-16, channels=8, buffer=512)  # Увеличиваем channels

        except ImportError:
            print("✗ Pygame not available")

    def play_audio(self, character_name: str, audio_source: str = None,
                   enable_lipsync: bool = False, sound_id: str = None) -> bool:
        """
        Умное воспроизведение аудио - понимает оба формата

        Args:
            character_name: имя персонажа или "Effects" для эффектов
            audio_source: тип аудио или путь к файлу
            enable_lipsync: включить ли синхронизацию губ
            sound_id: уникальный идентификатор звука (опционально)
        """
        try:
            import pygame.mixer

            # Определяем character_name если не указан
            if character_name is None:
                character_name = getattr(self.win, 'character_name', "default")

            # Автоматически создаем sound_id если не указан
            if sound_id is None:
                sound_id = f"{character_name}_{audio_source}"

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
                if self.win.playing_audio_log:
                    print(f"✗ Audio file not found: {source_info}")
                return False

            # Создаем Sound объект и воспроизводим его
            sound = pygame.mixer.Sound(audio_file)
            channel = sound.play()

            # Сохраняем информацию о звуке если нужен sound_id
            if sound_id:
                self.current_sounds[sound_id] = {
                    'sound': sound,
                    'channel': channel,
                    'file': audio_file
                }

            # LipSync - только для основного звука персонажа
            if enable_lipsync and self.wavHandler:
                self.wavHandler.Start(audio_file)

            if self.win.playing_audio_log:
                print(f"🔊 Playing: {source_info}")
            return True

        except Exception as e:
            print(f"✗ Audio playback error: {e}")
            return False

    def stop_audio(self, character_name: str = None, audio_source: str = None, sound_id: str = None):
        """Остановить звук по sound_id или по character_name + audio_source"""
        import pygame.mixer

        if sound_id:
            # Останавливаем по sound_id
            if sound_id in self.current_sounds:
                self.current_sounds[sound_id]['sound'].stop()
                del self.current_sounds[sound_id]
        elif character_name and audio_source:
            # Останавливаем по character_name + audio_source
            sound_key = f"{character_name}_{audio_source}"
            if sound_key in self.current_sounds:
                self.current_sounds[sound_key]['sound'].stop()
                del self.current_sounds[sound_key]
        else:
            # Останавливаем все звуки
            pygame.mixer.stop()
            self.current_sounds.clear()