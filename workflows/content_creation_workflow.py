from typing import Dict, List, Optional
from datetime import datetime
import json
import os

class ContentCreationWorkflow:
    def __init__(self, config_path: str = "config/content_creation_config.json"):
        self.config = self._load_config(config_path)
        self.content_templates = self._load_templates()
        
    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        if not os.path.exists(config_path):
            return {
                "templates_dir": "templates/content",
                "output_dir": "output/content",
                "supported_formats": ["text", "image"],
                "max_retries": 3
            }
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_templates(self) -> Dict:
        """加载内容模板"""
        templates_dir = self.config.get("templates_dir", "templates/content")
        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir)
            return {}
        
        templates = {}
        for file in os.listdir(templates_dir):
            if file.endswith('.json'):
                with open(os.path.join(templates_dir, file), 'r', encoding='utf-8') as f:
                    templates[file.replace('.json', '')] = json.load(f)
        return templates
    
    def create_text_content(self, 
                          template_name: str,
                          parameters: Dict,
                          metadata: Optional[Dict] = None) -> Dict:
        """创建文本内容"""
        if template_name not in self.content_templates:
            raise ValueError(f"Template {template_name} not found")
            
        template = self.content_templates[template_name]
        content = self._apply_template(template, parameters)
        
        result = {
            "content": content,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "type": "text"
        }
        
        self._save_content(result)
        return result
    
    def create_image_content(self,
                           template_name: str,
                           parameters: Dict,
                           metadata: Optional[Dict] = None) -> Dict:
        """创建图片内容"""
        if template_name not in self.content_templates:
            raise ValueError(f"Template {template_name} not found")
            
        template = self.content_templates[template_name]
        content = self._apply_template(template, parameters)
        
        result = {
            "content": content,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "type": "image"
        }
        
        self._save_content(result)
        return result
    
    def _apply_template(self, template: Dict, parameters: Dict) -> str:
        """应用模板和参数生成内容"""
        # TODO: 实现模板应用逻辑
        return template.get("content", "")
    
    def _save_content(self, content: Dict) -> None:
        """保存生成的内容"""
        output_dir = self.config.get("output_dir", "output/content")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        filename = f"{content['type']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=2) 