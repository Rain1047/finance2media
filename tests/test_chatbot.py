import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.chatbot import Chatbot

def test_chatbot():
    # 初始化对话机器人
    chatbot = Chatbot()
    
    # 测试对话
    test_messages = [
        "你好",
        "我想了解一下小红书",
        "怎么发布笔记比较好？",
        "如何增加粉丝互动？",
        "再见"
    ]
    
    print("开始测试对话机器人...\n")
    
    for message in test_messages:
        print(f"用户: {message}")
        response = chatbot.process_message(message)
        print(f"机器人: {response}\n")
    
    # 显示对话历史
    print("对话历史:")
    for msg in chatbot.get_conversation_history():
        print(f"{msg['user_id']}: {msg['message']}")

if __name__ == "__main__":
    test_chatbot() 