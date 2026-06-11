from PySide6.QtCore import Signal, QLocale, QDate
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QDoubleSpinBox, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QCheckBox, QSpinBox, \
    QComboBox, QDateEdit, QGroupBox, QGridLayout

from datetime import datetime, date, timedelta


class SleepSchedule(QWidget):
    """Sleep Shedule"""
    schedule_changed = Signal()
    def __init__(self, parent=None):
        super().__init__(parent)

        self.sleep_time = None
        self.wake_time = None
        self.global_format_checkbox = None

        self._create_ui()
        self._connect_all_signals()

    def set_text(self, sleep_time = "Go to sleep at:", wake_time = "Wake up at:", format = "Use 12-hour format"):
        self.sleep_label.setText(sleep_time)
        self.wake_label.setText(wake_time)
        self.global_format_checkbox.setText(format)

    def set_icon(self, icon_path):
        self.global_format_checkbox.setIcon(icon_path)

    def _create_ui(self):
        """Create UI elements"""
        layout = QVBoxLayout()
        layout.setSpacing(5)

        title = QLabel("Sleep Schedule")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(10)
        title.setFont(title_font)
        # layout.addWidget(title)

        # time go to sleep
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

        # time to wake
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

        # Global time format switch
        self.format_layout = QHBoxLayout()
        self.global_format_checkbox = QCheckBox("Use 12-hour format")
        self.global_format_checkbox.setChecked(False)

        # Apply
        self.sleep_time.format_checkbox.setChecked(False)
        self.wake_time.format_checkbox.setChecked(False)

        self.global_format_checkbox.toggled.connect(self._on_global_format_toggled)
        self.format_layout.addWidget(self.global_format_checkbox)
        self.format_layout.addStretch()

        layout.addLayout(self.sleep_layout)
        layout.addLayout(self.wake_layout)
        layout.addLayout(self.format_layout)

        self.setLayout(layout)

    def _connect_all_signals(self):
        if not self.sleep_time or not self.wake_time:
            return

        self.sleep_time.hour_spin.valueChanged.connect(self._emit_schedule_changed)
        self.sleep_time.minute_spin.valueChanged.connect(self._emit_schedule_changed)
        self.sleep_time.ampm_combo.currentTextChanged.connect(self._emit_schedule_changed)
        self.sleep_time.format_checkbox.toggled.connect(self._emit_schedule_changed)

        self.wake_time.hour_spin.valueChanged.connect(self._emit_schedule_changed)
        self.wake_time.minute_spin.valueChanged.connect(self._emit_schedule_changed)
        self.wake_time.ampm_combo.currentTextChanged.connect(self._emit_schedule_changed)
        self.wake_time.format_checkbox.toggled.connect(self._emit_schedule_changed)

        # Global format
        if self.global_format_checkbox:
            self.global_format_checkbox.toggled.connect(self._emit_schedule_changed)

    def _emit_schedule_changed(self, *args):
        self.schedule_changed.emit()

    def _on_global_format_toggled(self, checked):
        self.sleep_time.format_checkbox.setChecked(checked)
        self.wake_time.format_checkbox.setChecked(checked)
        self._emit_schedule_changed()

    def _apply_preset(self, sleep_hour, sleep_minute, wake_hour, wake_minute):
        self.sleep_time.set_time(sleep_hour, sleep_minute)
        self.wake_time.set_time(wake_hour, wake_minute)

    def get_sleep_time(self) -> tuple:
        return self.sleep_time.get_time()

    def get_wake_time(self) -> tuple:
        return self.wake_time.get_time()

    def set_sleep_time(self, hour: int, minute: int):
        self.sleep_time.set_time(hour, minute)

    def set_wake_time(self, hour: int, minute: int):
        self.wake_time.set_time(hour, minute)

    def set_all_settings(self, sleep_hour: int, sleep_minute: int,
                         wake_hour: int, wake_minute: int,
                         use_12h_format: bool):
        """Set shedule settings"""
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
            self.sleep_time.hour_spin.blockSignals(False)
            self.sleep_time.minute_spin.blockSignals(False)
            self.wake_time.hour_spin.blockSignals(False)
            self.wake_time.minute_spin.blockSignals(False)
            self.global_format_checkbox.blockSignals(False)

    def set_12h_format(self, enabled: bool):
        """Enables/disables the 12-hour format"""
        self.global_format_checkbox.setChecked(enabled)

    def use_12h_format(self) -> bool:
        """Use the 12-hour format"""
        return self.global_format_checkbox.isChecked()

