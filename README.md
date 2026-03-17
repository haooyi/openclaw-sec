# openclaw-sec

[![CI](https://github.com/haooyi/openclaw-sec/actions/workflows/ci.yml/badge.svg)](https://github.com/haooyi/openclaw-sec/actions/workflows/ci.yml)
[Chinese README (Simplified Chinese)](./README.zh-CN.md)
[Contributing Guide](./CONTRIBUTING.md) | [Security Policy](./SECURITY.md) | [Changelog](./CHANGELOG.md)
[Release Notes v0.1.0](./docs/releases/v0.1.0.md) | [Demo Fixture](./examples/redacted-lab/README.md)

`openclaw-sec` is a local-first, low-dependency security audit tool for OpenClaw environments.

The V1 goal is intentionally narrow:

- run locally with minimal setup
- surface high-signal, explainable risks
- produce human-actionable summaries and reports
- avoid auto-fix, mandatory networking, or LLM-only detection

The current CLI surface is a single command:

```bash
openclaw-sec audit
```

## Project Metadata

- Repository: `haooyi/openclaw-sec`
- Default branch: `main`
- License: MIT
- Maintainer contact: `haooyi@gmail.com`

## Why

Common OpenClaw risks are usually simple, but easy to miss:

- plaintext secrets left in config, backups, or logs
- overly broad permissions on `~/.openclaw`, `.env`, or session artifacts
- sensitive content copied into workspace bootstrap or memory files
- weak host hardening around listening ports, SSH, firewall, or fail2ban
- secrets already present in the current Git working tree

`openclaw-sec` is not trying to be a full security platform. The first goal is to catch these common, locally verifiable issues quickly and explain them clearly.

## What It Checks

V1 focuses on these categories:

- OpenClaw config existence, parseability, and high-risk heuristic settings
- plaintext secrets in config, `.env`, backups, workspace documents, logs, and Git tracked files
- overly broad permissions on `~/.openclaw`, config files, environment files, and logs
- symlink escape risks for security-sensitive paths
- Linux-first host checks for listening ports, SSH, firewall, fail2ban, and umask

## What It Does Not Check

V1 explicitly does not include:

- automatic remediation
- remote host scanning
- a TUI or web UI
- daemon mode
- strong coupling to OpenClaw internal plugin systems
- mandatory network access
- a large-scale policy or rule platform

## Platform Support

- Linux: first-class support, including host and network checks
- macOS: core file and secret scans work, some host checks may be marked `skipped`
- Windows: recommended via WSL2 or another Unix-like environment

## Requirements

- Python 3.11+
- standard-library-first implementation with minimal dependencies

## Installation

### Editable install

```bash
git clone <your-repo-url>
cd openclaw-sec
python3 -m pip install -e .
```

### Run without install

```bash
PYTHONPATH=src python3 -m openclaw_sec audit
```

## Usage

V1 exposes a single subcommand:

```bash
openclaw-sec audit
```

Supported arguments:

```text
--config PATH
--workspace PATH
--output-dir PATH
--format text|json|md|all
--no-git
--no-host
--strict
--debug
```

Default behavior:

- `config`: `~/.openclaw/openclaw.json`
- `workspace`: if present, prefers `~/.openclaw/workspace`
- `output-dir`: `./openclaw-sec-report-<timestamp>`
- `format`: `all`

## Example

```bash
openclaw-sec audit --format all
```

Example terminal summary:

```text
OpenClaw-Sec Audit 0.1.0
Generated: 2026-03-17T15:00:00+00:00
Overall score: 48/100
Severity counts:
  critical: 2
  high: 3
  medium: 2
  low: 0
  info: 1

Top 5 findings:
  - [critical] PRIV-001 Plaintext secrets detected in OpenClaw config
  - [high] EXEC-002 Elevated or unrestricted exec appears enabled

Report files:
  json: /path/to/openclaw-sec-report-20260317-230000/report.json
  md: /path/to/openclaw-sec-report-20260317-230000/report.md
  text: /path/to/openclaw-sec-report-20260317-230000/summary.txt
```

## Demo Fixture

The repository includes a synthetic demo fixture under [`examples/redacted-lab`](./examples/redacted-lab/README.md).

It is designed for quick local trials and intentionally avoids storing pattern-matching fake secrets directly in Git. Instead, a generator script creates a local ignored environment that you can audit safely:

```bash
./examples/redacted-lab/generate_demo.sh
cd examples/redacted-lab/generated
PYTHONPATH=../../../src python3 -m openclaw_sec audit \
  --config ./openclaw.json \
  --workspace ./workspace \
  --output-dir ./report \
  --no-host \
  --no-git
```

## Report Outputs

The audit produces three report forms:

- terminal summary
- JSON report
- Markdown report

The JSON report includes at least:

- tool / version / mode / generated_at
- host information
- target information
- summary
- findings

Each finding includes at least:

- `id`
- `title`
- `category`
- `severity`
- `confidence`
- `heuristic`
- `evidence`
- `risk`
- `recommendation`
- `masked_examples`
- `references`

The Markdown report includes:

- Executive summary
- Score & severity counts
- Findings by severity
- Detailed evidence
- Fix recommendations
- Immediate next steps
- Limitations / unsupported checks

## Secret Redaction Policy

- the tool must never print full secrets in reports
- only masked values are allowed, for example `sk-****abcd`
- findings from logs, config, workspace, and Git only retain `masked_examples`
- the tool reports evidence and remediation guidance, not the leaked secret itself

## Heuristic OpenClaw Checks

The following OpenClaw-specific checks are heuristic and are explicitly marked `heuristic=true` in reports:

- suspicious public bind hints
- weak or missing auth hints
- sandbox disabled hints
- elevated exec hints
- missing allowFrom hints
- log hygiene hints
- insecure umask hints

The rule here is simple: prefer conservative, explainable warnings over blocking on incomplete schema details.

## OpenClaw Skill Wrapper

The repository includes a skill wrapper:

- `skills/openclaw-sec-audit/SKILL.md`
- `skills/openclaw-sec-audit/resources/run_audit.sh`

You can call it directly:

```bash
./skills/openclaw-sec-audit/resources/run_audit.sh --format all
```

The skill is expected to:

- avoid printing raw secrets
- summarize risks and remediation only
- order remediation steps by severity

## Development

Run tests:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Run a local verification:

```bash
PYTHONPATH=src python3 -m openclaw_sec audit --format all
```

## Repository Layout

```text
.
|-- README.md
|-- README.zh-CN.md
|-- LICENSE
|-- pyproject.toml
|-- src/
|   `-- openclaw_sec/
|       |-- cli.py
|       |-- audit.py
|       |-- models.py
|       |-- report.py
|       |-- utils.py
|       |-- detectors/
|       `-- data/
|-- skills/
|   `-- openclaw-sec-audit/
`-- tests/
```

## Design Principles

- independent detectors
- a central runner that aggregates findings
- clear separation between models and rendering
- unsupported checks must degrade gracefully
- heuristic checks must be explicitly labeled
- prioritize high-signal, explainable, locally verifiable checks

## Limitations

- V1 is not a vulnerability scanner or IDS
- host checks vary across platforms and may be best effort
- Git scanning only covers the current tree, not full history
- some OpenClaw config findings are heuristic signals, not proof of exploitation

## Roadmap

Good next steps after V1:

- deeper OpenClaw schema rules
- more accurate public exposure attribution
- stronger Git secret detection strategies
- richer log hygiene and rotation checks
- broader fixture coverage in tests

## Security Note

If the tool finds a real secret leak, do not stop at deleting the file content. The usual order is:

1. rotate or revoke the credential
2. remove it from config, logs, backups, and workspace artifacts
3. scrub repository history if the secret already reached a remote

## License

This project is released under the MIT License. See [LICENSE](./LICENSE).
