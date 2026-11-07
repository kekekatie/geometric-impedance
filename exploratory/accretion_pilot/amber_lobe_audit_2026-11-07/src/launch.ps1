param([Parameter(Mandatory=$true)][string]$Phase,
      [string]$Workspace=(Resolve-Path "$PSScriptRoot/../../../../../..").Path)
$env:EFP_SNAPSHOT=Join-Path $Workspace 'work/efp-snapshot/exploratory/accretion_pilot/expansion_front_paper'
$env:AMBER_BASE_CACHE=Join-Path $Workspace 'work/archive-free-cache'
$env:AMBER_CACHE=Join-Path $Workspace 'work/amber-audit-cache'
$env:AMBER_FORK_CACHE=Join-Path $Workspace 'work/scar-audit/exploratory/accretion_pilot/jam_repair_pilot/results/baseline/forks.pkl'
$env:PYTHONUTF8='1'
$env:MPLBACKEND='Agg'
& (Join-Path $Workspace 'work/scar-venv/Scripts/python.exe') "$PSScriptRoot/execute.py" $Phase
exit $LASTEXITCODE
