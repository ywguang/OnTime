"""
全屏弹窗通知模块
使用tkinter创建全屏置顶窗口，支持背景图片和自定义文字
"""

import tkinter as tk
from tkinter import font
from PIL import Image, ImageTk, ImageFilter, ImageDraw, ImageFont
import os
from config import (
    TITLE_TEXT,
    BUTTON_CONFIRM_TEXT, BUTTON_LATER_TEXT, WINDOW_ALPHA, REMIND_INTERVAL_MINUTES
)
from core.text_manager import get_remind_message
from utils.image_manager import get_background_image_path
from utils.logger import logger


class RemindWindow:
    """打卡提醒全屏窗口"""
    
    # 类变量，保持所有活动窗口的引用，防止被垃圾回收
    _active_windows = []
    
    def __init__(self, remind_type="work_start", remind_count=1, next_remind_time=None, on_confirm=None, on_later=None):
        """
        初始化提醒窗口
        
        Args:
            remind_type (str): 提醒类型（"work_start" 或 "work_end"）
            remind_count (int): 当前提醒次数
            next_remind_time (str): 下次提醒时间（格式：HH:MM）
            on_confirm (callable): 确认按钮回调函数
            on_later (callable): 稍后按钮回调函数
        """
        self.remind_type = remind_type
        self.remind_count = remind_count
        self.next_remind_time = next_remind_time
        self.on_confirm = on_confirm
        self.on_later = on_later
        self.root = None
        self.bg_photo = None  # 保持引用防止被垃圾回收
        self.final_photo = None  # 保持引用防止被垃圾回收
        self.bg_image = None  # 保持引用防止被垃圾回收
        self.full_label = None  # 保持引用防止被垃圾回收
        self.is_toplevel = False  # 标记是否使用 Toplevel
        
        # 使用文案管理器获取随机文案
        self.message_text = get_remind_message(remind_type)
        
    def show(self):
        """显示提醒窗口"""
        try:
            # 将当前窗口添加到活动窗口列表，防止被垃圾回收
            RemindWindow._active_windows.append(self)
            
            self._create_window()
            self._setup_background()
            # 注意：_setup_background 内部会调用 _create_glass_effect 或 _create_simple_card
            # 不需要再单独调用 _create_widgets
            
            # 关键修复：只有当使用 Tk() 时才调用 mainloop()
            # Toplevel 共享父窗口的 mainloop，不需要自己调用
            if not self.is_toplevel:
                self.root.mainloop()
        except Exception as e:
            logger.error(f"显示提醒窗口失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            # 如果窗口创建失败，仍然调用回调函数
            if self.on_confirm:
                self.on_confirm()
    
    def _create_window(self):
        """创建基础窗口"""
        # 关键修复：检测是否已有 Tk 实例，避免创建多个 Tk()
        # 多个 Tk() 实例会导致 PhotoImage 在不同 Tcl 解释器间无法共享
        try:
            existing_root = tk._default_root
            if existing_root and existing_root.winfo_exists():
                # 已有根窗口，使用 Toplevel
                self.root = tk.Toplevel(existing_root)
                self.is_toplevel = True
                logger.info("Using Toplevel (existing root detected)")
            else:
                # 没有现有根窗口，创建新的 Tk 实例
                self.root = tk.Tk()
                self.is_toplevel = False
                logger.info("Creating new Tk instance")
        except Exception as e:
            logger.warning(f"Failed to check existing root: {e}, creating new Tk")
            self.root = tk.Tk()
            self.is_toplevel = False
        
        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 设置全屏
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)  # 置顶
        self.root.overrideredirect(True)  # 去除标题栏和边框
        
        # 设置透明度
        self.root.attributes('-alpha', WINDOW_ALPHA)
        
        # 设置窗口大小
        self.root.geometry(f"{screen_width}x{screen_height}")
        
        # 绑定ESC键关闭窗口（作为备用退出方式）
        self.root.bind('<Escape>', lambda e: self._on_confirm())
        
    def _setup_background(self):
        """设置背景图片和毛玻璃效果"""
        try:
            # 使用图片管理器获取背景图片
            image_path = get_background_image_path()
            
            if image_path and os.path.exists(image_path):
                # 打开图片并缩放到屏幕尺寸
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
                
                self.bg_image = Image.open(image_path)
                self.bg_image = self.bg_image.resize((screen_width, screen_height), Image.LANCZOS)
                
                # 创建毛玻璃效果（内部会创建 full_label 显示背景）
                self._create_glass_effect()
                
                logger.info(f"背景图片加载成功: {image_path}")
            else:
                # 如果没有可用图片，使用默认背景色
                logger.warning("没有可用的背景图片，使用默认背景色")
                self.root.configure(bg='#FF6B35')
                self._create_simple_card()
                
        except Exception as e:
            logger.error(f"加载背景图片失败: {str(e)}，使用默认背景色")
            self.root.configure(bg='#FF6B35')
            self._create_simple_card()
    
    def _create_glass_effect(self):
        """创建圆角毛玻璃效果的卡片，并直接在上面绘制文字"""
        try:
            # 卡片尺寸和位置
            card_width = 550
            card_height = 400
            corner_radius = 20  # 圆角半径
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            # 计算卡片位置（居中）
            card_x = (screen_width - card_width) // 2
            card_y = (screen_height - card_height) // 2
            
            # 关键修复：使用RGBA模式创建最终图片，支持透明遮罩
            final_image = self.bg_image.copy().convert('RGBA')
            
            # 从背景中截取卡片区域并应用高斯模糊
            card_region = self.bg_image.crop((card_x, card_y, card_x + card_width, card_y + card_height))
            blurred_region = card_region.filter(ImageFilter.GaussianBlur(radius=15))
            
            # 创建圆角遮罩（用于确定哪些像素属于圆角卡片内部）
            mask = Image.new('L', (card_width, card_height), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.rounded_rectangle(
                [(0, 0), (card_width, card_height)],
                radius=corner_radius,
                fill=255
            )
            
            # 将模糊后的区域转换为RGBA，应用遮罩得到圆角模糊图
            blurred_rgba = blurred_region.convert('RGBA')
            rounded_blurred = Image.new('RGBA', (card_width, card_height), (0, 0, 0, 0))
            rounded_blurred.paste(blurred_rgba, (0, 0), mask)
            
            # 添加半透明白色遮罩（毛玻璃效果）
            white_overlay = Image.new('RGBA', (card_width, card_height), (255, 255, 255, 77))
            glass_rgba = Image.alpha_composite(rounded_blurred, white_overlay)
            
            # 在毛玻璃图片上绘制文字
            draw = ImageDraw.Draw(glass_rgba)
            
            # 尝试加载字体
            try:
                title_font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 32)
                message_font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 18)
                small_font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
            except:
                title_font = ImageFont.load_default()
                message_font = ImageFont.load_default()
                small_font = ImageFont.load_default()
            
            # 绘制标题（移除 emoji，使用纯文字）
            title_text = TITLE_TEXT.replace('⏰ ', '').replace('⏰', '')  # 移除闹钟图标
            bbox = draw.textbbox((0, 0), title_text, font=title_font)
            title_width = bbox[2] - bbox[0]
            title_x = (card_width - title_width) // 2
            draw.text((title_x, 40), title_text, font=title_font, fill=(255, 255, 255))
            
            current_y = 100
            
            # 绘制提醒次数
            if self.remind_count > 1:
                count_text = f"第 {self.remind_count} 次提醒"
                bbox = draw.textbbox((0, 0), count_text, font=small_font)
                count_width = bbox[2] - bbox[0]
                count_x = (card_width - count_width) // 2
                draw.text((count_x, current_y), count_text, font=small_font, fill=(255, 215, 0))  # 金色
                current_y += 35
            
            # 绘制提示文字（支持换行）
            message_lines = self.message_text.split('\n')
            for line in message_lines:
                bbox = draw.textbbox((0, 0), line, font=message_font)
                line_width = bbox[2] - bbox[0]
                line_x = (card_width - line_width) // 2
                draw.text((line_x, current_y), line, font=message_font, fill=(255, 255, 255))
                current_y += 30
            
            current_y += 20
            
            # 绘制下次提醒时间
            if self.next_remind_time:
                time_text = f"⏰ 下次提醒时间: {self.next_remind_time}"
                bbox = draw.textbbox((0, 0), time_text, font=small_font)
                time_width = bbox[2] - bbox[0]
                time_x = (card_width - time_width) // 2
                draw.text((time_x, current_y), time_text, font=small_font, fill=(135, 206, 235))  # 浅蓝色
                current_y += 40
            
            # 绘制底部提示文字（直接画在毛玻璃上，无额外背景）
            hint_text = "按 ESC 键也可快速关闭"
            bbox = draw.textbbox((0, 0), hint_text, font=small_font)
            hint_width = bbox[2] - bbox[0]
            hint_x = (card_width - hint_width) // 2
            draw.text((hint_x, card_height - 35), hint_text, font=small_font, fill=(153, 153, 153))  # 灰色
            
            # 关键修复：使用遮罩将毛玻璃卡片粘贴到最终背景上
            final_image.paste(glass_rgba, (card_x, card_y), mask)
            
            # 创建一个全屏 Label（先创建，不设置 image）
            logger.info("Creating full_label...")
            self.full_label = tk.Label(
                self.root,
                bd=0,
                highlightthickness=0
            )
            self.full_label.place(x=0, y=0, width=screen_width, height=screen_height)
            
            # 关键修复：在 Label 创建并放置后，再设置 image
            # 这样可以确保 Tcl 解释器已经准备好接收图像
            logger.info(f"Creating PhotoImage from final_image: {final_image.size}, mode={final_image.mode}")
            self.final_photo = ImageTk.PhotoImage(final_image)
            logger.info(f"PhotoImage created: {self.final_photo}")
            
            # 关键修复：使用 after(0) 延迟设置 image，让事件循环有机会处理
            # 这比 update_idletasks() 更安全，不会触发意外的清理操作
            def set_image():
                try:
                    self.full_label.config(image=self.final_photo)
                    logger.info("Image set successfully on label")
                except Exception as e:
                    logger.error(f"Failed to set image on label: {e}")
                    raise
            
            self.root.after(0, set_image)
            
            # 在毛玻璃卡片区域放置圆角按钮（按钮放在背景之上）
            self._create_rounded_buttons_v2(card_x, card_y, card_width, card_height, current_y + 20)
            
            logger.info("圆角毛玻璃效果创建成功")
            
        except Exception as e:
            logger.error(f"创建毛玻璃效果失败: {str(e)}，使用普通卡片")
            import traceback
            logger.error(traceback.format_exc())
            self._create_simple_card()
    
    def _create_rounded_buttons_v2(self, card_x, card_y, card_width, card_height, btn_y):
        """创建圆角按钮（放在背景之上）"""
        btn_width_px = 160  # 按钮宽度（像素）
        btn_height_px = 50  # 按钮高度（像素）
        
        # 获取按钮文字（移除 emoji）
        confirm_text = BUTTON_CONFIRM_TEXT.replace('✓ ', '').replace('✓', '')
        later_text = BUTTON_LATER_TEXT.replace('⏱ ', '').replace('⏱', '').replace('⏲ ', '').replace('⏲', '')
        
        # 计算按钮位置
        btn1_x = card_x + card_width//2 - 170
        btn2_x = card_x + card_width//2 + 10
        btn_y_pos = card_y + btn_y
        
        # 创建按钮（使用 tk.Button，放在背景之上）
        # 确认按钮
        confirm_btn = tk.Button(
            self.root,
            text=confirm_text,
            font=('Microsoft YaHei', 14, 'bold'),
            width=12,
            height=2,
            bg='#4CAF50',  # 绿色背景
            fg='white',
            activebackground='#45a049',
            activeforeground='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self._on_confirm,
            highlightthickness=0,
            bd=0
        )
        confirm_btn.place(x=btn1_x, y=btn_y_pos, width=btn_width_px, height=btn_height_px)
        
        # 稍后按钮
        later_btn = tk.Button(
            self.root,
            text=later_text,
            font=('Microsoft YaHei', 14, 'bold'),
            width=12,
            height=2,
            bg='#FF9800',  # 橙色背景
            fg='white',
            activebackground='#e68900',
            activeforeground='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self._on_later,
            highlightthickness=0,
            bd=0
        )
        later_btn.place(x=btn2_x, y=btn_y_pos, width=btn_width_px, height=btn_height_px)
    
    def _create_simple_card(self):
        """创建普通卡片（降级方案，当毛玻璃效果失败时使用）"""
        # 创建主框架（居中显示，圆角效果）
        main_frame = tk.Frame(self.root, bg='white', bd=0)
        main_frame.place(relx=0.5, rely=0.5, anchor='center', width=550, height=400)
        
        # 标题
        title_font = font.Font(family="Microsoft YaHei", size=28, weight="bold")
        title_label = tk.Label(
            main_frame,
            text=TITLE_TEXT,
            font=title_font,
            bg='white',
            fg='#FF6B35'
        )
        title_label.pack(pady=(35, 15))
        
        # 提醒次数标签（仅在非首次提醒时显示）
        if self.remind_count > 1:
            count_font = font.Font(family="Microsoft YaHei", size=14, weight="bold")
            count_label = tk.Label(
                main_frame,
                text=f"第 {self.remind_count} 次提醒",
                font=count_font,
                bg='white',
                fg='#FF9800'
            )
            count_label.pack(pady=(0, 10))
        
        # 提示文字
        message_font = font.Font(family="Microsoft YaHei", size=16)
        message_label = tk.Label(
            main_frame,
            text=self.message_text,
            font=message_font,
            bg='white',
            fg='#333333',
            justify='center',
            wraplength=450
        )
        message_label.pack(pady=(0, 20))
        
        # 下次提醒时间标签
        if self.next_remind_time:
            next_time_font = font.Font(family="Microsoft YaHei", size=13, weight="bold")
            next_time_label = tk.Label(
                main_frame,
                text=f"⏰ 下次提醒时间: {self.next_remind_time}",
                font=next_time_font,
                bg='white',
                fg='#2196F3'
            )
            next_time_label.pack(pady=(0, 15))
        
        # 按钮框架
        btn_frame = tk.Frame(main_frame, bg='white')
        btn_frame.pack(pady=(10, 15))
        
        # 按钮样式
        btn_font = font.Font(family="Microsoft YaHei", size=14, weight="bold")
        btn_width = 14
        btn_height = 2
        
        # 确认按钮
        confirm_btn = tk.Button(
            btn_frame,
            text=BUTTON_CONFIRM_TEXT,
            font=btn_font,
            width=btn_width,
            height=btn_height,
            bg='#4CAF50',
            fg='white',
            activebackground='#45a049',
            activeforeground='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self._on_confirm,
            highlightthickness=0,
            bd=0
        )
        confirm_btn.pack(side=tk.LEFT, padx=15)
        
        # 稍后按钮
        later_btn = tk.Button(
            btn_frame,
            text=BUTTON_LATER_TEXT,
            font=btn_font,
            width=btn_width,
            height=btn_height,
            bg='#FF9800',
            fg='white',
            activebackground='#e68900',
            activeforeground='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self._on_later,
            highlightthickness=0,
            bd=0
        )
        later_btn.pack(side=tk.LEFT, padx=15)
        
        # 提示文字
        hint_font = font.Font(family="Microsoft YaHei", size=10)
        hint_label = tk.Label(
            main_frame,
            text="按 ESC 键也可快速关闭",
            font=hint_font,
            bg='white',
            fg='#999999'
        )
        hint_label.pack(pady=(5, 10))
    
    def _on_confirm(self):
        """处理确认按钮点击"""
        logger.info("用户点击确认按钮")
        self._close_window()
        if self.on_confirm:
            self.on_confirm()
    
    def _on_later(self):
        """处理稍后按钮点击"""
        logger.info("用户点击稍后按钮")
        
        # 调用回调函数，获取下次提醒信息
        later_info = {}
        if self.on_later:
            result = self.on_later()
            if result is not None:
                later_info = result
        
        # 显示等待状态
        self._show_waiting_status(later_info)
    
    def _show_waiting_status(self, later_info):
        """
        显示等待状态（点击稍后提醒后）
        
        Args:
            later_info (dict): 包含下次提醒信息的字典
        """
        # 清除原有所有子控件（包括按钮和标签）
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 卡片尺寸和位置
        card_width = 500
        card_height = 300
        corner_radius = 20
        card_x = (screen_width - card_width) // 2
        card_y = (screen_height - card_height) // 2
        
        try:
            # 使用背景图片创建毛玻璃效果
            if hasattr(self, 'bg_image') and self.bg_image:
                # 关键修复：使用RGBA模式创建最终图片
                final_image = self.bg_image.copy().convert('RGBA')
                
                # 从背景中截取卡片区域并应用高斯模糊
                card_region = self.bg_image.crop((card_x, card_y, card_x + card_width, card_y + card_height))
                blurred_region = card_region.filter(ImageFilter.GaussianBlur(radius=15))
                
                # 创建圆角遮罩
                mask = Image.new('L', (card_width, card_height), 0)
                mask_draw = ImageDraw.Draw(mask)
                mask_draw.rounded_rectangle(
                    [(0, 0), (card_width, card_height)],
                    radius=corner_radius,
                    fill=255
                )
                
                # 将模糊后的区域转换为RGBA，应用遮罩得到圆角模糊图
                blurred_rgba = blurred_region.convert('RGBA')
                rounded_blurred = Image.new('RGBA', (card_width, card_height), (0, 0, 0, 0))
                rounded_blurred.paste(blurred_rgba, (0, 0), mask)
                
                # 添加半透明白色遮罩（毛玻璃效果）
                white_overlay = Image.new('RGBA', (card_width, card_height), (255, 255, 255, 77))
                glass_rgba = Image.alpha_composite(rounded_blurred, white_overlay)
                
                # 在毛玻璃图片上绘制文字
                draw = ImageDraw.Draw(glass_rgba)
                
                # 尝试加载字体
                try:
                    title_font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 32)
                    message_font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 22)
                    time_font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)
                    hint_font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 13)
                except:
                    title_font = ImageFont.load_default()
                    message_font = ImageFont.load_default()
                    time_font = ImageFont.load_default()
                    hint_font = ImageFont.load_default()
                
                # 绘制等待图标文字（使用汉字代替emoji）
                icon_text = "稍后提醒"
                bbox = draw.textbbox((0, 0), icon_text, font=title_font)
                icon_width = bbox[2] - bbox[0]
                icon_x = (card_width - icon_width) // 2
                draw.text((icon_x, 50), icon_text, font=title_font, fill=(255, 152, 0))  # 橙色
                
                # 绘制提示文字
                message_text = "已设置成功"
                bbox = draw.textbbox((0, 0), message_text, font=message_font)
                message_width = bbox[2] - bbox[0]
                message_x = (card_width - message_width) // 2
                draw.text((message_x, 110), message_text, font=message_font, fill=(51, 51, 51))
                
                # 绘制下次提醒时间
                next_time = later_info.get('next_time', '未知')
                interval = later_info.get('interval', REMIND_INTERVAL_MINUTES)
                time_text = f"将在 {interval} 分钟后 ({next_time}) 再次提醒"
                bbox = draw.textbbox((0, 0), time_text, font=time_font)
                time_width = bbox[2] - bbox[0]
                time_x = (card_width - time_width) // 2
                draw.text((time_x, 160), time_text, font=time_font, fill=(33, 150, 243))  # 蓝色
                
                # 绘制自动关闭提示
                hint_text = "窗口将自动关闭..."
                bbox = draw.textbbox((0, 0), hint_text, font=hint_font)
                hint_width = bbox[2] - bbox[0]
                hint_x = (card_width - hint_width) // 2
                draw.text((hint_x, 220), hint_text, font=hint_font, fill=(153, 153, 153))
                
                # 将毛玻璃卡片粘贴到最终背景上
                final_image.paste(glass_rgba, (card_x, card_y), mask)
                
                # 创建新的全屏 Label 显示图片
                self.full_label = tk.Label(
                    self.root,
                    bd=0,
                    highlightthickness=0
                )
                self.full_label.place(x=0, y=0, width=screen_width, height=screen_height)
                
                # 更新图片引用
                self.final_photo = ImageTk.PhotoImage(final_image)
                self.full_label.config(image=self.final_photo)
                
                logger.info("等待状态页面创建成功（毛玻璃效果）")
            else:
                # 降级方案：使用普通白色卡片
                raise Exception("No background image available")
                
        except Exception as e:
            logger.warning(f"创建毛玻璃等待页面失败: {e}，使用降级方案")
            # 降级方案：创建简单的白色卡片
            wait_frame = tk.Frame(self.root, bg='white', bd=2, relief=tk.RAISED)
            wait_frame.place(relx=0.5, rely=0.5, anchor='center', width=500, height=300)
            
            wait_font = font.Font(family="Microsoft YaHei", size=20, weight="bold")
            wait_label = tk.Label(
                wait_frame,
                text="稍后提醒",
                font=wait_font,
                bg='white',
                fg='#FF9800'
            )
            wait_label.pack(pady=(40, 20))
            
            message_font = font.Font(family="Microsoft YaHei", size=16)
            message_label = tk.Label(
                wait_frame,
                text="已设置成功",
                font=message_font,
                bg='white',
                fg='#333333'
            )
            message_label.pack(pady=(0, 20))
            
            next_time = later_info.get('next_time', '未知')
            interval = later_info.get('interval', REMIND_INTERVAL_MINUTES)
            
            time_font = font.Font(family="Microsoft YaHei", size=14, weight="bold")
            time_label = tk.Label(
                wait_frame,
                text=f"将在 {interval} 分钟后 ({next_time}) 再次提醒",
                font=time_font,
                bg='white',
                fg='#2196F3'
            )
            time_label.pack(pady=(0, 30))
            
            hint_font = font.Font(family="Microsoft YaHei", size=11)
            hint_label = tk.Label(
                wait_frame,
                text="窗口将自动关闭...",
                font=hint_font,
                bg='white',
                fg='#999999'
            )
            hint_label.pack(pady=(0, 10))
        
        # 3秒后自动关闭窗口
        self.root.after(3000, self._close_window)
    
    def _close_window(self):
        """关闭窗口"""
        if self.root:
            self.root.destroy()
            self.root = None
            # 从活动窗口列表中移除自己
            if self in RemindWindow._active_windows:
                RemindWindow._active_windows.remove(self)


def show_reminder(remind_type="work_start", remind_count=1, next_remind_time=None, on_confirm=None, on_later=None):
    """
    显示提醒窗口的便捷函数
    
    Args:
        remind_type (str): 提醒类型（"work_start" 或 "work_end"）
        remind_count (int): 当前提醒次数
        next_remind_time (str): 下次提醒时间（格式：HH:MM）
        on_confirm (callable): 确认按钮回调函数
        on_later (callable): 稍后按钮回调函数
    """
    window = RemindWindow(
        remind_type=remind_type,
        remind_count=remind_count,
        next_remind_time=next_remind_time,
        on_confirm=on_confirm,
        on_later=on_later
    )
    window.show()


if __name__ == "__main__":
    # 测试代码
    def test_confirm():
        print("用户已确认打卡")
    
    def test_later():
        print("用户选择稍后提醒")
    
    show_reminder(remind_type="work_start", on_confirm=test_confirm, on_later=test_later)
