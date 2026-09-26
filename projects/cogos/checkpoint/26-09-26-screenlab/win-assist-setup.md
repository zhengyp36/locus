# screenlab Windows 3a · `assist` 账户创建与准备

> 在 Windows 机（tablet-bbt8eqb4 / 100.112.50.115）上、**以管理员**执行。
> 目标：一个**标准（非管理员）**本地账户 `assist`，供真人在其上操作、agent 接入协助。
> 三件事：① 创建 ② 登录一次生成 profile ③（推荐）配置免密 ssh，便于我部署。

---

## 1) 创建标准账户（管理员 PowerShell）

```powershell
# 会让你输入密码（自己记住，规则宽松即可）
$pw = Read-Host -AsSecureString "给 assist 设密码"
New-LocalUser -Name assist -Password $pw -PasswordNeverExpires `
  -Description "screenlab 3a assist target"

# 确认：在 Users 组、不在 Administrators 组
Remove-LocalGroupMember -Group Administrators -Member assist -ErrorAction SilentlyContinue
Get-LocalGroupMember -Group Users | Where-Object Name -like '*assist'
```

> cmd 等价写法（管理员 cmd，密码明文）：
> ```
> net user assist <你的密码> /add
> ```

## 2) 注销 → 用 `assist` 登录一次（生成 profile）→ 切回 `zhengyp`

这一步必须做：没有 profile，第 3 步和后续部署都落不了地。

## 3)（推荐）配置免密 ssh（管理员 PowerShell；assist 的 profile 已存在后再做）

```powershell
$ak = "C:\Users\assist\.ssh\authorized_keys"
New-Item -ItemType Directory -Force C:\Users\assist\.ssh | Out-Null
@'
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINYoGoeop3pC9ikZFoCo/QyffZXkHpQLR8P+lHoz8JGY zhengyp36@gmail.com
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCPbYgtfAXh2axR/FXklmODXCdp3wSWLZwLZPZAzMVvt3hlkhhCngpvwfgIwgCxlamx2FUo4CWAoTo+mfuvCgq6d2ihF4t7UhxDSO3Gs8kPP8ZUhPQHMZbOCX3Slh1Q8ryCJ8z4IkTkVm0pmLVJoSxQFUzq7F5VAdSh4qz3E+S2hs4b3YPSBEvzkMmZC0g7H9G2ANXysZlB1mdF9tEtMmSim7suApud/zD2utkMYD7ibKJjscyN5UzoZP5RmZ25l8dAWiwUpucW3kGPeLXiOUfx7GkZsKSLsPLuY7szEipD3ZgS40iKOni3NMbeK+punKkBUVtnm0iZvkRVVEWDG2r7M2l8bI8SHZ3rVotAPtFJkGV+Dnyn8r/xfkdTbdQMS9fe6NBNac/RpH1aUvDcJI5y9kfopJkH3GEC1UCetnXnsjc9qtupM+YG/k+qDAC22YHZ03v0bY7+vdVR77sk3AxRqLee6Igzwi0+S/V/LvvfqX3NokVUhzdOX2DMkVkhgkE= zhengyp@10.0.2.15
'@ | Set-Content -Encoding ascii $ak

# OpenSSH 要求属主可写、他人不可写
icacls C:\Users\assist\.ssh /inheritance:r
icacls C:\Users\assist\.ssh /grant "assist:(OI)(CI)F" "SYSTEM:(OI)(CI)F" "Administrators:(OI)(CI)F"
icacls $ak /inheritance:r
icacls $ak /grant "assist:F" "SYSTEM:F" "Administrators:F"
```

## 4) 告知我

我会从 Linux 侧验证：`ssh assist@100.112.50.115 whoami` → 应回 `tablet-bbt8eqb4\assist`，然后进 W1。

---

### 说明 / 边界

- `assist` 必须是**标准账户**（与已定 Windows 形态一致：专用非管理员账户）。
- 若第 3 步不做，就把密码告诉我（但 Windows OpenSSH 可能禁用了密码登录，届时仍需走第 3 步）。
- 清理（测试结束）：`Remove-LocalUser -Name assist` + 删除 `C:\Users\assist`（或保留由你决定）。
