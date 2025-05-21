"""
命令基类

所有命令都应继承自此基类，并实现相应的方法。
"""

class BaseCommand:
    """所有命令的基类"""
    
    def __init__(self):
        """初始化命令"""
        self.name = self.__class__.__name__
        # 默认不需要确认
        self.require_confirmation = False
    
    def execute(self, command_text):
        """
        执行命令，需要子类实现
        
        参数:
            command_text (str): 命令文本
            
        返回:
            str: 执行结果
        """
        raise NotImplementedError("命令必须实现 execute 方法")
    
    def get_help(self):
        """
        获取命令帮助信息
        
        返回:
            str: 帮助信息
        """
        return f"命令 {self.name} 的帮助信息"
    
    def get_required_permission(self):
        """
        获取执行命令所需的权限
        
        返回:
            str: 权限名称，None表示不需要特殊权限
        """
        return None
    
    def get_confirmation_details(self, command_text):
        """
        获取命令确认详情，用于二次确认
        
        参数:
            command_text (str): 命令文本
            
        返回:
            str: 确认详情
        """
        return f"执行命令: {command_text}"
    
    def matches(self, text):
        """
        检查文本是否匹配此命令
        子类可以覆盖此方法以提供自定义匹配逻辑
        
        参数:
            text (str): 要检查的文本
            
        返回:
            bool: 是否匹配
        """
        return False 