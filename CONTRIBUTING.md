# Contributing

Thanks for helping improve Whispefy.

## Setup

```bash
uv sync
cp .env.example .env
./scripts/check-deps.sh
```

## Development Loop

- Make changes in the `whispefy/` package.
- Run tests with `uv run python -m unittest discover -s tests -v`.
- Run syntax checks with `python3 -m compileall whispefy tests`.
- If you touch runtime behavior, test it in a Wayland session.

## Pull Requests

- Keep changes focused.
- Include a short summary of what changed and how you verified it.
- Avoid introducing new dependencies unless they reduce complexity or are required for the feature.

## License

By contributing, you agree that your changes are licensed under GPL-3.0-or-later.
