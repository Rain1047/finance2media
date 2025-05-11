import sqlite3
from datetime import datetime
import pandas as pd
from pathlib import Path
import os

class Database:
    def __init__(self, db_path=None):
        if db_path is None:
            # 默认在data目录下创建数据库文件
            db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'fred_data.db')
        
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化数据库，创建必要的表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 创建经济数据表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS economic_data (
                    series_id TEXT,
                    date TEXT,
                    value REAL,
                    last_updated TEXT,
                    PRIMARY KEY (series_id, date)
                )
            ''')
            
            # 创建元数据表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS series_metadata (
                    series_id TEXT PRIMARY KEY,
                    title TEXT,
                    units TEXT,
                    frequency TEXT,
                    last_updated TEXT
                )
            ''')
            
            conn.commit()
    
    def save_series_data(self, series_id: str, df: pd.DataFrame, metadata: dict = None):
        """保存系列数据到数据库"""
        with sqlite3.connect(self.db_path) as conn:
            # 准备数据
            df = df.copy()
            df['series_id'] = series_id
            df['last_updated'] = datetime.now().isoformat()
            df = df.reset_index()  # 将日期索引转换为列
            df = df.rename(columns={'index': 'date'})
            
            # 保存数据
            df.to_sql('economic_data', conn, if_exists='append', index=False, 
                     method='multi', chunksize=1000)
            
            # 保存元数据
            if metadata:
                metadata['last_updated'] = datetime.now().isoformat()
                metadata_df = pd.DataFrame([metadata])
                metadata_df.to_sql('series_metadata', conn, if_exists='replace', 
                                 index=False)
    
    def get_series_data(self, series_id: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """从数据库获取系列数据"""
        with sqlite3.connect(self.db_path) as conn:
            query = f"""
                SELECT date, value 
                FROM economic_data 
                WHERE series_id = ?
            """
            params = [series_id]
            
            if start_date:
                query += " AND date >= ?"
                params.append(start_date)
            if end_date:
                query += " AND date <= ?"
                params.append(end_date)
            
            query += " ORDER BY date"
            
            df = pd.read_sql_query(query, conn, params=params)
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
                df.index.name = 'date'
            return df
    
    def get_series_metadata(self, series_id: str) -> dict:
        """获取系列元数据"""
        with sqlite3.connect(self.db_path) as conn:
            query = "SELECT * FROM series_metadata WHERE series_id = ?"
            df = pd.read_sql_query(query, conn, params=[series_id])
            return df.to_dict('records')[0] if not df.empty else None
    
    def get_latest_data(self, series_id: str) -> pd.DataFrame:
        """获取最新的数据点"""
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT date, value 
                FROM economic_data 
                WHERE series_id = ? 
                ORDER BY date DESC 
                LIMIT 1
            """
            df = pd.read_sql_query(query, conn, params=[series_id])
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
                df.index.name = 'date'
            return df 

    def _get_connection(self):
        return sqlite3.connect(self.db_path) 