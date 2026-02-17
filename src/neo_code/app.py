"""NEO CODE application entry point."""

import sys
import logging

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from neo_code.ui.main_window import MainWindow
from neo_code.core.code_analyzer import CodeAnalyzerWorker
from neo_code.utils.signal_bus import SignalBus
from neo_code.config.settings import get_settings


def setup_logging() -> None:
    """Configure application logging."""
    log_dir = get_settings().storage.database_path.replace("neo_code.db", "")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
        ],
    )


def main() -> None:
    """Main entry point for NEO CODE application."""
    setup_logging()
    logger = logging.getLogger("neo_code")
    logger.info("Starting NEO CODE...")

    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("NEO CODE")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("NEO TRE")

    # Initialize signal bus
    bus = SignalBus.instance()

    # Create and setup code analyzer
    analyzer = CodeAnalyzerWorker()
    bus.code_changed.connect(analyzer.analyze)
    analyzer.analysis_complete.connect(bus.analysis_complete.emit)

    # Create main window
    window = MainWindow()
    window.show()

    logger.info("NEO CODE ready!")

    # Run event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
