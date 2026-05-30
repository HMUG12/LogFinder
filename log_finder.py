import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from datetime import datetime, timedelta
import zipfile
import io

class LogFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("日志查找器")
        self.root.geometry("1024x768")
        self.root.minsize(800, 600)
        self.root.maxsize(1200, 900)
        
        self.current_results = []
        self.selected_files = []
        self.search_mode = 'normal'  # 'normal' or 'global'
        
        self.setup_styles()
        self.create_widgets()
        self.set_default_values()
    
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

        self.style.map('Global.TButton',
            background=[('active', '#10b981'), ('!active', '#10b981')],
            foreground=[('active', 'white'), ('!active', 'white')]
        )
    
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
    
    def create_widgets(self):
        self.create_title_bar()
        
        main_frame = ttk.Frame(self.root, style='Main.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        self.create_search_panel(main_frame)
        self.create_results_panel(main_frame)
        self.create_preview_dialog()
    
    def create_title_bar(self):
        title_bar = ttk.Frame(self.root, style='TitleBar.TFrame', height=36)
        title_bar.pack(fill=tk.X)
        title_bar.pack_propagate(False)
        
        title_left = ttk.Frame(title_bar, style='TitleBar.TFrame')
        title_left.pack(side=tk.LEFT, padx=12)
        
        self.app_icon = ttk.Label(title_left, text='📊', font=('Segoe UI', 16))
        self.app_icon.pack(side=tk.LEFT, padx=(0, 8))
        
        self.app_title = ttk.Label(title_left, text='日志查找器', font=('Segoe UI', 13, 'bold'), foreground='white', background='#4a4a4a')
        self.app_title.pack(side=tk.LEFT)
        
        title_right = ttk.Frame(title_bar, style='TitleBar.TFrame')
        title_right.pack(side=tk.RIGHT)
        
        minimize_btn = ttk.Button(title_right, text='−', width=3, command=self.minimize_window,
                                  style='TitleBar.TButton')
        minimize_btn.pack(side=tk.RIGHT, fill=tk.Y)
        
        close_btn = ttk.Button(title_right, text='×', width=3, command=self.close_window,
                               style='Close.TButton')
        close_btn.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.style.configure('TitleBar.TButton', background='#4a4a4a', foreground='white', 
                            font=('Segoe UI', 16), borderwidth=0)
        self.style.map('TitleBar.TButton',
            background=[('active', '#5a5a5a')]
        )
        
        self.style.configure('Close.TButton', background='#4a4a4a', foreground='white', 
                            font=('Segoe UI', 14), borderwidth=0)
        self.style.map('Close.TButton',
            background=[('active', '#e81123')]
        )
        
        title_bar.bind('<Button-1>', self.start_drag)
        title_bar.bind('<B1-Motion>', self.on_drag)
    
    def start_drag(self, event):
        self.drag_x = event.x
        self.drag_y = event.y
    
    def on_drag(self, event):
        x = self.root.winfo_x() + (event.x - self.drag_x)
        y = self.root.winfo_y() + (event.y - self.drag_y)
        self.root.geometry(f"+{x}+{y}")
    
    def minimize_window(self):
        self.root.iconify()
    
    def close_window(self):
        self.root.destroy()
    
    def create_search_panel(self, parent):
        search_panel = ttk.Frame(parent, style='Panel.TFrame')
        search_panel.pack(fill=tk.X, pady=(0, 15))
        
        panel_title = ttk.Frame(search_panel, style='Panel.TFrame')
        panel_title.pack(fill=tk.X)
        
        title_label = ttk.Label(panel_title, text='搜索设置', style='PanelTitle.TLabel')
        title_label.pack(anchor=tk.W, padx=20, pady=15)
        
        ttk.Separator(search_panel, orient=tk.HORIZONTAL).pack(fill=tk.X)
        
        path_frame = ttk.Frame(search_panel, style='Panel.TFrame')
        path_frame.pack(fill=tk.X, padx=20, pady=(15, 10))
        
        path_label = ttk.Label(path_frame, text='搜索路径', style='Label.TLabel')
        path_label.pack(anchor=tk.W, pady=(0, 8))
        
        path_input_frame = ttk.Frame(path_frame, style='Panel.TFrame')
        path_input_frame.pack(fill=tk.X)
        
        self.path_entry = ttk.Entry(path_input_frame, style='Input.TEntry', font=('Segoe UI', 11))
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        
        browse_btn = ttk.Button(path_input_frame, text='浏览', command=self.browse_path,
                                style='Secondary.TButton')
        browse_btn.pack(side=tk.RIGHT, padx=(10, 0), ipady=4)
        
        self.path_status = ttk.Label(path_frame, text='', font=('Segoe UI', 10))
        self.path_status.pack(anchor=tk.W, pady=(5, 0))
        
        self.path_entry.bind('<FocusOut>', self.validate_path)
        
        filters_frame = ttk.Frame(search_panel, style='Panel.TFrame')
        filters_frame.pack(fill=tk.X, padx=20)
        
        keyword_frame = ttk.Frame(filters_frame, style='Panel.TFrame')
        keyword_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))
        
        keyword_label = ttk.Label(keyword_frame, text='关键词', style='Label.TLabel')
        keyword_label.pack(anchor=tk.W, pady=(0, 8))
        
        self.keyword_entry = ttk.Entry(keyword_frame, style='Input.TEntry', font=('Segoe UI', 11))
        self.keyword_entry.pack(fill=tk.X, ipady=8)
        
        start_date_frame = ttk.Frame(filters_frame, style='Panel.TFrame')
        start_date_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))
        
        start_date_label = ttk.Label(start_date_frame, text='开始日期', style='Label.TLabel')
        start_date_label.pack(anchor=tk.W, pady=(0, 8))
        
        self.start_date_entry = ttk.Entry(start_date_frame, style='Date.TEntry', font=('Segoe UI', 11))
        self.start_date_entry.pack(fill=tk.X, ipady=8)
        
        end_date_frame = ttk.Frame(filters_frame, style='Panel.TFrame')
        end_date_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        end_date_label = ttk.Label(end_date_frame, text='结束日期', style='Label.TLabel')
        end_date_label.pack(anchor=tk.W, pady=(0, 8))
        
        self.end_date_entry = ttk.Entry(end_date_frame, style='Date.TEntry', font=('Segoe UI', 11))
        self.end_date_entry.pack(fill=tk.X, ipady=8)
        
        buttons_frame = ttk.Frame(search_panel, style='Panel.TFrame')
        buttons_frame.pack(fill=tk.X, padx=20, pady=15)
        
        search_btn = ttk.Button(buttons_frame, text='开始搜索', command=self.perform_search,
                                style='Primary.TButton')
        search_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, 10))
        
        self.global_search_btn = ttk.Button(buttons_frame, text='全局搜索', command=self.perform_global_search,
                                            style='Global.TButton', state=tk.DISABLED)
        self.global_search_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, ipady=8)
    
    def create_results_panel(self, parent):
        results_panel = ttk.Frame(parent, style='Panel.TFrame')
        results_panel.pack(fill=tk.BOTH, expand=True)
        
        results_header = ttk.Frame(results_panel, style='Panel.TFrame')
        results_header.pack(fill=tk.X)
        
        header_left = ttk.Frame(results_header, style='Panel.TFrame')
        header_left.pack(side=tk.LEFT, padx=20, pady=15)
        
        results_title = ttk.Label(header_left, text='搜索结果', style='PanelTitle.TLabel')
        results_title.pack(anchor=tk.W)
        
        header_right = ttk.Frame(results_header, style='Panel.TFrame')
        header_right.pack(side=tk.RIGHT, padx=20, pady=15)
        
        self.result_count = ttk.Label(header_right, text='找到 0 个文件', font=('Segoe UI', 11), 
                                      foreground='#6b7280', background='white')
        self.result_count.pack(side=tk.LEFT, padx=(0, 15))
        
        select_all_btn = ttk.Button(header_right, text='全选', command=self.toggle_select_all,
                                    style='Outline.TButton', width=8)
        select_all_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.download_btn = ttk.Button(header_right, text='下载选中', command=self.download_selected,
                                        style='Primary.TButton', width=12, state=tk.DISABLED)
        self.download_btn.pack(side=tk.LEFT)
        
        ttk.Separator(results_panel, orient=tk.HORIZONTAL).pack(fill=tk.X)
        
        results_container = ttk.Frame(results_panel, style='Panel.TFrame')
        results_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.results_tree = ttk.Treeview(results_container, columns=('filename', 'path', 'size', 'modified'), 
                                         show='headings', height=15)
        self.results_tree.heading('filename', text='文件名', anchor=tk.W)
        self.results_tree.heading('path', text='路径', anchor=tk.W)
        self.results_tree.heading('size', text='大小', anchor=tk.W)
        self.results_tree.heading('modified', text='修改时间', anchor=tk.W)
        
        self.results_tree.column('filename', width=200, stretch=tk.NO)
        self.results_tree.column('path', width=400, stretch=tk.YES)
        self.results_tree.column('size', width=100, stretch=tk.NO)
        self.results_tree.column('modified', width=150, stretch=tk.NO)
        
        self.results_tree.bind('<Double-1>', self.preview_file)
        
        tree_scroll = ttk.Scrollbar(results_container, orient=tk.VERTICAL, command=self.results_tree.yview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.results_tree.configure(yscrollcommand=tree_scroll.set)
        self.results_tree.pack(fill=tk.BOTH, expand=True)
        
        self.results_tree.bind('<Button-1>', self.on_tree_click)
        
        self.empty_frame = ttk.Frame(results_container, style='Panel.TFrame')
        self.empty_label = ttk.Label(self.empty_frame, text='请设置搜索条件并点击"开始搜索"', 
                                     font=('Segoe UI', 12), foreground='#9ca3af', background='white')
        self.empty_label.pack(pady=20)
        
        self.empty_button = ttk.Button(self.empty_frame, text='试试关键词全局搜索功能', 
                                       command=self.perform_global_search, style='Global.TButton', 
                                       state=tk.DISABLED)
        self.empty_button.pack(pady=10)
        
        self.empty_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    def create_preview_dialog(self):
        self.preview_dialog = tk.Toplevel(self.root)
        self.preview_dialog.title('文件预览')
        self.preview_dialog.geometry('850x600')
        self.preview_dialog.minsize(600, 400)
        self.preview_dialog.withdraw()
        
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
        self.preview_dialog.geometry(f"+{x}+{y}")
    
    def browse_path(self):
        path = filedialog.askdirectory(title='选择搜索目录')
        if path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)
            self.validate_path(None)
    
    def validate_path(self, event):
        path = self.path_entry.get().strip()
        if not path:
            self.path_status.config(text='', foreground='black')
            return
        
        if os.path.exists(path):
            self.path_status.config(text='✓ 路径有效', foreground='#10b981')
        else:
            self.path_status.config(text='✗ 路径不存在', foreground='#ef4444')
    
    def perform_search(self):
        self.search_mode = 'normal'
        self.execute_search()
    
    def perform_global_search(self):
        self.search_mode = 'global'
        self.execute_search()
    
    def execute_search(self):
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
        
        self.empty_frame.place_forget()
        
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        self.current_results = []
        self.selected_files = []
        self.update_download_button()
        
        self.root.config(cursor='wait')
        self.root.update()
        
        try:
            if self.search_mode == 'global':
                self.current_results = self.search_logs_global(path, keyword, start_date, end_date)
            else:
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
        
        except Exception as e:
            messagebox.showerror('错误', f'搜索失败: {str(e)}')
        
        finally:
            self.root.config(cursor='')
    
    def show_empty_state(self, keyword):
        if keyword:
            self.empty_label.config(text='未找到符合条件的日志文件')
            self.empty_button.config(state=tk.NORMAL)
            self.global_search_btn.config(state=tk.NORMAL)
        else:
            self.empty_label.config(text='未找到符合条件的日志文件')
            self.empty_button.config(state=tk.DISABLED)
            self.global_search_btn.config(state=tk.DISABLED)
        
        self.empty_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    def search_logs(self, base_path, keyword='', start_date='', end_date=''):
        results = []
        
        for root, dirs, files in os.walk(base_path):
            for filename in files:
                if not filename.endswith('.log'):
                    continue
                
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
    
    def search_logs_global(self, base_path, keyword='', start_date='', end_date=''):
        results = []
        
        if not keyword:
            return self.search_logs(base_path, keyword, start_date, end_date)
        
        drives = self.get_available_drives()
        
        for drive in drives:
            try:
                for root, dirs, files in os.walk(drive):
                    for filename in files:
                        if not filename.endswith('.log'):
                            continue
                        
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
                            
                            try:
                                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read()
                                    if keyword.lower() in content.lower():
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
                        except:
                            continue
            except:
                continue
        
        results.sort(key=lambda x: x['modified'], reverse=True)
        return results
    
    def get_available_drives(self):
        drives = []
        for drive in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            path = f'{drive}:/'
            if os.path.exists(path):
                drives.append(path)
        return drives
    
    def format_size(self, bytes):
        if bytes == 0:
            return '0 B'
        k = 1024
        sizes = ['B', 'KB', 'MB', 'GB']
        i = min(int((bytes ** (1/3)) // 10), 3)
        return f'{bytes / (k ** i):.2f} {sizes[i]}'
    
    def on_tree_click(self, event):
        region = self.results_tree.identify_region(event.x, event.y)
        if region == 'heading':
            return
        
        item = self.results_tree.identify_row(event.y)
        if item:
            if item in self.selected_files:
                self.selected_files.remove(item)
                self.results_tree.selection_remove(item)
            else:
                self.selected_files.append(item)
                self.results_tree.selection_add(item)
            
            self.update_download_button()
    
    def toggle_select_all(self):
        if len(self.selected_files) == len(self.current_results):
            self.selected_files = []
            self.results_tree.selection_remove(*self.results_tree.selection())
        else:
            self.selected_files = [str(i) for i in range(len(self.current_results))]
            self.results_tree.selection_add(*self.selected_files)
        
        self.update_download_button()
    
    def update_download_button(self):
        if len(self.selected_files) > 0:
            self.download_btn.config(state=tk.NORMAL, text=f'下载选中 ({len(self.selected_files)})')
        else:
            self.download_btn.config(state=tk.DISABLED, text='下载选中')
    
    def download_selected(self):
        if not self.selected_files:
            return
        
        paths = [self.current_results[int(i)]['path'] for i in self.selected_files]
        
        if len(paths) == 1:
            self.download_single_file(paths[0])
        else:
            self.download_multiple_files(paths)
    
    def download_single_file(self, file_path):
        try:
            save_path = filedialog.asksaveasfilename(
                initialfile=os.path.basename(file_path),
                defaultextension='.log',
                filetypes=[('日志文件', '*.log'), ('所有文件', '*.*')]
            )
            
            if save_path:
                with open(file_path, 'rb') as src:
                    with open(save_path, 'wb') as dst:
                        dst.write(src.read())
                messagebox.showinfo('成功', '文件下载完成')
        except Exception as e:
            messagebox.showerror('错误', f'下载失败: {str(e)}')
    
    def download_multiple_files(self, paths):
        try:
            save_path = filedialog.asksaveasfilename(
                initialfile='logs.zip',
                defaultextension='.zip',
                filetypes=[('ZIP文件', '*.zip')]
            )
            
            if save_path:
                with zipfile.ZipFile(save_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for path in paths:
                        zipf.write(path, os.path.basename(path))
                messagebox.showinfo('成功', '文件打包完成')
        except Exception as e:
            messagebox.showerror('错误', f'下载失败: {str(e)}')
    
    def preview_file(self, event):
        item = self.results_tree.selection()
        if not item:
            return
        
        index = int(item[0])
        file_info = self.current_results[index]
        
        self.preview_title.config(text=f'预览: {file_info["filename"]}')
        self.preview_path.config(text=file_info['path'])
        self.current_preview_path = file_info['path']
        
        try:
            with open(file_info['path'], 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
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

if __name__ == '__main__':
    root = tk.Tk()
    app = LogFinderApp(root)
    root.mainloop()
