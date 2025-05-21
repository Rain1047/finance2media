"""
命令分发器模块

此模块负责加载命令配置，并将文本命令分发给相应的命令处理器。
"""

import re
import importlib
import yaml
import os
from pathlib import Path
import logging
from difflib import SequenceMatcher

# 配置日志
logger = logging.getLogger(__name__)

class CommandDispatcher:
    """命令分发器，负责查找和分发命令"""
    
    def __init__(self, config_path=None):
        """
        初始化命令分发器
        
        参数:
            config_path (str): 命令配置文件路径
        """
        self.commands = {}
        self.command_patterns = {}
        self.command_keywords = {}  # 存储每个命令的关键词，用于模糊匹配
        
        # 加载配置文件
        self.config_path = config_path or os.path.join('config', 'voice_command', 'commands.yaml')
        self._load_config()
        
        # 加载所有命令
        self._load_commands()
    
    def _load_config(self):
        """加载命令配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            logger.info(f"已加载命令配置: {self.config_path}")
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            self.config = {"commands": {}}
    
    def _load_commands(self):
        """加载所有命令"""
        if not hasattr(self, 'config') or not self.config:
            logger.warning("没有可用的命令配置")
            return
            
        command_modules = self.config.get('commands', {})
        
        # 遍历配置的命令模块
        for cmd_name, cmd_info in command_modules.items():
            module_path = cmd_info.get('module')
            class_name = cmd_info.get('class')
            patterns = cmd_info.get('patterns', [])
            
            try:
                # 动态导入命令模块
                module = importlib.import_module(module_path)
                cmd_class = getattr(module, class_name)
                
                # 实例化命令
                cmd_instance = cmd_class()
                
                # 注册命令
                self.commands[cmd_name] = cmd_instance
                
                # 编译正则表达式模式
                compiled_patterns = []
                for pattern in patterns:
                    if isinstance(pattern, str):
                        compiled_patterns.append(pattern)
                    else:
                        # 假设是正则表达式模式
                        try:
                            compiled_patterns.append(re.compile(pattern))
                        except Exception as e:
                            logger.error(f"编译正则表达式失败: {pattern} - {str(e)}")
                
                self.command_patterns[cmd_name] = compiled_patterns
                
                # 存储命令关键词，用于模糊匹配
                keywords = []
                for pattern in patterns:
                    if isinstance(pattern, str):
                        keywords.extend(pattern.lower().split())
                self.command_keywords[cmd_name] = list(set(keywords))  # 去重
                
                logger.info(f"已加载命令: {cmd_name}")
            except Exception as e:
                logger.error(f"加载命令 {cmd_name} 失败: {str(e)}")
    
    def dispatch(self, text):
        """
        根据文本分发命令
        
        参数:
            text (str): 命令文本
            
        返回:
            tuple: (命令实例, 文本) 或 (None, 错误信息)
        """
        if not text:
            return None, "空命令"
            
        matched_cmd = None
        max_score = 0
        
        # 查找匹配度最高的命令
        for cmd_name, patterns in self.command_patterns.items():
            for pattern in patterns:
                if isinstance(pattern, str):
                    # 字符串模式直接查找
                    if pattern.lower() in text.lower():
                        score = len(pattern) / len(text)
                        if score > max_score:
                            max_score = score
                            matched_cmd = cmd_name
                elif hasattr(pattern, 'search'):
                    # 正则表达式模式
                    match = pattern.search(text)
                    if match:
                        score = (match.end() - match.start()) / len(text)
                        if score > max_score:
                            max_score = score
                            matched_cmd = cmd_name
        
        # 找到匹配的命令
        if matched_cmd and max_score > 0.3:  # 设置一个最小匹配阈值
            logger.info(f"命令 '{text}' 匹配到: {matched_cmd}，匹配度: {max_score:.2f}")
            return self.commands[matched_cmd], text
        
        # 查找相似命令，用于提示
        similar_commands = self._find_similar_commands(text)
        
        if similar_commands:
            # 构建建议消息
            suggestions = [f"{cmd_name}：{self._get_command_example(cmd_name)}" for cmd_name in similar_commands[:3]]
            suggestion = f"未找到精确匹配的命令。您是否想要: \n" + "\n".join(suggestions)
            logger.info(suggestion)
            return None, suggestion
        
        logger.info(f"命令 '{text}' 没有匹配到任何命令")
        return None, "未找到匹配的命令，请尝试其他表述方式或查看帮助"
    
    def _find_similar_commands(self, text, threshold=0.3):
        """
        查找与文本相似的命令
        
        参数:
            text (str): 命令文本
            threshold (float): 相似度阈值
            
        返回:
            list: 相似命令列表
        """
        similar_commands = []
        text_words = set(text.lower().split())
        
        # 1. 关键词匹配
        for cmd_name, keywords in self.command_keywords.items():
            common_words = text_words.intersection(keywords)
            if common_words:
                similarity = len(common_words) / max(len(text_words), len(keywords))
                if similarity >= threshold:
                    similar_commands.append((cmd_name, similarity))
        
        # 2. 使用序列匹配算法进行模糊匹配
        for cmd_name, patterns in self.command_patterns.items():
            for pattern in patterns:
                if isinstance(pattern, str):
                    similarity = SequenceMatcher(None, text.lower(), pattern.lower()).ratio()
                    if similarity >= threshold:
                        similar_commands.append((cmd_name, similarity))
        
        # 去重并按相似度排序
        unique_commands = {}
        for cmd_name, similarity in similar_commands:
            if cmd_name not in unique_commands or similarity > unique_commands[cmd_name]:
                unique_commands[cmd_name] = similarity
                
        sorted_commands = sorted(unique_commands.items(), key=lambda x: x[1], reverse=True)
        
        return [cmd for cmd, _ in sorted_commands]
    
    def _get_command_example(self, cmd_name):
        """
        获取命令的用法示例
        
        参数:
            cmd_name (str): 命令名称
            
        返回:
            str: 命令示例
        """
        patterns = self.command_patterns.get(cmd_name, [])
        if patterns:
            # 返回第一个模式作为示例
            return patterns[0]
        return cmd_name
    
    def find_similar_commands(self, text, threshold=0.3):
        """
        公开接口: 查找与文本相似的命令
        
        参数:
            text (str): 命令文本
            threshold (float): 相似度阈值
            
        返回:
            list: 相似命令列表
        """
        return self._find_similar_commands(text, threshold)
    
    def get_all_commands(self):
        """
        获取所有可用命令及其模式
        
        返回:
            dict: 命令及其模式的字典
        """
        result = {}
        for cmd_name, cmd in self.commands.items():
            patterns = self.command_patterns.get(cmd_name, [])
            result[cmd_name] = {
                'name': cmd.name if hasattr(cmd, 'name') else cmd_name,
                'patterns': [p if isinstance(p, str) else p.pattern for p in patterns],
                'help': cmd.get_help() if hasattr(cmd, 'get_help') else f"命令: {cmd_name}"
            }
        return result 