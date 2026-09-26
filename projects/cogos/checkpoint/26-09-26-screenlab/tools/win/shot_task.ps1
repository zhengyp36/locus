# One-shot ground-truth screen grab in assist's interactive session.
# Requires tools/win/shot.py to already be at <prefix>\shot.py.
# Run as ADMIN; then pull <prefix>\tray_shot.png.
$ErrorActionPreference = "Stop"
$user = "TABLET-BBT8EQB4\assist"
$name = "screenlab-shot"
$prefix = "C:\Users\assist\AppData\Local\screenlab"
$exe = Join-Path $prefix "venv\Scripts\pythonw.exe"

$svc = New-Object -ComObject Schedule.Service
$svc.Connect()
$root = $svc.GetFolder("\")
$t = $svc.NewTask(0)
$t.RegistrationInfo.Description = "one-shot screen grab"
$t.Principal.UserId = $user
$t.Principal.LogonType = 3
$t.Principal.RunLevel = 0
$t.Settings.Enabled = $true
$t.Settings.AllowDemandStart = $true
$t.Settings.ExecutionTimeLimit = "PT0S"
$act = $t.Actions.Create(0)
$act.Path = $exe
$act.Arguments = "shot.py"
$act.WorkingDirectory = $prefix
$root.RegisterTaskDefinition($name, $t, 6, $null, $null, 3, $null) | Out-Null
$root.GetTask($name).Run($null) | Out-Null
Write-Output "SHOT_LAUNCHED"
