from datetime import datetime, date, timedelta
from typing import Dict, Optional

from PySide6.QtGui import QFont, QPainter, QColor, QFontMetrics
from PySide6.QtCore import QTimer


class EventManager:
    def __init__(self, win):
        self.win = win
        self.event_instance = None
        self.event_log = False
        self.event_time_manager = EventTimeManager(self)

        # 1. Получаем текущее событие
        self.current_event = self.event_time_manager.get_current_event()

        # 2. Запускаем проверку
        self.check_events()  # Этот метод теперь создает event_instance

    def check_events(self):
        """Проверяет и создает событие"""
        if self.current_event:
            class_name = self.current_event.replace(" ", "") + "Event"

            try:
                event_class = globals()[class_name]
                self.event_instance = event_class(self)  # ← сразу создаем экземпляр
            except KeyError:
                print(f"Класс {class_name} не найден")
                self.event_instance = None
        else:
            self.event_instance = None


    def draw_event_text(self, painter):
        if self.event_instance:
            self.event_instance.draw_text(painter)

    def draw_event_text(self, painter):
        if self.current_event is None:
            return
        self.event_instance.draw_new_year_text(painter)

    def draw_text_on_model(self):
        if self.current_event is None:
            return
        self.event_instance.draw_on_model()

class EventTimeManager:
    def __init__(self, event_manager):
        self.event_manager = event_manager

        self._event_schedule = self._load_schedule()

    def _load_schedule(self) -> Dict:
        """Загружает расписание событий"""
        return {
            "New Year": {
                "start": {"month": 12, "day": 17},
                "end": {"month": 1, "day": 10}
            }
            # Можно добавить другие события:
            # "Halloween": {"start": {"month": 10, "day": 28}, "end": {"month": 11, "day": 2}},
            # "Birthday": {"start": {"month": 1, "day": 15}, "end": {"month": 1, "day": 15}},
        }

    def get_current_event(self) -> Optional[str]:
        """Определяет текущее активное событие"""
        today = date.today()

        for event_name, schedule in self._event_schedule.items():
            start = schedule["start"]
            end = schedule["end"]

            # Проверяем, попадает ли сегодня в период события
            if self._is_date_in_period(today, start, end):
                return event_name

        return None

    def _is_date_in_period(self, check_date: date, start: dict, end: dict) -> bool:
        """Проверяет, находится ли дата в периоде события"""
        # Если событие переходит через год (например, декабрь-январь)
        if start["month"] > end["month"]:
            # Период: декабрь -> январь
            if check_date.month == 12 and check_date.day >= start["day"]:
                return True
            elif check_date.month == 1 and check_date.day <= end["day"]:
                return True
        else:
            # Период в пределах одного года
            start_date = date(check_date.year, start["month"], start["day"])
            end_date = date(check_date.year, end["month"], end["day"])
            return start_date <= check_date <= end_date

        return False

