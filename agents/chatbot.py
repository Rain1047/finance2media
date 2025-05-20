from typing import Dict, List, Optional
import json
import os
import random
from datetime import datetime

class Chatbot:
    def __init__(self, config_path: str = "config/chatbot_config.json"):
        self.config = self._load_config(config_path)
        self.conversation_history = []
        self.templates = self._load_templates()
        self.user_info = {}
        
    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        if not os.path.exists(config_path):
            return {
                "name": "小红助手",
                "max_history": 10,
                "templates_dir": "templates/chatbot",
                "greetings": ["你好", "嗨", "很高兴见到你"],
                "farewells": ["再见", "下次见", "期待下次对话"]
            }
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_templates(self) -> Dict:
        """加载对话模板"""
        templates_dir = self.config.get("templates_dir", "templates/chatbot")
        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir)
            return {}
        
        templates = {}
        for file in os.listdir(templates_dir):
            if file.endswith('.json'):
                with open(os.path.join(templates_dir, file), 'r', encoding='utf-8') as f:
                    templates[file.replace('.json', '')] = json.load(f)
        return templates
    
    def process_message(self, message: str, user_id: str = "default") -> str:
        """处理用户消息并返回回复"""
        # 记录对话历史
        self.conversation_history.append({
            "user_id": user_id,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # 保持历史记录在限制范围内
        if len(self.conversation_history) > self.config.get("max_history", 10):
            self.conversation_history.pop(0)
        
        # 处理消息并生成回复
        response = self._generate_response(message)
        
        # 记录机器人回复
        self.conversation_history.append({
            "user_id": "bot",
            "message": response,
            "timestamp": datetime.now().isoformat()
        })
        
        return response
    
    def _generate_response(self, message: str) -> str:
        """生成回复消息"""
        # 检查是否是问候语
        if any(greeting in message for greeting in self.config.get("greetings", [])):
            return random.choice(self.config.get("greetings", ["你好"]))
        
        # 检查是否是告别语
        if any(farewell in message for farewell in self.config.get("farewells", [])):
            return random.choice(self.config.get("farewells", ["再见"]))
        
        # 根据关键词匹配模板
        for template_name, template in self.templates.items():
            if any(keyword in message for keyword in template.get("keywords", [])):
                return random.choice(template.get("responses", ["抱歉，我不太明白"]))
        
        # 默认回复
        return "抱歉，我还在学习中，暂时无法理解您的意思。"
    
    def get_conversation_history(self, user_id: str = "default") -> List[Dict]:
        """获取对话历史"""
        return [msg for msg in self.conversation_history if msg["user_id"] in [user_id, "bot"]]
    
    def clear_history(self, user_id: str = "default") -> None:
        """清除对话历史"""
        self.conversation_history = [msg for msg in self.conversation_history if msg["user_id"] != user_id] 