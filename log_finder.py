import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from datetime import datetime, timedelta
import zipfile
import io
import threading
import json

class LogFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("日志查找器")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        self.current_results = []
        self.selected_files = []
        self.current_page = 'log'
        
        self.index_db = {}
        self.index_path = os.path.join(os.path.expanduser('~'), '.logfinder_index.json')
        
        self.setup_styles()
        self.create_widgets()
        self.set_default_values()
        self.show_update_log()
    
    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.style.configure('TitleBar.TFrame', background='#4a4a4a')
        self.style.configure('Main.TFrame', background='#f5f5f5')
        self.style.configure('Panel.TFrame', background='white')
        self.style.configure('PanelTitle.TLabel', background='#fafafa', foreground='#2c2c2c', font=('Segoe UI', 12, 'bold'))
        self.style.configure('Label.TLabel', background='#f5f5f5', foreground='#4a4a4a', font=('Segoe UI', 11))
        self.style.configure('Input.TEntry', fieldbackground='white', foreground='#333', font=('Segoe UI', 11))
        self.style.configure('Date.TEntry', fieldbackground='white', foreground='#333', font=('Segoe UI', 11))
        
        self.style.map('Primary.TButton',
            background=[('active', '#5b6270'), ('!active', '#6b7280')],
            foreground=[('active', 'white'), ('!active', 'white')]
        )
        
        self.style.map('Secondary.TButton',
            background=[('active', '#e5e7eb'), ('!active', '#f3f4f6')],
            foreground=[('active', '#374151'), ('!active', '#374151')]
        )
        
        self.style.map('Outline.TButton',
            background=[('active', '#6b7280'), ('!active', 'white')],
            foreground=[('active', 'white'), ('!active', '#6b7280')],
            bordercolor=[('active', '#6b7280'), ('!active', '#6b7280')]
        )
        
        self.style.map('Tab.TButton',
            background=[('active', '#6b7280'), ('selected', '#6b7280'), ('!selected', '#e5e7eb')],
            foreground=[('active', 'white'), ('selected', 'white'), ('!selected', '#374151')]
        )
        
        self.style.map('Treeview',
            background=[('selected', '#fef3c7')],
            foreground=[('selected', '#374151')]
        )
    
    def create_widgets(self):
        self.create_title_bar()
        
        self.tab_bar = ttk.Frame(self.root, style='Main.TFrame', height=40)
        self.tab_bar.pack(fill=tk.X)
        self.tab_bar.pack_propagate(False)
        
        tabs = [('log', '日志搜索'), ('test', '测试'), ('settings', '设置')]
        self.tab_buttons = {}
        
        for key, label in tabs:
            btn = ttk.Button(self.tab_bar, text=label, command=lambda k=key: self.switch_page(k),
                            style='Tab.TButton')
            btn.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.Y)
            self.tab_buttons[key] = btn
        
        self.main_content = ttk.Frame(self.root, style='Main.TFrame')
        self.main_content.pack(fill=tk.BOTH, expand=True)
        
        self.create_log_search_page()
        self.create_test_page()
        self.create_settings_page()
        
        self.switch_page('log')
    
    def create_title_bar(self):
        title_bar = ttk.Frame(self.root, style='TitleBar.TFrame', height=36)
        title_bar.pack(fill=tk.X)
        title_bar.pack_propagate(False)
        
        title_bar_left = ttk.Frame(title_bar, style='TitleBar.TFrame')
        title_bar_left.pack(side=tk.LEFT, padx=12)
        
        title_label = ttk.Label(title_bar_left, text='日志查找器', foreground='white', 
                               background='#4a4a4a', font=('Segoe UI', 12, 'bold'))
        title_label.pack()
        
        title_bar_right = ttk.Frame(title_bar, style='TitleBar.TFrame')
        title_bar_right.pack(side=tk.RIGHT)
        
        minimize_btn = ttk.Button(title_bar_right, text='−', width=3, command=self.minimize_window,
                                  style='Secondary.TButton')
        minimize_btn.pack(side=tk.LEFT, padx=2)
        
        close_btn = ttk.Button(title_bar_right, text='×', width=3, command=self.close_window,
                               style='Secondary.TButton')
        close_btn.pack(side=tk.LEFT, padx=2)
    
    def minimize_window(self):
        self.root.iconify()
    
    def close_window(self):
        self.root.destroy()
    
    def switch_page(self, page):
        self.current_page = page
        
        for key, btn in self.tab_buttons.items():
            if key == page:
                btn.config(style='Primary.TButton')
            else:
                btn.config(style='Outline.TButton')
        
        for child in self.main_content.winfo_children():
            child.pack_forget()
        
        if page == 'log':
            self.log_search_frame.pack(fill=tk.BOTH, expand=True)
        elif page == 'test':
            self.test_frame.pack(fill=tk.BOTH, expand=True)
        elif page == 'settings':
            self.settings_frame.pack(fill=tk.BOTH, expand=True)
    
    def create_log_search_page(self):
        self.log_search_frame = ttk.Frame(self.main_content, style='Main.TFrame')
        
        main_frame = ttk.Frame(self.log_search_frame, style='Main.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        search_panel = ttk.Frame(main_frame, style='Panel.TFrame')
        search_panel.pack(fill=tk.X, pady=(0, 10))
        
        panel_title = ttk.Frame(search_panel, style='Panel.TFrame')
        panel_title.pack(fill=tk.X)
        
        title_label = ttk.Label(panel_title, text='日志搜索', style='PanelTitle.TLabel')
        title_label.pack(anchor=tk.W, padx=15, pady=10)
        
        ttk.Separator(search_panel, orient=tk.HORIZONTAL).pack(fill=tk.X)
        
        path_frame = ttk.Frame(search_panel, style='Panel.TFrame')
        path_frame.pack(fill=tk.X, padx=15, pady=(10, 5))
        
        path_label = ttk.Label(path_frame, text='搜索路径', style='Label.TLabel')
        path_label.pack(anchor=tk.W, pady=(0, 5))
        
        path_input_frame = ttk.Frame(path_frame, style='Panel.TFrame')
        path_input_frame.pack(fill=tk.X)
        
        self.path_entry = ttk.Entry(path_input_frame, style='Input.TEntry', font=('Segoe UI', 10))
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6)
        
        browse_btn = ttk.Button(path_input_frame, text='浏览', command=self.browse_path,
                                style='Secondary.TButton')
        browse_btn.pack(side=tk.RIGHT, padx=(8, 0), ipady=3)
        
        self.path_status = ttk.Label(path_frame, text='', font=('Segoe UI', 9))
        self.path_status.pack(anchor=tk.W, pady=(3, 0))
        
        self.path_entry.bind('<FocusOut>', self.validate_path)
        
        filters_frame = ttk.Frame(search_panel, style='Panel.TFrame')
        filters_frame.pack(fill=tk.X, padx=15)
        
        keyword_frame = ttk.Frame(filters_frame, style='Panel.TFrame')
        keyword_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        keyword_label = ttk.Label(keyword_frame, text='关键词', style='Label.TLabel')
        keyword_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.keyword_entry = ttk.Entry(keyword_frame, style='Input.TEntry', font=('Segoe UI', 10))
        self.keyword_entry.pack(fill=tk.X, ipady=6)
        
        start_date_frame = ttk.Frame(filters_frame, style='Panel.TFrame')
        start_date_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        start_date_label = ttk.Label(start_date_frame, text='开始日期', style='Label.TLabel')
        start_date_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.start_date_entry = ttk.Entry(start_date_frame, style='Date.TEntry', font=('Segoe UI', 10))
        self.start_date_entry.pack(fill=tk.X, ipady=6)
        
        end_date_frame = ttk.Frame(filters_frame, style='Panel.TFrame')
        end_date_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        end_date_label = ttk.Label(end_date_frame, text='结束日期', style='Label.TLabel')
        end_date_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.end_date_entry = ttk.Entry(end_date_frame, style='Date.TEntry', font=('Segoe UI', 10))
        self.end_date_entry.pack(fill=tk.X, ipady=6)
        
        buttons_frame = ttk.Frame(search_panel, style='Panel.TFrame')
        buttons_frame.pack(fill=tk.X, padx=15, pady=10)
        
        search_btn = ttk.Button(buttons_frame, text='开始搜索', command=self.perform_log_search,
                                style='Primary.TButton')
        search_btn.pack(fill=tk.X, expand=True, ipady=6)
        
        results_panel = ttk.Frame(main_frame, style='Panel.TFrame')
        results_panel.pack(fill=tk.BOTH, expand=True)
        
        results_header = ttk.Frame(results_panel, style='Panel.TFrame')
        results_header.pack(fill=tk.X)
        
        header_left = ttk.Frame(results_header, style='Panel.TFrame')
        header_left.pack(side=tk.LEFT, padx=15, pady=10)
        
        results_title = ttk.Label(header_left, text='搜索结果', style='PanelTitle.TLabel')
        results_title.pack(side=tk.LEFT)
        
        self.result_count = ttk.Label(header_left, text='找到 0 个文件', 
                                      font=('Segoe UI', 10), foreground='#6b7280', background='white')
        self.result_count.pack(side=tk.LEFT, padx=10)
        
        header_right = ttk.Frame(results_header, style='Panel.TFrame')
        header_right.pack(side=tk.RIGHT, padx=15, pady=10)
        
        select_all_btn = ttk.Button(header_right, text='全选', command=self.toggle_select_all,
                                    style='Outline.TButton', width=8)
        select_all_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        self.download_btn = ttk.Button(header_right, text='下载选中', command=self.download_selected,
                                        style='Primary.TButton', width=12, state=tk.DISABLED)
        self.download_btn.pack(side=tk.LEFT)
        
        ttk.Separator(results_panel, orient=tk.HORIZONTAL).pack(fill=tk.X)
        
        results_container = ttk.Frame(results_panel, style='Panel.TFrame')
        results_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=8)
        
        self.results_tree = ttk.Treeview(results_container, columns=('filename', 'path', 'size', 'modified'), 
                                         show='headings', height=10, selectmode='extended')
        self.results_tree.heading('filename', text='文件名', anchor=tk.W)
        self.results_tree.heading('path', text='路径', anchor=tk.W)
        self.results_tree.heading('size', text='大小', anchor=tk.W)
        self.results_tree.heading('modified', text='修改时间', anchor=tk.W)
        
        self.results_tree.column('filename', width=200, stretch=tk.NO)
        self.results_tree.column('path', width=400, stretch=tk.YES)
        self.results_tree.column('size', width=100, stretch=tk.NO)
        self.results_tree.column('modified', width=150, stretch=tk.NO)
        
        self.results_tree.bind('<Double-1>', self.preview_file)
        self.results_tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        
        tree_scroll = ttk.Scrollbar(results_container, orient=tk.VERTICAL, command=self.results_tree.yview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.results_tree.configure(yscrollcommand=tree_scroll.set)
        self.results_tree.pack(fill=tk.BOTH, expand=True)
        
        self.empty_label = ttk.Label(results_container, text='请设置搜索条件并点击"开始搜索"', 
                                     font=('Segoe UI', 12), foreground='#9ca3af')
        self.empty_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    def create_test_page(self):
        self.test_frame = ttk.Frame(self.main_content, style='Main.TFrame')
        
        main_frame = ttk.Frame(self.test_frame, style='Main.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        title_label = ttk.Label(main_frame, text='neko测试日志收集', style='PanelTitle.TLabel')
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(0, 10))
        
        mode_frame = ttk.Frame(main_frame, style='Panel.TFrame')
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        mode_label = ttk.Label(mode_frame, text='运行模式', style='Label.TLabel')
        mode_label.pack(anchor=tk.W, padx=15, pady=(10, 6))
        
        self.mode_var = tk.StringVar(value='steam')
        
        steam_radio = ttk.Radiobutton(mode_frame, text='Steam模式', variable=self.mode_var, value='steam',
                                      command=self.on_mode_change)
        steam_radio.pack(anchor=tk.W, padx=15)
        
        custom_radio = ttk.Radiobutton(mode_frame, text='自定义模式', variable=self.mode_var, value='custom',
                                       command=self.on_mode_change)
        custom_radio.pack(anchor=tk.W, padx=15, pady=(3, 10))
        
        self.path_frame = ttk.Frame(main_frame, style='Panel.TFrame')
        self.path_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.drive_var = tk.StringVar()
        self.drives = self.get_available_drives()
        
        if self.mode_var.get() == 'steam':
            drive_label = ttk.Label(self.path_frame, text='选择Steam盘符', style='Label.TLabel')
            drive_label.pack(anchor=tk.W, padx=15, pady=(10, 6))
            
            drive_frame = ttk.Frame(self.path_frame)
            drive_frame.pack(fill=tk.X, padx=15)
            
            self.drive_combobox = ttk.Combobox(drive_frame, textvariable=self.drive_var, 
                                               values=self.drives, state='readonly', width=10)
            self.drive_combobox.pack(side=tk.LEFT, ipady=4)
            
            self.steam_path_label = ttk.Label(drive_frame, text='', font=('Segoe UI', 9), 
                                              foreground='#6b7280', background='white')
            self.steam_path_label.pack(side=tk.LEFT, padx=8)
            
            if self.drives:
                self.drive_var.set(self.drives[0])
                self.update_steam_path()
            
            self.drive_combobox.bind('<<ComboboxSelected>>', lambda e: self.update_steam_path())
        
        else:
            path_label = ttk.Label(self.path_frame, text='选择N.E.K.O.exe所在目录', style='Label.TLabel')
            path_label.pack(anchor=tk.W, padx=15, pady=(10, 6))
            
            path_entry_frame = ttk.Frame(self.path_frame)
            path_entry_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
            
            self.custom_path_entry = ttk.Entry(path_entry_frame, style='Input.TEntry', font=('Segoe UI', 10))
            self.custom_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)
            
            browse_btn = ttk.Button(path_entry_frame, text='浏览', command=self.browse_custom_path,
                                    style='Outline.TButton', width=10)
            browse_btn.pack(side=tk.RIGHT, padx=(8, 0))
        
        self.status_frame = ttk.Frame(main_frame, style='Panel.TFrame')
        self.status_frame.pack(fill=tk.X, pady=(0, 10))
        
        status_label = ttk.Label(self.status_frame, text='运行状态', style='Label.TLabel')
        status_label.pack(anchor=tk.W, padx=15, pady=(10, 6))
        
        self.status_text = tk.Text(self.status_frame, height=5, font=('Consolas', 9), wrap=tk.WORD,
                                   state=tk.DISABLED)
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))
        
        buttons_frame = ttk.Frame(main_frame, style='Panel.TFrame')
        buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.start_btn = ttk.Button(buttons_frame, text='启动并收集日志', command=self.start_neko_server,
                                    style='Primary.TButton')
        self.start_btn.pack(side=tk.LEFT, padx=15, fill=tk.X, expand=True, ipady=6)
        
        self.stop_btn = ttk.Button(buttons_frame, text='停止', command=self.stop_neko_server,
                                   style='Outline.TButton', state=tk.DISABLED)
        self.stop_btn.pack(side=tk.RIGHT, padx=(8, 15), fill=tk.X, expand=True, ipady=6)
        
        download_frame = ttk.Frame(main_frame, style='Panel.TFrame')
        download_frame.pack(fill=tk.X)
        
        self.download_btn = ttk.Button(download_frame, text='下载日志文件', command=self.download_neko_logs,
                                       style='Primary.TButton', state=tk.DISABLED)
        self.download_btn.pack(side=tk.RIGHT, padx=15, pady=10, ipady=6)
        
        self.neko_process = None
        self.log_file_path = None
    
    def get_available_drives(self):
        drives = []
        for drive in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            path = f'{drive}:/'
            if os.path.exists(path):
                drives.append(f'{drive}:')
        return drives
    
    def on_mode_change(self):
        for child in self.path_frame.winfo_children():
            child.destroy()
        
        if self.mode_var.get() == 'steam':
            drive_label = ttk.Label(self.path_frame, text='选择Steam盘符', style='Label.TLabel')
            drive_label.pack(anchor=tk.W, padx=15, pady=(10, 6))
            
            drive_frame = ttk.Frame(self.path_frame)
            drive_frame.pack(fill=tk.X, padx=15)
            
            self.drive_combobox = ttk.Combobox(drive_frame, textvariable=self.drive_var, 
                                               values=self.drives, state='readonly', width=10)
            self.drive_combobox.pack(side=tk.LEFT, ipady=4)
            
            self.steam_path_label = ttk.Label(drive_frame, text='', font=('Segoe UI', 9), 
                                              foreground='#6b7280', background='white')
            self.steam_path_label.pack(side=tk.LEFT, padx=8)
            
            if self.drives:
                self.drive_var.set(self.drives[0])
                self.update_steam_path()
            
            self.drive_combobox.bind('<<ComboboxSelected>>', lambda e: self.update_steam_path())
        
        else:
            path_label = ttk.Label(self.path_frame, text='选择N.E.K.O.exe所在目录', style='Label.TLabel')
            path_label.pack(anchor=tk.W, padx=15, pady=(10, 6))
            
            path_entry_frame = ttk.Frame(self.path_frame)
            path_entry_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
            
            self.custom_path_entry = ttk.Entry(path_entry_frame, style='Input.TEntry', font=('Segoe UI', 10))
            self.custom_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)
            
            browse_btn = ttk.Button(path_entry_frame, text='浏览', command=self.browse_custom_path,
                                    style='Outline.TButton', width=10)
            browse_btn.pack(side=tk.RIGHT, padx=(8, 0))
    
    def update_steam_path(self):
        drive = self.drive_var.get()
        steam_path = f'{drive}/SteamLibrary/steamapps/common/n.e.k.o/resources/bin/projectneko_server.exe'
        self.steam_path_label.config(text=f'路径: {steam_path}')
    
    def browse_custom_path(self):
        path = filedialog.askdirectory(title='选择N.E.K.O.exe所在目录')
        if path:
            self.custom_path_entry.delete(0, tk.END)
            self.custom_path_entry.insert(0, path)
    
    def start_neko_server(self):
        server_path = None
        
        if self.mode_var.get() == 'steam':
            drive = self.drive_var.get()
            server_path = f'{drive}/SteamLibrary/steamapps/common/n.e.k.o/resources/bin/projectneko_server.exe'
        else:
            custom_path = self.custom_path_entry.get()
            if not custom_path:
                self.append_status('错误: 请选择N.E.K.O.exe所在目录')
                return
            server_path = os.path.join(custom_path, 'resources', 'bin', 'projectneko_server.exe')
        
        if not os.path.exists(server_path):
            self.append_status(f'错误: 未找到文件 {server_path}')
            return
        
        self.append_status(f'正在启动: {server_path}')
        
        self.log_file_path = os.path.join(os.path.dirname(server_path), 'server.log')
        
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            self.neko_process = subprocess.Popen(
                [server_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=os.path.dirname(server_path),
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.download_btn.config(state=tk.DISABLED)
            
            self.append_status('服务器已启动')
            self.read_logs()
        
        except Exception as e:
            self.append_status(f'启动失败: {str(e)}')
            self.start_btn.config(state=tk.NORMAL)
    
    def read_logs(self):
        if self.neko_process and self.neko_process.poll() is None:
            try:
                line = self.neko_process.stdout.readline()
                if line:
                    self.append_status(line.strip())
            except:
                pass
            self.root.after(100, self.read_logs)
        else:
            if self.neko_process and self.neko_process.poll() is not None:
                self.append_status(f'服务器已停止，退出码: {self.neko_process.returncode}')
                self.download_btn.config(state=tk.NORMAL)
    
    def stop_neko_server(self):
        if self.neko_process:
            self.neko_process.terminate()
            self.neko_process = None
            self.append_status('服务器已停止')
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.download_btn.config(state=tk.NORMAL)
    
    def append_status(self, text):
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, text + '\n')
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
    
    def download_neko_logs(self):
        content = self.status_text.get('1.0', tk.END)
        if not content.strip():
            self.append_status('错误: 没有捕获到日志内容')
            return
        
        save_path = filedialog.asksaveasfilename(
            defaultextension='.txt',
            filetypes=[('Text Files', '*.txt'), ('All Files', '*.*')],
            initialfile='neko_server_log.txt'
        )
        
        if save_path:
            try:
                encoding = getattr(self, 'encoding_var', None)
                if encoding:
                    encoding = encoding.get()
                else:
                    encoding = 'utf-8-sig'
                
                with open(save_path, 'w', encoding=encoding) as f:
                    f.write(content)
                self.append_status(f'日志文件已保存到: {save_path}')
                self.append_status(f'使用编码: {encoding}')
            except Exception as e:
                self.append_status(f'保存失败: {str(e)}')
    
    def create_settings_page(self):
        self.settings_frame = ttk.Frame(self.main_content, style='Main.TFrame')
        
        title_label = ttk.Label(self.settings_frame, text='设置', style='PanelTitle.TLabel')
        title_label.pack(anchor=tk.W, padx=15, pady=10)
        
        ttk.Separator(self.settings_frame, orient=tk.HORIZONTAL).pack(fill=tk.X)
        
        settings_container = ttk.Frame(self.settings_frame, style='Panel.TFrame')
        settings_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        default_path_frame = ttk.Frame(settings_container, style='Panel.TFrame')
        default_path_frame.pack(fill=tk.X, pady=(0, 10))
        
        default_path_label = ttk.Label(default_path_frame, text='默认搜索路径', style='Label.TLabel')
        default_path_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.default_path_entry = ttk.Entry(default_path_frame, style='Input.TEntry', font=('Segoe UI', 10), width=60)
        username = os.getlogin()
        self.default_path_entry.insert(0, f'C:\\Users\\{username}\\AppData\\Local\\N.E.K.O\\logs')
        self.default_path_entry.pack(fill=tk.X, ipady=6)
        
        date_range_frame = ttk.Frame(settings_container, style='Panel.TFrame')
        date_range_frame.pack(fill=tk.X, pady=(0, 10))
        
        date_range_label = ttk.Label(date_range_frame, text='默认日期范围（天）', style='Label.TLabel')
        date_range_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.date_range_entry = ttk.Entry(date_range_frame, style='Input.TEntry', font=('Segoe UI', 10), width=10)
        self.date_range_entry.insert(0, '1')
        self.date_range_entry.pack(side=tk.LEFT, ipady=6)
        
        days_label = ttk.Label(date_range_frame, text='天', style='Label.TLabel')
        days_label.pack(side=tk.LEFT, padx=8)
        
        encoding_frame = ttk.Frame(settings_container, style='Panel.TFrame')
        encoding_frame.pack(fill=tk.X, pady=(0, 10))
        
        encoding_label = ttk.Label(encoding_frame, text='日志文件编码格式', style='Label.TLabel')
        encoding_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.encoding_var = tk.StringVar(value='utf-8-sig')
        encoding_options = [
            ('UTF-8 (带BOM)', 'utf-8-sig'),
            ('UTF-8 (无BOM)', 'utf-8'),
            ('GBK', 'gbk'),
            ('GB2312', 'gb2312'),
            ('GB18030', 'gb18030'),
            ('ANSI', 'cp1252'),
        ]
        
        encoding_option_frame = ttk.Frame(encoding_frame)
        encoding_option_frame.pack(fill=tk.X)
        
        for text, value in encoding_options:
            rb = ttk.Radiobutton(encoding_option_frame, text=text, variable=self.encoding_var, value=value)
            rb.pack(side=tk.LEFT, padx=(0, 15))
        
        steam_path_frame = ttk.Frame(settings_container, style='Panel.TFrame')
        steam_path_frame.pack(fill=tk.X, pady=(0, 10))
        
        steam_path_label = ttk.Label(steam_path_frame, text='默认Steam盘符', style='Label.TLabel')
        steam_path_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.steam_drive_var = tk.StringVar()
        drives = self.get_available_drives_for_settings()
        self.steam_drive_combobox = ttk.Combobox(steam_path_frame, textvariable=self.steam_drive_var, 
                                                  values=drives, state='readonly', width=10)
        self.steam_drive_combobox.pack(side=tk.LEFT, ipady=4)
        
        steam_path_hint = ttk.Label(steam_path_frame, text=f'路径示例: X:/SteamLibrary/steamapps/common/n.e.k.o', 
                                    font=('Segoe UI', 9), foreground='#6b7280', background='white')
        steam_path_hint.pack(side=tk.LEFT, padx=10)
        
        if drives:
            self.steam_drive_var.set(drives[0])
        
        custom_path_frame = ttk.Frame(settings_container, style='Panel.TFrame')
        custom_path_frame.pack(fill=tk.X, pady=(0, 10))
        
        custom_path_label = ttk.Label(custom_path_frame, text='默认自定义路径', style='Label.TLabel')
        custom_path_label.pack(anchor=tk.W, pady=(0, 5))
        
        custom_path_input_frame = ttk.Frame(custom_path_frame)
        custom_path_input_frame.pack(fill=tk.X)
        
        self.custom_path_entry = ttk.Entry(custom_path_input_frame, style='Input.TEntry', font=('Segoe UI', 10))
        self.custom_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)
        
        custom_browse_btn = ttk.Button(custom_path_input_frame, text='浏览', command=self.browse_custom_test_path,
                                       style='Outline.TButton', width=10)
        custom_browse_btn.pack(side=tk.RIGHT, padx=(8, 0))
        
        save_btn = ttk.Button(settings_container, text='保存设置', command=self.save_settings,
                              style='Primary.TButton')
        save_btn.pack(pady=15)
    
    def set_default_values(self):
        username = os.getlogin()
        default_path = f'C:\\Users\\{username}\\AppData\\Local\\N.E.K.O\\logs'
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, default_path)
        self.validate_path(None)
        
        today = datetime.now()
        end_date = today.strftime('%Y-%m-%d')
        start_date = (today - timedelta(days=1)).strftime('%Y-%m-%d')
        
        self.start_date_entry.delete(0, tk.END)
        self.start_date_entry.insert(0, start_date)
        
        self.end_date_entry.delete(0, tk.END)
        self.end_date_entry.insert(0, end_date)
    
    def browse_path(self):
        path = filedialog.askdirectory()
        if path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)
            self.validate_path(None)
    
    def validate_path(self, event):
        path = self.path_entry.get().strip()
        if os.path.exists(path):
            self.path_status.config(text='✓ 路径有效', foreground='#10b981')
        else:
            self.path_status.config(text='✗ 路径不存在', foreground='#ef4444')
    
    def perform_log_search(self):
        path = self.path_entry.get().strip()
        keyword = self.keyword_entry.get().strip()
        start_date = self.start_date_entry.get().strip()
        end_date = self.end_date_entry.get().strip()
        
        if not path:
            messagebox.showwarning('警告', '请输入搜索路径')
            return
        
        if not os.path.exists(path):
            messagebox.showwarning('警告', '无效的路径')
            return
        
        self.empty_label.place_forget()
        
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        self.current_results = []
        self.selected_files = []
        self.update_download_button()
        
        self.root.config(cursor='wait')
        self.root.update()
        
        try:
            self.current_results = self.search_logs(path, keyword, start_date, end_date)
            
            for i, file_info in enumerate(self.current_results):
                self.results_tree.insert('', tk.END, iid=str(i), values=(
                    file_info['filename'],
                    file_info['path'],
                    file_info['size_str'],
                    file_info['modified']
                ))
            
            self.result_count.config(text=f'找到 {len(self.current_results)} 个文件')
            
            if len(self.current_results) == 0:
                self.show_empty_state(keyword)
            else:
                self.empty_label.place_forget()
        finally:
            self.root.config(cursor='')
    
    def search_logs(self, base_path, keyword='', start_date='', end_date=''):
        results = []
        
        has_real_files = False
        
        for root, dirs, files in os.walk(base_path):
            for filename in files:
                if not filename.endswith('.log'):
                    continue
                
                has_real_files = True
                file_path = os.path.join(root, filename)
                
                try:
                    stat = os.stat(file_path)
                    file_date = datetime.fromtimestamp(stat.st_mtime)
                    
                    if start_date:
                        try:
                            start = datetime.strptime(start_date, '%Y-%m-%d')
                            if file_date < start:
                                continue
                        except:
                            pass
                    
                    if end_date:
                        try:
                            end = datetime.strptime(end_date, '%Y-%m-%d')
                            end = end.replace(hour=23, minute=59, second=59)
                            if file_date > end:
                                continue
                        except:
                            pass
                    
                    if keyword:
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                if keyword.lower() not in content.lower():
                                    continue
                        except:
                            continue
                    
                    size = stat.st_size
                    size_str = self.format_size(size)
                    
                    results.append({
                        'path': file_path,
                        'filename': filename,
                        'size': size,
                        'size_str': size_str,
                        'modified': file_date.strftime('%Y-%m-%d %H:%M:%S')
                    })
                except:
                    continue
        
        results.sort(key=lambda x: x['modified'], reverse=True)
        return results
    
    def show_empty_state(self, keyword):
        if keyword:
            self.empty_label.config(text='未找到符合条件的日志文件')
        else:
            self.empty_label.config(text='请设置搜索条件并点击"开始搜索"')
        
        self.empty_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    def on_tree_select(self, event):
        self.selected_files = self.results_tree.selection()
        self.update_download_button()
    
    def update_download_button(self):
        if len(self.selected_files) > 0:
            self.download_btn.config(state=tk.NORMAL)
            self.download_btn.config(text=f'下载选中 ({len(self.selected_files)})')
        else:
            self.download_btn.config(state=tk.DISABLED)
            self.download_btn.config(text='下载选中')
    
    def toggle_select_all(self):
        if len(self.selected_files) == len(self.current_results):
            self.selected_files = []
            self.results_tree.selection_remove(*self.results_tree.selection())
        else:
            self.selected_files = [str(i) for i in range(len(self.current_results))]
            self.results_tree.selection_add(*self.selected_files)
        
        self.update_download_button()
    
    def download_selected(self):
        if not self.selected_files:
            return
        
        files_to_download = [self.current_results[int(i)] for i in self.selected_files]
        
        if len(files_to_download) == 1:
            self.download_single_file(files_to_download[0]['path'])
        else:
            self.download_multiple_files([f['path'] for f in files_to_download])
    
    def download_single_file(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            save_path = filedialog.asksaveasfilename(
                defaultextension='.log',
                filetypes=[('Log files', '*.log'), ('All files', '*.*')],
                initialfile=os.path.basename(file_path)
            )
            
            if save_path:
                with open(save_path, 'wb') as f:
                    f.write(content)
                messagebox.showinfo('成功', '文件保存成功')
        except Exception as e:
            messagebox.showerror('错误', f'下载失败: {str(e)}')
    
    def download_multiple_files(self, paths):
        try:
            save_path = filedialog.asksaveasfilename(
                defaultextension='.zip',
                filetypes=[('ZIP files', '*.zip')],
                initialfile='logs.zip'
            )
            
            if save_path:
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for path in paths:
                        zipf.write(path, os.path.basename(path))
                
                with open(save_path, 'wb') as f:
                    f.write(zip_buffer.getvalue())
                
                messagebox.showinfo('成功', '文件打包完成')
        except Exception as e:
            messagebox.showerror('错误', f'下载失败: {str(e)}')
    
    def preview_file(self, event):
        item = self.results_tree.selection()
        if not item:
            return
        
        index = int(item[0])
        file_info = self.current_results[index]
        
        self.current_preview_path = file_info['path']
        
        try:
            with open(file_info['path'], 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            try:
                self.preview_title.config(text=f'预览: {file_info["filename"]}')
                self.preview_path.config(text=file_info['path'])
                self.content_text.config(state=tk.NORMAL)
                self.content_text.delete(1.0, tk.END)
                self.content_text.insert(tk.END, content)
                self.content_text.config(state=tk.DISABLED)
                self.preview_dialog.deiconify()
            except Exception:
                self.create_preview_dialog()
                self.preview_title.config(text=f'预览: {file_info["filename"]}')
                self.preview_path.config(text=file_info['path'])
                self.content_text.config(state=tk.NORMAL)
                self.content_text.delete(1.0, tk.END)
                self.content_text.insert(tk.END, content)
                self.content_text.config(state=tk.DISABLED)
                self.preview_dialog.deiconify()
        except Exception as e:
            messagebox.showerror('错误', f'无法读取文件: {str(e)}')
    
    def download_current_file(self):
        if hasattr(self, 'current_preview_path'):
            self.download_single_file(self.current_preview_path)
    
    def close_preview(self):
        self.preview_dialog.withdraw()
    
    def create_preview_dialog(self):
        self.preview_dialog = tk.Toplevel(self.root)
        self.preview_dialog.title('文件预览')
        self.preview_dialog.geometry('850x600')
        self.preview_dialog.minsize(600, 400)
        self.preview_dialog.withdraw()
        self.preview_dialog.protocol('WM_DELETE_WINDOW', self.close_preview)
        
        preview_title_bar = ttk.Frame(self.preview_dialog, style='TitleBar.TFrame', height=36)
        preview_title_bar.pack(fill=tk.X)
        preview_title_bar.pack_propagate(False)
        
        self.preview_title = ttk.Label(preview_title_bar, text='文件预览', font=('Segoe UI', 12, 'bold'), 
                                       foreground='white', background='#4a4a4a')
        self.preview_title.pack(side=tk.LEFT, padx=12)
        
        preview_close_btn = ttk.Button(preview_title_bar, text='×', width=3, command=self.close_preview,
                                       style='Close.TButton')
        preview_close_btn.pack(side=tk.RIGHT, fill=tk.Y)
        
        preview_title_bar.bind('<Button-1>', self.start_preview_drag)
        preview_title_bar.bind('<B1-Motion>', self.on_preview_drag)
        
        preview_content = ttk.Frame(self.preview_dialog, style='Main.TFrame')
        preview_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        info_frame = ttk.Frame(preview_content, style='Panel.TFrame')
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.preview_path = ttk.Label(info_frame, text='', font=('Segoe UI', 11), 
                                      foreground='#6b7280', background='white', wraplength=600)
        self.preview_path.pack(side=tk.LEFT, padx=15, pady=10)
        
        preview_download_btn = ttk.Button(info_frame, text='下载此文件', command=self.download_current_file,
                                          style='Primary.TButton')
        preview_download_btn.pack(side=tk.RIGHT, padx=15, pady=10)
        
        self.content_text = scrolledtext.ScrolledText(preview_content, wrap=tk.WORD, 
                                                      font=('Consolas', 12), bg='#f8f9fa', 
                                                      fg='#374151', padx=10, pady=10)
        self.content_text.pack(fill=tk.BOTH, expand=True)
        self.content_text.config(state=tk.DISABLED)
    
    def start_preview_drag(self, event):
        self.preview_drag_x = event.x
        self.preview_drag_y = event.y
    
    def on_preview_drag(self, event):
        x = self.preview_dialog.winfo_x() + (event.x - self.preview_drag_x)
        y = self.preview_dialog.winfo_y() + (event.y - self.preview_drag_y)
        self.preview_dialog.geometry(f'+{x}+{y}')
    
    def format_size(self, bytes):
        if bytes == 0:
            return '0 B'
        k = 1024
        sizes = ['B', 'KB', 'MB', 'GB']
        i = min(int((bytes ** (1/3)) // 10), 3)
        return f'{bytes / (k ** i):.2f} {sizes[i]}'
    
    def load_or_build_index(self):
        if os.path.exists(self.index_path):
            self.load_index()
        else:
            self.build_index()
    
    def load_index(self):
        try:
            with open(self.index_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.index_db = data.get('files', {})
                self.index_status.config(text=f'索引状态: 已加载 ({len(self.index_db)} 个文件)', 
                                        foreground='#10b981')
                self.index_loaded = True
        except Exception as e:
            self.index_db = {}
            self.build_index()
    
    def build_index(self):
        if hasattr(self, 'index_building') and self.index_building:
            messagebox.showwarning('提示', '索引正在建立中，请稍候...')
            return
        
        self.index_building = True
        self.index_status.config(text='索引状态: 正在扫描磁盘...', foreground='#f59e0b')
        self.index_progress_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        self.index_progress['value'] = 0
        self.index_progress_label.config(text='0%')
        self.root.update()
        
        threading.Thread(target=self._build_index_thread, daemon=True).start()
    
    def _build_index_thread(self):
        self.index_db = {}
        drives = self.get_available_drives()
        
        has_real_files = False
        total_files = 0
        
        self.index_status.config(text='索引状态: 正在统计文件...', foreground='#f59e0b')
        
        for drive in drives:
            try:
                for root, dirs, files in os.walk(drive):
                    for filename in files:
                        if filename.endswith('.log'):
                            total_files += 1
                            has_real_files = True
            except:
                continue
        
        if not has_real_files:
            self.index_progress_frame.pack_forget()
            self.index_loaded = True
            self.index_building = False
            self.index_status.config(text='索引状态: 未找到日志文件', 
                                    foreground='#ef4444')
            return
        
        self.index_status.config(text='索引状态: 正在建立索引...', foreground='#f59e0b')
        
        processed = 0
        for drive in drives:
            try:
                for root, dirs, files in os.walk(drive):
                    for filename in files:
                        if filename.endswith('.log'):
                            try:
                                file_path = os.path.join(root, filename)
                                stat = os.stat(file_path)
                                file_date = datetime.fromtimestamp(stat.st_mtime)
                                size = stat.st_size
                                
                                self.index_db[file_path] = {
                                    'filename': filename,
                                    'size': size,
                                    'modified': file_date.strftime('%Y-%m-%d %H:%M:%S'),
                                    'modified_timestamp': stat.st_mtime
                                }
                                
                                processed += 1
                                if total_files > 0:
                                    progress = int((processed / total_files) * 100)
                                    self.index_progress['value'] = progress
                                    self.index_progress_label.config(text=f'{progress}% ({processed}/{total_files})')
                                    self.root.update()
                            except:
                                continue
            except:
                continue
        
        try:
            with open(self.index_path, 'w', encoding='utf-8') as f:
                json.dump({'files': self.index_db, 'build_time': datetime.now().isoformat()}, f)
        except:
            pass
        
        self.index_progress_frame.pack_forget()
        self.index_loaded = True
        self.index_building = False
        self.index_status.config(text=f'索引状态: 已建立 ({len(self.index_db)} 个文件)', 
                                foreground='#10b981')
    
    def rebuild_index(self):
        self.index_db = {}
        self.build_index()
    
    def get_available_drives(self):
        drives = []
        for drive in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            path = f'{drive}:/'
            if os.path.exists(path):
                drives.append(path)
        return drives
    
    def perform_global_search(self):
        keyword = self.global_keyword_entry.get().strip()
        ext = self.ext_entry.get().strip() or '.log'
        start_date = self.global_start_date.get().strip()
        end_date = self.global_end_date.get().strip()
        
        if not keyword:
            messagebox.showwarning('警告', '请输入搜索关键词')
            return
        
        self.global_empty_label.place_forget()
        
        for item in self.global_results_tree.get_children():
            self.global_results_tree.delete(item)
        
        self.global_current_results = []
        self.global_selected_files = []
        self.update_global_download_button()
        
        results = []
        
        for file_path, info in self.index_db.items():
            if not file_path.endswith(ext):
                continue
            
            if keyword.lower() not in info['filename'].lower():
                continue
            
            if start_date:
                try:
                    start = datetime.strptime(start_date, '%Y-%m-%d')
                    file_date = datetime.fromtimestamp(info['modified_timestamp'])
                    if file_date < start:
                        continue
                except:
                    pass
            
            if end_date:
                try:
                    end = datetime.strptime(end_date, '%Y-%m-%d')
                    end = end.replace(hour=23, minute=59, second=59)
                    file_date = datetime.fromtimestamp(info['modified_timestamp'])
                    if file_date > end:
                        continue
                except:
                    pass
            
            results.append({
                'path': file_path,
                'filename': info['filename'],
                'size': info['size'],
                'size_str': self.format_size(info['size']),
                'modified': info['modified']
            })
        
        results.sort(key=lambda x: x['modified'], reverse=True)
        
        for i, file_info in enumerate(results):
            self.global_results_tree.insert('', tk.END, iid=str(i), values=(
                file_info['filename'],
                file_info['path'],
                file_info['size_str'],
                file_info['modified']
            ))
        
        self.global_current_results = results
        self.global_result_count.config(text=f'找到 {len(results)} 个文件')
        
        if len(results) == 0:
            self.global_empty_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        else:
            self.global_empty_label.place_forget()
    
    def on_global_tree_select(self, event):
        self.global_selected_files = self.global_results_tree.selection()
        self.update_global_download_button()
    
    def update_global_download_button(self):
        if len(self.global_selected_files) > 0:
            self.global_download_btn.config(state=tk.NORMAL)
            self.global_download_btn.config(text=f'下载选中 ({len(self.global_selected_files)})')
        else:
            self.global_download_btn.config(state=tk.DISABLED)
            self.global_download_btn.config(text='下载选中')
    
    def toggle_select_all_global(self):
        if len(self.global_selected_files) == len(self.global_current_results):
            self.global_selected_files = []
            self.global_results_tree.selection_remove(*self.global_results_tree.selection())
        else:
            self.global_selected_files = [str(i) for i in range(len(self.global_current_results))]
            self.global_results_tree.selection_add(*self.global_selected_files)
        
        self.update_global_download_button()
    
    def download_selected_global(self):
        if not self.global_selected_files:
            return
        
        files_to_download = [self.global_current_results[int(i)] for i in self.global_selected_files]
        
        if len(files_to_download) == 1:
            self.download_single_file(files_to_download[0]['path'])
        else:
            self.download_multiple_files([f['path'] for f in files_to_download])
    
    def preview_global_file(self, event):
        item = self.global_results_tree.selection()
        if not item:
            return
        
        index = int(item[0])
        file_info = self.global_current_results[index]
        
        self.current_preview_path = file_info['path']
        
        try:
            with open(file_info['path'], 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            try:
                self.preview_title.config(text=f'预览: {file_info["filename"]}')
                self.preview_path.config(text=file_info['path'])
                self.content_text.config(state=tk.NORMAL)
                self.content_text.delete(1.0, tk.END)
                self.content_text.insert(tk.END, content)
                self.content_text.config(state=tk.DISABLED)
                self.preview_dialog.deiconify()
            except Exception:
                self.create_preview_dialog()
                self.preview_title.config(text=f'预览: {file_info["filename"]}')
                self.preview_path.config(text=file_info['path'])
                self.content_text.config(state=tk.NORMAL)
                self.content_text.delete(1.0, tk.END)
                self.content_text.insert(tk.END, content)
                self.content_text.config(state=tk.DISABLED)
                self.preview_dialog.deiconify()
        except Exception as e:
            messagebox.showerror('错误', f'无法读取文件: {str(e)}')
    
    def get_available_drives_for_settings(self):
        drives = []
        for drive in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            path = f'{drive}:/'
            if os.path.exists(path):
                drives.append(f'{drive}:')
        return drives
    
    def browse_custom_test_path(self):
        path = filedialog.askdirectory(title='选择N.E.K.O.exe所在目录')
        if path:
            self.custom_path_entry.delete(0, tk.END)
            self.custom_path_entry.insert(0, path)
    
    def save_settings(self):
        settings = {
            'default_path': self.default_path_entry.get(),
            'date_range': self.date_range_entry.get(),
            'encoding': self.encoding_var.get(),
            'steam_drive': self.steam_drive_var.get(),
            'custom_path': self.custom_path_entry.get(),
        }
        
        try:
            with open('log_finder_settings.json', 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
            messagebox.showinfo('成功', '设置已保存')
        except Exception as e:
            messagebox.showerror('错误', f'保存设置失败: {str(e)}')
    
    def load_settings(self):
        if os.path.exists('log_finder_settings.json'):
            try:
                with open('log_finder_settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    if 'encoding' in settings:
                        self.encoding_var.set(settings['encoding'])
                    if 'steam_drive' in settings:
                        self.steam_drive_var.set(settings['steam_drive'])
                    if 'custom_path' in settings:
                        self.custom_path_entry.delete(0, tk.END)
                        self.custom_path_entry.insert(0, settings['custom_path'])
            except Exception:
                pass

    def show_update_log(self):
        current_version = '1.0.0'
        last_version_file = 'last_version.txt'
        
        if os.path.exists(last_version_file):
            with open(last_version_file, 'r', encoding='utf-8') as f:
                last_version = f.read().strip()
            if last_version == current_version:
                return
        
        update_content = f"""日志查找器 v{current_version} 更新日志

【新增功能】
• 新增"测试"页面，支持neko测试日志收集功能
• 支持Steam模式和自定义模式启动项目
• 设置页面新增编码格式选择（UTF-8、GBK、GB2312等）
• 设置页面新增默认测试路径配置
• 新增首次启动更新日志弹窗

【优化改进】
• 优化UI布局，确保最小窗口尺寸下完整显示
• 优化打包配置，减少杀软误报
• 日志下载支持多种编码格式
• 修复subprocess未导入问题

【修复问题】
• 修复双击预览后无法再次打开问题
• 修复选择下载文件数量不匹配问题
• 修复UI拖拽重叠问题
• 修复Tkinter预览对话框错误

感谢您使用日志查找器！"""
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f'更新日志 - v{current_version}')
        dialog.geometry('500x400')
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, style='Main.TFrame')
        frame.pack(fill=tk.BOTH, expand=True)
        
        text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, font=('Segoe UI', 11), state=tk.DISABLED)
        text.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        text.config(state=tk.NORMAL)
        text.insert(tk.END, update_content)
        text.config(state=tk.DISABLED)
        text.see(tk.END)
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        ok_btn = ttk.Button(button_frame, text='知道了', command=dialog.destroy, style='Primary.TButton')
        ok_btn.pack(fill=tk.X, ipady=6)
        
        with open(last_version_file, 'w', encoding='utf-8') as f:
            f.write(current_version)

if __name__ == '__main__':
    root = tk.Tk()
    app = LogFinderApp(root)
    root.mainloop()
