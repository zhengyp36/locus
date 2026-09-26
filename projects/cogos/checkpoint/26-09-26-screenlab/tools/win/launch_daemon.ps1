# Start the screenlab daemon inside assist's interactive session (Session 6).
# Run as ADMIN over ssh. This is a W1/W3 test harness (Task Scheduler COM with an
# interactive token); the product path is the human opening the tray entry (W4).
$ErrorActionPreference = "Stop"
$user = "TABLET-BBT8EQB4\assist"
$name = "screenlab-w1"
$prefix = "C:\Users\assist\AppData\Local\screenlab"
$exe = Join-Path $prefix "venv\Scripts\pythonw.exe"

$svc = New-Object -ComObject Schedule.Service
$svc.Connect()
$root = $svc.GetFolder("\")
$t = $svc.NewTask(0)
$t.RegistrationInfo.Description = "screenlab daemon (session injection harness)"
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
$act.Arguments = "-m screenlab.service.launch"
$act.WorkingDirectory = $prefix
$root.RegisterTaskDefinition($name, $t, 6, $null, $null, 3, $null) | Out-Null
$root.GetTask($name).Run($null) | Out-Null
Write-Output "LAUNCHED=$name"
