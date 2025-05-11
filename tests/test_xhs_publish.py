import time
from time import sleep
import os
from datetime import datetime
import pytest
import requests
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

from xhs import FeedType, IPBlockError, XhsClient
from xhs.exception import SignError, DataFetchError
from src.publishers.media_publisher import XhsPublisher

# 直接定义 beauty_print 函数，替换原有导入

def beauty_print(data):
    import json
    print(json.dumps(data, ensure_ascii=False, indent=2))

# 加载环境变量
load_dotenv()

def get_context_page(playwright):
    chromium = playwright.chromium
    browser = chromium.launch(headless=True)
    browser_context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    )
    browser_context.add_init_script(path="tests/stealth.min.js")
    context_page = browser_context.new_page()
    return browser_context, context_page

playwright = sync_playwright().start()
browser_context, context_page = get_context_page(playwright)

@pytest.fixture
def xhs_client():
    def sign(uri, data, a1="", web_session=""):
        context_page.goto("https://www.xiaohongshu.com")
        cookie_list = browser_context.cookies()
        web_session_cookie = list(filter(lambda cookie: cookie["name"] == "web_session", cookie_list))
        if not web_session_cookie:
            browser_context.add_cookies([
                {'name': 'web_session', 'value': web_session, 'domain': ".xiaohongshu.com", 'path': "/"},
                {'name': 'a1', 'value': a1, 'domain': ".xiaohongshu.com", 'path': "/"}]
            )
            sleep(1)
        encrypt_params = context_page.evaluate("([url, data]) => window._webmsxyw(url, data)", [uri, data])
        return {
            "x-s": encrypt_params["X-s"],
            "x-t": str(encrypt_params["X-t"])
        }

    # 设置测试用的cookie
    cookie = "a1=191829f884a96q7kipie52sdoln1o9pfui8ifl9bx30000415580; webId=c946b16471dcbca3bd0703e9f13a4397; web_session=04006979dbb94aa5de378333b9354bbcf2bb38"
    return XhsClient(cookie=cookie, sign=sign)

# def test_xhs_client_init():
#     xhs_client = XhsClient()
#     assert xhs_client


# def test_cookie_setter_getter():
#     xhs_client = XhsClient()
#     cd = xhs_client.cookie_dict
#     beauty_print(cd)
#     assert "web_session" in cd


def test_external_sign_func():
    def sign(url, data=None, a1=""):
        """signature url and data in here"""
        return {}

    with pytest.raises(SignError):
        xhs_client = XhsClient(sign=sign)
        xhs_client.get_qrcode()


def test_get_note_by_id(xhs_client: XhsClient):
    note_id = "6413cf6b00000000270115b5"
    data = xhs_client.get_note_by_id(note_id)
    beauty_print(data)
    assert data["note_id"] == note_id


def test_get_note_by_id_from_html(xhs_client: XhsClient):
    note_id = "6413cf6b00000000270115b5"
    data = xhs_client.get_note_by_id_from_html(note_id)
    beauty_print(data)
    assert data["note_id"] == note_id


def test_report_note_metrics(xhs_client: XhsClient):
    res = xhs_client.report_note_metrics(
        note_id="646837b9000000001300a4c3",
        note_type=1,
        note_user_id="6037a89b0000000001007e72",
        viewer_user_id="63273a77000000002303cc9b")
    beauty_print(res)
    assert res["success"]


def test_get_self_info(xhs_client: XhsClient):
    data = xhs_client.get_self_info()
    beauty_print(data)
    assert isinstance(data, dict)


def test_get_self_info2(xhs_client: XhsClient):
    data = xhs_client.get_self_info2()
    beauty_print(data)
    assert isinstance(data, dict)


def test_get_user_info(xhs_client: XhsClient):
    user_id = "5ff0e6410000000001008400"
    data = xhs_client.get_user_info(user_id)
    basic_info = data["basic_info"]
    beauty_print(data)
    assert (basic_info["red_id"] == "hh06ovo"
            or basic_info["nickname"] == "小王不爱睡")


def test_get_home_feed_category(xhs_client: XhsClient):
    data = xhs_client.get_home_feed_category()
    beauty_print(data)
    assert len(data)


def test_get_home_feed(xhs_client: XhsClient):
    recommend_type = FeedType.RECOMMEND
    data = xhs_client.get_home_feed(recommend_type)
    beauty_print(data)
    assert len(data["items"]) > 0


def test_get_search_suggestion(xhs_client: XhsClient):
    res = xhs_client.get_search_suggestion("jvm")
    beauty_print(res)
    assert len(res)


def test_get_note_by_keyword(xhs_client: XhsClient):
    keyword = "小红书"
    data = xhs_client.get_note_by_keyword(keyword)
    beauty_print(data)
    assert len(data["items"]) > 0


