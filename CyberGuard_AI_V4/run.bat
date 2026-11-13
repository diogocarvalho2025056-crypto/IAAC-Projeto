@echo off
cd /d "%~dp0"
set "CYBERGUARD_PYTHON=.venv\Scripts\python.exe"
if exist "local-runtime.bat" call "local-runtime.bat"
if not exist "%CYBERGUARD_PYTHON%" (
  echo Executa install.bat primeiro.
  pause
  exit /b 1
)
echo CyberGuard AI V4: http://127.0.0.1:8000
set OMP_NUM_THREADS=1
set OTEL_SDK_DISABLED=true
set CREWAI_DISABLE_TELEMETRY=true
"%CYBERGUARD_PYTHON%" -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
pause
