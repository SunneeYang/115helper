# -*- coding: utf-8 -*-
import os
import json
import sys
import logging
import requests
from typing import List, Dict
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rename.log'),
        logging.StreamHandler()
    ]
)

def get_directory_names(directory_path: str) -> List[str]:
    """获取指定目录下的所有文件夹名称"""
    try:
        # 获取目录下的所有项目
        items = os.listdir(directory_path)
        # 过滤出文件夹
        directories = [item for item in items if os.path.isdir(os.path.join(directory_path, item))]
        return sorted(directories)
    except Exception as e:
        logging.error(f"读取目录失败: {e}")
        sys.exit(1)

def save_to_json(data: dict, filename: str):
    """保存数据到JSON文件"""
    try:
        # 确保data目录存在
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        os.makedirs(data_dir, exist_ok=True)
        
        # 构建完整的文件路径
        filepath = os.path.join(data_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logging.info(f"数据已保存到 {filepath}")
    except Exception as e:
        logging.error(f"保存JSON文件失败: {e}")
        sys.exit(1)

def load_from_json(filename: str) -> dict:
    """从JSON文件加载数据"""
    try:
        # 构建完整的文件路径
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        filepath = os.path.join(data_dir, filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logging.info(f"从 {filepath} 加载数据成功")
        return data
    except Exception as e:
        logging.error(f"加载JSON文件失败: {e}")
        sys.exit(1)

def send_to_server(directory_names: List[str], server_url: str) -> List[str]:
    """发送目录名称到服务器并获取转换后的名称"""
    try:
        # 文件名列表格式化（每行一个文件名）
        filenames = "\n".join(directory_names)
        
        # 准备请求数据
        payload = json.dumps({
            "inputs": {
                "filename": filenames
            },
            "response_mode": "blocking",
            "user": "rename-tool"
        })
        
        headers = {
            'Authorization': 'Bearer app-OiPO40nXe8ibTTAJoDBM0Jab',
            'User-Agent': 'Rename-Tool/1.0.0',
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Connection': 'keep-alive'
        }
        
        logging.info(f"发送请求到 {server_url}")
        
        # 发送请求
        response = requests.request("POST", server_url, headers=headers, data=payload)
        
        # 检查响应状态
        if response.status_code != 200:
            logging.error(f"服务器返回错误: {response.status_code}")
            logging.error(f"响应内容: {response.text}")
            sys.exit(1)
        
        # 解析响应
        response_data = response.json()
        
        # 从响应中提取转换后的文件名列表
        if ("data" in response_data and "outputs" in response_data["data"] 
                and "text" in response_data["data"]["outputs"]):
            # 从转换后的字符串中分割出各个文件名
            converted_names = response_data["data"]["outputs"]["text"].strip().split("\n")
            
            # 确保所有名称都转换为大写并去除额外空格
            converted_names = [name.upper().strip() for name in converted_names]
            
            if len(converted_names) != len(directory_names):
                logging.warning(f"转换前的目录数量({len(directory_names)})与转换后的数量({len(converted_names)})不一致")
            
            return converted_names
        else:
            logging.error("服务器响应格式不正确，无法获取转换后的文件名")
            logging.error(f"响应内容: {json.dumps(response_data, ensure_ascii=False)}")
            sys.exit(1)
    
    except Exception as e:
        logging.error(f"与服务器通信失败: {e}")
        sys.exit(1)

def create_mapping(original_names: List[str], converted_names: List[str]) -> Dict[str, str]:
    """创建原始名称和转换后名称的映射"""
    return dict(zip(original_names, converted_names))

def rename_directories_and_files(directory_path: str, mapping: Dict[str, str]):
    """根据映射重命名目录和文件"""
    for old_name, new_name in mapping.items():
        old_path = os.path.join(directory_path, old_name)
        new_path = os.path.join(directory_path, new_name)
        
        # 检查原目录是否存在
        if not os.path.exists(old_path):
            logging.warning(f"目录不存在，跳过重命名: {old_path}")
            continue
            
        # 检查目标名称是否已存在
        if os.path.exists(new_path) and old_path != new_path:
            logging.warning(f"目标目录已存在，跳过重命名: {new_path}")
            continue
            
        # 重命名目录
        try:
            os.rename(old_path, new_path)
            logging.info(f"目录重命名: {old_name} -> {new_name}")
        except Exception as e:
            logging.error(f"重命名目录失败 {old_name}: {e}")
            continue

        # 重命名目录下的文件
        try:
            files = os.listdir(new_path)
            if len(files) == 1:  # 只有当目录下只有一个文件时才重命名
                old_file = files[0]
                file_ext = os.path.splitext(old_file)[1]
                new_file = new_name + file_ext
                old_file_path = os.path.join(new_path, old_file)
                new_file_path = os.path.join(new_path, new_file)
                if old_file_path != new_file_path:
                    os.rename(old_file_path, new_file_path)
                    logging.info(f"文件重命名: {old_file} -> {new_file}")
            elif len(files) > 1:
                logging.warning(f"目录 {new_name} 包含多个文件，跳过文件重命名")
        except Exception as e:
            logging.error(f"重命名文件失败 {old_name}: {e}")

def step1_scan_directories(directory_path: str, output_file: str = "original_directories.json"):
    """扫描目录的文件夹并保存目录名字列表到json"""
    logging.info("执行步骤1: 扫描目录并保存目录名列表")
    directory_names = get_directory_names(directory_path)
    save_to_json({"directories": directory_names}, output_file)
    logging.info(f"已找到 {len(directory_names)} 个目录并保存到 {output_file}")
    return directory_names

def step2_send_to_server(input_file: str, server_url: str, output_file: str = "converted_directories.json"):
    """加载json文件把目录名列表发给服务器获取新的列表并保存"""
    logging.info("执行步骤2: 发送目录名列表到服务器并获取转换后的名称")
    data = load_from_json(input_file)
    directory_names = data.get("directories", [])
    if not directory_names:
        logging.error(f"在 {input_file} 中没有找到目录名列表")
        sys.exit(1)
        
    converted_names = send_to_server(directory_names, server_url)
    save_to_json({"directories": converted_names}, output_file)
    logging.info(f"已获取 {len(converted_names)} 个转换后的目录名并保存到 {output_file}")
    return converted_names

def step3_create_mapping(original_file: str, converted_file: str, output_file: str = "name_mapping.json"):
    """加载两个json文件，生成转换前后目录名的对应关系"""
    logging.info("执行步骤3: 生成转换前后目录名的对应关系")
    original_data = load_from_json(original_file)
    converted_data = load_from_json(converted_file)
    
    original_names = original_data.get("directories", [])
    converted_names = converted_data.get("directories", [])
    
    if len(original_names) != len(converted_names):
        logging.error("原始目录名列表和转换后目录名列表长度不一致")
        sys.exit(1)
        
    mapping = create_mapping(original_names, converted_names)
    save_to_json(mapping, output_file)
    logging.info(f"已生成 {len(mapping)} 个名称映射关系并保存到 {output_file}")
    return mapping

def step4_rename_directories(directory_path: str, mapping_file: str):
    """加载对应关系的json重命名目录和目录内的文件"""
    logging.info("执行步骤4: 重命名目录和目录内的文件")
    mapping = load_from_json(mapping_file)
    rename_directories_and_files(directory_path, mapping)
    logging.info("重命名操作完成")

def print_help():
    """打印帮助信息"""
    print("""
目录重命名工具 - 使用说明：

完整流程：
python main.py all <目标目录路径> <服务器URL>

分步执行：
1. 扫描目录并保存列表：
   python main.py step1 <目标目录路径> [输出文件名]

2. 发送到服务器并获取转换后的列表：
   python main.py step2 <输入文件名> <服务器URL> [输出文件名]

3. 生成名称映射关系：
   python main.py step3 <原始目录名文件> <转换后目录名文件> [输出文件名]

4. 重命名目录和文件：
   python main.py step4 <目标目录路径> <映射关系文件>

注意: 方括号 [] 中的参数是可选的
    """)

def main():
    args = sys.argv[1:]
    
    if len(args) == 0 or args[0] in ['-h', '--help', 'help']:
        print_help()
        return
        
    command = args[0]
    
    if command == "step1":
        if len(args) < 2:
            print("错误: 缺少目标目录路径")
            print_help()
            return
        directory_path = args[1]
        output_file = args[2] if len(args) > 2 else "original_directories.json"
        step1_scan_directories(directory_path, output_file)
        
    elif command == "step2":
        if len(args) < 3:
            print("错误: 缺少输入文件或服务器URL")
            print_help()
            return
        input_file = args[1]
        server_url = args[2]
        output_file = args[3] if len(args) > 3 else "converted_directories.json"
        step2_send_to_server(input_file, server_url, output_file)
        
    elif command == "step3":
        if len(args) < 3:
            print("错误: 缺少原始目录名文件或转换后目录名文件")
            print_help()
            return
        original_file = args[1]
        converted_file = args[2]
        output_file = args[3] if len(args) > 3 else "name_mapping.json"
        step3_create_mapping(original_file, converted_file, output_file)
        
    elif command == "step4":
        if len(args) < 3:
            print("错误: 缺少目标目录路径或映射关系文件")
            print_help()
            return
        directory_path = args[1]
        mapping_file = args[2]
        step4_rename_directories(directory_path, mapping_file)
        
    elif command == "all":
        if len(args) < 3:
            print("错误: 缺少目标目录路径或服务器URL")
            print_help()
            return
        directory_path = args[1]
        server_url = args[2]
        
        # 执行完整流程
        directory_names = step1_scan_directories(directory_path)
        converted_names = step2_send_to_server("original_directories.json", server_url)
        step3_create_mapping("original_directories.json", "converted_directories.json")
        step4_rename_directories(directory_path, "name_mapping.json")
        
    else:
        print(f"错误: 未知命令 '{command}'")
        print_help()

if __name__ == "__main__":
    main() 