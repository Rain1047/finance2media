import unittest
import pandas as pd
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.append(str(project_root))

from src.collectors.tv_collector import TvDataCollector
from src.tvDatafeed import Interval

class TestTvDataCollector(unittest.TestCase):
    def setUp(self):
        """测试开始前的设置"""
        self.collector = TvDataCollector()
        self.test_symbol = "AAPL"
        self.test_exchange = "NASDAQ"
        
    def test_get_symbol_data(self):
        """测试单个品种数据获取"""
        df = self.collector.get_symbol_data(
            symbol=self.test_symbol,
            exchange=self.test_exchange
        )
        
        self.assertIsInstance(df, pd.DataFrame)
        self.assertTrue(len(df) > 0)
        
        # 检查必要的列
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in required_columns:
            self.assertIn(col, df.columns)
            
    def test_multiple_symbols(self):
        """测试多个品种数据获取"""
        symbols = [
            {"symbol": "AAPL", "exchange": "NASDAQ"},
            {"symbol": "MSFT", "exchange": "NASDAQ"},
            {"symbol": "GOOGL", "exchange": "NASDAQ"}
        ]
        
        results = self.collector.get_multiple_symbols(symbols)
        
        self.assertIsInstance(results, dict)
        self.assertEqual(len(results), len(symbols))
        
    def test_technical_indicators(self):
        """测试技术指标计算"""
        df = self.collector.get_symbol_data(
            symbol=self.test_symbol,
            exchange=self.test_exchange
        )
        
        indicators = ['SMA20', 'SMA50', 'RSI']
        df_with_indicators = self.collector.get_technical_indicators(df, indicators)
        
        # 检查指标是否被添加
        for indicator in indicators:
            self.assertIn(indicator, df_with_indicators.columns)

def main():
    unittest.main()

if __name__ == '__main__':
    main() 