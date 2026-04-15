"""
打卡提醒系统 - 配置界面
提供图形化配置界面，支持参数修改和开机自启动设置
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
import sys
import winreg
from utils.path_helper import get_user_config_file, get_main_script


class ConfigWindow:
    """配置界面窗口"""
    
    def __init__(self):
        self.root = None
        self.config_file = self._get_config_file_path()
        self.current_config = self._load_config()
        
    def _get_config_file_path(self):
        """获取配置文件路径"""
        return get_user_config_file()
    
    def _load_config(self):
        """加载配置（从 config.py 获取默认值，从 user_config.json 获取用户配置）"""
        from config import default_config
        
        # 从 config.py 获取所有可配置项
        default_config_dict = {
            # 时间配置
            'WORK_START_TIME': default_config.WORK_START_TIME,
            'WORK_END_TIME': default_config.WORK_END_TIME,
            'REMIND_ADVANCE_MINUTES': default_config.REMIND_ADVANCE_MINUTES,
            'REMIND_INTERVAL_MINUTES': default_config.REMIND_INTERVAL_MINUTES,
            'MAX_REMIND_COUNT': default_config.MAX_REMIND_COUNT,
            'ABSOLUTE_MAX_REMIND_COUNT': default_config.ABSOLUTE_MAX_REMIND_COUNT,
            
            # 工作日配置
            'SKIP_WEEKEND': default_config.SKIP_WEEKEND,
            
            # 弹窗样式配置
            'TITLE_TEXT': default_config.TITLE_TEXT,
            'BUTTON_CONFIRM_TEXT': default_config.BUTTON_CONFIRM_TEXT,
            'BUTTON_LATER_TEXT': default_config.BUTTON_LATER_TEXT,
            'WINDOW_ALPHA': default_config.WINDOW_ALPHA,
            
            # 随机文案配置
            'ENABLE_RANDOM_MESSAGES': default_config.ENABLE_RANDOM_MESSAGES,
            'WORK_START_MESSAGES': default_config.WORK_START_MESSAGES,
            'WORK_END_MESSAGES': default_config.WORK_END_MESSAGES,
            
            # 图片配置
            'ENABLE_TIME_BASED_IMAGES': default_config.ENABLE_TIME_BASED_IMAGES,
            'BACKGROUND_IMAGE': default_config.BACKGROUND_IMAGE,
        }
        
        # 加载用户配置覆盖默认值
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    # 处理列表类型的配置
                    for key in ['WORK_START_MESSAGES', 'WORK_END_MESSAGES']:
                        if key in saved_config and isinstance(saved_config[key], str):
                            saved_config[key] = saved_config[key].split('\n')
                    default_config_dict.update(saved_config)
            except Exception as e:
                print(f"加载配置失败: {e}")
        
        # 检查当前开机启动状态
        default_config_dict['AUTO_START'] = self._check_auto_start()
        
        return default_config_dict
    
    def _save_config(self):
        """保存配置到文件"""
        try:
            config_to_save = {
                # 时间配置
                'WORK_START_TIME': self.work_start_var.get(),
                'WORK_END_TIME': self.work_end_var.get(),
                'REMIND_ADVANCE_MINUTES': int(self.advance_var.get()),
                'REMIND_INTERVAL_MINUTES': int(self.interval_var.get()),
                'MAX_REMIND_COUNT': int(self.max_remind_var.get()),
                'ABSOLUTE_MAX_REMIND_COUNT': int(self.abs_max_remind_var.get()),
                
                # 工作日配置
                'SKIP_WEEKEND': self.skip_weekend_var.get(),
                
                # 弹窗样式配置
                'TITLE_TEXT': self.title_var.get(),
                'BUTTON_CONFIRM_TEXT': self.confirm_text_var.get(),
                'BUTTON_LATER_TEXT': self.later_text_var.get(),
                'WINDOW_ALPHA': float(self.alpha_var.get()),
                
                # 随机文案配置
                'ENABLE_RANDOM_MESSAGES': self.enable_random_var.get(),
                'WORK_START_MESSAGES': self.work_start_msgs.get('1.0', tk.END).strip().split('\n'),
                'WORK_END_MESSAGES': self.work_end_msgs.get('1.0', tk.END).strip().split('\n'),
                
                # 图片配置
                'ENABLE_TIME_BASED_IMAGES': self.enable_time_images_var.get(),
                'BACKGROUND_IMAGE': self.bg_image_var.get(),
            }
            
            # 过滤空字符串
            config_to_save['WORK_START_MESSAGES'] = [m for m in config_to_save['WORK_START_MESSAGES'] if m.strip()]
            config_to_save['WORK_END_MESSAGES'] = [m for m in config_to_save['WORK_END_MESSAGES'] if m.strip()]
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            messagebox.showerror("保存失败", f"保存配置失败: {str(e)}")
            return False
    
    def _check_auto_start(self):
        """检查是否已设置开机自启动"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_READ
            )
            try:
                value, _ = winreg.QueryValueEx(key, "DingDingReminder")
                winreg.CloseKey(key)
                return True
            except FileNotFoundError:
                winreg.CloseKey(key)
                return False
        except Exception:
            return False
    
    def _set_auto_start(self, enable):
        """设置/取消开机自启动"""
        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            
            if enable:
                if getattr(sys, 'frozen', False):
                    exe_path = sys.executable
                else:
                    exe_path = get_main_script()
                
                winreg.SetValueEx(key, "DingDingReminder", 0, winreg.REG_SZ, f'"{exe_path}"')
            else:
                try:
                    winreg.DeleteValue(key, "DingDingReminder")
                except FileNotFoundError:
                    pass
            
            winreg.CloseKey(key)
            return True
        except Exception as e:
            messagebox.showerror("设置失败", f"设置开机自启动失败: {str(e)}")
            return False
    
    def show(self):
        """显示配置窗口"""
        self.root = tk.Tk()
        self.root.title("打卡提醒助手 - 配置")
        self.root.geometry("600x700")
        
        # 设置窗口居中
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        self._create_widgets()
        self.root.mainloop()
    
    def _create_widgets(self):
        """创建界面组件"""
        # 创建 Notebook（选项卡）
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # ========== 基础配置选项卡 ==========
        basic_frame = ttk.Frame(notebook, padding="10")
        notebook.add(basic_frame, text='基础配置')
        
        # 时间配置
        time_frame = ttk.LabelFrame(basic_frame, text="时间配置", padding="10")
        time_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(time_frame, text="上班时间:").grid(row=0, column=0, sticky='w', pady=2)
        self.work_start_var = tk.StringVar(value=self.current_config['WORK_START_TIME'])
        ttk.Entry(time_frame, textvariable=self.work_start_var, width=10).grid(row=0, column=1, sticky='w', padx=5)
        
        ttk.Label(time_frame, text="下班时间:").grid(row=1, column=0, sticky='w', pady=2)
        self.work_end_var = tk.StringVar(value=self.current_config['WORK_END_TIME'])
        ttk.Entry(time_frame, textvariable=self.work_end_var, width=10).grid(row=1, column=1, sticky='w', padx=5)
        
        ttk.Label(time_frame, text="提前提醒(分钟):").grid(row=2, column=0, sticky='w', pady=2)
        self.advance_var = tk.StringVar(value=str(self.current_config['REMIND_ADVANCE_MINUTES']))
        ttk.Spinbox(time_frame, from_=0, to=60, textvariable=self.advance_var, width=8).grid(row=2, column=1, sticky='w', padx=5)
        
        ttk.Label(time_frame, text="提醒间隔(分钟):").grid(row=3, column=0, sticky='w', pady=2)
        self.interval_var = tk.StringVar(value=str(self.current_config['REMIND_INTERVAL_MINUTES']))
        ttk.Spinbox(time_frame, from_=1, to=60, textvariable=self.interval_var, width=8).grid(row=3, column=1, sticky='w', padx=5)
        
        ttk.Label(time_frame, text="最大提醒次数:").grid(row=4, column=0, sticky='w', pady=2)
        self.max_remind_var = tk.StringVar(value=str(self.current_config['MAX_REMIND_COUNT']))
        ttk.Spinbox(time_frame, from_=1, to=10, textvariable=self.max_remind_var, width=8).grid(row=4, column=1, sticky='w', padx=5)
        
        ttk.Label(time_frame, text="绝对最大次数:").grid(row=5, column=0, sticky='w', pady=2)
        self.abs_max_remind_var = tk.StringVar(value=str(self.current_config['ABSOLUTE_MAX_REMIND_COUNT']))
        ttk.Spinbox(time_frame, from_=1, to=20, textvariable=self.abs_max_remind_var, width=8).grid(row=5, column=1, sticky='w', padx=5)
        
        # 选项配置
        option_frame = ttk.LabelFrame(basic_frame, text="选项配置", padding="10")
        option_frame.pack(fill='x', pady=(0, 10))
        
        self.skip_weekend_var = tk.BooleanVar(value=self.current_config['SKIP_WEEKEND'])
        ttk.Checkbutton(option_frame, text="跳过周末（周六日不提醒）", variable=self.skip_weekend_var).pack(anchor='w', pady=2)
        
        self.auto_start_var = tk.BooleanVar(value=self.current_config['AUTO_START'])
        ttk.Checkbutton(option_frame, text="开机自动启动", variable=self.auto_start_var).pack(anchor='w', pady=2)
        
        # ========== 弹窗样式选项卡 ==========
        style_frame = ttk.Frame(notebook, padding="10")
        notebook.add(style_frame, text='弹窗样式')
        
        style_config = ttk.LabelFrame(style_frame, text="样式配置", padding="10")
        style_config.pack(fill='x', pady=(0, 10))
        
        ttk.Label(style_config, text="标题文字:").grid(row=0, column=0, sticky='w', pady=2)
        self.title_var = tk.StringVar(value=self.current_config['TITLE_TEXT'])
        ttk.Entry(style_config, textvariable=self.title_var, width=40).grid(row=0, column=1, sticky='w', padx=5)
        
        ttk.Label(style_config, text="确认按钮:").grid(row=1, column=0, sticky='w', pady=2)
        self.confirm_text_var = tk.StringVar(value=self.current_config['BUTTON_CONFIRM_TEXT'])
        ttk.Entry(style_config, textvariable=self.confirm_text_var, width=40).grid(row=1, column=1, sticky='w', padx=5)
        
        ttk.Label(style_config, text="稍后按钮:").grid(row=2, column=0, sticky='w', pady=2)
        self.later_text_var = tk.StringVar(value=self.current_config['BUTTON_LATER_TEXT'])
        ttk.Entry(style_config, textvariable=self.later_text_var, width=40).grid(row=2, column=1, sticky='w', padx=5)
        
        ttk.Label(style_config, text="窗口透明度:").grid(row=3, column=0, sticky='w', pady=2)
        self.alpha_var = tk.StringVar(value=str(self.current_config['WINDOW_ALPHA']))
        ttk.Spinbox(style_config, from_=0.1, to=1.0, increment=0.1, textvariable=self.alpha_var, width=8).grid(row=3, column=1, sticky='w', padx=5)
        
        # 图片配置
        image_frame = ttk.LabelFrame(style_frame, text="图片配置", padding="10")
        image_frame.pack(fill='x', pady=(0, 10))
        
        self.enable_time_images_var = tk.BooleanVar(value=self.current_config['ENABLE_TIME_BASED_IMAGES'])
        ttk.Checkbutton(image_frame, text="启用时间段图片切换", variable=self.enable_time_images_var).pack(anchor='w', pady=2)
        
        ttk.Label(image_frame, text="背景图片路径:").pack(anchor='w', pady=(5, 0))
        self.bg_image_var = tk.StringVar(value=self.current_config['BACKGROUND_IMAGE'])
        ttk.Entry(image_frame, textvariable=self.bg_image_var, width=50).pack(fill='x', pady=2)
        
        # ========== 文案配置选项卡 ==========
        msg_frame = ttk.Frame(notebook, padding="10")
        notebook.add(msg_frame, text='文案配置')
        
        self.enable_random_var = tk.BooleanVar(value=self.current_config['ENABLE_RANDOM_MESSAGES'])
        ttk.Checkbutton(msg_frame, text="启用随机文案", variable=self.enable_random_var).pack(anchor='w', pady=(0, 10))
        
        # 上班文案
        ttk.Label(msg_frame, text="上班打卡文案（每行一条）:").pack(anchor='w')
        self.work_start_msgs = scrolledtext.ScrolledText(msg_frame, height=8, width=60)
        self.work_start_msgs.pack(fill='both', expand=True, pady=(0, 10))
        self.work_start_msgs.insert('1.0', '\n'.join(self.current_config['WORK_START_MESSAGES']))
        
        # 下班文案
        ttk.Label(msg_frame, text="下班打卡文案（每行一条）:").pack(anchor='w')
        self.work_end_msgs = scrolledtext.ScrolledText(msg_frame, height=8, width=60)
        self.work_end_msgs.pack(fill='both', expand=True)
        self.work_end_msgs.insert('1.0', '\n'.join(self.current_config['WORK_END_MESSAGES']))
        
        # ========== 底部按钮 ==========
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        ttk.Button(button_frame, text="💾 保存配置", command=self._on_save, width=15).pack(side='left', padx=5)
        ttk.Button(button_frame, text="🧪 测试弹窗", command=self._on_test, width=15).pack(side='left', padx=5)
        ttk.Button(button_frame, text="❌ 关闭", command=self.root.destroy, width=15).pack(side='right', padx=5)
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill='x', padx=10, pady=(0, 5))
    
    def _on_save(self):
        """保存配置"""
        # 验证时间格式
        time_format = lambda t: len(t) == 5 and t[2] == ':' and t[:2].isdigit() and t[3:].isdigit()
        
        if not time_format(self.work_start_var.get()):
            messagebox.showerror("格式错误", "上班时间格式错误，请使用 HH:MM 格式")
            return
        
        if not time_format(self.work_end_var.get()):
            messagebox.showerror("格式错误", "下班时间格式错误，请使用 HH:MM 格式")
            return
        
        # 保存配置
        if self._save_config():
            # 设置开机自启动
            if self._set_auto_start(self.auto_start_var.get()):
                self.status_var.set("配置已保存，重启程序后生效")
                messagebox.showinfo("保存成功", "配置已保存，重启程序后生效")
            else:
                self.status_var.set("配置已保存，但开机启动设置失败")
        else:
            self.status_var.set("保存失败")
    
    def _on_test(self):
        """测试弹窗"""
        try:
            # 先隐藏配置窗口，避免多个 Tk() 实例冲突
            self.root.withdraw()
            
            from core.notifier import show_reminder
            
            def on_confirm():
                # 弹窗关闭后恢复配置窗口
                self.root.deiconify()
            
            def on_later():
                from datetime import datetime, timedelta
                next_time = datetime.now() + timedelta(minutes=3)
                result = {
                    'next_time': next_time.strftime('%H:%M'),
                    'interval': 3
                }
                # 弹窗关闭后恢复配置窗口
                self.root.deiconify()
                return result
            
            # 关键修复：使用 after() 延迟调用，让当前事件循环有机会处理
            # 这样可以避免多个 Tk() 实例之间的冲突
            self.root.after(100, lambda: show_reminder(remind_type='work_start', on_confirm=on_confirm, on_later=on_later))
            
        except Exception as e:
            # 发生错误时也要恢复配置窗口
            self.root.deiconify()
            messagebox.showerror("测试失败", f"测试弹窗失败: {str(e)}")


def show_config_window():
    """显示配置窗口的便捷函数"""
    config_window = ConfigWindow()
    config_window.show()


if __name__ == '__main__':
    show_config_window()
