"""omni-usage — Compact, clean, single-screen token dashboard for OmniRoute."""

import os
import shutil
import sys
import time

from .collector import build_report, load_all_records


def fmt(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n // 1000}K"
    return str(n)


def _w() -> int:
    tw = shutil.get_terminal_size((80, 24)).columns
    return min(max(tw - 4, 66), 78)


def _h(err: int) -> str:
    return "✓" if err == 0 else f"⚠{err}"


def draw(report: dict, interval: int) -> list[str]:
    t = report["total"]
    today = report["today"]
    sess = report["session"]
    models = report["models"]
    combos = report["combos"]
    cur = report.get("current", {})
    now_str = report["now"].strftime("%d %b %H:%M")

    tt = t["in"] + t["out"]
    cache_pct = round(t["cache"] / max(t["in"], 1) * 100)
    W = _w()
    IW = W
    lines: list[str] = []
    bar = "─" * W

    def _pad(content: str) -> str:
        return content + " " * (IW - len(content))

    # ── header (single line with brand + timestamp) ────────
    lines.append(f"┌{bar}┐")
    hdr = f"⚡ omni-usage  ·  v0.1.0  ·  {now_str}  ·  ref {interval}s"
    lines.append(f"│{_pad('  ' + hdr)}│")
    lines.append(f"├{bar}┤")

    # ── stat columns ────────────────────────────────────────
    inner = IW - 8  # 3 cols + 2 separators(2ea) + border pads(4)
    cw = inner // 3
    rem = inner % 3
    c1 = cw + (1 if rem > 0 else 0)
    c2 = cw + (1 if rem > 1 else 0)
    c3 = cw
    sp = "  "

    stok = sess["in"] + sess["out"]

    lines.append(f"│  {'⏳ Session (5m)':<{c1}}{sp}{'📅 Today':<{c2}}{sp}{'📊 All Time':<{c3}}  │")
    lines.append(f"│  {'Req ' + fmt(sess['req']):<{c1}}{sp}{'Req ' + fmt(today['req']):<{c2}}{sp}{'Req ' + fmt(t['req']):<{c3}}  │")
    lines.append(f"│  {'Tok ' + fmt(stok):<{c1}}{sp}{'In  ' + fmt(today['in']):<{c2}}{sp}{'✓  ' + fmt(t['ok']):<{c3}}  │")
    lines.append(f"│  {'':<{c1}}{sp}{'Out ' + fmt(today['out']):<{c2}}{sp}{'✗  ' + fmt(t['err']):<{c3}}  │")

    # ── models ──────────────────────────────────────────────
    lines.append(f"├{bar}┤")
    title_m = "🤖  Models Used (by token volume)"
    lines.append(f"│{_pad('  ' + title_m)}│")

    data_pad = IW - 2 - 26 - 1 - 4 - 1 - 10 - 1 - 4  # = IW - 49
    for m, s in models[:5]:
        tok = s["in"] + s["out"]
        name = m if len(m) <= 26 else m[:23] + "…"
        lines.append(f"│  {name:<26} {s['req']:>4} {fmt(tok):>10} {_h(s['err']):>4}{' ' * data_pad}│")

    # ── combos ──────────────────────────────────────────────
    lines.append(f"├{bar}┤")
    title_c = "🎯  Route Combos (by token volume)"
    lines.append(f"│{_pad('  ' + title_c)}│")

    c_pad = IW - 2 - 28 - 1 - 10  # = IW - 41
    for combo, val in combos[:5]:
        name = combo if len(combo) <= 28 else combo[:25] + "…"
        lines.append(f"│  {name:<28} {fmt(val):>10}{' ' * c_pad}│")

    # ── footer ──────────────────────────────────────────────
    lines.append(f"├{bar}┤")
    active = cur.get("combo") or cur.get("model") or "—"
    foot = f"  Now: {active}"
    if cache_pct:
        foot += f"  ·  🔥 {cache_pct}% cache saved"
    foot += f"  ·  press Ctrl+C to quit"
    lines.append(f"│{_pad(foot)}│")
    lines.append(f"└{bar}┘")

    return lines


def run_widget(interval: int = 30) -> None:
    os.system("")
    prev_h = 0
    try:
        while True:
            records = load_all_records()
            if records:
                lines = draw(build_report(records), interval)
            else:
                w = _w()
                lines = [
                    f"┌{'─' * w}┐",
                    f"│{'Waiting for OmniRoute call logs...':^{w}}│",
                    f"└{'─' * w}┘",
                ]

            h = len(lines)
            if prev_h:
                sys.stdout.write(f"\033[{prev_h}A")
            for l in lines:
                sys.stdout.write("\033[2K" + l + "\n")
            sys.stdout.flush()
            prev_h = h
            time.sleep(interval)
    except KeyboardInterrupt:
        if prev_h:
            sys.stdout.write(f"\033[{prev_h}B\n")
        sys.stdout.write("omni-usage closed.\n")
        sys.stdout.flush()
