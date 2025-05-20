import os
import pytest
from datetime import datetime
from src.publishers.media_publisher import XhsPublisher
from playwright.sync_api import sync_playwright, TimeoutError
import time
from crewai import Agent, Task, Crew, Process
from tools.file_tools import FileTool
from tools.web_tools import WebScraperTool, ScriptGeneratorTool
from tools.content_tools import ContentPlannerTool
from tools.scraper_tools import ScraperGeneratorTool
from tools.media_tools import MediaProcessorTool
from tools.resource_tools import ResourceClassifierTool
from tools.publish_tools import XhsPublisherTool, WeiboPublisherTool, TiktokPublisherTool, PublishSchedulerTool
from tools.monitor_tools import DataCollectorTool, InteractionAnalyzerTool, FeedbackCollectorTool, PerformanceReportTool
from langchain.tools import Tool

def beauty_print(data):
    import json
    print(json.dumps(data, ensure_ascii=False, indent=2))

@pytest.fixture
def xhs_publisher():
    cookie = "a1=191829f884a96q7kipie52sdoln1o9pfui8ifl9bx30000415580; webId=c946b16471dcbca3bd0703e9f13a4397; web_session=04006979dbb94aa5de378333b9354bbcf2bb38"
    return XhsPublisher(cookie=cookie)

def test_get_upload_image_ids(xhs_publisher: XhsPublisher):
    """测试获取图片上传ID"""
    count = 5
    ids = xhs_publisher.get_upload_image_ids(count)
    beauty_print(ids)
    assert len(ids[0]["fileIds"]) == count

def test_upload_image(xhs_publisher: XhsPublisher):
    """测试上传图片"""
    ids = xhs_publisher.get_upload_image_ids(1)
    file_info = ids[0]
    file_id = file_info["fileIds"][0]
    file_token = file_info["token"]
    file_path = "data/images/test_image.jpg"  # 请确保此文件存在
    
    # 如果文件不存在，创建一个测试文件
    if not os.path.exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(b"test image content")
    
    res = xhs_publisher.upload_image(file_id, file_token, file_path)
    assert res.status_code == 200
    print(res.headers.get("X-Ros-Preview-Url"))

def test_get_suggest_topic(xhs_publisher: XhsPublisher):
    """测试获取话题建议"""
    topic_keyword = "Python"
    topics = xhs_publisher.get_suggest_topic(topic_keyword)
    beauty_print(topics)
    assert len(topics) > 0
    assert topic_keyword.upper() in topics[0]["name"].upper()

def test_get_suggest_ats(xhs_publisher: XhsPublisher):
    """测试获取@用户建议"""
    ats_keyword = "星空的花"
    ats = xhs_publisher.get_suggest_ats(ats_keyword)
    beauty_print(ats)
    assert len(ats) > 0
    assert ats_keyword.upper() in ats[0]["user_base_dto"]["user_nickname"].upper()

def test_create_simple_note(xhs_publisher: XhsPublisher):
    """测试发布简单笔记"""
    title = "经济数据周报"
    desc = """本周经济数据概览：
    1. GDP增长情况
    2. 失业率变化
    3. 通货膨胀指标
    4. 利率走势"""

    # 图片路径，请确保这些图片存在
    image_paths = [
        "data/images/gdp_trend.png",
        "data/images/unemployment.png",
        "data/images/inflation.png",
        "data/images/interest_rates.png"
    ]

    # 设置发布时间为当前时间
    post_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    note = xhs_publisher.create_image_note(
        title=title,
        desc=desc,
        image_paths=image_paths,
        is_private=False,
        post_time=post_time
    )
    assert note["success"]

def test_create_note_with_topics(xhs_publisher: XhsPublisher):
    """测试发布带话题的笔记"""
    title = "经济数据分析报告"
    desc = """#经济分析 #数据分析 #宏观经济
    
    本周经济数据分析：
    1. 经济增长指标
    2. 就业市场状况
    3. 通货膨胀趋势
    4. 货币政策走向"""

    # 获取话题建议
    topics = xhs_publisher.get_suggest_topic("经济分析")
    if not topics:
        pytest.skip("No topics found")

    # 选择前两个话题
    selected_topics = topics[:2]

    image_paths = [
        "data/images/economic_indicators.png",
        "data/images/market_trends.png"
    ]

    post_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    note = xhs_publisher.create_image_note(
        title=title,
        desc=desc,
        image_paths=image_paths,
        topics=selected_topics,
        is_private=False,
        post_time=post_time
    )
    assert note["success"]

def test_create_note_with_ats(xhs_publisher: XhsPublisher):
    """测试发布带@的笔记"""
    title = "经济数据分享"
    desc = """@数据分析师 请帮忙分析一下这组数据：
    1. 季度GDP增长率
    2. 月度失业率
    3. 年度通胀率"""

    # 获取@建议
    ats = xhs_publisher.get_suggest_ats("数据分析师")
    if not ats:
        pytest.skip("No users found to @")

    # 选择第一个用户
    selected_ats = [ats[0]]

    image_paths = [
        "data/images/quarterly_gdp.png",
        "data/images/monthly_unemployment.png"
    ]

    post_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    note = xhs_publisher.create_image_note(
        title=title,
        desc=desc,
        image_paths=image_paths,
        ats=selected_ats,
        is_private=False,
        post_time=post_time
    )
    assert note["success"]

