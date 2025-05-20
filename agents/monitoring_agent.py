from crewai import Agent
from tools.monitor_tools import DataCollectorTool, InteractionAnalyzerTool, FeedbackCollectorTool, PerformanceReportTool
from langchain_openai import ChatOpenAI

def get_monitoring_agent():
    """
    创建监控反馈Agent实例
    """
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    return Agent(
        name="PerformanceMonitor",
        role="内容监控者",
        goal="监控内容表现，提供基于数据的优化建议",
        backstory="我擅长数据分析和洞察，能从用户反馈中发掘有价值的信息",
        tools=[
            DataCollectorTool(),
            InteractionAnalyzerTool(),
            FeedbackCollectorTool(),
            PerformanceReportTool(),
        ],
        llm=llm,
        verbose=True,
        allow_delegation=True,
    )
