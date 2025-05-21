"""
命令执行器模块

此模块负责连接命令监听器和命令分发器，
并处理命令的执行流程，包括权限验证、确认、执行和反馈。
"""

import logging
import time
import os
from src.voice_command.command_dispatcher import CommandDispatcher
from src.voice_command.command_listener import CommandListener
from src.tts.speech_synthesizer import SpeechSynthesizer

# 配置日志
logger = logging.getLogger(__name__)

class CommandExecutor:
    """命令执行器，连接监听器和分发器"""
    
    def __init__(self, config_path=None, use_voice_feedback=False):
        """
        初始化命令执行器
        
        参数:
            config_path (str): 命令配置文件路径
            use_voice_feedback (bool): 是否使用语音反馈
        """
        self.dispatcher = CommandDispatcher(config_path)
        self.listener = None
        self.last_commands = []  # 存储最近执行的命令，用于撤销
        self.max_history = 10    # 最大历史记录数
        
        # 语音反馈
        self.use_voice_feedback = use_voice_feedback
        self.tts = None
        if use_voice_feedback:
            try:
                self.tts = SpeechSynthesizer()
                # 测试TTS是否工作正常
                test_file = self.tts.synthesize("测试")
                if not os.path.exists(test_file) or os.path.getsize(test_file) < 100:
                    raise Exception("生成的测试音频文件无效")
                logger.info("语音合成器初始化成功")
            except Exception as e:
                logger.warning(f"初始化语音合成器失败: {str(e)}")
                self.use_voice_feedback = False
                self.tts = None
    
    def _speak(self, text):
        """
        安全地使用TTS播放文本
        
        参数:
            text (str): 要播放的文本
            
        返回:
            bool: 是否成功播放
        """
        if not self.use_voice_feedback or not self.tts:
            return False
            
        try:
            self.tts.speak(text)
            return True
        except Exception as e:
            logger.warning(f"语音播放失败: {str(e)}")
            return False
    
    def start_listening(self, continuous=False, energy_threshold=1000):
        """
        开始监听命令
        
        参数:
            continuous (bool): 是否持续监听
            energy_threshold (int): 音频能量阈值
            
        返回:
            CommandListener: 监听器实例
        """
        # 如果已经有监听器，优先使用现有的
        if not self.listener:
            self.listener = CommandListener(
                callback=self.process_command,
                continuous=continuous,
                energy_threshold=energy_threshold
            )
        
        logger.info(f"开始{'持续' if continuous else '单次'}监听命令")
        
        # 语音反馈
        self._speak("开始监听命令")
            
        return self.listener.start()
    
    def stop_listening(self):
        """停止监听"""
        if self.listener:
            self.listener.stop()
            logger.info("停止监听命令")
            
            # 语音反馈
            self._speak("停止监听命令")
    
    def process_command(self, text):
        """
        处理识别出的命令文本
        
        参数:
            text (str): 命令文本
            
        返回:
            str: 执行结果
        """
        logger.info(f"识别到命令: {text}")
        
        # 语音反馈
        self._speak(f"识别到命令: {text}")
        
        # 1. 分发命令
        command, cmd_text = self.dispatcher.dispatch(text)
        
        # 2. 执行命令
        if command:
            try:
                # 检查是否需要确认
                if command.require_confirmation:
                    confirm = self._ask_confirmation(command, cmd_text)
                    if not confirm:
                        logger.info("用户取消了命令执行")
                        
                        # 语音反馈
                        self._speak("已取消执行命令")
                            
                        return "已取消执行命令"
                
                # 执行命令前记录
                start_time = time.time()
                
                # 执行命令
                result = command.execute(cmd_text)
                
                # 记录执行时间
                duration = time.time() - start_time
                logger.info(f"命令执行完成，耗时: {duration:.2f}秒")
                
                # 记录到历史
                self._add_to_history(command, cmd_text, result)
                
                logger.info(f"执行结果: {result}")
                
                # 语音反馈
                if result:
                    # 如果结果太长，只朗读前200个字符
                    tts_result = result[:200] + ("..." if len(result) > 200 else "")
                    self._speak(tts_result)
                    
                return result
            except Exception as e:
                error_msg = f"执行命令时出错: {str(e)}"
                logger.error(error_msg, exc_info=True)
                
                # 语音反馈
                self._speak("执行命令时出错")
                    
                return error_msg
        else:
            logger.info(f"命令解析结果: {cmd_text}")
            
            # 语音反馈
            self._speak(cmd_text)
                
            return cmd_text
    
    def execute_once(self):
        """
        执行一次命令监听和处理
        
        返回:
            str: 执行结果，如果未执行任何命令则为None
        """
        logger.info("准备执行一次命令")
        
        # 语音反馈
        self._speak("请说出命令")
            
        self.start_listening(continuous=False)
        # 这里不需要返回值，因为结果会通过回调函数处理
    
    def _ask_confirmation(self, command, cmd_text):
        """
        请求用户确认执行命令
        
        参数:
            command (BaseCommand): 命令实例
            cmd_text (str): 命令文本
            
        返回:
            bool: 是否确认执行
        """
        # 获取确认详情
        details = command.get_confirmation_details(cmd_text)
        
        # 语音反馈
        self._speak(details)
        
        # 在实际应用中，这里可以使用TTS播放确认信息，并使用ASR获取用户回复
        # 这里简化为控制台交互
        print(f"\n需要确认: {details}")
        response = input("请确认是否执行 (y/n): ").lower()
        
        return response in ('y', 'yes', '是', '确认', '执行')
    
    def _add_to_history(self, command, cmd_text, result):
        """
        添加命令到历史记录
        
        参数:
            command (BaseCommand): 命令实例
            cmd_text (str): 命令文本
            result (str): 执行结果
        """
        # 限制历史记录长度
        if len(self.last_commands) >= self.max_history:
            self.last_commands.pop(0)  # 移除最旧的记录
        
        # 添加新记录
        self.last_commands.append({
            'command': command,
            'text': cmd_text,
            'result': result,
            'timestamp': time.time()
        })
    
    def undo_last_command(self):
        """
        撤销最后一个命令
        
        返回:
            str: 撤销结果
        """
        if not self.last_commands:
            undo_result = "没有可撤销的命令"
            
            # 语音反馈
            self._speak(undo_result)
                
            return undo_result
        
        # 获取最后一个命令
        last_cmd = self.last_commands.pop()
        
        # 如果命令支持撤销操作
        if hasattr(last_cmd['command'], 'undo'):
            try:
                undo_result = last_cmd['command'].undo(last_cmd['text'])
                
                # 语音反馈
                self._speak(f"已撤销: {last_cmd['text']}")
                    
                return f"已撤销: {last_cmd['text']} - {undo_result}"
            except Exception as e:
                error_msg = f"撤销命令时出错: {str(e)}"
                
                # 语音反馈
                self._speak(error_msg)
                    
                return error_msg
        else:
            undo_result = f"命令 {last_cmd['command'].name} 不支持撤销操作"
            
            # 语音反馈
            self._speak(undo_result)
                
            return undo_result 