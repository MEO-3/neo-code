"""Main AI assistant service - orchestrates code analysis and LLM responses."""
from __future__ import annotations

import logging
import time

from PyQt6.QtCore import QThread, pyqtSignal

from neo_code.core.models import (
    AnalysisResult, ExecutionResult, AIResponse, HintLevel, StudentProfile,
)
from neo_code.ai.llm_client import LLMClient
from neo_code.ai.context_builder import ContextBuilder
from neo_code.ai.response_parser import parse_response
from neo_code.ai.conversation_history import ConversationHistory
from neo_code.education.hints.common_errors import get_rule_based_hint
from neo_code.config.settings import get_settings

logger = logging.getLogger(__name__)


# ── Bilingual message templates ──

_MSGS = {
    "error_fixed": {
        "vi": "Code của bạn đã đúng rồi! Làm tốt lắm, bạn đã sửa được lỗi. Tiếp tục phát huy nhé!",
        "en": "Your code looks correct now! Well done fixing that error. Keep going - you're doing great!",
    },
    "timeout": {
        "vi": ("Code của bạn chạy quá lâu! Thường là do **vòng lặp vô hạn** - "
               "vòng lặp không bao giờ dừng. Kiểm tra lại `while` hoặc `for` "
               "và đảm bảo chúng có điều kiện dừng."),
        "en": ("Your code took too long to run! This usually means there's an "
               "**infinite loop** - a loop that never stops. Check your `while` or "
               "`for` loops and make sure they have a way to end."),
    },
    "runtime_error_generic": {
        "vi": "Code của bạn gặp lỗi khi chạy:\n\n```\n{stderr}\n```\n\n"
              "Hãy đọc kỹ thông báo lỗi - nó thường cho biết số dòng và nguyên nhân.",
        "en": "Your code encountered an error:\n\n```\n{stderr}\n```\n\n"
              "Try reading the error message carefully - it usually tells you the line number "
              "and what went wrong.",
    },
    "error_on_line": {
        "vi": "Mình thấy lỗi ở **dòng {line}**: `{message}`",
        "en": "I see an error on **line {line}**: `{message}`",
    },
    "hint_label": {
        "vi": "**Gợi ý:** {suggestion}",
        "en": "**Hint:** {suggestion}",
    },
    "syntax_issues": {
        "vi": "Mình thấy có vấn đề trong code. Hãy kiểm tra lại cú pháp nhé!",
        "en": "I noticed some issues in your code. Take a careful look at your syntax!",
    },
    "ollama_unavailable": {
        "vi": "Mình là NEO TRE, trợ lý lập trình của bạn!\n\n"
              "Bạn có thể hỏi mình về:\n"
              "- Cách vẽ hình (vuông, tam giác, ngôi sao, tròn...)\n"
              "- Vòng lặp, biến, hàm\n"
              "- Giải thích lỗi trong code\n"
              "- Cách sử dụng turtle\n\n"
              "Hãy thử hỏi cụ thể hơn nhé, ví dụ: *\"Làm sao vẽ hình vuông?\"*",
        "en": "I'm NEO TRE, your coding assistant!\n\n"
              "You can ask me about:\n"
              "- How to draw shapes (square, triangle, star, circle...)\n"
              "- Loops, variables, functions\n"
              "- Explaining errors in your code\n"
              "- How to use turtle\n\n"
              "Try asking something specific, e.g.: *\"How do I draw a square?\"*",
    },
    "turtle_limit": {
        "vi": ("Code của bạn có **quá nhiều lệnh turtle**! Giới hạn là {limit} lệnh.\n\n"
               "Hãy giảm số lần lặp lại. Ví dụ thay vì `range(1000000)`, "
               "thử `range(100)` hoặc nhỏ hơn."),
        "en": ("Your code has **too many turtle commands**! The limit is {limit} commands.\n\n"
               "Try reducing your loop count. For example, instead of `range(1000000)`, "
               "try `range(100)` or smaller."),
    },
    "run_help": {
        "vi": "Để chạy code, bấm nút **Run** (màu xanh lá) trên toolbar.\n\n"
              "Nếu code dùng `turtle`, kết quả sẽ hiện ở tab **Turtle Canvas**.",
        "en": "To run your code, click the **Run** button (green) on the toolbar.\n\n"
              "If your code uses `turtle`, the result will appear in the **Turtle Canvas** tab.",
    },
    "for_loop": {
        "vi": "**Vòng lặp `for`** giúp lặp lại hành động nhiều lần:\n\n"
              "```python\n# Lặp 4 lần (từ 0 đến 3)\nfor i in range(4):\n    print(i)\n```\n\n"
              "Dùng `range(n)` để lặp n lần. Với turtle, vòng lặp rất hữu ích để vẽ hình!",
        "en": "**`for` loop** repeats an action multiple times:\n\n"
              "```python\n# Loop 4 times (0 to 3)\nfor i in range(4):\n    print(i)\n```\n\n"
              "Use `range(n)` to loop n times. With turtle, loops are great for drawing shapes!",
    },
    "variable": {
        "vi": "**Biến** (variable) là cách lưu trữ dữ liệu:\n\n"
              "```python\nname = \"Neo\"     # biến kiểu chuỗi\n"
              "age = 10          # biến kiểu số\n"
              "colors = [\"red\"]  # biến kiểu danh sách\nprint(name, age)\n```\n\n"
              "Đặt tên biến bằng chữ cái, không dấu cách, không bắt đầu bằng số.",
        "en": "A **variable** stores data:\n\n"
              "```python\nname = \"Neo\"     # string variable\n"
              "age = 10          # number variable\n"
              "colors = [\"red\"]  # list variable\nprint(name, age)\n```\n\n"
              "Variable names start with a letter, no spaces, no starting with digits.",
    },
    "print_help": {
        "vi": "Dùng `print()` để in ra màn hình:\n\n"
              "```python\nprint(\"Xin chào!\")    # in chuỗi\n"
              "print(1 + 2)           # in kết quả: 3\n"
              "name = \"Neo\"\nprint(f\"Hello {name}\") # f-string\n```",
        "en": "Use `print()` to display output:\n\n"
              "```python\nprint(\"Hello!\")        # print string\n"
              "print(1 + 2)           # print result: 3\n"
              "name = \"Neo\"\nprint(f\"Hello {name}\") # f-string\n```",
    },
    "code_has_error": {
        "vi": "Mình thấy code của bạn có lỗi ở **dòng {line}**: `{message}`\n\n",
        "en": "I see an error in your code at **line {line}**: `{message}`\n\n",
    },
    "check_syntax": {
        "vi": "Hãy kiểm tra lại cú pháp ở dòng đó nhé!",
        "en": "Please check the syntax on that line!",
    },
    "working_on": {
        "vi": "Mình thấy bạn đang làm việc với **{intent}**! Đây là gợi ý:\n\n{hint}",
        "en": "I see you're working on **{intent}**! Here's a tip:\n\n{hint}",
    },
}


