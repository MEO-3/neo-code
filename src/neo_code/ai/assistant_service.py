"""Main AI assistant service - orchestrates code analysis and LLM responses."""

import logging

from PyQt6.QtCore import QThread, pyqtSignal

from neo_code.core.models import (
    AnalysisResult, ExecutionResult, AIResponse, HintLevel, StudentProfile,
)
from neo_code.ai.llm_client import LLMClient
from neo_code.ai.context_builder import ContextBuilder
from neo_code.ai.response_parser import parse_response
from neo_code.ai.conversation_history import ConversationHistory
from neo_code.education.hints.common_errors import get_rule_based_hint

logger = logging.getLogger(__name__)


class SignificanceChecker:
    """Determines if code changes warrant a new LLM query."""

    def __init__(self, significance_threshold: int = 3):
        self._threshold = significance_threshold
        self._last_error_count = 0
        self._last_error_messages: set[str] = set()
        self._last_line_count = 0
        self._last_patterns: set = set()

    def is_significant(
        self,
        old_analysis: AnalysisResult | None,
        new_analysis: AnalysisResult,
    ) -> tuple[bool, str]:
        """Check if the change is significant enough to trigger AI response.

        Returns (is_significant, reason).
        """
        if old_analysis is None:
            if new_analysis.errors:
                return True, "first_error"
            return False, "initial"

        # New error appeared
        new_error_msgs = {e.message for e in new_analysis.errors}
        old_error_msgs = {e.message for e in old_analysis.errors}
        if new_error_msgs - old_error_msgs:
            return True, "new_error"

        # Error was fixed
        if old_analysis.errors and not new_analysis.errors:
            return True, "error_fixed"

        # Specific error was fixed
        if len(new_analysis.errors) < len(old_analysis.errors):
            return True, "error_partially_fixed"

        # New structural element
        new_patterns = set(new_analysis.patterns) - set(old_analysis.patterns)
        if new_patterns:
            return True, "new_pattern"

        # Significant code growth
        line_diff = abs(new_analysis.line_count - old_analysis.line_count)
        if line_diff >= self._threshold:
            return True, "code_growth"

        return False, "no_change"


