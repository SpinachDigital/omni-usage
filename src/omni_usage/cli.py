"""CLI entry points for omni-usage."""

import argparse
import json
import sys

from . import __about__
from .collector import build_report, load_all_records
from .widget import run_widget


def fmt(n: int | float, pad: int = 0) -> str:
    if n >= 1_000_000:
        s = f"{n / 1_000_000:.1f}M"
    elif n >= 1_000:
        s = f"{n / 1_000:.0f}K"
    else:
        s = str(n)
    return s.rjust(pad) if pad else s


def cmd_report(args: argparse.Namespace) -> None:
    """Print a one-shot report to stdout."""
    records = load_all_records()
    if not records:
        print("No call logs found. Make some requests through OmniRoute first.")
        sys.exit(0)

    report = build_report(records)
    t = report["total"]

    print(f"omni-usage report  ·  {report['now'].strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"{'─' * 56}")
    print(f"  Requests:   {t['req']:>8}  ✓ {t['ok']:>5}  ✗ {t['err']:>5}")
    print(f"  Input:      {fmt(t['in'], 10)}")
    print(f"  Output:     {fmt(t['out'], 10)}")
    print(f"  Cache read: {fmt(t['cache'], 10)}")
    print(f"  Total:      {fmt(t['in'] + t['out'], 10)}")
    print()

    if report["models"]:
        print(f"  {'Model':<30} {'Req':>5} {'Tokens':>10}")
        print(f"  {'─' * 47}")
        for model, s in report["models"][:15]:
            tok = s["in"] + s["out"]
            print(f"  {model:<30} {s['req']:>5} {fmt(tok):>10}")

    if args.json:
        print()
        print(json.dumps(report, indent=2, default=str))


def cmd_peek(args: argparse.Namespace) -> None:
    """Print a single-line summary for shell prompts."""
    report = build_report()
    t = report["total"]
    today = report["today"]
    total_tok = t["in"] + t["out"]
    today_tok = today["in"] + today["out"]
    print(f"⚡ {fmt(total_tok)} total  ·  {fmt(today_tok)} today  ·  {t['req']} requests")


def cmd_widget(args: argparse.Namespace) -> None:
    """Launch the live TUI widget."""
    run_widget(interval=args.interval)


def build_parser() -> argparse.ArgumentParser:
    """Return a fully configured argument parser."""
    parser = argparse.ArgumentParser(
        prog="omni-usage",
        description="Token usage dashboard for OmniRoute",
    )
    parser.add_argument(
        "--version", action="version", version=f"omni-usage v{__about__.__version__}"
    )

    sub = parser.add_subparsers(dest="command", required=True)

    w = sub.add_parser("widget", help="Live TUI dashboard (default)")
    w.add_argument(
        "--interval", "-i",
        type=int,
        default=30,
        help="Refresh interval in seconds (default: 30)",
    )
    w.set_defaults(func=cmd_widget)

    r = sub.add_parser("report", help="One-shot usage report")
    r.add_argument("--json", action="store_true", help="Output as JSON")
    r.set_defaults(func=cmd_report)

    p = sub.add_parser("peek", help="Single-line summary")
    p.set_defaults(func=cmd_peek)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
