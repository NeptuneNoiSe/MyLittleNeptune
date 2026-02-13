from datetime import datetime, date, timedelta
from os.path import split
import random
from typing import Dict, Optional

from PySide6.QtGui import QFont, QPainter, QColor, QFontMetrics
from PySide6.QtCore import QTimer


class EventManager:
    def __init__(self, win):
        self.win = win
        self.event_instance = None
        self.event_log = False
        self.special_stage = None
        self.delay_congratulation_after_greeting = None
        self.show_event_greeting = False

        self.event_time_manager = EventTimeManager(self)

        # Get the current event
        self.current_event = self.event_time_manager.get_current_event()

        # Run the check current event
        self.check_events()  # This method create event_instance

        self.set_stage()

    @property
    def bgm_name(self):
        return self.win.bgm_name

    @bgm_name.setter
    def bgm_name(self, value):
        self.win.bgm_name = value

    def set_stage(self):
        if self.event_instance:
            self.special_stage = self.event_instance.get_special_stage()

    def check_events(self):
        """Checks and creates an event"""
        if self.current_event:
            class_name = self.current_event.replace(" ", "") + "Event"

            try:
                event_class = globals()[class_name]
                self.event_instance = event_class(self)
            except KeyError:
                print(f"Класс {class_name} не найден")
                self.event_instance = None
        else:
            self.event_instance = None

    def draw_event_text(self, painter):
        if self.event_instance:
            self.event_instance.draw_event_text(painter)

    def congratulate_event(self, duration= 10000):
        if self.event_instance:
            self.event_instance.congratulate_event(duration)

    #def draw_event_text(self, painter):
    #    if self.current_event is None:
    #        return
    #    self.event_instance.draw_new_year_text(painter)

    def draw_text_on_model(self):
        if self.current_event is None:
            return
        self.event_instance.draw_on_model()

class EventTimeManager:
    def __init__(self, event_manager):
        self.event_manager = event_manager

        self._event_schedule = self._load_schedule()

        self._special_event_schedule = self._load_special_day_schedule()

    def _load_schedule(self) -> Dict:
        """Loads the event schedule"""
        return {
            "New Year": {
                "start": {"month": 12, "day": 17},
                "end": {"month": 1, "day": 11}
            },
            "Valentines Day": {
                "start": {"month": 2, "day": 14},
                "end": {"month": 2, "day": 15}
            }
            # Other Events:
            # "Halloween": {"start": {"month": 10, "day": 28}, "end": {"month": 11, "day": 2}},
            # "Birthday": {"start": {"month": 1, "day": 15}, "end": {"month": 1, "day": 15}},
        }

    def _load_special_day_schedule(self) -> Dict:
        """Loads the special day event schedule"""
        return {
            "New Year Day": {
                "start": {"month": 12, "day": 31},
                "end": {"month": 1, "day": 1}
            }
        }

    def get_current_event(self) -> Optional[str]:
        """Defines the current active event"""
        today = date.today()

        for event_name, schedule in self._event_schedule.items():
            start = schedule["start"]
            end = schedule["end"]

            # Check if today falls within the event period.
            if self._is_date_in_period(today, start, end):
                return event_name

        return None

    def get_special_event(self) -> Optional[str]:
        """Defines the current active special event"""
        today = date.today()

        for special_event_name, schedule in self._special_event_schedule.items():
            start = schedule["start"]
            end = schedule["end"]

            # Check if today falls within the special event period.
            if self._is_date_in_period(today, start, end):
                return special_event_name

        return None

    def _is_date_in_period(self, check_date: date, start: dict, end: dict) -> bool:
        """Checks whether the date is in the event period"""
        # If the event passes through a year (for example, December-January)
        if start["month"] > end["month"]:
            # Period: December -> January
            if check_date.month == 12 and check_date.day >= start["day"]:
                return True
            elif check_date.month == 1 and check_date.day <= end["day"]:
                return True
        else:
            # A period of one year
            start_date = date(check_date.year, start["month"], start["day"])
            end_date = date(check_date.year, end["month"], end["day"])
            return start_date <= check_date <= end_date

        return False

