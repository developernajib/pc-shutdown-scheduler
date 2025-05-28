@echo off
setlocal enabledelayedexpansion

:: PC Shutdown Scheduler - Enhanced Batch Version
:: Enhanced with Friday exemption and proper user cancellation

:: Configure times (24-hour format)
set "FIRST_DIALOG_HOUR=21"
set "FIRST_DIALOG_MIN=30"
set "SECOND_DIALOG_HOUR=22"
set "SECOND_DIALOG_MIN=50"
set "SHUTDOWN_HOUR=23"
set "SHUTDOWN_MIN=00"

:: Set up logging
set "LOG_FILE=%USERPROFILE%\shutdown_scheduler.log"

:: Check if today is Friday (weekday 6 in Windows)
for /f "skip=1 tokens=2 delims= " %%a in ('wmic path win32_localtime get dayofweek /value') do (
    for /f "tokens=2 delims==" %%b in ("%%a") do set "DAYOFWEEK=%%b"
)

:: If Friday (6), exit immediately
if "%DAYOFWEEK%"=="6" (
    echo [%date% %time%]: 🎉 TODAY IS FRIDAY - Shutdown scheduler disabled for the weekend! >> "%LOG_FILE%"
    echo [%date% %time%]: 📅 The scheduler will resume automatically on Monday >> "%LOG_FILE%"
    echo 🎉 It's Friday! No shutdown scheduled today. Enjoy your weekend!
    timeout /t 3 >nul
    exit
)

echo Shutdown Scheduler: Started at %date% %time% >> "%LOG_FILE%"
echo [%date% %time%]: ✅ Shutdown scheduler started and running in background >> "%LOG_FILE%"

:: Get day name for logging
for /f "skip=1 delims= " %%a in ('wmic path win32_localtime get dayofweek /format:list') do (
    for /f "tokens=2 delims==" %%b in ("%%a") do (
        set "DAYNUM=%%b"
        if "%%b"=="1" set "DAYNAME=Monday"
        if "%%b"=="2" set "DAYNAME=Tuesday"
        if "%%b"=="3" set "DAYNAME=Wednesday"
        if "%%b"=="4" set "DAYNAME=Thursday"
        if "%%b"=="5" set "DAYNAME=Friday"
        if "%%b"=="6" set "DAYNAME=Saturday"
        if "%%b"=="7" set "DAYNAME=Sunday"
    )
)

echo [%date% %time%]: 📅 Today is %DAYNAME% - shutdown is scheduled >> "%LOG_FILE%"
echo [%date% %time%]: 🕘 Schedule: First warning at %FIRST_DIALOG_HOUR%:%FIRST_DIALOG_MIN%, Final warning at %SECOND_DIALOG_HOUR%:%SECOND_DIALOG_MIN%, Shutdown at %SHUTDOWN_HOUR%:%SHUTDOWN_MIN% >> "%LOG_FILE%"

:: Clear any existing temp files from previous runs
if exist "%TEMP%\shutdown_first_shown.tmp" del "%TEMP%\shutdown_first_shown.tmp"
if exist "%TEMP%\shutdown_second_shown.tmp" del "%TEMP%\shutdown_second_shown.tmp"
if exist "%TEMP%\shutdown_canceled.tmp" del "%TEMP%\shutdown_canceled.tmp"
if exist "%TEMP%\shutdown_dialog.hta" del "%TEMP%\shutdown_dialog.hta"
if exist "%TEMP%\shutdown_final_dialog.hta" del "%TEMP%\shutdown_final_dialog.hta"

:: Hide this window (will still show briefly at startup)
if not "%1"=="HIDDEN" (
    start /min "" "%~dpnx0" HIDDEN
    exit
)

:main_loop
:: Check if it's Friday again (in case day changed during execution)
for /f "skip=1 tokens=2 delims= " %%a in ('wmic path win32_localtime get dayofweek /value') do (
    for /f "tokens=2 delims==" %%b in ("%%a") do set "CURRENT_DAYOFWEEK=%%b"
)

if "%CURRENT_DAYOFWEEK%"=="6" (
    echo [%date% %time%]: 🎉 Day changed to Friday - canceling shutdown >> "%LOG_FILE%"
    call :cleanup_files
    exit
)

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

