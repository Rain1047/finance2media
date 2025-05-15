import os
import math
from typing import Dict, Any
import requests
from xhs import XhsClient
from test_xhs_sign import sign

def chunk_upload_file(xhs_client: XhsClient, file_id: str, token: str, file_path: str, chunk_size: int = 4 * 1024 * 1024) -> Dict[str, Any]:
    """
    分片上传文件
    
    Args:
        xhs_client: 小红书客户端
        file_id: 文件ID
        token: 上传token
        file_path: 文件路径
        chunk_size: 分片大小，默认4MB
        
    Returns:
        上传结果
    """
    file_size = os.path.getsize(file_path)
    total_chunks = math.ceil(file_size / chunk_size)
    
    with open(file_path, 'rb') as f:
        for chunk_index in range(total_chunks):
            chunk = f.read(chunk_size)
            if not chunk:
                break
                
            # 构建分片上传请求
            uri = "/api/sns/web/v1/upload/chunk"
            data = {
                "fileId": file_id,
                "token": token,
                "chunkIndex": chunk_index,
                "totalChunks": total_chunks
            }
            files = {"chunk": chunk}
            
            # 发送分片上传请求
            response = requests.post(
                f"https://edith.xiaohongshu.com{uri}",
                files=files,
                data=data,
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                    "Cookie": xhs_client.cookie
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to upload chunk {chunk_index + 1}/{total_chunks}")
            
            print(f"Uploaded chunk {chunk_index + 1}/{total_chunks}")
    
    # 完成上传
    uri = "/api/sns/web/v1/upload/complete"
    data = {
        "fileId": file_id,
        "token": token,
        "totalChunks": total_chunks
    }
    response = requests.post(
        f"https://edith.xiaohongshu.com{uri}",
        json=data,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Cookie": xhs_client.cookie
        }
    )
    
    if response.status_code != 200:
        raise Exception("Failed to complete upload")
    
    return response.json()

def test_create_video_note_with_chunk_upload():
    # 从环境变量获取 cookie

    cookie = f'a1="191829f884a96q7kipie52sdoln1o9pfui8ifl9bx30000415580"; webId="c946b16471dcbca3bd0703e9f13a4397"; web_session="04006979dbb94aa5de37914e173a4b58b8dde5"'
    # 初始化客户端
    xhs_client = XhsClient(cookie=cookie, sign=sign)
    
    # 获取上传权限
    file_info = xhs_client.get_upload_files_permit("video")
    print("file_info:", file_info)
    file_id = file_info[0]
    token = file_info[1]
    
    # 上传视频文件
    video_path = "/Users/rain/CursorProject/finance2media/data/videos/demo_video.mov"
    try:
        upload_result = chunk_upload_file(xhs_client, file_id, token, video_path)
        print("Upload result:", upload_result)
        
        # 创建视频笔记
        note = xhs_client.create_video_note(
            title="Test Video Note",
            video_path=video_path,
            desc="Auto Publish Video With Chunk Upload Test",
            cover_path="/Users/rain/CursorProject/finance2media/data/images/demo_image.jpg",
            is_private=True
        )
        print("Note created:", note)
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_create_video_note_with_chunk_upload() 