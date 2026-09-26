param([ValidateSet("start","stop")][string]$Action = "start")
$svc = New-Object -ComObject Schedule.Service
$svc.Connect()
$root = $svc.GetFolder("\")
$name = "screenlab-it-daemon"
if ($Action -eq "stop") {
  try { $root.GetTask($name).Stop(0) | Out-Null } catch {}
  try { $root.DeleteTask($name, 0) } catch {}
  Write-Output "STOPPED"
  exit 0
}
try { $root.DeleteTask($name, 0) } catch {}
$t = $svc.NewTask(0)
$t.RegistrationInfo.Description = "screenlab integration test daemon"
$t.Principal.UserId = "TABLET-BBT8EQB4\assist"
$t.Principal.LogonType = 3
$t.Principal.RunLevel = 0
$t.Settings.Enabled = $true
$t.Settings.AllowDemandStart = $true
$t.Settings.ExecutionTimeLimit = "PT0S"
$t.Settings.DisallowStartIfOnBatteries = $false
$t.Settings.StopIfGoingOnBatteries = $false
$act = $t.Actions.Create(0)
$act.Path = "C:\Users\assist\AppData\Local\screenlab\venv\Scripts\python.exe"
$act.Arguments = "-m screenlab.service.cli --tcp 127.0.0.1:19911 --auth C:\Users\assist\.config\screenlab\registry --consent auto --presence daemon"
$act.WorkingDirectory = "C:\Users\assist\AppData\Local\screenlab"
$root.RegisterTaskDefinition($name, $t, 6, $null, $null, 3, $null) | Out-Null
$root.GetTask($name).Run($null) | Out-Null
Write-Output "STARTED"
