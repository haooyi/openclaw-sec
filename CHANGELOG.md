# Changelog

All notable changes to this project will be documented in this file.

The format is inspired by Keep a Changelog, but kept intentionally lightweight for this repository.

## [Unreleased]

- No unreleased changes yet.

## [0.1.0] - 2026-03-18

### Added

- initial `openclaw-sec audit` CLI
- text, JSON, and Markdown report rendering
- detectors for config, secrets, filesystem, Git, network, and host checks
- masking rules for secret-like values
- OpenClaw skill wrapper under `skills/openclaw-sec-audit/`
- English and Simplified Chinese READMEs
- MIT license
- unit tests for key V1 behaviors

### Notes

- V1 is intentionally local-first and does not perform auto-remediation.