def test_create_video_note(xhs_publisher: XhsPublisher):
    """测试发布视频笔记"""
    # 确保视频文件小于5MB
    video_path = "data/videos/small_demo_video.mp4"  # 使用较小的视频文件
    
    # 如果文件不存在，创建一个测试文件
    if not os.path.exists(video_path):
        os.makedirs(os.path.dirname(video_path), exist_ok=True)
        with open(video_path, "wb") as f:
            f.write(b"test video content")
    
    note = xhs_publisher.create_video_note(
        title="经济数据视频分析",
        video_path=video_path,
        desc="经济数据分析视频",
        is_private=True
    )
    assert note["success"]

def test_create_video_note_with_cover(xhs_publisher: XhsPublisher):
    """测试发布带封面的视频笔记"""
    video_path = "data/videos/small_demo_video.mp4"  # 使用较小的视频文件
    cover_path = "data/images/video_cover.jpg"
    
    # 如果文件不存在，创建测试文件
    if not os.path.exists(video_path):
        os.makedirs(os.path.dirname(video_path), exist_ok=True)
        with open(video_path, "wb") as f:
            f.write(b"test video content")
    
    if not os.path.exists(cover_path):
        os.makedirs(os.path.dirname(cover_path), exist_ok=True)
        with open(cover_path, "wb") as f:
            f.write(b"test cover content")
    
    note = xhs_publisher.create_video_note(
        title="经济数据视频分析",
        video_path=video_path,
        desc="经济数据分析视频",
        cover_path=cover_path,
        is_private=True
    )
    assert note["success"]

def publish_xhs_image_note(cookie_str, title, desc, image_paths):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        
        # 解析 cookie 字符串并设置多个 cookie
        cookies = []
        for cookie in cookie_str.split(';'):
            if '=' in cookie:
                name, value = cookie.strip().split('=', 1)
                cookies.append({
                    "name": name,
                    "value": value,
                    "domain": ".xiaohongshu.com",
                    "path": "/"
                })
        
        context.add_cookies(cookies)
        
        page = context.new_page()

        try:
            # 1. 直接打开创作中心
            print("正在打开创作中心...")
            page.goto("https://creator.xiaohongshu.com/publish", wait_until="networkidle")
            time.sleep(5)

            # 2. 上传图片
            print("开始上传图片...")
            for img in image_paths:
                print(f"正在上传图片: {img}")
                try:
                    page.set_input_files('input[type="file"]', img)
                    time.sleep(3)
                except Exception as e:
                    print(f"上传图片 {img} 失败: {str(e)}")
                    raise

            # 3. 填写标题和内容
            print("正在填写标题和内容...")
            try:
                page.fill('textarea[placeholder="请输入标题"]', title)
                page.fill('div[contenteditable="true"]', desc)
                time.sleep(2)
            except Exception as e:
                print(f"填写标题和内容失败: {str(e)}")
                raise

            # 4. 点击发布
            print("正在点击发布按钮...")
            try:
                publish_button = page.wait_for_selector('button:has-text("发布")', timeout=10000)
                if publish_button:
                    publish_button.click()
                    print("已点击发布按钮")
                else:
                    raise Exception("未找到发布按钮")
            except Exception as e:
                print(f"点击发布按钮失败: {str(e)}")
                raise
            
            print("等待发布完成...")
            time.sleep(10)

            print("图片笔记已发布！")

        except Exception as e:
            print(f"发生错误: {str(e)}")
            try:
                page.screenshot(path="error_screenshot.png")
                print("已保存错误截图到 error_screenshot.png")
            except Exception as screenshot_error:
                print(f"保存错误截图失败: {str(screenshot_error)}")
        
        finally:
            try:
                browser.close()
            except Exception as e:
                print(f"关闭浏览器时出错: {str(e)}")

# 用法示例
if __name__ == "__main__":
    cookie_str = "a1=191829f884a96q7kipie52sdoln1o9pfui8ifl9bx30000415580; webId=c946b16471dcbca3bd0703e9f13a4397; web_session=04006979dbb94aa5de378333b9354bbcf2bb38"
    publish_xhs_image_note(
        cookie_str=cookie_str,
        title="自动化测试标题",
        desc="自动化测试内容",
        image_paths=[
            "/Users/rain/CursorProject/finance2media/data/images/demo_image.jpg"
        ]
    )

if __name__ == '__main__':
    pytest.main(['-v', 'test_xhs_publisher.py'])

content_agent = Agent(
    name="ContentCreator",
    goal="创建高质量多模态内容，自动获取所需资源",
    backstory="我是一位多才多艺的内容创作者，擅长整合多种资源，创造引人入胜的内容",
    verbose=True,
    allow_delegation=True,
    tools=[
        FileTool(),  # 文件操作工具
        WebScraperTool(),  # 网页抓取
        ScriptGeneratorTool(),  # 脚本生成
        ContentPlannerTool(),  # 内容规划
    ]
)

