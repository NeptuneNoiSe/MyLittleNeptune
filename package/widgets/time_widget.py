from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QDoubleSpinBox, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QCheckBox, QSpinBox, QComboBox


class SleepSchedule(QWidget):
    """Упрощенная версия расписания сна без сложных зависимостей"""
    schedule_changed = Signal()
    def __init__(self, parent=None):
        super().__init__(parent)

        # Инициализируем атрибуты
        self.sleep_time = None
        self.wake_time = None
        self.global_format_checkbox = None

        # Создаем UI элементы
        self._create_ui()

        # Подключаем сигналы ПОСЛЕ создания всех виджетов
        self._connect_all_signals()

    def set_text(self, sleep_time = "Go to sleep at:", wake_time = "Wake up at:", format = "Use 12-hour format"):
        self.sleep_label.setText(sleep_time)
        self.wake_label.setText(wake_time)
        self.global_format_checkbox.setText(format)

    def set_icon(self, icon_path):
        self.global_format_checkbox.setIcon(icon_path)

    def _create_ui(self):
        """Создает все UI элементы"""
        layout = QVBoxLayout()
        layout.setSpacing(5)

        # Заголовок
        title = QLabel("Sleep Schedule")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(10)
        title.setFont(title_font)
        # layout.addWidget(title)

        # Время отхода ко сну
        self.sleep_layout = QHBoxLayout()
        self.sleep_label = QLabel("Go to sleep at:")
        self.sleep_layout.addWidget(self.sleep_label)

        self.sleep_time = TimeSelector24H(
            label="",
            default_hour=21,
            default_minute=0
        )
        self.sleep_layout.addWidget(self.sleep_time)
        self.sleep_layout.addStretch()

        # Время пробуждения
        self.wake_layout = QHBoxLayout()
        self.wake_label = QLabel("Wake up at:")
        self.wake_layout.addWidget(self.wake_label)

        self.wake_time = TimeSelector24H(
            label="",
            default_hour=8,
            default_minute=0
        )
        self.wake_layout.addWidget(self.wake_time)
        self.wake_layout.addStretch()

        # Глобальный переключатель формата
        self.format_layout = QHBoxLayout()
        self.global_format_checkbox = QCheckBox("Use 12-hour format")
        self.global_format_checkbox.setChecked(False)

        # Применяем начальное состояние к селекторам
        self.sleep_time.format_checkbox.setChecked(False)
        self.wake_time.format_checkbox.setChecked(False)

        self.global_format_checkbox.toggled.connect(self._on_global_format_toggled)
        self.format_layout.addWidget(self.global_format_checkbox)
        self.format_layout.addStretch()

        # Сборка
        layout.addLayout(self.sleep_layout)
        layout.addLayout(self.wake_layout)
        layout.addLayout(self.format_layout)

        self.setLayout(layout)

    def _connect_all_signals(self):
        """Подключает все возможные изменения к единому сигналу"""
        if not self.sleep_time or not self.wake_time:
            return

        # Все элементы управления временем сна
        self.sleep_time.hour_spin.valueChanged.connect(self._emit_schedule_changed)
        self.sleep_time.minute_spin.valueChanged.connect(self._emit_schedule_changed)
        self.sleep_time.ampm_combo.currentTextChanged.connect(self._emit_schedule_changed)
        self.sleep_time.format_checkbox.toggled.connect(self._emit_schedule_changed)

        # Все элементы управления временем пробуждения
        self.wake_time.hour_spin.valueChanged.connect(self._emit_schedule_changed)
        self.wake_time.minute_spin.valueChanged.connect(self._emit_schedule_changed)
        self.wake_time.ampm_combo.currentTextChanged.connect(self._emit_schedule_changed)
        self.wake_time.format_checkbox.toggled.connect(self._emit_schedule_changed)

        # Глобальный формат времени
        if self.global_format_checkbox:
            self.global_format_checkbox.toggled.connect(self._emit_schedule_changed)

    def _emit_schedule_changed(self, *args):
        """Испускает сигнал об изменении"""
        self.schedule_changed.emit()

    def _on_global_format_toggled(self, checked):
        """Применяет глобальную настройку формата ко всем селекторам"""
        self.sleep_time.format_checkbox.setChecked(checked)
        self.wake_time.format_checkbox.setChecked(checked)
        self._emit_schedule_changed()

    def _apply_preset(self, sleep_hour, sleep_minute, wake_hour, wake_minute):
        """Применяет пресет"""
        self.sleep_time.set_time(sleep_hour, sleep_minute)
        self.wake_time.set_time(wake_hour, wake_minute)

    def get_sleep_time(self) -> tuple:
        """Возвращает время отхода ко сну"""
        return self.sleep_time.get_time()

    def get_wake_time(self) -> tuple:
        """Возвращает время пробуждения"""
        return self.wake_time.get_time()

    def set_sleep_time(self, hour: int, minute: int):
        """Устанавливает время сна"""
        self.sleep_time.set_time(hour, minute)

    def set_wake_time(self, hour: int, minute: int):
        """Устанавливает время пробуждения"""
        self.wake_time.set_time(hour, minute)

    def set_all_settings(self, sleep_hour: int, sleep_minute: int,
                         wake_hour: int, wake_minute: int,
                         use_12h_format: bool):
        """Устанавливает все настройки расписания"""
        # Временно блокируем сигналы для массового обновления
        self.sleep_time.hour_spin.blockSignals(True)
        self.sleep_time.minute_spin.blockSignals(True)
        self.wake_time.hour_spin.blockSignals(True)
        self.wake_time.minute_spin.blockSignals(True)
        self.global_format_checkbox.blockSignals(True)

        try:
            self.set_sleep_time(sleep_hour, sleep_minute)
            self.set_wake_time(wake_hour, wake_minute)
            self.set_12h_format(use_12h_format)
        finally:
            # Восстанавливаем сигналы
            self.sleep_time.hour_spin.blockSignals(False)
            self.sleep_time.minute_spin.blockSignals(False)
            self.wake_time.hour_spin.blockSignals(False)
            self.wake_time.minute_spin.blockSignals(False)
            self.global_format_checkbox.blockSignals(False)

    def set_12h_format(self, enabled: bool):
        """Включает/выключает 12-часовой формат"""
        self.global_format_checkbox.setChecked(enabled)

    def use_12h_format(self) -> bool:
        """Используется ли 12-часовой формат"""
        return self.global_format_checkbox.isChecked()

