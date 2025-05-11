import os
import pytest
from datetime import datetime
from src.publishers.media_publisher import XhsPublisher
from playwright.sync_api import sync_playwright, TimeoutError
import time

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