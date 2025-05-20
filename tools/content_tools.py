from langchain.tools import Tool

# 内容结构规划工具
def ContentPlannerTool():
    def plan_content_structure(topic):
        # 示例：返回内容结构建议
        return {
            "title": f"{topic}的内容结构规划",
            "sections": ["引言", "主体", "结论"]
        }
    return Tool(
        name="ContentPlanner",
        description="为指定主题规划内容结构",
        func=plan_content_structure
    )

# 主题建议工具（可选）
def TopicSuggestTool():
    def suggest_topics(keyword):
        # 示例：返回相关主题
        return [f"{keyword}相关主题1", f"{keyword}相关主题2"]
    return Tool(
        name="TopicSuggest",
        description="根据关键词推荐相关主题",
        func=suggest_topics
    )
