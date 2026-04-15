"""
立即测试弹窗脚本

直接触发提醒窗口，无需等待定时任务
用于快速测试弹窗是否正常显示
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from core.notifier import show_reminder
from utils.logger import logger


def test_immediate_remind():
    """立即测试提醒弹窗"""
    
    print("=" * 60)
    print("  立即测试提醒弹窗")
    print("=" * 60)
    print()
    
    print("即将显示全屏提醒窗口...")
    print("请测试以下功能：")
    print("  1. 窗口是否全屏显示")
    print("  2. 背景图片是否正常显示")
    print("  3. 文字是否清晰可见")
    print("  4. '我已打卡'按钮是否正常工作")
    print("  5. '稍后提醒'按钮是否正常工作")
    print("  6. ESC键是否可以关闭窗口")
    print()
    print("按 Ctrl+C 可以随时退出")
    print("-" * 60)
    print()
    
    try:
        # 定义回调函数
        def on_confirm():
            print("\n✓ 用户点击了'我已打卡'按钮")
            print("弹窗已关闭")
        
        def on_later():
            print("\n⏱ 用户点击了'稍后提醒'按钮")
            print("（实际项目中会在3分钟后再次提醒）")
            # 返回下次提醒信息（测试用）
            from datetime import datetime, timedelta
            next_time = datetime.now() + timedelta(minutes=3)
            return {
                "next_time": next_time.strftime("%H:%M"),
                "interval": 3
            }
        
        # 显示上班提醒
        print("正在显示上班提醒窗口...")
        show_reminder(
            remind_type="work_start",
            remind_count=1,
            next_remind_time=None,  # 首次提醒没有下次时间
            on_confirm=on_confirm,
            on_later=on_later
        )
        
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n错误：{str(e)}")
        logger.error(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    test_immediate_remind()
