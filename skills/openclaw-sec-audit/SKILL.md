# OpenClaw Security Audit

## 用途

对本机 OpenClaw 安装与运行环境执行本地安全审计，输出高信号风险、受影响位置和修复建议。

## 何时触发

- 用户要求检查 OpenClaw 当前环境是否安全
- 用户怀疑存在 API Key、日志泄漏、权限过宽或公网暴露问题
- 用户希望获得一份本地可执行的安全报告

## 执行方式

使用本地 shell 能力运行 `resources/run_audit.sh`。该脚本会定位项目根目录，并调用本地 `openclaw-sec audit` CLI。

## 输出要求

- 不得展示原始 secrets
- 只输出风险摘要、受影响文件位置、优先级和修复建议
- 修复建议按 `critical -> high -> medium -> low` 排序
- 若某些宿主机检查不支持或权限不足，明确说明 `skipped` 或 `unsupported`

## 建议调用

```bash
./skills/openclaw-sec-audit/resources/run_audit.sh --format all
```
