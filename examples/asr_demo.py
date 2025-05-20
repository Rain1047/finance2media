"""
ASR 功能演示
"""

import os
import time
from src.asr import AudioCapture, AudioProcessor, FunASRRecognizer

def main():
    # 创建必要的目录
    os.makedirs('models/funasr', exist_ok=True)
    
    # 初始化组件
    audio_capture = AudioCapture()
    audio_processor = AudioProcessor()
    recognizer = FunASRRecognizer()
    
    def error_callback(error_msg):
        print(f"错误: {error_msg}")
    
    def result_callback(result):
        print(f"识别结果: {result}")
    
    try:
        # 启动识别器
        recognizer.start(error_callback)
        
        # 开始录音
        print("开始录音，请说话...")
        audio_capture.start(error_callback)
        
        # 收集音频数据
        audio_chunks = []
        start_time = time.time()
        
        while time.time() - start_time < 10:  # 录音10秒
            audio_data = audio_capture.read(timeout=1.0)
            if audio_data is not None:
                # 预处理音频数据
                processed_audio = audio_processor.preprocess(audio_data)
                audio_chunks.append(processed_audio)
        
        # 停止录音
        audio_capture.stop()
        print("录音结束")
        
        # 识别音频
        print("开始识别...")
        result = recognizer.recognize_stream(audio_chunks, result_callback)
        print(f"最终识别结果: {result}")
        
    except Exception as e:
        print(f"发生错误: {str(e)}")
    finally:
        # 清理资源
        audio_capture.stop()
        recognizer.stop()

if __name__ == "__main__":
    main() 