@echo off
setlocal
cd /d "%~dp0"
echo.
echo ==== Instalar CyberGuard AI Web ====
where py >nul 2>&1
if errorlevel 1 (
  echo [ERRO] Python Launcher nao encontrado. Instala Python 3.
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
  py -3 -m venv .venv
  if errorlevel 1 goto :fail
)
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :fail
".venv\Scripts\python.exe" -m pip install -r requirements-web.txt
if errorlevel 1 goto :fail
echo.
echo Dependencias Web instaladas.
pause
exit /b 0
:fail
echo.
echo [ERRO] Instalacao falhou.
pause
exit /b 1
