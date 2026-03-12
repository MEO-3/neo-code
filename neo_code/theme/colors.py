"""
Color palette for NEO CODE.

Primary  : #32A852  (green)
Background: #FFFFFF (white)

All other colors are derived from these two anchors to keep the UI consistent.
Import `colors` anywhere in the app — do NOT hardcode hex strings in widgets.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class _Palette:
    # ── Brand ──────────────────────────────────────────────────────────────
    primary:          str = "#32A852"   # green — buttons, highlights, active state
    primary_hover:    str = "#28904A"   # darker green on hover
    primary_dim:      str = "#A8D8B4"   # light green tint — subtle accents
    primary_text:     str = "#FFFFFF"   # text on primary-colored surfaces

    # ── Background family ──────────────────────────────────────────────────
    background:       str = "#FFFFFF"   # main window / editor background
    surface:          str = "#F4F4F5"   # panels, sidebars, cards
    surface_alt:      str = "#E8E8EA"   # alternate rows, input fields
    border:           str = "#D1D5DB"   # dividers, widget borders

    # ── Text family ────────────────────────────────────────────────────────
    text:             str = "#1A1A2E"   # primary text (near-black)
    text_secondary:   str = "#6B7280"   # labels, placeholders, captions
    text_disabled:    str = "#B0B3BA"   # disabled widgets

    # ── Editor / terminal ──────────────────────────────────────────────────
    editor_bg:        str = "#FAFAFA"   # editor background (slightly off-white)
    editor_text:      str = "#1A1A2E"
    editor_line_hl:   str = "#EAF4EE"   # current-line highlight (soft green)
    editor_selection: str = "#B6DFBF"   # selection background

    terminal_bg:      str = "#1A1A2E"   # dark terminal background
    terminal_text:    str = "#F4F4F5"
    terminal_error:   str = "#E05252"   # stderr text
    terminal_success: str = "#32A852"   # exit 0 message

    # ── Syntax highlighting ────────────────────────────────────────────────
    syn_keyword:      str = "#32A852"   # keywords  — green (brand)
    syn_builtin:      str = "#1D6FA4"   # builtins  — blue
    syn_string:       str = "#B5600A"   # strings   — amber/orange
    syn_number:       str = "#9333EA"   # numbers   — purple
    syn_comment:      str = "#9CA3AF"   # comments  — grey italic
    syn_decorator:    str = "#DB6E00"   # decorators

    # ── Activity bar (sidebar) ─────────────────────────────────────────────
    activity_bar_bg:      str = "#F0F0F2"   # activity bar strip background
    activity_bar_active:  str = "#32A852"   # active indicator line
    activity_bar_icon:    str = "#6B7280"   # inactive icon
    activity_bar_icon_hl: str = "#1A1A2E"   # hovered / active icon

    # ── Content panel ──────────────────────────────────────────────────────
    panel_bg:         str = "#FFFFFF"
    panel_header_bg:  str = "#F0F0F2"
    panel_header_text: str = "#6B7280"

    # ── Toolbar ────────────────────────────────────────────────────────────
    toolbar_bg:       str = "#FFFFFF"
    toolbar_border:   str = "#D1D5DB"

    # ── Run / Stop buttons ─────────────────────────────────────────────────
    run_bg:           str = "#32A852"
    run_bg_hover:     str = "#28904A"
    run_text:         str = "#FFFFFF"
    stop_bg:          str = "#E05252"
    stop_bg_hover:    str = "#C43B3B"
    stop_text:        str = "#FFFFFF"


# Module-level singleton — import this everywhere
colors = _Palette()
