"""
NEO CODE — QApplication bootstrap.
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt

from neo_code.ui.main_window import MainWindow


class NeoCodeApp(QApplication):
    def __init__(self, argv: list[str]) -> None:
        super().__init__(argv)
        self.setApplicationName("NEO Code")
        self.setOrganizationName("ThingEdu")
        self._apply_dark_theme()

        # Start the execution runner (listens to event_bus internally)
        from neo_code.execution.runner import Runner
        self._runner = Runner()

        self._window = MainWindow()
        self._window.show()

    def _apply_dark_theme(self) -> None:
        self.setStyle("Fusion")
        palette = QPalette()
        dark = QColor(30, 30, 46)        # #1E1E2E  base
        mid_dark = QColor(49, 50, 68)    # #313244  surface
        highlight = QColor(137, 180, 250) # #89B4FA  blue
        text = QColor(205, 214, 244)     # #CDD6F4  text
        dim_text = QColor(108, 112, 134) # #6C7086  subtext

        palette.setColor(QPalette.ColorRole.Window, dark)
        palette.setColor(QPalette.ColorRole.WindowText, text)
        palette.setColor(QPalette.ColorRole.Base, mid_dark)
        palette.setColor(QPalette.ColorRole.AlternateBase, dark)
        palette.setColor(QPalette.ColorRole.ToolTipBase, dark)
        palette.setColor(QPalette.ColorRole.ToolTipText, text)
        palette.setColor(QPalette.ColorRole.Text, text)
        palette.setColor(QPalette.ColorRole.Button, mid_dark)
        palette.setColor(QPalette.ColorRole.ButtonText, text)
        palette.setColor(QPalette.ColorRole.BrightText, QColor("white"))
        palette.setColor(QPalette.ColorRole.Highlight, highlight)
        palette.setColor(QPalette.ColorRole.HighlightedText, dark)
        palette.setColor(QPalette.ColorRole.PlaceholderText, dim_text)
        self.setPalette(palette)

