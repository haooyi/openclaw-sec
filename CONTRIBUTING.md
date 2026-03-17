# Contributing to openclaw-sec

Thanks for contributing.

This project is intentionally small, local-first, and standard-library-first. Contributions are welcome, but the bar for adding complexity is high.

## Principles

- prefer explainable checks over clever but opaque detection
- keep dependencies minimal
- avoid network requirements for core audit logic
- make unsupported checks degrade gracefully instead of crashing
- never print raw secrets in reports, examples, or tests

## Development Setup

```bash
git clone https://github.com/haooyi/openclaw-sec.git
cd openclaw-sec
python3 -m pip install -e .
```

Run tests:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Run a local audit:

```bash
PYTHONPATH=src python3 -m openclaw_sec audit --format all
```

## Project Layout

- `src/openclaw_sec/cli.py`: CLI entrypoint
- `src/openclaw_sec/audit.py`: central runner and aggregation
- `src/openclaw_sec/report.py`: text, JSON, and Markdown rendering
- `src/openclaw_sec/detectors/`: independent audit detectors
- `src/openclaw_sec/data/`: detection patterns and static data
- `tests/`: unit tests
- `skills/openclaw-sec-audit/`: OpenClaw skill wrapper

## Contribution Scope

Good contribution candidates:

- tighter OpenClaw config heuristics
- stronger secret detection with low false-positive rates
- better host and filesystem checks
- clearer reports and remediation guidance
- tests that improve fixture coverage

Changes that should be discussed before implementation:

- large dependency additions
- auto-remediation behavior
- daemon or remote scanning modes
- broad rule-engine abstractions
- features that require cloud services or an LLM to function

## Coding Guidelines

- use Python 3.11+ compatible code
- prefer the standard library unless a dependency clearly pays for itself
- keep detector logic isolated and easy to review
- favor simple data flow over framework-heavy abstractions
- use ASCII by default
- keep comments short and only where they help readability

## Tests

New logic should include tests when practical, especially for:

- config parsing success and failure
- secret redaction behavior
- permissions and symlink handling
- unsupported host-check behavior
- report rendering and output stability

## Pull Requests

Please keep pull requests focused and easy to review.

A good pull request usually includes:

- a short description of the change
- why the change is needed
- any tradeoffs or limitations
- tests or verification notes

If the change affects detection behavior, mention expected false-positive or false-negative tradeoffs explicitly.

## Security Contributions

If you believe you found a real security issue in the project itself, please follow [SECURITY.md](./SECURITY.md) instead of opening a public issue with exploit details.