class TimeSelector24H(QWidget):
    """Селектор времени с динамическим переключением 12/24-часового формата"""

    def __init__(self, label="Time:", default_hour=21, default_minute=0, parent=None):
        super().__init__(parent)

        self._use_12h_format = False
        self._current_hour_24h = default_hour  # Храним в 24-часовом формате
        self._current_minute = default_minute

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Метка
        layout.addWidget(QLabel(label))

        # SpinBox для часа (изначально 24-часовой)
        self.hour_spin = QSpinBox()
        self.hour_spin.setRange(0, 23)  # 24-часовой формат
        self.hour_spin.setValue(default_hour)
        self.hour_spin.setFixedWidth(60)
        self.hour_spin.valueChanged.connect(self._on_hour_changed)

        # Двоеточие
        # layout.addWidget(QLabel(" : "))

        # SpinBox для минут
        self.minute_spin = QSpinBox()
        self.minute_spin.setRange(0, 59)
        self.minute_spin.setValue(default_minute)
        self.minute_spin.setFixedWidth(60)
        self.minute_spin.setSingleStep(5)  # Шаг 5 минут
        self.minute_spin.valueChanged.connect(self._on_minute_changed)

        # Чекбокс для переключения формата
        self.format_checkbox = QCheckBox("12h")
        self.format_checkbox.setToolTip("Switch to 12-hour format (AM/PM)")
        self.format_checkbox.setFixedWidth(50)
        self.format_checkbox.toggled.connect(self._on_format_toggled)

        # ComboBox для AM/PM (скрыт в 24-часовом режиме)
        self.ampm_combo = QComboBox()
        self.ampm_combo.addItems(["AM", "PM"])
        self.ampm_combo.setFixedWidth(60)
        self.ampm_combo.hide()  # Скрыт по умолчанию
        self.ampm_combo.currentTextChanged.connect(self._on_ampm_changed)

        layout.addWidget(self.hour_spin)
        layout.addWidget(self.minute_spin)
        # layout.addWidget(self.format_checkbox)
        layout.addWidget(self.ampm_combo)
        layout.addStretch()

        self.setLayout(layout)

        # Инициализируем AM/PM в зависимости от начального времени
        self._update_ampm_from_24h()

    def _on_format_toggled(self, checked):
        """Переключает между 12 и 24-часовым форматом"""
        self._use_12h_format = checked

        if checked:
            # Переходим в 12-часовой формат
            self._switch_to_12h_format()
        else:
            # Возвращаемся к 24-часовому формату
            self._switch_to_24h_format()

    def _switch_to_12h_format(self):
        """Переключает на 12-часовой формат"""
        # Скрываем AM/PM комбобокс
        self.ampm_combo.hide()

        # Получаем текущее время в 24-часовом формате
        hour_24h = self._current_hour_24h

        # Конвертируем в 12-часовой формат
        if hour_24h == 0:
            hour_12h = 12
            ampm = "AM"
        elif hour_24h == 12:
            hour_12h = 12
            ampm = "PM"
        elif hour_24h > 12:
            hour_12h = hour_24h - 12
            ampm = "PM"
        else:
            hour_12h = hour_24h
            ampm = "AM"

        # Устанавливаем диапазон 1-12
        self.hour_spin.setRange(1, 12)
        self.hour_spin.setValue(hour_12h)

        # Устанавливаем AM/PM
        self.ampm_combo.setCurrentText(ampm)
        self.ampm_combo.show()

    def _switch_to_24h_format(self):
        """Переключает на 24-часовой формат"""
        # Скрываем AM/PM комбобокс
        self.ampm_combo.hide()

        # Получаем текущее время в 12-часовом формате
        hour_12h = self.hour_spin.value()
        ampm = self.ampm_combo.currentText()

        # Конвертируем в 24-часовой формат
        if hour_12h == 12:
            hour_24h = 0 if ampm == "AM" else 12
        else:
            hour_24h = hour_12h + 12 if ampm == "PM" else hour_12h

        # Устанавливаем диапазон 0-23
        self.hour_spin.setRange(0, 23)
        self.hour_spin.setValue(hour_24h)

    def _on_hour_changed(self, hour):
        """Обработчик изменения часа"""
        if self._use_12h_format:
            # В 12-часовом формате обновляем 24-часовое значение
            ampm = self.ampm_combo.currentText()
            if hour == 12:
                self._current_hour_24h = 0 if ampm == "AM" else 12
            else:
                self._current_hour_24h = hour + 12 if ampm == "PM" else hour
        else:
            # В 24-часовом формате просто сохраняем
            self._current_hour_24h = hour

    def _on_minute_changed(self, minute):
        """Обработчик изменения минут"""
        self._current_minute = minute

    def _on_ampm_changed(self, ampm):
        """Обработчик изменения AM/PM"""
        if not self._use_12h_format:
            return

        # Пересчитываем 24-часовое значение
        hour_12h = self.hour_spin.value()

        if hour_12h == 12:
            self._current_hour_24h = 0 if ampm == "AM" else 12
        else:
            self._current_hour_24h = hour_12h + 12 if ampm == "PM" else hour_12h

    def _update_ampm_from_24h(self):
        """Обновляет AM/PM на основе 24-часового времени"""
        hour_24h = self._current_hour_24h

        if hour_24h < 12:
            self.ampm_combo.setCurrentText("AM")
        else:
            self.ampm_combo.setCurrentText("PM")

    def get_time(self) -> tuple:
        """Возвращает (час, минута) в 24-часовом формате"""
        return self._current_hour_24h, self._current_minute

    def set_time(self, hour_24h: int, minute: int):
        """Устанавливает время из 24-часового формата"""
        # Сохраняем в 24-часовом формате
        self._current_hour_24h = hour_24h
        self._current_minute = minute

        # Обновляем виджеты в зависимости от текущего формата
        if self._use_12h_format:
            # Конвертируем в 12-часовой для отображения
            if hour_24h == 0:
                hour_12h = 12
                ampm = "AM"
            elif hour_24h == 12:
                hour_12h = 12
                ampm = "PM"
            elif hour_24h > 12:
                hour_12h = hour_24h - 12
                ampm = "PM"
            else:
                hour_12h = hour_24h
                ampm = "AM"

            self.hour_spin.setValue(hour_12h)
            self.ampm_combo.setCurrentText(ampm)
        else:
            # Просто устанавливаем 24-часовой формат
            self.hour_spin.setValue(hour_24h)

        self.minute_spin.setValue(minute)

    def set_12h_format(self, enabled: bool):
        """Включает/выключает 12-часовой формат"""
        self.format_checkbox.setChecked(enabled)

