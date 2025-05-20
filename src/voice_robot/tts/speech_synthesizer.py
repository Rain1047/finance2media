import os
import time
from typing import Dict, Optional, Union
import numpy as np
import soundfile as sf

# 尝试导入PaddleSpeech
try:
    from paddlespeech.cli.tts.infer import TTSExecutor
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("PaddleSpeech 未安装，将使用模拟TTS")

class SpeechSynthesizer:
    """语音合成器，负责将文本转换为语音"""
    
    def __init__(self, config: Dict = None):
        """
        初始化语音合成器
        
        Args:
            config: 配置参数，包括模型路径、输出目录等
        """
        self.config = config or {
            "model_path": "models/tts_model",      # 模型路径
            "output_dir": "output/audio",          # 输出目录
            "sample_rate": 24000,                  # 采样率
            "use_mock": not TTS_AVAILABLE,         # 是否使用模拟TTS
            "voice_id": "default",                 # 声音ID
            "speed": 1.0,                          # 语速
        }
        
        self.tts_executor = None
        
        # 创建输出目录
        os.makedirs(self.config["output_dir"], exist_ok=True)
        
        # 如果不使用模拟，则初始化模型
        if not self.config["use_mock"]:
            self._initialize_model()
    
    def _initialize_model(self):
        """初始化TTS模型"""
        try:
            print("正在加载TTS模型...")
            self.tts_executor = TTSExecutor()
            print("TTS模型加载完成")
        except Exception as e:
            print(f"加载TTS模型失败: {str(e)}")
            self.config["use_mock"] = True
    
    def synthesize(self, text: str, output_filename: Optional[str] = None) -> str:
        """
        将文本转换为语音
        
        Args:
            text: 要转换的文本
            output_filename: 输出文件名（可选）
            
        Returns:
            生成的音频文件路径
        """
        if not output_filename:
            timestamp = int(time.time())
            output_filename = f"tts_output_{timestamp}.wav"
        
        output_path = os.path.join(self.config["output_dir"], output_filename)
        
        try:
            if self.config["use_mock"]:
                self._mock_synthesize(text, output_path)
            else:
                self._real_synthesize(text, output_path)
            
            return output_path
        except Exception as e:
            print(f"语音合成失败: {str(e)}")
            return None
    
    def _real_synthesize(self, text: str, output_path: str) -> None:
        """使用PaddleSpeech进行实际的语音合成"""
        try:
            self.tts_executor(
                text=text,
                output=output_path,
                model=self.config["model_path"],
                lang="zh",
                spk_id=self.config["voice_id"],
                speed=self.config["speed"]
            )
        except Exception as e:
            print(f"PaddleSpeech合成失败: {str(e)}")
            # 如果实际合成失败，回退到模拟合成
            self._mock_synthesize(text, output_path)
    
    def _mock_synthesize(self, text: str, output_path: str) -> None:
        """模拟语音合成，生成一个简单的提示音"""
        # 生成一个简单的提示音
        duration = 1.0  # 1秒
        t = np.linspace(0, duration, int(self.config["sample_rate"] * duration))
        frequency = 440  # A4音符
        audio = 0.5 * np.sin(2 * np.pi * frequency * t)
        
        # 保存音频文件
        sf.write(output_path, audio, self.config["sample_rate"])
        
        print(f"模拟TTS: 文本 '{text}' 已转换为音频文件 {output_path}")
    
    def set_voice(self, voice_id: str) -> None:
        """设置声音ID"""
        self.config["voice_id"] = voice_id
    
    def set_speed(self, speed: float) -> None:
        """设置语速"""
        if 0.5 <= speed <= 2.0:
            self.config["speed"] = speed
        else:
            print("语速必须在0.5到2.0之间") 