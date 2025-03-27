# 115helper

## 项目简介

`115helper` 是一个增强型工具集，旨在提升115网盘用户的体验。它包括三个主要部分：一个用于添加115网盘离线任务的HTTP服务器 (`lx115`)，一个用于识别网页上的磁力链接并使其可以一键添加到115网盘的Tampermonkey脚本，以及一个Chrome扩展程序，用于获取115网盘登录后的Cookies信息，以便`lx115`服务器能够进行身份验证并添加离线任务。

## 组件介绍

### 1. lx115 HTTP服务器

`lx115` 是一个HTTP服务器，用于将磁力链接添加为115网盘的离线下载任务。

#### 安装与运行

```bash
# 克隆仓库
git clone

# 编译运行main.go
```

### 2. 自动重命名工具

`rename` 是一个智能的批量重命名工具，专门用于处理视频文件的命名规范化。它能够自动扫描目录，通过AI服务将各种格式的文件名转换为标准格式，并保持文件结构不变。

#### 主要特性

- 支持多种命名格式的智能识别和转换
- 自动处理目录和文件的命名
- 支持批量操作
- 提供重命名历史记录
- 支持还原操作
- 分步骤执行，每步都可确认

#### 安装与运行

```bash
# 进入rename目录
cd rename

# 安装依赖
pip install -r requirements.txt

# Windows运行
run_rename.bat all    # 执行所有步骤
run_rename.bat step1  # 仅执行步骤1：扫描目录
run_rename.bat step2  # 仅执行步骤2：发送到服务器
run_rename.bat step3  # 仅执行步骤3：创建映射
run_rename.bat step4  # 仅执行步骤4：重命名
revert.bat           # 还原重命名操作

# Linux/Mac运行
./run_rename.sh all    # 执行所有步骤
./run_rename.sh step1  # 仅执行步骤1：扫描目录
./run_rename.sh step2  # 仅执行步骤2：发送到服务器
./run_rename.sh step3  # 仅执行步骤3：创建映射
./run_rename.sh step4  # 仅执行步骤4：重命名
./revert.sh           # 还原重命名操作
```

#### 使用说明

1. 准备配置文件：
   - 在`rename`目录下创建`config.json`文件
   - 配置目标目录路径和其他必要参数

2. 执行重命名：
   - 运行`run_rename.bat all`（Windows）或`./run_rename.sh all`（Linux/Mac）
   - 脚本会自动执行以下步骤：
     1. 扫描目录并生成目录列表
     2. 发送目录名到AI服务获取标准名称
     3. 创建重命名映射
     4. 执行重命名操作
   - 每个步骤执行前都会显示相关信息并等待确认

3. 还原操作：
   - 如果需要还原重命名，运行`revert.bat`（Windows）或`./revert.sh`（Linux/Mac）
   - 脚本会根据历史记录还原所有文件到原始名称

4. 注意事项：
   - 执行重命名前会自动检查并清理旧的JSON文件
   - 每个步骤都可以单独执行，方便调试和验证
   - 所有操作都有详细的日志记录
   - 重命名历史保存在`data/rename_history.json`中

### 3. Tampermonkey 脚本

此脚本会在浏览磁力链接的网页时，在链接旁边添加一个图标，点击该图标可以将磁力链接发送到`lx115`服务器，从而添加到115网盘的离线任务中。

#### 安装

1. 确保你的浏览器安装了Tampermonkey扩展。
2. 打开`115helper/tampermonkey`目录，找到脚本文件。
3. 在Tampermonkey扩展中，创建一个新脚本并复制该文件内容进去。
4. 保存并启用脚本。

### 4. Cookies-Extensions Chrome插件

`cookies-extensions`是一个Chrome插件，用于在登录115网盘后，一键提取Cookies并发送给`lx115`服务器，以便进行身份验证。

#### 安装与使用

1. 进入`115helper/cookies-extensions`目录。
2. 将整个文件夹拖拽到Chrome的扩展页面(`chrome://extensions/`)，开启"开发者模式"，点击"加载已解压的扩展程序"。
3. 登录115网盘，点击扩展图标发送Cookies到`lx115`服务器。

### 5. Explosion-Extensions Chrome扩展

`explosion-extensions`是一个Chrome扩展程序，用于一键打开当前页面上符合格式的链接，比如论坛的所有帖子。

## 使用说明

确保所有组件均已安装并运行。浏览含有磁力链接的网页时，点击Tampermonkey脚本添加的图标，即可将磁力链接添加到115网盘的离线下载任务中。

## 贡献

欢迎任何形式的贡献，包括但不限于新功能、bug修复或文档改善。请提交Pull Request或Issue。

## 许可证

本项目采用MIT许可证。详细信息请查看LICENSE文件。