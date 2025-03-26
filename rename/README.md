# 目录重命名工具

这是一个用于批量重命名目录的工具，具有以下功能：

1. 读取指定目录下的所有文件夹名称（不包含子目录）
2. 将目录名称列表保存为 JSON 格式
3. 通过 HTTP 请求将目录名称发送到服务器进行转换
4. 生成转换前后的名称对应关系
5. 根据对应关系重命名目录和文件

## 服务器API格式

本工具使用的服务器API格式如下：

### 请求
```json
{
  "inputs": {
    "filename": "目录名1\n目录名2\n目录名3"
  },
  "response_mode": "blocking",
  "user": "rename-tool"
}
```

### 响应
```json
{
  "task_id": "364b26ee-05f3-4018-935a-fa8861d84357",
  "workflow_run_id": "1657e61e-eaee-4df3-afcc-4b7bb2a10987",
  "data": {
    "id": "1657e61e-eaee-4df3-afcc-4b7bb2a10987",
    "workflow_id": "1661970e-ab46-46bb-acd5-9c60de0ea5b3",
    "status": "succeeded",
    "outputs": {
      "text": "转换后名称1\n转换后名称2\n转换后名称3"
    },
    "error": null,
    "elapsed_time": 3.854253939993214,
    "total_tokens": 102,
    "total_steps": 3,
    "created_at": 1742988881,
    "finished_at": 1742988884
  }
}
```

## 使用方法

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行程序：

### 完整流程
```bash
python main.py all <目标目录路径> <服务器URL>
```

### 分步执行
1. 扫描目录并保存目录名列表到 JSON：
```bash
python main.py step1 <目标目录路径> [输出文件名]
```

2. 加载 JSON 文件，发送目录名列表到服务器并保存结果：
```bash
python main.py step2 <输入文件名> <服务器URL> [输出文件名]
```

3. 加载两个 JSON 文件，生成转换前后目录名的对应关系：
```bash
python main.py step3 <原始目录名文件> <转换后目录名文件> [输出文件名]
```

4. 加载对应关系的 JSON 文件，重命名目录和目录内的文件：
```bash
python main.py step4 <目标目录路径> <映射关系文件>
```

5. 查看帮助信息：
```bash
python main.py help
```

注意：方括号 [] 中的参数是可选的。

## 注意事项

- 程序只会重命名目录下的文件，如果目录下有多个文件，将跳过文件重命名
- 文件扩展名将保持不变
- 所有操作都会记录到日志文件中 (rename.log)
- 如果目录不存在或目标名称已存在，将跳过该目录的重命名操作
- 服务器URL应该包含协议前缀（http:// 或 https://） 