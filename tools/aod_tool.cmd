@echo off
setlocal
chcp 65001 >nul
set "PYTHONIOENCODING=utf-8"
if not defined AOD_TOOL_PYTHON set "AOD_TOOL_PYTHON=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if not exist "%AOD_TOOL_PYTHON%" (
  echo ERROR: Python not found. Set AOD_TOOL_PYTHON to your Python executable.
  pause
  exit /b 1
)
"%AOD_TOOL_PYTHON%" -B "%~dp0aod_self_service.py" menu
if errorlevel 1 echo ERROR: Processing stopped. Do not install a failed build.
pause
endlocal
