@echo off
echo 执行重命名还原操作...

REM 检查配置文件是否存在
if not exist "config.json" (
    echo 错误: 配置文件 config.json 不存在
    pause
    exit /b 1
)

REM 执行还原操作
python main.py revert "config.json"

REM 等待用户按任意键退出
pause 