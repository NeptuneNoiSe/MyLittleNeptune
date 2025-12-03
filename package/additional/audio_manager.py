import os


class AudioManager:
    def __init__(self, win, resources_dir: str):
        self.win = win
        self.resources_dir = resources_dir
        self._init_pygame_mixer()
        self.current_sounds = {}  # Словарь для отслеживания активных звуков
        self.sound_categories = {}  # Для группировки звуков по категориям

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
                   enable_lipsync: bool = False,
                   stop_audio: bool = False,
                   sound_id: str = None,
                   category: str = "voice") -> bool:
        """
        Умное воспроизведение аудио - понимает оба формата

        Args:
            character_name: имя персонажа или "Effects" для эффектов
            audio_source: тип аудио или путь к файлу
            enable_lipsync: включить ли синхронизацию губ
            stop_audio: останавливает воспроизведение предыдущего аудио файла
            sound_id: уникальный идентификатор звука (опционально)
            category: категория звука - "voice" (речь), "sfx" (эффекты), "bgm" (музыка)
        """
        if stop_audio:
            # Останавливаем только звуки определенной категории
            self.stop_category(category) #  exclude_categories=["bgm", "sfx"]

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

            # Сохраняем информацию о звуке
            sound_data = {
                'sound': sound,
                'channel': channel,
                'file': audio_file,
                'category': category
            }

            self.current_sounds[sound_id] = sound_data

            # Также добавляем в группировку по категориям
            if category not in self.sound_categories:
                self.sound_categories[category] = []
            self.sound_categories[category].append(sound_id)

            # LipSync - только для основного звука персонажа
            if enable_lipsync and self.wavHandler:
                self.wavHandler.Start(audio_file)

            if self.win.playing_audio_log:
                print(f"🔊 Playing [{category}]: {source_info}")
            return True

        except Exception as e:
            print(f"✗ Audio playback error: {e}")
            return False

    def stop_audio(self, character_name: str = None, audio_source: str = None,
                   sound_id: str = None, category: str = None):
        """Остановить звук по различным критериям"""
        import pygame.mixer

        # 1. Остановка по sound_id (высший приоритет)
        if sound_id:
            if sound_id in self.current_sounds:
                self._stop_sound_by_id(sound_id)
            return

        # 2. Остановка по character_name + audio_source
        elif character_name and audio_source:
            sound_key = f"{character_name}_{audio_source}"
            if sound_key in self.current_sounds:
                self._stop_sound_by_id(sound_key)
            return

        # 3. Остановка по категории
        elif category:
            self.stop_category(category)
            return

        # 4. Остановка всего (по умолчанию)
        else:
            # Останавливаем все звуки кроме музыки
            self.stop_all_except(["bgm"])

    def stop_category(self, category: str, exclude_categories: list = None):
        """Остановить все звуки определенной категории"""
        if exclude_categories is None:
            exclude_categories = []

        if category in self.sound_categories:
            sound_ids_to_remove = []
            for sound_id in self.sound_categories[category]:
                if sound_id in self.current_sounds:
                    # Проверяем, не входит ли звук в исключения
                    sound_category = self.current_sounds[sound_id]['category']
                    if sound_category not in exclude_categories:
                        self.current_sounds[sound_id]['sound'].stop()
                        sound_ids_to_remove.append(sound_id)

            # Удаляем остановленные звуки из словарей
            for sound_id in sound_ids_to_remove:
                del self.current_sounds[sound_id]
                self.sound_categories[category].remove(sound_id)

            if not self.sound_categories[category]:
                del self.sound_categories[category]

    def stop_all_except(self, exclude_categories: list = None):
        """Остановить все звуки кроме указанных категорий"""
        if exclude_categories is None:
            exclude_categories = ["bgm"]  # По умолчанию не останавливаем музыку

        # Создаем список звуков для остановки
        sound_ids_to_stop = []
        for sound_id, sound_data in self.current_sounds.items():
            if sound_data['category'] not in exclude_categories:
                sound_ids_to_stop.append(sound_id)

        # Останавливаем звуки
        for sound_id in sound_ids_to_stop:
            self._stop_sound_by_id(sound_id)

    def _stop_sound_by_id(self, sound_id: str):
        """Внутренний метод остановки звука по ID"""
        if sound_id in self.current_sounds:
            sound_data = self.current_sounds[sound_id]
            sound_data['sound'].stop()

            # Удаляем из категорий
            category = sound_data['category']
            if category in self.sound_categories and sound_id in self.sound_categories[category]:
                self.sound_categories[category].remove(sound_id)
                if not self.sound_categories[category]:
                    del self.sound_categories[category]

            # Удаляем из текущих звуков
            del self.current_sounds[sound_id]