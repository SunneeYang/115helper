@echo off
chcp 65001>nul
setlocal EnableDelayedExpansion

REM Check config file
if not exist "config.json" (
    echo Error: config.json not found
    pause
    exit /b 1
)

REM Create data directory if not exists
if not exist "data" mkdir data

REM Check for existing JSON files
set "JSON_EXISTS="
for %%F in (data\*.json) do (
    set "JSON_EXISTS=1"
    goto :check_delete
)

:check_delete
if defined JSON_EXISTS (
    echo Found existing JSON files:
    dir /b "data\*.json"
    echo.
    choice /C YN /M "Delete these files"
    if errorlevel 2 (
        echo Operation cancelled.
        pause
        exit /b 1
    ) else (
        echo Deleting JSON files...
        del /q "data\*.json"
        if errorlevel 1 (
            echo Error deleting files
            pause
            exit /b 1
        )
        echo JSON files deleted successfully.
    )
)

REM Process commands
if "%1"=="" goto :help
if "%1"=="help" goto :help
if "%1"=="all" goto :all
if "%1"=="step1" goto :step1
if "%1"=="step2" goto :step2
if "%1"=="step3" goto :step3
if "%1"=="step4" goto :step4

echo Unknown command: %1
echo Use run_rename.bat help for help
pause
exit /b 1

:help
echo Usage: run_rename.bat ^<command^> [params...]
echo.
echo Commands:
echo     all     - Run all steps
echo     step1   - Scan directories and save list
echo     step2   - Send to server and get converted names
echo     step3   - Create name mapping
echo     step4   - Rename directories
echo     help    - Show help
pause
exit /b 0

:all
echo Running all steps...
python main.py all "%~dp0config.json"
if errorlevel 1 (
    echo Error occurred during execution
    pause
    exit /b 1
)
goto :eof

:step1
echo Running step 1...
python main.py step1 "%~dp0config.json"
if errorlevel 1 (
    echo Error occurred during step 1
    pause
    exit /b 1
)
goto :eof

:step2
echo Running step 2...
python main.py step2 "%~dp0config.json"
if errorlevel 1 (
    echo Error occurred during step 2
    pause
    exit /b 1
)
goto :eof

:step3
echo Running step 3...
python main.py step3 "%~dp0config.json"
if errorlevel 1 (
    echo Error occurred during step 3
    pause
    exit /b 1
)
goto :eof

:step4
echo Running step 4...
python main.py step4 "%~dp0config.json"
if errorlevel 1 (
    echo Error occurred during step 4
    pause
    exit /b 1
)
goto :eof 