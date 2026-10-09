# sources（可复现）

- **Claude Code 2.1.295 官方正文**：`claude-code-2.1.295-prompt.md`（157635 bytes）
  - URL: https://raw.githubusercontent.com/WEIFENG2333/phistory/main/captures/claude-code/2.1.295/variants/default/prompt.md
  - 抓取方法：phistory 用 claude-tap 安装精确版本 CLI、拦截 prompt-bearing HTTP 请求体（不调真实模型），`prompt.md` 由 archived trace 渲染。
  - 分层：Block 1 计费头 / **Block 2+3 官方正文（分析对象）** / Block 4 环境快照＋agent/skill 清单（动态注入） / Messages 会话注入 / Tools 工具 schema（动态注入）。
  - 注：Anthropic 未官方公开此 prompt；此为抓包 payload，非模型回忆。工具 schema/环境快照/CLAUDE.md 非官方正文，须剥离。

- **Kilo 7.8.8 主 agent prompt**：`kilo-7.8.8-primary-agent-prompt.md`（8504 bytes）
  - 来源：本地二进制 `~/.nvm/versions/node/*/lib/node_modules/@kilocode/cli/bin/.kilo`（bun 打包，字符串明文未加密）。
  - 提取方法：grep -a 定位 `You are Kilo` 8 个变体 → 主 agent = `interactive CLI tool` 变体（offset 213323361）→ 读到第一个 NUL 字节（UTF-16 边界）截断。
  - 注：同二进制内还混有 UTF-16 编码的其他 agent prompt（如 "agent - please keep going" 长文），非主 agent，已排除。
