"""
恢复配置文件脚本

用于将 config.py 恢复到测试前的状态
"""

import sys
import os
import shutil

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(__file__))


def restore_config():
    """恢复配置文件"""
    
    print("=" * 60)
    print("  恢复配置文件")
    print("=" * 60)
    print()
    
    config_path = os.path.join(os.path.dirname(__file__), "config.py")
    backup_path = config_path + ".backup"
    
    # 检查备份文件是否存在
    if not os.path.exists(backup_path):
        print("错误：找不到备份文件")
        print(f"期望的备份文件: {backup_path}")
        print()
        print("如果没有备份文件，请手动修改 config.py 中的时间配置")
        return
    
    try:
        # 恢复备份
        shutil.copy2(backup_path, config_path)
        print(f"✓ 已从备份文件恢复配置")
        print(f"  备份文件: {backup_path}")
        print()
        
        # 删除备份文件
        os.remove(backup_path)
        print(f"✓ 已删除备份文件")
        print()
        print("=" * 60)
        print("配置已恢复完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"错误：恢复配置失败 - {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    restore_config()
