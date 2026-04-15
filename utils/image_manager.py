"""
图片管理器
负责根据时间段选择和管理背景图片
"""

import os
import random
from datetime import datetime
from config import (
    ENABLE_TIME_BASED_IMAGES,
    BACKGROUND_IMAGE,
    TIME_PERIODS,
    IMAGE_FOLDERS
)
from utils.logger import logger


class ImageManager:
    """图片管理器"""
    
    def __init__(self):
        """初始化图片管理器"""
        self.cached_images = {}  # 缓存各时间段的图片列表
        self._scan_images()
        
        logger.info("图片管理器初始化完成")
        if ENABLE_TIME_BASED_IMAGES:
            logger.info("时间段图片切换已启用")
        else:
            logger.info(f"时间段图片切换已禁用，使用固定图片: {BACKGROUND_IMAGE}")
    
    def _scan_images(self):
        """扫描所有图片文件夹，建立缓存"""
        supported_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
        
        for period, folder in IMAGE_FOLDERS.items():
            images = []
            
            if not os.path.exists(folder):
                logger.warning(f"图片文件夹不存在: {folder}")
                self.cached_images[period] = images
                continue
            
            # 扫描文件夹中的所有图片
            for filename in os.listdir(folder):
                ext = os.path.splitext(filename)[1].lower()
                if ext in supported_extensions:
                    filepath = os.path.join(folder, filename)
                    images.append(filepath)
            
            self.cached_images[period] = images
            logger.info(f"[{period}] 扫描到 {len(images)} 张图片 - 文件夹: {folder}")
    
    def get_current_period(self):
        """
        获取当前时间段
        
        Returns:
            str: 时间段名称（"morning"/"daytime"/"evening"/"night"）
        """
        current_hour = datetime.now().hour
        
        for period, time_range in TIME_PERIODS.items():
            start = time_range["start"]
            end = time_range["end"]
            
            # 处理跨天的情况（如夜晚 19:00-次日6:00）
            if start > end:
                if current_hour >= start or current_hour < end:
                    return period
            else:
                if start <= current_hour < end:
                    return period
        
        # 默认返回白天
        logger.warning(f"无法确定时间段（当前小时: {current_hour}），使用默认时间段")
        return "daytime"
    
    def get_background_image(self):
        """
        获取背景图片路径
        
        Returns:
            str: 背景图片路径
        """
        if not ENABLE_TIME_BASED_IMAGES:
            # 禁用时间段切换，使用固定图片
            if os.path.exists(BACKGROUND_IMAGE):
                return BACKGROUND_IMAGE
            else:
                logger.warning(f"固定背景图片不存在: {BACKGROUND_IMAGE}")
                return None
        
        # 启用时间段切换
        current_period = self.get_current_period()
        images = self.cached_images.get(current_period, [])
        
        if not images:
            logger.warning(f"[{current_period}] 时间段没有可用图片，尝试使用固定图片")
            if os.path.exists(BACKGROUND_IMAGE):
                return BACKGROUND_IMAGE
            else:
                logger.error("没有可用的背景图片")
                return None
        
        # 随机选择一张图片
        selected_image = random.choice(images)
        logger.debug(f"[{current_period}] 选择图片: {selected_image}")
        
        return selected_image
    
    def reload_images(self):
        """重新扫描图片文件夹（用于动态添加图片后刷新）"""
        logger.info("重新扫描图片文件夹...")
        self.cached_images.clear()
        self._scan_images()
        logger.info("图片缓存已更新")
    
    def get_period_info(self):
        """
        获取当前时间段的详细信息
        
        Returns:
            dict: 包含时间段名称、图片数量等信息
        """
        current_period = self.get_current_period()
        images = self.cached_images.get(current_period, [])
        
        return {
            "period": current_period,
            "period_name": {
                "morning": "早晨",
                "daytime": "白天",
                "evening": "傍晚",
                "night": "夜晚"
            }.get(current_period, "未知"),
            "image_count": len(images),
            "current_hour": datetime.now().hour
        }


# 创建全局图片管理器实例
image_manager = ImageManager()


def get_background_image_path():
    """
    便捷函数：获取背景图片路径
    
    Returns:
        str: 背景图片路径，如果不存在返回None
    """
    return image_manager.get_background_image()


if __name__ == "__main__":
    # 测试代码
    print("测试图片管理器:")
    print("=" * 60)
    
    # 显示当前时间段信息
    info = image_manager.get_period_info()
    print(f"\n当前时间: {datetime.now().strftime('%H:%M:%S')}")
    print(f"当前时间段: {info['period_name']} ({info['period']})")
    print(f"该时间段图片数量: {info['image_count']}")
    
    print("\n各时间段图片统计:")
    for period, folder in IMAGE_FOLDERS.items():
        images = image_manager.cached_images.get(period, [])
        print(f"  {period:10s}: {len(images):3d} 张图片 - {folder}")
    
    print("\n连续获取5次背景图片（测试随机性）:")
    for i in range(5):
        img_path = get_background_image_path()
        if img_path:
            print(f"{i+1}. {os.path.basename(img_path)}")
        else:
            print(f"{i+1}. [无可用图片]")
