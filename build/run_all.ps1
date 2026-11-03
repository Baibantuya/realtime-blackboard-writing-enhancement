param([Parameter(Mandatory=$true)][string]$ToolRoot,[string]$VivadoOverlay='',[string]$Python='python')
$ErrorActionPreference='Stop'
$taskRoot=Split-Path $PSScriptRoot -Parent
if ($taskRoot -match '[^\x00-\x7F]') {throw 'Use an ASCII short build path on Windows'}
if ($env:XILINX_PATH -or $env:MYVIVADO) {throw 'Unexpected inherited executable overlay'}
$taskHls=Join-Path $ToolRoot 'Vitis/bin/vitis-run.bat'
$taskVivado=Join-Path $ToolRoot 'Vivado/bin/vivado.bat'
Set-Location -LiteralPath $taskRoot
foreach($taskGenerated in @('h','v','i')) {
    if(Test-Path -LiteralPath (Join-Path $taskRoot $taskGenerated)){throw 'Use a fresh source-only directory; generated evidence already exists'}
}
foreach($taskFolder in @('logs','report')) {
    New-Item -ItemType Directory -Force -Path (Join-Path $taskRoot $taskFolder) | Out-Null
}
& $Python build/verify_sources.py *> logs/inputs_before.json
if($LASTEXITCODE -ne 0){throw 'Source verification failed'}
foreach ($taskPhase in @('r','s','w')) {
    & $taskHls --mode hls --tcl "build/hls_$taskPhase.tcl" *> "logs/hls_$taskPhase.log"
    $taskExit=$LASTEXITCODE
    @{phase="hls_$taskPhase";exit_code=$taskExit;finished_at=(Get-Date).ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath "logs/hls_$taskPhase.status.json" -Encoding utf8
    if($taskExit -ne 0){Get-Content "logs/hls_$taskPhase.log" -Tail 20;exit $taskExit}
}
try {
    if($VivadoOverlay){$env:XILINX_PATH=$VivadoOverlay}
    & $taskVivado -mode batch -source build/vivado.tcl -log logs/vivado.log -journal logs/vivado.jou *> logs/vivado_console.log
    $taskExit=$LASTEXITCODE
    @{phase='vivado';exit_code=$taskExit;finished_at=(Get-Date).ToString('o');overlay_used=[bool]$VivadoOverlay;scope='Tool completion only, review routed timing and CDC separately'} | ConvertTo-Json | Set-Content -LiteralPath logs/vivado.status.json -Encoding utf8
    Get-Content logs/vivado_console.log -Tail 20
    if($taskExit -eq 0){& "$PSScriptRoot/check_reset.ps1" -ToolRoot $ToolRoot}
    & $Python build/verify_sources.py *> logs/inputs_after.json
    if($LASTEXITCODE -ne 0){throw 'Sources changed during build'}
    exit $taskExit
} finally {Remove-Item Env:XILINX_PATH -ErrorAction SilentlyContinue}
