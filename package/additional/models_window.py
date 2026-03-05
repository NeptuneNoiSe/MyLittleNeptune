from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QScrollArea,
                               QGridLayout, QPushButton, QLabel, QFrame, QToolButton)
from PySide6.QtCore import Qt, Signal, Slot, QSize, QPropertyAnimation, QEasingCurve, QPoint, Property, QTimer
from PySide6.QtGui import QIcon, QPixmap
import os
from typing import List, Dict, Optional
import resources

class ModelsWindow(QWidget):
    """Models Window Class"""
    character_selected = Signal(str)  # Сигнал для передачи выбранного персонажа

    def __init__(self, win):
        super().__init__()
        self.win = win

        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

        self.can_select = True
        self.selection_timer = QTimer()
        self.selection_timer.setSingleShot(True)
        self.selection_timer.timeout.connect(self.allow_selection)
        self.is_error = False

        self.message_timer = QTimer()
        self.message_timer.setSingleShot(True)
        self.message_timer.timeout.connect(self.hide_message)

        # Настройка окна
        self.setWindowTitle("Character Selector")
        self.setFixedSize(660, 560)

        # Установка иконки окна
        icon_path = os.path.join(resources.RESOURCES_DIRECTORY, "icons/color/character.svg")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Основной layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Заголовок
        self.title_label = QLabel("Выберите персонажа")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            padding: 10px;
        """)
        # main_layout.addWidget(self.title_label)

        # Лейбл для сообщений (изначально скрыт)
        self.message_label = QLabel()
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setStyleSheet("""
            QLabel {
                background-color: #ff9800;
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 8px;
                border-radius: 5px;
                margin: 5px;
            }
        """)
        self.message_label.hide()  # Скрываем по умолчанию
        main_layout.addWidget(self.message_label)

        # Создание прокручиваемой области для кнопок
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Виджет для контента внутри скролла
        self.scroll_content = QWidget()
        self.scroll_layout = QGridLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll_layout.setSpacing(15)

        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)

    def set_language(self):
        self.setWindowTitle(self.win.lang['ModelsWindow']['Title'])
        self.title_label.setText(self.win.lang['ModelsWindow']['Title'])
        self.load_characters()

    def load_characters(self, include_hdd: bool = True):
        """Загружает и отображает кнопки всех персонажей"""
        # Получаем списки персонажей (английские имена для логики)
        base_names = self.win.resource_manager.get_base_character_names()
        hdd_names = self.win.resource_manager.get_hdd_character_names() if include_hdd else []

        # Очищаем предыдущее содержимое
        self.clear_layout(self.scroll_layout)

        row = 0
        col = 0
        max_cols = 4

        def get_localized_name(orig_name: str) -> str:
            """Возвращает локализованное имя персонажа"""
            normalized_name = orig_name.replace(" ", "")
            if hasattr(self.win, 'lang') and 'Names' in self.win.lang:
                return self.win.lang['Names'].get(normalized_name, orig_name)
            return orig_name

        def create_character_button(orig_name: str, is_hdd: bool = False):
            display_name = get_localized_name(orig_name)

            image_path = self.win.resource_manager.get_character_image_path(orig_name)

            btn = CharacterButton(
                character_name=display_name,
                image_path=image_path,
                is_hdd=is_hdd
            )

            btn.clicked.connect(lambda checked, name=orig_name: self.on_character_selected(name))
            return btn

        for orig_name in base_names:
            if col >= max_cols:
                row += 1
                col = 0
            btn = create_character_button(orig_name, is_hdd=False)
            self.scroll_layout.addWidget(btn, row, col)
            col += 1

        if hdd_names:
            row += 1
            col = 0

            hdd_label_text = "HDD персонажи"
            if hasattr(self.win, 'lang') and 'ModelsWindow' in self.win.lang:
                hdd_label_text = self.win.lang['ModelsWindow'].get('HDDTitle', hdd_label_text)

            hdd_label = QLabel(hdd_label_text)
            hdd_label.setStyleSheet("""
                font-weight: bold;
                color: #ff9800;
                font-size: 14px;
                padding: 10px 0 5px 0;
            """)
            self.scroll_layout.addWidget(hdd_label, row, 0, 1, max_cols)
            row += 1

            for orig_name in hdd_names:
                if col >= max_cols:
                    row += 1
                    col = 0
                btn = create_character_button(orig_name, is_hdd=True)
                self.scroll_layout.addWidget(btn, row, col)
                col += 1

    def on_character_selected(self, character_name: str):
        """Обработчик выбора персонажа с защитой от спама"""
        normalized_name = character_name.replace(" ", "")

        if hasattr(self.win, 'lang') and 'Names' in self.win.lang:
            display_name = self.win.lang['Names'].get(normalized_name, character_name)
        else:
            display_name = character_name

        if not self.can_select:
            # print("Выбор временно заблокирован")
            self.show_message(f"⏳ {self.win.lang['ModelsWindow']['DelayMessage']}",
                              is_error=True,
                              type_error="can_select",
                              duration=5000)
            return

        # print(f"Выбран персонаж: {character_name}")

        if self.win.character_lock:
            return

        if self.win.input_handler.input_lock:
            # print("Input locked")
            self.show_message(f"🔒 {self.win.lang['ModelsWindow']['InputLockMessage']}",
                              is_error=True,
                              type_error="input_lock")
            return

        if self.win.settings_lock:
            # print("Settings locked")
            self.win.character.state.set_character_lock_state()
            self.show_message(f"⚙️ {self.win.lang['ModelsWindow']['SettingsLockMessage']}",
                              is_error=True,
                              type_error="settings_lock")
            return

        if hasattr(self.win, 'character_name') and self.win.character_name == character_name:
            # print(f"Персонаж {character_name} уже выбран")
            self.win.character.state.already_changed_character()
            self.show_message(f"✨ {display_name} {self.win.lang['ModelsWindow']['AlreadyChangedMessage']}",
                              is_info=True)
            return

        self.can_select = False

        self.selection_timer.start(7000)

        #self.set_buttons_enabled(False)

        self.show_message(f"✅ {self.win.lang['ModelsWindow']['CharacterSelectedMessage']} {display_name}",
                          is_success=True)

        self.win.talk_widget.talk_update = False

        self.win.model_move = True
        self.win.character.state.set_goodbye_state()

        # Устанавливаем нового персонажа
        self.win.character_name = character_name

        # print(f"Персонаж успешно изменен на: {character_name}")

    def allow_selection(self):
        """Разрешает выбор персонажа"""
        self.can_select = True
        self.set_buttons_enabled(True)
        if self.type_error == "can_select":
            self.show_message(f"✨ {self.win.lang['ModelsWindow']['AllowSelectionMessage']}",
                              is_info=True, duration=1500)
            self.type_error == ""
        # print("Выбор снова разрешен")

    def set_buttons_enabled(self, enabled: bool):
        """Включает/отключает все кнопки"""
        for button in self.findChildren(CharacterButton):
            button.setEnabled(enabled)

    def show_message(self, text: str, is_error: bool = False, type_error: str = "", is_success: bool = False,
                     is_info: bool = False, duration: int = 2000):
        """Показывает сообщение в окне"""
        if self.message_timer.isActive():
            self.message_timer.stop()

        self.message_label.setText(text)
        self.type_error = type_error

        if is_error:
            self.is_error = True
            self.message_label.setStyleSheet("""
                QLabel {
                    background-color: #f44336;
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 8px;
                    border-radius: 5px;
                    margin: 5px;
                }
            """)
        elif is_success:
            self.message_label.setStyleSheet("""
                QLabel {
                    background-color: #4CAF50;
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 8px;
                    border-radius: 5px;
                    margin: 5px;
                }
            """)
        else:  # info
            self.message_label.setStyleSheet("""
                QLabel {
                    background-color: #2196F3;
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 8px;
                    border-radius: 5px;
                    margin: 5px;
                }
            """)

        self.message_label.show()

        self.message_timer.start(duration)

    def hide_message(self):
        """Скрывает сообщение"""
        self.message_label.hide()

    def clear_layout(self, layout):
        """Очищает layout от всех виджетов"""
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())

    def show_with_filter(self, show_hdd: bool = True):
        """Показывает окно с возможностью фильтрации HDD персонажей"""
        self.load_characters(show_hdd)
        self.show()

class CharacterButton(QFrame):
    """Кнопка с анимацией при нажатии и задержкой возврата"""
    clicked = Signal(str)

    def __init__(self, character_name: str, image_path: Optional[str] = None,
                 is_hdd: bool = False, orig_name: Optional[str] = None, parent=None):
        super().__init__(parent)

        self.character_name = character_name
        self.display_name = character_name
        self.orig_name = orig_name or character_name
        self.image_path = image_path
        self.is_hdd = is_hdd
        self.is_pressed = False
        self.pressed_image_path = None
        self.return_timer = QTimer()
        self.return_timer.setSingleShot(True)
        self.return_timer.timeout.connect(self.return_to_normal)

        if image_path:
            base, ext = os.path.splitext(image_path)
            self.pressed_image_path = f"{base}_push{ext}"

        self.setFixedSize(140, 160)
        self.setCursor(Qt.PointingHandCursor)

        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(100)
        self.animation.setEasingCurve(QEasingCurve.OutQuad)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)

        self.image_container = QLabel()
        self.image_container.setFixedSize(120, 120)
        self.image_container.setAlignment(Qt.AlignCenter)

        self.name_label = QLabel(character_name)
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setWordWrap(True)
        self.name_label.setStyleSheet("""
            font-weight: bold;
            color: #333;
            font-size: 12px;
            padding: 2px;
            background-color: transparent;
        """)

        layout.addWidget(self.image_container)
        layout.addWidget(self.name_label)

        self.set_normal_image()

        self.update_style(normal=True)

    def get_base_style(self, normal: bool = True) -> str:
        """Возвращает базовый стиль в зависимости от типа персонажа"""
        if self.is_hdd:
            base_style = """
                CharacterButton {
                    background-color: #fff3e0;
                    border: 2px solid #ff9800;
                    border-radius: 12px;
                }
                CharacterButton:hover {
                    background-color: #ffe0b2;
                    border-color: #f57c00;
                }
            """
        else:
            base_style = """
                CharacterButton {
                    background-color: #f5f5f5;
                    border: 2px solid #ddd;
                    border-radius: 12px;
                }
                CharacterButton:hover {
                    background-color: #e8e8e8;
                    border-color: #2196F3;
                }
            """

        if normal:
            return base_style
        else:
            return base_style + """
                CharacterButton {
                    background-color: #d0d0d0;
                }
            """

    def update_style(self, normal: bool = True):
        """Обновляет стиль кнопки"""
        self.setStyleSheet(self.get_base_style(normal))

    def set_normal_image(self):
        """Устанавливает обычное изображение"""
        if self.image_path and os.path.exists(self.image_path):
            pixmap = QPixmap(self.image_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    110, 110,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.image_container.setPixmap(scaled_pixmap)
                self.image_container.setStyleSheet("")
                return

        self.set_placeholder_image()

    def set_pressed_image(self):
        """Устанавливает изображение для нажатого состояния"""
        if self.pressed_image_path and os.path.exists(self.pressed_image_path):
            pixmap = QPixmap(self.pressed_image_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    110, 110,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.image_container.setPixmap(scaled_pixmap)
                return

        # Если нет изображения для нажатия, используем обычное с эффектом
        self.set_normal_image()
        self.image_container.setStyleSheet("""
            QLabel {
                opacity: 0.7;
            }
        """)

    def set_placeholder_image(self):
        """Устанавливает заглушку для изображения"""
        self.image_container.setText(self.character_name[0] if self.character_name else "?")

        if self.is_hdd:
            bg_color = "#ffe0b2"
            text_color = "#f57c00"
        else:
            bg_color = "#e0e0e0"
            text_color = "#666"

        self.image_container.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                border-radius: 10px;
                font-size: 48px;
                font-weight: bold;
                color: {text_color};
                qproperty-alignment: AlignCenter;
            }}
        """)

    def return_to_normal(self):
        """Возвращает кнопку в обычное состояние после задержки"""
        self.is_pressed = False
        self.set_normal_image()

        # Анимация возврата
        self.animation.setDirection(QPropertyAnimation.Backward)
        self.animation.start()

        # Возвращаем обычный стиль
        self.update_style(normal=True)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.is_pressed:
            self.is_pressed = True
            self.set_pressed_image()

            self.animation.setStartValue(self.pos())
            self.animation.setEndValue(self.pos() + QPoint(2, 2))
            self.animation.start()

            self.update_style(normal=False)

            self.return_timer.start(1500)

            self.clicked.emit(self.orig_name)

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        """Если мышь ушла с кнопки во время нажатия"""
        if self.is_pressed and not self.rect().contains(event.pos()):
            self.is_pressed = False
            self.return_timer.stop()
            self.set_normal_image()
            self.update_style(normal=True)
            self.animation.stop()
            self.move(self.animation.startValue())
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        """Когда курсор покидает виджет"""
        super().leaveEvent(event)