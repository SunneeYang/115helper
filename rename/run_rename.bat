@echo off
REM 重命名工具运行脚本

REM 创建JSON存储目录
if not exist data mkdir data

REM 检查参数
if "%~1"=="" (
  echo 用法: run_rename.bat ^<命令^> ^<目录路径^> [服务器URL] [其他参数...]
  echo 命令可以是: all, step1, step2, step3, step4 或 help
  python main.py help
  exit /b 1
)

set COMMAND=%1

REM 如果是全流程，先删除已有的JSON文件
if "%COMMAND%"=="all" (
  echo 删除现有的JSON文件...
  del /q data\*.json 2>nul
)

REM 根据命令类型执行不同的操作
if "%COMMAND%"=="all" (
  python main.py step1 "%2" "data/original_directories.json"
  python main.py step2 "data/original_directories.json" "%3" "data/converted_directories.json"
  python main.py step3 "data/original_directories.json" "data/converted_directories.json" "data/name_mapping.json"
  python main.py step4 "%2" "data/name_mapping.json"
) else if "%COMMAND%"=="step1" (
  if "%~4"=="" (
    python main.py step1 "%2" "data/original_directories.json"
  ) else (
    python main.py step1 "%2" "%3"
  )
) else if "%COMMAND%"=="step2" (
  if "%~5"=="" (
    python main.py step2 "%2" "%3" "data/converted_directories.json"
  ) else (
    python main.py step2 "%2" "%3" "%4"
  )
) else if "%COMMAND%"=="step3" (
  if "%~5"=="" (
    python main.py step3 "%2" "%3" "data/name_mapping.json"
  ) else (
    python main.py step3 "%2" "%3" "%4"
  )
) else if "%COMMAND%"=="step4" (
  python main.py step4 "%2" "%3"
) else (
  python main.py %*
) 