def _msg(key: str, lang: str = "vi", **kwargs) -> str:
    """Get a bilingual message."""
    template = _MSGS.get(key, {}).get(lang, _MSGS.get(key, {}).get("vi", ""))
    if kwargs:
        return template.format(**kwargs)
    return template


class SignificanceChecker:
    """Determines if code changes warrant a new LLM query."""

    def __init__(self, significance_threshold: int = 3):
        self._threshold = significance_threshold

    def is_significant(
        self,
        old_analysis: AnalysisResult | None,
        new_analysis: AnalysisResult,
    ) -> tuple[bool, str]:
        if old_analysis is None:
            if new_analysis.errors:
                return True, "first_error"
            return False, "initial"

        new_error_msgs = {e.message for e in new_analysis.errors}
        old_error_msgs = {e.message for e in old_analysis.errors}
        if new_error_msgs - old_error_msgs:
            return True, "new_error"

        if old_analysis.errors and not new_analysis.errors:
            return True, "error_fixed"

        if len(new_analysis.errors) < len(old_analysis.errors):
            return True, "error_partially_fixed"

        new_patterns = set(new_analysis.patterns) - set(old_analysis.patterns)
        if new_patterns:
            return True, "new_pattern"

        line_diff = abs(new_analysis.line_count - old_analysis.line_count)
        if line_diff >= self._threshold:
            return True, "code_growth"

        return False, "no_change"


