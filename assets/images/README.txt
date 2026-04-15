# 背景图片说明

## 如何添加自定义背景图片

1. **准备图片**
   - 格式支持：JPG、PNG、BMP等常见格式
   - 建议分辨率：与你的屏幕分辨率匹配（如 1920x1080）
   - 建议选择国漫风格的精美画面

2. **放置图片**
   - 将图片重命名为 `background.jpg`
   - 或者修改 `config.py` 中的 `BACKGROUND_IMAGE` 配置项指向你的图片路径

3. **示例路径配置**
   ```python
   # 使用默认名称
   BACKGROUND_IMAGE = "images/background.jpg"
   
   # 或使用自定义名称
   BACKGROUND_IMAGE = "images/my_anime_bg.png"
   
   # 或使用绝对路径
   BACKGROUND_IMAGE = "D:/Pictures/anime_background.jpg"
   ```

## 推荐图片来源

- 国漫官方壁纸
- 动漫网站高清壁纸
- 自己设计的图片

## 注意事项

- 如果图片不存在，程序会自动使用橙色背景（#FF6B35）
- 图片过大会自动缩放到屏幕尺寸
- 建议使用清晰的图片以获得最佳视觉效果
