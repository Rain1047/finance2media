import sys
import os
import time
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.voice_robot.voice_assistant import VoiceAssistant

def test_voice_assistant():
    """测试语音助手的基本功能"""
    print("开始测试语音助手...")
    
    # 创建语音助手实例
    assistant = VoiceAssistant({
        "user_id": "test_user",
        "wake_word": "开始测试",
        "exit_phrases": ["测试结束", "退出测试"],
    })
    
    # 设置回调函数
    def on_wake():
        print("助手被唤醒")
    
    def on_error(error_msg):
        print(f"发生错误: {error_msg}")
    
    assistant.set_callbacks(on_wake=on_wake, on_error=on_error)
    
    try:
        # 启动助手
        print("\n=== 测试1: 基本对话 ===")
        print("请说'开始测试'来唤醒助手")
        assistant.start()
        
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
    finally:
        assistant.stop()
        print("\n测试结束")

def test_conversation_history():
    """测试对话历史功能"""
    print("\n=== 测试2: 对话历史 ===")
    
    assistant = VoiceAssistant({
        "user_id": "history_test_user",
    })
    
    # 模拟一些对话
    test_messages = [
        "你好",
        "今天天气怎么样？",
        "谢谢你的回答",
    ]
    
    for message in test_messages:
        print(f"\n用户: {message}")
        response = assistant.llm.process_message(message)
        print(f"助手: {response}")
    
    # 获取对话历史
    history = assistant.get_conversation_history()
    print("\n对话历史:")
    for entry in history:
        print(f"{entry['role']}: {entry['message']}")
    
    # 清除历史
    assistant.clear_history()
    print("\n已清除对话历史")

if __name__ == "__main__":
    print("=== 语音助手测试程序 ===")
    print("时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # 运行测试
    test_voice_assistant()
    test_conversation_history() 