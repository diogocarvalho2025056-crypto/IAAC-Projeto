@echo off
setlocal
cd /d "%~dp0"
title CyberGuard AI - Web
if not exist ".venv\Scripts\python.exe" (
  echo [ERRO] Primeiro executa install-web.bat.
  pause
  exit /b 1
)
echo.
echo ====================================
echo          CYBERGUARD AI
 echo ====================================
echo Dashboard: http://127.0.0.1:8000
echo API:       http://127.0.0.1:8000/docs
echo.
".venv\Scripts\python.exe" -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
if errorlevel 1 echo [ERRO] O servidor terminou com erro.
pause
