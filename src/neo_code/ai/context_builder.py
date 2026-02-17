"""Builds LLM context from code, analysis results, and student profile."""

from neo_code.core.models import (
    AnalysisResult, CodeError, CodePattern, ErrorSeverity,
    ExecutionResult, StudentProfile, HintLevel,
)
from neo_code.ai.prompt_templates import (
    SYSTEM_PROMPT_PHASE1, SYSTEM_PROMPT_PHASE2,
    ERROR_CONTEXT_TEMPLATE, PROACTIVE_GUIDANCE_TEMPLATE,
    MANUAL_QUESTION_TEMPLATE, EXECUTION_ERROR_TEMPLATE,
    ENCOURAGEMENT_TEMPLATE,
)
from neo_code.config.settings import get_settings


class ContextBuilder:
    """Builds structured prompts from code, errors, phase, and student level."""

    def __init__(self):
        self._settings = get_settings()

    def get_system_prompt(self, phase: int = 1) -> str:
        """Get the system prompt for the current educational phase."""
        if phase == 2:
            return SYSTEM_PROMPT_PHASE2
        return SYSTEM_PROMPT_PHASE1

    def build_error_context(
        self,
        code: str,
        analysis: AnalysisResult,
        profile: StudentProfile,
        hint_level: str = "guidance",
    ) -> str:
        """Build context for an error explanation."""
        if not analysis.errors:
            return ""

        error = analysis.errors[0]  # Focus on the first error

        # Count how often this error type has occurred
        error_type = error.error_code or "unknown"
        error_freq = profile.common_error_patterns.get(error_type, 0)

        error_details = "\n".join(
            f"  - Line {e.line}: {e.message} ({e.severity.name})"
            for e in analysis.errors
        )

        patterns_str = ", ".join(p.name for p in analysis.patterns) or "none"

        return ERROR_CONTEXT_TEMPLATE.format(
            code=self._truncate_code(code),
            error_count=len(analysis.errors),
            error_details=error_details,
            patterns=patterns_str,
            skill_level=profile.skill_level,
            lesson_name=f"Phase {profile.current_phase}, Lesson {profile.current_lesson}",
            error_frequency=error_freq,
            error_type=error_type,
            line_number=error.line,
            error_message=error.message,
            hint_level=hint_level,
        )

    def build_proactive_context(
        self,
        code: str,
        analysis: AnalysisResult,
        profile: StudentProfile,
    ) -> str:
        """Build context for proactive guidance (no errors)."""
        patterns_str = ", ".join(p.name for p in analysis.patterns) or "none"
        detected_intent = self._detect_intent(analysis)

        return PROACTIVE_GUIDANCE_TEMPLATE.format(
            code=self._truncate_code(code),
            patterns=patterns_str,
            skill_level=profile.skill_level,
            lesson_name=f"Phase {profile.current_phase}, Lesson {profile.current_lesson}",
            detected_intent=detected_intent,
        )

    def build_question_context(
        self,
        question: str,
        code: str,
        analysis: AnalysisResult,
        profile: StudentProfile,
    ) -> str:
        """Build context for a manual student question."""
        analysis_summary = "No errors." if not analysis.errors else (
            f"{len(analysis.errors)} errors found: " +
            ", ".join(f"Line {e.line}: {e.message}" for e in analysis.errors[:3])
        )

        return MANUAL_QUESTION_TEMPLATE.format(
            question=question,
            code=self._truncate_code(code),
            analysis_summary=analysis_summary,
            skill_level=profile.skill_level,
            phase=profile.current_phase,
        )

    def build_execution_error_context(
        self,
        code: str,
        result: ExecutionResult,
    ) -> str:
        """Build context for a runtime error."""
        return EXECUTION_ERROR_TEMPLATE.format(
            code=self._truncate_code(code),
            return_code=result.return_code,
            stderr=result.stderr[:500],
        )

    def build_encouragement_context(
        self,
        code: str,
        error_type: str,
        fix_count: int,
        profile: StudentProfile,
    ) -> str:
        """Build context for positive reinforcement."""
        return ENCOURAGEMENT_TEMPLATE.format(
            code=self._truncate_code(code),
            error_type=error_type,
            fix_count=fix_count,
            skill_level=profile.skill_level,
        )

    def _truncate_code(self, code: str) -> str:
        """Truncate code to fit within context window."""
        max_lines = self._settings.ai.context.max_code_lines
        lines = code.splitlines()
        if len(lines) > max_lines:
            return "\n".join(lines[:max_lines]) + f"\n# ... ({len(lines) - max_lines} more lines)"
        return code

    def _detect_intent(self, analysis: AnalysisResult) -> str:
        """Detect what the student is trying to do based on patterns."""
        intents = []
        pattern_intents = {
            CodePattern.TURTLE_DRAWING: "turtle graphics drawing",
            CodePattern.LOOP_CONSTRUCT: "using loops",
            CodePattern.FUNCTION_DEFINITION: "defining functions",
            CodePattern.GPIO_SETUP: "GPIO/hardware setup",
            CodePattern.SENSOR_READ: "reading sensor data",
            CodePattern.CONDITIONAL: "conditional logic",
            CodePattern.LIST_USAGE: "working with lists",
            CodePattern.CLASS_DEFINITION: "defining classes",
        }
        for pattern in analysis.patterns:
            if pattern in pattern_intents:
                intents.append(pattern_intents[pattern])

        return ", ".join(intents) if intents else "general Python programming"
