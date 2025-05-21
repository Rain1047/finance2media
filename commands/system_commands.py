"""
系统操作命令

提供系统操作相关的命令，如获取系统信息、执行Shell命令等。
"""

import os
import platform
import subprocess
import re
import time
from commands.base_command import BaseCommand

class SystemInfoCommand(BaseCommand):
    """获取系统信息命令"""
    
    def __init__(self):
        super().__init__()
        self.name = "系统信息"
        self.require_confirmation = False
    
    def execute(self, command_text):
        """
        执行获取系统信息操作
        
        参数:
            command_text (str): 命令文本
            
        返回:
            str: 执行结果
        """
        # 收集系统信息
        system_info = {
            "操作系统": platform.system(),
            "系统版本": platform.version(),
            "系统发行版": platform.release(),
            "处理器": platform.processor(),
            "架构": platform.architecture()[0],
            "Python版本": platform.python_version(),
            "主机名": platform.node(),
            "当前时间": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }
        
        # 检查是否要获取特定信息
        if "处理器" in command_text.lower() or "cpu" in command_text.lower():
            return f"处理器信息: {system_info['处理器']}"
        
        elif "内存" in command_text.lower() or "ram" in command_text.lower():
            # 获取内存信息，这需要平台特定的实现
            if platform.system() == "Linux":
                try:
                    with open('/proc/meminfo', 'r') as f:
                        meminfo = f.read()
                    total = re.search(r'MemTotal:\s+(\d+)', meminfo).group(1)
                    free = re.search(r'MemFree:\s+(\d+)', meminfo).group(1)
                    return f"内存信息:\n总内存: {int(total)//1024} MB\n空闲内存: {int(free)//1024} MB"
                except Exception as e:
                    return f"获取内存信息失败: {str(e)}"
            elif platform.system() == "Darwin":  # macOS
                try:
                    result = subprocess.run(['sysctl', '-n', 'hw.memsize'], capture_output=True, text=True)
                    total_bytes = int(result.stdout.strip())
                    return f"内存信息:\n总内存: {total_bytes // (1024**2)} MB"
                except Exception as e:
                    return f"获取内存信息失败: {str(e)}"
            elif platform.system() == "Windows":
                try:
                    result = subprocess.run(['wmic', 'OS', 'get', 'FreePhysicalMemory,TotalVisibleMemorySize'], capture_output=True, text=True)
                    lines = result.stdout.strip().split('\n')
                    values = lines[-1].split()
                    total = int(values[1]) // 1024
                    free = int(values[0]) // 1024
                    return f"内存信息:\n总内存: {total} MB\n空闲内存: {free} MB"
                except Exception as e:
                    return f"获取内存信息失败: {str(e)}"
            else:
                return "无法获取内存信息，不支持的操作系统"
        
        # 默认返回所有系统信息
        return "系统信息:\n" + "\n".join([f"{k}: {v}" for k, v in system_info.items()])


class RunShellCommand(BaseCommand):
    """执行Shell命令"""
    
    def __init__(self):
        super().__init__()
        self.name = "执行命令"
        # 由于安全考虑，Shell命令需要确认
        self.require_confirmation = True
    
    def execute(self, command_text):
        """
        执行Shell命令
        
        参数:
            command_text (str): 命令文本
            
        返回:
            str: 执行结果
        """
        # 从命令文本中提取Shell命令
        pattern = re.compile(r'(?:执行|运行)(?:命令|shell)\s*(.+)')
        match = pattern.search(command_text)
        
        if not match:
            return "未能识别Shell命令。请使用格式：执行命令 [shell命令]"
        
        shell_cmd = match.group(1).strip()
        if not shell_cmd:
            return "请指定要执行的Shell命令"
        
        try:
            # 执行Shell命令
            result = subprocess.run(
                shell_cmd, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=30  # 30秒超时
            )
            
            # 格式化输出
            if result.returncode == 0:
                output = result.stdout or "命令执行成功，没有输出"
                return f"命令执行结果 (退出码: {result.returncode}):\n{output}"
            else:
                error = result.stderr or "未知错误"
                return f"命令执行失败 (退出码: {result.returncode}):\n{error}"
        except subprocess.TimeoutExpired:
            return "命令执行超时（超过30秒）"
        except Exception as e:
            return f"执行命令失败: {str(e)}"
    
    def get_confirmation_details(self, command_text):
        """
        获取确认详情
        
        参数:
            command_text (str): 命令文本
            
        返回:
            str: 确认详情
        """
        pattern = re.compile(r'(?:执行|运行)(?:命令|shell)\s*(.+)')
        match = pattern.search(command_text)
        
        if not match:
            return "未能识别要执行的Shell命令"
        
        shell_cmd = match.group(1).strip()
        
        return f"您确定要执行以下Shell命令吗？这可能会影响系统状态：\n{shell_cmd}"
    
    def get_required_permission(self):
        """
        获取执行命令所需的权限
        
        返回:
            str: 权限名称
        """
        return "shell_execution"  # 定义一个权限名称，可以在权限管理系统中使用


class CurrentDirectoryCommand(BaseCommand):
    """获取或切换当前目录"""
    
    def __init__(self):
        super().__init__()
        self.name = "当前目录"
        self.require_confirmation = False
    
    def execute(self, command_text):
        """
        执行获取或切换当前目录操作
        
        参数:
            command_text (str): 命令文本
            
        返回:
            str: 执行结果
        """
        # 检查是否请求获取当前目录
        if re.search(r'(?:获取|显示|查看|当前)(?:目录|文件夹|路径)', command_text):
            return f"当前目录: {os.getcwd()}"
        
        # 检查是否请求切换目录
        cd_pattern = re.compile(r'(?:切换|进入|改变)(?:目录|文件夹|路径)\s*(.+)')
        match = cd_pattern.search(command_text)
        
        if match:
            target_dir = match.group(1).strip()
            
            try:
                # 切换目录
                os.chdir(target_dir)
                return f"已切换到目录: {os.getcwd()}"
            except FileNotFoundError:
                return f"目录不存在: {target_dir}"
            except PermissionError:
                return f"没有权限访问目录: {target_dir}"
            except Exception as e:
                return f"切换目录失败: {str(e)}"
        
        return "未能识别目录操作。请使用格式：'当前目录' 或 '切换目录 [目标路径]'" 