from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from openclaw_sec.detectors.config_scan import load_and_scan_config
from openclaw_sec.detectors.fs_scan import scan_filesystem
from openclaw_sec.detectors.host_scan import scan_host
from openclaw_sec.detectors.secret_scan import scan_secrets
from openclaw_sec.models import AuditContext, AuditReport, Finding
from openclaw_sec.report import render_markdown
from openclaw_sec.utils import CommandResult, find_secret_hits


REPO_ROOT = Path(__file__).resolve().parents[1]


class OpenClawSecTests(unittest.TestCase):
    def make_context(self, root: Path, config_name: str = "openclaw.json") -> AuditContext:
        return AuditContext(
            config_path=root / config_name,
            workspace_path=root / "workspace" if (root / "workspace").exists() else None,
            output_dir=root / "out",
            output_format="all",
            enable_git=False,
            enable_host=False,
            strict=False,
            debug=False,
            current_dir=root,
        )

    def test_config_missing_returns_info(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            findings, parsed = load_and_scan_config(self.make_context(root))
            self.assertIsNone(parsed)
            self.assertEqual(findings[0].id, "CFG-001")
            self.assertEqual(findings[0].severity, "info")

    def test_config_parse_error_returns_high(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "openclaw.json").write_text("{bad json", encoding="utf-8")
            findings, parsed = load_and_scan_config(self.make_context(root))
            self.assertIsNone(parsed)
            self.assertEqual(findings[0].id, "CFG-002")
            self.assertEqual(findings[0].severity, "high")

    def test_config_success_detects_exec_and_sandbox_hints(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "openclaw.json").write_text(
                '{"browser":{"noSandbox":true},"tools":{"allow":["exec"],"exec":{"security":"full","ask":"off"}}}',
                encoding="utf-8",
            )
            findings, parsed = load_and_scan_config(self.make_context(root))
            self.assertIsNotNone(parsed)
            ids = {finding.id for finding in findings}
            self.assertIn("EXEC-001", ids)
            self.assertIn("EXEC-002", ids)

    def test_secret_redaction_masks_values(self) -> None:
        hits = find_secret_hits('OPENAI_API_KEY="sk-abcdefghijklmnopqrstuvwxyz123456"\nTOKEN=ghp_abcdefghijklmnopqrstuvwxyz1234\n')
        masked = [hit.masked_value for hit in hits]
        self.assertTrue(any(value.startswith("sk-a****") for value in masked))
        self.assertTrue(any(value.startswith("ghp_****") for value in masked))

    def test_backup_file_detection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "openclaw.json").write_text("{}", encoding="utf-8")
            (root / "secret.env.bak").write_text("OPENAI_API_KEY=sk-abcdefghijklmnopqrstuvwxyz123456", encoding="utf-8")
            findings = scan_secrets(self.make_context(root))
            ids = {finding.id for finding in findings}
            self.assertIn("PRIV-003", ids)

    def test_env_without_secret_does_not_create_secret_finding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "openclaw.json").write_text("{}", encoding="utf-8")
            (root / ".env").write_text("HELLO=world", encoding="utf-8")
            findings = scan_secrets(self.make_context(root))
            ids = {finding.id for finding in findings}
            self.assertNotIn("PRIV-002", ids)

    def test_permission_detection_on_config_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "openclaw.json"
            config.write_text("{}", encoding="utf-8")
            config.chmod(0o644)
            findings = scan_filesystem(self.make_context(root))
            ids = {finding.id for finding in findings}
            self.assertIn("FS-001", ids)

    def test_symlink_escape_detection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root.parent / "outside-secret.json"
            target.write_text("{}", encoding="utf-8")
            config = root / "openclaw.json"
            config.symlink_to(target)
            findings = scan_filesystem(self.make_context(root))
            ids = {finding.id for finding in findings}
            self.assertIn("FS-005", ids)

    def test_report_rendering_contains_required_sections(self) -> None:
        finding = Finding(
            id="PRIV-001",
            title="Plaintext secrets detected in OpenClaw config",
            category="secrets",
            severity="critical",
            confidence="high",
            heuristic=False,
            evidence=["/tmp/openclaw.json:1 (openai_key)"],
            risk="secret exposure",
            recommendation="rotate it",
            masked_examples=["sk-a****3456"],
            references=["config"],
        )
        report = AuditReport(
            tool="openclaw-sec",
            version="0.1.0",
            mode="audit",
            generated_at="2026-03-17T00:00:00+00:00",
            host={},
            target={},
            summary={"score": 75, "severity_counts": {"critical": 1, "high": 0, "medium": 0, "low": 0, "info": 0}, "top_findings": [finding.to_dict()], "finding_count": 1},
            findings=[finding],
            notes=["HOST-004 skipped"],
        )
        rendered = render_markdown(report)
        self.assertIn("## Executive summary", rendered)
        self.assertIn("## Findings by severity", rendered)
        self.assertIn("## Detailed evidence", rendered)
        self.assertIn("## Immediate next steps", rendered)
        self.assertIn("## Limitations / unsupported checks", rendered)

    def test_host_scan_graceful_degradation(self) -> None:
        failed = CommandResult(ok=False, returncode=127, stdout="", stderr="missing", command=["test"])
        with mock.patch("openclaw_sec.detectors.host_scan.run_command", return_value=failed):
            findings, _, notes = scan_host()
        self.assertIsInstance(findings, list)
        self.assertTrue(any("skipped" in note for note in notes))

    def test_standalone_skill_bundle_runs_without_repo_imports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            skill_root = temp_root / "openclaw-sec-audit"
            resources_dir = skill_root / "resources"
            resources_dir.mkdir(parents=True)
            wrapper_source = REPO_ROOT / "skills" / "openclaw-sec-audit" / "resources" / "run_audit.sh"
            wrapper_target = resources_dir / "run_audit.sh"
            wrapper_target.write_text(wrapper_source.read_text(encoding="utf-8"), encoding="utf-8")
            wrapper_target.chmod(0o755)
            build = subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts" / "build_skill_bundle.py"), "--output", str(resources_dir / "runtime")],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(build.returncode, 0, build.stderr)
            self.assertTrue((resources_dir / "runtime" / "openclaw_sec" / "__main__.py").exists())

            fixture_root = temp_root / "fixture"
            workspace = fixture_root / "workspace"
            logs = fixture_root / "logs"
            workspace.mkdir(parents=True)
            logs.mkdir(parents=True)
            (fixture_root / "openclaw.json").write_text(
                '{"env":{"OPENAI_API_KEY":"sk-proj-demoDEMOdemoDEMOdemoDEMO1234"},"browser":{"noSandbox":true},"tools":{"allow":["exec"],"exec":{"security":"full","ask":"off"}},"auth":{"profiles":{}}}',
                encoding="utf-8",
            )
            (fixture_root / ".env").write_text("TOKEN=ghp_demoDEMOdemoDEMOdemoDEMO12345678\n", encoding="utf-8")
            (workspace / "MEMORY.md").write_text("Bearer demoDEMOdemoDEMOdemoDEMOtoken1234567890\n", encoding="utf-8")
            (logs / "session.jsonl").write_text(
                '{"content":"Stored synthetic key sk-ant-demoDEMOdemoDEMOdemoDEMO123456"}\n',
                encoding="utf-8",
            )

            report_dir = fixture_root / "report"
            env = os.environ.copy()
            env.pop("PYTHONPATH", None)
            run = subprocess.run(
                [
                    str(wrapper_target),
                    "--config",
                    str(fixture_root / "openclaw.json"),
                    "--workspace",
                    str(workspace),
                    "--output-dir",
                    str(report_dir),
                    "--no-host",
                    "--no-git",
                ],
                cwd=temp_root,
                env=env,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertIn("Plaintext secrets detected in OpenClaw config", run.stdout)
            self.assertTrue((report_dir / "report.json").exists())
            self.assertTrue((report_dir / "report.md").exists())
            self.assertTrue((report_dir / "summary.txt").exists())


if __name__ == "__main__":
    unittest.main()