def test_get_user_notes(xhs_client: XhsClient):
    user_id = "63273a77000000002303cc9b"
    data = xhs_client.get_user_notes(user_id)
    beauty_print(data)
    assert len(data["notes"]) > 0


# @pytest.mark.skip(reason="it take much request and time")
def test_get_user_all_notes(xhs_client: XhsClient):
    user_id = "576e7b1d50c4b4045222de08"
    notes = xhs_client.get_user_all_notes(user_id, 0)
    beauty_print(notes)


def test_get_note_comments(xhs_client: XhsClient):
    note_id = "63db8819000000001a01ead1"
    comments = xhs_client.get_note_comments(note_id)
    beauty_print(comments)
    assert len(comments["comments"]) > 0


def test_get_note_sub_comments(xhs_client: XhsClient):
    note_id = "63db8819000000001a01ead1"
    root_comment_id = "63db8957000000001c03e5b5"
    comments = xhs_client.get_note_sub_comments(note_id, root_comment_id)
    beauty_print(comments)
    assert len(comments["comments"]) > 0


@pytest.mark.skip(reason="it take much request and time")
def test_get_note_all_comments(xhs_client: XhsClient):
    note_id = "63db8819000000001a01ead1"
    note = xhs_client.get_note_by_id(note_id)
    comments_count = int(note["interact_info"]["comment_count"])
    print(comments_count)
    comments = xhs_client.get_note_all_comments(note_id)
    beauty_print(comments)
    assert len(comments) == comments_count


def test_get_qrcode(xhs_client: XhsClient):
    data = xhs_client.get_qrcode()
    beauty_print(data)
    assert data["url"].startswith("xhsdiscover://")


def test_check_qrcode(xhs_client: XhsClient):
    qrcode = xhs_client.get_qrcode()
    data = xhs_client.check_qrcode(qr_id=qrcode["qr_id"], code=qrcode["code"])
    beauty_print(data)
    assert "code_status" in data


@pytest.mark.skip()
def test_comment_note(xhs_client: XhsClient):
    data = xhs_client.comment_note("642b96640000000014027cd2", "你最好说你在说你自己")
    beauty_print(data)
    assert data["comment"]["id"]


@pytest.mark.skip()
def test_comment_user(xhs_client: XhsClient):
    data = xhs_client.comment_user("642b96640000000014027cd2",
                                   "642f801000000000150037f8",
                                   "我评论你了")
    beauty_print(data)
    assert data["comment"]["id"]


@pytest.mark.skip()
def test_delete_comment(xhs_client: XhsClient):
    data = xhs_client.delete_note_comment("642b96640000000014027cd2",
                                          "642f801000000000150037f8")
    beauty_print(data)


@pytest.mark.parametrize("note_id", [
    "6413cf6b00000000270115b5",
    "641718a200000000130143f2"
])
@pytest.mark.skip()
def test_save_files_from_note_id(xhs_client: XhsClient, note_id: str):
    xhs_client.save_files_from_note_id(note_id, r"C:\Users\ReaJason\Desktop")


@pytest.mark.parametrize("note_id", [
    "639a7064000000001f0098a8",
    "635d06790000000015020497"
])
@pytest.mark.skip()
def test_save_files_from_note_id_invalid_title(xhs_client: XhsClient, note_id):
    xhs_client.save_files_from_note_id(note_id, r"C:\Users\ReaJason\Desktop")


@pytest.mark.skip()
def test_get_user_collect_notes(xhs_client: XhsClient):
    notes = xhs_client.get_user_collect_notes(
        user_id="63273a77000000002303cc9b")["notes"]
    beauty_print(notes)
    assert len(notes) == 1


@pytest.mark.skip()
def test_get_user_like_notes(xhs_client: XhsClient):
    notes = xhs_client.get_user_like_notes(
        user_id="63273a77000000002303cc9b")["notes"]
    beauty_print(notes)
    assert len(notes) == 2


@pytest.mark.skip(reason="i don't want to block by ip")
def test_ip_block_error(xhs_client: XhsClient):
    with pytest.raises(IPBlockError):
        note_id = "6413cf6b00000000270115b5"
        for _ in range(150):
            xhs_client.get_note_by_id(note_id)


def test_activate(xhs_client: XhsClient):
    info = xhs_client.activate()
    beauty_print(info)
    assert info["session"]


def test_get_emojis(xhs_client: XhsClient):
    emojis = xhs_client.get_emojis()
    beauty_print(emojis)
    assert len(emojis)


def test_get_upload_image_ids(xhs_client: XhsClient):
    count = 5
    ids = xhs_client.get_upload_image_ids(count)
    beauty_print(ids)
    assert len(ids[0]["fileIds"]) == count