class NewYearEvent:
    def __init__(self, event_manager):
        self.event_manager = event_manager

        self._win = None

        self.new_year_arrived = False

        # Таймер для обновления (каждую минуту для проверки полночи)
        self.new_year_timer = QTimer()
        self.new_year_timer.timeout.connect(self.check_time)
        self.new_year_timer.start(60000)  # 60 секунд

        # Таймер для анимации текста (если нужно мигание)
        self.text_animation_timer = QTimer()
        self.text_animation_timer.timeout.connect(self.animate_text)
        #self.text_animation_timer.start(500)  # 0.5 секунды
        self.text_visible = True

        # Таймер для обновления счетчика каждую секунду
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._check_triggers)
        self.update_timer.start(1000)  # Каждую секунду

        # Триггер для момента наступления Нового года
        self.triggered = False
        self.new_year_triggered = False  # Новый год наступил (00:00 1 января)
        self.holidays_triggered = False  # Начались каникулы (08:00 1 января)

        # Новогодние переменные
        self.new_year_event = False
        self.new_year_text = ""
        self.show_new_year_text = True  # Флаг для показа/скрытия текста
        self.text_position = "bottom_left"  # Позиция текста
        self.text_color = QColor(255, 215, 0)  # Золотой цвет
        self.text_shadow_color = QColor(139, 0, 0)  # Темно-красный для тени
        self.text_font = QFont("Arial", 10 * self.win.models_scale, QFont.Bold)

        # Инициализация новогоднего статуса
        self.update_new_year_status()

        self.check_initial_status()

        self._update_text()

    @property
    def win(self):
        """Actual window link"""
        return self.event_manager.win

    def check_initial_status(self):
        """Проверяет и устанавливает начальный статус при запуске"""
        now = datetime.now()

        # Если уже 1 января
        if now.month == 1 and now.day == 1:
            if now.hour < 8:
                self.new_year_triggered = True
            else:
                self.new_year_triggered = True
                self.holidays_triggered = True

        # Если уже после 1 января (но в пределах новогоднего периода)
        elif now.month == 1 and 1 < now.day <= 10:
            self.new_year_triggered = True
            self.holidays_triggered = True

        if self.event_manager.event_log:
            print(f"Initial status: new_year_triggered={self.new_year_triggered}, holidays_triggered={self.holidays_triggered}")

    def _check_triggers(self):
        """Проверяет все триггеры каждую секунду"""
        now = datetime.now()

        if now.second == 0 and self.event_manager.event_log:  # Логируем каждую минуту
            print(f"Debug: {now} | new_year_triggered={self.new_year_triggered} | holidays_triggered={self.holidays_triggered}")

        # 1. Триггер Нового года (1 января 00:00)
        if (now.month == 1 and now.day == 1 and
                now.hour == 0 and now.minute == 0 and now.second == 0):

            if not self.new_year_triggered:
                self._on_new_year_arrival()

        # 2. Триггер начала каникул (1 января 08:00)
        elif (now.month == 1 and now.day == 1 and
              now.hour == 8 and now.minute == 0 and now.second == 0):

            if not self.holidays_triggered:
                self._on_holidays_start()

        # 3. Если уже после 1 января, автоматически включаем каникулы
        elif now.month == 1 and now.day > 1 and not self.holidays_triggered:
            self.holidays_triggered = True

        # Обновляем текст
        self._update_text()

    def _on_new_year_arrival(self):
        """Триггер наступления Нового года (00:00 1 января)"""
        self.new_year_triggered = True
        if self.event_manager.event_log:
            print("🎉🎉🎉 С НОВЫМ ГОДОМ! 🎉🎉🎉")

        # Здесь можно запустить праздничные эффекты:
        # self._start_fireworks()
        # self._play_new_year_sound()
        # self._show_confetti()

        # Установим таймер на 8 часов для переключения на каникулы
        self.holidays_timer = QTimer()
        self.holidays_timer.timeout.connect(self._force_holidays_start)
        self.holidays_timer.setSingleShot(True)
        self.holidays_timer.start(8 * 60 * 60 * 1000)  # 8 часов в миллисекундах

    def _on_holidays_start(self):
        """Триггер начала новогодних каникул (08:00 1 января)"""
        self.holidays_triggered = True
        if self.event_manager.event_log:
            print("🎅🎄 Начались новогодние каникулы! 🎄🎅")

        # Здесь можно запустить эффекты для каникул:
        # self._change_holiday_theme()
        # self._play_holiday_music()

    def _force_holidays_start(self):
        """Принудительно запускает каникулы через 8 часов после НГ"""
        if not self.holidays_triggered:
            self.holidays_triggered = True
            if self.event_manager.event_log:
                print("⏰ Прошло 8 часов - начинаем каникулы!")

    def _update_text(self):
        """Обновляет текст в зависимости от состояния"""
        self.new_year_text = self.get_new_year_info()

    def get_new_year_info(self) -> str:
        """Возвращает информацию в зависимости от этапа"""
        now = datetime.now()  # Используем datetime вместо date
        today = now.date()  # Получаем только дату для сравнений

        # Этап 1: Обратный отсчет до Нового года (до 31 декабря)
        if today.month == 12:
            return self._get_countdown_to_new_year()

        # Этап 2: Новый год только что наступил (1 января 00:00-08:00)
        elif today.month == 1 and today.day == 1 and not self.holidays_triggered:
            if self.new_year_triggered:
                # Показываем сколько прошло времени после Нового года
                time_since = self._get_time_since_new_year()
                hours = time_since.seconds // 3600
                minutes = (time_since.seconds % 3600) // 60

                if now.hour < 8:  # Используем now.hour вместо today.hour
                    return f"🎉🎉🎉 {self.win.lang['NewYearEvent']['Congratulation']} 🎉🎉🎉"
                else:
                    return f"🎅 {self.win.lang['NewYearEvent']['Holidays']} 1"
            else:
                # Если почему-то не сработал триггер, но уже 1 января
                return f"🎉🎉🎉 {self.win.lang['NewYearEvent']['Congratulation']} 🎉🎉🎉"

        # Этап 3: Новогодние каникулы (1-10 января)
        elif today.month == 1 and today.day <= 10:
            days_passed = (today - date(today.year, 1, 1)).days
            return f"🎅 {self.win.lang['NewYearEvent']['Holidays']} {days_passed + 1}"

        # Этап 4: Вне новогоднего периода
        else:
            return self._get_countdown_to_next_year()

    def _get_countdown_to_new_year(self) -> str:
        """Обратный отсчет до Нового года (в декабре)"""
        now = datetime.now()
        new_year = datetime(now.year + 1, 1, 1, 0, 0, 0)
        time_left = new_year - now

        if time_left.days > 0:
            return (f"🎄 {self.win.lang['NewYearEvent']['Until']} {time_left.days}"
                    f" {self.win.lang['NewYearEvent']['Days']}")
        elif time_left.seconds >= 3600:
            hours = time_left.seconds // 3600
            minutes = (time_left.seconds % 3600) // 60
            seconds = time_left.seconds % 60
            return (f"🎄 {self.win.lang['NewYearEvent']['Until']} {hours:02d}"
                    f" {self.win.lang['NewYearEvent']['Hours']} {minutes:02d}"
                    f" {self.win.lang['NewYearEvent']['Minutes']}")
        elif time_left.seconds >= 60:
            minutes = time_left.seconds // 60
            seconds = time_left.seconds % 60
            return (f"🎄 {self.win.lang['NewYearEvent']['Until']} {minutes:02d}"
                    f" {self.win.lang['NewYearEvent']['Minutes']} {seconds:02d}"
                    f" {self.win.lang['NewYearEvent']['Seconds']}")
        else:
            return (f"🎄 {self.win.lang['NewYearEvent']['Until']} {time_left.seconds:02d}"
                    f" {self.win.lang['NewYearEvent']['Seconds']}")

    def _get_time_since_new_year(self) -> timedelta:
        """Сколько времени прошло с Нового года"""
        now = datetime.now()
        new_year = datetime(now.year, 1, 1, 0, 0, 0)
        return now - new_year

    def _get_countdown_to_next_year(self) -> str:
        """Обратный отсчет до следующего Нового года (вне сезона)"""
        now = datetime.now()
        next_new_year = datetime(now.year + 1, 1, 1, 0, 0, 0)
        time_left = next_new_year - now

        if time_left.days > 30:
            return (f"🎄 {self.win.lang['NewYearEvent']['Until']} {time_left.days}"
                    f" {self.win.lang['NewYearEvent']['Days']}")
        elif time_left.days > 0:
            return (f"🎄 {self.win.lang['NewYearEvent']['Until']} {time_left.days}"
                    f" {self.win.lang['NewYearEvent']['Days']} {time_left.seconds // 3600}"
                    f" {self.win.lang['NewYearEvent']['Minutes']}")
        else:
            return (f"🎄 {self.win.lang['NewYearEvent']['Until']} {time_left.seconds // 3600}"
                    f" {self.win.lang['NewYearEvent']['Minutes']}")

    def text_update(self):
        """Обновляет текст счетчика"""
        if not self.new_year_arrived:
            self.new_year_text = self.get_new_year_info()

    def _get_time_until_new_year(self) -> timedelta:
        """Рассчитывает время до ближайшего Нового года"""
        now = datetime.now()
        current_year = now.year

        # Если сегодня уже после 1 января (но до 10 января - наш новогодний период)
        # то Новый год УЖЕ наступил
        if now.month == 1 and now.day >= 1:
            # Новый год уже наступил в этом году
            # Возвращаем отрицательное время или 0
            new_year_this_year = datetime(current_year, 1, 1, 0, 0, 0)
            time_since = now - new_year_this_year

            # Если прошло больше 0 секунд - Новый год уже наступил
            if time_since.total_seconds() > 0:
                return timedelta(seconds=0)  # Возвращаем 0

        # Если мы в декабре (после 20) или в январе (до 1), считаем до следующего НГ
        new_year_datetime = datetime(current_year + 1, 1, 1, 0, 0, 0)
        return new_year_datetime - now

    def update_new_year_status(self):
        """Обновляет статус новогоднего события"""
        old_status = self.new_year_event
        self.new_year_event = self.event_status()
        #self.new_year_text = self.get_new_year_info()

        # Если статус изменился
        if old_status != self.new_year_event:
            self.on_new_year_status_changed(self.new_year_event)

    def event_status(self) -> bool:
        if self.event_manager.current_event is None:
            return False
        else:
            return True

    def check_time(self):
        """Проверяет время и обновляет статус если наступила полночь"""
        now = datetime.now()
        if now.hour == 0 and now.minute == 0:
            self.update_new_year_status()
            self.win.update()  # Перерисовываем виджет

    def animate_text(self):
        """Анимация текста (мигание)"""
        if self.new_year_event and self.show_new_year_text:
            self.text_visible = not self.text_visible
            self.win.update()

    def on_new_year_status_changed(self, is_new_year: bool):
        """Вызывается при изменении статуса новогоднего события"""
        if is_new_year:
            if self.event_manager.event_log:
                print("🎄 Новогодний период начался!")
            self.apply_new_year_theme()
            # Запускаем анимацию текста
            #self.text_animation_timer.start(800)
        else:
            if self.event_manager.event_log:
                print("📅 Новогодний период закончился")
            self.apply_normal_theme()
            # Останавливаем анимацию
            #self.text_animation_timer.stop()
            self.text_visible = True

    def apply_new_year_theme(self):
        """Применяем новогоднюю тему"""
        self.win.background_name = "new_year"

        # Можно также изменить другие параметры
        self.text_color = QColor(255, 215, 0)  # Золотой
        self.text_shadow_color = QColor(139, 0, 0)  # Темно-красный

    def apply_normal_theme(self):
        """Возвращаем обычную тему"""
        self.win.background_name = ""

        self.text_color = QColor(255, 255, 255)  # Белый
        self.text_shadow_color = QColor(0, 0, 0)  # Черный

    def draw_new_year_text(self, painter: QPainter):
        """Рисует новогодний текст на виджете"""
        if not self.new_year_event or not self.show_new_year_text or not self.text_visible:
            return

        if not self.new_year_text:
            return

        # Настраиваем шрифт
        painter.setFont(self.text_font)
        self.text_font = QFont("Arial", 10 * self.win.models_scale, QFont.Bold)

        # Получаем размеры текста
        font_metrics = QFontMetrics(self.text_font)
        text_width = font_metrics.horizontalAdvance(self.new_year_text)
        text_height = font_metrics.height()

        # Определяем позицию в зависимости от настроек
        if self.win.frameless:
            padding = 50
            framless_c = 25
        else:
            padding = 25
            framless_c = 0

        if self.text_position == "top_right":
            x = self.win.width() - text_width - padding
            y = padding + text_height
        elif self.text_position == "top_left":
            x = padding
            y = padding + text_height
        elif self.text_position == "bottom_right":
            x = self.win.width() - self.win.w_correction - text_width - padding
            y = self.win.height() - padding
        elif self.text_position == "bottom_left":
            x = padding
            y = self.win.height() - padding + framless_c
        else:  # center
            x = (self.win.width() - self.win.w_correction - text_width) // 2
            y = (self.win.height() // 2) - text_height

        # Рисуем тень текста (смещение 2px)
        painter.setPen(self.text_shadow_color)
        painter.drawText(x + 2, y + 2, self.new_year_text)

        # Рисуем основной текст
        painter.setPen(self.text_color)
        painter.drawText(x, y, self.new_year_text)

        # Методы для управления текстом извне

    def toggle_new_year_text(self, visible: bool = None):
        """Включить/выключить отображение новогоднего текста"""
        if visible is None:
            self.show_new_year_text = not self.show_new_year_text
        else:
            self.show_new_year_text = visible
        self.win.update()

    def set_text_position(self, position: str):
        """Установить позицию текста"""
        valid_positions = ["top_right", "top_left", "bottom_right", "bottom_left", "center"]
        if position in valid_positions:
            self.text_position = position
            self.win.update()

    def set_text_color(self, color: QColor):
        """Установить цвет текста"""
        self.text_color = color
        self.win.update()

    def set_text_font(self, font_family: str = "Arial", size: int = 12, bold: bool = True):
        """Установить шрифт текста"""
        self.text_font = QFont(font_family, size)
        self.text_font.setBold(bold)
        self.win.update()

    def draw_on_model(self):
        if self.show_new_year_text:
            painter2 = QPainter(self.win)
            self.draw_new_year_text(painter2)
            painter2.end()


