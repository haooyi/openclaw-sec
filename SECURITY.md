# Security Policy

## Reporting a Vulnerability

If you believe you found a security issue in `openclaw-sec` itself, please avoid opening a public GitHub issue with sensitive details.

Instead, report it privately to:

- `haooyi@gmail.com`

Please include:

- a clear description of the issue
- affected versions or commit hashes, if known
- reproduction steps or proof of concept
- impact assessment
- any suggested remediation

## Scope

This policy covers vulnerabilities in the `openclaw-sec` codebase, packaging, and project-maintained workflows.

Examples:

- raw secret disclosure in reports where masking should have applied
- command execution behavior that exceeds documented intent
- unsafe file handling in project-owned code
- CI or release workflow weaknesses in this repository

This policy does not cover:

- insecure OpenClaw deployments detected by the tool
- secrets already leaked in a user environment before running the tool
- third-party service outages or upstream vulnerabilities outside this repository

## Supported Versions

At this stage, security fixes are expected on the latest `main` branch.

Older commits or private forks may not receive coordinated patches.

## Disclosure Expectations

- please allow a reasonable time window for triage and remediation before public disclosure
- do not include real active credentials in reports
- if a proof of concept needs a secret-like value, use synthetic test material only
