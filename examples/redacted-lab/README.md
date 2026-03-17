# Redacted Lab Demo

This example provides a safe, synthetic OpenClaw-like environment for trying `openclaw-sec` locally.

It does **not** store pattern-matching fake secrets directly in the repository. Instead, it generates them on demand into a local `generated/` directory that is ignored by Git.

## What It Demonstrates

The generated lab intentionally includes:

- plaintext secrets in `openclaw.json`
- plaintext secrets in `.env`
- secrets in workspace memory files
- secrets in log files
- risky OpenClaw config hints such as disabled sandboxing and unrestricted exec
- broad file permissions on selected files

## Generate The Demo Environment

From the repository root:

```bash
./examples/redacted-lab/generate_demo.sh
```

This creates:

```text
examples/redacted-lab/generated/
|-- openclaw.json
|-- .env
|-- logs/
|-- workspace/
`-- expected-findings.txt
```

## Run The Demo Audit

```bash
cd examples/redacted-lab/generated
PYTHONPATH=../../../src python3 -m openclaw_sec audit \
  --config ./openclaw.json \
  --workspace ./workspace \
  --output-dir ./report \
  --no-host \
  --no-git
```

The `--no-git` flag is intentional here. The demo is meant to focus on config, secret, filesystem, and workspace behavior rather than repository scanning.

## Expected Themes

The generated output should usually include findings in these areas:

- `PRIV-001`
- `PRIV-002`
- `PRIV-004`
- `PRIV-005`
- `FS-001`
- `FS-003`
- `FS-004`
- `EXEC-001`
- `EXEC-002`

Exact counts can change as detection logic evolves.
