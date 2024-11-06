#!/bin/bash

# 更新包管理器
sudo apt-get update

# 安装必要的依赖库
pip install psutil aiohttp qqbot pyyaml regex logging multiprocessing

echo "所有库已成功安装！"
