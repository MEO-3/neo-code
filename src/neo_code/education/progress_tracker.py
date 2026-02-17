"""Student progress tracking and skill assessment."""

from neo_code.core.models import StudentProfile, ExecutionResult


class ProgressTracker:
    """Tracks student progress and adjusts skill level."""

    def __init__(self, profile: StudentProfile):
        self._profile = profile

    @property
    def profile(self) -> StudentProfile:
        return self._profile

    def record_code_run(self, result: ExecutionResult) -> None:
        """Record a code execution event."""
        self._profile.total_code_runs += 1

    def record_error(self, error_code: str) -> None:
        """Record an error occurrence."""
        count = self._profile.common_error_patterns.get(error_code, 0)
        self._profile.common_error_patterns[error_code] = count + 1

    def record_error_fixed(self, error_code: str) -> None:
        """Record that the student fixed a specific error type."""
        self._profile.total_errors_fixed += 1
        self._update_skill_level()

    def record_exercise_completed(self, exercise_id: str) -> None:
        """Record exercise completion."""
        if exercise_id not in self._profile.exercises_completed:
            self._profile.exercises_completed.append(exercise_id)
            self._update_skill_level()

    def get_completion_percentage(self) -> float:
        """Get overall completion percentage for current phase."""
        total = 10  # Adjust based on actual curriculum
        completed = len(self._profile.exercises_completed)
        return min(completed / total * 100, 100.0) if total > 0 else 0.0

    def get_error_frequency(self, error_code: str) -> int:
        """Get how often a specific error has occurred."""
        return self._profile.common_error_patterns.get(error_code, 0)

    def _update_skill_level(self) -> None:
        """Recalculate skill level based on progress metrics."""
        score = 0

        # Exercises completed
        exercises = len(self._profile.exercises_completed)
        if exercises >= 2:
            score += 1
        if exercises >= 5:
            score += 1
        if exercises >= 8:
            score += 1

        # Error fix ratio
        if self._profile.total_code_runs > 5:
            fix_ratio = self._profile.total_errors_fixed / max(self._profile.total_code_runs, 1)
            if fix_ratio > 0.3:
                score += 1

        # Total experience
        if self._profile.total_code_runs > 20:
            score += 1

        self._profile.skill_level = max(1, min(5, score))
