"""

**omni-usage** — Token usage dashboard for OmniRoute.

See your LLM token consumption at a glance:
- Live TUI widget with auto-refresh
- One-shot reports (terminal or JSON)
- Single-line peek for shell prompts
"""

from .cli import main
from .collector import build_report, load_all_records
from .widget import run_widget

__all__ = ["main", "build_report", "load_all_records", "run_widget"]
