#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件扫描模块
"""

import os
import time


class FileScanner:
    """文件扫描器类"""
    
    def scan_directory(self, directory, recursive=True):
        """
        扫描目录下的所有文件
        
        Args:
            directory: 要扫描的目录路径
            recursive: 是否递归扫描子目录
            
        Returns:
            list: 文件信息列表
        """
        file_list = []
        
        try:
            if recursive:
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        file_path = os.path.join(root, file)
                        file_info = self._get_file_info(file_path)
                        if file_info:
                            file_list.append(file_info)
            else:
                for item in os.listdir(directory):
                    item_path = os.path.join(directory, item)
                    if os.path.isfile(item_path):
                        file_info = self._get_file_info(item_path)
                        if file_info:
                            file_list.append(file_info)
        except Exception as e:
            print(f"扫描目录时出错: {e}")
        
        return file_list
    
    def _get_file_info(self, file_path):
        """
        获取文件信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            dict: 文件信息字典
        """
        try:
            stat_info = os.stat(file_path)
            
            # 获取文件大小（格式化）
            size = stat_info.st_size
            formatted_size = self._format_size(size)
            
            # 获取修改时间
            modified_time = stat_info.st_mtime
            formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(modified_time))
            
            # 获取文件名和扩展名
            file_name = os.path.basename(file_path)
            file_ext = os.path.splitext(file_name)[1].lower()
            
            return {
                'name': file_name,
                'path': file_path,
                'size': formatted_size,
                'size_bytes': size,
                'modified': formatted_time,
                'modified_timestamp': modified_time,
                'extension': file_ext
            }
        except Exception as e:
            print(f"获取文件信息时出错 {file_path}: {e}")
            return None
    
    def _format_size(self, size):
        """
        格式化文件大小
        
        Args:
            size: 文件大小（字节）
            
        Returns:
            str: 格式化后的文件大小
        """
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        unit_index = 0
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        if unit_index == 0:
            return f"{size} {units[unit_index]}"
        else:
            return f"{size:.2f} {units[unit_index]}"
    
    def scan_by_extension(self, directory, extensions):
        """
        按扩展名扫描文件
        
        Args:
            directory: 要扫描的目录路径
            extensions: 扩展名列表，如 ['.txt', '.doc']
            
        Returns:
            list: 符合条件的文件信息列表
        """
        all_files = self.scan_directory(directory)
        
        # 转换扩展名为小写
        extensions = [ext.lower() for ext in extensions]
        
        # 过滤文件
        filtered_files = [
            file_info for file_info in all_files 
            if file_info['extension'] in extensions
        ]
        
        return filtered_files
    
    def scan_by_size(self, directory, min_size=None, max_size=None):
        """
        按文件大小扫描文件
        
        Args:
            directory: 要扫描的目录路径
            min_size: 最小文件大小（字节）
            max_size: 最大文件大小（字节）
            
        Returns:
            list: 符合条件的文件信息列表
        """
        all_files = self.scan_directory(directory)
        filtered_files = []
        
        for file_info in all_files:
            size = file_info['size_bytes']
            
            # 检查最小大小
            if min_size is not None and size < min_size:
                continue
            
            # 检查最大大小
            if max_size is not None and size > max_size:
                continue
            
            filtered_files.append(file_info)
        
        return filtered_files
    
    def scan_by_date(self, directory, start_date=None, end_date=None):
        """
        按修改日期扫描文件
        
        Args:
            directory: 要扫描的目录路径
            start_date: 开始日期（时间戳）
            end_date: 结束日期（时间戳）
            
        Returns:
            list: 符合条件的文件信息列表
        """
        all_files = self.scan_directory(directory)
        filtered_files = []
        
        for file_info in all_files:
            modified_time = file_info['modified_timestamp']
            
            # 检查开始日期
            if start_date is not None and modified_time < start_date:
                continue
            
            # 检查结束日期
            if end_date is not None and modified_time > end_date:
                continue
            
            filtered_files.append(file_info)
        
        return filtered_files
