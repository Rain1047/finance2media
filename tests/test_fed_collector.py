import unittest
import pandas as pd
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.collectors.fed_collector import FedDataCollector
from src.config import CACHE_DIR, FRED_SERIES

class TestFedDataCollector(unittest.TestCase):
    def setUp(self):
        """测试开始前的设置"""
        # 确保缓存目录存在
        os.makedirs(CACHE_DIR, exist_ok=True)
        
        self.collector = FedDataCollector()
        self.test_series_id = 'GDP'  # 使用 GDP 作为测试数据
        
    def test_initialization(self):
        """测试采集器初始化"""
        self.assertIsNotNone(self.collector)
        self.assertIsNotNone(self.collector.fred)
        
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
        
    def test_cache_mechanism(self):
        """测试缓存机制"""
        # 第一次获取数据（会写入缓存）
        df1 = self.collector.get_series_data(self.test_series_id, use_cache=True)
        
        # 验证缓存文件存在
        cache_files = list(Path(CACHE_DIR).glob(f"{self.test_series_id}_*.csv"))
        self.assertTrue(len(cache_files) > 0)
        
        # 第二次获取数据（应该从缓存读取）
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
            
    def test_latest_data_summary(self):
        """测试最新数据摘要"""
        summary = self.collector.get_latest_data_summary()
        
        # 验证摘要数据
        self.assertIsInstance(summary, pd.DataFrame)
        self.assertTrue(len(summary) > 0)
        
        # 验证必要的列
        required_columns = ['latest_date', 'latest_value', 'change', 'pct_change']
        for col in required_columns:
            self.assertIn(col, summary.columns)

def main():
    unittest.main()

if __name__ == '__main__':
    main()
