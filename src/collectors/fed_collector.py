from fredapi import Fred
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import logging
from .utils import cache_data, load_cached_data
from ..config import FRED_API_KEY, FRED_SERIES, CACHE_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FedDataCollector:
    def __init__(self):
        if not FRED_API_KEY:
            raise ValueError("FRED API key not found in environment variables")
        self.fred = Fred(api_key=FRED_API_KEY)
        
    def get_series_data(self, 
                       series_id: str, 
                       start_date: Optional[str] = None,
                       end_date: Optional[str] = None,
                       use_cache: bool = True) -> Optional[pd.DataFrame]:
        """
        获取单个系列的数据
        """
        # 检查缓存
        if use_cache:
            cached_data = load_cached_data(series_id, CACHE_DIR)
            if cached_data is not None:
                logger.info(f"Using cached data for {series_id}")
                return cached_data
        
        try:
            data = self.fred.get_series(
                series_id,
                observation_start=start_date,
                observation_end=end_date
            )
            df = pd.DataFrame(data, columns=['value'])
            df.index.name = 'date'
            
            # 缓存数据
            if use_cache:
                cache_data(df, series_id, CACHE_DIR)
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data for {series_id}: {str(e)}")
            return None
            
    def get_multiple_series(self, 
                           series_ids: Optional[List[str]] = None,
                           start_date: Optional[str] = None,
                           end_date: Optional[str] = None) -> Dict[str, pd.DataFrame]:
        """
        获取多个系列的数据
        """
        if series_ids is None:
            series_ids = list(FRED_SERIES.values())
            
        results = {}
        for series_id in series_ids:
            df = self.get_series_data(series_id, start_date, end_date)
            if df is not None:
                results[series_id] = df
                
        return results
        
    def get_latest_data_summary(self) -> pd.DataFrame:
        """
        获取所有系列的最新数据摘要
        """
        data = self.get_multiple_series()
        summary = {}
        
        for series_id, df in data.items():
            if df is not None and not df.empty:
                latest_date = df.index.max()
                latest_value = df.loc[latest_date, 'value']
                
                # 计算变化
                if len(df) > 1:
                    prev_value = df.iloc[-2]['value']
                    change = latest_value - prev_value
                    pct_change = (change / prev_value) * 100
                else:
                    change = None
                    pct_change = None
                
                summary[series_id] = {
                    'latest_date': latest_date,
                    'latest_value': latest_value,
                    'change': change,
                    'pct_change': pct_change
                }
        
        return pd.DataFrame(summary).T
