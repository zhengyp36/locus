# 62c: run a probe script inside assist's INTERACTIVE session (Session 7), not
# the ssh Session 0. Same Task Scheduler COM + interactive-token pattern as
# tools/win/launch_daemon.ps1. Run as ADMIN over ssh.
param(
    [Parameter(Mandatory=$true)][string]$Script,
    [string]$Name = "screenlab-62c-probe",
    [string]$Out
)
$ErrorActionPreference = "Stop"
$user = "TABLET-BBT8EQB4\assist"
$dir  = "C:\Users\assist\screenlab-62c"
$py   = "C:\Users\assist\AppData\Local\screenlab\venv\Scripts\python.exe"
if (-not $Out) { $Out = ($Script -replace '\.py$','') + ".out" }

$svc = New-Object -ComObject Schedule.Service
$svc.Connect()
$root = $svc.GetFolder("\")
try { $root.DeleteTask($Name, 0) } catch { }
$t = $svc.NewTask(0)
$t.RegistrationInfo.Description = "62c probe: $Script"
$t.Principal.UserId = $user
$t.Principal.LogonType = 3
$t.Principal.RunLevel = 0
$t.Settings.Enabled = $true
$t.Settings.AllowDemandStart = $true
$t.Settings.ExecutionTimeLimit = "PT0S"
$t.Settings.DisallowStartIfOnBatteries = $false
$t.Settings.StopIfGoingOnBatteries = $false
$act = $t.Actions.Create(0)
$act.Path = "C:\Windows\System32\cmd.exe"
$cmdline = "`"$py`" `"$dir\$Script`" > `"$dir\$Out`" 2>&1"
$act.Arguments = "/c `"$cmdline`""
$act.WorkingDirectory = $dir
$root.RegisterTaskDefinition($Name, $t, 6, $null, $null, 3, $null) | Out-Null
$root.GetTask($Name).Run($null) | Out-Null
Write-Output "LAUNCHED=$Name OUT=$Out"
