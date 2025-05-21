"""
文件操作命令

提供文件操作相关的命令，如创建文件、列出文件等。
"""

import os
import shutil
from pathlib import Path
import re
from commands.base_command import BaseCommand

class CreateFileCommand(BaseCommand):
    """创建文件命令"""
    
    def __init__(self):
        super().__init__()
        self.name = "创建文件"
        # 此命令不需要确认
        self.require_confirmation = False
    
    def execute(self, command_text):
        """
        执行创建文件操作
        
        参数:
            command_text (str): 命令文本
            
        返回:
            str: 执行结果
        """
        # 从命令文本中提取文件名
        pattern = re.compile(r'(?:创建|新建|添加|生成)(?:文件|档案)\s*(.+)')
        match = pattern.search(command_text)
        
        if not match:
            return "未能识别文件名。请使用格式：创建文件 文件名"
        
        filename = match.group(1).strip()
        if not filename:
            return "请指定文件名"
        
        try:
            # 创建文件
            with open(filename, 'w', encoding='utf-8') as f:
                pass
            return f"已创建文件: {os.path.abspath(filename)}"
        except Exception as e:
            return f"创建文件失败: {str(e)}"
    
    def undo(self, command_text):
        """
        撤销创建文件操作
        
        参数:
            command_text (str): 命令文本
            
        返回:
            str: 撤销结果
        """
        pattern = re.compile(r'(?:创建|新建|添加|生成)(?:文件|档案)\s*(.+)')
        match = pattern.search(command_text)
        
        if not match:
            return "无法确定要删除的文件"
        
        filename = match.group(1).strip()
        
        try:
            # 检查文件是否存在
            if os.path.exists(filename):
                # 删除文件
                os.remove(filename)
                return f"已删除文件: {filename}"
            else:
                return f"文件不存在: {filename}"
        except Exception as e:
            return f"删除文件失败: {str(e)}"


class ListFilesCommand(BaseCommand):
    """列出文件命令"""
    
    def __init__(self):
        super().__init__()
        self.name = "列出文件"
        self.require_confirmation = False
    
    def execute(self, command_text):
        """
        执行列出文件操作
        
        参数:
            command_text (str): 命令文本
            
        返回:
            str: 执行结果
        """
        # 从命令文本中提取目录
        directory = "."  # 默认当前目录
        
        pattern = re.compile(r'(?:列出|显示|查看)(?:文件|目录|文件夹)\s*(.+)?')
        match = pattern.search(command_text)
        
        if match and match.group(1):
            dir_name = match.group(1).strip()
            if dir_name:
                directory = dir_name
        
        try:
            # 检查目录是否存在
            if not os.path.exists(directory):
                return f"目录不存在: {directory}"
            
            if not os.path.isdir(directory):
                return f"{directory} 不是一个目录"
            
            # 列出文件
            files = os.listdir(directory)
            
            # 格式化输出
            if not files:
                return f"目录 {directory} 为空"
            
            # 获取文件类型
            file_list = []
            for f in files:
                full_path = os.path.join(directory, f)
                if os.path.isdir(full_path):
                    file_list.append(f"{f}/")
                else:
                    file_list.append(f)
            
            return f"目录 {os.path.abspath(directory)} 中的文件:\n" + "\n".join(file_list)
        except Exception as e:
            return f"列出文件失败: {str(e)}"


class DeleteFileCommand(BaseCommand):
    """删除文件命令"""
    
    def __init__(self):
        super().__init__()
        self.name = "删除文件"
        # 需要确认，因为是危险操作
        self.require_confirmation = True
        self.deleted_files = {}  # 存储已删除的文件，用于撤销
    
    def execute(self, command_text):
        """
        执行删除文件操作
        
        参数:
            command_text (str): 命令文本
            
        返回:
            str: 执行结果
        """
        # 从命令文本中提取文件名
        pattern = re.compile(r'(?:删除|移除|清除)(?:文件|档案)\s*(.+)')
        match = pattern.search(command_text)
        
        if not match:
            return "未能识别文件名。请使用格式：删除文件 文件名"
        
        filename = match.group(1).strip()
        if not filename:
            return "请指定文件名"
        
        try:
            # 检查文件是否存在
            if not os.path.exists(filename):
                return f"文件不存在: {filename}"
            
            # 备份文件内容（用于可能的撤销操作）
            temp_backup = None
            if os.path.isfile(filename):
                try:
                    with open(filename, 'rb') as f:
                        content = f.read()
                    temp_backup = filename + ".bak"
                    with open(temp_backup, 'wb') as f:
                        f.write(content)
                except Exception as e:
                    # 备份失败，但不妨碍删除操作
                    print(f"备份文件失败: {str(e)}")
            
            # 删除文件或目录
            if os.path.isdir(filename):
                shutil.rmtree(filename)
                result = f"已删除目录: {filename}"
            else:
                os.remove(filename)
                result = f"已删除文件: {filename}"
            
            # 记录删除的文件信息，用于撤销
            self.deleted_files[filename] = temp_backup
            
            return result
        except Exception as e:
            return f"删除文件失败: {str(e)}"
    
    def undo(self, command_text):
        """
        撤销删除文件操作
        
        参数:
            command_text (str): 命令文本
            
        返回:
            str: 撤销结果
        """
        pattern = re.compile(r'(?:删除|移除|清除)(?:文件|档案)\s*(.+)')
        match = pattern.search(command_text)
        
        if not match:
            return "无法确定要恢复的文件"
        
        filename = match.group(1).strip()
        
        # 检查是否有备份
        if filename not in self.deleted_files:
            return f"找不到 {filename} 的备份"
        
        backup_file = self.deleted_files[filename]
        
        try:
            if backup_file and os.path.exists(backup_file):
                # 恢复文件
                with open(backup_file, 'rb') as f:
                    content = f.read()
                with open(filename, 'wb') as f:
                    f.write(content)
                    
                # 删除备份
                os.remove(backup_file)
                
                # 从记录中移除
                del self.deleted_files[filename]
                
                return f"已恢复文件: {filename}"
            else:
                return f"找不到 {filename} 的备份文件"
        except Exception as e:
            return f"恢复文件失败: {str(e)}"
    
    def get_confirmation_details(self, command_text):
        """
        获取确认详情
        
        参数:
            command_text (str): 命令文本
            
        返回:
            str: 确认详情
        """
        pattern = re.compile(r'(?:删除|移除|清除)(?:文件|档案)\s*(.+)')
        match = pattern.search(command_text)
        
        if not match:
            return "未能识别要删除的文件"
        
        filename = match.group(1).strip()
        
        if os.path.exists(filename):
            if os.path.isdir(filename):
                return f"您确定要删除目录 {filename} 吗？此操作不可逆。"
            else:
                return f"您确定要删除文件 {filename} 吗？"
        else:
            return f"文件 {filename} 不存在" 