"""
图形界面语音命令系统示例

此示例演示如何构建一个带有图形界面的语音命令系统，
提供更好的用户体验和可视化反馈。
"""

import os
import sys
import logging
import time
import threading
import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
import queue
import json
import wave
import numpy as np
import torch
import torchaudio
from funasr import AutoModel
import pygame
import tempfile
import sounddevice as sd
import soundfile as sf
from datetime import datetime

# 将当前目录添加到路径中，以便导入模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.voice_command.command_executor import CommandExecutor
from src.voice_command.command_listener import CommandListener

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('voice_command.log')
    ]
)

logger = logging.getLogger(__name__)

class VoiceCommandGUI:
    """语音命令系统图形界面"""
    
    def __init__(self, root):
        """初始化GUI界面"""
        self.root = root
        self.root.title("语音命令系统")
        self.root.geometry("800x600")
        
        # 创建消息队列用于线程间通信
        self.message_queue = queue.Queue()
        
        # 初始化命令执行器
        config_path = os.path.join('config', 'voice_command', 'commands.yaml')
        self.executor = CommandExecutor(config_path)
        
        # 初始化语音识别模型
        self.model = AutoModel(
            model="paraformer",
            vad_model="fsmn-vad",
            vad_kwargs={"max_single_segment_time": 30000},
            punc_model="ct-punc",
            punc_kwargs={},
        )
        
        # 设置样式
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#4CAF50")
        self.style.configure("TLabel", padding=6)
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 状态标签
        self.status_label = ttk.Label(self.main_frame, text="准备就绪", font=("Arial", 12))
        self.status_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # 实时识别结果显示
        self.recognition_frame = ttk.LabelFrame(self.main_frame, text="实时识别", padding="5")
        self.recognition_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.recognition_text = tk.Text(self.recognition_frame, height=3, wrap=tk.WORD, font=("Arial", 12))
        self.recognition_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.recognition_text.config(state=tk.DISABLED)
        
        # 命令历史显示
        self.history_frame = ttk.LabelFrame(self.main_frame, text="命令历史", padding="5")
        self.history_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.history_text = scrolledtext.ScrolledText(self.history_frame, wrap=tk.WORD, height=20)
        self.history_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.history_text.config(state=tk.DISABLED)
        
        # 添加滚动条
        history_scrollbar = ttk.Scrollbar(self.history_frame, orient=tk.VERTICAL, command=self.history_text.yview)
        history_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.history_text['yscrollcommand'] = history_scrollbar.set
        
        # 控制按钮
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.listen_button = ttk.Button(self.button_frame, text="开始监听", command=self._toggle_listening)
        self.listen_button.grid(row=0, column=0, padx=5)
        
        self.clear_button = ttk.Button(self.button_frame, text="清除历史", command=self._clear_history)
        self.clear_button.grid(row=0, column=1, padx=5)
        
        # 模式选择
        self.mode_frame = ttk.LabelFrame(self.main_frame, text="识别模式", padding="5")
        self.mode_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.mode_var = tk.StringVar(value="stream")
        ttk.Radiobutton(self.mode_frame, text="流式识别", variable=self.mode_var, value="stream").grid(row=0, column=0, padx=5)
        ttk.Radiobutton(self.mode_frame, text="普通识别", variable=self.mode_var, value="normal").grid(row=0, column=1, padx=5)
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(2, weight=1)
        self.history_frame.columnconfigure(0, weight=1)
        self.history_frame.rowconfigure(0, weight=1)
        
        # 初始化变量
        self.is_listening = False
        self.is_processing = False
        self.audio_data = []
        self.sample_rate = 16000
        self.listener_thread = None
        
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # 设置窗口图标
        try:
            self.root.iconbitmap("assets/icon.ico")
        except:
            pass
        
        # 启动消息处理
        self._process_messages()
        
    def _process_messages(self):
        try:
            while True:
                # 从队列中获取消息
                msg_type, msg_content = self.message_queue.get_nowait()
                
                if msg_type == 'append':
                    # 在主线程中更新GUI
                    self.history_text.config(state=tk.NORMAL)
                    self.history_text.insert(tk.END, msg_content)
                    self.history_text.see(tk.END)
                    self.history_text.config(state=tk.DISABLED)
                    
                self.message_queue.task_done()
        except queue.Empty:
            pass
        finally:
            # 每100ms检查一次消息队列
            self.root.after(100, self._process_messages)

    def _update_recognition_text(self, text):
        """更新实时识别文本"""
        self.recognition_text.config(state=tk.NORMAL)
        self.recognition_text.delete(1.0, tk.END)
        self.recognition_text.insert(tk.END, text)
        self.recognition_text.config(state=tk.DISABLED)
        self.recognition_text.see(tk.END)
        
        # 设置文本颜色
        self.recognition_text.tag_configure("interim", foreground="blue")
        self.recognition_text.tag_configure("final", foreground="green")
        
        # 根据文本类型设置不同的颜色
        if text.endswith("..."):  # 中间结果
            self.recognition_text.tag_add("interim", "1.0", "end")
        else:  # 最终结果
            self.recognition_text.tag_add("final", "1.0", "end")
    
    def _append_output(self, text):
        """添加输出到历史记录"""
        self.history_text.config(state=tk.NORMAL)
        self.history_text.insert(tk.END, text + "\n")
        self.history_text.config(state=tk.DISABLED)
        self.history_text.see(tk.END)
        
        # 设置不同类型文本的颜色
        self.history_text.tag_configure("command", foreground="blue")
        self.history_text.tag_configure("result", foreground="green")
        self.history_text.tag_configure("error", foreground="red")
        
        # 根据文本内容设置不同的颜色
        if text.startswith("命令:"):
            self.history_text.tag_add("command", "end-2c linestart", "end-1c")
        elif text.startswith("结果:"):
            self.history_text.tag_add("result", "end-2c linestart", "end-1c")
        elif text.startswith("错误:"):
            self.history_text.tag_add("error", "end-2c linestart", "end-1c")

    def _toggle_listening(self):
        """切换监听状态"""
        if not self.is_listening:
            self._start_listening()
        else:
            self._stop_listening()
            
    def _start_listening(self):
        """开始监听"""
        self.is_listening = True
        self.listen_button.config(text="停止监听")
        self.status_label.config(text="正在监听...")
        self.listener_thread = threading.Thread(target=self._listening_worker)
        self.listener_thread.daemon = True
        self.listener_thread.start()
        
    def _stop_listening(self):
        """停止监听"""
        self.is_listening = False
        self.listen_button.config(text="开始监听")
        self.status_label.config(text="准备就绪")
        if self.listener_thread:
            self.listener_thread.join(timeout=1.0)
            
    def _listening_worker(self):
        """监听工作线程"""
        try:
            # 设置音频参数
            channels = 1
            dtype = np.float32
            
            # 创建音频流
            stream = sd.InputStream(
                channels=channels,
                samplerate=self.sample_rate,
                dtype=dtype,
                blocksize=int(self.sample_rate * 0.5),  # 0.5秒的块大小
                callback=self._audio_callback
            )
            
            with stream:
                while self.is_listening:
                    time.sleep(0.1)
                    
        except Exception as e:
            logger.error(f"监听错误: {str(e)}")
            self.message_queue.put(('append', f"错误: 监听过程中发生错误 - {str(e)}"))
            self._stop_listening()
            
    def _audio_callback(self, indata, frames, time, status):
        """音频回调函数"""
        if status:
            logger.warning(f"音频回调状态: {status}")
            
        if self.is_listening:
            # 将音频数据添加到缓冲区
            self.audio_data.extend(indata[:, 0])
            
            # 当缓冲区达到一定大小时进行识别
            if len(self.audio_data) >= self.sample_rate * 2:  # 2秒的数据
                audio_chunk = np.array(self.audio_data[:self.sample_rate * 2])
                self.audio_data = self.audio_data[self.sample_rate:]
                
                # 使用 FunASR 进行识别
                try:
                    result = self.model.generate(input=audio_chunk)
                    text = result[0]["text"]
                    
                    if text.strip():
                        # 更新识别结果
                        self._update_recognition_text(text)
                        
                        # 执行命令
                        try:
                            result = self.executor.execute_command(text)
                            self.message_queue.put(('append', f"命令: {text}"))
                            self.message_queue.put(('append', f"结果: {result}"))
                        except Exception as e:
                            logger.error(f"命令执行错误: {str(e)}")
                            self.message_queue.put(('append', f"错误: 命令执行失败 - {str(e)}"))
                            
                except Exception as e:
                    logger.error(f"识别错误: {str(e)}")
                    self.message_queue.put(('append', f"错误: 识别失败 - {str(e)}"))
                    
    def _update_after_listen(self):
        """监听结束后的更新"""
        self.listen_button.config(text="开始监听")
        self.status_label.config(text="准备就绪")
        
    def _clear_history(self):
        """清除历史记录"""
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete(1.0, tk.END)
        self.history_text.config(state=tk.DISABLED)
        
    def _on_closing(self):
        """窗口关闭时的处理"""
        if self.is_listening:
            self._stop_listening()
        self.root.destroy()
        
def main():
    """主函数"""
    root = tk.Tk()
    app = VoiceCommandGUI(root)
    root.mainloop()
    
if __name__ == "__main__":
    main() 