resource_agent = Agent(
    name="ResourceManager",
    goal="收集、处理和优化内容所需的各类资源",
    backstory="我专注于发现和优化各类数字资源，是内容创作的供应商",
    verbose=True,
    allow_delegation=True,
    tools=[
        ScraperGeneratorTool(),  # 爬虫生成
        MediaProcessorTool(),  # 媒体处理
        ResourceClassifierTool()  # 资源分类
    ]
)

publishing_agent = Agent(
    name="Publisher",
    goal="将内容有效地发布到各平台，确保最大曝光和影响力",
    backstory="我精通各大内容平台的发布机制，擅长优化发布策略以获得最佳效果",
    verbose=True,
    tools=[
        XhsPublisherTool(),  # 小红书发布
        WeiboPublisherTool(),  # 微博发布(预留)
        TiktokPublisherTool(),  # 抖音发布(预留)
        PublishSchedulerTool()  # 发布调度
    ]
)

monitoring_agent = Agent(
    name="PerformanceMonitor",
    goal="监控内容表现，提供基于数据的优化建议",
    backstory="我擅长数据分析和洞察，能从用户反馈中发掘有价值的信息",
    verbose=True,
    tools=[
        DataCollectorTool(),  # 数据收集
        InteractionAnalyzerTool(),  # 互动分析
        FeedbackCollectorTool(),  # 反馈收集
        PerformanceReportTool()  # 表现报告
    ]
)

# 创建协作团队
content_crew = Crew(
    agents=[content_agent, resource_agent, publishing_agent, monitoring_agent],
    tasks=[
        Task(
            description="规划并创建一份关于[主题]的完整内容",
            expected_output="完整的内容包，包含文本、图片和视频素材",
            agent=content_agent
        ),
        Task(
            description="收集并处理所需的各类资源",
            expected_output="优化后的资源文件集",
            agent=resource_agent
        ),
        Task(
            description="将内容发布到小红书平台",
            expected_output="发布成功确认和链接",
            agent=publishing_agent
        ),
        Task(
            description="监控内容表现并提供优化建议",
            expected_output="表现报告和优化方案",
            agent=monitoring_agent
        )
    ],
    process=Process.sequential  # 可选择并行(parallel)或顺序(sequential)
)

# 启动团队工作
result = content_crew.kickoff()

def iterative_content_process(topic, iterations=3):
    for i in range(iterations):
        # 创建内容
        content_task = Task(
            description=f"创建第{i+1}版关于{topic}的内容",
            agent=content_agent
        )
        content_result = content_agent.execute_task(content_task)
        
        # 发布内容
        publish_task = Task(
            description=f"发布第{i+1}版内容到小红书",
            agent=publishing_agent,
            context={"content": content_result}
        )
        publish_result = publishing_agent.execute_task(publish_task)
        
        # 监控表现
        monitor_task = Task(
            description=f"监控第{i+1}版内容表现",
            agent=monitoring_agent,
            context={"publish_info": publish_result}
        )
        feedback = monitoring_agent.execute_task(monitor_task)
        
        # 基于反馈优化下一轮内容
        if i < iterations - 1:
            content_agent.update_context({"feedback": feedback})
    
    return "内容迭代完成"

def WebScraperTool():
    def scrape_website(url, data_type="text,images", depth=1):
        """
        从指定网站抓取资源
        params:
            url: 网站URL
            data_type: 要抓取的数据类型，如'text,images,videos'
            depth: 抓取深度
        """
        # 实现代码...
        return {"text": [...], "images": [...], "videos": [...]}
    
    return Tool(
        name="WebScraper",
        description="从网站抓取指定类型的资源",
        func=scrape_website
    )

def ScriptGeneratorTool():
    def generate_scraper_script(target_site, data_needs):
        """
        自动生成爬虫脚本
        params:
            target_site: 目标网站
            data_needs: 数据需求描述
        """
        # 实现代码...
        return "# 生成的Python爬虫脚本\nimport requests\n..."
    
    return Tool(
        name="ScriptGenerator",
        description="根据需求自动生成爬虫脚本",
        func=generate_scraper_script
    )

def XhsPublisherTool():
    def publish_to_xhs(content_package, schedule_time=None):
        """
        发布内容到小红书
        params:
            content_package: 内容包(文本、图片等)
            schedule_time: 计划发布时间
        """
        # 实现代码...
        from src.publishers.media_publisher import XhsPublisher
        
        xhs_publisher = XhsPublisher(cookie=get_cookie())
        result = xhs_publisher.create_image_note(
            title=content_package["title"],
            desc=content_package["text"],
            image_paths=content_package["images"],
            topics=content_package.get("topics", []),
            is_private=False
        )
        return result
    
    return Tool(
        name="XhsPublisher",
        description="发布内容到小红书平台",
        func=publish_to_xhs
    )

def WeiboPublisherTool():
    def publish_to_weibo(content_package, schedule_time=None):
        # 实现代码...
        return result
    
    return Tool(
        name="WeiboPublisher",
        description="发布内容到微博平台",
        func=publish_to_weibo
    )