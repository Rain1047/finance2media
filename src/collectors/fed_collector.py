from fredapi import Fred
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import logging
from .utils import cache_data, load_cached_data
from ..config import FRED_API_KEY, FRED_SERIES, CACHE_DIR
from src.models.database import Database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FedDataCollector:
    def __init__(self, db: Database = None):
        """初始化FRED数据采集器"""
        self.fred = Fred(api_key=FRED_API_KEY)
        self.db = db if db is not None else Database()
        
    def get_series_data(self, series_id: str, start_date: str = None, end_date: str = None, use_cache: bool = True) -> pd.DataFrame:
        """获取单个系列的数据
        
        Args:
            series_id: FRED系列ID
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            use_cache: 是否使用缓存
            
        Returns:
            pd.DataFrame: 包含日期和值的数据框
        """
        if use_cache:
            # 尝试从数据库获取数据
            df = self.db.get_series_data(series_id, start_date, end_date)
            if not df.empty:
                df.index.name = 'date'
                logger.info(f"Using cached data for {series_id}")
                return df
        
        # 如果缓存中没有数据，从FRED获取
        try:
            df = self.fred.get_series(series_id, start_date, end_date)
            df = pd.DataFrame(df, columns=['value'])
            df.index.name = 'date'
            
            # 获取元数据
            metadata = self.fred.get_series_info(series_id)
            metadata_dict = {
                'series_id': series_id,
                'title': metadata.title,
                'units': metadata.units,
                'frequency': metadata.frequency
            }
            
            # 保存到数据库
            self.db.save_series_data(series_id, df, metadata_dict)
            logger.info(f"Fetched and cached new data for {series_id}")
            
            return df
        except Exception as e:
            logger.error(f"Error fetching data for {series_id}: {str(e)}")
            raise
    
    def get_multiple_series(self, series_ids: list = None) -> dict:
        """获取多个系列的数据
        
        Args:
            series_ids: FRED系列ID列表，如果为None则使用配置中的所有系列
            
        Returns:
            dict: 包含所有系列数据的字典
        """
        if series_ids is None:
            series_ids = list(FRED_SERIES.values())
            
        results = {}
        for series_id in series_ids:
            try:
                results[series_id] = self.get_series_data(series_id)
            except Exception as e:
                logger.error(f"Error fetching {series_id}: {str(e)}")
                continue
                
        return results
    
    def get_latest_data_summary(self) -> pd.DataFrame:
        """获取所有系列的最新数据摘要
        
        Returns:
            pd.DataFrame: 包含所有系列最新数据的摘要
        """
        summary_data = []
        
        for series_id in FRED_SERIES.values():
            try:
                # 获取最新数据
                latest_df = self.db.get_latest_data(series_id)
                if latest_df.empty:
                    continue
                latest_value = latest_df['value'].iloc[0]
                latest_date = latest_df.index[0]
                # 获取上一个数据点（比最新日期小的最大日期）
                with self.db._get_connection() as conn:
                    query = """
                        SELECT date, value FROM economic_data
                        WHERE series_id = ? AND date < ?
                        ORDER BY date DESC LIMIT 1
                    """
                    prev_df = pd.read_sql_query(query, conn, params=[series_id, latest_date.strftime('%Y-%m-%d')])
                if not prev_df.empty:
                    prev_value = prev_df['value'].iloc[0]
                    change = latest_value - prev_value
                    pct_change = (change / prev_value) * 100
                else:
                    change = None
                    pct_change = None
                # 获取元数据
                metadata = self.db.get_series_metadata(series_id)
                title = metadata['title'] if metadata else series_id
                summary_data.append({
                    'series_id': series_id,
                    'title': title,
                    'latest_date': latest_date,
                    'latest_value': latest_value,
                    'change': change,
                    'pct_change': pct_change
                })
            except Exception as e:
                logger.error(f"Error getting summary for {series_id}: {str(e)}")
                continue
        return pd.DataFrame(summary_data)
