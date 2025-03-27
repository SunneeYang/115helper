# -*- coding: utf-8 -*-
import os
import json
import sys
import logging
import requests
import time
from typing import List, Dict
from pathlib import Path
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rename.log'),
        logging.StreamHandler()
    ]
)

def confirm_continue(message: str) -> bool:
    """确认是否继续执行下一步"""
    while True:
        response = input(f"\n{message}\n是否继续？(y/n): ").lower().strip()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        print("请输入 y 或 n")

def print_json_file(filepath: str):
    """打印JSON文件内容"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"\n{filepath} 的内容:")
            print(json.dumps(data, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"读取文件 {filepath} 失败: {str(e)}")

def load_config(config_file: str) -> dict:
    """从配置文件加载配置"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        logging.info(f"从 {config_file} 加载配置成功")
        return config
    except Exception as e:
        logging.error(f"加载配置文件失败: {e}")
        sys.exit(1)

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
        # 如果filename是相对路径，则使用data目录
        if not os.path.isabs(filename):
            data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
            os.makedirs(data_dir, exist_ok=True)
            filepath = os.path.join(data_dir, filename)
        else:
            # 如果是绝对路径，直接使用
            filepath = filename
            # 确保目标目录存在
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logging.info(f"数据已保存到 {filepath}")
    except Exception as e:
        logging.error(f"保存JSON文件失败: {str(e)}")
        raise

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

