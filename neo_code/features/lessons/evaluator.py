from neo_code.features.lessons.feedback_mapper import (
    map_error_feedback,
    map_mismatch_feedback,
    map_success_feedback,
)


def _normalize(text: str) -> str:
    lines = [line.rstrip() for line in text.strip().splitlines()]
    return "\n".join(lines).strip()


def evaluate_lesson(challenge: dict, stdout: str, stderr: str, exit_code: int) -> tuple[bool, str]:
    if exit_code != 0 or stderr.strip():
        return False, map_error_feedback(stderr, exit_code)

    expected = challenge.get("expected_output")
    if expected:
        if _normalize(stdout) == _normalize(expected):
            return True, map_success_feedback(challenge)
        return False, map_mismatch_feedback(challenge)

    return True, map_success_feedback(challenge)
