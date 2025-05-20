from crewai import Agent
from tools.file_tools import FileReadTool, FileWriteTool, FileDeleteTool
from tools.web_tools import WebScraperTool, ScriptGeneratorTool
from tools.content_tools import ContentPlannerTool
from langchain_openai import ChatOpenAI


def get_content_agent():
    """
    创建内容创作Agent实例
    """
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    return Agent(
        name="ContentCreator",
        role="内容创作者",
        goal="创建高质量多模态内容，自动获取所需资源",
        backstory="我是一位多才多艺的内容创作者，擅长整合多种资源，创造引人入胜的内容",
        tools=[
            FileReadTool(),
            FileWriteTool(),
            FileDeleteTool(),
            WebScraperTool(),
            ScriptGeneratorTool(),
            ContentPlannerTool(),
        ],
        llm=llm,
        verbose=True,
        allow_delegation=True,
    )