def send_to_server(directory_names: List[str], server_url: str, access_token: str) -> List[str]:
    """发送目录名称到服务器并获取转换后的名称"""
    max_retries = 3
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            # 文件名列表格式化（每行一个文件名）
            filenames = "\n".join(directory_names)
            
            # 准备请求数据
            payload = json.dumps({
                "inputs": {
                    "filename": filenames
                },
                "response_mode": "blocking",
                "user": "abc-123"
            })
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            logging.info(f"发送请求到 {server_url}")
            logging.info(f"请求数据: {payload}")
            logging.info("服务器处理可能需要较长时间，请耐心等待...")
            
            # 发送请求，设置更长的超时时间
            response = requests.request(
                "POST", 
                server_url, 
                headers=headers, 
                data=payload, 
                timeout=600,  # 增加到10分钟
                verify=False  # 忽略SSL验证
            )
            
            # 检查响应状态
            if response.status_code != 200:
                logging.error(f"服务器返回错误状态码: {response.status_code}")
                if attempt < max_retries - 1:
                    logging.info(f"将在 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)
                    continue
                sys.exit(1)
                
            # 解析响应数据
            try:
                response_data = response.json()
                logging.info(f"服务器响应: {json.dumps(response_data, ensure_ascii=False)}")
            except json.JSONDecodeError as e:
                logging.error(f"解析服务器响应失败: {e}")
                if attempt < max_retries - 1:
                    logging.info(f"将在 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)
                    continue
                sys.exit(1)
            
            # 获取转换后的文件名列表，并去除每个名称前后的空格
            if "data" in response_data and "outputs" in response_data["data"]:
                converted_names = [name.strip() for name in response_data["data"]["outputs"]["text"].strip().split("\n")]
                if converted_names:
                    logging.info(f"成功获取到 {len(converted_names)} 个转换后的文件名")
                    return converted_names
                    
            logging.error("服务器返回的数据中没有转换后的文件名")
            if attempt < max_retries - 1:
                logging.info(f"将在 {retry_delay} 秒后重试...")
                time.sleep(retry_delay)
                continue
            sys.exit(1)
            
        except requests.exceptions.Timeout:
            logging.error("请求超时")
            if attempt < max_retries - 1:
                logging.info(f"将在 {retry_delay} 秒后重试...")
                time.sleep(retry_delay)
                continue
            sys.exit(1)
        except requests.exceptions.RequestException as e:
            logging.error(f"请求失败: {e}")
            if attempt < max_retries - 1:
                logging.info(f"将在 {retry_delay} 秒后重试...")
                time.sleep(retry_delay)
                continue
            sys.exit(1)
        except Exception as e:
            logging.error(f"发生未知错误: {e}")
            if attempt < max_retries - 1:
                logging.info(f"将在 {retry_delay} 秒后重试...")
                time.sleep(retry_delay)
                continue
            sys.exit(1)
    
    logging.error("达到最大重试次数，操作失败")
    sys.exit(1)

def create_mapping(original_names: List[str], converted_names: List[str]) -> Dict[str, str]:
    """创建原始名称和转换后名称的映射"""
    if len(original_names) != len(converted_names):
        logging.warning(f"原始名称({len(original_names)}个)和转换后名称({len(converted_names)}个)的数量不匹配")
        # 使用较短的长度来创建映射
        min_length = min(len(original_names), len(converted_names))
        mapping = dict(zip(original_names[:min_length], converted_names[:min_length]))
        # 记录未映射的名称
        if len(original_names) > min_length:
            logging.warning(f"以下原始名称未被映射: {original_names[min_length:]}")
        if len(converted_names) > min_length:
            logging.warning(f"以下转换后名称未被映射: {converted_names[min_length:]}")
        return mapping
    return dict(zip(original_names, converted_names))

def rename_directories_and_files(config_file):
    """重命名目录和文件"""
    # 加载配置
    config = load_config(config_file)
    target_dir = config['target_dir']
    data_dir = config['data_dir']
    files = config['files']
    
    # 加载名称映射
    mapping_file = os.path.join(data_dir, files['name_mapping'])
    if not os.path.exists(mapping_file):
        logging.error(f"名称映射文件不存在: {mapping_file}")
        return
    
    with open(mapping_file, 'r', encoding='utf-8') as f:
        name_mapping = json.load(f)
    
    # 获取目录下的所有文件夹，创建大小写不敏感的映射
    actual_dirs = {}
    for item in os.listdir(target_dir):
        if os.path.isdir(os.path.join(target_dir, item)):
            actual_dirs[item.lower()] = item
    
    # 存储重命名记录
    rename_records = []
    
    # 重命名目录和文件
    for old_name, new_name in name_mapping.items():
        # 使用实际的目录名（大小写匹配）
        actual_old_name = actual_dirs.get(old_name.lower())
        if not actual_old_name:
            logging.warning(f"源目录不存在: {old_name}")
            continue
            
        old_path = os.path.join(target_dir, actual_old_name)
        new_path = os.path.join(target_dir, new_name)
        
        # 记录目录重命名操作
        dir_renamed = False
        
        try:
            # 如果新旧名称不同（忽略大小写），则重命名目录
            if old_name.lower() != new_name.lower():
                if os.path.exists(new_path):
                    # 如果目标目录已存在，使用临时名称
                    temp_name = f"temp_{datetime.now().strftime('%H%M%S')}"
                    temp_path = os.path.join(target_dir, temp_name)
                    
                    # 先将目标目录重命名为临时名称
                    os.rename(new_path, temp_path)
                    logging.info(f"将目标目录重命名为临时名称: {new_path} -> {temp_path}")
                    
                    # 重命名源目录
                    os.rename(old_path, new_path)
                    logging.info(f"重命名目录: {old_path} -> {new_path}")
                    
                    # 将临时目录重命名为源目录名称
                    os.rename(temp_path, old_path)
                    logging.info(f"将临时目录重命名为源目录名称: {temp_path} -> {old_path}")
                else:
                    # 直接重命名
                    os.rename(old_path, new_path)
                    logging.info(f"重命名目录: {old_path} -> {new_path}")
                dir_renamed = True
            else:
                logging.info(f"新旧名称相同（忽略大小写），跳过目录重命名: {old_name}")
                new_path = old_path  # 使用原始路径
            
            # 重命名目录中的文件
            try:
                # 获取目录中的所有文件
                files = [f for f in os.listdir(new_path) if os.path.isfile(os.path.join(new_path, f))]
                
                # 按扩展名分组
                ext_groups = {}
                for file in files:
                    _, ext = os.path.splitext(file)
                    if ext not in ext_groups:
                        ext_groups[ext] = []
                    ext_groups[ext].append(file)
                
                # 重命名文件
                file_renames = []
                for ext, file_list in ext_groups.items():
                    if len(file_list) == 1:  # 如果只有一个文件使用该扩展名
                        old_file = file_list[0]
                        new_file = f"{new_name}{ext}"
                        old_file_path = os.path.join(new_path, old_file)
                        new_file_path = os.path.join(new_path, new_file)
                        
                        if old_file.lower() != new_file.lower():  # 只在文件名不同时重命名
                            os.rename(old_file_path, new_file_path)
                            logging.info(f"重命名文件: {old_file} -> {new_file}")
                            file_renames.append({
                                'old_name': old_file,
                                'new_name': new_file,
                                'directory': new_name
                            })
            except Exception as e:
                logging.error(f"重命名目录 {new_path} 中的文件时出错: {str(e)}")
            
            # 记录重命名操作
            if dir_renamed or file_renames:
                record = {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                if dir_renamed:
                    record.update({
                        'old_dir_name': actual_old_name,
                        'new_dir_name': new_name
                    })
                if file_renames:
                    record['file_renames'] = file_renames
                rename_records.append(record)
                
        except Exception as e:
            logging.error(f"重命名目录失败: {old_path} -> {new_path}, 错误: {str(e)}")
    
    # 保存重命名历史记录
    if rename_records:
        try:
            history_file = 'rename_history.json'
            save_to_json(rename_records, history_file)
            logging.info(f"已保存重命名历史记录到: {history_file}")
        except Exception as e:
            logging.error(f"保存重命名历史记录失败: {str(e)}")
            
    logging.info("目录重命名完成")

def step1_scan_directories(config_file: str, output_file: str = "original_directories.json"):
    """步骤1：扫描目录并保存目录名列表"""
    logging.info("执行步骤1: 扫描目录并保存目录名列表")
    
    # 加载配置
    config = load_config(config_file)
    target_dir = config.get("target_dir")
    
    if not target_dir:
        logging.error("配置文件中缺少必要的参数: target_dir")
        sys.exit(1)
    
    directory_names = get_directory_names(target_dir)
    save_to_json({"directories": directory_names}, output_file)
    logging.info(f"已找到 {len(directory_names)} 个目录并保存到 {output_file}")

def step2_send_to_server(input_file: str, config_file: str):
    """步骤2：分批发送目录名列表到服务器并获取转换后的名称，直接更新name_mapping.json"""
    logging.info("执行步骤2: 分批发送目录名列表到服务器并获取转换后的名称")
    
    # 加载配置
    config = load_config(config_file)
    server_url = config.get("server_url")
    access_token = config.get("access_token")
    
    if not server_url or not access_token:
        logging.error("配置文件中缺少必要的参数: server_url 或 access_token")
        sys.exit(1)
    
    # 加载原始目录名列表
    data = load_from_json(input_file)
    directory_names = data.get("directories", [])
    
    # 删除现有的name_mapping.json
    mapping_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "name_mapping.json")
    if os.path.exists(mapping_file):
        os.remove(mapping_file)
        logging.info("已删除现有的name_mapping.json")
    
    # 分批处理目录名
    batch_size = 10
    total_batches = (len(directory_names) + batch_size - 1) // batch_size
    
    for i in range(0, len(directory_names), batch_size):
        batch = directory_names[i:i + batch_size]
        batch_number = (i // batch_size) + 1
        logging.info(f"处理第 {batch_number}/{total_batches} 批，包含 {len(batch)} 个目录名")
        
        # 发送到服务器并获取转换后的名称
        converted_names = send_to_server(batch, server_url, access_token)
        
        # 创建当前批次的映射
        batch_mapping = dict(zip(batch, converted_names))
        
        # 读取现有的映射（如果存在）
        existing_mapping = {}
        if os.path.exists(mapping_file):
            try:
                with open(mapping_file, 'r', encoding='utf-8') as f:
                    existing_mapping = json.load(f)
            except Exception as e:
                logging.error(f"读取现有映射文件失败: {str(e)}")
        
        # 合并映射
        existing_mapping.update(batch_mapping)
        
        # 保存更新后的映射
        try:
            os.makedirs(os.path.dirname(mapping_file), exist_ok=True)
            with open(mapping_file, 'w', encoding='utf-8') as f:
                json.dump(existing_mapping, f, ensure_ascii=False, indent=2)
            logging.info(f"已更新name_mapping.json，当前包含 {len(existing_mapping)} 个映射")
        except Exception as e:
            logging.error(f"保存映射文件失败: {str(e)}")
    
    logging.info("所有批次处理完成")

def step3_create_mapping(original_file: str, converted_file: str, output_file: str = "name_mapping.json"):
    """步骤3：创建原始名称和转换后名称的映射"""
    logging.info("执行步骤3: 创建名称映射")
    
    # 加载原始名称和转换后的名称
    original_data = load_from_json(original_file)
    converted_data = load_from_json(converted_file)
    
    original_names = original_data.get("directories", [])
    converted_names = converted_data.get("directories", [])
    
    # 创建映射
    mapping = create_mapping(original_names, converted_names)
    
    # 保存映射
    save_to_json(mapping, output_file)
    logging.info(f"已创建并保存名称映射到 {output_file}")

def step4_rename_directories(config_file: str, mapping_file: str):
    """步骤4：根据映射重命名目录"""
    logging.info("执行步骤4: 重命名目录")
    
    # 加载配置
    config = load_config(config_file)
    target_dir = config.get("target_dir")
    
    if not target_dir:
        logging.error("配置文件中缺少必要的参数: target_dir")
        sys.exit(1)
    
    # 加载映射
    mapping = load_from_json(mapping_file)
    
    # 重命名目录
    rename_directories_and_files(config_file)
    logging.info("目录重命名完成")

def revert_rename(config_file):
    """还原重命名操作"""
    # 加载配置
    config = load_config(config_file)
    target_dir = config['target_dir']
    data_dir = config['data_dir']
    
    # 读取重命名历史记录
    history_file = os.path.join(data_dir, 'rename_history.json')
    if not os.path.exists(history_file):
        logging.error(f"重命名历史记录文件不存在: {history_file}")
        return
    
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            rename_records = json.load(f)
    except Exception as e:
        logging.error(f"读取重命名历史记录失败: {str(e)}")
        return
    
    if not rename_records:
        logging.warning("没有找到重命名记录")
        return
    
    logging.info(f"找到 {len(rename_records)} 条重命名记录")
    
    # 按时间戳倒序排列，确保从最新的记录开始还原
    rename_records.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # 还原重命名操作
    for record in rename_records:
        # 还原目录重命名
        if 'old_dir_name' in record and 'new_dir_name' in record:
            old_name = record['old_dir_name']
            new_name = record['new_dir_name']
            old_path = os.path.join(target_dir, old_name)
            new_path = os.path.join(target_dir, new_name)
            
            if not os.path.exists(new_path):
                logging.warning(f"目标目录不存在，跳过还原: {new_path}")
                continue
                
            if os.path.exists(old_path):
                logging.warning(f"源目录已存在，跳过还原: {old_path}")
                continue
                
            try:
                os.rename(new_path, old_path)
                logging.info(f"还原目录: {new_path} -> {old_path}")
            except Exception as e:
                logging.error(f"还原目录失败: {new_path} -> {old_path}, 错误: {str(e)}")
        
        # 还原文件重命名
        if 'file_renames' in record:
            for file_rename in record['file_renames']:
                old_file = file_rename['old_name']
                new_file = file_rename['new_name']
                directory = file_rename['directory']
                
                # 确定目录路径（如果目录已还原，使用old_dir_name）
                if 'old_dir_name' in record and directory == record['new_dir_name']:
                    dir_path = os.path.join(target_dir, record['old_dir_name'])
                else:
                    dir_path = os.path.join(target_dir, directory)
                
                old_file_path = os.path.join(dir_path, old_file)
                new_file_path = os.path.join(dir_path, new_file)
                
                if not os.path.exists(new_file_path):
                    logging.warning(f"目标文件不存在，跳过还原: {new_file_path}")
                    continue
                    
                if os.path.exists(old_file_path):
                    logging.warning(f"源文件已存在，跳过还原: {old_file_path}")
                    continue
                    
                try:
                    os.rename(new_file_path, old_file_path)
                    logging.info(f"还原文件: {new_file} -> {old_file}")
                except Exception as e:
                    logging.error(f"还原文件失败: {new_file_path} -> {old_file_path}, 错误: {str(e)}")
    
    logging.info("目录还原完成")

def print_help():
    """打印帮助信息"""
    print("""重命名工具使用说明：
    
    用法: python main.py <命令> [参数...]
    
    命令:
        step1 <目录路径> [输出文件]  - 扫描目录并保存目录名列表
        step2 <输入文件> <配置文件> [输出文件]  - 发送目录名列表到服务器并获取转换后的名称
        step3 <原始文件> <转换后文件> [输出文件]  - 创建名称映射
        step4 <目录路径> <映射文件>  - 根据映射重命名目录
        all <目录路径>  - 执行所有步骤
        revert <配置文件>  - 根据日志文件回退重命名操作
        help  - 显示此帮助信息
    
    示例:
        python main.py step1 "Z:\\library-1\\Unsorted"
        python main.py step2 "data\\original_directories.json" "config.json"
        python main.py step3 "data\\original_directories.json" "data\\converted_directories.json"
        python main.py step4 "Z:\\library-1\\Unsorted" "data\\name_mapping.json"
        python main.py all "Z:\\library-1\\Unsorted"
        python main.py revert "config.json"
    """)

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)
        
    command = sys.argv[1]
    
    if command == "help":
        print_help()
    elif command == "revert":
        if len(sys.argv) < 3:
            print_help()
            sys.exit(1)
        revert_rename(sys.argv[2])
    elif command == "step1":
        if len(sys.argv) < 3:
            print_help()
            sys.exit(1)
        output_file = sys.argv[3] if len(sys.argv) > 3 else "original_directories.json"
        step1_scan_directories(sys.argv[2], output_file)
        print_json_file(os.path.join("data", output_file))
        if not confirm_continue("请检查生成的目录列表是否正确"):
            sys.exit(0)
    elif command == "step2":
        if len(sys.argv) < 4:
            print_help()
            sys.exit(1)
        input_file = sys.argv[2]
        print_json_file(os.path.join("data", input_file))
        if not confirm_continue("请检查目录列表是否正确"):
            sys.exit(0)
        step2_send_to_server(input_file, sys.argv[3])
        print_json_file(os.path.join("data", "name_mapping.json"))
        if not confirm_continue("请检查名称映射是否正确"):
            sys.exit(0)
    elif command == "step3":
        if len(sys.argv) < 4:
            print_help()
            sys.exit(1)
        original_file = sys.argv[2]
        converted_file = sys.argv[3]
        print_json_file(os.path.join("data", original_file))
        if not confirm_continue("请检查原始目录列表是否正确"):
            sys.exit(0)
        print_json_file(os.path.join("data", converted_file))
        if not confirm_continue("请检查转换后的目录列表是否正确"):
            sys.exit(0)
        output_file = sys.argv[4] if len(sys.argv) > 4 else "name_mapping.json"
        step3_create_mapping(original_file, converted_file, output_file)
        print_json_file(os.path.join("data", output_file))
        if not confirm_continue("请检查名称映射是否正确"):
            sys.exit(0)
    elif command == "step4":
        if len(sys.argv) < 4:
            print_help()
            sys.exit(1)
        mapping_file = sys.argv[3]
        print_json_file(os.path.join("data", mapping_file))
        if not confirm_continue("请检查名称映射是否正确"):
            sys.exit(0)
        step4_rename_directories(sys.argv[2], mapping_file)
    elif command == "all":
        if len(sys.argv) < 3:
            print_help()
            sys.exit(1)
        directory_path = sys.argv[2]
        
        # 步骤1
        step1_scan_directories(directory_path)
        print_json_file(os.path.join("data", "original_directories.json"))
        if not confirm_continue("请检查生成的目录列表是否正确"):
            sys.exit(0)
            
        # 步骤2
        step2_send_to_server("original_directories.json", "config.json")
        print_json_file(os.path.join("data", "name_mapping.json"))
        if not confirm_continue("请检查名称映射是否正确"):
            sys.exit(0)
            
        # 步骤4
        step4_rename_directories(directory_path, "name_mapping.json")
    else:
        print_help()
        sys.exit(1)

if __name__ == "__main__":
    main() 