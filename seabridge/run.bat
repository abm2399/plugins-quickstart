@echo off
REM One-step local runner for the SeaBridge dashboard (Windows).
REM
REM   run.bat            - sample provider (offline, no pip installs)
REM   run.bat yfinance   - live prices (needs: pip install -r requirements.txt)
REM
REM Double-click this file, or run it from a terminal. It starts the server and
REM opens the dashboard at http://localhost:8787 in your browser.
setlocal
cd /d "%~dp0"
if "%PRICE_PROVIDER%"=="" set "PRICE_PROVIDER=sample"
if not "%~1"=="" set "PRICE_PROVIDER=%~1"
if "%PORT%"=="" set "PORT=8787"

REM Find Python (try 'python', then the 'py' launcher).
where python >nul 2>&1
if %ERRORLEVEL%==0 (set "PY=python") else (set "PY=py")

echo Starting SeaBridge dashboard (provider=%PRICE_PROVIDER%, port=%PORT%)...
echo A browser tab will open at http://localhost:%PORT%
echo Close this window (or press Ctrl+C) to stop.
echo.

REM Open the browser after a short delay so the server has time to start.
start "" /b cmd /c "timeout /t 2 >nul & start "" http://localhost:%PORT%/"

REM Run the server in THIS window (so closing the window stops it).
"%PY%" server.py

endlocal
