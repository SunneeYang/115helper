#!/bin/bash

# 检查配置文件是否存在
if [ ! -f "config.json" ]; then
    echo "错误: 配置文件 config.json 不存在"
    exit 1
fi

# 执行还原操作
python main.py revert "config.json"

# 等待用户按任意键退出
read -n 1 -s -r -p "按任意键退出..." 