@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo [ERRO] Executa primeiro install-web.bat.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m pip install -r requirements-ai.txt
if errorlevel 1 (
  echo [ERRO] Nao foi possivel instalar CrewAI.
  pause
  exit /b 1
)
echo CrewAI instalado. Reinicia o servidor.
pause
