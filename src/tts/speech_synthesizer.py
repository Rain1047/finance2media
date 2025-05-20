import os
import time
import tempfile
from typing import Dict, Optional, Union
import threading
import queue

# 尝试导入paddlespeech
try:
    import paddlehub as hub
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("PaddleSpeech 未安装，将使用模拟TTS")

# 尝试导入pygame用于音频播放
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("Pygame 未安装，将使用系统默认播放器")

class SpeechSynthesizer:
    """语音合成模块，负责将文本转换为语音"""
    
    def __init__(self, config: Dict = None):
        """
        初始化语音合成器
        
        Args:
            config: 配置参数，包括模型、声音类型等
        """
        self.config = config or {
            "model_name": "fastspeech2_baker",  # 默认中文模型
            "voice_type": "female",           # 声音类型：male/female
            "speed": 1.0,                     # 语速
            "volume": 1.0,                    # 音量
            "output_dir": "output/audio",     # 音频输出目录
            "use_mock": not TTS_AVAILABLE,    # 是否使用模拟TTS
            "use_pygame": PYGAME_AVAILABLE,   # 是否使用pygame播放
        }
        
        self.model = None
        self.audio_queue = queue.Queue()
        self.is_playing = False
        self.player_thread = None
        
        # 初始化输出目录
        os.makedirs(self.config["output_dir"], exist_ok=True)
        
        # 初始化pygame
        if self.config["use_pygame"] and PYGAME_AVAILABLE:
            pygame.mixer.init()
        
        # 如果不使用模拟，则初始化模型
        if not self.config["use_mock"]:
            self._initialize_model()
    
    def _initialize_model(self):
        """初始化TTS模型"""
        try:
            print("正在加载TTS模型...")
            
            # 使用PaddleSpeech的TTS模型
            self.model = hub.Module(name=self.config["model_name"])
            
            print("TTS模型加载完成")
        except Exception as e:
            print(f"加载模型失败: {str(e)}")
            self.config["use_mock"] = True
    
    def synthesize(self, text: str, output_file: Optional[str] = None) -> str:
        """
        将文本转换为语音
        
        Args:
            text: 需要转换的文本
            output_file: 输出文件路径，如果为None则自动生成
            
        Returns:
            生成的音频文件路径
        """
        if output_file is None:
            # 生成唯一的输出文件名
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(self.config["output_dir"], f"tts_{timestamp}.wav")
        
        if self.config["use_mock"]:
            # 模拟TTS生成过程
            time.sleep(len(text) * 0.05)  # 文本越长，生成时间越长
            
            # 创建一个空的音频文件
            with open(output_file, 'wb') as f:
                f.write(b'\x00' * 44)  # 简单的WAV文件头部
            
            print(f"模拟TTS: 已生成文件 {output_file}")
        else:
            # 使用实际模型生成语音
            result = self.model.synthesize(
                text=text,
                output_dir=os.path.dirname(output_file),
                output_file=os.path.basename(output_file),
                speed=self.config["speed"],
                volume=self.config["volume"]
            )
            print(f"TTS: 已生成文件 {output_file}")
        
        return output_file
    
    def start_playback_thread(self):
        """启动音频播放线程"""
        if self.is_playing:
            print("已经在播放中")
            return
            
        self.is_playing = True
        self.player_thread = threading.Thread(target=self._playback_worker)
        self.player_thread.daemon = True
        self.player_thread.start()
        print("开始音频播放线程")
    
    def stop_playback_thread(self):
        """停止音频播放线程"""
        self.is_playing = False
        if self.player_thread:
            self.player_thread.join(timeout=2.0)
            print("停止音频播放线程")
    
    def _playback_worker(self):
        """音频播放线程函数"""
        while self.is_playing:
            try:
                if not self.audio_queue.empty():
                    audio_file = self.audio_queue.get()
                    self._play_audio(audio_file)
                else:
                    time.sleep(0.1)  # 避免空转
            except Exception as e:
                print(f"播放音频时发生错误: {str(e)}")
    
    def _play_audio(self, audio_file: str):
        """播放音频文件"""
        if not os.path.exists(audio_file):
            print(f"音频文件不存在: {audio_file}")
            return
            
        if self.config["use_pygame"] and PYGAME_AVAILABLE:
            # 使用pygame播放
            try:
                pygame.mixer.music.load(audio_file)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
            except Exception as e:
                print(f"pygame播放失败: {str(e)}")
                self._play_with_system(audio_file)
        else:
            # 使用系统默认播放器
            self._play_with_system(audio_file)
    
    def _play_with_system(self, audio_file: str):
        """使用系统默认播放器播放音频"""
        import platform
        system = platform.system()
        
        try:
            if system == "Darwin":  # macOS
                os.system(f"afplay {audio_file}")
            elif system == "Linux":
                os.system(f"aplay {audio_file}")
            elif system == "Windows":
                os.system(f"start {audio_file}")
            else:
                print(f"不支持的操作系统: {system}")
        except Exception as e:
            print(f"系统播放失败: {str(e)}")
    
    def speak(self, text: str) -> str:
        """
        合成并播放文本
        
        Args:
            text: 需要转换和播放的文本
            
        Returns:
            生成的音频文件路径
        """
        # 合成语音
        audio_file = self.synthesize(text)
        
        # 将音频文件加入播放队列
        self.audio_queue.put(audio_file)
        
        # 如果播放线程未启动，则启动
        if not self.is_playing:
            self.start_playback_thread()
            
        return audio_file 