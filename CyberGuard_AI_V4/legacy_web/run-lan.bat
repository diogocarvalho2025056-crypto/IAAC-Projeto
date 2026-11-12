@echo off
setlocal
cd /d "%~dp0"
if "%CYBERGUARD_WEB_USER%"=="" goto :missing
if "%CYBERGUARD_WEB_PASSWORD%"=="" goto :missing
if not exist ".venv\Scripts\python.exe" (
  echo [ERRO] Primeiro executa install-web.bat.
  pause
  exit /b 1
)
echo.
echo CyberGuard AI a aceitar ligacoes LAN na porta 8000.
echo Usa o endereco IPv4 do PC: http://SEU-IP:8000
echo Atencao: HTTP Basic sem TLS e adequado apenas a uma LAN privada fiavel.
".venv\Scripts\python.exe" -m uvicorn backend.app:app --host 0.0.0.0 --port 8000
pause
exit /b 0
:missing
echo [ERRO] Configura as variaveis CYBERGUARD_WEB_USER e CYBERGUARD_WEB_PASSWORD.
echo Exemplo no PowerShell, antes de executar:
echo $env:CYBERGUARD_WEB_USER="utilizador"
echo $env:CYBERGUARD_WEB_PASSWORD="uma-palavra-passe-forte"
pause
exit /b 1
