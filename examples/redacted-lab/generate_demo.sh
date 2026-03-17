#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
OUT_DIR="${SCRIPT_DIR}/generated"

rm -rf "${OUT_DIR}"
mkdir -p "${OUT_DIR}/workspace" "${OUT_DIR}/logs"

cat > "${OUT_DIR}/openclaw.json" <<'EOF'
{
  "env": {
    "OPENAI_API_KEY": "sk-proj-demoDEMOdemoDEMOdemoDEMO1234",
    "OPENAI_BASE_URL": "https://example.invalid/v1"
  },
  "browser": {
    "enabled": true,
    "headless": true,
    "noSandbox": true
  },
  "tools": {
    "allow": ["exec", "read", "write"],
    "exec": {
      "security": "full",
      "ask": "off"
    }
  },
  "auth": {
    "profiles": {}
  }
}
EOF

cat > "${OUT_DIR}/.env" <<'EOF'
GITHUB_TOKEN=ghp_demoDEMOdemoDEMOdemoDEMO12345678
SLACK_TOKEN=xoxb-demoDEMOdemoDEMOdemoDEMO
EOF

cat > "${OUT_DIR}/workspace/MEMORY.md" <<'EOF'
# Memory

Synthetic example token:

Bearer demoDEMOdemoDEMOdemoDEMOtoken1234567890
EOF

cat > "${OUT_DIR}/workspace/TOOLS.md" <<'EOF'
# Tools

Synthetic Telegram bot token:

123456789:DEMOdemoDEMOdemoDEMOdemoTOKEN
EOF

cat > "${OUT_DIR}/logs/session.jsonl" <<'EOF'
{"type":"message","content":"Stored synthetic key sk-ant-demoDEMOdemoDEMOdemoDEMO123456"}
{"type":"message","content":"Observed synthetic bearer token Bearer demoDEMOdemoDEMOdemoDEMOtoken1234567890"}
EOF

cat > "${OUT_DIR}/expected-findings.txt" <<'EOF'
Expected finding themes for this generated demo:
- PRIV-001
- PRIV-002
- PRIV-004
- PRIV-005
- FS-001
- FS-003
- FS-004
- EXEC-001
- EXEC-002
EOF

chmod 644 "${OUT_DIR}/openclaw.json" "${OUT_DIR}/.env" "${OUT_DIR}/logs/session.jsonl"

echo "Generated demo environment at: ${OUT_DIR}"
echo "Run it with:"
echo "  cd ${OUT_DIR}"
echo "  PYTHONPATH=../../../src python3 -m openclaw_sec audit --config ./openclaw.json --workspace ./workspace --output-dir ./report --no-host --no-git"
