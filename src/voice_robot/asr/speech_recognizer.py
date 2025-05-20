import os
import time
import numpy as np
from typing import Optional, Dict, List, Union
import threading
import queue

# 引入语音识别库（假设使用whisper离线版）
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("Whisper 未安装，将使用模拟ASR")

class SpeechRecognizer:
    """语音识别模块，负责将语音转换为文本"""
    
    def __init__(self, config: Dict = None):
        """
        初始化语音识别器
        
        Args:
            config: 配置参数，包括模型大小、语言等
        """
        self.config = config or {
            "model_size": "base",  # tiny, base, small, medium, large
            "language": "zh",      # 默认语言为中文
            "device": "cpu",       # 使用CPU或GPU
            "use_mock": not WHISPER_AVAILABLE  # 如果whisper不可用，则使用模拟ASR
        }
        
        self.model = None
        self.audio_queue = queue.Queue()
        self.is_listening = False
        self.listener_thread = None
        
        # 初始化模型
        self._initialize_model()
    
    def _initialize_model(self):
        """初始化ASR模型"""
        if self.config.get("use_mock"):
            print("使用模拟ASR模型")
            return
            
        try:
            print(f"正在加载Whisper模型 ({self.config['model_size']})...")
            self.model = whisper.load_model(
                self.config["model_size"], 
                device=self.config["device"]
            )
            print("Whisper模型加载完成")
        except Exception as e:
            print(f"加载模型失败: {str(e)}")
            self.config["use_mock"] = True
    
    def start_listening(self):
        """开始监听音频输入"""
        if self.is_listening:
            print("已经在监听中")
            return
            
        self.is_listening = True
        self.listener_thread = threading.Thread(target=self._listen_audio_stream)
        self.listener_thread.daemon = True
        self.listener_thread.start()
        print("开始监听音频输入")
    
    def stop_listening(self):
        """停止监听音频输入"""
        self.is_listening = False
        if self.listener_thread:
            self.listener_thread.join(timeout=2.0)
            print("停止监听音频输入")
    
    def _listen_audio_stream(self):
        """监听音频流的线程函数"""
        import pyaudio
        import wave
        
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
        
        print("* 录音中...")
        
        frames = []
        
        # 持续录音，直到停止信号
        while self.is_listening:
            data = stream.read(CHUNK)
            frames.append(data)
            
            # 检测静音，可以添加更复杂的静音检测逻辑
            if len(frames) > 50:  # 大约3秒的音频
                audio_data = b''.join(frames)
                self.audio_queue.put(audio_data)
                frames = []
        
        stream.stop_stream()
        stream.close()
        p.terminate()
    
    def transcribe(self, audio_data: Optional[bytes] = None) -> str:
        """
        识别音频数据并转换为文本
        
        Args:
            audio_data: 音频数据，如果为None则从队列获取
            
        Returns:
            识别的文本
        """
        if self.config.get("use_mock"):
            # 模拟延迟，以及一些预定义的回复
            time.sleep(1.0)
            mock_texts = [
                "你好，我能帮你什么忙?",
                "今天天气真不错",
                "我想了解小红书平台的运营技巧",
                "这个问题很有趣，让我想一想"
            ]
            return np.random.choice(mock_texts)
            
        if audio_data is None:
            if not self.audio_queue.empty():
                audio_data = self.audio_queue.get()
            else:
                return ""
                
        # 保存临时音频文件
        temp_file = "temp_audio.wav"
        with wave.open(temp_file, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(audio_data)
        
        # 使用Whisper转录
        result = self.model.transcribe(
            temp_file,
            language=self.config["language"],
            fp16=False
        )
        
        # 清理临时文件
        if os.path.exists(temp_file):
            os.remove(temp_file)
            
        return result["text"] 