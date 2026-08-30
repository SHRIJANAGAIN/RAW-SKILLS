# Copy skills from this repository into an agent's skill directory.
#
#   .\scripts\install-skills.ps1 -Target .agents\skills -Skill react-best-practices
#   .\scripts\install-skills.ps1 -Target $HOME\.claude\skills -Skill brainstorming,systematic-debugging
#   .\scripts\install-skills.ps1 -Target .opencode\skills -All
[CmdletBinding(DefaultParameterSetName = "Named")]
param(
  [Parameter(Mandatory = $true)]
  [string]$Target,

  [Parameter(Mandatory = $true, ParameterSetName = "Named")]
  [string[]]$Skill,

  [Parameter(Mandatory = $true, ParameterSetName = "All")]
  [switch]$All
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$skip = @("scripts", "node_modules", ".git", ".github")

New-Item -ItemType Directory -Force -Path $Target | Out-Null

if ($All) {
  $copied = 0
  foreach ($dir in Get-ChildItem $root -Directory) {
    if ($skip -contains $dir.Name) { continue }
    if (-not (Test-Path (Join-Path $dir.FullName "SKILL.md"))) { continue }
    Copy-Item -Recurse -Force $dir.FullName $Target
    $copied++
  }
  Write-Host "copied $copied skills to $Target"
  return
}

foreach ($name in $Skill) {
  $source = Join-Path $root $name
  if (-not (Test-Path (Join-Path $source "SKILL.md"))) {
    Write-Warning "skip: $name (no SKILL.md)"
    continue
  }
  Copy-Item -Recurse -Force $source $Target
  Write-Host "copied $name"
}
