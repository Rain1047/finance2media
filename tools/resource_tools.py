from langchain.tools import Tool

def ResourceClassifierTool():
    def classify_resource(file_path):
        # 示例：返回分类结果
        return f"{file_path} 被分类为: 示例类别"
    return Tool(
        name="ResourceClassifier",
        description="对资源文件进行自动分类",
        func=classify_resource
    ) 