"""
后台语音命令系统示例

此示例演示如何使用语音命令系统进行持续的语音命令监听和执行。
系统会在后台持续监听用户的语音输入，自动识别并执行命令。
"""

import os
import sys
import logging
import time
import signal

# 将当前目录添加到路径中，以便导入模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.voice_command.command_executor import CommandExecutor

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

# 全局变量
executor = None
running = True

def signal_handler(sig, frame):
    """处理信号（如Ctrl+C）"""
    global running
    print("\n正在停止语音命令系统...")
    running = False
    if executor:
        executor.stop_listening()
    print("已停止")
    sys.exit(0)

def main():
    """主函数"""
    global executor
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    
    print("="*50)
    print("     后台语音命令系统")
    print("="*50)
    print("\n持续监听中... 按 Ctrl+C 退出\n")
    
    # 初始化命令执行器
    config_path = os.path.join('config', 'voice_command', 'commands.yaml')
    executor = CommandExecutor(config_path)
    
    # 显示可用命令
    print("可用命令示例:")
    print("- 系统信息")
    print("- 列出文件")
    print("- 创建文件 test.txt")
    print("- 删除文件 test.txt")
    print("- 当前目录")
    print("- 切换目录 ..")
    print("- 执行命令 ls -la")
    print("\n" + "="*50)
    
    try:
        # 开始持续监听
        executor.start_listening(continuous=True)
        
        # 保持程序运行，直到收到信号
        while running:
            time.sleep(0.5)  # 减少CPU使用率
            
    except Exception as e:
        logger.error(f"监听过程中出错: {str(e)}", exc_info=True)
        print(f"出错: {str(e)}")
    finally:
        # 确保停止监听
        if executor:
            executor.stop_listening()
        print("\n程序已退出")

if __name__ == "__main__":
    main() 