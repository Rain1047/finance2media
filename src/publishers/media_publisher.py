import os
from datetime import datetime
from typing import List, Optional, Dict, Any
import requests
from dotenv import load_dotenv

class XhsPublisher:
    """小红书发布器，专门用于发布笔记"""
    
    def __init__(self, cookie: str = None):
        """
        初始化发布器
        
        Args:
            cookie: 小红书cookie，如果为None则从环境变量获取
        """
        if cookie is None:
            load_dotenv()
            cookie = os.getenv('XHS_COOKIE')
            if not cookie:
                raise ValueError("XHS_COOKIE not found in environment variables")
        
        self.cookie = cookie
        self.base_url = "https://edith.xiaohongshu.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Cookie": cookie
        }
    
    def get_upload_image_ids(self, count: int) -> List[Dict[str, Any]]:
        """
        获取图片上传ID
        
        Args:
            count: 需要获取的图片数量
            
        Returns:
            包含fileIds和token的列表
        """
        uri = "/api/sns/web/v1/upload/image_ids"
        data = {"count": count}
        response = requests.post(f"{self.base_url}{uri}", json=data, headers=self.headers)
        return response.json()["data"]
    
    def upload_image(self, file_id: str, file_token: str, file_path: str) -> requests.Response:
        """
        上传图片
        
        Args:
            file_id: 图片ID
            file_token: 上传token
            file_path: 图片路径
            
        Returns:
            上传响应
        """
        uri = "/api/sns/web/v1/upload/image"
        with open(file_path, "rb") as f:
            files = {"file": f}
            data = {
                "fileId": file_id,
                "token": file_token
            }
            response = requests.post(f"{self.base_url}{uri}", files=files, data=data, headers=self.headers)
            return response
    
    def get_suggest_topic(self, keyword: str) -> List[Dict[str, Any]]:
        """
        获取话题建议
        
        Args:
            keyword: 话题关键词
            
        Returns:
            话题列表
        """
        uri = "/api/sns/web/v1/search/topic"
        params = {"keyword": keyword}
        response = requests.get(f"{self.base_url}{uri}", params=params, headers=self.headers)
        return response.json()["data"]["topics"]
    
    def get_suggest_ats(self, keyword: str) -> List[Dict[str, Any]]:
        """
        获取@用户建议
        
        Args:
            keyword: 用户名关键词
            
        Returns:
            用户列表
        """
        uri = "/api/sns/web/v1/search/user"
        params = {"keyword": keyword}
        response = requests.get(f"{self.base_url}{uri}", params=params, headers=self.headers)
        return response.json()["data"]["users"]
    
    def create_image_note(
        self,
        title: str,
        desc: str,
        image_paths: List[str],
        is_private: bool = False,
        post_time: Optional[str] = None,
        topics: Optional[List[Dict[str, Any]]] = None,
        ats: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        发布图片笔记
        
        Args:
            title: 笔记标题
            desc: 笔记描述
            image_paths: 图片路径列表
            is_private: 是否私密
            post_time: 发布时间，格式：YYYY-MM-DD HH:MM:SS
            topics: 话题列表
            ats: @用户列表
            
        Returns:
            发布结果
        """
        # 1. 获取图片上传ID
        file_infos = self.get_upload_image_ids(len(image_paths))
        
        # 2. 上传图片
        image_ids = []
        for file_info, image_path in zip(file_infos, image_paths):
            file_id = file_info["fileIds"][0]
            file_token = file_info["token"]
            response = self.upload_image(file_id, file_token, image_path)
            if response.status_code != 200:
                raise Exception(f"Failed to upload image: {image_path}")
            image_ids.append(file_id)
        
        # 3. 构建发布数据
        data = {
            "title": title,
            "desc": desc,
            "image_ids": image_ids,
            "is_private": is_private
        }
        
        if post_time:
            data["post_time"] = post_time
        if topics:
            data["topics"] = topics
        if ats:
            data["ats"] = ats
        
        # 4. 发布笔记
        uri = "/api/sns/web/v1/note/create"
        response = requests.post(f"{self.base_url}{uri}", json=data, headers=self.headers)
        return response.json()
    
    def create_video_note(
        self,
        title: str,
        video_path: str,
        desc: str,
        is_private: bool = False,
        cover_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        发布视频笔记
        
        Args:
            title: 笔记标题
            video_path: 视频路径
            desc: 笔记描述
            is_private: 是否私密
            cover_path: 封面图片路径
            
        Returns:
            发布结果
        """
        # 1. 获取视频上传ID
        file_info = self.get_upload_image_ids(1)[0]
        file_id = file_info["fileIds"][0]
        file_token = file_info["token"]
        
        # 2. 上传视频
        with open(video_path, "rb") as f:
            files = {"file": f}
            data = {
                "fileId": file_id,
                "token": file_token
            }
            uri = "/api/sns/web/v1/upload/video"
            response = requests.post(f"{self.base_url}{uri}", files=files, data=data, headers=self.headers)
            if response.status_code != 200:
                raise Exception(f"Failed to upload video: {video_path}")
        
        # 3. 如果有封面，上传封面
        cover_id = None
        if cover_path:
            cover_info = self.get_upload_image_ids(1)[0]
            cover_id = cover_info["fileIds"][0]
            cover_token = cover_info["token"]
            response = self.upload_image(cover_id, cover_token, cover_path)
            if response.status_code != 200:
                raise Exception(f"Failed to upload cover: {cover_path}")
        
        # 4. 构建发布数据
        data = {
            "title": title,
            "desc": desc,
            "video_id": file_id,
            "is_private": is_private
        }
        
        if cover_id:
            data["cover_id"] = cover_id
        
        # 5. 发布笔记
        uri = "/api/sns/web/v1/note/create"
        response = requests.post(f"{self.base_url}{uri}", json=data, headers=self.headers)
        return response.json()
