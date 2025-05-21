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
        """
        初始化图形界面
        
        参数:
            root: tkinter根窗口
        """
        self.root = root
        self.root.title("语音命令系统")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # 设置主题和样式
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", font=('Arial', 10))
        self.style.configure("TLabel", font=('Arial', 10))
        self.style.configure("Header.TLabel", font=('Arial', 12, 'bold'))
        
        # 初始化命令执行器
        config_path = os.path.join('config', 'voice_command', 'commands.yaml')
        self.executor = CommandExecutor(config_path, use_voice_feedback=True)
        
        # 创建界面组件
        self._create_widgets()
        
        # 初始化变量
        self.is_listening = False
        self.is_continuous = False
        self.listening_thread = None
        
        # 加载命令列表
        self._load_command_list()
        
        # 设置窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _create_widgets(self):
        """创建界面组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 顶部区域 - 标题和状态
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        header_label = ttk.Label(top_frame, text="语音命令系统", style="Header.TLabel")
        header_label.pack(side=tk.LEFT, padx=5)
        
        self.status_label = ttk.Label(top_frame, text="准备就绪")
        self.status_label.pack(side=tk.RIGHT, padx=5)
        
        # 创建分隔线
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=5)
        
        # 中间区域 - 左侧命令列表和右侧输出
        middle_frame = ttk.Frame(main_frame)
        middle_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧 - 命令列表
        left_frame = ttk.LabelFrame(middle_frame, text="可用命令")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 5), pady=5, ipadx=5, ipady=5)
        
        self.command_list = ttk.Treeview(left_frame, columns=("patterns"), height=20)
        self.command_list.heading("#0", text="命令")
        self.command_list.heading("patterns", text="匹配模式")
        self.command_list.column("#0", width=100)
        self.command_list.column("patterns", width=180)
        self.command_list.pack(fill=tk.BOTH, expand=True)
        
        # 右侧 - 输出区域和实时识别结果
        right_frame = ttk.Frame(middle_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, pady=5)
        
        # 实时识别结果区域
        recognition_frame = ttk.LabelFrame(right_frame, text="实时识别")
        recognition_frame.pack(fill=tk.X, expand=False, ipadx=5, ipady=5, pady=(0, 5))
        
        self.recognition_var = tk.StringVar()
        self.recognition_var.set("等待输入...")
        
        recognition_label = ttk.Label(
            recognition_frame, 
            textvariable=self.recognition_var,
            font=('Arial', 12),
            wraplength=450
        )
        recognition_label.pack(fill=tk.X, padx=5, pady=10)
        
        # 命令输出区域
        output_frame = ttk.LabelFrame(right_frame, text="命令输出")
        output_frame.pack(fill=tk.BOTH, expand=True, ipadx=5, ipady=5)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, width=50, height=15)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        self.output_text.config(state=tk.DISABLED)
        
        # 底部区域 - 控制按钮
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.continuous_var = tk.BooleanVar()
        continuous_check = ttk.Checkbutton(
            bottom_frame, 
            text="持续监听", 
            variable=self.continuous_var,
            command=self._on_continuous_change
        )
        continuous_check.pack(side=tk.LEFT, padx=5)
        
        self.stream_var = tk.BooleanVar(value=True)
        stream_check = ttk.Checkbutton(
            bottom_frame, 
            text="实时识别", 
            variable=self.stream_var,
            command=self._on_stream_change
        )
        stream_check.pack(side=tk.LEFT, padx=5)
        
        self.listen_button = ttk.Button(
            bottom_frame, 
            text="开始监听",
            command=self._on_listen_click
        )
        self.listen_button.pack(side=tk.LEFT, padx=5)
        
        help_button = ttk.Button(
            bottom_frame, 
            text="帮助",
            command=self._show_help
        )
        help_button.pack(side=tk.RIGHT, padx=5)
        
        clear_button = ttk.Button(
            bottom_frame, 
            text="清除输出",
            command=self._clear_output
        )
        clear_button.pack(side=tk.RIGHT, padx=5)
    
    def _load_command_list(self):
        """加载命令列表"""
        # 清空列表
        for item in self.command_list.get_children():
            self.command_list.delete(item)
        
        # 获取所有命令
        commands = self.executor.dispatcher.get_all_commands()
        
        # 添加到列表
        for cmd_name, cmd_info in commands.items():
            patterns = ", ".join(cmd_info['patterns'][:3])  # 显示前三个模式
            if len(cmd_info['patterns']) > 3:
                patterns += "..."
            
            self.command_list.insert("", tk.END, text=cmd_info['name'], values=(patterns,))
    
    def _on_listen_click(self):
        """监听按钮点击事件"""
        if not self.is_listening:
            self._start_listening()
        else:
            self._stop_listening()
    
    def _start_listening(self):
        """开始监听"""
        self.is_listening = True
        self.is_continuous = self.continuous_var.get()
        
        # 更新界面
        self.listen_button.config(text="停止监听")
        self.status_label.config(text="正在监听...")
        self._append_output("系统: 开始监听命令...\n")
        
        # 启动监听线程
        self.listening_thread = threading.Thread(target=self._listening_worker)
        self.listening_thread.daemon = True
        self.listening_thread.start()
    
    def _stop_listening(self):
        """停止监听"""
        if self.is_listening:
            self.is_listening = False
            self.executor.stop_listening()
            
            # 更新界面
            self.listen_button.config(text="开始监听")
            self.status_label.config(text="已停止监听")
            self._append_output("系统: 停止监听命令\n")
    
    def _on_stream_change(self):
        """实时识别选项改变事件"""
        use_stream = self.stream_var.get()
        if self.is_listening:
            # 如果正在监听，则停止后重新开始
            self._stop_listening()
            self._start_listening()
    
    def _update_recognition_text(self, text):
        """更新实时识别文本"""
        self.recognition_var.set(text)
    
    def _listening_worker(self):
        """监听工作线程"""
        try:
            # 启动命令执行器的监听
            if self.is_continuous:
                # 持续监听模式
                self._append_output("系统: 已开启持续监听模式，随时可以说话...\n")
                self._append_output("系统: 语音命令将在检测到语音后自动处理\n")
                self._append_output("系统: 请对着麦克风说话\n")
                
                # 设置是否使用流式识别
                use_stream = self.stream_var.get()
                
                # 定义自定义回调，用于更新界面
                original_callback = self.executor.process_command
                
                def continuous_gui_callback(text):
                    """持续监听模式的GUI回调函数"""
                    self._append_output(f"\n识别到语音命令: {text}\n")
                    result = original_callback(text)
                    if result:
                        self._append_output(f"执行结果: {result}\n")
                    self._append_output("系统: 继续监听中，随时可以说话...\n")
                    
                    # 清空识别结果文本
                    self.root.after(100, lambda: self._update_recognition_text("等待输入..."))
                    return result
                
                # 定义实时识别结果更新回调
                def interim_result_callback(text):
                    """实时识别结果回调"""
                    if text:
                        self.root.after(0, lambda: self._update_recognition_text(text))
                
                # 修改执行器的process_command方法
                self.executor.process_command = continuous_gui_callback
                
                # 创建新的监听器，使用更低的能量阈值
                self.executor.listener = None  # 确保重新初始化
                self.executor.listener = CommandListener(
                    callback=self.executor.process_command,
                    continuous=True,
                    energy_threshold=300  # 降低能量阈值，增加敏感度
                )
                
                # 设置流式识别模式
                self.executor.listener.stream_mode = use_stream
                
                # 监听模式特殊处理
                if use_stream:
                    # 修改FunASRRecognizer的缓存，以便实时获取中间结果
                    original_recognize = self.executor.listener.recognizer.recognize
                    
                    def recognize_with_interim_callback(audio, is_final=False):
                        result = original_recognize(audio, is_final)
                        # 对中间结果进行回调
                        if not is_final and result:
                            interim_result_callback(result)
                        return result
                    
                    # 替换recognize方法
                    self.executor.listener.recognizer.recognize = recognize_with_interim_callback
                
                # 启动持续监听
                self.executor.listener.start()
                
                # 保持线程运行直到停止
                while self.is_listening:
                    time.sleep(0.5)
                    
                # 停止监听并恢复原始回调
                self.executor.process_command = original_callback
                if hasattr(self.executor.listener.recognizer, 'original_recognize'):
                    self.executor.listener.recognizer.recognize = original_recognize
                self.executor.stop_listening()
                
                # 重置识别结果文本
                self.root.after(0, lambda: self._update_recognition_text("等待输入..."))
            else:
                # 单次监听模式
                self._append_output("系统: 请说出命令...\n")
                
                # 设置是否使用流式识别
                use_stream = self.stream_var.get()
                
                # 创建一个GUI回调函数
                def gui_callback(text):
                    """GUI回调函数"""
                    # 处理识别的文本
                    self._append_output(f"识别到: {text}\n")
                    
                    # 使用执行器处理命令
                    result = self.executor.process_command(text)
                    
                    if result:
                        self._append_output(f"结果: {result}\n")
                    
                    # 清空识别结果文本
                    self.root.after(100, lambda: self._update_recognition_text("等待输入..."))
                    
                    # 单次监听完成后更新界面
                    self.root.after(100, self._update_after_listen)
                
                # 定义实时识别结果更新回调
                def interim_result_callback(text):
                    """实时识别结果回调"""
                    if text:
                        self.root.after(0, lambda: self._update_recognition_text(text))
                
                # 初始化命令执行器并设置回调
                self.executor.listener = None  # 确保重新初始化
                self.executor.listener = CommandListener(
                    callback=gui_callback,
                    continuous=False,
                    energy_threshold=300  # 降低能量阈值，增加敏感度
                )
                
                # 设置流式识别模式
                self.executor.listener.stream_mode = use_stream
                
                # 监听模式特殊处理
                if use_stream:
                    # 修改FunASRRecognizer的缓存，以便实时获取中间结果
                    original_recognize = self.executor.listener.recognizer.recognize
                    
                    def recognize_with_interim_callback(audio, is_final=False):
                        result = original_recognize(audio, is_final)
                        # 对中间结果进行回调
                        if not is_final and result:
                            interim_result_callback(result)
                        return result
                    
                    # 替换recognize方法
                    self.executor.listener.recognizer.recognize = recognize_with_interim_callback
                
                # 启动监听
                self.executor.listener.start()
        except Exception as e:
            error_msg = f"监听过程中出错: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self._append_output(f"错误: {error_msg}\n")
            
            # 发生错误时更新界面
            self.root.after(100, self._update_after_listen)
    
    def _update_after_listen(self):
        """监听完成后更新界面"""
        if not self.is_continuous:
            self.is_listening = False
            self.listen_button.config(text="开始监听")
            self.status_label.config(text="准备就绪")
    
    def _on_continuous_change(self):
        """持续监听选项改变事件"""
        if self.is_listening:
            # 如果正在监听，则停止后重新开始
            self._stop_listening()
            self._start_listening()
    
    def _append_output(self, text):
        """添加文本到输出区域"""
        def _update():
            self.output_text.config(state=tk.NORMAL)
            self.output_text.insert(tk.END, text)
            self.output_text.see(tk.END)
            self.output_text.config(state=tk.DISABLED)
        
        # 在主线程中更新UI
        self.root.after(0, _update)
    
    def _clear_output(self):
        """清除输出区域"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
    
    def _show_help(self):
        """显示帮助信息"""
        help_text = """语音命令系统使用说明:

1. 点击"开始监听"按钮开始语音输入
2. 说出您想执行的命令
3. 系统会识别并执行相应的操作
4. 勾选"持续监听"可以让系统一直监听命令
5. 勾选"实时识别"可以查看边说边识别的结果

左侧列表显示了所有可用的命令和匹配模式。
尝试使用这些命令或类似的表述。

常用命令示例:
- 系统信息
- 列出文件
- 创建文件 test.txt
- 删除文件 test.txt

实时识别会在您说话的同时显示识别结果，
让您能够更快地了解系统理解了什么。
"""
        messagebox.showinfo("使用帮助", help_text)
    
    def _on_close(self):
        """窗口关闭事件"""
        # 停止监听
        self._stop_listening()
        
        # 确保TTS停止
        if self.executor.tts:
            self.executor.tts.stop_playback_thread()
        
        # 关闭窗口
        self.root.destroy()


def main():
    """主函数"""
    try:
        # 创建tkinter根窗口
        root = tk.Tk()
        
        # 初始化应用
        app = VoiceCommandGUI(root)
        
        # 启动主循环
        root.mainloop()
    except Exception as e:
        logger.error(f"应用启动错误: {str(e)}", exc_info=True)
        messagebox.showerror("错误", f"应用启动失败: {str(e)}")


if __name__ == "__main__":
    main() 