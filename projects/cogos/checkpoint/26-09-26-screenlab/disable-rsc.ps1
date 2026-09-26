# disable-rsc.ps1
# Work around VirtualBox 7.2.x bridged-mode slow-RX (rx_long_length_errors).
# Host NIC RSC coalesces segments into oversized frames that the guest e1000 drops.
# Run elevated (Administrator) on the Windows host that runs VirtualBox.
#
# RSC has two layers:
#   - global TCP setting  -> netsh int tcp set global rsc=disabled   (always applies)
#   - per-NIC advanced property *RSCIPv4 / *RSCIPv6                  (only some drivers)
# This script handles both and matches by RegistryKeyword, so it works on
# localized (e.g. Chinese) Windows where DisplayName is translated.
#
# Usage:
#   .\disable-rsc.ps1 -Diagnose            # show current state, change nothing
#   .\disable-rsc.ps1                      # disable global + per-NIC RSC
#   .\disable-rsc.ps1 -All                 # include Down adapters
#   .\disable-rsc.ps1 -InterfaceAlias "Ethernet","Wi-Fi"
#   .\disable-rsc.ps1 -OnlyGlobal          # skip per-NIC properties
#   .\disable-rsc.ps1 -Restart             # restart adapters after the change
#   .\disable-rsc.ps1 -Enable              # roll back
#
#Requires -RunAsAdministrator
[CmdletBinding()]
param(
    [switch]$Enable,
    [switch]$Diagnose,
    [switch]$All,
    [switch]$OnlyGlobal,
    [string[]]$InterfaceAlias = @(),
    [switch]$Restart
)

$ErrorActionPreference = 'Stop'

$targetValue = if ($Enable) { 'Enabled' } else { 'Disabled' }
$targetWord  = if ($Enable) { 'enabled' } else { 'disabled' }
$defaultReg  = if ($Enable) { 1 } else { 0 }
$verb        = if ($Enable) { 'enabling' } else { 'disabling' }

# RegistryKeyword matching is language-neutral; *RSSIPv4/*RSSIPv6 kept for reference.
$rscKeywords = @('*RSCIPv4', '*RSCIPv6')

function Show-GlobalRsc {
    Write-Host '--- netsh int tcp show global ---'
    (netsh int tcp show global) -split "`n" |
        Where-Object { $_ -match 'RSC|RSS|Coalesc|合并|缩放' } |
        ForEach-Object { Write-Host $_.Trim() }
}

function Show-AdapterRsc {
    Write-Host '--- per-adapter RSC ---'
    try {
        Get-NetAdapterRsc -ErrorAction Stop |
            Format-Table Name, IPv4Enabled, IPv6Enabled, IPv4Operational -AutoSize |
            Out-String | Write-Host
    } catch {
        Write-Host '(Get-NetAdapterRsc not available on this build)'
    }
}

if ($Diagnose) {
    Show-GlobalRsc
    $adapters = if ($All -or $InterfaceAlias.Count) {
        if ($InterfaceAlias.Count) { Get-NetAdapter -InterfaceAlias $InterfaceAlias } else { Get-NetAdapter }
    } else { Get-NetAdapter | Where-Object Status -eq 'Up' }
    foreach ($a in $adapters) {
        Write-Host ''
        Write-Host ("--- {0} ({1}) ---" -f $a.Name, $a.Status)
        Get-NetAdapterAdvancedProperty -Name $a.Name -ErrorAction SilentlyContinue |
            Select-Object DisplayName, RegistryKeyword, DisplayValue |
            Format-Table -AutoSize | Out-String | Write-Host
        $rsc = Get-NetAdapterAdvancedProperty -Name $a.Name -ErrorAction SilentlyContinue |
            Where-Object { $_.RegistryKeyword -in $rscKeywords }
        if (-not $rsc) { Write-Host '  no *RSCIPv4/*RSCIPv6 advanced property on this NIC' }
    }
    Show-AdapterRsc
    return
}

# --- global RSC (netsh) ---
Write-Host ("[global]  netsh int tcp set global rsc={0}" -f $targetWord)
netsh int tcp set global rsc=$targetWord | Out-Host

if ($OnlyGlobal) { Write-Host 'Done (global only).'; return }

# --- per-NIC RSC ---
$adapters = if ($InterfaceAlias.Count) {
    Get-NetAdapter -InterfaceAlias $InterfaceAlias
} elseif ($All) {
    Get-NetAdapter
} else {
    Get-NetAdapter | Where-Object { $_.Status -eq 'Up' }
}

if (-not $adapters) { Write-Host 'No matching adapters found.'; return }

$touched = @()
foreach ($adapter in $adapters) {
    $props = Get-NetAdapterAdvancedProperty -Name $adapter.Name -ErrorAction SilentlyContinue |
        Where-Object { $_.RegistryKeyword -in $rscKeywords }

    if (-not $props) {
        Write-Host ("[none]    {0,-24} no *RSCIPv4/*RSCIPv6 property (global setting still applies)" -f $adapter.Name)
        continue
    }

    foreach ($p in $props) {
        if ($p.DisplayValue -eq $targetValue) {
            Write-Host ("[skip]    {0,-24} {1}: already {2}" -f $adapter.Name, $p.RegistryKeyword, $targetValue)
            continue
        }
        Set-NetAdapterAdvancedProperty -Name $adapter.Name `
            -RegistryKeyword $p.RegistryKeyword -RegistryValue $defaultReg
        Write-Host ("[changed] {0,-24} {1}: {2} -> {3}" -f `
            $adapter.Name, $p.RegistryKeyword, $p.DisplayValue, $targetValue)
        $touched += $adapter.Name
    }
}

if ($Restart -and $touched.Count) {
    foreach ($name in ($touched | Select-Object -Unique)) {
        Write-Host ("[restart] {0}" -f $name)
        Restart-NetAdapter -Name $name -Confirm:$false
    }
}

$changedNames = ($touched | Select-Object -Unique) -join ', '
if (-not $changedNames) { $changedNames = '(none)' }
Write-Host ''
Write-Host ("Done ({0} RSC). Global set; per-NIC changed: {1}" -f $verb, $changedNames)
Write-Host 'Add -Restart if RX is still slow. Roll back with -Enable.'
