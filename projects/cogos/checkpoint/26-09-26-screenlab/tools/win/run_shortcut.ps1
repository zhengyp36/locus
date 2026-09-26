# Launch a .lnk in assist's interactive session, emulating a human double-click
# (remote ssh is Session 0 and sees no desktop). Run as ADMIN. This exists to
# validate the W4 product entry — the desktop/Start-Menu shortcut — end to end,
# not just its target command.
param(
    [string]$Link = "C:\Users\assist\Desktop\screenlab-assist.lnk",
    [string]$Name = "screenlab-shortcut"
)
$ErrorActionPreference = "Stop"
$user = "TABLET-BBT8EQB4\assist"

$svc = New-Object -ComObject Schedule.Service
$svc.Connect()
$root = $svc.GetFolder("\")
try { $root.DeleteTask($Name, 0) } catch { }
$t = $svc.NewTask(0)
$t.RegistrationInfo.Description = "launch a shortcut in the interactive session (test harness)"
$t.Principal.UserId = $user
$t.Principal.LogonType = 3
$t.Principal.RunLevel = 0
$t.Settings.Enabled = $true
$t.Settings.AllowDemandStart = $true
$t.Settings.ExecutionTimeLimit = "PT0S"
$t.Settings.DisallowStartIfOnBatteries = $false
$act = $t.Actions.Create(0)
$act.Path = "C:\Windows\System32\cmd.exe"
$act.Arguments = "/c start `"`" `"$Link`""
$act.WorkingDirectory = "C:\Users\assist"
$root.RegisterTaskDefinition($Name, $t, 6, $null, $null, 3, $null) | Out-Null
$root.GetTask($Name).Run($null) | Out-Null
Write-Output "LAUNCHED=$Name LINK=$Link"
