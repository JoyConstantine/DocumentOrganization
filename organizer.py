#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件整理模块
"""

import os
import shutil
import uuid


class FileOrganizer:
    """文件整理器类"""
    
    def organize_files(self, files_to_organize, target_directory):
        """
        整理文件到目标目录
        
        Args:
            files_to_organize: 要整理的文件列表，每个元素是 (file_path, tag) 元组
            target_directory: 目标目录路径
            
        Returns:
            dict: 整理结果，包含成功和失败的文件数量
        """
        success_count = 0
        failed_count = 0
        failed_files = []
        
        for file_path, tag in files_to_organize:
            try:
                # 确保目标目录存在
                self._ensure_directory_exists(target_directory)
                
                # 创建标签子目录
                tag_directory = os.path.join(target_directory, tag)
                self._ensure_directory_exists(tag_directory)
                
                # 移动文件
                self._move_file(file_path, tag_directory)
                success_count += 1
            except Exception as e:
                print(f"整理文件时出错 {file_path}: {e}")
                failed_count += 1
                failed_files.append((file_path, str(e)))
        
        return {
            'success': success_count,
            'failed': failed_count,
            'failed_files': failed_files
        }
    
    def _ensure_directory_exists(self, directory):
        """
        确保目录存在，如果不存在则创建
        
        Args:
            directory: 目录路径
        """
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
    
    def _move_file(self, source_path, target_directory):
        """
        移动文件到目标目录
        
        Args:
            source_path: 源文件路径
            target_directory: 目标目录路径
        """
        # 获取文件名
        file_name = os.path.basename(source_path)
        
        # 构建目标文件路径
        target_path = os.path.join(target_directory, file_name)
        
        # 处理文件名冲突
        if os.path.exists(target_path):
            # 生成唯一文件名
            unique_name = self._generate_unique_filename(file_name)
            target_path = os.path.join(target_directory, unique_name)
        
        # 移动文件
        shutil.move(source_path, target_path)
    
    def _generate_unique_filename(self, original_filename):
        """
        生成唯一文件名
        
        Args:
            original_filename: 原始文件名
            
        Returns:
            str: 唯一文件名
        """
        # 获取文件名和扩展名
        base_name, ext = os.path.splitext(original_filename)
        
        # 生成唯一标识符
        unique_id = str(uuid.uuid4())[:8]
        
        # 构建唯一文件名
        unique_filename = f"{base_name}_{unique_id}{ext}"
        
        return unique_filename
    
    def organize_by_extension(self, directory, target_directory):
        """
        按文件扩展名整理文件
        
        Args:
            directory: 源目录路径
            target_directory: 目标目录路径
            
        Returns:
            dict: 整理结果
        """
        from scanner import FileScanner
        
        scanner = FileScanner()
        files = scanner.scan_directory(directory)
        
        files_to_organize = []
        for file_info in files:
            # 使用扩展名作为标签
            extension = file_info['extension']
            if extension:
                # 移除点号
                tag = extension[1:]
            else:
                tag = '无扩展名'
            
            files_to_organize.append((file_info['path'], tag))
        
        return self.organize_files(files_to_organize, target_directory)
    
    def organize_by_size(self, directory, target_directory):
        """
        按文件大小整理文件
        
        Args:
            directory: 源目录路径
            target_directory: 目标目录路径
            
        Returns:
            dict: 整理结果
        """
        from scanner import FileScanner
        
        scanner = FileScanner()
        files = scanner.scan_directory(directory)
        
        files_to_organize = []
        for file_info in files:
            # 根据文件大小分类
            size = file_info['size_bytes']
            
            if size < 1024:
                tag = '小于1KB'
            elif size < 1024 * 1024:
                tag = '1KB-1MB'
            elif size < 1024 * 1024 * 10:
                tag = '1MB-10MB'
            elif size < 1024 * 1024 * 100:
                tag = '10MB-100MB'
            else:
                tag = '大于100MB'
            
            files_to_organize.append((file_info['path'], tag))
        
        return self.organize_files(files_to_organize, target_directory)
    
    def organize_by_date(self, directory, target_directory):
        """
        按文件修改日期整理文件
        
        Args:
            directory: 源目录路径
            target_directory: 目标目录路径
            
        Returns:
            dict: 整理结果
        """
        from scanner import FileScanner
        import time
        
        scanner = FileScanner()
        files = scanner.scan_directory(directory)
        
        files_to_organize = []
        for file_info in files:
            # 使用修改日期作为标签（格式：YYYY-MM-DD）
            modified_time = file_info['modified_timestamp']
            date_tag = time.strftime('%Y-%m-%d', time.localtime(modified_time))
            
            files_to_organize.append((file_info['path'], date_tag))
        
        return self.organize_files(files_to_organize, target_directory)
