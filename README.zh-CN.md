# openclaw-sec

[English README](./README.md)

`openclaw-sec` 是一个本地优先、少依赖的 OpenClaw 环境安全审计工具。

V1 的目标很明确：

- 能在本机直接运行
- 能输出高信号、可解释的风险发现
- 能给出适合人工处理的摘要与报告
- 不做自动修复、不依赖联网、不依赖 LLM 才能完成检测

当前命令入口只有一个：

```bash
openclaw-sec audit
```

## 为什么做这个工具

OpenClaw 常见的风险并不复杂，但很容易被忽略：

- 配置文件、备份文件、日志中残留明文 secret
- `~/.openclaw`、`.env`、会话产物权限过宽
- 敏感内容被写进 workspace bootstrap 或 memory 文件
- 宿主机在监听端口、SSH、firewall、fail2ban 等方面缺少基础加固
- 当前 Git 工作区里已经包含敏感信息

`openclaw-sec` 不是为了做一个全功能安全平台。V1 的重点是尽快抓住这些常见、可本地验证、可解释的问题。

## 检查范围

V1 重点覆盖：

- OpenClaw 配置文件存在性、可解析性和高风险启发式配置
- config、`.env`、备份文件、workspace 文档、日志、Git tracked files 中的明文 secret
- `~/.openclaw`、配置文件、环境文件、日志文件的过宽权限
- 安全敏感路径的 symlink 越界风险
- 以 Linux 为主的监听端口、SSH、firewall、fail2ban、umask 检查

## 不做什么

V1 明确不包含：

- 自动修复
- 远程主机扫描
- TUI / Web UI
- daemon 模式
- 强依赖 OpenClaw 内部插件体系
- 强制联网
- 大规模规则平台化

## 平台支持

- Linux：一等支持，包含 host / network 检查
- macOS：可运行基础文件和 secret 检查，部分 host 检查可能显示为 `skipped`
- Windows：建议通过 WSL2 或其他类 Unix 环境运行

## 环境要求

- Python 3.11+
- 当前实现尽量使用标准库，依赖较少

## 安装

### 可编辑安装

```bash
git clone <your-repo-url>
cd openclaw-sec
python3 -m pip install -e .
```

### 不安装直接运行

```bash
PYTHONPATH=src python3 -m openclaw_sec audit
```

## 使用方式

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
- `workspace`: 若存在，则优先使用 `~/.openclaw/workspace`
- `output-dir`: `./openclaw-sec-report-<timestamp>`
- `format`: `all`

## 示例

```bash
openclaw-sec audit --format all
```

示例终端摘要：

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

## 报告输出

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

## Secret 脱敏策略

- 报告中绝不输出完整 secret
- 只允许输出脱敏后的 masked 值，例如 `sk-****abcd`
- 日志、配置、workspace、Git 的检测结果只保留 `masked_examples`
- 工具输出的是证据和修复建议，不是泄漏内容本身

## OpenClaw 启发式检查

以下 OpenClaw 专项规则属于启发式结论，会在报告中显式标记 `heuristic=true`：

- suspicious public bind hints
- weak or missing auth hints
- sandbox disabled hints
- elevated exec hints
- missing allowFrom hints
- log hygiene hints
- insecure umask hints

原则很简单：宁可给出保守、可解释的提醒，也不因为 schema 细节不完整而阻塞本地审计。

## OpenClaw Skill 包装

仓库内提供了 skill wrapper：

- `skills/openclaw-sec-audit/SKILL.md`
- `skills/openclaw-sec-audit/resources/run_audit.sh`

可以直接调用：

```bash
./skills/openclaw-sec-audit/resources/run_audit.sh --format all
```

skill 的输出要求：

- 不展示原始 secret
- 只总结风险与修复建议
- 修复建议按严重级别排序

## 开发

运行测试：

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

运行本地验证：

```bash
PYTHONPATH=src python3 -m openclaw_sec audit --format all
```

## 仓库结构

```text
.
├─ README.md
├─ README.zh-CN.md
├─ LICENSE
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

## 设计原则

- detector 独立
- 中央 runner 统一聚合 findings
- 模型与渲染解耦
- 不支持的检查必须优雅降级
- 启发式检查必须明确标记
- 优先做高信号、可解释、可本地验证的检查

## 当前限制

- V1 不是漏洞扫描器，也不是入侵检测系统
- host 检查存在平台差异，很多场景只能 best effort
- Git 扫描目前只覆盖当前 tree，不扫描完整历史
- 某些 OpenClaw 配置结论属于启发式信号，不等于已被利用

## Roadmap

V1 之后适合继续补的方向：

- 更细的 OpenClaw schema 规则
- 更准确的公网暴露归因
- 更强的 Git secret 检测策略
- 更细的日志卫生和 rotation 检查
- 更完整的测试样本库

## 安全说明

如果工具发现了真实 secret 泄漏，不要只删除文件内容。通常正确顺序是：

1. 先旋转或废弃凭据
2. 再清理配置、日志、备份和 workspace 痕迹
3. 如果 secret 已进入 Git 远程，再处理仓库历史

## 许可证

本项目使用 MIT License。详见 [LICENSE](./LICENSE)。
