@echo off
setlocal enabledelayedexpansion

:: PC Shutdown Scheduler - Batch Version
:: This batch implementation provides similar functionality to the Python version

:: Configure times (24-hour format)
set "FIRST_DIALOG_HOUR=21"
set "FIRST_DIALOG_MIN=30"
set "SECOND_DIALOG_HOUR=22"
set "SECOND_DIALOG_MIN=50"
set "SHUTDOWN_HOUR=23"
set "SHUTDOWN_MIN=00"

:: Set up logging
set "LOG_FILE=%USERPROFILE%\shutdown_scheduler.log"
echo Shutdown Scheduler started at %date% %time% >> "%LOG_FILE%"

:: Hide this window (will still show briefly at startup)
if not "%1"=="HIDDEN" (
    start /min "" "%~dpnx0" HIDDEN
    exit
)

:main_loop
:: Get current time
for /f "tokens=1-4 delims=:." %%a in ("%time%") do (
    set "HOUR=%%a"
    set "MIN=%%b"
    
    :: Handle leading space in hour
    set "HOUR=!HOUR: =0!"
)

:: Convert to 24-hour format if needed
if %HOUR% LSS 10 set "HOUR=0%HOUR%"

:: Check if it's time for first dialog (9:30 PM to 10:50 PM)
set /a "CURRENT_TIME_MINS=%HOUR%*60+%MIN%"
set /a "FIRST_DIALOG_TIME_MINS=%FIRST_DIALOG_HOUR%*60+%FIRST_DIALOG_MIN%"
set /a "SECOND_DIALOG_TIME_MINS=%SECOND_DIALOG_HOUR%*60+%SECOND_DIALOG_MIN%"
set /a "SHUTDOWN_TIME_MINS=%SHUTDOWN_HOUR%*60+%SHUTDOWN_MIN%"

:: Debug logging
:: echo Current time mins: %CURRENT_TIME_MINS% >> "%LOG_FILE%"
:: echo First dialog mins: %FIRST_DIALOG_TIME_MINS% >> "%LOG_FILE%"
:: echo Second dialog mins: %SECOND_DIALOG_TIME_MINS% >> "%LOG_FILE%"

:: Check if we should show first dialog
if %CURRENT_TIME_MINS% GEQ %FIRST_DIALOG_TIME_MINS% if %CURRENT_TIME_MINS% LSS %SECOND_DIALOG_TIME_MINS% (
    if not exist "%TEMP%\shutdown_first_shown.tmp" (
        echo Showing first dialog at %date% %time% >> "%LOG_FILE%"
        call :show_first_dialog
    )
)

:: Check if we should show second dialog
if %CURRENT_TIME_MINS% GEQ %SECOND_DIALOG_TIME_MINS% if %CURRENT_TIME_MINS% LSS %SHUTDOWN_TIME_MINS% (
    if not exist "%TEMP%\shutdown_second_shown.tmp" (
        :: Close first dialog if it's still open
        taskkill /f /im mshta.exe >nul 2>&1
        
        :: Delete first dialog marker
        if exist "%TEMP%\shutdown_first_shown.tmp" del "%TEMP%\shutdown_first_shown.tmp"
        
        echo Showing second dialog at %date% %time% >> "%LOG_FILE%"
        call :show_second_dialog
    )
)

:: Check if it's shutdown time
if %CURRENT_TIME_MINS% GEQ %SHUTDOWN_TIME_MINS% (
    :: Only shut down if not canceled
    if not exist "%TEMP%\shutdown_canceled.tmp" (
        echo PC shutdown initiated at %date% %time% >> "%LOG_FILE%"
        shutdown /s /t 0 /f
        exit
    )
)

:: Check every minute
timeout /t 60 /nobreak >nul
goto main_loop

