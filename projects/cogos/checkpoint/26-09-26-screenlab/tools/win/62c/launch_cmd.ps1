# 62c: run an arbitrary command line inside assist's INTERACTIVE session, output
# redirected to a file in the 62c dir. Run as ADMIN over ssh.
param(
    [Parameter(Mandatory=$true)][string]$Cmd,
    [string]$Name = "screenlab-62c-cmd",
    [string]$Out = "cmd.out"
)
$ErrorActionPreference = "Stop"
$user = "TABLET-BBT8EQB4\assist"
$dir  = "C:\Users\assist\screenlab-62c"
$svc = New-Object -ComObject Schedule.Service
$svc.Connect()
$root = $svc.GetFolder("\")
try { $root.DeleteTask($Name, 0) } catch { }
$t = $svc.NewTask(0)
$t.RegistrationInfo.Description = "62c cmd: $Name"
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
$act.Arguments = "/c `"$Cmd > `"$dir\$Out`" 2>&1`""
$act.WorkingDirectory = $dir
$root.RegisterTaskDefinition($Name, $t, 6, $null, $null, 3, $null) | Out-Null
$root.GetTask($Name).Run($null) | Out-Null
Write-Output "LAUNCHED=$Name OUT=$Out"