class AIAssistantService:
    """Main AI assistant orchestrator."""

    def __init__(self):
        self._llm = LLMClient()
        self._context = ContextBuilder()
        self._history = ConversationHistory()
        self._significance = SignificanceChecker()
        self._last_analysis: AnalysisResult | None = None
        self._profile = StudentProfile(student_id="default", name="Student")
        self._current_code = ""

    def on_code_changed(self, code: str, analysis: AnalysisResult) -> AIResponse | None:
        """Process a code change. Returns a response if the change is significant."""
        self._current_code = code

        is_sig, reason = self._significance.is_significant(self._last_analysis, analysis)
        self._last_analysis = analysis

        if not is_sig:
            return None

        logger.info(f"Significant change detected: {reason}")

        if reason == "error_fixed":
            return self._handle_error_fixed(code, analysis)
        elif reason in ("new_error", "first_error"):
            return self._handle_new_error(code, analysis)
        elif reason == "new_pattern":
            return self._handle_proactive_guidance(code, analysis)
        elif reason == "code_growth":
            return self._handle_proactive_guidance(code, analysis)

        return None

    def on_manual_query(self, question: str, code: str, analysis: AnalysisResult) -> AIResponse:
        """Handle a manual student question."""
        self._current_code = code
        prompt = self._context.build_question_context(
            question, code, analysis, self._profile,
        )
        system = self._context.get_system_prompt(self._profile.current_phase)

        # Try LLM
        response_text = self._query_llm(prompt, system)
        if response_text:
            self._history.add_user_message(question)
            self._history.add_assistant_message(response_text)
            return parse_response(response_text, hint_level=HintLevel.GUIDANCE)

        # Fallback
        return AIResponse(
            message="I'm having trouble connecting to my AI brain right now. "
                    "Please check that Ollama is running on your computer.",
            hint_level=HintLevel.GUIDANCE,
        )

    def on_execution_result(self, code: str, result: ExecutionResult) -> AIResponse | None:
        """Process execution result (especially errors)."""
        self._profile.total_code_runs += 1

        if result.return_code == 0 and not result.stderr:
            return None  # Success, no comment needed

        if result.was_timeout:
            return AIResponse(
                message="Your code took too long to run! This usually means there's an "
                        "**infinite loop** - a loop that never stops. Check your `while` or "
                        "`for` loops and make sure they have a way to end.",
                hint_level=HintLevel.GUIDANCE,
                is_error_explanation=True,
            )

        # Runtime error
        prompt = self._context.build_execution_error_context(code, result)
        system = self._context.get_system_prompt(self._profile.current_phase)

        response_text = self._query_llm(prompt, system)
        if response_text:
            return parse_response(response_text, hint_level=HintLevel.GUIDANCE, is_error=True)

        # Fallback: rule-based hint for runtime errors
        hint = get_rule_based_hint(result.stderr)
        if hint:
            return AIResponse(
                message=hint,
                hint_level=HintLevel.GUIDANCE,
                is_error_explanation=True,
            )

        return AIResponse(
            message=f"Your code encountered an error:\n\n```\n{result.stderr[:300]}\n```\n\n"
                    "Try reading the error message carefully - it usually tells you the line number "
                    "and what went wrong.",
            hint_level=HintLevel.NUDGE,
            is_error_explanation=True,
        )

    def _handle_new_error(self, code: str, analysis: AnalysisResult) -> AIResponse:
        """Handle a new error in the code."""
        # Try rule-based hint first (faster, no LLM needed)
        if analysis.errors:
            error = analysis.errors[0]
            hint = get_rule_based_hint(error.message)
            if hint:
                return AIResponse(
                    message=hint,
                    hint_level=HintLevel.GUIDANCE,
                    related_lines=[error.line],
                    is_error_explanation=True,
                )

        # Try LLM
        prompt = self._context.build_error_context(code, analysis, self._profile)
        system = self._context.get_system_prompt(self._profile.current_phase)
        response_text = self._query_llm(prompt, system)

        if response_text:
            return parse_response(response_text, hint_level=HintLevel.GUIDANCE, is_error=True)

        # Basic fallback
        error = analysis.errors[0] if analysis.errors else None
        if error:
            msg = f"I see an error on **line {error.line}**: `{error.message}`"
            if error.suggestion:
                msg += f"\n\n**Hint:** {error.suggestion}"
            return AIResponse(
                message=msg,
                hint_level=HintLevel.GUIDANCE,
                related_lines=[error.line],
                is_error_explanation=True,
            )

        return AIResponse(
            message="I noticed some issues in your code. Take a careful look at your syntax!",
            hint_level=HintLevel.NUDGE,
            is_error_explanation=True,
        )

    def _handle_error_fixed(self, code: str, analysis: AnalysisResult) -> AIResponse:
        """Handle when an error has been fixed (positive reinforcement)."""
        self._profile.total_errors_fixed += 1
        return AIResponse(
            message="Your code looks correct now! Well done fixing that error. "
                    "Keep going - you're doing great!",
            hint_level=HintLevel.NUDGE,
            is_encouragement=True,
        )

    def _handle_proactive_guidance(self, code: str, analysis: AnalysisResult) -> AIResponse | None:
        """Provide proactive guidance when code is correct."""
        if analysis.errors:
            return None

        prompt = self._context.build_proactive_context(code, analysis, self._profile)
        system = self._context.get_system_prompt(self._profile.current_phase)
        response_text = self._query_llm(prompt, system)

        if response_text:
            return parse_response(response_text, is_encouragement=True)

        return None

    def _query_llm(self, prompt: str, system_prompt: str) -> str:
        """Query the LLM, returning empty string on failure."""
        if not self._llm.is_available():
            return ""

        try:
            return self._llm.generate(prompt, system_prompt)
        except Exception as e:
            logger.error(f"LLM query failed: {e}")
            return ""

    @property
    def profile(self) -> StudentProfile:
        return self._profile


class AIAssistantWorker(QThread):
    """Background thread for AI assistant operations."""

    thinking_started = pyqtSignal()
    response_chunk = pyqtSignal(str)
    response_complete = pyqtSignal(object)  # AIResponse
    error_occurred = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._service = AIAssistantService()
        self._pending_code: str | None = None
        self._pending_analysis: AnalysisResult | None = None

    def on_analysis_ready(self, code: str, analysis: AnalysisResult) -> None:
        """Queue an analysis result for processing."""
        self._pending_code = code
        self._pending_analysis = analysis
        if not self.isRunning():
            self.start()

    def run(self) -> None:
        if self._pending_code is None or self._pending_analysis is None:
            return

        self.thinking_started.emit()

        try:
            response = self._service.on_code_changed(
                self._pending_code, self._pending_analysis
            )
            if response:
                self.response_complete.emit(response)
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            self._pending_code = None
            self._pending_analysis = None
