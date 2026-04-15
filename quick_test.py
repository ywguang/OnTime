"""
快速测试脚本 - 用于测试提醒功能

使用方法：
1. 运行此脚本，它会自动将下次提醒时间设置为1分钟后
2. 观察是否弹出全屏提醒窗口
3. 测试"我已打卡"和"稍后提醒"按钮
4. 测试完成后，记得恢复 config.py 中的正常时间配置
"""

import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(__file__))

import config


def quick_test():
    """快速测试提醒功能"""
    
    print("=" * 60)
    print("  打卡提醒助手 - 快速测试")
    print("=" * 60)
    print()
    
    # 获取当前时间
    now = datetime.now()
    test_time = now + timedelta(minutes=1)
    test_time_str = test_time.strftime("%H:%M")
    
    print(f"当前时间: {now.strftime('%H:%M:%S')}")
    print(f"测试时间: {test_time_str} (1分钟后)")
    print()
    
    # 临时修改配置
    original_start = config.WORK_START_TIME
    original_end = config.WORK_END_TIME
    
    print("⚠️  注意：这将临时修改 config.py 中的时间配置")
    print(f"   原上班时间: {original_start}")
    print(f"   原下班时间: {original_end}")
    print()
    
    confirm = input("是否继续？(y/n): ")
    if confirm.lower() != 'y':
        print("已取消测试")
        return
    
    # 修改配置文件
    config_path = os.path.join(os.path.dirname(__file__), "config.py")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 备份原始内容
        backup_path = config_path + ".backup"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ 已创建备份文件: {backup_path}")
        
        # 替换时间配置
        content = content.replace(
            f'WORK_START_TIME = "{original_start}"',
            f'WORK_START_TIME = "{test_time_str}"'
        )
        content = content.replace(
            f'WORK_END_TIME = "{original_end}"',
            f'WORK_END_TIME = "{test_time_str}"'
        )
        
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ 已将测试时间设置为: {test_time_str}")
        print()
        print("=" * 60)
        print("现在请运行以下命令开始测试:")
        print("  python main.py")
        print()
        print(f"等待到 {test_time_str}，应该会弹出提醒窗口")
        print("=" * 60)
        print()
        print("测试完成后，请运行以下命令恢复配置:")
        print("  python restore_config.py")
        print()
        
    except Exception as e:
        print(f"错误：修改配置文件失败 - {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    quick_test()
