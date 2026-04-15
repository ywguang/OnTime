"""
配置模块
自动加载默认配置和用户配置
"""

import os
import sys
import json

# 获取项目根目录
if getattr(sys, 'frozen', False):
    # PyInstaller 打包后的环境
    exe_dir = os.path.dirname(sys.executable)
    # 检查是否存在 _internal 目录（PyInstaller 目录模式）
    internal_dir = os.path.join(exe_dir, '_internal')
    if os.path.exists(internal_dir):
        PROJECT_ROOT = internal_dir
    else:
        PROJECT_ROOT = exe_dir
else:
    # 开发环境
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 从默认配置导入所有配置项
from .default_config import *

# 加载用户配置覆盖默认值
# 注意：打包后配置文件保存在 exe 同目录，方便用户修改
if getattr(sys, 'frozen', False):
    # 打包环境：配置文件放在 exe 同目录
    _USER_CONFIG_FILE = os.path.join(os.path.dirname(sys.executable), 'user_config.json')
else:
    # 开发环境：配置文件放在 config 目录
    _USER_CONFIG_FILE = os.path.join(PROJECT_ROOT, 'config', 'user_config.json')

if os.path.exists(_USER_CONFIG_FILE):
    try:
        with open(_USER_CONFIG_FILE, 'r', encoding='utf-8') as f:
            _user_config = json.load(f)
        
        # 动态更新配置
        for key, value in _user_config.items():
            if key in globals():
                globals()[key] = value
                
    except Exception as e:
        print(f"加载用户配置失败: {e}")