:: Check if we should show first dialog
if %CURRENT_TIME_MINS% GEQ %FIRST_DIALOG_TIME_MINS% if %CURRENT_TIME_MINS% LSS %SECOND_DIALOG_TIME_MINS% (
    if not exist "%TEMP%\shutdown_first_shown.tmp" (
        if not exist "%TEMP%\shutdown_canceled.tmp" (
            echo [%date% %time%]: 📢 Displaying first shutdown warning dialog >> "%LOG_FILE%"
            call :show_first_dialog
        )
    )
)

:: Check if we should show second dialog
if %CURRENT_TIME_MINS% GEQ %SECOND_DIALOG_TIME_MINS% if %CURRENT_TIME_MINS% LSS %SHUTDOWN_TIME_MINS% (
    if not exist "%TEMP%\shutdown_second_shown.tmp" (
        if not exist "%TEMP%\shutdown_canceled.tmp" (
            :: Close first dialog if it's still open
            taskkill /f /im mshta.exe >nul 2>&1
            
            :: If first dialog was shown but user didn't interact, log it
            if exist "%TEMP%\shutdown_first_shown.tmp" (
                if not exist "%TEMP%\shutdown_user_responded.tmp" (
                    echo [%date% %time%]: ℹ️ First dialog closed without interaction (proceeding with shutdown) >> "%LOG_FILE%"
                )
            )
            
            :: Delete first dialog marker
            if exist "%TEMP%\shutdown_first_shown.tmp" del "%TEMP%\shutdown_first_shown.tmp"
            
            echo [%date% %time%]: 📢 Displaying final shutdown warning dialog (10 minutes remaining) >> "%LOG_FILE%"
            call :show_second_dialog
        )
    )
)

:: Check if it's shutdown time
if %CURRENT_TIME_MINS% GEQ %SHUTDOWN_TIME_MINS% (
    :: Only shut down if not canceled
    if not exist "%TEMP%\shutdown_canceled.tmp" (
        :: Final Friday check before shutdown
        for /f "skip=1 tokens=2 delims= " %%a in ('wmic path win32_localtime get dayofweek /value') do (
            for /f "tokens=2 delims==" %%b in ("%%a") do set "FINAL_DAYOFWEEK=%%b"
        )
        
        if "!FINAL_DAYOFWEEK!"=="6" (
            echo [%date% %time%]: 🎉 Friday detected at shutdown time - aborting shutdown >> "%LOG_FILE%"
            call :cleanup_files
            exit
        )
        
        :: If second dialog was shown but user didn't interact, log it
        if exist "%TEMP%\shutdown_second_shown.tmp" (
            if not exist "%TEMP%\shutdown_user_responded.tmp" (
                echo [%date% %time%]: ℹ️ Final dialog closed without interaction (proceeding with shutdown) >> "%LOG_FILE%"
            )
        )
        
        echo [%date% %time%]: 🕒 Shutdown time reached, initiating shutdown >> "%LOG_FILE%"
        echo [%date% %time%]: 🔴 PC SHUTDOWN INITIATED at scheduled time (11:00 PM) >> "%LOG_FILE%"
        echo [%date% %time%]: 💻 No user interaction detected to cancel the shutdown >> "%LOG_FILE%"
        
        :: Kill any remaining dialog windows
        taskkill /f /im mshta.exe >nul 2>&1
        
        :: Execute the shutdown command
        shutdown /s /t 5 /f /c "Scheduled shutdown at 11:00 PM"
        exit
    ) else (
        echo [%date% %time%]: ✅ Shutdown time reached but shutdown was previously canceled >> "%LOG_FILE%"
        :: Clean up temp files
        call :cleanup_files
        exit
    )
)

:: Check every 30 seconds for better responsiveness
timeout /t 30 /nobreak >nul
goto main_loop

:cleanup_files
:: Clean up temporary files
if exist "%TEMP%\shutdown_first_shown.tmp" del "%TEMP%\shutdown_first_shown.tmp"
if exist "%TEMP%\shutdown_second_shown.tmp" del "%TEMP%\shutdown_second_shown.tmp"
if exist "%TEMP%\shutdown_user_responded.tmp" del "%TEMP%\shutdown_user_responded.tmp"
if exist "%TEMP%\shutdown_dialog.hta" del "%TEMP%\shutdown_dialog.hta"
if exist "%TEMP%\shutdown_final_dialog.hta" del "%TEMP%\shutdown_final_dialog.hta"
if exist "%TEMP%\shutdown_canceled.tmp" del "%TEMP%\shutdown_canceled.tmp"
exit /b

