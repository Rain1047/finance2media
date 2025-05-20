from langchain.tools import Tool

def MediaProcessorTool():
    def process_media(file_path, operation="compress"):
        # 示例：返回处理结果
        return f"已对{file_path}执行操作: {operation}"
    return Tool(
        name="MediaProcessor",
        description="对图片、视频等媒体文件进行处理（如压缩、裁剪等）",
        func=process_media
    ) 