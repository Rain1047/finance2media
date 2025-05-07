import pandas as pd
import os
from datetime import datetime
import json
from typing import Optional, Union
from pathlib import Path

def cache_data(data: pd.DataFrame, 
               cache_name: str, 
               cache_dir: str) -> None:
    """
    缓存数据到本地
    """
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = Path(cache_dir) / f"{cache_name}_{datetime.now().strftime('%Y%m%d')}.csv"
    
    # 确保索引名称为 'date'
    data.index.name = 'date'
    data.to_csv(cache_path)

def load_cached_data(cache_name: str, 
                    cache_dir: str, 
                    max_age_days: int = 1) -> Optional[pd.DataFrame]:
    """
    从缓存加载数据
    """
    try:
        cache_path = Path(cache_dir)
        if not cache_path.exists():
            return None
            
        files = list(cache_path.glob(f"{cache_name}_*.csv"))
        if not files:
            return None
            
        latest_file = max(files, key=lambda x: x.stat().st_mtime)
        file_age = (datetime.now() - datetime.fromtimestamp(latest_file.stat().st_mtime)).days
        
        if file_age > max_age_days:
            return None
            
        # 先尝试读取文件头，检查列名
        df = pd.read_csv(latest_file)
        
        # 如果 'date' 不在列中，可能是索引
        if 'date' not in df.columns and df.index.name != 'date':
            # 重置索引，确保日期列存在
            df = df.reset_index()
            if 'index' in df.columns:
                df = df.rename(columns={'index': 'date'})
                
        # 设置日期索引
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
        
        return df
        
    except Exception as e:
        print(f"Error loading cached data: {e}")
        return None
