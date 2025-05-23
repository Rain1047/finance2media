"""
命令监听器模块

此模块负责捕获音频，识别语音命令，并将文本传递给回调函数。
"""

import threading
import time
import numpy as np
from src.asr.audio_capture import AudioCapture
from src.asr.audio_processor import AudioProcessor
from src.asr.funasr_recognizer import FunASRRecognizer

class CommandListener:
    """命令监听器，持续监听语音并转换为文本命令"""
    
    def __init__(self, callback=None, continuous=False, energy_threshold=1000):
        """
        初始化命令监听器
        
        参数:
            callback (callable): 识别到命令后的回调函数，接收文本参数
            continuous (bool): 是否持续监听
            energy_threshold (int): 音频能量阈值，用于检测是否有语音
        """
        # 初始化ASR组件
        self.audio_capture = AudioCapture()
        self.audio_processor = AudioProcessor()
        self.recognizer = FunASRRecognizer()
        
        # 设置回调函数和工作模式
        self.callback = callback
        self.continuous = continuous
        self.energy_threshold = energy_threshold
        self.is_listening = False
        self.listen_thread = None
        
        # 设置语音检测参数
        self.silence_limit = 0.5  # 降低静默阈值到0.5秒，使系统更快响应
        self.prev_audio_size = 0.3  # 减少保留的语音前音频到0.3秒
        self.min_speech_duration = 0.3  # 降低最短语音持续时间到0.3秒
        
        # 流式识别相关
        self.stream_mode = True  # 默认使用流式识别
        self.interim_results = []  # 中间识别结果
        self.last_interim_text = ""  # 上一次的中间结果
        self.last_update_time = 0  # 上次更新时间
        self.update_interval = 0.1  # 更新间隔（秒）
    
    def start(self):
        """
        开始监听语音命令
        
        返回:
            self: 允许方法链式调用
        """
        if self.is_listening:
            return self
            
        self.is_listening = True
        self.listen_thread = threading.Thread(target=self._listen_loop)
        self.listen_thread.daemon = True
        self.listen_thread.start()
        return self
    
    def stop(self):
        """
        停止监听
        
        返回:
            self: 允许方法链式调用
        """
        self.is_listening = False
        if self.listen_thread and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=1.0)
        # 确保音频捕获器停止
        if hasattr(self, 'audio_capture') and self.audio_capture:
            self.audio_capture.stop()
        return self
    
    def _listen_loop(self):
        """监听循环，内部方法"""
        while self.is_listening:
            try:
                # 启动音频捕获
                self.audio_capture.start()
                print("等待语音输入...")
                
                if self.continuous:
                    # 持续监听模式
                    if self.stream_mode:
                        self._stream_listen()
                    else:
                        self._continuous_listen()
                else:
                    # 单次录音模式
                    audio_data = self._capture_audio_single()
                    if audio_data is not None and len(audio_data) > 0:
                        self._process_audio(audio_data)
                
                # 停止捕获
                self.audio_capture.stop()
                
                # 单次模式检查
                if not self.continuous:
                    self.is_listening = False
                    
                # 短暂暂停，避免CPU占用过高
                time.sleep(0.1)
                
            except Exception as e:
                print(f"监听过程中出错: {str(e)}")
                if not self.continuous:
                    self.is_listening = False
    
    def _stream_listen(self):
        """流式持续监听模式，检测语音并实时处理"""
        # 初始化识别器，准备流式处理
        self.recognizer.start()
        
        # 缓冲区
        audio_buffer = []
        
        # 语音状态
        speech_started = False
        silent_chunks = 0
        
        # 采样率和每个数据块时长
        sample_rate = 16000  # 16kHz，标准ASR采样率
        chunk_duration = 0.05  # 降低到0.05秒，提高实时性
        silence_threshold = int(self.silence_limit / chunk_duration)  # 静默阈值（块数）
        
        try:
            print("实时语音识别监听中...")
            while self.is_listening:
                # 读取音频数据
                chunk = self.audio_capture.read(timeout=0.05)  # 降低超时时间
                if chunk is None:
                    time.sleep(0.01)
                    continue
                
                # 计算音频能量
                energy = np.sqrt(np.mean(chunk**2))
                
                if energy > self.energy_threshold:
                    # 检测到语音
                    if not speech_started:
                        print("检测到语音，开始实时识别...")
                        speech_started = True
                        # 清空缓冲区和中间结果
                        audio_buffer = []
                        self.interim_results = []
                        self.last_interim_text = ""
                    
                    # 预处理音频块
                    processed_chunk = self.audio_processor.preprocess(chunk)
                    
                    # 将音频块添加到缓冲区
                    audio_buffer.append(processed_chunk)
                    
                    # 流式识别，这里is_final设为False表示不是最后一块
                    interim_text = self.recognizer.recognize(processed_chunk, is_final=False)
                    
                    # 检查中间结果是否变化，并控制更新频率
                    current_time = time.time()
                    if interim_text and interim_text != self.last_interim_text and \
                       current_time - self.last_update_time >= self.update_interval:
                        self.last_interim_text = interim_text
                        self.interim_results.append(interim_text)
                        self.last_update_time = current_time
                        print(f"中间识别结果: {interim_text}")
                    
                    # 重置静默计数
                    silent_chunks = 0
                else:
                    # 静音处理
                    silent_chunks += 1
                    if speech_started and silent_chunks >= silence_threshold:
                        # 语音结束，处理最后的音频
                        if audio_buffer:
                            final_audio = np.concatenate(audio_buffer)
                            final_text = self.recognizer.recognize(final_audio, is_final=True)
                            if final_text:
                                print(f"最终识别结果: {final_text}")
                                if self.callback:
                                    self.callback(final_text)
                        
                        # 重置状态
                        speech_started = False
                        audio_buffer = []
                        self.interim_results = []
                        self.last_interim_text = ""
                
                # 短暂休眠，避免CPU占用过高
                time.sleep(0.01)
                
        except Exception as e:
            print(f"流式监听过程中出错: {str(e)}")
            if not self.continuous:
                self.is_listening = False
    
    def _continuous_listen(self):
        """持续监听模式，检测语音并处理"""
        while self.is_listening:
            try:
                # 等待语音输入
                audio_data = self._capture_audio_single()
                if audio_data is not None and len(audio_data) > 0:
                    self._process_audio(audio_data)
                
                # 短暂暂停，避免CPU占用过高
                time.sleep(0.1)
                
            except Exception as e:
                print(f"持续监听过程中出错: {str(e)}")
                if not self.continuous:
                    self.is_listening = False
    
    def _process_audio(self, audio_data):
        """处理音频数据"""
        try:
            # 预处理音频
            processed_audio = self.audio_processor.preprocess(audio_data)
            
            # 识别音频
            text = self.recognizer.recognize(processed_audio, is_final=True)
            
            # 如果有识别结果，调用回调函数
            if text and self.callback:
                self.callback(text)
                
        except Exception as e:
            print(f"音频处理过程中出错: {str(e)}")
    
    def _capture_audio_single(self):
        """捕获单次音频"""
        try:
            # 等待语音开始
            while self.is_listening:
                chunk = self.audio_capture.read(timeout=0.1)
                if chunk is None:
                    continue
                
                # 计算音频能量
                energy = np.sqrt(np.mean(chunk**2))
                
                if energy > self.energy_threshold:
                    # 检测到语音，开始录音
                    audio_data = []
                    silent_chunks = 0
                    
                    # 添加之前的音频（如果有）
                    if self.prev_audio_size > 0:
                        prev_audio = self.audio_capture.get_previous_audio(
                            int(self.prev_audio_size * self.audio_capture.sample_rate)
                        )
                        if prev_audio is not None:
                            audio_data.extend(prev_audio)
                    
                    # 添加当前音频块
                    audio_data.extend(chunk)
                    
                    # 继续录音直到检测到静音
                    while self.is_listening:
                        chunk = self.audio_capture.read(timeout=0.1)
                        if chunk is None:
                            continue
                        
                        # 计算音频能量
                        energy = np.sqrt(np.mean(chunk**2))
                        
                        if energy > self.energy_threshold:
                            # 检测到语音，重置静默计数
                            silent_chunks = 0
                            audio_data.extend(chunk)
                        else:
                            # 检测到静音
                            silent_chunks += 1
                            if silent_chunks >= int(self.silence_limit / 0.1):
                                # 静音时间超过阈值，结束录音
                                break
                            audio_data.extend(chunk)
                    
                    # 检查录音时长是否满足最小要求
                    if len(audio_data) >= self.min_speech_duration * self.audio_capture.sample_rate:
                        return np.array(audio_data)
                    
        except Exception as e:
            print(f"音频捕获过程中出错: {str(e)}")
        
        return None 