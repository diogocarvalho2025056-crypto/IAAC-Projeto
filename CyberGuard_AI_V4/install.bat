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
echo Instalacao concluida. Inicia o Ollama e executa ollama pull qwen2.5:3b.
echo Depois executa run.bat.
pause
