# One-glance Windows 3a state. Run as admin (to see other sessions' processes).
$ErrorActionPreference = "Continue"
"--- pythonw (daemon = big, launcher stub = ~6MB) ---"
Get-Process pythonw -ErrorAction SilentlyContinue |
    Select-Object Id, SessionId, @{n="Start";e={$_.StartTime.ToString("HH:mm:ss")}}, `
                  @{n="MB";e={[int]($_.WorkingSet64/1MB)}}, Path |
    Format-Table -AutoSize | Out-String -Width 200
"--- listening / consent connections (9911 screen, 9912 consent) ---"
netstat -ano | Select-String ":991[12]"
"--- daemon.log tail ---"
Get-Content "C:\Users\assist\AppData\Local\screenlab\daemon.log" -Tail 6 -ErrorAction SilentlyContinue
"--- consent.addr ---"
Get-Content "C:\Users\assist\.config\screenlab\registry\consent.addr" -ErrorAction SilentlyContinue
