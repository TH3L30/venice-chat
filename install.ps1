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
Write-Host "[2/3] Installing dependencies..." -ForegroundColor Yellow
python -m pip install -q -r "$scriptDir\requirements.txt"

# 3. Create CMD wrapper in user path
$targetDir = "$env:LOCALAPPDATA\Microsoft\WindowsApps"
$cmdFile = "$targetDir\venice.cmd"

$batchContent = "@echo off`r`npython `"$scriptDir\venice_chat.py`" %*"
Set-Content -Path $cmdFile -Value $batchContent

Write-Host "[3/3] Created global command 'venice' at $cmdFile" -ForegroundColor Green
Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  ✔ Venice Chat successfully installed for Windows!" -ForegroundColor Green
Write-Host "  Run it anywhere by simply typing: venice" -ForegroundColor Yellow
Write-Host "  To uninstall completely, run: venice uninstall" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""
