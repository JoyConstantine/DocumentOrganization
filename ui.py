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
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(title_frame, text="文件整理工具", font=("Microsoft YaHei", 20, "bold"), foreground=self.colors['primary'])
        title_label.pack(anchor=tk.W)
        
        subtitle_label = ttk.Label(title_frame, text="快速整理和分类您的文件", font=("Microsoft YaHei", 12), foreground=self.colors['text_light'])
        subtitle_label.pack(anchor=tk.W, pady=(5, 0))
        
        # 搜索功能
        search_frame = ttk.Frame(title_frame, style="MainFrame.TFrame")
        search_frame.pack(anchor=tk.E, pady=(10, 0))
        
        search_label = ttk.Label(search_frame, text="搜索:", foreground=self.colors['text'])
        search_label.pack(side=tk.LEFT, padx=5)
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30, style="Card.TEntry")
        search_entry.pack(side=tk.LEFT, padx=5)
        
        search_btn = ttk.Button(search_frame, text="搜索", command=self.search_files, style="Primary.TButton")
        search_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ttk.Button(search_frame, text="清除", command=self.clear_search, style="Secondary.TButton")
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # 目录设置区域
        dir_frame = ttk.Frame(self.main_frame, style="MainFrame.TFrame")
        dir_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 源目录选择
        source_frame = ttk.LabelFrame(dir_frame, text="源目录", padding="15", style="Card.TLabelframe")
        source_frame.pack(fill=tk.X, pady=(0, 10))
        
        source_entry = ttk.Entry(source_frame, textvariable=self.source_dir, style="Card.TEntry")
        source_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        browse_btn = ttk.Button(source_frame, text="浏览", command=self.select_source_dir, style="Secondary.TButton")
        browse_btn.pack(side=tk.RIGHT, padx=5)
        
        scan_btn = ttk.Button(source_frame, text="扫描", command=self.scan_files, style="Primary.TButton")
        scan_btn.pack(side=tk.RIGHT, padx=5)
        
        # 目标目录选择
        target_frame = ttk.LabelFrame(dir_frame, text="目标目录", padding="15", style="Card.TLabelframe")
        target_frame.pack(fill=tk.X, pady=(10, 0))
        
        target_entry = ttk.Entry(target_frame, textvariable=self.target_dir, style="Card.TEntry")
        target_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        target_browse_btn = ttk.Button(target_frame, text="浏览", command=self.select_target_dir, style="Secondary.TButton")
        target_browse_btn.pack(side=tk.RIGHT, padx=5)
        
        # 中间内容区域
        content_frame = ttk.Frame(self.main_frame, style="MainFrame.TFrame")
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # 文件列表
        file_frame = ttk.LabelFrame(content_frame, text="文件列表", padding="15", style="Card.TLabelframe")
        file_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # 文件列表树
        columns = ("name", "path", "size", "modified", "tag")
        self.tree = ttk.Treeview(file_frame, columns=columns, show="headings", style="Card.Treeview")
        
        # 设置列标题
        self.tree.heading("name", text="文件名", anchor=tk.W)
        self.tree.heading("path", text="路径", anchor=tk.W)
        self.tree.heading("size", text="大小", anchor=tk.CENTER)
        self.tree.heading("modified", text="修改时间", anchor=tk.CENTER)
        self.tree.heading("tag", text="标签", anchor=tk.CENTER)
        
        # 设置列宽
        self.tree.column("name", width=180, minwidth=100)
        self.tree.column("path", width=350, minwidth=200)
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
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # 底部操作区域
        bottom_frame = ttk.Frame(self.main_frame, style="MainFrame.TFrame")
        bottom_frame.pack(fill=tk.X)
        
        # 标签管理
        tag_frame = ttk.LabelFrame(bottom_frame, text="标签管理", padding="15", style="Card.TLabelframe")
        tag_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.tag_var = tk.StringVar()
        tag_entry = ttk.Entry(tag_frame, textvariable=self.tag_var, width=40, style="Card.TEntry")
        tag_entry.pack(side=tk.LEFT, padx=5)
        
        add_tag_btn = ttk.Button(tag_frame, text="添加标签", command=self.add_tag, style="Secondary.TButton")
        add_tag_btn.pack(side=tk.LEFT, padx=5)
        
        remove_tag_btn = ttk.Button(tag_frame, text="移除标签", command=self.remove_tag, style="Accent.TButton")
        remove_tag_btn.pack(side=tk.LEFT, padx=5)
        
        # 操作按钮
        action_frame = ttk.Frame(bottom_frame, style="MainFrame.TFrame")
        action_frame.pack(fill=tk.X)
        
        select_all_btn = ttk.Button(action_frame, text="全选", command=self.select_all, style="Secondary.TButton")
        select_all_btn.pack(side=tk.LEFT, padx=5)
        
        deselect_all_btn = ttk.Button(action_frame, text="取消全选", command=self.deselect_all, style="Secondary.TButton")
        deselect_all_btn.pack(side=tk.LEFT, padx=5)
        
        refresh_btn = ttk.Button(action_frame, text="刷新", command=self.refresh_list, style="Secondary.TButton")
        refresh_btn.pack(side=tk.RIGHT, padx=5)
        
        organize_btn = ttk.Button(action_frame, text="整理文件", command=self.organize_files, style="Primary.TButton")
        organize_btn.pack(side=tk.RIGHT, padx=5)
    
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
        # 清空现有列表
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 显示文件
        for file_info in files:
            tag = self.tags.get(file_info['path'], "")
            self.tree.insert("", tk.END, values=(
                file_info['name'],
                file_info['path'],
                file_info['size'],
                file_info['modified'],
                tag
            ))
    
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
            values = self.tree.item(item, "values")
            file_path = values[1]
            self.tags[file_path] = tag
            # 更新树视图
            self.tree.item(item, values=(values[0], values[1], values[2], values[3], tag))
        
        messagebox.showinfo("完成", f"已为 {len(selected_items)} 个文件添加标签: {tag}")
    
    def remove_tag(self):
        """移除标签"""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showerror("错误", "请先选择要移除标签的文件")
            return
        
        for item in selected_items:
            values = self.tree.item(item, "values")
            file_path = values[1]
            if file_path in self.tags:
                del self.tags[file_path]
                # 更新树视图
                self.tree.item(item, values=(values[0], values[1], values[2], values[3], ""))
        
        messagebox.showinfo("完成", f"已为 {len(selected_items)} 个文件移除标签")
    
    def select_all(self):
        """全选文件"""
        self.tree.selection_set(self.tree.get_children())
    
    def deselect_all(self):
        """取消全选"""
        self.tree.selection_remove(self.tree.selection())
    
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
            file_path = values[1]
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
