"""
Sidebar — activity bar + content panel navigation.

Layout:
  ┌────┬──────────────────┐
  │ ▲  │                  │
  │Nav │  Content Panel   │
  │Bar │  (QStackedWidget)│
  │    │                  │
  │ ▼  │                  │
  └────┴──────────────────┘

The activity bar is a narrow strip of NavButtons (icon + label).
Clicking the active button collapses the panel (toggle).
"""

from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget,
    QPushButton, QLabel, QSizePolicy, QFrame, QToolButton,
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QFont

from dataclasses import dataclass

from neo_code.core.extension_interface import IFeature
from neo_code.theme.colors import colors


# ── Data ──────────────────────────────────────────────────────────────────────

@dataclass
class NavEntry:
    key: str
    icon: str       # Unicode symbol or emoji
    label: str
    widget: QWidget


# ── Activity bar button ───────────────────────────────────────────────────────

class _NavButton(QPushButton):
    """Icon + label stacked vertically, styled like an activity-bar item."""

    _STYLE_INACTIVE = f"""
        QPushButton {{
            background: transparent;
            border: none;
            color: {colors.activity_bar_icon};
            padding: 10px 0px;
        }}
        QPushButton:hover {{
            color: {colors.activity_bar_icon_hl};
            background-color: {colors.surface_alt};
        }}
    """
    _STYLE_ACTIVE = f"""
        QPushButton {{
            background: transparent;
            border-left: 3px solid {colors.activity_bar_active};
            border-right: none;
            border-top: none;
            border-bottom: none;
            color: {colors.activity_bar_icon_hl};
            padding: 10px 0px;
        }}
    """

    def __init__(self, icon: str, label: str) -> None:
        super().__init__()
        self.setFixedWidth(56)
        self.setCheckable(True)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(label)

        # Stack icon + label vertically inside the button
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(2)
        layout.setAlignment(Qt.AlignCenter)

        icon_lbl = QLabel(icon)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_font = QFont()
        icon_font.setPointSize(18)
        icon_lbl.setFont(icon_font)
        icon_lbl.setAttribute(Qt.WA_TransparentForMouseEvents)
        layout.addWidget(icon_lbl)

        text_lbl = QLabel(label)
        text_lbl.setAlignment(Qt.AlignCenter)
        text_font = QFont()
        text_font.setPointSize(8)
        text_lbl.setFont(text_font)
        text_lbl.setAttribute(Qt.WA_TransparentForMouseEvents)
        layout.addWidget(text_lbl)

        # Keep child label colours in sync with button state
        self._icon_lbl = icon_lbl
        self._text_lbl = text_lbl
        self._set_active(False)

    def _set_active(self, active: bool) -> None:
        color = "#CDD6F4" if active else "#6C7086"
        self._icon_lbl.setStyleSheet(f"color: {color};")
        self._text_lbl.setStyleSheet(f"color: {color};")
        self.setStyleSheet(self._STYLE_ACTIVE if active else self._STYLE_INACTIVE)

    def setChecked(self, checked: bool) -> None:
        super().setChecked(checked)
        self._set_active(checked)


# ── Activity bar ──────────────────────────────────────────────────────────────

class _ActivityBar(QWidget):
    """Narrow vertical strip of nav buttons."""

    nav_selected = pyqtSignal(str)   # key of selected entry
    nav_toggled = pyqtSignal()        # same key clicked again → collapse

    def __init__(self) -> None:
        super().__init__()
        self.setFixedWidth(56)
        self.setStyleSheet(f"background-color: {colors.activity_bar_bg};")

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 8, 0, 8)
        self._layout.setSpacing(0)
        self._layout.setAlignment(Qt.AlignTop)

        self._buttons: dict[str, _NavButton] = {}
        self._active_key: str | None = None

    def add_entry(self, key: str, icon: str, label: str) -> None:
        btn = _NavButton(icon, label)
        btn.clicked.connect(lambda _checked, k=key: self._on_clicked(k))
        self._buttons[key] = btn
        self._layout.addWidget(btn)

    def _on_clicked(self, key: str) -> None:
        if self._active_key == key:
            # Toggle off
            self._active_key = None
            self._buttons[key].setChecked(False)
            self.nav_toggled.emit()
        else:
            if self._active_key and self._active_key in self._buttons:
                self._buttons[self._active_key].setChecked(False)
            self._active_key = key
            self._buttons[key].setChecked(True)
            self.nav_selected.emit(key)

    def set_active(self, key: str) -> None:
        self._on_clicked(key)


# ── Content panel ─────────────────────────────────────────────────────────────

