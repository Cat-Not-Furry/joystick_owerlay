@echo off
setlocal

if "%~1"=="" (
	echo Uso: install\update_windows.bat ruta\al\update.zip
	exit /b 1
)

set "ZIP_PATH=%~1"
set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "ROOT=%%~fI"

set "PYTHON_BIN=%ROOT%\venv\Scripts\python.exe"
if exist "%PYTHON_BIN%" goto run_update
set "PYTHON_BIN=python"

:run_update
"%PYTHON_BIN%" "%ROOT%\cli.py" --update --zip "%ZIP_PATH%"
exit /b %ERRORLEVEL%
