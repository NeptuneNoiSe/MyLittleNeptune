import os

class AudioManager:
    def __init__(self, win, resources_dir: str):
        self.win = win
        self.resources_dir = resources_dir
        self.audio_switch = True

        # Система громкости
        # self.master_volume = (self.win.app_config.master/100)  # Общая громкость (0.0 - 1.0)

        self._defaults = {
            'master': 0.8,    # 80%
            'voice': 1.0,     # 100%
            'sfx': 0.9,       # 90%
            'bgm': 0.6,       # 60%
            'ambient': 0.9    # 90%
        }

        self._init_pygame_mixer()
        self.current_sounds = {}  # Словарь для отслеживания активных звуков
        self.sound_categories = {}  # Для группировки звуков по категориям
        self.category_volumes = {}
        self.load_config()

    def load_config(self):
        """Загружает или перезагружает настройки из конфига"""
        # Мастер громкость
        self.master_volume = self._get_config_value('master')

        # Категории
        self.category_volumes = {
            "voice": self._get_config_value('voice'),
            "sfx": self._get_config_value('sfx'),
            "bgm": self._get_config_value('bgm'),
            "ambient": self._get_config_value('ambient')
        }

        # Применяем сразу
        #self.apply_all_volumes()

    def _get_config_value(self, key):
        """Безопасно получает значение из конфига"""
        try:
            value = getattr(self.win.app_config, key, self._defaults[key] * 100)
            # Если значение > 1, значит это проценты, конвертируем
            if value > 1.0:
                return value / 100.0
            return value
        except:
            return self._defaults[key]

    def reload_config(self):
        """Публичный метод для перезагрузки конфига"""
        self.load_config()

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
            pygame.mixer.init(frequency=44100, size=-16, channels=16, buffer=512)  # Увеличил channels

        except ImportError:
            print("✗ Pygame not available")

    # ======================= Volume Control Methods =======================
    def set_master_volume(self, volume: float, update_existing: bool = True):
        """Установить общую громкость (0.0 - 1.0)"""
        self.master_volume = max(0.0, min(1.0, volume))

        if update_existing:
            # Обновляем громкость всех текущих звуков
            self._update_all_volumes()

    def set_category_volume(self, category: str, volume: float, update_existing: bool = True):
        """Установить громкость для категории (0.0 - 1.0)"""
        if category in self.category_volumes:
            self.category_volumes[category] = max(0.0, min(1.0, volume))

            if update_existing:
                # Обновляем громкость всех звуков этой категории
                self._update_category_volumes(category)

    def get_category_volume(self, category: str) -> float:
        """Получить громкость категории"""
        return self.category_volumes.get(category, 1.0)

    def get_effective_volume(self, category: str) -> float:
        """Получить итоговую громкость для категории с учетом master_volume"""
        category_vol = self.category_volumes.get(category, 1.0)
        return self.master_volume * category_vol

    def _update_all_volumes(self):
        """Обновить громкость всех текущих звуков"""
        for sound_id, sound_data in self.current_sounds.items():
            category = sound_data['category']
            effective_volume = self.get_effective_volume(category)
            sound_data['sound'].set_volume(effective_volume)

    def _update_category_volumes(self, category: str):
        """Обновить громкость всех звуков определенной категории"""
        effective_volume = self.get_effective_volume(category)

        if category in self.sound_categories:
            for sound_id in self.sound_categories[category]:
                if sound_id in self.current_sounds:
                    self.current_sounds[sound_id]['sound'].set_volume(effective_volume)

    def play_test_sound(self):
        self.play_audio(self.win.character_name, "default", enable_lipsync=True,
                                      stop_audio=True)


    def play_audio(self, character_name: str, audio_source: str = None,
                   enable_lipsync: bool = False,
                   stop_audio: bool = False,
                   sound_id: str = None,
                   category: str = "voice",
                   volume_override: float = None) -> bool:
        """
        Умное воспроизведение аудио с поддержкой громкости

        Args:
            character_name: имя персонажа или "Effects" для эффектов
            audio_source: тип аудио или путь к файлу
            enable_lipsync: включить ли синхронизацию губ
            stop_audio: останавливает воспроизведение предыдущего аудио файла
            sound_id: уникальный идентификатор звука (опционально)
            category: категория звука - "voice" (речь), "sfx" (эффекты),
            volume_override: Переопределение громкости (0.0-1.0), None - использовать системные настройки
        """
        if not self.audio_switch:
            return False

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

            # Создаем Sound объект
            sound = pygame.mixer.Sound(audio_file)

            # Устанавливаем громкость
            if volume_override is not None:
                # Используем переопределение
                final_volume = max(0.0, min(1.0, volume_override))
            else:
                # Используем системные настройки
                final_volume = self.get_effective_volume(category)

            sound.set_volume(final_volume)

            # Воспроизводим
            channel = sound.play()

            # Сохраняем информацию о звуке
            sound_data = {
                'sound': sound,
                'channel': channel,
                'file': audio_file,
                'category': category,
                'volume': final_volume,
                'volume_override': volume_override
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
                volume_percent = int(final_volume * 100)
                print(f"🔊 Playing [{category}] at {volume_percent}%: {source_info}")
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

    # Additional Methods
    def fade_out(self, sound_id: str = None, category: str = None,
                 duration_ms: int = 1000):
        """Плавное уменьшение громкости до 0"""
        import pygame.mixer
        from PySide6.QtCore import QTimer, QElapsedTimer

        def fade_sound(sound_obj, fade_time):
            """Плавное затухание одного звука"""
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
                # Удаляем из словарей после завершения
                QTimer.singleShot(duration_ms + 100,
                                  lambda: self._stop_sound_by_id(sound_id))

        elif category:
            if category in self.sound_categories:
                for sound_id in self.sound_categories[category].copy():
                    if sound_id in self.current_sounds:
                        fade_sound(self.current_sounds[sound_id]['sound'], duration_ms)
                # Удаляем после завершения
                QTimer.singleShot(duration_ms + 100,
                                  lambda: self.stop_category(category))

    def set_sound_volume(self, sound_id: str, volume: float):
        """Установить громкость конкретного звука"""
        if sound_id in self.current_sounds:
            sound_data = self.current_sounds[sound_id]
            final_volume = max(0.0, min(1.0, volume))
            sound_data['sound'].set_volume(final_volume)
            sound_data['volume'] = final_volume
            sound_data['volume_override'] = volume  # Помечаем как переопределенный
            return True
        return False

    def get_sound_info(self, sound_id: str) -> dict:
        """Получить информацию о звуке"""
        if sound_id in self.current_sounds:
            data = self.current_sounds[sound_id].copy()
            data['effective_volume'] = data['sound'].get_volume()
            return data
        return {}

    def get_active_sounds_by_category(self) -> dict:
        """Получить список активных звуков по категориям"""
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