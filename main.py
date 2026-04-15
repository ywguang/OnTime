"""
打卡提醒助手 - 主入口程序

功能：
1. 在固定时间显示全屏弹窗提醒打卡
2. 支持多次提醒和稍后提醒
3. 自动跳过周末和法定节假日
4. 记录提醒日志
5. 支持配置界面和托盘图标

使用方法：
1. 首次运行前，请修改 config.py 中的配置参数
2. 准备背景图片放在 images/ 目录下（可选）
3. 运行本程序：python main.py
4. 右键托盘图标打开配置界面
"""

import sys
import os
from utils.logger import log_startup, log_error
from core.scheduler import start_scheduler_in_background


def check_dependencies():
    """检查依赖包是否已安装"""
    missing_packages = []
    
    try:
        import PIL
    except ImportError:
        missing_packages.append("Pillow")
    
    try:
        import schedule
    except ImportError:
        missing_packages.append("schedule")
    
    if missing_packages:
        print("错误：缺少必要的依赖包")
        print(f"缺少的包: {', '.join(missing_packages)}")
        print("\n请运行以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True


def check_background_image():
    """检查背景图片是否存在"""
    from config import BACKGROUND_IMAGE
    
    if not os.path.exists(BACKGROUND_IMAGE):
        print(f"警告：背景图片不存在: {BACKGROUND_IMAGE}")
        print("程序将使用默认背景色")
        print("您可以将自定义图片放在 images/ 目录下")
        return False
    
    return True


def print_banner():
    """打印启动横幅"""
    from config import APP_NAME, VERSION
    
    print("=" * 60)
    print(f"  {APP_NAME} v{VERSION}")
    print("=" * 60)
    print()


def load_user_config():
    """加载用户配置（覆盖默认配置）"""
    import json
    
    # 获取配置文件路径
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    config_file = os.path.join(base_dir, 'user_config.json')
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
            
            # 动态修改 config 模块的值
            import config
            for key, value in user_config.items():
                if hasattr(config, key):
                    setattr(config, key, value)
                    print(f"  已加载用户配置: {key} = {value}")
            
            return True
        except Exception as e:
            print(f"  加载用户配置失败: {e}")
    
    return False


def show_config_window():
    """显示配置界面"""
    try:
        from ui.config_ui import ConfigWindow
        config_window = ConfigWindow()
        config_window.show()
    except Exception as e:
        print(f"打开配置界面失败: {e}")


def cleanup_resources(tray=None, scheduler_thread=None):
    """
    清理程序资源
    
    Args:
        tray: 托盘图标管理器
        scheduler_thread: 调度器线程
    """
    print("\n正在清理资源...")
    
    # 停止托盘图标
    if tray:
        try:
            tray.stop()
            print("  ✓ 托盘图标已停止")
        except Exception as e:
            print(f"  ✗ 停止托盘图标失败: {e}")
    
    # 记录退出日志
    try:
        log_error("程序退出")
    except:
        pass
    
    print("  ✓ 资源清理完成")


def main():
    """主函数"""
    # 初始化变量
    tray = None
    scheduler_thread = None
    
    try:
        # 打印横幅
        print_banner()
        
        # 检查依赖
        print("正在检查依赖...")
        if not check_dependencies():
            sys.exit(1)
        print("✓ 依赖检查通过\n")
        
        # 检查背景图片
        print("正在检查背景图片...")
        check_background_image()
        print()
        
        # 加载用户配置
        print("正在加载用户配置...")
        load_user_config()
        print()
        
        # 记录启动日志
        log_startup()
        
        # 显示配置信息
        from config import (
            WORK_START_TIME, WORK_END_TIME, REMIND_ADVANCE_MINUTES,
            REMIND_INTERVAL_MINUTES, MAX_REMIND_COUNT
        )
        
        print("当前配置:")
        print(f"  上班时间: {WORK_START_TIME}")
        print(f"  下班时间: {WORK_END_TIME}")
        print(f"  提前提醒: {REMIND_ADVANCE_MINUTES} 分钟")
        print(f"  提醒间隔: {REMIND_INTERVAL_MINUTES} 分钟")
        print(f"  最大提醒次数: {MAX_REMIND_COUNT}")
        print()
        
        # 启动调度器
        print("正在启动定时任务调度器...")
        scheduler_thread = start_scheduler_in_background()
        print("✓ 调度器启动成功\n")
        
        # 启动托盘图标
        print("正在启动托盘图标...")
        try:
            from ui.tray_icon import create_tray_icon
            
            # 定义退出函数，确保正确清理资源
            def exit_app():
                print("\n接收到退出指令...")
                cleanup_resources(tray, scheduler_thread)
                # 使用 os._exit 强制退出，避免线程阻塞
                os._exit(0)
            
            tray = create_tray_icon(
                on_show_config=show_config_window,
                on_exit=exit_app
            )
            if tray:
                print("✓ 托盘图标启动成功")
                print("  提示：右键托盘图标可打开配置界面")
            else:
                print("  警告：托盘图标启动失败，程序将继续运行")
        except Exception as e:
            print(f"  警告：托盘图标启动失败: {e}")
        
        print()
        print("程序正在运行中...")
        print("按 Ctrl+C 退出程序")
        print("-" * 60)
        
        # 保持主线程运行
        while True:
            import time
            time.sleep(1)
            
            # 检查并执行测试弹窗请求（在主线程中）
            if tray and hasattr(tray, 'check_and_execute_test'):
                tray.check_and_execute_test()
                
    except KeyboardInterrupt:
        print("\n\n程序被用户中断 (Ctrl+C)")
        cleanup_resources(tray, scheduler_thread)
        sys.exit(0)
    except SystemExit:
        # 正常的系统退出（如托盘菜单点击退出）
        cleanup_resources(tray, scheduler_thread)
        raise
    except Exception as e:
        print(f"\n错误：程序运行异常 - {str(e)}")
        log_error(f"程序运行异常: {str(e)}")
        cleanup_resources(tray, scheduler_thread)
        sys.exit(1)


if __name__ == "__main__":
    main()
