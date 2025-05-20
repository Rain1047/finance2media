"""
音频采集模块
实现实时音频采集功能
"""

import pyaudio
import numpy as np
import threading
import queue
import time
from typing import Optional, Callable
from .config import AUDIO_CONFIG

class AudioCapture:
    def __init__(self, 
                 sample_rate: int = AUDIO_CONFIG['sample_rate'],
                 channels: int = AUDIO_CONFIG['channels'],
                 chunk_size: int = AUDIO_CONFIG['chunk_size'],
                 format: str = AUDIO_CONFIG['format'],
                 device_index: Optional[int] = AUDIO_CONFIG['device_index']):
        """
        初始化音频采集器
        
        Args:
            sample_rate: 采样率
            channels: 通道数
            chunk_size: 缓冲区大小
            format: 采样格式
            device_index: 音频设备索引
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.format = getattr(pyaudio, f'pa{format.capitalize()}')
        self.device_index = device_index
        
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.error_callback = None
        
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """音频回调函数"""
        if status:
            if self.error_callback:
                self.error_callback(f"音频采集错误: {status}")
        self.audio_queue.put(in_data)
        return (in_data, pyaudio.paContinue)
    
    def start(self, error_callback: Optional[Callable] = None):
        """
        开始录音
        
        Args:
            error_callback: 错误回调函数
        """
        if self.is_recording:
            return
            
        self.error_callback = error_callback
        self.is_recording = True
        
        try:
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=self.device_index,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_callback
            )
            self.stream.start_stream()
        except Exception as e:
            self.is_recording = False
            if self.error_callback:
                self.error_callback(f"启动录音失败: {str(e)}")
            raise
    
    def stop(self):
        """停止录音"""
        if not self.is_recording:
            return
            
        self.is_recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.audio.terminate()
    
    def read(self, timeout: Optional[float] = None) -> Optional[np.ndarray]:
        """
        读取音频数据
        
        Args:
            timeout: 超时时间（秒）
            
        Returns:
            numpy.ndarray: 音频数据，如果超时则返回 None
        """
        try:
            data = self.audio_queue.get(timeout=timeout)
            return np.frombuffer(data, dtype=np.int16)
        except queue.Empty:
            return None
    
    def __enter__(self):
        """上下文管理器入口"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.stop() 