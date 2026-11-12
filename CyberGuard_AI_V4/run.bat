@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Executa install.bat primeiro.
  pause
  exit /b 1
)
echo CyberGuard AI V4: http://127.0.0.1:8000
set OMP_NUM_THREADS=1
set OTEL_SDK_DISABLED=true
set CREWAI_DISABLE_TELEMETRY=true
".venv\Scripts\python.exe" -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
pause