class NewYearEvent:
    def __init__(self, event_manager):
        self.event_manager = event_manager

        self._win = None

        self.new_year_arrived = False

        self.win.background_available = True

        # Timer for updating (every minute to check midnight)
        self.new_year_timer = QTimer()
        self.new_year_timer.timeout.connect(self.check_time)
        self.new_year_timer.start(60000)  # 60 секунд

        # Timer for text animation (blinking if needed)
        self.text_animation_timer = QTimer()
        self.text_animation_timer.timeout.connect(self.animate_text)
        #self.text_animation_timer.start(500)  # 0.5 sec
        self.text_visible = True

        # Timer for updating the counter every second
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._check_triggers)
        self.update_timer.start(1000)  # every 1 sec

        # The trigger for the New Year's Eve
        self.triggered = False
        self.new_year_triggered = False  # New Year's has arrived (00:00 on January 1st)
        self.holidays_triggered = False  # Holidays have started (08:00 on January 1st)
        self.christmas_triggered = False  # Christmas (25 and 7)
        self.event_end_triggered = False # End of the Event

        # New Year's Variables
        self.new_year_event = False
        self.new_year_text = ""
        self.show_new_year_text = True  # Flag for showing/hiding text
        self.text_position = "bottom_left"  # Text possition
        self.text_color = QColor(255, 215, 0)  # Gold color
        self.text_shadow_color = QColor(139, 0, 0)  # Dark red for shade
        self.text_font = QFont("Ink Free", 12 * self.win.models_scale, QFont.Bold)
        self.win.current_sing_song = "padoru"

        # BackGround Hint
        if not self.win.app_config.background and self.win.background_available and self.win.first_run:
            self.hint_timer = QTimer()
            self.hint_timer.timeout.connect(lambda: self.win.character.state.set_event_hint_state("BackGroundHint"))
            self.hint_timer.setSingleShot(True)
            hint_interval = random.randint(10, 100) * 1000
            self.hint_timer.start(hint_interval)

        # Initializing the New Year's status
        self.update_new_year_status()

        self.check_initial_status()

        self._update_text()

    @property
    def win(self):
        """Actual window link"""
        return self.event_manager.win

    def get_special_stage(self):
        now = datetime.now()

        # PRIORITY CHECK (from more specific to general):

        # Highest priority: New Year's Eve on January 1st in the morning
        if now.month == 1 and now.day == 1 and now.hour < 8:
            return "Congratulation"

        # Christmas (depends on the language)
        if now.month == 12 and now.day == 25 and self.win.language == "English":
            return "Xmas"
        if now.month == 1 and now.day == 7 and self.win.language == "Russian":
            return "Xmas"

        # New Year's Eve
        if now.month == 12 and now.day == 31:
            return "Greeting Today"

        # New Year's holidays (January 1 after 8 a.m. and January 2-11)
        if now.month == 1:
            if now.day == 1 and now.hour >= 8:
                return "Greeting Holidays"
            elif 2 <= now.day <= 11:
                return "Greeting Holidays"

        return None

    def get_song_name(self):
        """Get song name deppending event triggers"""
        song_name = None
        if self.christmas_triggered:
            song_name = "christmas_song"
        elif self.holidays_triggered:
            song_name = "holidays_song"
        elif self.event_end_triggered:
            song_name = None
        else:
            song_name = "new_year_song"
        return song_name

    def check_initial_status(self):
        """Checks and sets the initial status at startup"""
        now = datetime.now()

        if (now.month == 12 and now.day == 31):
            self.on_new_year_day_arrival()

        # If it's already January 1st
        if now.month == 1 and now.day == 1:
            if now.hour < 8:
                self.new_year_triggered = True
            else:
                self.new_year_triggered = True
                self.holidays_triggered = True

        # If it is already after January 1 (but within the New Year period)
        elif now.month == 1 and 1 < now.day <= 11:
            self.new_year_triggered = True
            self.holidays_triggered = True

        elif (now.month == 12 and now.day == 25 and self.win.language == "English"):
            self.christmas_triggered = True

        elif (now.month == 1 and now.day == 7 and self.win.language == "Russian"):
            self.christmas_triggered = True

        if self.event_manager.event_log:
            print(f"Initial status: new_year_triggered={self.new_year_triggered}, holidays_triggered={self.holidays_triggered}")

    def _check_triggers(self):
        """Checks all triggers every second"""
        now = datetime.now()

        if now.second == 0 and self.event_manager.event_log:  # Логируем каждую минуту
            print(f"Debug: {now} | new_year_triggered={self.new_year_triggered} | holidays_triggered={self.holidays_triggered}")

        # Character Sleep OFF
        if (now.month == 12 and now.day == 24 and
                now.hour == 23 and now.minute >= 0 and self.win.language == "English" and not self.christmas_triggered):
            self.win.character.tired_controller.reset_timer()

        elif (now.month == 12 and now.day == 31 and
                now.hour == 23 and now.minute >= 0  and not self.new_year_triggered):
            self.win.character.tired_controller.reset_timer()

        elif (now.month == 1 and now.day == 1
              and now.hour < 1):
            self.win.character.tired_controller.reset_timer()

        elif (now.month == 1 and now.day == 6 and
                now.hour == 23 and now.minute >= 0 and self.win.language == "Russian" and not self.christmas_triggered):
            self.win.character.tired_controller.reset_timer()

        # Character Sleep ON
        elif (now.month == 1 and now.day == 1
              and now.hour == 1 and now.minute == 0 and now.second == 0):
            self.win.character.tired_controller.start_timer()

        if (now.month == 1 and now.day == 12
              and now.hour == 0 and now.minute == 0 and now.second == 0):
            self.event_end_triggered = True
            self.holidays_triggered = False
            self.event_end()

        # New Year's Trigger (January 1, 00:00)
        if (now.month == 1 and now.day == 1 and
                now.hour == 0 and now.minute == 0 and now.second == 0):

            if not self.new_year_triggered:
                self._on_new_year_arrival()

        # Holiday start trigger (January 1, 08:00)
        elif (now.month == 1 and now.day == 1 and
              now.hour == 8 and now.minute == 0 and now.second == 0):

            if not self.holidays_triggered:
                self._on_holidays_start()

        # If it's already after January 1st, we automatically turn on the holidays.
        elif now.month == 1 and now.day > 1 and now.day <= 11 and not self.holidays_triggered:
            self.holidays_triggered = True

        # If English Christmas 25 december
        elif (now.month == 12 and now.day == 25 and self.win.language == "English"):
            self.christmas_triggered = True
            if (now.hour == 0 and now.minute == 0 and now.second == 0):
                self._on_christmas_arrival()

        # English Christmas end 26 december
        elif (now.month == 12 and now.day == 26
              and now.hour == 0 and now.minute == 0 and now.second == 0
              and self.win.language == "English" ):
            self.christmas_triggered = False

        # If Russian Christmas 7 january
        elif (now.month == 1 and now.day == 7 and self.win.language == "Russian"):
            self.christmas_triggered = True
            if (now.hour == 0 and now.minute == 0 and now.second == 0):
                self._on_christmas_arrival()

        # Russian Christmas end 8 january
        elif (now.month == 1 and now.day == 8
              and now.hour == 0 and now.minute == 0 and now.second == 0
              and self.win.language == "Russian" ):
            self.christmas_triggered = False

        self.event_manager.bgm_name = self.get_song_name()

        # Update Text
        self._update_text()

    def on_new_year_day_arrival(self):
        """New Year's Eve Trigger (00:00 on January 1st)"""
        #self.new_year_triggered = True
        if self.event_manager.event_log:
            print("🎉 31 December 🎉")

        self.event_manager.special_event = "New Year Day"

    def _on_new_year_arrival(self):
        """New Year's Eve Trigger (00:00 on January 1st)"""
        self.new_year_triggered = True
        self.win.character.state.set_event_congratulation_state(event_name=self.event_manager.current_event,
                                                                event_key="Congratulation")
        self.win.audio_manager.play_audio("Effects", "new_year_fanfare", enable_lipsync=False, category="sfx",
                                      stop_audio=False)
        if self.event_manager.event_log:
            print("🎉🎉🎉 HAPPY NEW YEAR 🎉🎉🎉")

        # Set the timer to 8 o'clock to switch to the holidays.
        self.holidays_timer = QTimer()
        self.holidays_timer.timeout.connect(self._force_holidays_start)
        self.holidays_timer.setSingleShot(True)
        self.holidays_timer.start(8 * 60 * 60 * 1000)  # 8 hours in milliseconds

    def _on_christmas_arrival(self):
        """Christmas trigger (00:00 on December 25th or January 7th)"""
        self.christmas_triggered = True
        self.win.character.state.set_event_congratulation_state(event_name=self.event_manager.current_event,
                                                                event_key="Xmas")
        if self.event_manager.event_log:
            print("🎅🎄 Merry Christmas 🎄🎅")

        self.win.character.tired_controller.start_timer()

    def _on_holidays_start(self):
        """The trigger for the start of the New Year holidays (08:00 on January 1)"""
        self.holidays_triggered = True
        if self.event_manager.event_log:
            print("🎅 The New Year holidays have begun! 🎅")

    def _force_holidays_start(self):
        """Forcibly launches holidays 8 hours after NY"""
        if not self.holidays_triggered:
            self.holidays_triggered = True
            if self.event_manager.event_log:
                print("⏰ It's been 8 hours - let's start the holidays!")

    def _update_text(self):
        """Updates the text depending on the status"""
        self.new_year_text = self.get_new_year_info()

    def get_new_year_info(self) -> str:
        """Returns information depending on the stage"""
        now = datetime.now()
        today = now.date()

        # FIRST PRIORITY: Christmas (January 7th)
        if now.month == 1 and now.day == 7 and self.win.language == "Russian":
            return f"🎅🎄 {self.win.lang['NewYearEvent']['Xmas']} 🎄🎅"

        # Countdown to the New Year (until December 31)
        if today.month == 12:
            return self._get_countdown_to_new_year()

        # The New Year has just arrived (January 1, 00:00-08:00)
        elif today.month == 1 and today.day == 1 and not self.holidays_triggered:
            if self.new_year_triggered:
                time_since = self._get_time_since_new_year()
                hours = time_since.seconds // 3600

                if now.hour < 8:
                    return f"🎉🎉🎉 {self.win.lang['NewYearEvent']['Congratulation']} 🎉🎉🎉"
                else:
                    return f"🎅 {self.win.lang['NewYearEvent']['Holidays']} 1"
            else:
                return f"🎉🎉🎉 {self.win.lang['NewYearEvent']['Congratulation']} 🎉🎉🎉"

        # New Year's holidays (January 1-11)
        elif today.month == 1 and today.day <= 11:
            days_passed = (today - date(today.year, 1, 1)).days

            # January 8 (the day after Christmas) - return to the holidays
            if now.day == 8:
                return f"🎅 {self.win.lang['NewYearEvent']['Holidays']} {days_passed + 1}"
            # January 1-6, 9-11 - regular holidays
            else:
                return f"🎅 {self.win.lang['NewYearEvent']['Holidays']} {days_passed + 1}"

        # Outside the New Year period
        else:
            return self._get_countdown_to_next_year()

    def _get_countdown_to_new_year(self) -> str:
        """Countdown to New Year's Eve (in December)"""
        now = datetime.now()
        new_year = datetime(now.year + 1, 1, 1, 0, 0, 0)
        time_left = new_year - now

        if not self.christmas_triggered:
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
        else:
            return f"🎅🎄 {self.win.lang['NewYearEvent']['Xmas']} 🎄🎅"

    def _get_time_since_new_year(self) -> timedelta:
        """How long has it been since New Year's"""
        now = datetime.now()
        new_year = datetime(now.year, 1, 1, 0, 0, 0)
        return now - new_year

    def _get_countdown_to_next_year(self) -> str:
        """Countdown to next New Year (out of season)"""
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
        """Updates the tag text"""
        if not self.new_year_arrived:
            self.new_year_text = self.get_new_year_info()

    def _get_time_until_new_year(self) -> timedelta:
        """Calculates the time until the next New Year"""
        now = datetime.now()
        current_year = now.year

        # If today is after January 1st (but before January 10th is our New Year period)
        # then the New Year has ALREADY arrived
        if now.month == 1 and now.day >= 1:
            # The New Year has already arrived this year
            # Return negative time or 0
            new_year_this_year = datetime(current_year, 1, 1, 0, 0, 0)
            time_since = now - new_year_this_year

            # If more than 0 seconds have passed, the New Year has already arrived.
            if time_since.total_seconds() > 0:
                return timedelta(seconds=0)  # Return 0

        # If we are in December (after 20) or January (before 1), we count until the next NY
        new_year_datetime = datetime(current_year + 1, 1, 1, 0, 0, 0)
        return new_year_datetime - now

    def update_new_year_status(self):
        """Updates the status of the New Year's event"""
        old_status = self.new_year_event
        self.new_year_event = self.event_status()
        #self.new_year_text = self.get_new_year_info()

        # If the status has changed
        if old_status != self.new_year_event:
            self.on_new_year_status_changed(self.new_year_event)

    def event_status(self) -> bool:
        if self.event_manager.current_event is None:
            return False
        else:
            return True

    def check_time(self):
        """Checks the time and updates the status if midnight has arrived."""
        now = datetime.now()
        if now.hour == 0 and now.minute == 0:
            self.update_new_year_status()
            self.win.update()  # ReDraw widget

    def animate_text(self):
        """Text animation (blinking)"""
        if self.new_year_event and self.show_new_year_text:
            self.text_visible = not self.text_visible
            self.win.update()

    def on_new_year_status_changed(self, is_new_year: bool):
        """Called when the status of a New Year's event changes."""
        if is_new_year:
            if self.event_manager.event_log:
                print("🎄 The New Year period has begun!")
            self.apply_new_year_theme()
            # Run Text Animation
            #self.text_animation_timer.start(800)
        else:
            if self.event_manager.event_log:
                print("📅 The New Year period is over")
            self.apply_normal_theme()
            # Stop Animation
            #self.text_animation_timer.stop()
            self.text_visible = True

    def apply_new_year_theme(self):
        """Apply a New Year's theme"""
        self.win.background_name = "new_year"
        self.text_color = QColor(255, 215, 0)  # Gold
        self.text_shadow_color = QColor(139, 0, 0)  # Dark Red

    def apply_normal_theme(self):
        """Return the usual theme"""
        self.win.background_name = ""

        self.text_color = QColor(255, 255, 255)  # Белый
        self.text_shadow_color = QColor(0, 0, 0)  # Черный

    def draw_new_year_text(self, painter: QPainter):
        """Draws New Year's text on the widget"""
        if not self.new_year_event or not self.show_new_year_text or not self.text_visible:
            return

        if not self.new_year_text:
            return

        # Set Font
        painter.setFont(self.text_font)
        self.text_font = QFont("Ink Free", 12 * self.win.models_scale, QFont.Bold)

        # Get text size
        font_metrics = QFontMetrics(self.text_font)
        text_width = font_metrics.horizontalAdvance(self.new_year_text)
        text_height = font_metrics.height()

        # Determine the position depending on the settings
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

        # Draw the shadow of the text (offset 2px)
        painter.setPen(self.text_shadow_color)
        painter.drawText(x + 2, y + 2, self.new_year_text)

        # Draw the main text
        painter.setPen(self.text_color)
        painter.drawText(x, y, self.new_year_text)

    def toggle_new_year_text(self, visible: bool = None):
        """Turn on/off the display of New Year's text"""
        if visible is None:
            self.show_new_year_text = not self.show_new_year_text
        else:
            self.show_new_year_text = visible
        self.win.update()

    def set_text_position(self, position: str):
        """Set the text position"""
        valid_positions = ["top_right", "top_left", "bottom_right", "bottom_left", "center"]
        if position in valid_positions:
            self.text_position = position
            self.win.update()

    def set_text_color(self, color: QColor):
        """Set the text color"""
        self.text_color = color
        self.win.update()

    def set_text_font(self, font_family: str = "Ink Free", size: int = 12, bold: bool = True):
        """Set the text font"""
        self.text_font = QFont(font_family, size)
        self.text_font.setBold(bold)
        self.win.update()

    def draw_on_model(self):
        if self.show_new_year_text:
            painter2 = QPainter(self.win)
            self.draw_new_year_text(painter2)
            painter2.end()

    def event_end(self):
        self.holidays_triggered = False
        self.new_year_event = False
        self.event_manager.bgm_name = None
        self.win.background_name = None
        self.win.background = False
        self.win.current_sing_song = None
        self.win.background_available = False

