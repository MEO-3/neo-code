"""
NEO Code — QApplication bootstrap.
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPalette, QColor

from neo_code.ui.main_window import MainWindow
from neo_code.theme.colors import colors
from neo_code.core.settings import Settings


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

        self._start_update_check()

    def _start_update_check(self) -> None:
        settings = Settings()
        if not settings.auto_check_update:
            return
        from neo_code.core.updater import UpdateChecker
        from neo_code.core.event_bus import event_bus

        self._update_checker = UpdateChecker(self)
        self._update_checker.update_available.connect(event_bus.update_available)
        self._update_checker.check()

    def _apply_theme(self) -> None:
        self.setStyle("Fusion")
        palette = QPalette()
        c = colors

        palette.setColor(QPalette.Window,          QColor(c.surface))
        palette.setColor(QPalette.WindowText,      QColor(c.text))
        palette.setColor(QPalette.Base,            QColor(c.background))
        palette.setColor(QPalette.AlternateBase,   QColor(c.surface_alt))
        palette.setColor(QPalette.ToolTipBase,     QColor(c.background))
        palette.setColor(QPalette.ToolTipText,     QColor(c.text))
        palette.setColor(QPalette.Text,            QColor(c.text))
        palette.setColor(QPalette.Button,          QColor(c.surface))
        palette.setColor(QPalette.ButtonText,      QColor(c.text))
        palette.setColor(QPalette.BrightText,      QColor("#FFFFFF"))
        palette.setColor(QPalette.Highlight,       QColor(c.primary))
        palette.setColor(QPalette.HighlightedText, QColor(c.primary_text))
        palette.setColor(QPalette.PlaceholderText, QColor(c.text_secondary))
        palette.setColor(QPalette.Mid,             QColor(c.border))
        palette.setColor(QPalette.Dark,            QColor(c.surface_alt))
        self.setPalette(palette)
