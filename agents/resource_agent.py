from crewai import Agent
from tools.scraper_tools import ScraperGeneratorTool
from tools.media_tools import MediaProcessorTool
from tools.resource_tools import ResourceClassifierTool
from langchain_openai import ChatOpenAI

def get_resource_agent():
    """
    创建资源处理Agent实例
    """
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    return Agent(
        name="ResourceManager",
        role="资源管理者",
        goal="收集、处理和优化内容所需的各类资源",
        backstory="我专注于发现和优化各类数字资源，是内容创作的供应商",
        tools=[
            ScraperGeneratorTool(),
            MediaProcessorTool(),
            ResourceClassifierTool(),
        ],
        llm=llm,
        verbose=True,
        allow_delegation=True,
    )