class ValentinesDayEvent:
    def __init__(self, event_manager):
        self.event_manager = event_manager

        self._win = None

    @property
    def win(self):
        """Actual window link"""
        return self.event_manager.win

    def get_special_stage(self):
        self.event_manager.delay_congratulation_after_greeting = 15000
        return "Congratulation"

    def draw_event_text(self, painter: QPainter):
        """Draws Even text on the widget"""
        pass

    def draw_on_model(self):
        pass

    def congratulate_event(self, duration):
        self.win.animation_manager.play_color_pulse(pulse_duration=1000, r=255, g=126, b=147, stop_after_ms=duration)
        self.win.image_manager.item_image.set_item("valentinebox", position=(0, -50 * self.win.a_scale),opacity=0)
        self.win.image_manager.item_image.set_percentage_size(relative_to_model=True,
                                                              width_percent=16,
                                                              height_percent=16)
        self.win.animation_manager.opacity_animator.animate_opacity(source=self.win.image_manager.item_image,
                                                                    start=0,
                                                                    end=1,
                                                                    duration=1500,
                                                                    easing="in_quad")

        self.win.image_manager.item_image.animate_bounce_continuous(animation = "animate_bounce",
                                                                    height=10,
                                                                    bounce_duration=duration/10,
                                                                    bounces=3,
                                                                    total_duration=duration)

        def function_stop():
            end_duration = duration / 4
            self.win.image_manager.item_image.animate_scale_bounce(0, 0.5, duration=end_duration)
            self.win.animation_manager.opacity_animator.animate_opacity(
                source=self.win.image_manager.item_image,
                start=1,
                end=0,
                duration=end_duration,
                easing="out_quad")
            QTimer.singleShot(duration, self.win.image_manager.item_image.hide)

        QTimer.singleShot(duration, function_stop)
