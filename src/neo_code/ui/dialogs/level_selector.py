"""Level selector dialog for choosing difficulty level."""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget,
    QGraphicsDropShadowEffect,
)


LEVELS = [
    {
        "number": 1,
        "name": "Kham pha",
        "name_en": "Explorer",
        "age": "6-8",
        "icon": "🌱",
        "color": "#a6e3a1",
        "description": "Code gan nhu day du, chi thay 1-2 gia tri.\nPhu hop cho nguoi moi bat dau.",
        "description_en": "Nearly complete code, just change 1-2 values.\nPerfect for beginners.",
    },
    {
        "number": 2,
        "name": "Lap trinh vien",
        "name_en": "Programmer",
        "age": "9-11",
        "icon": "🚀",
        "color": "#89b4fa",
        "description": "Phan quan trong de trong (___), co goi y.\nThach thuc vua phai.",
        "description_en": "Key parts blanked out (___), with hints.\nModerate challenge.",
    },
    {
        "number": 3,
        "name": "Chuyen gia",
        "name_en": "Expert",
        "age": "12+",
        "icon": "⭐",
        "color": "#f9e2af",
        "description": "Chi co mo ta nhiem vu va khung code.\nTu suy nghi va viet code!",
        "description_en": "Only task description and code skeleton.\nThink and write code yourself!",
    },
]


class LevelCard(QWidget):
    """A clickable card representing a difficulty level."""

    clicked = pyqtSignal(int)  # emits level number

    def __init__(self, level_info: dict, parent: QWidget | None = None):
        super().__init__(parent)
        self._level = level_info["number"]
        self._color = level_info["color"]
        self._selected = False
        self._setup_ui(level_info)

    def _setup_ui(self, info: dict) -> None:
        self.setFixedSize(200, 220)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._update_style(hover=False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Icon
        icon_label = QLabel(info["icon"])
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("font-size: 36px; background: transparent;")
        layout.addWidget(icon_label)

        # Level number + name
        name_label = QLabel(f"Level {info['number']}")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet(
            f"font-size: 18px; font-weight: bold; color: {info['color']}; background: transparent;"
        )
        layout.addWidget(name_label)

        subtitle = QLabel(info["name"])
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"font-size: 14px; color: {info['color']}; background: transparent;")
        layout.addWidget(subtitle)

        # Age range
        age_label = QLabel(f"({info['age']} tuoi)")
        age_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        age_label.setStyleSheet("font-size: 11px; color: #6c7086; background: transparent;")
        layout.addWidget(age_label)

        # Description
        desc_label = QLabel(info["description"])
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("font-size: 11px; color: #a6adc8; background: transparent;")
        layout.addWidget(desc_label)

        layout.addStretch()

    def _update_style(self, hover: bool = False, selected: bool = False) -> None:
        border_color = self._color if (hover or selected) else "#45475a"
        bg = "#313244" if (hover or selected) else "#1e1e2e"
        border_width = 2 if selected else 1
        self.setStyleSheet(
            f"LevelCard {{ background-color: {bg}; border: {border_width}px solid {border_color}; "
            f"border-radius: 12px; }}"
        )

    def set_selected(self, selected: bool) -> None:
        self._selected = selected
        self._update_style(selected=selected)

    def enterEvent(self, event) -> None:
        if not self._selected:
            self._update_style(hover=True)

    def leaveEvent(self, event) -> None:
        self._update_style(selected=self._selected)

    def mousePressEvent(self, event) -> None:
        self.clicked.emit(self._level)


class LevelSelectorDialog(QDialog):
    """Dialog for selecting difficulty level."""

    level_selected = pyqtSignal(int)  # emits chosen level (1, 2, or 3)

    def __init__(self, current_level: int = 1, parent: QWidget | None = None):
        super().__init__(parent)
        self._current_level = current_level
        self._chosen_level = current_level
        self._cards: list[LevelCard] = []
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setWindowTitle("Chon cap do")
        self.setFixedSize(680, 380)
        self.setStyleSheet("""
            QDialog {
                background-color: #11111b;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Title
        title = QLabel("Ban muon hoc o cap do nao?")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #cdd6f4;"
        )
        layout.addWidget(title)

        # Cards row
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)
        cards_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        for level_info in LEVELS:
            card = LevelCard(level_info, self)
            card.clicked.connect(self._on_card_clicked)
            if level_info["number"] == self._current_level:
                card.set_selected(True)
            self._cards.append(card)
            cards_layout.addWidget(card)

        layout.addLayout(cards_layout)

        # Buttons row
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_layout.setSpacing(12)

        self._ok_btn = QPushButton("Chon")
        self._ok_btn.setFixedSize(120, 36)
        self._ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #89b4fa;
                color: #1e1e2e;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #b4d0fb;
            }
        """)
        self._ok_btn.clicked.connect(self._on_ok)
        btn_layout.addWidget(self._ok_btn)

        cancel_btn = QPushButton("Huy")
        cancel_btn.setFixedSize(120, 36)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45475a;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def _on_card_clicked(self, level: int) -> None:
        self._chosen_level = level
        for card in self._cards:
            card.set_selected(card._level == level)

    def _on_ok(self) -> None:
        self.level_selected.emit(self._chosen_level)
        self.accept()

    def chosen_level(self) -> int:
        return self._chosen_level
