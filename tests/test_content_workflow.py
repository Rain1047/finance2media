import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflows.content_creation_workflow import ContentCreationWorkflow

def test_content_creation():
    # 初始化工作流
    workflow = ContentCreationWorkflow()
    
    # 测试创建文本内容
    text_content = workflow.create_text_content(
        template_name="xiaohongshu_post",
        parameters={
            "title": "测试标题",
            "content": "这是一篇测试内容",
            "tags": ["测试", "小红书"],
            "images": ["image1.jpg", "image2.jpg"]
        },
        metadata={
            "author": "测试用户",
            "category": "测试分类"
        }
    )
    
    print("生成的文本内容：")
    print(text_content)
    
    # 测试创建图片内容
    image_content = workflow.create_image_content(
        template_name="xiaohongshu_post",
        parameters={
            "title": "图片测试",
            "content": "这是一篇图片测试内容",
            "tags": ["图片", "测试"],
            "images": ["test_image.jpg"]
        },
        metadata={
            "author": "测试用户",
            "category": "图片测试"
        }
    )
    
    print("\n生成的图片内容：")
    print(image_content)

if __name__ == "__main__":
    test_content_creation() 