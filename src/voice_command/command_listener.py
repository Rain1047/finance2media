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
        self.silence_limit = 1.0  # 静默超过1秒视为语音结束
        self.prev_audio_size = 0.5  # 保留语音前0.5秒的音频
        self.min_speech_duration = 0.5  # 最短语音持续时间
        
        # 流式识别相关
        self.stream_mode = True  # 是否使用流式识别
        self.interim_results = []  # 中间识别结果
        self.last_interim_text = ""  # 上一次的中间结果
    
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
        chunk_duration = 0.1  # 每块0.1秒
        silence_threshold = int(self.silence_limit / chunk_duration)  # 静默阈值（块数）
        
        # 初始化识别会话的缓存
        self.recognizer._cache = {}
        
        try:
            print("实时语音识别监听中...")
            while self.is_listening:
                # 读取音频数据
                chunk = self.audio_capture.read(timeout=0.1)
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
                        # 重置识别器缓存
                        self.recognizer._cache = {}
                    
                    # 预处理音频块
                    processed_chunk = self.audio_processor.preprocess(chunk)
                    
                    # 将音频块添加到缓冲区
                    audio_buffer.append(processed_chunk)
                    
                    # 流式识别，这里is_final设为False表示不是最后一块
                    interim_text = self.recognizer.recognize(processed_chunk, is_final=False)
                    
                    # 检查中间结果是否变化
                    if interim_text and interim_text != self.last_interim_text:
                        self.last_interim_text = interim_text
                        self.interim_results.append(interim_text)
                        print(f"中间识别结果: {interim_text}")
                    
                    # 重置静默计数
                    silent_chunks = 0
                    
                elif speech_started:
                    # 语音之后的静默
                    silent_chunks += 1
                    
                    # 静默超过阈值，认为语音结束
                    if silent_chunks >= silence_threshold:
                        speech_duration = len(audio_buffer) * chunk_duration
                        if speech_duration >= self.min_speech_duration:
                            print(f"语音结束，持续时间: {speech_duration:.2f}秒")
                            
                            # 处理最后一块，获取最终结果
                            if audio_buffer:
                                # 使用最后一个音频块进行最终识别，is_final设为True
                                final_text = self.recognizer.recognize(audio_buffer[-1], is_final=True)
                                print(f"最终识别结果: {final_text}")
                                
                                # 如果最终结果为空，但有中间结果，则使用最后一个中间结果
                                if not final_text and self.interim_results:
                                    final_text = self.interim_results[-1]
                                    print(f"使用中间结果: {final_text}")
                                
                                # 回调处理
                                if final_text and self.callback:
                                    self.callback(final_text)
                        else:
                            print("语音太短，忽略")
                            
                        # 重置状态
                        speech_started = False
                        silent_chunks = 0
                        audio_buffer = []
                        self.interim_results = []
                        self.last_interim_text = ""
                
                # 短暂休眠
                time.sleep(0.01)
                
        except Exception as e:
            print(f"流式监听出错: {str(e)}")
        finally:
            # 确保停止识别器
            self.recognizer.stop()
    
    def _continuous_listen(self):
        """非流式持续监听模式，检测语音并处理"""
        # 启动音频缓冲
        audio_buffer = []
        silent_chunks = 0
        speech_started = False
        
        # 保存语音之前的一小段音频
        prev_audio = []
        
        # 采样率和每个数据块时长
        sample_rate = 16000  # 16kHz，标准ASR采样率
        chunk_duration = 0.1  # 每块0.1秒
        silence_threshold = int(self.silence_limit / chunk_duration)  # 静默阈值（块数）
        
        try:
            print("持续监听中...")
            while self.is_listening:
                # 读取音频数据
                chunk = self.audio_capture.read(timeout=0.1)
                if chunk is None:
                    time.sleep(0.01)
                    continue
                
                # 计算音频能量
                energy = np.sqrt(np.mean(chunk**2))
                
                if energy > self.energy_threshold:
                    # 检测到语音
                    if not speech_started:
                        print("检测到语音...")
                        speech_started = True
                        # 将之前的一小段音频添加到缓冲区
                        audio_buffer.extend(prev_audio)
                    
                    # 添加到缓冲区
                    audio_buffer.append(chunk)
                    silent_chunks = 0
                elif speech_started:
                    # 语音之后的静默
                    audio_buffer.append(chunk)
                    silent_chunks += 1
                    
                    # 静默超过阈值，认为语音结束
                    if silent_chunks >= silence_threshold:
                        speech_duration = len(audio_buffer) * chunk_duration
                        if speech_duration >= self.min_speech_duration:
                            print(f"语音结束，持续时间: {speech_duration:.2f}秒")
                            # 处理完整音频
                            if audio_buffer:
                                audio_data = np.concatenate(audio_buffer)
                                self._process_audio(audio_data)
                        else:
                            print("语音太短，忽略")
                            
                        # 重置状态
                        audio_buffer = []
                        speech_started = False
                        silent_chunks = 0
                else:
                    # 保存语音前的一小段音频
                    prev_audio.append(chunk)
                    # 保持prev_audio的大小
                    if len(prev_audio) > int(self.prev_audio_size / chunk_duration):
                        prev_audio.pop(0)
                
                # 短暂休眠
                time.sleep(0.01)
                
        except Exception as e:
            print(f"持续监听出错: {str(e)}")
    
    def _process_audio(self, audio_data):
        """处理音频数据"""
        # 处理音频
        processed_audio = self.audio_processor.preprocess(audio_data)
        
        # 语音识别
        text = self.recognizer.recognize(processed_audio, is_final=True)
        print(f"识别结果: {text}")
        
        # 回调处理
        if text and self.callback:
            self.callback(text)
    
    def _capture_audio_single(self):
        """
        单次捕获音频
        
        返回:
            numpy.ndarray: 音频数据
        """
        # 开始录音
        audio_chunks = []
        try:
            # 录音持续约3秒钟
            start_time = time.time()
            recording_duration = 3  # 3秒
            
            print("开始录音...")
            while time.time() - start_time < recording_duration:
                # 读取音频数据
                chunk = self.audio_capture.read(timeout=0.1)
                if chunk is not None:
                    audio_chunks.append(chunk)
                time.sleep(0.01)  # 短暂休眠
            
            print("录音完成")
            
            # 将所有块连接起来
            if audio_chunks:
                return np.concatenate(audio_chunks)
            else:
                return np.array([])
                
        except Exception as e:
            print(f"录音出错: {str(e)}")
            return np.array([]) 