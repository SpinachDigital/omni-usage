# Contributing

## Development

```bash
git clone https://github.com/<your-org>/omni-usage
cd omni-usage
pip install -e ".[dev]"
```

## Code style

- Python 3.10+ type hints everywhere
- `ruff` for linting
- Keep the widget dependency-free beyond `rich`

## PR checklist

- [ ] Tested against real OmniRoute call logs
- [ ] `omni-usage widget` launches without error
- [ ] `omni-usage report --json` produces valid JSON
- [ ] `omni-usage peek` prints a single line
