"""Theme and styling for NEO CODE IDE."""

# Color palette - student-friendly dark theme
COLORS = {
    "bg_primary": "#1e1e2e",
    "bg_secondary": "#181825",
    "bg_tertiary": "#313244",
    "bg_hover": "#45475a",
    "text_primary": "#cdd6f4",
    "text_secondary": "#a6adc8",
    "text_dim": "#6c7086",
    "accent": "#89b4fa",
    "accent_hover": "#74c7ec",
    "success": "#a6e3a1",
    "warning": "#f9e2af",
    "error": "#f38ba8",
    "info": "#89dceb",
    "border": "#45475a",
    "editor_bg": "#1e1e2e",
    "editor_line_highlight": "#2a2a3c",
    "toolbar_bg": "#181825",
    "chat_bg": "#11111b",
    "chat_user_bg": "#313244",
    "chat_ai_bg": "#1e1e2e",
    "button_bg": "#89b4fa",
    "button_text": "#1e1e2e",
    "button_hover": "#74c7ec",
    "run_button": "#a6e3a1",
    "stop_button": "#f38ba8",
}

MAIN_STYLESHEET = f"""
QMainWindow {{
    background-color: {COLORS['bg_primary']};
}}

QWidget {{
    color: {COLORS['text_primary']};
    font-family: "Segoe UI", "Noto Sans", sans-serif;
    font-size: 13px;
}}

QSplitter::handle {{
    background-color: {COLORS['border']};
    width: 2px;
}}

QToolBar {{
    background-color: {COLORS['toolbar_bg']};
    border: none;
    padding: 4px;
    spacing: 6px;
}}

QToolBar QToolButton {{
    background-color: {COLORS['bg_tertiary']};
    color: {COLORS['text_primary']};
    border: none;
    border-radius: 6px;
    padding: 6px 14px;
    font-weight: bold;
    font-size: 13px;
}}

QToolBar QToolButton:hover {{
    background-color: {COLORS['bg_hover']};
}}

QToolBar QToolButton#runButton {{
    background-color: {COLORS['run_button']};
    color: {COLORS['button_text']};
}}

QToolBar QToolButton#runButton:hover {{
    background-color: #94d89a;
}}

QToolBar QToolButton#stopButton {{
    background-color: {COLORS['stop_button']};
    color: {COLORS['button_text']};
}}

QToolBar QToolButton#stopButton:hover {{
    background-color: #e67e96;
}}

QTextBrowser {{
    background-color: {COLORS['chat_bg']};
    color: {COLORS['text_primary']};
    border: none;
    padding: 10px;
    font-size: 13px;
}}

QLineEdit {{
    background-color: {COLORS['bg_tertiary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
}}

QLineEdit:focus {{
    border-color: {COLORS['accent']};
}}

QTextEdit {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
    border: none;
    font-family: "JetBrains Mono", "Fira Code", "Consolas", monospace;
    font-size: 13px;
}}

QLabel {{
    color: {COLORS['text_primary']};
}}

QLabel#sectionTitle {{
    font-size: 15px;
    font-weight: bold;
    color: {COLORS['accent']};
    padding: 4px 0px;
}}

QProgressBar {{
    background-color: {COLORS['bg_tertiary']};
    border: none;
    border-radius: 4px;
    height: 8px;
    text-align: center;
}}

QProgressBar::chunk {{
    background-color: {COLORS['accent']};
    border-radius: 4px;
}}

QTabWidget::pane {{
    border: none;
    background-color: {COLORS['bg_primary']};
}}

QTabBar::tab {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_secondary']};
    border: none;
    padding: 8px 16px;
    margin-right: 2px;
}}

QTabBar::tab:selected {{
    background-color: {COLORS['bg_primary']};
    color: {COLORS['accent']};
    border-bottom: 2px solid {COLORS['accent']};
}}

QScrollBar:vertical {{
    background-color: {COLORS['bg_primary']};
    width: 10px;
    border: none;
}}

QScrollBar::handle:vertical {{
    background-color: {COLORS['bg_hover']};
    border-radius: 5px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {COLORS['text_dim']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
"""

EDITOR_COLORS = {
    "background": 0x1E1E2E,
    "foreground": 0xCDD6F4,
    "caret": 0xF5E0DC,
    "selection_bg": 0x45475A,
    "line_highlight": 0x2A2A3C,
    "margin_bg": 0x181825,
    "margin_fg": 0x6C7086,
    "fold_margin_bg": 0x181825,
    "brace_match_bg": 0x45475A,
    "brace_match_fg": 0xF9E2AF,
    "error_marker": 0xF38BA8,
    "warning_marker": 0xF9E2AF,
    # Python lexer colors
    "keyword": 0xCBA6F7,
    "string": 0xA6E3A1,
    "number": 0xFAB387,
    "comment": 0x6C7086,
    "decorator": 0xF9E2AF,
    "function_name": 0x89B4FA,
    "class_name": 0xF9E2AF,
    "operator": 0x89DCEB,
    "builtin": 0xF38BA8,
}
