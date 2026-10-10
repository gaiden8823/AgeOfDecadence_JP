@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
:menu
powershell.exe -NoLogo -NoProfile -ExecutionPolicy RemoteSigned -File "%~dp0AoDJP\installer.ps1" %*
if errorlevel 1 echo 処理を中止しました。上に表示された理由を確認してください。
echo.
echo 今回の処理は終了しました。導入済みの場合、画面を閉じても日本語化は解除されません。
echo ゲームは自動起動しません。Steamなどから通常どおり起動してください。
echo 詳しい説明は、同じフォルダの「導入手順.txt」を開いてください。
choice /c M0 /n /m "M：操作メニューへ戻る ／ 0：この画面を閉じる > "
if errorlevel 2 exit /b
goto menu
