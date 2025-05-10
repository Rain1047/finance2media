import unittest
from xhs import XhsClient
import os
from dotenv import load_dotenv

class TestXhsCrawler(unittest.TestCase):
    def setUp(self):
        """测试开始前的设置"""
        load_dotenv()
        # 从环境变量获取登录信息
        self.cookie = os.getenv('XHS_COOKIE')
        self.client = XhsClient(cookie=self.cookie)
        
    def test_get_note_info(self):
        """测试获取笔记信息"""
        # 测试笔记ID
        note_id = "65f1c4c1000000001e03c4c4"  # 这是一个示例ID，需要替换为实际的笔记ID
        try:
            note_info = self.client.get_note_info(note_id)
            self.assertIsNotNone(note_info)
            print(f"笔记标题: {note_info.get('title', '')}")
            print(f"笔记内容: {note_info.get('desc', '')}")
        except Exception as e:
            self.fail(f"获取笔记信息失败: {str(e)}")
            
    def test_search_notes(self):
        """测试搜索笔记"""
        keyword = "Python"
        try:
            search_results = self.client.search_notes(keyword)
            self.assertIsNotNone(search_results)
            print(f"搜索到 {len(search_results)} 条笔记")
            for note in search_results[:3]:  # 只打印前3条结果
                print(f"标题: {note.get('title', '')}")
                print(f"描述: {note.get('desc', '')}")
                print("---")
        except Exception as e:
            self.fail(f"搜索笔记失败: {str(e)}")
            
    def test_get_user_notes(self):
        """测试获取用户笔记"""
        user_id = "5ff577b9000000000100c5c5"  # 这是一个示例ID，需要替换为实际的用户ID
        try:
            user_notes = self.client.get_user_notes(user_id)
            self.assertIsNotNone(user_notes)
            print(f"获取到用户 {user_id} 的 {len(user_notes)} 条笔记")
        except Exception as e:
            self.fail(f"获取用户笔记失败: {str(e)}")

if __name__ == '__main__':
    unittest.main() 