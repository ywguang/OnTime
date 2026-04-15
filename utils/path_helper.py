"""
路径助手模块
提供统一的路径获取方法，兼容开发环境和打包环境
"""

import os
import sys


def get_project_root():
    """
    获取项目根目录
    
    优先级：
    1. 如果是打包后的 exe，检查 _internal 目录
    2. 如果是开发环境，返回 main.py 所在目录
    3. 兜底方案：返回当前工作目录
    
    Returns:
        str: 项目根目录的绝对路径
    """
    # 方式1：打包后的 exe 环境
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        # 检查是否存在 _internal 目录（PyInstaller 目录模式）
        internal_dir = os.path.join(exe_dir, '_internal')
        if os.path.exists(internal_dir):
            return internal_dir
        return exe_dir
    
    # 方式2：尝试从 sys.path 找到项目根目录
    # sys.path[0] 通常是脚本启动时的目录
    if sys.path and len(sys.path) > 0:
        # 尝试找到包含 main.py 的目录
        for path in sys.path:
            if os.path.isfile(os.path.join(path, 'main.py')):
                return path
    
    # 方式3：从当前文件向上查找
    current_file = os.path.abspath(__file__)
    # utils/path_helper.py -> 项目根目录
    project_root = os.path.dirname(os.path.dirname(current_file))
    if os.path.isfile(os.path.join(project_root, 'main.py')):
        return project_root
    
    # 方式4：兜底，使用当前工作目录
    return os.getcwd()


def get_config_dir():
    """获取配置目录"""
    return os.path.join(get_project_root(), 'config')


def get_user_config_file():
    """获取用户配置文件路径"""
    # 打包环境：配置文件放在 exe 同目录，方便用户修改
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), 'user_config.json')
    # 开发环境：配置文件放在 config 目录
    return os.path.join(get_config_dir(), 'user_config.json')


def get_assets_dir():
    """获取资源目录"""
    return os.path.join(get_project_root(), 'assets')


def get_images_dir():
    """获取图片目录"""
    return os.path.join(get_assets_dir(), 'images')


def get_logs_dir():
    """获取日志目录"""
    return os.path.join(get_assets_dir(), 'logs')


def get_log_file():
    """获取日志文件路径"""
    return os.path.join(get_logs_dir(), 'remind.log')


def get_main_script():
    """
    获取主脚本路径
    
    Returns:
        str: main.py 的完整路径
    """
    return os.path.join(get_project_root(), 'main.py')


# 测试代码
if __name__ == '__main__':
    print("路径测试:")
    print(f"项目根目录: {get_project_root()}")
    print(f"配置目录: {get_config_dir()}")
    print(f"用户配置文件: {get_user_config_file()}")
    print(f"资源目录: {get_assets_dir()}")
    print(f"图片目录: {get_images_dir()}")
    print(f"日志目录: {get_logs_dir()}")
    print(f"日志文件: {get_log_file()}")
    print(f"主脚本: {get_main_script()}")
