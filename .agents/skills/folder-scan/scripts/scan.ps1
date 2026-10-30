[CmdletBinding()]
param(
    [string]$TargetDir = ".",
    [int]$MaxDepth = 3,
    [int]$MaxFilesPerDir = 20
)

$ErrorActionPreference = "SilentlyContinue"

$resolvedPath = (Resolve-Path $TargetDir).Path
if (-not (Test-Path $resolvedPath)) {
    Write-Host "Directory not found: $TargetDir"
    exit 1
}

Write-Host "=================================================="
Write-Host "FOLDER SCAN REPORT: $resolvedPath"
Write-Host "=================================================="

$excludeDirs = @(
    '.git', '.agent', '.agents', '.gemini', 'node_modules', 
    '__pycache__', '.venv', 'venv', 'env', 'dist', 'build', 
    '.idea', '.vscode', 'tmp', 'bin', 'obj', 'coverage'
)

Write-Host "`n### 1. DIRECTORY STRUCTURE (Depth <= $MaxDepth)"

function Show-Tree {
    param(
        [string]$CurrentPath,
        [string]$Indent = "",
        [int]$Depth = 1
    )
    if ($Depth -gt $MaxDepth) { return }

    $items = Get-ChildItem -Path $CurrentPath -Force | Where-Object {
        $name = $_.Name
        if ($_.PSIsContainer) {
            return ($excludeDirs -notcontains $name)
        }
        return $true
    } | Sort-Object { -not $_.PSIsContainer }, Name

    $count = 0
    $total = $items.Count
    foreach ($item in $items) {
        $count++
        if ($count -gt $MaxFilesPerDir) {
            Write-Host ($Indent + "\-- ... (truncated: " + ($total - $MaxFilesPerDir) + " more items)")
            break
        }

        $isLast = ($count -eq $total) -or ($count -eq $MaxFilesPerDir)
        $prefix = if ($isLast) { "\-- " } else { "+-- " }

        if ($item.PSIsContainer) {
            Write-Host ($Indent + $prefix + "[DIR] " + $item.Name + "/")
            $nextIndent = if ($isLast) { $Indent + "    " } else { $Indent + "|   " }
            Show-Tree -CurrentPath $item.FullName -Indent $nextIndent -Depth ($Depth + 1)
        } else {
            $sizeKb = [math]::Round($item.Length / 1KB, 1)
            Write-Host ($Indent + $prefix + "[FILE] " + $item.Name + " (" + $sizeKb + " KB)")
        }
    }
}

Show-Tree -CurrentPath $resolvedPath

Write-Host "`n### 2. FILE STATISTICS"
$allFiles = Get-ChildItem -Path $resolvedPath -Recurse -File -Force | Where-Object {
    $fullName = $_.FullName
    $skip = $false
    foreach ($ex in $excludeDirs) {
        if ($fullName -match "[\\/]$ex[\\/]") { $skip = $true; break }
    }
    return -not $skip
}

$extStats = $allFiles | Group-Object Extension | Sort-Object Count -Descending | Select-Object -First 10
foreach ($group in $extStats) {
    $ext = if ($group.Name) { $group.Name } else { "(no ext)" }
    $sumSize = ($group.Group | Measure-Object -Property Length -Sum).Sum
    $totalSize = [math]::Round($sumSize / 1KB, 1)
    Write-Host ("  - " + $ext + " : " + $group.Count + " files (" + $totalSize + " KB)")
}

Write-Host "`n### 3. KEY PROJECT FILES FOUND"
$keyFilePatterns = @(
    'README.md', 'GEMINI.md', 'AGENTS.md', 'package.json', 
    'requirements.txt', 'pyproject.toml', 'pom.xml', 'build.gradle',
    'docker-compose.yml', 'Dockerfile', 'Makefile', '.env.example'
)

$foundKeyFiles = @()
foreach ($kf in $keyFilePatterns) {
    $found = Get-ChildItem -Path $resolvedPath -Filter $kf -File -Recurse | Where-Object {
        $fullName = $_.FullName
        $skip = $false
        foreach ($ex in $excludeDirs) {
            if ($fullName -match "[\\/]$ex[\\/]") { $skip = $true; break }
        }
        return -not $skip
    }
    if ($found) {
        $foundKeyFiles += $found
    }
}

foreach ($f in $foundKeyFiles) {
    $rel = $f.FullName.Substring($resolvedPath.Length).TrimStart('\', '/')
    Write-Host ("`n--- Preview: " + $rel + " ---")
    Get-Content -Path $f.FullName -TotalCount 25 | ForEach-Object { Write-Host ("  " + $_) }
}

Write-Host "`n=================================================="
Write-Host "SCAN COMPLETE"
Write-Host "=================================================="