:show_first_dialog
:: Create an HTA application for the dialog
echo ^<html^>^<head^>^<title^>Shutdown Confirmation^</title^> > "%TEMP%\shutdown_dialog.hta"
echo ^<HTA:APPLICATION ID="ShutdownApp" APPLICATIONNAME="Shutdown Confirmation" BORDER="dialog" BORDERSTYLE="normal" >> "%TEMP%\shutdown_dialog.hta"
echo CAPTION="yes" ICON="warning" MAXIMIZEBUTTON="no" MINIMIZEBUTTON="yes" >> "%TEMP%\shutdown_dialog.hta"
echo SHOWINTASKBAR="yes" SINGLEINSTANCE="yes" SYSMENU="yes" VERSION="1.0"^> >> "%TEMP%\shutdown_dialog.hta"
echo ^<style^> >> "%TEMP%\shutdown_dialog.hta"
echo body { font-family: Arial; background-color: #f0f0f0; text-align: center; margin-top: 20px; } >> "%TEMP%\shutdown_dialog.hta"
echo .content { background-color: white; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); padding: 25px; margin: 0 auto; max-width: 450px; } >> "%TEMP%\shutdown_dialog.hta"
echo button { padding: 10px 20px; margin: 15px; border-radius: 6px; cursor: pointer; font-size: 11px; font-weight: bold; } >> "%TEMP%\shutdown_dialog.hta"
echo .cancel-btn { background-color: #4CAF50; color: white; border: none; } >> "%TEMP%\shutdown_dialog.hta"
echo .proceed-btn { background-color: #f44336; color: white; border: none; } >> "%TEMP%\shutdown_dialog.hta"
echo .warning { color: #e74c3c; font-size: 1.3em; margin-bottom: 15px; font-weight: bold; } >> "%TEMP%\shutdown_dialog.hta"
echo .question { font-size: 1.1em; margin: 15px 0; color: #333; } >> "%TEMP%\shutdown_dialog.hta"
echo ^</style^> >> "%TEMP%\shutdown_dialog.hta"
echo ^<script language="VBScript"^> >> "%TEMP%\shutdown_dialog.hta"
echo Sub CancelShutdown >> "%TEMP%\shutdown_dialog.hta"
echo   CreateLogFile("✅ SHUTDOWN CANCELED by user at first dialog (clicked YES)") >> "%TEMP%\shutdown_dialog.hta"
echo   Set fso = CreateObject("Scripting.FileSystemObject") >> "%TEMP%\shutdown_dialog.hta"
echo   Set file = fso.CreateTextFile("%TEMP%\shutdown_canceled.tmp", True) >> "%TEMP%\shutdown_dialog.hta"
echo   file.Close >> "%TEMP%\shutdown_dialog.hta"
echo   Set userFile = fso.CreateTextFile("%TEMP%\shutdown_user_responded.tmp", True) >> "%TEMP%\shutdown_dialog.hta"
echo   userFile.Close >> "%TEMP%\shutdown_dialog.hta"
echo   MsgBox "✅ The scheduled shutdown has been canceled!" ^& vbCrLf ^& vbCrLf ^& "Your PC will NOT shut down at 11:00 PM today.", 64, "Shutdown Canceled" >> "%TEMP%\shutdown_dialog.hta"
echo   CreateLogFile("🛑 Script terminating - shutdown canceled by user") >> "%TEMP%\shutdown_dialog.hta"
echo   window.close >> "%TEMP%\shutdown_dialog.hta"
echo   ' Force terminate the batch script >> "%TEMP%\shutdown_dialog.hta"
echo   Set objShell = CreateObject("WScript.Shell") >> "%TEMP%\shutdown_dialog.hta"
echo   objShell.Run "taskkill /f /im cmd.exe /fi ""WINDOWTITLE eq Administrator:*shutdown*""", 0, False >> "%TEMP%\shutdown_dialog.hta"
echo End Sub >> "%TEMP%\shutdown_dialog.hta"

echo Sub ProceedWithShutdown >> "%TEMP%\shutdown_dialog.hta"
echo   CreateLogFile("⏭️ User clicked NO - will proceed with scheduled shutdown") >> "%TEMP%\shutdown_dialog.hta"
echo   Set fso = CreateObject("Scripting.FileSystemObject") >> "%TEMP%\shutdown_dialog.hta"
echo   Set file = fso.CreateTextFile("%TEMP%\shutdown_first_shown.tmp", True) >> "%TEMP%\shutdown_dialog.hta"
echo   file.Close >> "%TEMP%\shutdown_dialog.hta"
echo   Set userFile = fso.CreateTextFile("%TEMP%\shutdown_user_responded.tmp", True) >> "%TEMP%\shutdown_dialog.hta"
echo   userFile.Close >> "%TEMP%\shutdown_dialog.hta"
echo   window.close >> "%TEMP%\shutdown_dialog.hta"
echo End Sub >> "%TEMP%\shutdown_dialog.hta"

echo Sub Window_onLoad >> "%TEMP%\shutdown_dialog.hta"
echo   Set fso = CreateObject("Scripting.FileSystemObject") >> "%TEMP%\shutdown_dialog.hta"
echo   Set file = fso.CreateTextFile("%TEMP%\shutdown_first_shown.tmp", True) >> "%TEMP%\shutdown_dialog.hta"
echo   file.Close >> "%TEMP%\shutdown_dialog.hta"
echo End Sub >> "%TEMP%\shutdown_dialog.hta"

echo Function CreateLogFile(message) >> "%TEMP%\shutdown_dialog.hta"
echo   On Error Resume Next >> "%TEMP%\shutdown_dialog.hta"
echo   Dim fso, logFile, timestamp >> "%TEMP%\shutdown_dialog.hta"
echo   Set fso = CreateObject("Scripting.FileSystemObject") >> "%TEMP%\shutdown_dialog.hta"
echo   timestamp = Now >> "%TEMP%\shutdown_dialog.hta"
echo   Set logFile = fso.OpenTextFile("%USERPROFILE%\shutdown_scheduler.log", 8, True) >> "%TEMP%\shutdown_dialog.hta"
echo   If Err.Number <> 0 Then >> "%TEMP%\shutdown_dialog.hta"
echo     Set logFile = fso.CreateTextFile("%USERPROFILE%\shutdown_scheduler.log", True) >> "%TEMP%\shutdown_dialog.hta"
echo   End If >> "%TEMP%\shutdown_dialog.hta"
echo   logFile.WriteLine "[" ^& FormatDateTime(timestamp, 2) ^& " " ^& FormatDateTime(timestamp, 4) ^& "]: " ^& message >> "%TEMP%\shutdown_dialog.hta"
echo   logFile.Close >> "%TEMP%\shutdown_dialog.hta"
echo   On Error Goto 0 >> "%TEMP%\shutdown_dialog.hta"
echo End Function >> "%TEMP%\shutdown_dialog.hta"

echo ^</script^> >> "%TEMP%\shutdown_dialog.hta"
echo ^</head^>^<body^> >> "%TEMP%\shutdown_dialog.hta"
echo ^<div class="content"^> >> "%TEMP%\shutdown_dialog.hta"
echo ^<h2 class="warning"^>🚨 Shutdown Confirmation^</h2^> >> "%TEMP%\shutdown_dialog.hta"
echo ^<p^>Your PC is scheduled to shut down at 11:00 PM.^</p^> >> "%TEMP%\shutdown_dialog.hta"
echo ^<p class="question"^>^<strong^>Do you want to cancel the shutdown?^</strong^>^</p^> >> "%TEMP%\shutdown_dialog.hta"
echo ^<div^> >> "%TEMP%\shutdown_dialog.hta"
echo ^<button class="cancel-btn" onclick="CancelShutdown"^>YES - Cancel Shutdown^</button^> >> "%TEMP%\shutdown_dialog.hta"
echo ^<button class="proceed-btn" onclick="ProceedWithShutdown"^>NO - Let PC Shutdown^</button^> >> "%TEMP%\shutdown_dialog.hta"
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
echo .content { background-color: white; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); padding: 25px; margin: 0 auto; max-width: 450px; } >> "%TEMP%\shutdown_final_dialog.hta"
echo button { padding: 12px 25px; margin: 15px; border-radius: 6px; cursor: pointer; font-size: 12px; font-weight: bold; } >> "%TEMP%\shutdown_final_dialog.hta"
echo .cancel-btn { background-color: #4CAF50; color: white; border: none; } >> "%TEMP%\shutdown_final_dialog.hta"
echo .proceed-btn { background-color: #f44336; color: white; border: none; } >> "%TEMP%\shutdown_final_dialog.hta"
echo .warning { color: #e74c3c; font-size: 1.4em; margin-bottom: 15px; font-weight: bold; } >> "%TEMP%\shutdown_final_dialog.hta"
echo #countdown { font-weight: bold; font-size: 1.2em; color: #e74c3c; } >> "%TEMP%\shutdown_final_dialog.hta"
echo .info { font-size: 0.9em; color: #666; margin-top: 10px; } >> "%TEMP%\shutdown_final_dialog.hta"
echo ^</style^> >> "%TEMP%\shutdown_final_dialog.hta"
echo ^<script language="VBScript"^> >> "%TEMP%\shutdown_final_dialog.hta"
echo Dim countdown >> "%TEMP%\shutdown_final_dialog.hta"
echo countdown = 10 >> "%TEMP%\shutdown_final_dialog.hta"

echo Sub CancelShutdown >> "%TEMP%\shutdown_final_dialog.hta"
echo   CreateLogFile("✅ SHUTDOWN CANCELED by user at final dialog (clicked YES)") >> "%TEMP%\shutdown_final_dialog.hta"
echo   Set fso = CreateObject("Scripting.FileSystemObject") >> "%TEMP%\shutdown_final_dialog.hta"
echo   Set file = fso.CreateTextFile("%TEMP%\shutdown_canceled.tmp", True) >> "%TEMP%\shutdown_final_dialog.hta"
echo   file.Close >> "%TEMP%\shutdown_final_dialog.hta"
echo   Set userFile = fso.CreateTextFile("%TEMP%\shutdown_user_responded.tmp", True) >> "%TEMP%\shutdown_final_dialog.hta"
echo   userFile.Close >> "%TEMP%\shutdown_final_dialog.hta"
echo   MsgBox "✅ The scheduled shutdown has been canceled!" ^& vbCrLf ^& vbCrLf ^& "Your PC will NOT shut down at 11:00 PM today.", 64, "Shutdown Canceled" >> "%TEMP%\shutdown_final_dialog.hta"
echo   CreateLogFile("🛑 Script terminating - shutdown canceled by user") >> "%TEMP%\shutdown_final_dialog.hta"
echo   window.close >> "%TEMP%\shutdown_final_dialog.hta"
echo   ' Force terminate the batch script >> "%TEMP%\shutdown_final_dialog.hta"
echo   Set objShell = CreateObject("WScript.Shell") >> "%TEMP%\shutdown_final_dialog.hta"
echo   objShell.Run "taskkill /f /im cmd.exe /fi ""WINDOWTITLE eq Administrator:*shutdown*""", 0, False >> "%TEMP%\shutdown_final_dialog.hta"
echo End Sub >> "%TEMP%\shutdown_final_dialog.hta"

echo Sub ProceedWithShutdown >> "%TEMP%\shutdown_final_dialog.hta"
echo   CreateLogFile("⏭️ User clicked NO - will proceed with scheduled shutdown") >> "%TEMP%\shutdown_final_dialog.hta"
echo   Set fso = CreateObject("Scripting.FileSystemObject") >> "%TEMP%\shutdown_final_dialog.hta"
echo   Set userFile = fso.CreateTextFile("%TEMP%\shutdown_user_responded.tmp", True) >> "%TEMP%\shutdown_final_dialog.hta"
echo   userFile.Close >> "%TEMP%\shutdown_final_dialog.hta"
echo   window.close >> "%TEMP%\shutdown_final_dialog.hta"
echo End Sub >> "%TEMP%\shutdown_final_dialog.hta"

echo Sub Window_onLoad >> "%TEMP%\shutdown_final_dialog.hta"
echo   Set fso = CreateObject("Scripting.FileSystemObject") >> "%TEMP%\shutdown_final_dialog.hta"
echo   Set file = fso.CreateTextFile("%TEMP%\shutdown_second_shown.tmp", True) >> "%TEMP%\shutdown_final_dialog.hta"
echo   file.Close >> "%TEMP%\shutdown_final_dialog.hta"
echo   CreateLogFile("⏰ Countdown to shutdown started (10 minutes remaining)") >> "%TEMP%\shutdown_final_dialog.hta"
echo   window.setTimeout "UpdateCountdown", 60000 >> "%TEMP%\shutdown_final_dialog.hta"
echo End Sub >> "%TEMP%\shutdown_final_dialog.hta"

echo Sub UpdateCountdown >> "%TEMP%\shutdown_final_dialog.hta"
echo   countdown = countdown - 1 >> "%TEMP%\shutdown_final_dialog.hta"
echo   document.getElementById("countdown").innerHTML = countdown >> "%TEMP%\shutdown_final_dialog.hta"
echo   If countdown > 1 Then >> "%TEMP%\shutdown_final_dialog.hta"
echo     window.setTimeout "UpdateCountdown", 60000 >> "%TEMP%\shutdown_final_dialog.hta"
echo   End If >> "%TEMP%\shutdown_final_dialog.hta"
echo End Sub >> "%TEMP%\shutdown_final_dialog.hta"

echo Function CreateLogFile(message) >> "%TEMP%\shutdown_final_dialog.hta"
echo   On Error Resume Next >> "%TEMP%\shutdown_final_dialog.hta"
echo   Dim fso, logFile, timestamp >> "%TEMP%\shutdown_final_dialog.hta"
echo   Set fso = CreateObject("Scripting.FileSystemObject") >> "%TEMP%\shutdown_final_dialog.hta"
echo   timestamp = Now >> "%TEMP%\shutdown_final_dialog.hta"
echo   Set logFile = fso.OpenTextFile("%USERPROFILE%\shutdown_scheduler.log", 8, True) >> "%TEMP%\shutdown_final_dialog.hta"
echo   If Err.Number <> 0 Then >> "%TEMP%\shutdown_final_dialog.hta"
echo     Set logFile = fso.CreateTextFile("%USERPROFILE%\shutdown_scheduler.log", True) >> "%TEMP%\shutdown_final_dialog.hta"
echo   End If >> "%TEMP%\shutdown_final_dialog.hta"
echo   logFile.WriteLine "[" ^& FormatDateTime(timestamp, 2) ^& " " ^& FormatDateTime(timestamp, 4) ^& "]: " ^& message >> "%TEMP%\shutdown_final_dialog.hta"
echo   logFile.Close >> "%TEMP%\shutdown_final_dialog.hta"
echo   On Error Goto 0 >> "%TEMP%\shutdown_final_dialog.hta"
echo End Function >> "%TEMP%\shutdown_final_dialog.hta"

echo ^</script^> >> "%TEMP%\shutdown_final_dialog.hta"
echo ^</head^>^<body^> >> "%TEMP%\shutdown_final_dialog.hta"
echo ^<div class="content"^> >> "%TEMP%\shutdown_final_dialog.hta"
echo ^<h2 class="warning"^>🚨 FINAL WARNING 🚨^</h2^> >> "%TEMP%\shutdown_final_dialog.hta"
echo ^<p^>Your PC will shut down in ^<span id="countdown"^>10^</span^> minutes!^</p^> >> "%TEMP%\shutdown_final_dialog.hta"
echo ^<p^>^<strong^>(at exactly 11:00 PM)^</strong^>^</p^> >> "%TEMP%\shutdown_final_dialog.hta"
echo ^<div^> >> "%TEMP%\shutdown_final_dialog.hta"
echo ^<button class="cancel-btn" onclick="CancelShutdown"^>YES - Cancel Shutdown^</button^> >> "%TEMP%\shutdown_final_dialog.hta"
echo ^<button class="proceed-btn" onclick="ProceedWithShutdown"^>NO - Let PC Shutdown^</button^> >> "%TEMP%\shutdown_final_dialog.hta"
echo ^</div^> >> "%TEMP%\shutdown_final_dialog.hta"
echo ^<p class="info"^>If you do nothing, PC will shutdown automatically.^</p^> >> "%TEMP%\shutdown_final_dialog.hta"
echo ^</div^> >> "%TEMP%\shutdown_final_dialog.hta"
echo ^</body^>^</html^> >> "%TEMP%\shutdown_final_dialog.hta"

:: Start the dialog
start "" "%TEMP%\shutdown_final_dialog.hta"

:: Create a marker file to indicate we showed the second dialog
echo. > "%TEMP%\shutdown_second_shown.tmp"
exit /b

endlocal