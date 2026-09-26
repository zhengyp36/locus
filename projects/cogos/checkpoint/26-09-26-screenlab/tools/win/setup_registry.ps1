# Write the agent registry on the Windows target (assist). Run as assist.
# The file MUST be a JSON array; PowerShell ConvertTo-Json unwraps a 1-element
# array into an object, so the literal is written by hand.
$ErrorActionPreference = "Stop"
$reg = "C:\Users\assist\.config\screenlab\registry"
New-Item -ItemType Directory -Force -Path $reg | Out-Null
$json = '[{"pubkey": "TsrTNVQgfSeKuFDFxp07O06ji5NKH+Cmc2qwLqOj4cE=", "name": "", "alias": "kilocode"}]'
Set-Content -Encoding ASCII -Path "$reg\registry.json" -Value $json
Write-Output "REGISTRY_WRITTEN"
Get-Content "$reg\registry.json"
