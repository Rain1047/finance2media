from crewai import Task, Crew, Process
from agents.content_agent import get_content_agent
from agents.resource_agent import get_resource_agent
from agents.publishing_agent import get_publishing_agent
from agents.monitoring_agent import get_monitoring_agent


def build_content_crew_workflow(topic: str = "经济数据分析"):
    """
    构建内容生产与发布的多Agent协作工作流
    """
    content_agent = get_content_agent()
    resource_agent = get_resource_agent()
    publishing_agent = get_publishing_agent()
    monitoring_agent = get_monitoring_agent()

    tasks = [
        Task(
            description=f"围绕主题'{topic}'进行内容结构规划和初稿创作，输出多模态内容包（文本、图片、视频脚本等）",
            expected_output="内容包（文本、图片、视频脚本等）",
            agent=content_agent
        ),
        Task(
            description="收集并处理内容所需的各类资源，优化为可用素材",
            expected_output="优化后的资源文件集",
            agent=resource_agent
        ),
        Task(
            description="将内容包发布到小红书平台，并调度定时发布",
            expected_output="发布成功确认和链接",
            agent=publishing_agent
        ),
        Task(
            description="监控内容表现，收集互动数据和用户反馈，生成表现报告和优化建议",
            expected_output="表现报告和优化建议",
            agent=monitoring_agent
        )
    ]

    crew = Crew(
        agents=[content_agent, resource_agent, publishing_agent, monitoring_agent],
        tasks=tasks,
        process=Process.sequential,  # 可选并行 Process.parallel
        verbose=2
    )
    return crew