class _ContentPanel(QWidget):
    """Collapsible panel that shows the widget for the active nav entry."""

    _EXPANDED_WIDTH = 240

    def __init__(self) -> None:
        super().__init__()
        self.setFixedWidth(self._EXPANDED_WIDTH)
        self.setStyleSheet(
            f"background-color: {colors.panel_bg};"
            f"border-right: 1px solid {colors.border};"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Title bar
        header = QWidget()
        header.setFixedHeight(32)
        header.setStyleSheet(
            f"background-color: {colors.panel_header_bg};"
        )
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(6, 0, 6, 0)
        header_layout.setSpacing(4)

        self._back_btn = QToolButton()
        self._back_btn.setText("←")
        self._back_btn.setVisible(False)
        self._back_btn.setFixedSize(22, 22)
        self._back_btn.setStyleSheet(
            f"color: {colors.panel_header_text};"
            "border: none;"
            "border-radius: 3px;"
            "font-size: 14px;"
        )
        self._back_btn.clicked.connect(self._on_back_clicked)
        header_layout.addWidget(self._back_btn)

        self._title = QLabel("")
        self._title.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        title_font = QFont()
        title_font.setPointSize(9)
        title_font.setBold(True)
        self._title.setFont(title_font)
        self._title.setStyleSheet(
            f"color: {colors.panel_header_text};"
        )
        header_layout.addWidget(self._title)
        header_layout.addStretch()
        layout.addWidget(header)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #313244;")
        layout.addWidget(sep)

        self._stack = QStackedWidget()
        self._stack.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._stack)

        self._entries: dict[str, int] = {}   # key → stack index
        self._back_callback = None

    def add_entry(self, entry: NavEntry) -> None:
        idx = self._stack.addWidget(entry.widget)
        self._entries[entry.key] = idx

    def show_entry(self, key: str, label: str) -> None:
        if key in self._entries:
            self._stack.setCurrentIndex(self._entries[key])
            self._title.setText(label.upper())
        self.setFixedWidth(self._EXPANDED_WIDTH)
        self.setVisible(True)

    def collapse(self) -> None:
        self.setFixedWidth(0)
        self.setVisible(False)

    def set_back_button(self, visible: bool, callback=None, tooltip: str = "Quay lại") -> None:
        self._back_callback = callback
        self._back_btn.setVisible(visible)
        self._back_btn.setToolTip(tooltip)

    def _on_back_clicked(self) -> None:
        if callable(self._back_callback):
            self._back_callback()


# ── Public SidebarPanel ───────────────────────────────────────────────────────

class SidebarPanel(QWidget):
    """
    Activity bar + content panel.

    Usage:
        sidebar.add_feature(feature, key="lessons", icon="📖", label="Lessons")
        sidebar.add_feature(feature, key="turtle",  icon="🐢", label="Turtle")
        sidebar.set_active("lessons")   # optional default
    """

    active_changed = pyqtSignal(object)

    def __init__(self) -> None:
        super().__init__()
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._activity_bar = _ActivityBar()
        self._content = _ContentPanel()
        self._content.collapse()   # start collapsed

        layout.addWidget(self._activity_bar)
        layout.addWidget(self._content)

        self._entries: dict[str, NavEntry] = {}

        self._activity_bar.nav_selected.connect(self._on_nav_selected)
        self._activity_bar.nav_toggled.connect(self._on_nav_toggled)

    # ── Public API ────────────────────────────────────────────────────────────

    def add_nav_widget(self, key: str, icon: str, label: str, widget: QWidget) -> None:
        """Register a plain widget (not necessarily from a feature)."""
        entry = NavEntry(key=key, icon=icon, label=label, widget=widget)
        self._entries[key] = entry
        self._activity_bar.add_entry(key, icon, label)
        self._content.add_entry(entry)

    def add_feature(self, feature: IFeature, key: str, icon: str, label: str) -> None:
        """Register a feature's sidebar widget."""
        widget = feature.get_sidebar_widget()
        if widget is not None:
            self.add_nav_widget(key, icon, label, widget)

    def set_header_back(self, visible: bool, callback=None) -> None:
        self._content.set_back_button(visible, callback)

    def set_active(self, key: str) -> None:
        self._activity_bar.set_active(key)

    # ── Internal ──────────────────────────────────────────────────────────────

    def _on_nav_selected(self, key: str) -> None:
        entry = self._entries.get(key)
        if entry:
            self._content.show_entry(key, entry.label)
            self.active_changed.emit(key)

    def _on_nav_toggled(self) -> None:
        self._content.collapse()
        self.active_changed.emit(None)
