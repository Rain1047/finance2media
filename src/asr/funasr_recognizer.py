"""
FunASR 识别器模块
实现语音识别功能
"""

import os
import time
from typing import Optional, List, Dict, Any, Callable
import numpy as np
from funasr import AutoModel
from .config import FUNASR_CONFIG, STREAMING_CONFIG, ERROR_HANDLING

class FunASRRecognizer:
    def __init__(self,
                 model: str = FUNASR_CONFIG['model'],
                 model_dir: str = FUNASR_CONFIG['model_dir'],
                 device: str = FUNASR_CONFIG['device'],
                 batch_size: int = FUNASR_CONFIG['batch_size'],
                 hotword: Optional[List[str]] = FUNASR_CONFIG['hotword']):
        """
        初始化 FunASR 识别器
        
        Args:
            model: 模型名称
            model_dir: 模型目录
            device: 运行设备
            batch_size: 批处理大小
            hotword: 热词列表
        """
        self.model = model
        self.model_dir = model_dir
        self.device = device
        self.batch_size = batch_size
        self.hotword = hotword
        
        self._model = None
        self._cache = {}
        self._error_callback = None
        
        # 确保模型目录存在
        os.makedirs(model_dir, exist_ok=True)
    
    def _load_model(self):
        """加载模型"""
        if self._model is None:
            try:
                # 使用 FunASR AutoModel 加载模型
                self._model = AutoModel(
                    model="paraformer",
                    vad_model="fsmn-vad",
                    vad_kwargs={"max_single_segment_time": 30000},
                    punc_model="ct-punc",
                    punc_kwargs={},
                )
            except Exception as e:
                if self._error_callback:
                    self._error_callback(f"模型加载失败: {str(e)}")
                raise
    
    def start(self, error_callback: Optional[Callable] = None):
        """
        启动识别器
        
        Args:
            error_callback: 错误回调函数
        """
        self._error_callback = error_callback
        self._load_model()
        self._cache = {}
    
    def stop(self):
        """停止识别器"""
        self._model = None
        self._cache = {}
    
    def recognize(self, 
                 audio: np.ndarray, 
                 is_final: bool = False) -> str:
        """
        识别音频
        
        Args:
            audio: 音频数据
            is_final: 是否为最后一段音频
            
        Returns:
            识别结果文本
        """
        if self._model is None:
            self._load_model()
        
        try:
            # 执行识别
            result = self._model.generate(input=audio)
            
            # 从结果中提取文本
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("text", "")
            return ""
            
        except Exception as e:
            if self._error_callback:
                self._error_callback(f"识别失败: {str(e)}")
            raise
    
    def recognize_stream(self, 
                        audio_chunks: List[np.ndarray], 
                        callback: Optional[Callable[[str], None]] = None) -> str:
        """
        流式识别
        
        Args:
            audio_chunks: 音频块列表
            callback: 实时结果回调函数
            
        Returns:
            最终识别结果
        """
        results = []
        for i, chunk in enumerate(audio_chunks):
            is_final = (i == len(audio_chunks) - 1)
            result = self.recognize(chunk, is_final)
            results.append(result)
            
            if callback:
                callback(result)
        
        return "".join(results)
    
    def __enter__(self):
        """上下文管理器入口"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.stop() 