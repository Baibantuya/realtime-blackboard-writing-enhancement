param([Parameter(Mandatory=$true)][string]$ToolRoot)
$ErrorActionPreference='Stop'
$taskRoot=Split-Path $PSScriptRoot -Parent
$taskOut=Join-Path $taskRoot 'report/reset'
if(Test-Path -LiteralPath $taskOut){throw 'Preserve previous reset evidence'}
$taskNet=Join-Path $taskRoot 'v/b/design_1/ip/design_1_rst_clk_wiz_0_200M_0/design_1_rst_clk_wiz_0_200M_0_sim_netlist.v'
if(!(Test-Path -LiteralPath $taskNet)){throw 'Generate the candidate reset netlist first'}
New-Item -ItemType Directory -Path $taskOut | Out-Null
$taskBin=Join-Path $ToolRoot 'Vivado/bin'
Push-Location -LiteralPath $taskOut
try {
    & "$taskBin/xvlog.bat" --sv "$taskRoot/sim/tb/tb_reset.sv" *> compile_tb.log
    if($LASTEXITCODE -ne 0){throw 'Testbench compile failed'}
    & "$taskBin/xvlog.bat" $taskNet "$ToolRoot/Vivado/data/verilog/src/glbl.v" *> compile_netlist.log
    if($LASTEXITCODE -ne 0){throw 'Netlist compile failed'}
    & "$taskBin/xelab.bat" tb_reset glbl -L unisims_ver -L secureip -s reset_check *> elaborate.log
    if($LASTEXITCODE -ne 0){throw 'Elaboration failed'}
    & "$taskBin/xsim.bat" reset_check -runall *> simulate.log
    if($LASTEXITCODE -ne 0 -or !(Select-String -LiteralPath simulate.log -SimpleMatch 'PASS_RESET_COMPONENT_ONLY')){throw 'Reset component test failed'}
    @{status='PASS_RESET_COMPONENT_ONLY';source_sha256=(Get-FileHash -LiteralPath $taskNet -Algorithm SHA256).Hash;board_test='NOT_RUN'} | ConvertTo-Json | Set-Content -LiteralPath result.json -Encoding utf8
} finally {Pop-Location}