class PowerOfTwoSpinBox(QDoubleSpinBox):
    """SpinBox для степеней двойки без лишних нулей"""

    POWERS = [0.1, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(0.1, 32.0)
        self.setDecimals(3)  # Для точного отображения 0.25 и 0.5

    def stepBy(self, steps):
        """Переопределяем стандартное поведение шага"""
        current = self.value()
        current_idx = self._find_power_index(current)

        new_idx = current_idx + steps
        new_idx = max(0, min(len(self.POWERS) - 1, new_idx))

        self.setValue(self.POWERS[new_idx])

    def _find_power_index(self, value):
        """Находит индекс в массиве степеней"""
        for i, power in enumerate(self.POWERS):
            if abs(power - value) < 0.001:
                return i

        # Fallback: находим ближайшую
        closest_idx = 0
        min_diff = abs(value - self.POWERS[0])

        for i, power in enumerate(self.POWERS[1:], 1):
            diff = abs(value - power)
            if diff < min_diff:
                min_diff = diff
                closest_idx = i

        return closest_idx

    def textFromValue(self, value):
        """Форматируем значение без лишних нулей"""
        # Убираем .0 и .00 для целых чисел
        if value.is_integer():
            return f"{int(value):d}X"
        else:
            # Для дробных показываем максимум 2 знака
            formatted = f"{value:.2f}".rstrip('0').rstrip('.')
            return f"{formatted}X"