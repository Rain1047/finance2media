"""
音频预处理模块
实现音频数据的预处理功能
"""

import numpy as np
import soundfile as sf
from typing import Optional, Tuple, List
from .config import AUDIO_CONFIG

class AudioProcessor:
    def __init__(self, 
                 sample_rate: int = AUDIO_CONFIG['sample_rate'],
                 channels: int = AUDIO_CONFIG['channels']):
        """
        初始化音频处理器
        
        Args:
            sample_rate: 采样率
            channels: 通道数
        """
        self.sample_rate = sample_rate
        self.channels = channels
    
    def normalize(self, audio: np.ndarray) -> np.ndarray:
        """
        音频归一化
        
        Args:
            audio: 输入音频数据
            
        Returns:
            归一化后的音频数据
        """
        if audio.dtype != np.float32:
            audio = audio.astype(np.float32)
        return audio / np.max(np.abs(audio))
    
    def resample(self, audio: np.ndarray, orig_sr: int) -> np.ndarray:
        """
        重采样
        
        Args:
            audio: 输入音频数据
            orig_sr: 原始采样率
            
        Returns:
            重采样后的音频数据
        """
        if orig_sr == self.sample_rate:
            return audio
        return sf.resample(audio, self.sample_rate, orig_sr)
    
    def convert_to_mono(self, audio: np.ndarray) -> np.ndarray:
        """
        转换为单声道
        
        Args:
            audio: 输入音频数据
            
        Returns:
            单声道音频数据
        """
        if len(audio.shape) == 1:
            return audio
        return np.mean(audio, axis=1)
    
    def preprocess(self, 
                  audio: np.ndarray, 
                  orig_sr: Optional[int] = None) -> np.ndarray:
        """
        音频预处理
        
        Args:
            audio: 输入音频数据
            orig_sr: 原始采样率
            
        Returns:
            预处理后的音频数据
        """
        # 转换为单声道
        audio = self.convert_to_mono(audio)
        
        # 重采样
        if orig_sr is not None:
            audio = self.resample(audio, orig_sr)
        
        # 归一化
        audio = self.normalize(audio)
        
        return audio
    
    def split_audio(self, 
                    audio: np.ndarray, 
                    chunk_size: int) -> List[np.ndarray]:
        """
        将音频分割成固定大小的块
        
        Args:
            audio: 输入音频数据
            chunk_size: 块大小
            
        Returns:
            音频块列表
        """
        return [audio[i:i + chunk_size] 
                for i in range(0, len(audio), chunk_size)]
    
    def merge_audio(self, audio_chunks: List[np.ndarray]) -> np.ndarray:
        """
        合并音频块
        
        Args:
            audio_chunks: 音频块列表
            
        Returns:
            合并后的音频数据
        """
        return np.concatenate(audio_chunks)
    
    def save_audio(self, 
                   audio: np.ndarray, 
                   filepath: str, 
                   format: str = 'WAV') -> None:
        """
        保存音频文件
        
        Args:
            audio: 音频数据
            filepath: 文件路径
            format: 文件格式
        """
        sf.write(filepath, audio, self.sample_rate, format=format)
    
    def load_audio(self, filepath: str) -> Tuple[np.ndarray, int]:
        """
        加载音频文件
        
        Args:
            filepath: 文件路径
            
        Returns:
            (音频数据, 采样率)
        """
        audio, sr = sf.read(filepath)
        return audio, sr 