"""
生成示例背景图片
运行此脚本会创建一个简单的渐变背景图片
"""

from PIL import Image, ImageDraw

def create_sample_background():
    """创建示例背景图片"""
    # 设置图片尺寸（1920x1080）
    width, height = 1920, 1080
    
    # 创建图片
    image = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(image)
    
    # 绘制渐变色背景（橙色到红色渐变）
    for y in range(height):
        # 计算渐变颜色
        r = int(255 - (y / height) * 50)  # 从255到205
        g = int(107 - (y / height) * 50)  # 从107到57
        b = int(53 - (y / height) * 30)   # 从53到23
        
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # 添加文字
    try:
        from PIL import ImageFont
        # 尝试使用系统字体
        font_large = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 80)
        font_small = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 40)
    except:
        # 如果找不到字体，使用默认字体
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # 绘制文字
    text1 = "打卡提醒助手"
    text2 = "请替换为您的自定义背景图片"
    
    # 计算文字位置（居中）
    bbox1 = draw.textbbox((0, 0), text1, font=font_large)
    text1_width = bbox1[2] - bbox1[0]
    text1_x = (width - text1_width) // 2
    text1_y = height // 3
    
    bbox2 = draw.textbbox((0, 0), text2, font=font_small)
    text2_width = bbox2[2] - bbox2[0]
    text2_x = (width - text2_width) // 2
    text2_y = height // 2
    
    # 绘制文字（白色，带阴影效果）
    shadow_offset = 3
    draw.text((text1_x + shadow_offset, text1_y + shadow_offset), text1, fill=(0, 0, 0), font=font_large)
    draw.text((text1_x, text1_y), text1, fill=(255, 255, 255), font=font_large)
    
    draw.text((text2_x + shadow_offset, text2_y + shadow_offset), text2, fill=(0, 0, 0), font=font_small)
    draw.text((text2_x, text2_y), text2, fill=(255, 255, 255), font=font_small)
    
    # 保存图片
    output_path = "images/background.jpg"
    image.save(output_path, 'JPEG', quality=95)
    print(f"示例背景图片已生成: {output_path}")
    print(f"图片尺寸: {width}x{height}")


if __name__ == "__main__":
    create_sample_background()