class TimeSelector24H(QWidget):
    """Time selector with dynamic 12/24-hour format switching"""

    def __init__(self, label="Time:", default_hour=21, default_minute=0, parent=None):
        super().__init__(parent)

        self._use_12h_format = False
        self._current_hour_24h = default_hour  # Храним в 24-часовом формате
        self._current_minute = default_minute

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(QLabel(label))

        # SpinBox for hour (default 24h-format)
        self.hour_spin = QSpinBox()
        self.hour_spin.setRange(0, 23)  # 24h-format
        self.hour_spin.setValue(default_hour)
        self.hour_spin.setFixedWidth(60)
        self.hour_spin.valueChanged.connect(self._on_hour_changed)

        # layout.addWidget(QLabel(" : "))

        # SpinBox for minut
        self.minute_spin = QSpinBox()
        self.minute_spin.setRange(0, 59)
        self.minute_spin.setValue(default_minute)
        self.minute_spin.setFixedWidth(60)
        self.minute_spin.setSingleStep(5)
        self.minute_spin.valueChanged.connect(self._on_minute_changed)

        # Set time format Checkbox
        self.format_checkbox = QCheckBox("12h")
        self.format_checkbox.setToolTip("Switch to 12-hour format (AM/PM)")
        self.format_checkbox.setFixedWidth(50)
        self.format_checkbox.toggled.connect(self._on_format_toggled)

        # ComboBox for AM/PM (hide in 24H)
        self.ampm_combo = QComboBox()
        self.ampm_combo.addItems(["AM", "PM"])
        self.ampm_combo.setFixedWidth(60)
        self.ampm_combo.hide()
        self.ampm_combo.currentTextChanged.connect(self._on_ampm_changed)

        layout.addWidget(self.hour_spin)
        layout.addWidget(self.minute_spin)
        # layout.addWidget(self.format_checkbox)
        layout.addWidget(self.ampm_combo)
        layout.addStretch()

        self.setLayout(layout)

        # Initializing AM/PM based on the initial time
        self._update_ampm_from_24h()

    def _on_format_toggled(self, checked):
        """Переключает между 12 и 24-часовым форматом"""
        self._use_12h_format = checked

        if checked:
            # Go to 12H
            self._switch_to_12h_format()
        else:
            # return to 24H
            self._switch_to_24h_format()

    def _switch_to_12h_format(self):
        """Switch to 12-hour format"""
        # Hide AM/PM
        self.ampm_combo.hide()

        # Get time in 24H
        hour_24h = self._current_hour_24h

        # convert to 12H
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

        # Set hour range 1-12
        self.hour_spin.setRange(1, 12)
        self.hour_spin.setValue(hour_12h)

        # Set AM/PM
        self.ampm_combo.setCurrentText(ampm)
        self.ampm_combo.show()

    def _switch_to_24h_format(self):
        """Switch to 24-hour format"""
        # hide AM/PM combobox
        self.ampm_combo.hide()

        # Get time in 12h format
        hour_12h = self.hour_spin.value()
        ampm = self.ampm_combo.currentText()

        # Convert 24H format
        if hour_12h == 12:
            hour_24h = 0 if ampm == "AM" else 12
        else:
            hour_24h = hour_12h + 12 if ampm == "PM" else hour_12h

        # Set hour range 0-23
        self.hour_spin.setRange(0, 23)
        self.hour_spin.setValue(hour_24h)

    def _on_hour_changed(self, hour):
        """Hour change handler"""
        if self._use_12h_format:
            # In 12H format updates 24H var
            ampm = self.ampm_combo.currentText()
            if hour == 12:
                self._current_hour_24h = 0 if ampm == "AM" else 12
            else:
                self._current_hour_24h = hour + 12 if ampm == "PM" else hour
        else:
            # Save in 24H format
            self._current_hour_24h = hour

    def _on_minute_changed(self, minute):
        """Minute change handler"""
        self._current_minute = minute

    def _on_ampm_changed(self, ampm):
        """Handler AM/PM changed"""
        if not self._use_12h_format:
            return

        hour_12h = self.hour_spin.value()

        if hour_12h == 12:
            self._current_hour_24h = 0 if ampm == "AM" else 12
        else:
            self._current_hour_24h = hour_12h + 12 if ampm == "PM" else hour_12h

    def _update_ampm_from_24h(self):
        """Updates AM/PM based on 24-hour time"""
        hour_24h = self._current_hour_24h

        if hour_24h < 12:
            self.ampm_combo.setCurrentText("AM")
        else:
            self.ampm_combo.setCurrentText("PM")

    def get_time(self) -> tuple:
        """Returns (hour, minute) in 24-hour format"""
        return self._current_hour_24h, self._current_minute

    def set_time(self, hour_24h: int, minute: int):
        """Set time from 24H format"""
        self._current_hour_24h = hour_24h
        self._current_minute = minute

        # Updates widgets
        if self._use_12h_format:
            # Convert to 12H format for display
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
            self.hour_spin.setValue(hour_24h)

        self.minute_spin.setValue(minute)

    def set_12h_format(self, enabled: bool):
        """Set 12H format"""
        self.format_checkbox.setChecked(enabled)