:show_first_dialog
:: Create an HTA application for the dialog
echo ^<html^>^<head^>^<title^>Shutdown Confirmation^</title^> > "%TEMP%\shutdown_dialog.hta"
echo ^<HTA:APPLICATION ID="ShutdownApp" APPLICATIONNAME="Shutdown Confirmation" BORDER="dialog" BORDERSTYLE="normal" >> "%TEMP%\shutdown_dialog.hta"
echo CAPTION="yes" ICON="warning" MAXIMIZEBUTTON="no" MINIMIZEBUTTON="yes" >> "%TEMP%\shutdown_dialog.hta"
echo SHOWINTASKBAR="yes" SINGLEINSTANCE="yes" SYSMENU="yes" VERSION="1.0"^> >> "%TEMP%\shutdown_dialog.hta"
echo ^<style^> >> "%TEMP%\shutdown_dialog.hta"
echo body { font-family: Arial; background-color: #f0f0f0; text-align: center; margin-top: 20px; } >> "%TEMP%\shutdown_dialog.hta"
echo .content { background-color: white; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); padding: 20px; margin: 0 auto; max-width: 400px; } >> "%TEMP%\shutdown_dialog.hta"
echo button { padding: 8px 16px; margin: 10px; border-radius: 4px; cursor: pointer; } >> "%TEMP%\shutdown_dialog.hta"
echo .cancel-btn { background-color: #4CAF50; color: white; border: none; } >> "%TEMP%\shutdown_dialog.hta"
echo .proceed-btn { background-color: #f44336; color: white; border: none; } >> "%TEMP%\shutdown_dialog.hta"
echo .warning { color: #e74c3c; font-size: 1.2em; margin-bottom: 10px; } >> "%TEMP%\shutdown_dialog.hta"
echo ^</style^> >> "%TEMP%\shutdown_dialog.hta"
echo ^<script language="VBScript"^> >> "%TEMP%\shutdown_dialog.hta"
echo Sub CancelShutdown >> "%TEMP%\shutdown_dialog.hta"
echo   Set fso = CreateObject("Scripting.FileSystemObject") >> "%TEMP%\shutdown_dialog.hta"
echo   Set file = fso.CreateTextFile("%TEMP%\shutdown_canceled.tmp", True) >> "%TEMP%\shutdown_dialog.hta"
echo   file.Close >> "%TEMP%\shutdown_dialog.hta"
echo   window.close >> "%TEMP%\shutdown_dialog.hta"
echo End Sub >> "%TEMP%\shutdown_dialog.hta"
echo Sub ProceedWithShutdown >> "%TEMP%\shutdown_dialog.hta"
echo   Set fso = CreateObject("Scripting.FileSystemObject") >> "%TEMP%\shutdown_dialog.hta"
echo   Set file = fso.CreateTextFile("%TEMP%\shutdown_first_shown.tmp", True) >> "%TEMP%\shutdown_dialog.hta"
echo   file.Close >> "%TEMP%\shutdown_dialog.hta"
echo   window.close >> "%TEMP%\shutdown_dialog.hta"
echo End Sub >> "%TEMP%\shutdown_dialog.hta"
echo ^</script^> >> "%TEMP%\shutdown_dialog.hta"
echo ^</head^>^<body^> >> "%TEMP%\shutdown_dialog.hta"
echo ^<div class="content"^> >> "%TEMP%\shutdown_dialog.hta"
echo ^<h2 class="warning"^>Shutdown Confirmation^</h2^> >> "%TEMP%\shutdown_dialog.hta"
echo ^<p^>Your PC is scheduled to shut down at 11:00 PM.^</p^> >> "%TEMP%\shutdown_dialog.hta"
echo ^<p^>Do you want to cancel the shutdown?^</p^> >> "%TEMP%\shutdown_dialog.hta"
echo ^<div^> >> "%TEMP%\shutdown_dialog.hta"
echo ^<button class="cancel-btn" onclick="CancelShutdown"^>Yes (Cancel Shutdown)^</button^> >> "%TEMP%\shutdown_dialog.hta"
echo ^<button class="proceed-btn" onclick="ProceedWithShutdown"^>No (Proceed with Shutdown)^</button^> >> "%TEMP%\shutdown_dialog.hta"
echo ^</div^> >> "%TEMP%\shutdown_dialog.hta"
echo ^</div^> >> "%TEMP%\shutdown_dialog.hta"
echo ^</body^>^</html^> >> "%TEMP%\shutdown_dialog.hta"

:: Start the dialog
start "" "%TEMP%\shutdown_dialog.hta"
exit /b

:show_second_dialog
:: Create an HTA application for the final warning dialog
echo ^<html^>^<head^>^<title^>Final Shutdown Warning^</title^> > "%TEMP%\shutdown_final_dialog.hta"
echo ^<HTA:APPLICATION ID="ShutdownFinalApp" APPLICATIONNAME="Final Shutdown Warning" BORDER="dialog" BORDERSTYLE="normal" >> "%TEMP%\shutdown_final_dialog.hta"
echo CAPTION="yes" ICON="warning" MAXIMIZEBUTTON="no" MINIMIZEBUTTON="yes" >> "%TEMP%\shutdown_final_dialog.hta"
echo SHOWINTASKBAR="yes" SINGLEINSTANCE="yes" SYSMENU="yes" VERSION="1.0"^> >> "%TEMP%\shutdown_final_dialog.hta"
echo ^<style^> >> "%TEMP%\shutdown_final_dialog.hta"
echo body { font-family: Arial; background-color: #f0f0f0; text-align: center; margin-top: 20px; } >> "%TEMP%\shutdown_final_dialog.hta"
echo .content { background-color: white; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); padding: 20px; margin: 0 auto; max-width: 400px; } >> "%TEMP%\shutdown_final_dialog.hta"
echo button { padding: 8px 16px; margin: 10px; border-radius: 4px; cursor: pointer; } >> "%TEMP%\shutdown_final_dialog.hta"
echo .cancel-btn { background-color: #4CAF50; color: white; border: none; } >> "%TEMP%\shutdown_final_dialog.hta"
echo .warning { color: #e74c3c; font-size: 1.2em; margin-bottom: 10px; } >> "%TEMP%\shutdown_final_dialog.hta"
echo ^</style^> >> "%TEMP%\shutdown_final_dialog.hta"
echo ^<script language="VBScript"^> >> "%TEMP%\shutdown_final_dialog.hta"
echo Sub CancelShutdown >> "%TEMP%\shutdown_final_dialog.hta"
echo   Set fso = CreateObject("Scripting.FileSystemObject") >> "%TEMP%\shutdown_final_dialog.hta"
echo   Set file = fso.CreateTextFile("%TEMP%\shutdown_canceled.tmp", True) >> "%TEMP%\shutdown_final_dialog.hta"
echo   file.Close >> "%TEMP%\shutdown_final_dialog.hta"
echo   MsgBox "The scheduled shutdown has been canceled.", 64, "Shutdown Canceled" >> "%TEMP%\shutdown_final_dialog.hta"
echo   window.close >> "%TEMP%\shutdown_final_dialog.hta"
echo End Sub >> "%TEMP%\shutdown_final_dialog.hta"

echo Sub Window_onLoad >> "%TEMP%\shutdown_final_dialog.hta"
echo   Set fso = CreateObject("Scripting.FileSystemObject") >> "%TEMP%\shutdown_final_dialog.hta"
echo   Set file = fso.CreateTextFile("%TEMP%\shutdown_second_shown.tmp", True) >> "%TEMP%\shutdown_final_dialog.hta"
echo   file.Close >> "%TEMP%\shutdown_final_dialog.hta"
echo End Sub >> "%TEMP%\shutdown_final_dialog.hta"
echo ^</script^> >> "%TEMP%\shutdown_final_dialog.hta"
echo ^</head^>^<body^> >> "%TEMP%\shutdown_final_dialog.hta"
echo ^<div class="content"^> >> "%TEMP%\shutdown_final_dialog.hta"
echo ^<h2 class="warning"^>Final Shutdown Warning^</h2^> >> "%TEMP%\shutdown_final_dialog.hta"
echo ^<p^>Your PC will shut down in 10 minutes.^</p^> >> "%TEMP%\shutdown_final_dialog.hta"
echo ^<p^>Click the button below to cancel the shutdown.^</p^> >> "%TEMP%\shutdown_final_dialog.hta"
echo ^<div^> >> "%TEMP%\shutdown_final_dialog.hta"
echo ^<button class="cancel-btn" onclick="CancelShutdown"^>Yes (Cancel Shutdown)^</button^> >> "%TEMP%\shutdown_final_dialog.hta"
echo ^</div^> >> "%TEMP%\shutdown_final_dialog.hta"
echo ^</div^> >> "%TEMP%\shutdown_final_dialog.hta"
echo ^</body^>^</html^> >> "%TEMP%\shutdown_final_dialog.hta"

:: Start the dialog
start "" "%TEMP%\shutdown_final_dialog.hta"

:: Create a marker file to indicate we showed the second dialog
echo. > "%TEMP%\shutdown_second_shown.tmp"
exit /b

endlocal