"""
语音命令处理模块

此模块提供语音命令的监听、分发和执行功能。
它利用ASR模块将语音转换为文本，然后识别并执行相应的命令。
"""

from src.voice_command.command_listener import CommandListener
from src.voice_command.command_dispatcher import CommandDispatcher
from src.voice_command.command_executor import CommandExecutor

__all__ = ['CommandListener', 'CommandDispatcher', 'CommandExecutor'] 