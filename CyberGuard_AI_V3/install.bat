@echo off
cd /d "%~dp0"
where py >nul 2>&1
if errorlevel 1 (
  echo Instala Python 3.13 e ativa o Python Launcher.
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" py -3.13 -m venv .venv
if errorlevel 1 exit /b 1
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 exit /b 1
set OMP_NUM_THREADS=1
".venv\Scripts\python.exe" -m unittest tests.test_v3.PEFeaturesTests tests.test_v3.DirectPipelineTests tests.test_v31 -v
pause
