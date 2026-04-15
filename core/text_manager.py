"""
文案管理器
负责管理和随机选择提醒文案
"""

import random
from config import (
    ENABLE_RANDOM_MESSAGES,
    WORK_START_MESSAGES,
    WORK_END_MESSAGES,
    MESSAGE_TEXT_WORK,
    MESSAGE_TEXT_OFF
)
from utils.logger import logger


class TextManager:
    """文案管理器"""
    
    def __init__(self):
        """初始化文案管理器"""
        self.used_messages = {
            "work_start": [],  # 记录已使用的上班文案
            "work_end": []     # 记录已使用的下班文案
        }
        self.max_history = 10  # 最多记录最近10条，避免短期重复
        
        logger.info("文案管理器初始化完成")
        if ENABLE_RANDOM_MESSAGES:
            logger.info(f"随机文案已启用 - 上班文案{len(WORK_START_MESSAGES)}条，下班文案{len(WORK_END_MESSAGES)}条")
        else:
            logger.info("随机文案已禁用，使用固定文案")
    
    def get_message(self, remind_type="work_start"):
        """
        获取一条提醒文案
        
        Args:
            remind_type (str): 提醒类型（"work_start" 或 "work_end"）
            
        Returns:
            str: 提醒文案
        """
        if not ENABLE_RANDOM_MESSAGES:
            # 禁用随机文案，使用固定文案
            if remind_type == "work_start":
                return MESSAGE_TEXT_WORK
            else:
                return MESSAGE_TEXT_OFF
        
        # 启用随机文案
        if remind_type == "work_start":
            messages = WORK_START_MESSAGES
        else:
            messages = WORK_END_MESSAGES
        
        if not messages:
            logger.warning(f"文案库为空，使用默认文案")
            return "该打卡了！"
        
        # 过滤掉最近使用过的文案
        available_messages = [
            msg for msg in messages 
            if msg not in self.used_messages[remind_type]
        ]
        
        # 如果所有文案都用过了，清空历史记录
        if not available_messages:
            logger.info(f"[{remind_type}] 所有文案已轮询一遍，重置历史记录")
            self.used_messages[remind_type] = []
            available_messages = messages
        
        # 随机选择一条
        selected_message = random.choice(available_messages)
        
        # 记录已使用
        self.used_messages[remind_type].append(selected_message)
        if len(self.used_messages[remind_type]) > self.max_history:
            self.used_messages[remind_type].pop(0)  # 移除最早的记录
        
        logger.debug(f"[{remind_type}] 选择文案: {selected_message}")
        return selected_message
    
    def reset_history(self, remind_type=None):
        """
        重置文案使用历史
        
        Args:
            remind_type (str): 提醒类型，如果为None则重置所有
        """
        if remind_type:
            self.used_messages[remind_type] = []
            logger.info(f"[{remind_type}] 文案历史已重置")
        else:
            self.used_messages = {
                "work_start": [],
                "work_end": []
            }
            logger.info("所有文案历史已重置")


# 创建全局文案管理器实例
text_manager = TextManager()


def get_remind_message(remind_type="work_start"):
    """
    便捷函数：获取提醒文案
    
    Args:
        remind_type (str): 提醒类型（"work_start" 或 "work_end"）
        
    Returns:
        str: 提醒文案
    """
    return text_manager.get_message(remind_type)


if __name__ == "__main__":
    # 测试代码
    print("测试文案管理器:")
    print("=" * 60)
    
    print("\n上班打卡文案（连续获取15次）:")
    for i in range(15):
        msg = get_remind_message("work_start")
        print(f"{i+1:2d}. {msg}")
    
    print("\n" + "=" * 60)
    print("\n下班打卡文案（连续获取15次）:")
    for i in range(15):
        msg = get_remind_message("work_end")
        print(f"{i+1:2d}. {msg}")
