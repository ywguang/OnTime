"""
系统托盘图标管理
提供托盘图标和右键菜单，方便用户快速访问配置界面
"""

import tkinter as tk
from tkinter import messagebox
import os
import threading
from utils.path_helper import get_log_file

# 尝试导入 pystray，如果没有安装则给出提示
try:
    import pystray
    from PIL import Image
    PYSTRAY_AVAILABLE = True
except ImportError:
    PYSTRAY_AVAILABLE = False


class TrayIconManager:
    """托盘图标管理器"""
    
    def __init__(self, on_show_config=None, on_exit=None):
        self.on_show_config = on_show_config
        self.on_exit = on_exit
        self.icon = None
        self.tray_thread = None
        self._test_popup_requested = False  # 测试弹窗请求标志
        
    def _create_icon_image(self):
        """创建托盘图标"""
        # 创建一个简单的图标（蓝色圆形）
        from PIL import Image, ImageDraw
        
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), 'white')
        dc = ImageDraw.Draw(image)
        
        # 绘制蓝色圆形
        dc.ellipse([4, 4, width-4, height-4], fill='#2196F3')
        
        # 绘制白色文字"卡"
        try:
            from PIL import ImageFont
            font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 32)
        except:
            font = ImageFont.load_default()
        
        # 计算文字位置使其居中
        bbox = dc.textbbox((0, 0), "卡", font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2 - 2
        
        dc.text((x, y), "卡", font=font, fill='white')
        
        return image
    
    def _setup_menu(self):
        """设置托盘菜单"""
        return pystray.Menu(
            pystray.MenuItem("⚙️ 打开配置", self._on_show_config),
            pystray.MenuItem("🧪 测试弹窗", self._on_test),
            pystray.MenuItem("📋 查看日志", self._on_view_log),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("❌ 退出程序", self._on_exit)
        )
    
    def _on_show_config(self, icon=None, item=None):
        """打开配置界面"""
        if self.on_show_config:
            # 在主线程中运行
            self.on_show_config()
    
    def _on_test(self, icon=None, item=None):
        """测试弹窗 - 设置标志，由主线程检测并执行"""
        self._test_popup_requested = True
    
    def check_and_execute_test(self):
        """检查并执行测试弹窗（需要在主线程中定期调用）"""
        if self._test_popup_requested:
            self._test_popup_requested = False
            self._execute_test_popup()
    
    def _execute_test_popup(self):
        """实际执行测试弹窗"""
        try:
            from core.notifier import show_reminder
            
            def on_confirm():
                pass
            
            def on_later():
                from datetime import datetime, timedelta
                next_time = datetime.now() + timedelta(minutes=3)
                return {
                    'next_time': next_time.strftime('%H:%M'),
                    'interval': 3
                }
            
            show_reminder(remind_type='work_start', on_confirm=on_confirm, on_later=on_later)
            
        except Exception as e:
            messagebox.showerror("测试失败", f"测试弹窗失败: {str(e)}")
    
    def _on_view_log(self, icon=None, item=None):
        """查看日志"""
        try:
            log_file = get_log_file()
            if os.path.exists(log_file):
                os.startfile(log_file)
            else:
                messagebox.showinfo("日志", "日志文件不存在，请先运行程序生成日志")
        except Exception as e:
            messagebox.showerror("错误", f"无法打开日志: {str(e)}")
    
    def _on_exit(self, icon=None, item=None):
        """退出程序"""
        if self.icon:
            self.icon.stop()
        if self.on_exit:
            self.on_exit()
    
    def start(self):
        """启动托盘图标"""
        if not PYSTRAY_AVAILABLE:
            print("警告: 未安装 pystray，无法显示托盘图标")
            print("请运行: pip install pystray")
            return False
        
        def run_tray():
            self.icon = pystray.Icon(
                "DingDingReminder",
                self._create_icon_image(),
                "打卡提醒助手",
                self._setup_menu()
            )
            self.icon.run()
        
        self.tray_thread = threading.Thread(target=run_tray, daemon=True)
        self.tray_thread.start()
        return True
    
    def stop(self):
        """停止托盘图标"""
        if self.icon:
            self.icon.stop()


class SimpleTrayManager:
    """简化版托盘管理（不使用 pystray，使用 Tkinter 最小化到任务栏）"""
    
    def __init__(self, root, on_show_config=None, on_exit=None):
        self.root = root
        self.on_show_config = on_show_config
        self.on_exit = on_exit
        self.is_minimized = False
        
        # 设置窗口关闭按钮行为（最小化到托盘）
        self.root.protocol("WM_DELETE_WINDOW", self._on_minimize)
        
        # 创建右键菜单
        self._create_context_menu()
        
        # 绑定托盘图标点击事件（使用任务栏图标）
        self.root.bind("<Unmap>", self._on_minimize_event)
    
    def _create_context_menu(self):
        """创建右键菜单"""
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="⚙️ 打开配置", command=self._show_config)
        self.menu.add_command(label="🧪 测试弹窗", command=self._test_popup)
        self.menu.add_separator()
        self.menu.add_command(label="❌ 退出", command=self._exit)
        
        # 绑定右键菜单到窗口
        self.root.bind("<Button-3>", self._show_menu)
    
    def _show_menu(self, event):
        """显示右键菜单"""
        self.menu.post(event.x_root, event.y_root)
    
    def _show_config(self):
        """显示配置界面"""
        if self.on_show_config:
            self.on_show_config()
    
    def _test_popup(self):
        """测试弹窗"""
        try:
            from core.notifier import show_reminder
            
            def on_confirm():
                pass
            
            def on_later():
                from datetime import datetime, timedelta
                next_time = datetime.now() + timedelta(minutes=3)
                return {
                    'next_time': next_time.strftime('%H:%M'),
                    'interval': 3
                }
            
            show_reminder(remind_type='work_start', on_confirm=on_confirm, on_later=on_later)
            
        except Exception as e:
            messagebox.showerror("测试失败", f"测试弹窗失败: {str(e)}")
    
    def _exit(self):
        """退出程序"""
        if self.on_exit:
            self.on_exit()
        self.root.quit()
    
    def _on_minimize(self):
        """最小化窗口"""
        self.root.withdraw()
        self.is_minimized = True
        print("程序已最小化，右键点击任务栏图标可显示菜单")
    
    def _on_minimize_event(self, event):
        """处理最小化事件"""
        if self.root.state() == 'iconic':
            self.root.withdraw()
            self.is_minimized = True
    
    def restore(self):
        """恢复窗口"""
        self.root.deiconify()
        self.is_minimized = False


def create_tray_icon(on_show_config=None, on_exit=None):
    """
    创建托盘图标
    
    Args:
        on_show_config: 显示配置的回调函数
        on_exit: 退出的回调函数
    
    Returns:
        TrayIconManager 或 None
    """
    if PYSTRAY_AVAILABLE:
        manager = TrayIconManager(on_show_config, on_exit)
        if manager.start():
            return manager
    return None


if __name__ == '__main__':
    # 测试托盘图标
    def show_config():
        print("显示配置界面")
    
    def exit_app():
        print("退出程序")
    
    tray = create_tray_icon(show_config, exit_app)
    
    if tray:
        print("托盘图标已启动，按 Ctrl+C 退出")
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            tray.stop()
    else:
        print("无法启动托盘图标")
