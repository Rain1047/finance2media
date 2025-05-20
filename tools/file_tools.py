from langchain.tools import Tool
import os

# 文件读取工具
def FileReadTool():
    def read_file(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return Tool(
        name="FileRead",
        description="读取本地文件内容",
        func=read_file
    )

# 文件写入工具
def FileWriteTool():
    def write_file(path, content):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"写入成功: {path}"
    return Tool(
        name="FileWrite",
        description="写入内容到本地文件",
        func=write_file
    )

# 文件删除工具
def FileDeleteTool():
    def delete_file(path):
        os.remove(path)
        return f"删除成功: {path}"
    return Tool(
        name="FileDelete",
        description="删除本地文件",
        func=delete_file
    )

# 统一导出

def FileTool():
    """
    文件操作工具集合
    """
    return [FileReadTool(), FileWriteTool(), FileDeleteTool()]
