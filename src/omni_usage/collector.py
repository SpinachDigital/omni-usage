"""Call log parser and aggregator for OmniRoute."""

import json
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CALL_LOGS = Path.home() / ".omniroute" / "call_logs"


def load_all_records() -> list[dict[str, Any]]:
    """Load all call log summaries from the OmniRoute data directory."""
    records: list[dict[str, Any]] = []
    if not CALL_LOGS.exists():
        return records

    for day_dir in sorted(CALL_LOGS.iterdir()):
        if not day_dir.is_dir():
            continue
        for f in sorted(day_dir.iterdir()):
            if f.suffix != ".json":
                continue
            try:
                data = json.loads(f.read_text())
                summary = data.get("summary", {})
                if summary:
                    records.append(summary)
            except (json.JSONDecodeError, KeyError):
                continue
    return records


def safe_tokens(r: dict[str, Any]) -> dict[str, int]:
    """Safely extract token counts from a record."""
    t = r.get("tokens") or {}
    return {
        "in": t.get("in", 0) or 0,
        "out": t.get("out", 0) or 0,
        "cacheRead": t.get("cacheRead", 0) or 0,
        "reasoning": t.get("reasoning", 0) or 0,
    }


def parse_timestamp(ts_str: str | None) -> datetime | None:
    """Parse ISO timestamp, return None on failure."""
    if not ts_str:
        return None
    try:
        return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def build_report(records: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Aggregate token usage stats from call log records."""
    if records is None:
        records = load_all_records()

    total_req = len(records)
    success = sum(1 for r in records if r.get("status") == 200)
    errors = total_req - success

    tok_in = sum(safe_tokens(r)["in"] for r in records)
    tok_out = sum(safe_tokens(r)["out"] for r in records)
    cache = sum(safe_tokens(r)["cacheRead"] for r in records)

    now = datetime.now(timezone.utc)
    today_str = now.strftime("%Y-%m-%d")
    now_ts = now.timestamp()

    # Today
    today_recs = [r for r in records if (r.get("timestamp") or "").startswith(today_str)]

    # Session (last 5 min)
    session_recs: list[dict[str, Any]] = []
    for r in records:
        ts = parse_timestamp(r.get("timestamp"))
        if ts and ts.timestamp() >= now_ts - 300:
            session_recs.append(r)

    # Per-model stats
    model_stats: dict[str, dict[str, int]] = {}
    for r in records:
        model = r.get("model") or "unknown"
        if model not in model_stats:
            model_stats[model] = {"req": 0, "ok": 0, "err": 0, "in": 0, "out": 0, "cache": 0}
        t = safe_tokens(r)
        model_stats[model]["req"] += 1
        model_stats[model]["in"] += t["in"]
        model_stats[model]["out"] += t["out"]
        model_stats[model]["cache"] += t["cacheRead"]
        if r.get("status") == 200:
            model_stats[model]["ok"] += 1
        else:
            model_stats[model]["err"] += 1

    sorted_models = sorted(
        [(m, s) for m, s in model_stats.items() if s["in"] + s["out"] > 0],
        key=lambda x: -(x[1]["in"] + x[1]["out"]),
    )

    # Per-combo stats
    combo_usage: dict[str, int] = defaultdict(int)
    for r in records:
        combo = r.get("comboName") or "none"
        combo_usage[combo] += safe_tokens(r)["in"]

    sorted_combos = sorted(combo_usage.items(), key=lambda x: -x[1])

    # Per-provider stats
    provider_stats: dict[str, dict[str, int]] = {}
    for r in records:
        prov = r.get("provider") or "unknown"
        if prov not in provider_stats:
            provider_stats[prov] = {"req": 0, "in": 0, "out": 0}
        t = safe_tokens(r)
        provider_stats[prov]["req"] += 1
        provider_stats[prov]["in"] += t["in"]
        provider_stats[prov]["out"] += t["out"]

    sorted_providers = sorted(
        [(p, s) for p, s in provider_stats.items() if s["in"] + s["out"] > 0],
        key=lambda x: -(x[1]["in"] + x[1]["out"]),
    )

    # Current/last-used model
    if records:
        last = records[-1]
        current_combo = last.get("comboName") or ""
        current_model = last.get("model") or ""
    else:
        current_combo = ""
        current_model = ""

    return {
        "now": now,
        "current": {
            "combo": current_combo,
            "model": current_model,
        },
        "total": {
            "req": total_req,
            "ok": success,
            "err": errors,
            "in": tok_in,
            "out": tok_out,
            "cache": cache,
        },
        "today": {
            "req": len(today_recs),
            "in": sum(safe_tokens(r)["in"] for r in today_recs),
            "out": sum(safe_tokens(r)["out"] for r in today_recs),
        },
        "session": {
            "req": len(session_recs),
            "in": sum(safe_tokens(r)["in"] for r in session_recs),
            "out": sum(safe_tokens(r)["out"] for r in session_recs),
        },
        "models": sorted_models,
        "combos": sorted_combos[:8],
        "providers": sorted_providers[:8],
    }
