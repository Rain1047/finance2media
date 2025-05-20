import os
import time
import json
import threading
import queue
from typing import Dict, List, Optional, Any

# 导入各个模块
from asr.speech_recognizer import SpeechRecognizer
from llm.conversation_manager import ConversationManager
from tts.speech_synthesizer import SpeechSynthesizer

class VoiceAssistant:
    """语音助手主类，整合ASR、LLM对话和TTS功能"""
    
    def __init__(self, config_path: str = "config/voice_assistant_config.json"):
        """
        初始化语音助手
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        
        # 初始化各个模块
        self.speech_recognizer = SpeechRecognizer(self.config.get("asr_config"))
        self.conversation_manager = ConversationManager(self.config.get("llm_config"))
        self.speech_synthesizer = SpeechSynthesizer(self.config.get("tts_config"))
        
        # 运行状态
        self.is_running = False
        self.main_thread = None
        self.user_id = "default"
        
        # 命令词
        self.wake_words = self.config.get("wake_words", ["你好小助手", "嗨小助手"])
        self.stop_words = self.config.get("stop_words", ["再见", "停止"])
        
        print("语音助手初始化完成")
    
    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        if not os.path.exists(config_path):
            # 默认配置
            return {
                "wake_words": ["你好小助手", "嗨小助手"],
                "stop_words": ["再见", "停止"],
                "max_idle_time": 60,  # 最大空闲时间(秒)
                "asr_config": {},
                "llm_config": {},
                "tts_config": {}
            }
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def start(self, user_id: str = "default"):
        """启动语音助手"""
        if self.is_running:
            print("语音助手已经在运行")
            return
            
        self.is_running = True
        self.user_id = user_id
        
        # 开始语音识别
        self.speech_recognizer.start_listening()
        
        # 开始TTS播放线程
        self.speech_synthesizer.start_playback_thread()
        
        # 欢迎语
        welcome_message = "你好，我是你的语音助手。有什么我可以帮你的吗？"
        self.speech_synthesizer.speak(welcome_message)
        
        # 启动主循环线程
        self.main_thread = threading.Thread(target=self._main_loop)
        self.main_thread.daemon = True
        self.main_thread.start()
        
        print(f"语音助手已启动，用户ID: {user_id}")
    
    def stop(self):
        """停止语音助手"""
        if not self.is_running:
            print("语音助手未运行")
            return
            
        self.is_running = False
        
        # 停止语音识别
        self.speech_recognizer.stop_listening()
        
        # 停止TTS播放线程
        self.speech_synthesizer.stop_playback_thread()
        
        # 等待主线程结束
        if self.main_thread:
            self.main_thread.join(timeout=2.0)
            
        # 告别语
        farewell_message = "再见，期待下次与你交流。"
        self.speech_synthesizer.speak(farewell_message)
        
        print("语音助手已停止")
    
    def _main_loop(self):
        """主循环，持续处理语音输入并生成回复"""
        last_activity_time = time.time()
        max_idle_time = self.config.get("max_idle_time", 60)
        
        while self.is_running:
            try:
                # 识别语音
                transcribed_text = self.speech_recognizer.transcribe()
                
                if transcribed_text:
                    print(f"用户: {transcribed_text}")
                    last_activity_time = time.time()
                    
                    # 检查停止命令
                    if any(stop_word in transcribed_text.lower() for stop_word in self.stop_words):
                        print("检测到停止命令")
                        self.stop()
                        break
                    
                    # 处理用户输入并获取回复
                    response = self.conversation_manager.process_message(
                        transcribed_text, 
                        user_id=self.user_id
                    )
                    
                    print(f"助手: {response}")
                    
                    # 将回复转为语音
                    self.speech_synthesizer.speak(response)
                
                # 检查空闲超时
                if time.time() - last_activity_time > max_idle_time:
                    print(f"空闲超过{max_idle_time}秒，自动停止")
                    self.stop()
                    break
                    
                time.sleep(0.1)  # 避免CPU占用过高
                
            except Exception as e:
                print(f"主循环发生错误: {str(e)}")
                time.sleep(1.0)  # 错误后暂停一下
    
    def process_text_input(self, text: str) -> str:
        """处理文本输入（用于非语音交互测试）"""
        if not text:
            return ""
            
        # 检查停止命令
        if any(stop_word in text.lower() for stop_word in self.stop_words):
            self.stop()
            return "已停止语音助手"
            
        # 处理文本并获取回复
        response = self.conversation_manager.process_message(
            text, 
            user_id=self.user_id
        )
        
        # 将回复转为语音
        self.speech_synthesizer.speak(response)
        
        return response 