"""
交互式语音命令系统示例

此示例演示如何使用语音命令系统进行交互式命令执行。
用户可以通过语音输入命令，系统会识别并执行相应的操作。
"""

import os
import sys
import logging
import time

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

def main():
    """主函数"""
    print("="*50)
    print("     交互式语音命令系统")
    print("="*50)
    print("\n按 Ctrl+C 退出\n")
    
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
        while True:
            try:
                # 每次执行一条命令
                print("\n等待语音命令...")
                executor.execute_once()
                
                # 等待用户确认继续
                input("\n按回车继续...")
                
            except Exception as e:
                logger.error(f"执行命令时出错: {str(e)}", exc_info=True)
                print(f"出错: {str(e)}")
                print("请重试...")
                time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n程序已退出")
    finally:
        # 确保停止监听
        executor.stop_listening()

if __name__ == "__main__":
    main() 