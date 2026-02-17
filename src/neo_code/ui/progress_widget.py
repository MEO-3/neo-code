"""Student progress display widget."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QHBoxLayout

from neo_code.core.models import StudentProfile
from neo_code.ui.theme import COLORS


class ProgressWidget(QWidget):
    """Displays student's current phase, lesson, and skill progress."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(6)

        self.setStyleSheet(f"""
            ProgressWidget {{
                background-color: {COLORS['bg_secondary']};
                border-top: 1px solid {COLORS['border']};
            }}
        """)

        # Phase & Lesson
        info_row = QHBoxLayout()
        self._phase_label = QLabel("Phase 1: Python & Turtle")
        self._phase_label.setStyleSheet(f"color: {COLORS['accent']}; font-weight: bold; font-size: 12px;")
        info_row.addWidget(self._phase_label)

        self._lesson_label = QLabel("Lesson 1")
        self._lesson_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        info_row.addWidget(self._lesson_label)
        info_row.addStretch()

        self._skill_label = QLabel("Skill: 1/5")
        self._skill_label.setStyleSheet(f"color: {COLORS['warning']}; font-size: 12px;")
        info_row.addWidget(self._skill_label)

        layout.addLayout(info_row)

        # Progress bar
        self._progress_bar = QProgressBar(self)
        self._progress_bar.setFixedHeight(8)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setValue(0)
        layout.addWidget(self._progress_bar)

        # Stats row
        stats_row = QHBoxLayout()
        self._runs_label = QLabel("Runs: 0")
        self._runs_label.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 11px;")
        stats_row.addWidget(self._runs_label)

        self._fixes_label = QLabel("Errors fixed: 0")
        self._fixes_label.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 11px;")
        stats_row.addWidget(self._fixes_label)
        stats_row.addStretch()

        layout.addLayout(stats_row)

    def update_profile(self, profile: StudentProfile) -> None:
        """Update display with student profile data."""
        phase_names = {1: "Python & Turtle", 2: "IoT & Sensors"}
        phase_name = phase_names.get(profile.current_phase, f"Phase {profile.current_phase}")
        self._phase_label.setText(f"Phase {profile.current_phase}: {phase_name}")
        self._lesson_label.setText(f"Lesson {profile.current_lesson}")
        self._skill_label.setText(f"Skill: {profile.skill_level}/5")
        self._runs_label.setText(f"Runs: {profile.total_code_runs}")
        self._fixes_label.setText(f"Errors fixed: {profile.total_errors_fixed}")

        # Calculate progress
        total_exercises = 10  # per phase, adjust based on curriculum
        completed = len(profile.exercises_completed)
        pct = min(int(completed / total_exercises * 100), 100) if total_exercises > 0 else 0
        self._progress_bar.setValue(pct)
