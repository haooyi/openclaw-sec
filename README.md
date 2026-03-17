# openclaw-sec

`openclaw-sec` 是一个本地优先、少依赖的 OpenClaw 环境安全审计工具。

V1 目标很明确：

- 能在本机直接运行
- 能给出高信号、可解释的风险发现
- 能输出适合人工处理的摘要与报告
- 不做自动修复，不依赖联网，不依赖 LLM 才能完成检测

当前命令入口只有一个：

```bash
openclaw-sec audit
```

## Why

OpenClaw 常见的风险并不复杂，但很容易被忽略：

- 配置文件、备份文件、日志里遗留明文 secret
- `~/.openclaw`、`.env`、会话日志权限过宽
- workspace bootstrap / memory 文件里混入敏感信息
- 监听端口、SSH、firewall、fail2ban 等宿主机基础防护缺失
- Git 当前工作区中已经包含敏感信息

`openclaw-sec` 的目标不是“做全功能安全平台”，而是先把这些本地可验证、可解释、真正常见的问题抓出来。

## What It Checks

V1 重点覆盖以下几类检查：

- OpenClaw 配置文件存在性、可解析性和高风险启发式配置
- 明文 secrets 是否出现在 config、`.env`、备份文件、workspace 文档、日志、Git tracked files 中
- `~/.openclaw`、配置文件、环境文件、日志文件权限是否过宽
- 关键路径是否存在 symlink 越界风险
- Linux 主机上的监听端口、SSH、firewall、fail2ban、umask 基础风险

## What It Does Not Check

V1 明确不做这些事：

- 自动修复
- 远程主机扫描
- TUI / Web UI
- daemon 模式
- 强依赖 OpenClaw 内部插件机制
- 强制联网
- 大规模规则平台化

## Platform Support

- Linux: 一等支持，包含 host / network 检查
- macOS: 可运行基础文件与 secret 检查，部分 host 检查可能显示为 `skipped`
- Windows: 建议在 WSL2 或其他类 Unix 环境中运行

## Requirements

- Python 3.11+
- 尽量少依赖，当前实现基于标准库

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

V1 只提供一个子命令：

```bash
openclaw-sec audit
```

支持参数：

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

默认行为：

- `config`: `~/.openclaw/openclaw.json`
- `workspace`: 若存在，优先使用 `~/.openclaw/workspace`
- `output-dir`: `./openclaw-sec-report-<timestamp>`
- `format`: `all`

## Example

```bash
openclaw-sec audit --format all
```

示例摘要：

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

## Report Outputs

审计会输出三类结果：

- 终端摘要
- JSON 报告
- Markdown 报告

JSON 报告至少包含：

- tool / version / mode / generated_at
- host 信息
- target 信息
- summary
- findings

每条 finding 至少包含：

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

Markdown 报告包含：

- Executive summary
- Score & severity counts
- Findings by severity
- Detailed evidence
- Fix recommendations
- Immediate next steps
- Limitations / unsupported checks

## Secret Redaction Policy

- 报告中严禁输出完整 secret
- 仅允许输出 masked 形式，例如 `sk-****abcd`
- 日志、配置、workspace、Git 的检测结果只保留 `masked_examples`
- 如发现 secret，工具输出的是审计证据和修复建议，不是泄漏内容本身

## Heuristic OpenClaw Checks

以下 OpenClaw-specific 检查属于启发式结论，报告中会显式标记 `heuristic=true`：

- suspicious public bind
- weak or missing auth hints
- sandbox disabled hints
- elevated exec hints
- missing allowFrom hints
- log hygiene hints
- insecure umask hints

这类规则遵循一个原则：宁可保守提示，也不因为 schema 细节未完全确定而阻塞本地审计。

## OpenClaw Skill Wrapper

仓库内提供了 skill 包装：

- `skills/openclaw-sec-audit/SKILL.md`
- `skills/openclaw-sec-audit/resources/run_audit.sh`

可以直接通过 wrapper 调用：

```bash
./skills/openclaw-sec-audit/resources/run_audit.sh --format all
```

skill 输出要求：

- 不展示原始 secrets
- 只总结风险与修复建议
- 修复建议按优先级排序

## Development

运行测试：

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

本地验证：

```bash
PYTHONPATH=src python3 -m openclaw_sec audit --format all
```

## Repository Layout

```text
.
├─ README.md
├─ pyproject.toml
├─ src/
│  └─ openclaw_sec/
│     ├─ cli.py
│     ├─ audit.py
│     ├─ models.py
│     ├─ report.py
│     ├─ utils.py
│     ├─ detectors/
│     └─ data/
├─ skills/
│  └─ openclaw-sec-audit/
└─ tests/
```

## Design Principles

- detector 独立
- 中央 runner 聚合 findings
- 模型与渲染分层
- 不支持的检查不能导致程序崩溃
- 启发式检查必须显式标记
- 优先做高信号、可解释、可本地验证的检查

## Limitations

- V1 不是漏洞扫描器，也不是入侵检测系统
- host 检查存在平台差异，某些环境只能 best effort
- Git 扫描当前只覆盖 current tree，不扫描完整历史
- 某些 OpenClaw 配置结论是启发式提示，不等于确定漏洞

## Roadmap

后续适合继续补的方向：

- 更细的 OpenClaw schema 规则
- 更准确的公网暴露归因
- 更强的 Git secret 扫描策略
- 更细的日志卫生与轮转检查
- 更完整的测试样本库

## Security Note

如果你用它扫到了真实 secret 泄漏，不要只删除文件内容。正确顺序通常是：

1. 先旋转或废弃凭据
2. 再清理配置、日志、备份和工作区痕迹
3. 如果已进入 Git 远程，再处理仓库历史

## License

暂未附带许可证文件。公开到 GitHub 之前，建议先补一个明确的开源许可证，否则别人默认没有合法复用权限。
