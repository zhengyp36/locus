# 授权问题与权限简化（2026-08-14）

人机配合中"频繁授权打断"的解法：权限白名单反转成黑名单。

## 问题

- 现象：AI 每碰到未授权命令就打断请求授权，用户逐个 allow；全局配置里 bash 白名单堆到 143 条，仍反复触发。
- 根因：白名单的枚举对象是"所有常见命令"，无限、枚举不完，必然漏、必然打断。

## 结论：反转成黑名单

- 原则：默认 allow，只枚举少数"危险命令"设 deny/ask。黑名单对象是"危险命令"，有限且稳定。
- 分级：
  - deny（拦死，不可逆/灾难）：force push、删根/家目录、远程管道执行、格式化磁盘。
  - ask（保留一次确认，高危但可能真要做）：提权、改属主、宽松权限、hard reset、dd、crontab、iptables、systemctl、docker rm、reboot。
- 匹配规则：last-match-wins——`*` 兜底放最前，具体规则放后（Kilo/opencode 文档确认）。

## 落点

- Kilo 全局配置 `~/.config/kilo/kilo.jsonc` 的 `permission` 字段：bash 143 条白名单 → `"*": "allow"` + 39 条 deny/ask；新增 `edit: {"*": "allow"}`；read/external_directory 原样。

## deny 清单

- `git push --force*` / `git push -f*`
- `rm -rf /*` / `rm -rf ~/*` / `rm -rf /` / `rm -rf ~` / `rm -fr /*`
- `curl * | sh` / `curl * | bash` / `wget * | sh`
- `bash <(curl *` / `sh <(curl *`
- `mkfs *`

## ask 清单

- `sudo *`、`chown *`、`chmod 777 *`、`chmod -R 777 *`
- `git reset --hard*`、`git clean *`、`git stash drop*`、`git push *--delete*`（删远程分支）、`git push --force-with-lease*`
- `dd *`、`crontab *`、`iptables *`
- `systemctl *`（例外：`systemctl --user *`、`systemctl is-active *` 保留 allow）
- `docker rm *`、`docker system prune*`、`reboot*`、`shutdown*`

## 遗留提醒

- `read: {"*": "allow"}` 覆盖了默认 `.env` deny，AI 目前能读 .env，未收紧（待用户决定）。
- 可选更激进：`--auto` 运行时开关（TUI 命令面板 "Enable auto-approve permissions"），deny 仍生效。
- 配置在 Kilo 启动时加载，改后需重启会话生效。
