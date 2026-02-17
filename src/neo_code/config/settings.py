"""Application settings management using TOML configuration."""

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


_DEFAULTS_PATH = Path(__file__).parent / "defaults.toml"
_USER_CONFIG_DIR = Path.home() / ".neo_code"
_USER_CONFIG_PATH = _USER_CONFIG_DIR / "config.toml"


def _deep_merge(base: dict, override: dict) -> dict:
    """Deep merge override into base dict."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


@dataclass
class EditorAnalysisSettings:
    debounce_ms: int = 500
    enable_pyflakes: bool = True
    enable_jedi: bool = True
    max_analysis_time_ms: int = 2000


@dataclass
class EditorSettings:
    font_family: str = "JetBrains Mono"
    font_size: int = 14
    tab_width: int = 4
    auto_indent: bool = True
    show_line_numbers: bool = True
    highlight_current_line: bool = True
    word_wrap: bool = False
    theme: str = "neo_dark"
    analysis: EditorAnalysisSettings = field(default_factory=EditorAnalysisSettings)


@dataclass
class ExecutionSettings:
    timeout_seconds: int = 30
    max_memory_mb: int = 256
    turtle_animation_speed: int = 6


@dataclass
class AIContextSettings:
    max_history_turns: int = 6
    max_code_lines: int = 200


@dataclass
class AISettings:
    model: str = "qwen2.5-coder:1.5b"
    fallback_model: str = "tinyllama:1.1b"
    ollama_host: str = "http://localhost:11434"
    max_response_tokens: int = 512
    temperature: float = 0.3
    enable_auto_analysis: bool = True
    significance_threshold: int = 3
    idle_timeout_seconds: int = 30
    hint_level: str = "guidance"
    context: AIContextSettings = field(default_factory=AIContextSettings)


@dataclass
class EducationSettings:
    default_phase: int = 1
    curriculum_path: str = "curriculum_data"


@dataclass
class HardwareSettings:
    enable_gpio: bool = False
    gpio_library: str = "gpiozero"


@dataclass
class StorageSettings:
    database_path: str = "~/.neo_code/neo_code.db"
    projects_path: str = "~/NEO_CODE_Projects"


@dataclass
class UISettings:
    splitter_ratio: list[int] = field(default_factory=lambda: [60, 40])
    show_ai_panel: bool = True
    show_output_panel: bool = True
    window_width: int = 1280
    window_height: int = 720


@dataclass
class AppSettings:
    """Root settings container."""
    name: str = "NEO CODE"
    version: str = "0.1.0"
    language: str = "vi"
    editor: EditorSettings = field(default_factory=EditorSettings)
    execution: ExecutionSettings = field(default_factory=ExecutionSettings)
    ai: AISettings = field(default_factory=AISettings)
    education: EducationSettings = field(default_factory=EducationSettings)
    hardware: HardwareSettings = field(default_factory=HardwareSettings)
    storage: StorageSettings = field(default_factory=StorageSettings)
    ui: UISettings = field(default_factory=UISettings)


def _apply_dict_to_dataclass(obj: Any, data: dict) -> None:
    """Apply dict values to a dataclass instance."""
    for key, value in data.items():
        if hasattr(obj, key):
            attr = getattr(obj, key)
            if isinstance(value, dict) and hasattr(attr, "__dataclass_fields__"):
                _apply_dict_to_dataclass(attr, value)
            else:
                setattr(obj, key, value)


def load_settings() -> AppSettings:
    """Load settings from defaults.toml, merged with user config if exists."""
    # Load defaults
    with open(_DEFAULTS_PATH, "rb") as f:
        defaults = tomllib.load(f)

    # Load user config if exists
    config = defaults
    if _USER_CONFIG_PATH.exists():
        with open(_USER_CONFIG_PATH, "rb") as f:
            user_config = tomllib.load(f)
        config = _deep_merge(defaults, user_config)

    # Build settings object
    settings = AppSettings()
    app_config = config.get("application", {})
    settings.name = app_config.get("name", settings.name)
    settings.version = app_config.get("version", settings.version)
    settings.language = app_config.get("language", settings.language)

    for section_name in ["editor", "execution", "ai", "education", "hardware", "storage", "ui"]:
        if section_name in config:
            _apply_dict_to_dataclass(getattr(settings, section_name), config[section_name])

    return settings


# Global settings instance (lazy loaded)
_settings: AppSettings | None = None


def get_settings() -> AppSettings:
    """Get the global settings instance."""
    global _settings
    if _settings is None:
        _settings = load_settings()
    return _settings
