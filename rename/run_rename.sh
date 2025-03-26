#!/bin/bash

# 重命名工具运行脚本

# 创建JSON存储目录
mkdir -p data

# 检查参数
if [ $# -lt 2 ]; then
  echo "用法: ./run_rename.sh <命令> <目录路径> [服务器URL] [其他参数...]"
  echo "命令可以是: all, step1, step2, step3, step4 或 help"
  python main.py help
  exit 1
fi

COMMAND="$1"

# 如果是全流程，先删除已有的JSON文件
if [ "$COMMAND" = "all" ]; then
  echo "删除现有的JSON文件..."
  rm -f data/*.json
fi

# 根据命令类型执行不同的操作
case "$COMMAND" in
  "all")
    python main.py step1 "$2" "original_directories.json"
    python main.py step2 "original_directories.json" "$3" "converted_directories.json"
    python main.py step3 "original_directories.json" "converted_directories.json" "name_mapping.json"
    python main.py step4 "$2" "name_mapping.json"
    ;;
  "step1")
    OUTPUT="${3:-data/original_directories.json}"
    python main.py step1 "$2" "$OUTPUT"
    ;;
  "step2")
    INPUT="$2"
    SERVER="$3"
    OUTPUT="${4:-data/converted_directories.json}"
    python main.py step2 "$INPUT" "$SERVER" "$OUTPUT"
    ;;
  "step3")
    ORIG="$2"
    CONV="$3"
    OUTPUT="${4:-data/name_mapping.json}"
    python main.py step3 "$ORIG" "$CONV" "$OUTPUT"
    ;;
  "step4")
    python main.py step4 "$2" "$3"
    ;;
  *)
    python main.py "$@"
    ;;
esac 