#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件整理工具用户界面
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from scanner import FileScanner
from organizer import FileOrganizer


class FileOrganizerUI:
    """文件整理工具界面类"""
    
    def __init__(self, root):
        """初始化界面"""
        self.root = root
        self.root.title("文件整理工具")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # 定义颜色方案
        self.colors = {
            'primary': '#3498db',
            'secondary': '#2ecc71',
            'accent': '#f39c12',
            'background': '#f8f9fa',
            'surface': '#ffffff',
            'text': '#333333',
            'text_light': '#777777',
            'border': '#e0e0e0',
            'success': '#27ae60',
            'error': '#e74c3c',
            'warning': '#f39c12'
        }
        
        # 设置主题
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self._setup_styles()
        
        # 初始化变量
        self.source_dir = tk.StringVar()
        self.target_dir = tk.StringVar()
        self.search_var = tk.StringVar()
        self.file_list = []  # 原始文件列表
        self.filtered_file_list = []  # 过滤后的文件列表
        self.selected_files = []
        self.tags = {}
        self.last_selected_item = None  # 用于Shift键选择范围
        self.selection_count_var = tk.StringVar(value="已选择: 0 个文件")
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="20", style="MainFrame.TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建UI组件
        self.create_widgets()
    
    def _setup_styles(self):
        """设置样式"""
        # 主框架样式
        self.style.configure("MainFrame.TFrame", background=self.colors['background'])
        
        # 卡片框架样式
        self.style.configure("Card.TFrame", 
                           background=self.colors['surface'],
                           borderwidth=1,
                           relief="solid")
        
        # 标签框架样式
        self.style.configure("Card.TLabelframe", 
                           background=self.colors['surface'],
                           borderwidth=1,
                           relief="solid")
        self.style.configure("Card.TLabelframe.Label", 
                           background=self.colors['surface'],
                           foreground=self.colors['text'])
        
        # 按钮样式
        self.style.configure("Primary.TButton", 
                           background=self.colors['primary'],
                           foreground="white",
                           borderwidth=0,
                           padding=8)
        self.style.map("Primary.TButton", 
                      background=[('active', self._lighten_color(self.colors['primary'], 10))])
        
        self.style.configure("Secondary.TButton", 
                           background=self.colors['secondary'],
                           foreground="white",
                           borderwidth=0,
                           padding=8)
        self.style.map("Secondary.TButton", 
                      background=[('active', self._lighten_color(self.colors['secondary'], 10))])
        
        self.style.configure("Accent.TButton", 
                           background=self.colors['accent'],
                           foreground="white",
                           borderwidth=0,
                           padding=8)
        self.style.map("Accent.TButton", 
                      background=[('active', self._lighten_color(self.colors['accent'], 10))])
        
        # 输入框样式
        self.style.configure("Card.TEntry", 
                           fieldbackground=self.colors['surface'],
                           background=self.colors['surface'],
                           foreground=self.colors['text'],
                           borderwidth=1,
                           relief="solid",
                           padding=8)
        
        # 树视图样式
        self.style.configure("Card.Treeview", 
                           background=self.colors['surface'],
                           foreground=self.colors['text'],
                           fieldbackground=self.colors['surface'],
                           borderwidth=1,
                           relief="solid")
        self.style.configure("Card.Treeview.Heading", 
                           background=self.colors['background'],
                           foreground=self.colors['text'],
                           padding=10)
        self.style.map("Card.Treeview.Heading", 
                      background=[('active', self.colors['primary'])],
                      foreground=[('active', "white")])
        
        # 滚动条样式
        self.style.configure("Card.Vertical.TScrollbar", 
                           background=self.colors['border'],
                           troughcolor=self.colors['background'],
                           borderwidth=1)
    
    def _lighten_color(self, color, percent):
        """调亮颜色"""
        import re
        hex_color = color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        lightened_rgb = tuple(min(255, int(c + (255 - c) * percent / 100)) for c in rgb)
        return '#{:02x}{:02x}{:02x}'.format(*lightened_rgb)
    
    def create_widgets(self):
        """创建UI组件"""
        # 顶部标题
        title_frame = ttk.Frame(self.main_frame, style="MainFrame.TFrame")
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_label = ttk.Label(title_frame, text="文件整理", font=("Microsoft YaHei", 18, "bold"), foreground=self.colors['primary'])
        title_label.pack(anchor=tk.W)
        
        # 搜索框 - 放置在标题右侧
        search_frame = ttk.Frame(title_frame, style="MainFrame.TFrame")
        search_frame.pack(anchor=tk.E, pady=(0, 0))
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30, style="Card.TEntry")
        search_entry.pack(side=tk.LEFT, padx=5)
        
        search_btn = ttk.Button(search_frame, text="搜索", command=self.search_files, style="Primary.TButton")
        search_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ttk.Button(search_frame, text="清除", command=self.clear_search, style="Secondary.TButton")
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # 主内容区域 - 左右分栏
        content_frame = ttk.Frame(self.main_frame, style="MainFrame.TFrame")
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # 左侧功能区
        left_frame = ttk.Frame(content_frame, style="MainFrame.TFrame", width=380)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        left_frame.pack_propagate(False)  # 保持固定宽度
        
        # 目录设置区域
        dir_frame = ttk.LabelFrame(left_frame, text="目录设置", padding="15", style="Card.TLabelframe")
        dir_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 源目录选择
        source_frame = ttk.Frame(dir_frame, style="MainFrame.TFrame")
        source_frame.pack(fill=tk.X, pady=(0, 10))
        
        source_label = ttk.Label(source_frame, text="源目录:", foreground=self.colors['text'])
        source_label.pack(anchor=tk.W, pady=(0, 5))
        
        source_entry = ttk.Entry(source_frame, textvariable=self.source_dir, style="Card.TEntry")
        source_entry.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        # 源目录按钮
        source_btn_frame = ttk.Frame(source_frame, style="MainFrame.TFrame")
        source_btn_frame.pack(fill=tk.X, padx=5)
        
        scan_btn = ttk.Button(source_btn_frame, text="扫描", command=self.scan_files, style="Primary.TButton")
        scan_btn.pack(side=tk.RIGHT, padx=5)
        
        browse_btn = ttk.Button(source_btn_frame, text="浏览", command=self.select_source_dir, style="Secondary.TButton")
        browse_btn.pack(side=tk.RIGHT, padx=5)
        
        # 目标目录选择
        target_frame = ttk.Frame(dir_frame, style="MainFrame.TFrame")
        target_frame.pack(fill=tk.X, pady=(10, 0))
        
        target_label = ttk.Label(target_frame, text="目标目录:", foreground=self.colors['text'])
        target_label.pack(anchor=tk.W, pady=(0, 5))
        
        target_entry = ttk.Entry(target_frame, textvariable=self.target_dir, style="Card.TEntry")
        target_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        target_browse_btn = ttk.Button(target_frame, text="浏览", command=self.select_target_dir, style="Secondary.TButton")
        target_browse_btn.pack(side=tk.RIGHT, padx=5)
        
        # 标签管理
        tag_frame = ttk.LabelFrame(left_frame, text="标签管理", padding="15", style="Card.TLabelframe")
        tag_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.tag_var = tk.StringVar()
        tag_entry = ttk.Entry(tag_frame, textvariable=self.tag_var, style="Card.TEntry")
        tag_entry.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        # 标签按钮
        tag_btn_frame = ttk.Frame(tag_frame, style="MainFrame.TFrame")
        tag_btn_frame.pack(fill=tk.X, padx=5)
        
        add_tag_btn = ttk.Button(tag_btn_frame, text="添加标签", command=self.add_tag, style="Secondary.TButton")
        add_tag_btn.pack(side=tk.RIGHT, padx=5)
        
        remove_tag_btn = ttk.Button(tag_btn_frame, text="移除标签", command=self.remove_tag, style="Accent.TButton")
        remove_tag_btn.pack(side=tk.RIGHT, padx=5)
        
        # 按标签选择
        tag_select_frame = ttk.LabelFrame(left_frame, text="按标签选择", padding="15", style="Card.TLabelframe")
        tag_select_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 获取所有唯一标签
        unique_tags = list(set(self.tags.values()))
        
        # 标签选择列表
        self.tag_select_var = tk.StringVar()
        self.tag_select_combo = ttk.Combobox(tag_select_frame, textvariable=self.tag_select_var, values=unique_tags, state="readonly")
        self.tag_select_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # 选择按钮
        select_by_tag_btn = ttk.Button(tag_select_frame, text="选择", command=self.select_by_tag, style="Secondary.TButton")
        select_by_tag_btn.pack(side=tk.LEFT, padx=5)
        
        # 按文件类型选择
        type_select_frame = ttk.LabelFrame(left_frame, text="按文件类型选择", padding="15", style="Card.TLabelframe")
        type_select_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 获取所有唯一文件类型
        unique_extensions = set()
        for file_info in self.file_list:
            if 'extension' in file_info:
                unique_extensions.add(file_info['extension'])
        unique_extensions = sorted(list(unique_extensions))
        
        # 文件类型选择列表
        self.type_select_var = tk.StringVar()
        self.type_select_combo = ttk.Combobox(type_select_frame, textvariable=self.type_select_var, values=unique_extensions, state="readonly")
        self.type_select_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # 选择按钮
        select_by_type_btn = ttk.Button(type_select_frame, text="选择", command=self.select_by_type, style="Secondary.TButton")
        select_by_type_btn.pack(side=tk.LEFT, padx=5)
        
        # 操作按钮
        action_frame = ttk.LabelFrame(left_frame, text="操作", padding="15", style="Card.TLabelframe")
        action_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 第一行按钮
        action_row1 = ttk.Frame(action_frame, style="MainFrame.TFrame")
        action_row1.pack(fill=tk.X, pady=(0, 5))
        
        select_all_btn = ttk.Button(action_row1, text="全选", command=self.select_all, style="Secondary.TButton")
        select_all_btn.pack(side=tk.LEFT, padx=5)
        
        deselect_all_btn = ttk.Button(action_row1, text="取消全选", command=self.deselect_all, style="Secondary.TButton")
        deselect_all_btn.pack(side=tk.LEFT, padx=5)
        
        # 显示选择数量
        selection_count_label = ttk.Label(action_row1, textvariable=self.selection_count_var, foreground=self.colors['text'])
        selection_count_label.pack(side=tk.LEFT, padx=10)
        
        # 第二行按钮
        action_row2 = ttk.Frame(action_frame, style="MainFrame.TFrame")
        action_row2.pack(fill=tk.X)
        
        refresh_btn = ttk.Button(action_row2, text="刷新", command=self.refresh_list, style="Secondary.TButton")
        refresh_btn.pack(side=tk.RIGHT, padx=5)
        
        organize_btn = ttk.Button(action_row2, text="整理文件", command=self.organize_files, style="Primary.TButton")
        organize_btn.pack(side=tk.RIGHT, padx=5)
        
        # 右侧文件展示区
        right_frame = ttk.Frame(content_frame, style="MainFrame.TFrame")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 文件列表
        file_frame = ttk.LabelFrame(right_frame, text="文件列表", padding="15", style="Card.TLabelframe")
        file_frame.pack(fill=tk.BOTH, expand=True)
        
        # 文件列表树
        columns = ("name", "path", "type", "size", "modified", "tag")
        self.tree = ttk.Treeview(file_frame, columns=columns, show="headings", style="Card.Treeview")
        
        # 设置列标题
        self.tree.heading("name", text="文件名", anchor=tk.W)
        self.tree.heading("path", text="路径", anchor=tk.W)
        self.tree.heading("type", text="类型", anchor=tk.CENTER)
        self.tree.heading("size", text="大小", anchor=tk.CENTER)
        self.tree.heading("modified", text="修改时间", anchor=tk.CENTER)
        self.tree.heading("tag", text="标签", anchor=tk.CENTER)
        
        # 设置列宽
        self.tree.column("name", width=180, minwidth=100)
        self.tree.column("path", width=350, minwidth=200)
        self.tree.column("type", width=100, minwidth=80, anchor=tk.CENTER)
        self.tree.column("size", width=100, minwidth=80, anchor=tk.CENTER)
        self.tree.column("modified", width=140, minwidth=120, anchor=tk.CENTER)
        self.tree.column("tag", width=100, minwidth=80, anchor=tk.CENTER)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(file_frame, orient=tk.VERTICAL, command=self.tree.yview, style="Card.Vertical.TScrollbar")
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 添加水平滚动条
        hscrollbar = ttk.Scrollbar(file_frame, orient=tk.HORIZONTAL, command=self.tree.xview, style="Card.Vertical.TScrollbar")
        self.tree.configure(xscroll=hscrollbar.set)
        hscrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 添加事件处理
        self.tree.bind('<Button-1>', self.on_tree_click, add='+')
        self.tree.bind('<Control-Button-1>', self.on_ctrl_click, add='+')
        self.tree.bind('<Shift-Button-1>', self.on_shift_click, add='+')
        self.tree.bind('<<TreeviewSelect>>', self.update_selection_count, add='+')
        
        # 添加右键菜单事件
        self.tree.bind('<Button-3>', self.on_tree_right_click)
        
        # 添加键盘事件
        self.tree.bind('<KeyPress-space>', self.on_space_press)
        self.tree.bind('<KeyPress-Return>', self.on_enter_press)
        self.tree.bind('<Control-a>', self.on_ctrl_a)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
    
    def select_source_dir(self):
        """选择源目录"""
        dir_path = filedialog.askdirectory(title="选择要扫描的目录")
        if dir_path:
            self.source_dir.set(dir_path)
    
    def select_target_dir(self):
        """选择目标目录"""
        dir_path = filedialog.askdirectory(title="选择整理目标目录")
        if dir_path:
            self.target_dir.set(dir_path)
    
    def scan_files(self):
        """扫描文件"""
        source_dir = self.source_dir.get()
        if not source_dir:
            messagebox.showerror("错误", "请先选择源目录")
            return
        
        if not os.path.exists(source_dir):
            messagebox.showerror("错误", "源目录不存在")
            return
        
        # 清空现有列表
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 扫描文件
        scanner = FileScanner()
        self.file_list = scanner.scan_directory(source_dir)
        self.filtered_file_list = self.file_list.copy()  # 初始化过滤列表
        
        # 显示文件列表
        self._display_files(self.filtered_file_list)
        
        messagebox.showinfo("完成", f"共扫描到 {len(self.file_list)} 个文件")
    
    def _display_files(self, files):
        """显示文件列表"""
        # 保存当前选择的文件路径
        selected_paths = []
        for item in self.tree.selection():
            values = self.tree.item(item, "values")
            if values:
                selected_paths.append(values[1])  # 路径现在是第二列
        
        # 清空现有列表
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 显示文件并恢复选择
        for file_info in files:
            tag = self.tags.get(file_info['path'], "")
            # 检查文件是否被选中
            is_selected = file_info['path'] in selected_paths
            # 获取文件类型（扩展名）
            file_type = file_info.get('extension', '')
            item = self.tree.insert("", tk.END, values=(
                file_info['name'],
                file_info['path'],
                file_type,
                file_info['size'],
                file_info['modified'],
                tag
            ))
            # 恢复选择状态
            if is_selected:
                self.tree.selection_add(item)
        
        # 更新选择数量
        self.update_selection_count()
        
        # 更新文件类型选择列表
        self._update_type_select_list()
    
    def search_files(self):
        """搜索文件"""
        search_term = self.search_var.get().strip().lower()
        if not search_term:
            messagebox.showinfo("提示", "请输入搜索关键词")
            return
        
        if not self.file_list:
            messagebox.showinfo("提示", "请先扫描文件")
            return
        
        # 执行搜索
        self.filtered_file_list = []
        for file_info in self.file_list:
            # 搜索文件名
            if search_term in file_info['name'].lower():
                self.filtered_file_list.append(file_info)
            # 搜索文件路径
            elif search_term in file_info['path'].lower():
                self.filtered_file_list.append(file_info)
            # 搜索文件类型（扩展名）
            elif search_term in file_info['extension'].lower():
                self.filtered_file_list.append(file_info)
            # 搜索标签
            elif search_term in self.tags.get(file_info['path'], "").lower():
                self.filtered_file_list.append(file_info)
        
        # 显示搜索结果
        self._display_files(self.filtered_file_list)
        messagebox.showinfo("搜索完成", f"找到 {len(self.filtered_file_list)} 个匹配的文件")
    
    def clear_search(self):
        """清除搜索"""
        self.search_var.set("")
        self.filtered_file_list = self.file_list.copy()
        self._display_files(self.filtered_file_list)
    
    def add_tag(self):
        """添加标签"""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showerror("错误", "请先选择要添加标签的文件")
            return
        
        tag = self.tag_var.get().strip()
        if not tag:
            messagebox.showerror("错误", "请输入标签名称")
            return
        
        for item in selected_items:
            values = list(self.tree.item(item, "values"))
            file_path = values[1]  # 路径现在是第二列
            self.tags[file_path] = tag
            # 更新树视图
            values[5] = tag  # 标签现在是第六列
            self.tree.item(item, values=values)
        
        # 更新标签选择列表
        self._update_tag_select_list()
        
        messagebox.showinfo("完成", f"已为 {len(selected_items)} 个文件添加标签: {tag}")
    
    def remove_tag(self):
        """移除标签"""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showerror("错误", "请先选择要移除标签的文件")
            return
        
        for item in selected_items:
            values = list(self.tree.item(item, "values"))
            file_path = values[1]  # 路径现在是第二列
            if file_path in self.tags:
                del self.tags[file_path]
                # 更新树视图
                values[5] = ""  # 标签现在是第六列
                self.tree.item(item, values=values)
        
        # 更新标签选择列表
        self._update_tag_select_list()
        
        messagebox.showinfo("完成", f"已为 {len(selected_items)} 个文件移除标签")
    
    def select_all(self):
        """全选文件"""
        # 全选所有项
        items = self.tree.get_children()
        self.tree.selection_set(items)
        
        # 更新选择数量
        self.update_selection_count()
    
    def deselect_all(self):
        """取消全选"""
        # 取消选择所有项
        items = self.tree.selection()
        self.tree.selection_remove(items)
        
        # 更新选择数量
        self.update_selection_count()
    
    def on_tree_right_click(self, event):
        """处理树视图右键点击事件"""
        # 获取点击的项和列
        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        
        if not item:
            return
        
        # 只在类型列显示右键菜单
        if column == '#4':  # 类型列
            # 获取文件类型
            values = self.tree.item(item, "values")
            if values and len(values) > 3:
                file_type = values[3]
                
                # 创建右键菜单
                self.context_menu = tk.Menu(self.tree, tearoff=0)
                self.context_menu.add_command(label=f"选择所有 {file_type} 类型文件", 
                                             command=lambda: self.select_files_by_type(file_type))
                
                # 显示菜单
                self.context_menu.post(event.x_root, event.y_root)
    
    def select_files_by_type(self, file_type):
        """选择所有指定类型的文件"""
        # 选择所有具有该类型的文件
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            if values and len(values) > 3:
                item_type = values[3]
                if item_type == file_type:
                    self.tree.selection_add(item)
                    # 更新复选框为选中
                    values[0] = "☑"
                    self.tree.item(item, values=values)
        
        # 更新选择数量
        self.update_selection_count()
    
    def organize_files(self):
        """整理文件"""
        target_dir = self.target_dir.get()
        if not target_dir:
            messagebox.showerror("错误", "请先选择目标目录")
            return
        
        if not os.path.exists(target_dir):
            messagebox.showerror("错误", "目标目录不存在")
            return
        
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showerror("错误", "请先选择要整理的文件")
            return
        
        # 收集要整理的文件
        files_to_organize = []
        for item in selected_items:
            values = self.tree.item(item, "values")
            file_path = values[1]  # 路径现在是第二列
            tag = self.tags.get(file_path, "未分类")
            files_to_organize.append((file_path, tag))
        
        # 执行整理
        organizer = FileOrganizer()
        result = organizer.organize_files(files_to_organize, target_dir)
        
        messagebox.showinfo("完成", f"成功整理 {result['success']} 个文件，失败 {result['failed']} 个文件")
        
        # 刷新列表
        self.refresh_list()
    
    def refresh_list(self):
        """刷新文件列表"""
        source_dir = self.source_dir.get()
        if source_dir:
            # 重新扫描文件
            scanner = FileScanner()
            self.file_list = scanner.scan_directory(source_dir)
            
            # 检查是否有搜索关键词
            search_term = self.search_var.get().strip().lower()
            if search_term:
                # 重新执行搜索
                self.filtered_file_list = []
                for file_info in self.file_list:
                    if (search_term in file_info['name'].lower() or
                        search_term in file_info['path'].lower() or
                        search_term in file_info['extension'].lower() or
                        search_term in self.tags.get(file_info['path'], "").lower()):
                        self.filtered_file_list.append(file_info)
            else:
                # 没有搜索，显示所有文件
                self.filtered_file_list = self.file_list.copy()
            
            # 显示文件列表
            self._display_files(self.filtered_file_list)
    

    
    def on_tree_click(self, event):
        """处理树视图点击事件"""
        
        
        # 获取点击的项
        item = self.tree.identify_row(event.y)
        if not item:
            return
        
        # 检查是否按下了Ctrl或Shift键
        if event.state & 0x4:  # Ctrl键
            return  # 让on_ctrl_click处理
        elif event.state & 0x1:  # Shift键
            return  # 让on_shift_click处理
        
        # 普通点击，替换选择
        self.tree.selection_set(item)
        
        # 更新最后选中的项
        self.last_selected_item = item
        
        # 更新选择数量
        self.update_selection_count()
    
    def on_ctrl_click(self, event):
        """处理Ctrl+点击事件（多选）"""
        
        
        # 获取点击的项
        item = self.tree.identify_row(event.y)
        if not item:
            return "break"
        
        # 切换选择状态，不取消其他选择
        if item in self.tree.selection():
            self.tree.selection_remove(item)
        else:
            self.tree.selection_add(item)
        
        # 更新最后选中的项
        self.last_selected_item = item
        
        # 更新选择数量
        self.update_selection_count()
        
        # 阻止事件传播
        return "break"
    
    def on_shift_click(self, event):
        """处理Shift+点击事件（范围选择）"""
        
        
        # 获取点击的项
        item = self.tree.identify_row(event.y)
        if not item or not self.last_selected_item:
            return "break"
        
        # 获取所有项
        items = self.tree.get_children()
        if not items:
            return "break"
        
        # 找到两个项的索引
        try:
            last_idx = items.index(self.last_selected_item)
            current_idx = items.index(item)
        except ValueError:
            return "break"
        
        # 确定选择范围
        start_idx = min(last_idx, current_idx)
        end_idx = max(last_idx, current_idx)
        
        # 选择范围内的所有项
        range_items = items[start_idx:end_idx+1]
        
        # 检查是否同时按下了Ctrl键
        if event.state & 0x4:  # Ctrl+Shift
            # 添加范围到现有选择
            for range_item in range_items:
                if range_item not in self.tree.selection():
                    self.tree.selection_add(range_item)
        else:  # 只按了Shift
            # 替换选择为范围
            self.tree.selection_set(range_items)
        
        # 更新最后选中的项
        self.last_selected_item = item
        
        # 更新选择数量
        self.update_selection_count()
        
        # 阻止事件传播
        return "break"
    
    def update_selection_count(self, event=None):
        """更新选择数量显示"""
        count = len(self.tree.selection())
        self.selection_count_var.set(f"已选择: {count} 个文件")
    
    def on_space_press(self, event):
        """处理空格键事件（选择/取消选择当前项）"""
        
        
        selected_items = self.tree.selection()
        if selected_items:
            current_item = selected_items[-1]  # 最后选中的项作为当前项
            if current_item in self.tree.selection():
                self.tree.selection_remove(current_item)
            else:
                self.tree.selection_add(current_item)
    
    def on_enter_press(self, event):
        """处理回车键事件（选择/取消选择当前项）"""
        self.on_space_press(event)
    
    def on_ctrl_a(self, event):
        """处理Ctrl+A事件（全选）"""
        self.select_all()
    
    def select_by_tag(self):
        """按标签选择文件"""
        
        
        # 获取选中的标签
        selected_tag = self.tag_select_var.get()
        if not selected_tag:
            return
        
        # 选择所有具有该标签的文件
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            if values and len(values) > 5:
                file_path = values[1]
                file_tag = self.tags.get(file_path, "")
                if file_tag == selected_tag:
                    self.tree.selection_add(item)
        
        # 更新选择数量
        self.update_selection_count()
    
    def _update_tag_select_list(self):
        """更新标签选择列表"""
        # 获取所有唯一标签
        unique_tags = list(set(self.tags.values()))
        
        # 更新标签选择下拉框
        if hasattr(self, 'tag_select_combo'):
            # 清空并重新填充下拉框
            self.tag_select_combo.destroy()
            self.tag_select_combo = ttk.Combobox(self.tag_select_combo.master, textvariable=self.tag_select_var, values=unique_tags, state="readonly")
            self.tag_select_combo.pack(side=tk.LEFT, padx=5)
    
    def select_by_type(self):
        """按文件类型选择文件"""
        
        
        # 获取选中的文件类型
        selected_type = self.type_select_var.get()
        if not selected_type:
            return
        
        # 选择所有具有该文件类型的文件
        for item in self.tree.get_children():
            values = list(self.tree.item(item, "values"))
            if values and len(values) > 5:
                file_type = values[2]  # 类型现在是第三列
                if file_type == selected_type:
                    self.tree.selection_add(item)
        
        # 更新选择数量
        self.update_selection_count()
    
    def _update_type_select_list(self):
        """更新文件类型选择列表"""
        # 获取所有唯一文件类型
        unique_extensions = set()
        for file_info in self.file_list:
            if 'extension' in file_info:
                unique_extensions.add(file_info['extension'])
        unique_extensions = sorted(list(unique_extensions))
        
        # 更新文件类型选择下拉框
        if hasattr(self, 'type_select_combo'):
            # 清空并重新填充下拉框
            self.type_select_combo.destroy()
            self.type_select_combo = ttk.Combobox(self.type_select_combo.master, textvariable=self.type_select_var, values=unique_extensions, state="readonly")
            self.type_select_combo.pack(side=tk.LEFT, padx=5)
