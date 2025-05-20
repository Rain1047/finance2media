import os
import time
from typing import Dict, Optional, Callable
from datetime import datetime

from .asr.speech_recognizer import SpeechRecognizer
from .llm.conversation_manager import ConversationManager
from .tts.speech_synthesizer import SpeechSynthesizer

class VoiceAssistant:
    """语音助手主控制器，整合ASR、LLM和TTS模块"""
    
    def __init__(self, config: Dict = None):
        """
        初始化语音助手
        
        Args:
            config: 配置参数
        """
        self.config = config or {
            "user_id": "default",
            "save_conversations": True,
            "auto_play": True,
            "wake_word": "你好小助手",
            "exit_phrases": ["再见", "退出", "结束对话"],
        }
        
        # 初始化各个模块
        self.asr = SpeechRecognizer()
        self.llm = ConversationManager()
        self.tts = SpeechSynthesizer()
        
        # 状态标志
        self.is_listening = False
        self.is_processing = False
        self.should_exit = False
        
        # 回调函数
        self.on_wake = None
        self.on_sleep = None
        self.on_error = None
    
    def start(self):
        """启动语音助手"""
        print("语音助手已启动，等待唤醒词...")
        self.is_listening = True
        
        try:
            while not self.should_exit:
                # 开始录音
                self.asr.start_listening()
                
                # 等待用户说话
                print("正在聆听...")
                text = self.asr.transcribe()
                
                if text:
                    print(f"识别到的文本: {text}")
                    
                    # 检查是否是唤醒词
                    if text.strip() == self.config["wake_word"]:
                        if self.on_wake:
                            self.on_wake()
                        self._handle_wake()
                        continue
                    
                    # 检查是否是退出短语
                    if text.strip() in self.config["exit_phrases"]:
                        self._handle_exit()
                        continue
                    
                    # 处理用户输入
                    self._process_user_input(text)
                
                time.sleep(0.1)  # 避免CPU占用过高
                
        except KeyboardInterrupt:
            print("\n收到退出信号")
        except Exception as e:
            if self.on_error:
                self.on_error(str(e))
            print(f"发生错误: {str(e)}")
        finally:
            self.stop()
    
    def stop(self):
        """停止语音助手"""
        self.is_listening = False
        self.asr.stop_listening()
        print("语音助手已停止")
    
    def _handle_wake(self):
        """处理唤醒事件"""
        print("已唤醒，请说出您的问题...")
        response = "我在听，请说"
        self._speak(response)
    
    def _handle_exit(self):
        """处理退出事件"""
        print("正在退出...")
        response = "再见，祝您有愉快的一天"
        self._speak(response)
        self.should_exit = True
    
    def _process_user_input(self, text: str):
        """处理用户输入"""
        self.is_processing = True
        
        try:
            # 获取LLM回复
            response = self.llm.process_message(text, self.config["user_id"])
            print(f"AI回复: {response}")
            
            # 转换为语音
            self._speak(response)
            
        except Exception as e:
            error_msg = f"处理输入时发生错误: {str(e)}"
            print(error_msg)
            if self.on_error:
                self.on_error(error_msg)
        finally:
            self.is_processing = False
    
    def _speak(self, text: str):
        """将文本转换为语音并播放"""
        try:
            # 生成语音文件
            audio_path = self.tts.synthesize(text)
            
            # 如果配置了自动播放，则播放音频
            if self.config["auto_play"] and audio_path:
                # 这里可以添加音频播放的代码
                # 例如使用 pygame 或其他音频库
                pass
                
        except Exception as e:
            print(f"语音合成失败: {str(e)}")
    
    def set_wake_word(self, wake_word: str):
        """设置唤醒词"""
        self.config["wake_word"] = wake_word
    
    def set_exit_phrases(self, phrases: list):
        """设置退出短语列表"""
        self.config["exit_phrases"] = phrases
    
    def set_callbacks(self, on_wake: Callable = None, on_sleep: Callable = None, on_error: Callable = None):
        """设置回调函数"""
        self.on_wake = on_wake
        self.on_sleep = on_sleep
        self.on_error = on_error
    
    def get_conversation_history(self, max_entries: int = None) -> list:
        """获取对话历史"""
        return self.llm.get_conversation_history(self.config["user_id"], max_entries)
    
    def clear_history(self):
        """清除对话历史"""
        self.llm.clear_history(self.config["user_id"]) 