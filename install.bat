@echo off
setlocal enabledelayedexpansion

echo.
echo =============================================
echo    Venice AI Chat Installer (Windows CMD)    
echo =============================================
echo.

:: 1. Check Python
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [!] Error: Python is not detected in PATH.
    echo Please install Python 3.8+ from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo [1/3] Python detected:
python --version

:: 2. Install dependencies
echo [2/3] Installing dependencies from requirements.txt...
python -m pip install -q -r "%~dp0requirements.txt"
if %ERRORLEVEL% neq 0 (
    echo [!] Warning: pip install encountered issues; continuing...
)

:: 3. Setup global command in WindowsApps (always in User PATH)
set "TARGET_DIR=%LOCALAPPDATA%\Microsoft\WindowsApps"
set "CMD_FILE=%TARGET_DIR%\venice.cmd"

echo [3/3] Creating global 'venice' command at %CMD_FILE%...
(
    echo @echo off
    echo python "%~dp0venice_chat.py" %%*
) > "%CMD_FILE%"

:: 4. Check for .env file
if not exist "%~dp0.env" (
    if exist "%~dp0.env.example" (
        copy "%~dp0.env.example" "%~dp0.env" >nul
    )
)

echo.
echo ==========================================================
echo   [OK] Venice Chat successfully installed for Windows!
echo   Run it anywhere by simply typing: venice
echo   To uninstall completely, run: venice uninstall
echo ==========================================================
echo.
pause
