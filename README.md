<div align="center">

# ⚡ omni-usage ⚡

**Token usage dashboard for OmniRoute**

See your LLM token consumption at a glance — live TUI, one-shot reports, or a single-line peek.

![Python](https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square)
[![PyPI](https://img.shields.io/pypi/v/omni-usage?style=flat-square&color=00B4D8)](https://pypi.org/project/omni-usage/)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey?style=flat-square)

![Screenshot placeholder](docs/screenshot.png)

> *Live dashboard showing model usage, combo routing, cache savings, and request health.*

---

</div>

## 📦 Install

```bash
pip install omni-usage
# or with uv:
uv tool install omni-usage
```

**Zero dependencies** — reads OmniRoute's local call logs directly from disk. No API calls, no extra token cost.

## 🚀 Usage

### 🖥️ Live widget (default)

```bash
# Launch the live dashboard
omni-usage widget

# Custom refresh rate
omni-usage widget --interval 60
```

Opens a full-screen live TUI that auto-refreshes. Shows:

- **⏳ Session** — requests and tokens in the last 5 minutes
- **📅 Today** — today's totals
- **📊 All Time** — cumulative statistics
- **🤖 Models** — per-model breakdown with progress bars and health status
- **🎯 Combos** — which routing combos are consuming the most tokens
- **🔥 Cache savings** — prompt cache hit ratio

### 📋 One-shot report

```bash
# Terminal report
omni-usage report

# JSON output (for piping into jq or scripts)
omni-usage report --json
```

### 🔍 Quick peek

```bash
omni-usage peek
```

Prints a single line like `⚡ 14.2M total  ·  8.7M today  ·  367 requests` — perfect for shell prompts or tmux status bars.

## 📊 What you see

```
┌──────────────────────────────────────────────────────────────┐
│                      ⚡ omni-usage ⚡                         │
│                Token Usage Dashboard                         │
│                2026-07-04 20:45:12 UTC                       │
├──────────────┬─────────────────┬─────────────────────────────┤
│ ⏳ Session   │ 📅 Today        │ 📊 All Time                 │
│ Reqs     12  │ Reqs      112   │ Reqs       367              │
│ Tokens 1.5M  │ Input    8.7M   │ Success   222  ✓ 60%        │
│              │ Output    40K   │ Total   14.2M                │
├──────────────┴─────────────────┴─────────────────────────────┤
│ 🤖 Models     Reqs  ████████████████  Tokens  Status          │
│ big-pickle     165  ████████████████  13.1M  ✓                │
│ GPT_5_4         49  ████               751K  ⚠                │
│ deepseek-v4…     2  ██                  96K  ✓                │
│ gemini_3_flash   8  ██                  75K  ⚠                │
├──────────────────────────────────────────────────────────────┤
│ 🎯 Combos                       ██████████████████████████     │
│ auto/best-coding                ████████████████████████  5.3M │
│ auto/claude-opus                ███████████████████████   4.7M │
│ auto/chat                       ███████████████           3.2M │
├──────────────────────────────────────────────────────────────┤
│ ⚡ big-pickle · 🔥 89% cache saved · refresh every 30s       │
└──────────────────────────────────────────────────────────────┘
```

## 🔧 How it works

`omni-usage` reads OmniRoute's local call log files directly from `~/.omniroute/call_logs/`. Each request OmniRoute proxies is logged as a JSON file with token counts, model name, provider, combo name, and status code.

The tool simply aggregates these local files — **no API calls, no network, zero additional token cost.**

## 🧩 Integration ideas

| Use case | Command |
|---|---|
| **Shell prompt** | `omni-usage peek` in your PS1 |
| **tmux status bar** | `omni-usage peek` via `#(omni-usage peek)` |
| **Hermes slash command** | Install as a Hermes plugin: `hermes skills install <url>` |
| **CI check** | `omni-usage report --json` to track token budgets |
| **Daily cron** | `0 9 * * * omni-usage report` |

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

```bash
git clone https://github.com/omniroute-community/omni-usage
cd omni-usage
pip install -e ".[dev]"
```

## 📄 License

MIT — see [LICENSE](LICENSE).

---

<div align="center">
<sub>Built with ❤️ for the OmniRoute community</sub>
</div>
