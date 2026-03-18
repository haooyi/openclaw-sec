from __future__ import annotations

import argparse
import shutil
import tempfile
import zipapp
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = REPO_ROOT / "src" / "openclaw_sec"
DEFAULT_OUTPUT = REPO_ROOT / "skills" / "openclaw-sec-audit" / "resources" / "openclaw-sec.pyz"
IGNORE_NAMES = {"__pycache__"}
IGNORE_SUFFIXES = {".pyc", ".pyo"}


def build_bundle(output_path: Path, package_root: Path = PACKAGE_ROOT) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        staging_root = Path(tmp)
        staged_package = staging_root / "openclaw_sec"
        shutil.copytree(package_root, staged_package, ignore=_ignore_paths)
        zipapp.create_archive(
            staging_root,
            target=output_path,
            interpreter="/usr/bin/env python3",
            main="openclaw_sec.cli:main",
            compressed=True,
        )
    output_path.chmod(0o755)
    return output_path


def _ignore_paths(_: str, names: list[str]) -> set[str]:
    ignored = {name for name in names if name in IGNORE_NAMES}
    ignored.update(name for name in names if Path(name).suffix in IGNORE_SUFFIXES)
    return ignored


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the standalone skill bundle for openclaw-sec")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Output path for the generated .pyz bundle")
    parser.add_argument("--package-root", default=str(PACKAGE_ROOT), help="Path to the openclaw_sec package source")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    output = Path(args.output).expanduser().resolve()
    package_root = Path(args.package_root).expanduser().resolve()
    bundle_path = build_bundle(output, package_root)
    print(bundle_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
