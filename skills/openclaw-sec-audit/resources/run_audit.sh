#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
BUNDLE_PATH="${SCRIPT_DIR}/openclaw-sec.pyz"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required to run openclaw-sec-audit." >&2
  exit 127
fi

if [[ ! -f "${BUNDLE_PATH}" ]]; then
  echo "Bundled runtime not found: ${BUNDLE_PATH}" >&2
  echo "Rebuild it with: python3 scripts/build_skill_bundle.py" >&2
  exit 1
fi

exec python3 "${BUNDLE_PATH}" audit "$@"
