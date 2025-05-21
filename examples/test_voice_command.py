"""
语音命令系统测试脚本

此脚本提供了一个简单的接口来测试语音命令系统的基本功能。
它首先测试音频捕获和语音识别，然后测试命令分发和执行。
"""

import os
import sys
import logging
import time

# 将当前目录添加到路径中，以便导入模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger(__name__)

def test_audio_capture():
    """测试音频捕获功能"""
    from src.asr.audio_capture import AudioCapture
    from src.asr.audio_processor import AudioProcessor
    import numpy as np
    
    print("===== 测试音频捕获 =====")
    
    # 初始化音频捕获器
    capture = AudioCapture()
    processor = AudioProcessor()
    
    # 录制音频
    try:
        print("准备录音...")
        capture.start()
        
        print("正在录音（3秒）...")
        audio_chunks = []
        
        # 录音3秒
        start_time = time.time()
        while time.time() - start_time < 3:
            chunk = capture.read(timeout=0.1)
            if chunk is not None:
                audio_chunks.append(chunk)
            time.sleep(0.01)
        
        print("录音完成")
        capture.stop()
        
        # 检查录音结果
        if not audio_chunks:
            print("错误：没有录到音频数据")
            return False
        
        # 合并音频块
        audio_data = np.concatenate(audio_chunks)
        
        # 检查音频数据
        print(f"音频数据形状: {audio_data.shape}")
        print(f"数据类型: {audio_data.dtype}")
        print(f"音频长度: {len(audio_data)/16000:.2f}秒")
        
        # 处理音频
        processed = processor.preprocess(audio_data)
        print(f"处理后音频形状: {processed.shape}")
        
        print("音频捕获测试成功")
        return True
        
    except Exception as e:
        print(f"音频捕获测试失败: {str(e)}")
        if capture:
            capture.stop()
        return False

def test_speech_recognition():
    """测试语音识别功能"""
    from src.asr.audio_capture import AudioCapture
    from src.asr.audio_processor import AudioProcessor
    from src.asr.funasr_recognizer import FunASRRecognizer
    import numpy as np
    
    print("\n===== 测试语音识别 =====")
    
    # 初始化组件
    capture = AudioCapture()
    processor = AudioProcessor()
    recognizer = FunASRRecognizer()
    
    # 录制并识别
    try:
        print("请准备好说一句话...")
        time.sleep(1)
        
        # 启动录音
        capture.start()
        print("开始录音（3秒）...")
        
        # 录音3秒
        audio_chunks = []
        start_time = time.time()
        while time.time() - start_time < 3:
            chunk = capture.read(timeout=0.1)
            if chunk is not None:
                audio_chunks.append(chunk)
            time.sleep(0.01)
        
        print("录音结束，正在识别...")
        capture.stop()
        
        if not audio_chunks:
            print("错误：没有录到音频数据")
            return False
        
        # 合并音频块
        audio_data = np.concatenate(audio_chunks)
        
        # 处理音频
        processed = processor.preprocess(audio_data)
        
        # 识别
        text = recognizer.recognize(processed)
        
        print(f"识别结果: '{text}'")
        
        if text:
            print("语音识别测试成功")
            return True
        else:
            print("警告: 识别结果为空")
            return False
            
    except Exception as e:
        print(f"语音识别测试失败: {str(e)}")
        if capture:
            capture.stop()
        return False

def test_command_execution():
    """测试命令执行功能"""
    from src.voice_command.command_executor import CommandExecutor
    import os
    
    print("\n===== 测试命令执行 =====")
    
    # 确保配置文件存在
    config_path = os.path.join('config', 'voice_command', 'commands.yaml')
    if not os.path.exists(config_path):
        print(f"错误: 配置文件不存在: {config_path}")
        return False
    
    # 初始化命令执行器
    try:
        executor = CommandExecutor(config_path)
        
        # 列出当前目录
        print("\n测试 '当前目录' 命令...")
        result = executor.process_command("当前目录")
        print(f"执行结果: {result}")
        
        # 列出文件
        print("\n测试 '列出文件' 命令...")
        result = executor.process_command("列出文件")
        print(f"执行结果: {result}")
        
        # 系统信息
        print("\n测试 '系统信息' 命令...")
        result = executor.process_command("系统信息")
        print(f"执行结果: {result}")
        
        print("命令执行测试成功")
        return True
        
    except Exception as e:
        print(f"命令执行测试失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("="*50)
    print("     语音命令系统测试")
    print("="*50)
    
    try:
        # 测试音频捕获
        if not test_audio_capture():
            print("音频捕获测试未通过，终止测试")
            return
        
        # 测试语音识别
        if not test_speech_recognition():
            print("语音识别测试未通过，继续测试")
        
        # 测试命令执行
        test_command_execution()
        
        print("\n所有测试完成")
        
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试过程中出错: {str(e)}")

if __name__ == "__main__":
    main() 