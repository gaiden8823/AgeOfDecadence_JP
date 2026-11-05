@echo off
setlocal DisableDelayedExpansion
set "ROOT=%~dp0"
set "FINAL_CODE=0"

rem Age of Decadence Japanese MOD - Windows command launcher.
rem This file contains only ASCII characters to avoid CMD code-page issues.
rem The installer menu and file operations remain in AoDJP\installer.ps1.

if not exist "%ROOT%AoDJP\installer.ps1" goto :missing
if not exist "%ROOT%AoDJP\manifest.json" goto :missing_manifest
pushd "%ROOT%" >nul 2>&1
if errorlevel 1 goto :bad_directory

:menu
echo.
echo ========================================================
echo Age of Decadence - Japanese MOD
echo Installer: check / install / restore / change font
echo ========================================================
echo.
rem Bypass applies to this PowerShell PROCESS only. It does not change
rem the user's system-wide execution policy. Organization policies may override it.
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%ROOT%AoDJP\installer.ps1" %*
set "EXIT_CODE=%ERRORLEVEL%"
set "FINAL_CODE=%EXIT_CODE%"
echo.
if not "%EXIT_CODE%"=="0" (
   echo [ERROR] Installer exited with code %EXIT_CODE%.
   echo Read the error message above before trying again.
   echo If needed, take a screenshot for troubleshooting.
) else (
   echo Installer returned successfully.
)
echo.
echo Installed files remain in place when this window closes.
echo The game is not started automatically. Launch it normally.
echo For instructions, open the documentation included in the ZIP.
echo.
choice /c M0 /n /m "M: Return to installer menu / 0: Close > "
if errorlevel 2 goto :finish
goto :menu

:missing
set "FINAL_CODE=2"
echo.
echo [ERROR] Missing: "%ROOT%AoDJP\installer.ps1"
echo Keep this CMD next to the AoDJP folder in the game directory.
echo.
pause
goto :finish

:missing_manifest
set "FINAL_CODE=2"
echo.
echo [ERROR] Missing: "%ROOT%AoDJP\manifest.json"
echo The release ZIP may be incomplete or folders were misplaced.
echo.
pause
goto :finish

:bad_directory
set "FINAL_CODE=3"
echo.
echo [ERROR] Cannot open launcher directory: "%ROOT%"
echo.
pause
goto :finish

:finish
popd >nul 2>&1
endlocal & exit /b %FINAL_CODE%
