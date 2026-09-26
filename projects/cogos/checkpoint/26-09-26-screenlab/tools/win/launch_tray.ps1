# Start the resident tray/consent entry inside assist's interactive session.
# Run as ADMIN over ssh. W3 test harness; product path is W4 (desktop shortcut).
$ErrorActionPreference = "Stop"
$user = "TABLET-BBT8EQB4\assist"
$name = "screenlab-tray"
$prefix = "C:\Users\assist\AppData\Local\screenlab"
$exe = Join-Path $prefix "venv\Scripts\pythonw.exe"
$reg = "C:\Users\assist\.config\screenlab\registry"

$svc = New-Object -ComObject Schedule.Service
$svc.Connect()
$root = $svc.GetFolder("\")
$t = $svc.NewTask(0)
$t.RegistrationInfo.Description = "screenlab tray entry (session injection harness)"
$t.Principal.UserId = $user
$t.Principal.LogonType = 3
$t.Principal.RunLevel = 0
$t.Settings.Enabled = $true
$t.Settings.AllowDemandStart = $true
$t.Settings.StartWhenAvailable = $true
$t.Settings.ExecutionTimeLimit = "PT0S"
$t.Settings.DisallowStartIfOnBatteries = $false
$t.Settings.StopIfGoingOnBatteries = $false
$act = $t.Actions.Create(0)
$act.Path = $exe
$act.Arguments = "-m screenlab.service.consent_app_win --auth `"$reg`""
$act.WorkingDirectory = $prefix
$root.RegisterTaskDefinition($name, $t, 6, $null, $null, 3, $null) | Out-Null
$root.GetTask($name).Run($null) | Out-Null
Write-Output "LAUNCHED=$name"
