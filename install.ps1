# Venice Chat Cross-Platform Installer for Windows (PowerShell)
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "    Venice AI Chat Installer (Windows)       " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check Python
try {
    $pythonVersion = python --version
    Write-Host "[1/3] Python detected: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[!] Error: Python is not detected in PATH. Please install Python 3.8+." -ForegroundColor Red
    exit 1
}

# 2. Install dependencies
Write-Host "[2/4] Installing dependencies..." -ForegroundColor Yellow
$reqFile = Join-Path $scriptDir "requirements.txt"
python -m pip install -q -r $reqFile

# 3. Check for OpenCode CLI (needed for zero-balance engine)
if (-not (Get-Command opencode -ErrorAction SilentlyContinue)) {
    Write-Host "[3/4] Installing OpenCode CLI for free zero-balance engine..." -ForegroundColor Cyan
    try {
        irm https://opencode.ai/install.ps1 | iex
    } catch {
        Write-Host "    Note: You can install OpenCode manually via: irm https://opencode.ai/install.ps1 | iex" -ForegroundColor Gray
    }
} else {
    Write-Host "[3/4] OpenCode CLI detected." -ForegroundColor Green
}

# 4. Create CMD wrapper in user path
$targetDir = "$env:LOCALAPPDATA\Microsoft\WindowsApps"
$cmdFile = Join-Path $targetDir "venice.cmd"
$pyScript = Join-Path $scriptDir "venice_chat.py"

$batchContent = "@echo off`r`npython `"$pyScript`" %*"
[System.IO.File]::WriteAllText($cmdFile, $batchContent)

Write-Host "[4/4] Created global command 'venice' at $cmdFile" -ForegroundColor Green
Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  [OK] Venice Chat successfully installed for Windows!" -ForegroundColor Green
Write-Host "  Run it anywhere by simply typing: venice" -ForegroundColor Yellow
Write-Host "  To uninstall completely, run: venice uninstall" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""
