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
$skillsRoot = Join-Path $root "skills"

New-Item -ItemType Directory -Force -Path $Target | Out-Null

if ($All) {
  $copied = 0
  foreach ($bucket in Get-ChildItem $skillsRoot -Directory) {
    foreach ($skill in Get-ChildItem $bucket.FullName -Directory) {
      if (-not (Test-Path (Join-Path $skill.FullName "SKILL.md"))) { continue }
      Copy-Item -Recurse -Force $skill.FullName $Target
      $copied++
    }
  }
  Write-Host "copied $copied skills to $Target"
  return
}

foreach ($name in $Skill) {
  $source = Get-ChildItem $skillsRoot -Directory |
    ForEach-Object { Get-ChildItem $_.FullName -Directory -Filter $name } |
    Select-Object -First 1

  if (-not $source -or -not (Test-Path (Join-Path $source.FullName "SKILL.md"))) {
    Write-Warning "skip: $name (no SKILL.md in skills\*\$name)"
    continue
  }
  Copy-Item -Recurse -Force $source.FullName $Target
  Write-Host "copied $name"
}
