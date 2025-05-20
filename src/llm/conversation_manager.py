import os
import json
import time
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime

# 尝试导入LangChain相关库
try:
    from langchain.llms import LlamaCpp
    from langchain.prompts import PromptTemplate
    from langchain.chains import ConversationChain
    from langchain.memory import ConversationBufferMemory
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("LangChain 未安装，将使用模拟LLM")

class ConversationManager:
    """对话管理器，负责管理对话上下文和调用LLM生成回复"""
    
    def __init__(self, config: Dict = None):
        """
        初始化对话管理器
        
        Args:
            config: 配置参数，包括模型路径、对话历史长度等
        """
        self.config = config or {
            "model_path": "models/chatglm-cpp.bin",  # 本地模型路径
            "max_history": 10,                     # 最大对话历史长度
            "temperature": 0.7,                    # 生成多样性
            "max_tokens": 256,                     # 最大生成长度
            "use_mock": not LLM_AVAILABLE,         # 是否使用模拟LLM
            "save_dir": "data/conversations",      # 对话保存目录
        }
        
        self.model = None
        self.memory = None
        self.conversation_chain = None
        self.conversation_history = []
        
        # 初始化目录
        os.makedirs(self.config["save_dir"], exist_ok=True)
        
        # 如果不使用模拟，则初始化模型
        if not self.config["use_mock"]:
            self._initialize_model()
    
    def _initialize_model(self):
        """初始化LLM模型和对话链"""
        try:
            print("正在加载LLM模型...")
            
            # 如果使用LlamaCpp
            self.model = LlamaCpp(
                model_path=self.config["model_path"],
                temperature=self.config["temperature"],
                max_tokens=self.config["max_tokens"],
                n_ctx=2048,
                verbose=False
            )
            
            # 初始化记忆模块
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
            
            # 创建对话链
            self.conversation_chain = ConversationChain(
                llm=self.model,
                memory=self.memory,
                verbose=False
            )
            
            print("LLM模型加载完成")
        except Exception as e:
            print(f"加载模型失败: {str(e)}")
            self.config["use_mock"] = True
            
    def process_message(self, message: str, user_id: str = "default") -> str:
        """
        处理用户消息并生成回复
        
        Args:
            message: 用户消息
            user_id: 用户ID
            
        Returns:
            LLM生成的回复
        """
        # 记录用户消息
        self._add_to_history(user_id, "user", message)
        
        # 生成回复
        if self.config["use_mock"]:
            response = self._mock_llm_response(message)
        else:
            response = self._generate_response(message)
        
        # 记录系统回复
        self._add_to_history(user_id, "assistant", response)
        
        # 保存对话历史
        self._save_conversation(user_id)
        
        return response
    
    def _generate_response(self, message: str) -> str:
        """使用LLM生成回复"""
        try:
            response = self.conversation_chain.predict(input=message)
            return response
        except Exception as e:
            print(f"生成回复失败: {str(e)}")
            return "抱歉，我遇到了一些技术问题，无法正常回复。"
    
    def _mock_llm_response(self, message: str) -> str:
        """模拟LLM回复，用于开发和测试"""
        time.sleep(1.5)  # 模拟延迟
        
        # 简单的关键词匹配
        if "你好" in message or "嗨" in message:
            return "你好！很高兴见到你，有什么我可以帮助你的吗？"
        
        if "小红书" in message:
            return "小红书是一个生活方式分享平台，用户可以通过短视频、图文等形式分享生活经验和创意。你想了解小红书的哪些方面呢？"
        
        if "财经" in message or "金融" in message:
            return "财经和金融领域涉及投资、股票、经济分析等多个方面。您对哪个具体方面感兴趣？我可以提供相关信息。"
            
        if "谢谢" in message or "感谢" in message:
            return "不客气！如果还有其他问题，随时可以问我。"
            
        # 默认回复
        return "这是个有趣的话题。作为AI助手，我很乐意继续讨论这个话题，或者我们可以聊聊其他你感兴趣的事情。"
    
    def _add_to_history(self, user_id: str, role: str, message: str) -> None:
        """添加消息到对话历史"""
        self.conversation_history.append({
            "user_id": user_id,
            "role": role,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # 保持历史在限制范围内
        if len(self.conversation_history) > self.config["max_history"] * 2:
            self.conversation_history = self.conversation_history[-self.config["max_history"]*2:]
    
    def _save_conversation(self, user_id: str) -> None:
        """保存对话历史到文件"""
        filename = os.path.join(self.config["save_dir"], f"{user_id}_{datetime.now().strftime('%Y%m%d')}.json")
        
        # 筛选当前用户的对话
        user_history = [msg for msg in self.conversation_history if msg["user_id"] == user_id]
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(user_history, f, ensure_ascii=False, indent=2)
    
    def get_conversation_history(self, user_id: str, max_entries: int = None) -> List[Dict]:
        """获取指定用户的对话历史"""
        history = [msg for msg in self.conversation_history if msg["user_id"] == user_id]
        
        if max_entries:
            return history[-max_entries:]
        return history
    
    def clear_history(self, user_id: str = None) -> None:
        """清除对话历史"""
        if user_id:
            self.conversation_history = [msg for msg in self.conversation_history if msg["user_id"] != user_id]
            if not self.config["use_mock"] and self.memory:
                self.memory.clear()
        else:
            self.conversation_history = []
            if not self.config["use_mock"] and self.memory:
                self.memory.clear() 