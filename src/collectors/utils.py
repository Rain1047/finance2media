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
    cache_path = Path(cache_dir) / f"{cache_name}_{datetime.now().strftime('%Y%m%d')}.csv"
    data.to_csv(cache_path)

def load_cached_data(cache_name: str, 
                    cache_dir: str, 
                    max_age_days: int = 1) -> Optional[pd.DataFrame]:
    """
    从缓存加载数据
    """
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
        
    return pd.read_csv(latest_file, index_col='date', parse_dates=['date'])
