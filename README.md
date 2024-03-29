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

### 2. Tampermonkey 脚本

此脚本会在浏览磁力链接的网页时，在链接旁边添加一个图标，点击该图标可以将磁力链接发送到`lx115`服务器，从而添加到115网盘的离线任务中。

#### 安装

1. 确保你的浏览器安装了Tampermonkey扩展。
2. 打开`115helper/tampermonkey`目录，找到脚本文件。
3. 在Tampermonkey扩展中，创建一个新脚本并复制该文件内容进去。
4. 保存并启用脚本。

### 3. Cookies-Extensions Chrome插件

`cookies-extensions`是一个Chrome插件，用于在登录115网盘后，一键提取Cookies并发送给`lx115`服务器，以便进行身份验证。

#### 安装与使用

1. 进入`115helper/cookies-extensions`目录。
2. 将整个文件夹拖拽到Chrome的扩展页面(`chrome://extensions/`)，开启"开发者模式"，点击"加载已解压的扩展程序"。
3. 登录115网盘，点击扩展图标发送Cookies到`lx115`服务器。

### 4. Explosion-Extensions Chrome扩展

`explosion-extensions`是一个Chrome扩展程序，用于一键打开当前页面上符合格式的链接，比如论坛的所有帖子。

## 使用说明

确保所有组件均已安装并运行。浏览含有磁力链接的网页时，点击Tampermonkey脚本添加的图标，即可将磁力链接添加到115网盘的离线下载任务中。

## 贡献

欢迎任何形式的贡献，包括但不限于新功能、bug修复或文档改善。请提交Pull Request或Issue。

## 许可证

本项目采用MIT许可证。详细信息请查看LICENSE文件。