class PowerOfTwoSpinBox(QDoubleSpinBox):
    """SpinBox for powers of two without extra zeros"""

    POWERS = [0.1, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(0.1, 32.0)
        self.setDecimals(3)  # For accurate display 0.25 и 0.5

    def stepBy(self, steps):
        """Redefining the standard step behavior"""
        current = self.value()
        current_idx = self._find_power_index(current)

        new_idx = current_idx + steps
        new_idx = max(0, min(len(self.POWERS) - 1, new_idx))

        self.setValue(self.POWERS[new_idx])

    def _find_power_index(self, value):
        """Finds the index in the array of degrees"""
        for i, power in enumerate(self.POWERS):
            if abs(power - value) < 0.001:
                return i

        # Fallback: find closer
        closest_idx = 0
        min_diff = abs(value - self.POWERS[0])

        for i, power in enumerate(self.POWERS[1:], 1):
            diff = abs(value - power)
            if diff < min_diff:
                min_diff = diff
                closest_idx = i

        return closest_idx

    def textFromValue(self, value):
        """For,at without zeros"""
        # clear .0 и .00
        if value.is_integer():
            return f"{int(value):d}X"
        else:
            formatted = f"{value:.2f}".rstrip('0').rstrip('.')
            return f"{formatted}X"

class BirthdayDateEdit(QWidget):
    """Custom widget for birthday date selection with language support"""

    # Custom signal emitted when date changes
    dateChanged = Signal(QDate)
    # Custom signal emitted when calendar language changes
    languageChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialize default values
        self.current_language = 'system'
        #self.birthday_date = QDate(now.year, now.month, now.day)
        self.birthday_date = QDate(2000, 11, 1)

        # Setup UI
        self.setup_ui()

        # Apply initial settings
        self.update_calendar_locale()

    def setDateFromComponents(self, year: int, month: int, day: int):
        """Set birthday date from year, month, day components"""
        now = datetime.now()
        if year and month and day:
            date = QDate(year, month, day)
            if date.isValid():
                self.setDate(date)
            else:
                print(f"Invalid date components: {year}-{month}-{day}")
                self.setDate(QDate.currentDate())
        else:
            #print("Missing date components")
            self.setDate(QDate.currentDate())

    def getDateComponents(self):
        """Get birthday date as tuple (year, month, day)"""
        return (
            self.birthday_date.year(),
            self.birthday_date.month(),
            self.birthday_date.day()
        )

    def setup_ui(self):
        """Setup the widget UI"""
        # Main layout
        main_layout = QGridLayout(self)
        #main_layout.setContentsMargins(0, 0, 0, 0)

        # Date selection row
        date_row = QHBoxLayout()
        self.date_label = QLabel("Date of Birth: ")

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("dd.MM.yyyy")
        self.date_edit.setMinimumDate(QDate(1900, 1, 1))
        self.date_edit.setMaximumDate(QDate.currentDate())
        self.date_edit.setDate(self.birthday_date)

        # Connect date change signal
        self.date_edit.dateChanged.connect(self.on_date_changed)

        date_row.addWidget(self.date_label)
        date_row.addWidget(self.date_edit)
        date_row.addStretch()

        # Language selection row
        language_row = QHBoxLayout()
        language_label = QLabel("Calendar Language:")

        self.language_combo = QComboBox()
        self.language_combo.addItem("System Default", "system")
        self.language_combo.addItem("English", "english")
        self.language_combo.addItem("Русский", "russian")

        # Add more languages as needed
        # self.language_combo.addItem("Deutsch", "de")
        # self.language_combo.addItem("Français", "fr")
        # self.language_combo.addItem("Español", "es")

        # Connect language change signal
        self.language_combo.currentIndexChanged.connect(self.on_language_changed)

        language_row.addWidget(language_label)
        language_row.addWidget(self.language_combo)
        language_row.addStretch()

        # Age display row (optional)
        age_row = QHBoxLayout()
        self.age_label = QLabel("Age:")
        self.age_value = QLabel()
        self.age_value.setStyleSheet("font-weight: bold;")

        age_row.addWidget(self.age_label)
        age_row.addWidget(self.age_value)
        age_row.addStretch()

        # Add all rows to main layout
        main_layout.addLayout(date_row, 0, 0)
        #main_layout.addLayout(language_row)
        main_layout.addLayout(age_row, 0, 1)

        # Update age display
        self.update_age_display()

    def on_date_changed(self, date: QDate):
        """Handle date change"""
        self.birthday_date = date
        self.update_age_display()
        self.dateChanged.emit(date)

    def on_language_changed(self, index: int):
        """Handle language change"""
        self.current_language = self.language_combo.currentData()
        self.update_calendar_locale()
        self.languageChanged.emit(self.current_language)

    def update_calendar_locale(self):
        """Update calendar locale based on selected language"""
        if self.current_language == 'english':
            locale = QLocale(QLocale.English, QLocale.UnitedStates)
            self.date_edit.setDisplayFormat("MM/dd/yyyy")
        elif self.current_language == 'russian':
            locale = QLocale(QLocale.Russian, QLocale.Russia)
            self.date_edit.setDisplayFormat("dd.MM.yyyy")
        else:  # system default
            locale = QLocale()
            # Keep existing format or use system format
            # self.date_edit.setDisplayFormat(locale.dateFormat(QLocale.ShortFormat))

        self.date_edit.setLocale(locale)

    def update_age_display(self):
        """Update age display based on selected date"""
        today = QDate.currentDate()
        age = self.birthday_date.daysTo(today) // 365

        # Color coding based on age
        if age < 18:
            self.age_value.setStyleSheet("color: orange; font-weight: bold;")
            self.age_value.setText(f"{age}") # (f"{age} years old (minor)")
        elif age >= 100:
            self.age_value.setStyleSheet("color: gold; font-weight: bold;")
            self.age_value.setText(f"{age}") # (f"{age} years old (centenarian!)")
        else:
            self.age_value.setStyleSheet("font-weight: bold;")
            self.age_value.setText(f"{age}") # (f"{age} years old")

    # Public methods
    def setDate(self, date: QDate):
        """Set the birthday date programmatically"""
        if date.isValid() and date <= QDate.currentDate():
            self.birthday_date = date
            self.date_edit.setDate(date)
            self.update_age_display()

    def getDate(self) -> QDate:
        """Get the current birthday date"""
        return self.birthday_date

    def setText(self,date_text: str, age_text: str):
        self.date_label.setText(date_text)
        self.age_label.setText(age_text)

    def setLanguage(self, language_code: str):
        """Set calendar language programmatically"""
        index = self.language_combo.findData(language_code)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
            self.current_language = language_code
            self.update_calendar_locale()

    def getLanguage(self) -> str:
        """Get current calendar language"""
        return self.current_language

    def setMinimumDate(self, date: QDate):
        """Set minimum selectable date"""
        self.date_edit.setMinimumDate(date)

    def setMaximumDate(self, date: QDate):
        """Set maximum selectable date"""
        self.date_edit.setMaximumDate(date)

    def setDisplayFormat(self, format_string: str):
        """Set date display format"""
        self.date_edit.setDisplayFormat(format_string)

    def getDateEdit(self) -> QDateEdit:
        """Get internal QDateEdit widget if direct access needed"""
        return self.date_edit

class BirthdayGroupBox(QGroupBox):
    """Group box version of birthday widget with title"""

    def __init__(self, title="Personal Information", parent=None):
        super().__init__(title, parent)

        self.birthday_widget = BirthdayDateEdit(self)

        layout = QVBoxLayout()
        layout.addWidget(self.birthday_widget)
        self.setLayout(layout)

    # Delegate methods to birthday_widget
    def setDate(self, date: QDate):
        self.birthday_widget.setDate(date)

    def getDate(self) -> QDate:
        return self.birthday_widget.getDate()

    def setLanguage(self, language_code: str):
        self.birthday_widget.setLanguage(language_code)

    def getLanguage(self) -> str:
        return self.birthday_widget.getLanguage()

    def dateChanged(self):
        return self.birthday_widget.dateChanged

    def languageChanged(self):
        return self.birthday_widget.languageChanged