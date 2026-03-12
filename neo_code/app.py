"""
NEO Code — QApplication bootstrap.
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor

from neo_code.ui.main_window import MainWindow
from neo_code.theme.colors import colors


class NeoCodeApp(QApplication):
    def __init__(self, argv: list[str]) -> None:
        super().__init__(argv)
        self.setApplicationName("NEO Code")
        self.setOrganizationName("ThingEdu")
        self._apply_theme()

        from neo_code.execution.runner import Runner
        self._runner = Runner()

        self._window = MainWindow()
        self._window.show()

    def _apply_theme(self) -> None:
        self.setStyle("Fusion")
        palette = QPalette()
        c = colors

        palette.setColor(QPalette.ColorRole.Window,          QColor(c.surface))
        palette.setColor(QPalette.ColorRole.WindowText,      QColor(c.text))
        palette.setColor(QPalette.ColorRole.Base,            QColor(c.background))
        palette.setColor(QPalette.ColorRole.AlternateBase,   QColor(c.surface_alt))
        palette.setColor(QPalette.ColorRole.ToolTipBase,     QColor(c.background))
        palette.setColor(QPalette.ColorRole.ToolTipText,     QColor(c.text))
        palette.setColor(QPalette.ColorRole.Text,            QColor(c.text))
        palette.setColor(QPalette.ColorRole.Button,          QColor(c.surface))
        palette.setColor(QPalette.ColorRole.ButtonText,      QColor(c.text))
        palette.setColor(QPalette.ColorRole.BrightText,      QColor("#FFFFFF"))
        palette.setColor(QPalette.ColorRole.Highlight,       QColor(c.primary))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(c.primary_text))
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(c.text_secondary))
        palette.setColor(QPalette.ColorRole.Mid,             QColor(c.border))
        palette.setColor(QPalette.ColorRole.Dark,            QColor(c.surface_alt))
        self.setPalette(palette)
