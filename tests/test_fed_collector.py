import unittest
import pandas as pd
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path
import sqlite3

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.collectors.fed_collector import FedDataCollector
from src.config import FRED_SERIES
from src.models.database import Database

class TestFedDataCollector(unittest.TestCase):
    def setUp(self):
        """测试开始前的设置"""
        # 使用测试数据库
        self.test_db_path = os.path.join(project_root, 'data', 'test_fred_data.db')
        self.db = Database(self.test_db_path)
        self.collector = FedDataCollector(db=self.db)
        self.test_series_id = 'GDP'  # 使用 GDP 作为测试数据
        
    def tearDown(self):
        """测试结束后的清理"""
        # 删除测试数据库
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        
    def test_initialization(self):
        """测试采集器初始化"""
        self.assertIsNotNone(self.collector)
        self.assertIsNotNone(self.collector.fred)
        self.assertIsNotNone(self.collector.db)
        
    def test_get_single_series(self):
        """测试单个系列数据获取"""
        # 获取过去一年的数据
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        df = self.collector.get_series_data(
            self.test_series_id,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )
        
        # 验证返回的数据
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.index.name, 'date')
        self.assertIn('value', df.columns)
        
        # 验证数据是否已保存到数据库
        db_data = self.db.get_series_data(self.test_series_id)
        self.assertFalse(db_data.empty)
        pd.testing.assert_frame_equal(df, db_data)
        
    def test_cache_mechanism(self):
        """测试缓存机制"""
        # 第一次获取数据（会写入数据库）
        df1 = self.collector.get_series_data(self.test_series_id, use_cache=True)
        
        # 验证数据已保存到数据库
        db_data = self.db.get_series_data(self.test_series_id)
        self.assertFalse(db_data.empty)
        
        # 第二次获取数据（应该从数据库读取）
        df2 = self.collector.get_series_data(self.test_series_id, use_cache=True)
        
        # 验证两次获取的数据相同
        pd.testing.assert_frame_equal(df1, df2)
        
    def test_multiple_series(self):
        """测试多个系列数据获取"""
        series_ids = list(FRED_SERIES.values())[:2]  # 测试前两个系列
        results = self.collector.get_multiple_series(series_ids=series_ids)
        
        # 验证返回结果
        self.assertIsInstance(results, dict)
        self.assertEqual(len(results), len(series_ids))
        for series_id in series_ids:
            self.assertIn(series_id, results)
            self.assertIsInstance(results[series_id], pd.DataFrame)
            
            # 验证数据是否已保存到数据库
            db_data = self.db.get_series_data(series_id)
            self.assertFalse(db_data.empty)
            
    def test_latest_data_summary(self):
        """测试最新数据摘要"""
        # 采集所有系列的多天数据，确保摘要有内容
        end_date = datetime.now()
        start_date = end_date - timedelta(days=10)
        for series_id in FRED_SERIES.values():
            self.collector.get_series_data(series_id, start_date=start_date.strftime('%Y-%m-%d'), end_date=end_date.strftime('%Y-%m-%d'))
        
        summary = self.collector.get_latest_data_summary()
        
        # 验证摘要数据
        self.assertIsInstance(summary, pd.DataFrame)
        self.assertTrue(len(summary) > 0)
        
        # 验证必要的列
        required_columns = ['series_id', 'title', 'latest_date', 'latest_value', 'change', 'pct_change']
        for col in required_columns:
            self.assertIn(col, summary.columns)
            
    def test_metadata_storage(self):
        """测试元数据存储"""
        # 获取数据（这会同时保存元数据）
        self.collector.get_series_data(self.test_series_id)
        
        # 验证元数据是否已保存
        metadata = self.db.get_series_metadata(self.test_series_id)
        self.assertIsNotNone(metadata)
        self.assertIn('title', metadata)
        self.assertIn('units', metadata)
        self.assertIn('frequency', metadata)

def main():
    unittest.main()

if __name__ == '__main__':
    main()
