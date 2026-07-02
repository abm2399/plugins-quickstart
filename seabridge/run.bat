@echo off
REM One-step local runner for the SeaBridge dashboard (Windows).
REM
REM   run.bat            - sample provider (offline, no pip installs)
REM   run.bat yfinance   - live prices (needs: pip install -r requirements.txt)
REM   set PORT=9000 ^& run.bat   - override port
REM
REM Starts the price service in its own window and opens the dashboard.
REM Close the service window to stop it.
setlocal
set "SCRIPT_DIR=%~dp0"
if "%PRICE_PROVIDER%"=="" set "PRICE_PROVIDER=sample"
if not "%~1"=="" set "PRICE_PROVIDER=%~1"
if "%PORT%"=="" set "PORT=8787"

where python >nul 2>&1
if %ERRORLEVEL%==0 (set "PY=python") else (set "PY=py")

echo Starting SeaBridge price service (provider=%PRICE_PROVIDER%, port=%PORT%)...
start "SeaBridge price service" cmd /k ""%PY%" "%SCRIPT_DIR%server.py""

REM Give the server a moment to bind the port.
timeout /t 2 >nul

if "%PORT%"=="8787" (
  start "" "%SCRIPT_DIR%..\seabridge_dashboard_v2.html"
) else (
  start "" "%SCRIPT_DIR%..\seabridge_dashboard_v2.html?api=http://localhost:%PORT%/api/prices"
)

echo.
echo Dashboard opened in your browser.
echo The price service is running in a separate window - close it to stop.
endlocal
