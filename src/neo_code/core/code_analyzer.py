"""Code analysis engine using AST and pyflakes."""

import ast
import hashlib
import io
import re

from PyQt6.QtCore import QThread, pyqtSignal

from neo_code.core.models import (
    AnalysisResult, CodeError, ErrorSeverity, CodePattern,
)


# Pattern detection regex
TURTLE_PATTERN = re.compile(r'\bturtle\b|\bforward\b|\bbackward\b|\bleft\b|\bright\b|\bpenup\b|\bpendown\b')
GPIO_PATTERN = re.compile(r'\bGPIO\b|\bgpiozero\b|\bLED\b|\bButton\b|\bServo\b')
SENSOR_PATTERN = re.compile(r'\bsensor\b|\btemperature\b|\bultrasonic\b|\bdistance\b', re.IGNORECASE)


def analyze_code(code: str) -> AnalysisResult:
    """Perform static analysis on Python code. Thread-safe."""
    code_hash = hashlib.md5(code.encode()).hexdigest()
    result = AnalysisResult(code_hash=code_hash)
    result.line_count = len(code.splitlines())

    if not code.strip():
        return result

    # 1. AST parsing for syntax errors
    try:
        tree = ast.parse(code)
        result.is_syntactically_valid = True
        _extract_ast_info(tree, result)
    except SyntaxError as e:
        result.is_syntactically_valid = False
        result.errors.append(CodeError(
            line=e.lineno or 1,
            column=e.offset or 0,
            message=str(e.msg),
            severity=ErrorSeverity.ERROR,
            error_code="SyntaxError",
            suggestion=_suggest_syntax_fix(str(e.msg)),
        ))

    # 2. Pyflakes analysis (only if syntax is valid)
    if result.is_syntactically_valid:
        _run_pyflakes(code, result)

    # 3. Pattern detection
    _detect_patterns(code, result)

    return result


def _extract_ast_info(tree: ast.Module, result: AnalysisResult) -> None:
    """Extract structural information from AST."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                result.imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                result.imports.append(node.module)
        elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            result.defined_functions.append(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    result.defined_variables.append(target.id)
        elif isinstance(node, ast.ClassDef):
            result.patterns.append(CodePattern.CLASS_DEFINITION)

    # Complexity: count branches
    complexity = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler,
                             ast.With, ast.BoolOp)):
            complexity += 1
    result.complexity_score = complexity


def _run_pyflakes(code: str, result: AnalysisResult) -> None:
    """Run pyflakes for semantic error detection."""
    try:
        from pyflakes.api import check as pyflakes_check
        from pyflakes.messages import Message

        warning_output = io.StringIO()
        pyflakes_check(code, "<student_code>", warning_output)
        output = warning_output.getvalue()

        for line in output.strip().splitlines():
            if not line:
                continue
            # Parse pyflakes output: filename:line:col: message
            match = re.match(r'<student_code>:(\d+):(\d+:)?\s*(.*)', line)
            if match:
                line_no = int(match.group(1))
                msg = match.group(3)
                severity = ErrorSeverity.WARNING
                if "undefined" in msg.lower():
                    severity = ErrorSeverity.ERROR
                result.warnings.append(CodeError(
                    line=line_no,
                    column=0,
                    message=msg,
                    severity=severity,
                    error_code="pyflakes",
                ))
    except ImportError:
        pass  # pyflakes not installed, skip
    except Exception:
        pass  # Don't let pyflakes errors crash the analyzer


def _detect_patterns(code: str, result: AnalysisResult) -> None:
    """Detect code patterns for AI context."""
    if TURTLE_PATTERN.search(code):
        result.patterns.append(CodePattern.TURTLE_DRAWING)
    if GPIO_PATTERN.search(code):
        result.patterns.append(CodePattern.GPIO_SETUP)
    if SENSOR_PATTERN.search(code):
        result.patterns.append(CodePattern.SENSOR_READ)

    # Check for structural patterns
    if "for " in code or "while " in code:
        result.patterns.append(CodePattern.LOOP_CONSTRUCT)
    if "def " in code:
        result.patterns.append(CodePattern.FUNCTION_DEFINITION)
    if "if " in code:
        result.patterns.append(CodePattern.CONDITIONAL)
    if "import " in code:
        result.patterns.append(CodePattern.IMPORT_STATEMENT)
    if "[" in code and "]" in code:
        result.patterns.append(CodePattern.LIST_USAGE)
    if "try:" in code or "except" in code:
        result.patterns.append(CodePattern.ERROR_HANDLING)


def _suggest_syntax_fix(error_msg: str) -> str | None:
    """Suggest a fix for common syntax errors."""
    suggestions = {
        "expected ':'": "Add a colon ':' at the end of the line (after if, for, def, etc.)",
        "unexpected indent": "Check your indentation - remove extra spaces at the beginning",
        "expected an indented block": "Add indented code after the ':' (use 4 spaces)",
        "EOL while scanning string": "Close your string with a matching quote (' or \")",
        "unexpected EOF": "Check for missing closing brackets ), ], or }",
        "invalid syntax": "Check for typos, missing operators, or unclosed brackets",
    }
    for pattern, suggestion in suggestions.items():
        if pattern.lower() in error_msg.lower():
            return suggestion
    return None


class CodeAnalyzerWorker(QThread):
    """Background thread for code analysis."""

    analysis_complete = pyqtSignal(object)  # AnalysisResult

    def __init__(self, parent=None):
        super().__init__(parent)
        self._code: str = ""
        self._should_run = False

    def analyze(self, code: str) -> None:
        """Queue code for analysis."""
        self._code = code
        self._should_run = True
        if not self.isRunning():
            self.start()

    def run(self) -> None:
        while self._should_run:
            self._should_run = False
            code = self._code
            result = analyze_code(code)
            self.analysis_complete.emit(result)