class AIAssistantService:
    """Main AI assistant orchestrator with bilingual support."""

    def __init__(self):
        self._llm = LLMClient()
        self._context = ContextBuilder()
        self._history = ConversationHistory()
        self._significance = SignificanceChecker()
        self._last_analysis: AnalysisResult | None = None
        self._profile = StudentProfile(student_id="default", name="Student")
        self._current_code = ""
        self._lang = "vi"  # default language
        self._ai_settings = get_settings().ai
        self._last_auto_llm_time: float = 0.0

    @property
    def lang(self) -> str:
        return self._lang

    @lang.setter
    def lang(self, value: str) -> None:
        self._lang = value

    def on_code_changed(self, code: str, analysis: AnalysisResult) -> AIResponse | None:
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
        self._current_code = code
        prompt = self._context.build_question_context(
            question, code, analysis, self._profile,
        )
        system = self._context.get_system_prompt(self._profile.current_phase)

        # Add language instruction to system prompt
        lang_instruction = (
            "\nIMPORTANT: Always respond in Vietnamese (Tiếng Việt)."
            if self._lang == "vi" else
            "\nIMPORTANT: Always respond in English."
        )
        system += lang_instruction

        # Pass conversation history for multi-turn context
        history = self._history.get_messages()
        self._history.add_user_message(question)

        response_text = self._query_llm(prompt, system, history=history)
        if response_text:
            self._history.add_assistant_message(response_text)
            return parse_response(response_text, hint_level=HintLevel.GUIDANCE)

        return self._fallback_manual_response(question, code, analysis)

    def _fallback_manual_response(
        self, question: str, code: str, analysis: AnalysisResult
    ) -> AIResponse:
        from neo_code.education.hints.turtle_hints import (
            get_turtle_hint, detect_turtle_intent,
        )

        q = question.lower()
        lang = self._lang

        # Turtle concept keywords (both languages)
        turtle_keywords = {
            "hình vuông": "square", "square": "square",
            "tam giác": "triangle", "triangle": "triangle",
            "hình tròn": "circle", "circle": "circle",
            "ngôi sao": "star", "star": "star",
            "xoắn ốc": "spiral", "spiral": "spiral",
            "đa giác": "polygon", "polygon": "polygon",
            "màu sắc": "color", "color": "color", "tô màu": "color",
            "hàm": "function", "function": "function",
        }
        for keyword, concept in turtle_keywords.items():
            if keyword in q:
                hint = get_turtle_hint(concept)
                if hint:
                    return AIResponse(message=hint, hint_level=HintLevel.GUIDANCE)

        # Check for errors in current code
        if analysis.errors:
            error = analysis.errors[0]
            hint = get_rule_based_hint(error.message)
            msg = _msg("code_has_error", lang, line=error.line, message=error.message)
            msg += hint if hint else _msg("check_syntax", lang)
            if error.suggestion:
                msg += "\n\n" + _msg("hint_label", lang, suggestion=error.suggestion)
            return AIResponse(
                message=msg, hint_level=HintLevel.GUIDANCE,
                related_lines=[error.line], is_error_explanation=True,
            )

        # Common question patterns
        if any(w in q for w in ["chạy", "run", "thực thi", "execute"]):
            return AIResponse(message=_msg("run_help", lang), hint_level=HintLevel.GUIDANCE)

        if any(w in q for w in ["vòng lặp", "loop", "for", "while", "lặp"]):
            return AIResponse(message=_msg("for_loop", lang), hint_level=HintLevel.GUIDANCE)

        if any(w in q for w in ["biến", "variable", "gán", "assign"]):
            return AIResponse(message=_msg("variable", lang), hint_level=HintLevel.GUIDANCE)

        if any(w in q for w in ["print", "in ra", "hiển thị", "display", "output"]):
            return AIResponse(message=_msg("print_help", lang), hint_level=HintLevel.GUIDANCE)

        # Detect intent from code
        intent = detect_turtle_intent(code)
        if intent:
            hint = get_turtle_hint(intent)
            if hint:
                return AIResponse(
                    message=_msg("working_on", lang, intent=intent, hint=hint),
                    hint_level=HintLevel.GUIDANCE,
                )

        return AIResponse(
            message=_msg("ollama_unavailable", lang),
            hint_level=HintLevel.GUIDANCE,
        )

    def on_execution_result(self, code: str, result: ExecutionResult) -> AIResponse | None:
        self._profile.total_code_runs += 1
        lang = self._lang

        if result.return_code == 0 and not result.stderr:
            return None

        # Turtle command limit exceeded - no LLM needed
        if "Qua nhieu lenh turtle" in result.stderr or "turtle command limit" in (result.stdout or ""):
            limit = self._ai_settings.context.max_code_lines  # approximate
            try:
                limit = get_settings().execution.max_turtle_commands
            except Exception:
                pass
            msg = _msg("turtle_limit", lang, limit=limit)
            self._history.add_assistant_message(msg)
            return AIResponse(
                message=msg,
                hint_level=HintLevel.GUIDANCE,
                is_error_explanation=True,
            )

        if result.was_timeout:
            msg = _msg("timeout", lang)
            self._history.add_assistant_message(msg)
            return AIResponse(
                message=msg,
                hint_level=HintLevel.GUIDANCE,
                is_error_explanation=True,
            )

        # Runtime error - try LLM first with conversation history
        prompt = self._context.build_execution_error_context(code, result)
        system = self._context.get_system_prompt(self._profile.current_phase)
        lang_instruction = (
            "\nIMPORTANT: Always respond in Vietnamese (Tiếng Việt)."
            if self._lang == "vi" else
            "\nIMPORTANT: Always respond in English."
        )
        system += lang_instruction
        history = self._history.get_messages()
        response_text = self._query_llm(prompt, system, history=history)
        if response_text:
            self._history.add_assistant_message(response_text)
            return parse_response(response_text, hint_level=HintLevel.GUIDANCE, is_error=True)

        # Fallback: rule-based hint
        hint = get_rule_based_hint(result.stderr)
        if hint:
            return AIResponse(message=hint, hint_level=HintLevel.GUIDANCE, is_error_explanation=True)

        return AIResponse(
            message=_msg("runtime_error_generic", lang, stderr=result.stderr[:300]),
            hint_level=HintLevel.NUDGE,
            is_error_explanation=True,
        )

    def _handle_new_error(self, code: str, analysis: AnalysisResult) -> AIResponse:
        lang = self._lang

        # Always try rule-based hints first (free, no tokens)
        if analysis.errors:
            error = analysis.errors[0]
            hint = get_rule_based_hint(error.message)
            if hint:
                return AIResponse(
                    message=hint, hint_level=HintLevel.GUIDANCE,
                    related_lines=[error.line], is_error_explanation=True,
                )

        # Cooldown check: skip LLM if called too recently
        now = time.time()
        cooldown = self._ai_settings.auto_cooldown_seconds
        if now - self._last_auto_llm_time < cooldown:
            return self._fallback_error_response(analysis)

        # Use smaller token limit for auto-analysis
        prompt = self._context.build_error_context(code, analysis, self._profile)
        system = self._context.get_system_prompt(self._profile.current_phase)
        response_text = self._query_auto_llm(prompt, system)
        if response_text:
            return parse_response(response_text, hint_level=HintLevel.GUIDANCE, is_error=True)

        return self._fallback_error_response(analysis)

    def _fallback_error_response(self, analysis: AnalysisResult) -> AIResponse:
        """Build a response from analysis without LLM."""
        lang = self._lang
        error = analysis.errors[0] if analysis.errors else None
        if error:
            msg = _msg("error_on_line", lang, line=error.line, message=error.message)
            if error.suggestion:
                msg += "\n\n" + _msg("hint_label", lang, suggestion=error.suggestion)
            return AIResponse(
                message=msg, hint_level=HintLevel.GUIDANCE,
                related_lines=[error.line], is_error_explanation=True,
            )

        return AIResponse(
            message=_msg("syntax_issues", lang),
            hint_level=HintLevel.NUDGE,
            is_error_explanation=True,
        )

    def _handle_error_fixed(self, code: str, analysis: AnalysisResult) -> AIResponse:
        self._profile.total_errors_fixed += 1
        return AIResponse(
            message=_msg("error_fixed", self._lang),
            hint_level=HintLevel.NUDGE,
            is_encouragement=True,
        )

    def _handle_proactive_guidance(self, code: str, analysis: AnalysisResult) -> AIResponse | None:
        """Use local hints only - no LLM call to save tokens."""
        if analysis.errors:
            return None

        from neo_code.education.hints.turtle_hints import (
            detect_turtle_intent, get_turtle_hint,
        )
        intent = detect_turtle_intent(code)
        if intent:
            hint = get_turtle_hint(intent)
            if hint:
                return AIResponse(
                    message=_msg("working_on", self._lang, intent=intent, hint=hint),
                    hint_level=HintLevel.NUDGE,
                    is_encouragement=True,
                )

        return None

    def _query_llm(
        self, prompt: str, system_prompt: str,
        history: list[dict[str, str]] | None = None,
    ) -> str:
        if not self._llm.is_available():
            return ""
        try:
            return self._llm.generate(prompt, system_prompt, history=history)
        except Exception as e:
            logger.error(f"LLM query failed: {e}")
            return ""

    def _query_auto_llm(self, prompt: str, system_prompt: str) -> str:
        """LLM query for auto-analysis: smaller tokens, no history, with cooldown tracking."""
        if not self._llm.is_available():
            return ""
        try:
            self._last_auto_llm_time = time.time()
            return self._llm.generate(
                prompt, system_prompt,
                max_tokens=self._ai_settings.auto_response_tokens,
            )
        except Exception as e:
            logger.error(f"Auto LLM query failed: {e}")
            return ""

    @property
    def profile(self) -> StudentProfile:
        return self._profile


class AIAssistantWorker(QThread):
    """Background thread for AI assistant operations."""

    thinking_started = pyqtSignal()
    response_chunk = pyqtSignal(str)
    response_complete = pyqtSignal(object)
    error_occurred = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._service = AIAssistantService()
        self._pending_code: str | None = None
        self._pending_analysis: AnalysisResult | None = None

    def on_analysis_ready(self, code: str, analysis: AnalysisResult) -> None:
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
