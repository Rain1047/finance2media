from crewai import Agent
from tools.publish_tools import XhsPublisherTool, WeiboPublisherTool, TiktokPublisherTool, PublishSchedulerTool
from langchain_openai import ChatOpenAI

def get_publishing_agent():
    """
    创建内容发布Agent实例
    """
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    return Agent(
        name="Publisher",
        role="内容发布者",
        goal="将内容有效地发布到各平台，确保最大曝光和影响力",
        backstory="我精通各大内容平台的发布机制，擅长优化发布策略以获得最佳效果",
        tools=[
            XhsPublisherTool(),
            WeiboPublisherTool(),
            TiktokPublisherTool(),
            PublishSchedulerTool(),
        ],
        llm=llm,
        verbose=True,
        allow_delegation=True,
    )
