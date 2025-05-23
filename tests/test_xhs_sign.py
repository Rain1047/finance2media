import datetime
import json
from time import sleep
from playwright.sync_api import sync_playwright
from xhs import DataFetchError, XhsClient, help
import os
from dotenv import load_dotenv


def sign(uri, data=None, a1="191829f884a96q7kipie52sdoln1o9pfui8ifl9bx30000415580", web_session=""):
    for _ in range(10):
        try:
            with sync_playwright() as playwright:
                stealth_js_path = "/Users/rain/CursorProject/finance2media/tests/stealth.min.js"
                chromium = playwright.chromium
                browser = chromium.launch(headless=True)
                browser_context = browser.new_context()
                browser_context.add_init_script(path=stealth_js_path)
                context_page = browser_context.new_page()
                context_page.goto("https://www.xiaohongshu.com")
                browser_context.add_cookies([
                    {'name': 'a1', 'value': a1, 'domain': ".xiaohongshu.com", 'path': "/"}]
                )
                context_page.reload()
                sleep(1)
                encrypt_params = context_page.evaluate("([url, data]) => window._webmsxyw(url, data)", [uri, data])
                return {
                    "x-s": encrypt_params["X-s"],
                    "x-t": str(encrypt_params["X-t"])
                }
        except Exception:
            pass
    raise Exception("重试了这么多次还是无法签名成功，寄寄寄")

def __get_note_with_id(xhs_client: XhsClient, note_id: str, xsec: str):
    uri = '/api/sns/web/v1/feed'
    data = {"source_note_id":note_id,"image_formats":["jpg","webp","avif"],"extra":{"need_body_topic":"1"},"xsec_source":"pc_search","xsec_token": xsec}
    res = xhs_client.post(uri, data=data)
    return res["items"][0]["note_card"]

def beauty_print(data: dict):
    print(json.dumps(data, ensure_ascii=False, indent=2))


# 创建一个简单的笔记 success
def test_create_simple_note(xhs_client: XhsClient):
    title = "RedNote AutoPublish Test2"
    desc = "Test note for RedNote AutoPublish \n 1. Say Some Words \n 2. Thank You"
    images = [
        "/Users/rain/CursorProject/finance2media/data/images/demo_image.jpg",
    ]
    # get current time str
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    note = xhs_client.create_image_note(title, desc, images, is_private=False, post_time=current_time)
    beauty_print(note)

# 获取推荐话题 success
def test_get_suggest_topic(xhs_client: XhsClient):
    topic_keyword = "Python"
    topics = xhs_client.get_suggest_topic(topic_keyword)
    beauty_print(topics)
    assert topic_keyword.upper() in topics[0]["name"].upper()

def test_create_video_note_with_cover(xhs_client: XhsClient):
    note = xhs_client.create_video_note(title="Test Video Note", 
                                        video_path="/Users/rain/CursorProject/finance2media/data/videos/demo_video.mov", 
                                        desc="Auto Publish Video With CoverTest",
                                        cover_path="/Users/rain/CursorProject/finance2media/data/images/demo_image.jpg",
                                        is_private=False)
    beauty_print(note)


if __name__ == '__main__':
    # 从环境变量获取 cookie
    load_dotenv()
    cookie = os.getenv('XHS_COOKIE')
    
    # 确保 cookie 格式正确
    if cookie:
        cookie = f'a1="191829f884a96q7kipie52sdoln1o9pfui8ifl9bx30000415580"; webId="c946b16471dcbca3bd0703e9f13a4397"; web_session="04006979dbb94aa5de37914e173a4b58b8dde5"'
        
    else:
        raise ValueError("XHS_COOKIE not found in environment variables")

    
    print(datetime.datetime.now())

    for _ in range(5):
        try:
            xhs_client = XhsClient(cookie, sign=sign)
            # note = xhs_client.get_note_by_id(note_id="681deaed000000002200777e",xsec="AB7go17vApNBtz2hFPi6cTKF18YXX78nUFQ-UQa_FiSfE=")
            # note2 = __get_note_with_id(xhs_client,note_id="681deaed000000002200777e",xsec="AB7go17vApNBtz2hFPi6cTKF18YXX78nUFQ-UQa_FiSfE=")
            # print(json.dumps(note, indent=4))
            # print(help.get_imgs_url_from_note(note))
            # print(json.dumps(note2, indent=4))
            # test_create_simple_note(xhs_client)

            # 获取推荐话题
            test_create_video_note_with_cover(xhs_client)
            break
        except DataFetchError as e:
            print(e)
            print("失败重试一下下")