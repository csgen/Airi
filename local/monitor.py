import psutil
import time
import pandas as pd
from datetime import datetime, timedelta
from pynput import mouse, keyboard
import json
import threading
from collections import defaultdict
import win32gui
from pathlib import Path
import tzlocal

# 工作相关
work_keywords = ['visual studio', 'pycharm', 'vscode', 'intellij', 'sublime', 'docker',
                'terminal', 'cmd', 'powershell', 'outlook', 'slack', 'teams', 'word', 'excel', 'powerpoint',
                'deepseek', 'chatgpt', 'gemini', 'github', 'gmail', 'mail', 'linkedIn']
# 创作相关
creative_keywords = ['photoshop', 'premiere', 'figma', 'blender', 'sketch', 'wikipedia', '公众号', '微信公众平台', '维基百科']
# 娱乐相关  
entertainment_keywords = ['chrome', 'firefox', 'safari', 'edge', 'spotify', 
                        'netflix', 'youtube', 'steam', 'game', 'KPL', 'bilibili']
# 社交相关
social_keywords = ['wechat', 'wexin', 'whatsapp', 'discord', 'twitter', 'facebook']

class ComputerActivityMonitor:
    def __init__(self):
        self.activity_data = []
        self.last_activity_time = time.time()
        self.current_app = None
        self.input_count = 0
        self.last_app_switch_time = None
        self.is_first_app = True

        self.data_dir = Path(__file__).resolve().parent.parent / "data"
        self.data_dir.mkdir(exist_ok=True)

    def start(self):
        print("===== Airi — 观测模块已启动 =====")
        print("正在观测应用切换、鼠标键盘输入，并每5分钟自动保存数据。")
        print("按 Ctrl + C 可退出程序。\n")

        self.start_app_monitor()
        self.start_input_monitor()
        self.start_auto_save()

        # 主线程阻塞，保持运行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n退出中，正在保存剩余数据...")
            self.save_data()
            print("已安全退出。")

    def start_app_monitor(self):
        '''监控应用使用情况'''
        def monitor_apps():
            while True:
                try:
                    active_window = self.get_active_window()
                    local_tz = tzlocal.get_localzone()
                    current_time = datetime.now(local_tz)

                    if active_window and active_window != self.current_app:
                        if self.current_app:
                            self.record_app_usage(self.current_app, current_time)
                        
                        self.current_app = active_window

                        if self.is_first_app:
                            self.last_app_switch_time = current_time
                            self.is_first_app = False
                        
                        print(f"[切换应用] => {active_window}")
                    time.sleep(2) #每2秒检查一次
                
                except Exception as e:
                    print(f"应用监控错误：{e}")
                    time.sleep(5)
        
        thread = threading.Thread(target=monitor_apps, daemon=True)
        thread.start()
                    
    def get_active_window(self):
        '''获取当前活动窗口信息'''
        # windows系统
        window = win32gui.GetForegroundWindow()
        window_title = win32gui.GetWindowText(window)
        return window_title if window_title else 'Unknown'
    
    def categorize_application(self, app_name):
        app_lower = app_name.lower()
        if any(keyword in app_lower for keyword in work_keywords):
            return 'work'
        elif any(keyword in app_lower for keyword in creative_keywords):
            return 'creative'
        elif any(keyword in app_lower for keyword in entertainment_keywords):
            return 'entertainment'
        elif any(keyword in app_lower for keyword in social_keywords):
            return 'social'
        else:
            return 'other'

    def record_app_usage(self, app_name, end_time):
        '''记录应用使用情况'''
        if self.last_app_switch_time is not None:
            duration = (end_time - self.last_app_switch_time).total_seconds()
            if duration > 1:
                activity_type = self.categorize_application(app_name)
                record = {
                    'timestamp': self.last_app_switch_time.isoformat(),
                    'duration_seconds': duration,
                    'application': app_name,
                    'activity_type': activity_type,
                    'input_count': self.input_count
                }
                
                self.activity_data.append(record)
                self.input_count = 0

        self.last_app_switch_time = end_time

    def start_input_monitor(self):
        '''监控键盘和鼠标的输入'''
        def on_click(x,y,button,pressed):
            if pressed:
                self.last_activity_time = time.time()
                self.input_count += 1
        
        def on_press(key):
            self.last_activity_time = time.time()
            self.input_count += 1

        mouse_listener = mouse.Listener(on_click=on_click)
        keyboard_listener = keyboard.Listener(on_press=on_press)

        mouse_listener.start()
        keyboard_listener.start()

    def start_auto_save(self):
        '''自动保存数据'''
        def save_loop():
            while True:
                time.sleep(300) # 每5分钟
                self.save_data()

        threading.Thread(target=save_loop, daemon=True).start()

    def save_data(self):
        '''保存数据到文件'''
        if self.activity_data:
            df = pd.DataFrame(self.activity_data)
            
            # 按日期保存到不同的文件
            today = datetime.now().strftime("%Y-%m-%d")
            filename = f"{self.data_dir}/computer_activity_{today}.csv"
            
            try:
                # 如果文件已存在，追加数据
                existing_df = pd.read_csv(filename)
                combined_df = pd.concat([existing_df, df], ignore_index=True)
                combined_df.to_csv(filename, index=False)
            except FileNotFoundError:
                # 文件不存在，创建新文件
                df.to_csv(filename, index=False)
            
            print(f"数据已保存到 {filename}, 记录数: {len(df)}")
            self.activity_data = []  # 清空已保存的数据

    # 处理旧文件
    def process_csv_file(self, file_path):
        try:
            df = pd.read_csv(file_path)
            print(f"正在处理文件: {file_path}")
            print(f"原始数据行数: {len(df)}")
            df['activity_type'] = df['application'].apply(self.categorize_application)
            df.to_csv(file_path, index=False)
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {e}")
            return None

if __name__ == "__main__":
    monitor = ComputerActivityMonitor()
    monitor.start()
    