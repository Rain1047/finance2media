from workflows.content_workflow import build_content_crew_workflow
from dotenv import load_dotenv
load_dotenv()

if __name__ == "__main__":
    # 你可以自定义主题
    topic = "月度经济数据分析"
    crew = build_content_crew_workflow(topic)
    result = crew.kickoff()
    print("\n=== 工作流执行结果 ===")
    print(result)