def test_upload_image(xhs_client: XhsClient):
    ids = xhs_client.get_upload_image_ids(1)
    file_info = ids[0]
    file_id = file_info["fileIds"][0]
    file_token = file_info["token"]
    file_path = "/Users/reajason/Downloads/221686462282_.pic.jpg"
    res = xhs_client.upload_image(file_id, file_token, file_path)
    assert res.status_code == 200
    print(res.headers["X-Ros-Preview-Url"])

    with pytest.raises(DataFetchError, match="file already exists"):
        xhs_client.upload_image(file_id, file_token, file_path)


def test_get_suggest_topic(xhs_client: XhsClient):
    topic_keyword = "Python"
    topics = xhs_client.get_suggest_topic(topic_keyword)
    beauty_print(topics)
    assert topic_keyword.upper() in topics[0]["name"].upper()


def test_get_suggest_ats(xhs_client: XhsClient):
    ats_keyword = "星空的花"
    ats = xhs_client.get_suggest_ats(ats_keyword)
    beauty_print(ats)
    assert ats_keyword.upper() in ats[0]["user_base_dto"]["user_nickname"].upper()


def test_create_simple_note(xhs_client: XhsClient):
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

    note = xhs_client.create_image_note(
        title=title,
        desc=desc,
        image_paths=image_paths,  # 修改参数名
        is_private=False,  # 设置为公开
        post_time=post_time
    )
    assert note["success"]


def test_create_note_with_topics(xhs_client: XhsClient):
    """测试发布带话题的笔记"""
    title = "经济数据分析报告"
    desc = """#经济分析 #数据分析 #宏观经济
    
    本周经济数据分析：
    1. 经济增长指标
    2. 就业市场状况
    3. 通货膨胀趋势
    4. 货币政策走向"""

    # 获取话题建议
    topics = xhs_client.get_suggest_topic("经济分析")
    if not topics:
        pytest.skip("No topics found")

    # 选择前两个话题
    selected_topics = topics[:2]

    image_paths = [
        "data/images/economic_indicators.png",
        "data/images/market_trends.png"
    ]

    post_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    note = xhs_client.create_image_note(
        title=title,
        desc=desc,
        image_paths=image_paths,  # 修改参数名
        topics=selected_topics,
        is_private=False,
        post_time=post_time
    )
    assert note["success"]


def test_create_note_with_ats(xhs_client: XhsClient):
    """测试发布带@的笔记"""
    title = "经济数据分享"
    desc = """@数据分析师 请帮忙分析一下这组数据：
    1. 季度GDP增长率
    2. 月度失业率
    3. 年度通胀率"""

    # 获取@建议
    ats = xhs_client.get_suggest_ats("数据分析师")
    if not ats:
        pytest.skip("No users found to @")

    # 选择第一个用户
    selected_ats = [ats[0]]

    image_paths = [
        "data/images/quarterly_gdp.png",
        "data/images/monthly_unemployment.png"
    ]

    post_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    note = xhs_client.create_image_note(
        title=title,
        desc=desc,
        image_paths=image_paths,  # 修改参数名
        ats=selected_ats,
        is_private=False,
        post_time=post_time
    )
    assert note["success"]


def test_create_video_note(xhs_client: XhsClient):
    """测试发布视频笔记"""
    # 确保视频文件小于5MB
    video_path = "data/videos/small_demo_video.mp4"  # 使用较小的视频文件
    note = xhs_client.create_video_note(
        title="经济数据视频分析",
        video_path=video_path,
        desc="经济数据分析视频",
        is_private=True
    )
    assert note["success"]


def test_create_video_note_with_cover(xhs_client: XhsClient):
    """测试发布带封面的视频笔记"""
    video_path = "data/videos/small_demo_video.mp4"  # 使用较小的视频文件
    cover_path = "data/images/video_cover.jpg"
    note = xhs_client.create_video_note(
        title="经济数据视频分析",
        video_path=video_path,
        desc="经济数据分析视频",
        cover_path=cover_path,
        is_private=True
    )
    assert note["success"]


# 初始化发布器
publisher = XhsPublisher(cookie="your_cookie_here")

# 发布图片笔记
note = publisher.create_image_note(
    title="经济数据周报",
    desc="本周经济数据概览...",
    image_paths=["path/to/image1.jpg", "path/to/image2.jpg"],
    is_private=False
)

# 发布视频笔记
video_note = publisher.create_video_note(
    title="经济数据视频分析",
    video_path="path/to/video.mp4",
    desc="经济数据分析视频",
    is_private=True,
    cover_path="path/to/cover.jpg"  # 可选
)

if __name__ == '__main__':
    pytest.main(['-v', 'test_xhs_publish.py'])