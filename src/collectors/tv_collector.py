from src.tvDatafeed import TvDatafeed, Interval # type: ignore
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import logging
from pathlib import Path
from .utils import cache_data, load_cached_data
from ..config import CACHE_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TvDataCollector:
    def __init__(self, username: str = None, password: str = None):
        """
        初始化 TradingView 数据采集器
        Args:
            username: TradingView 用户名
            password: TradingView 密码
        """
        self.tv = TvDatafeed(username=username, password=password)
        
    def get_symbol_data(self,
                       symbol: str,
                       exchange: str = "NASDAQ",
                       interval: Interval = Interval.in_daily,
                       n_bars: int = 1000,
                       use_cache: bool = True) -> Optional[pd.DataFrame]:
        """
        获取单个交易品种的数据
        Args:
            symbol: 交易品种代码
            exchange: 交易所
            interval: 时间间隔
            n_bars: 获取的K线数量
            use_cache: 是否使用缓存
        """
        cache_key = f"{exchange}_{symbol}_{interval.value}"
        
        # 检查缓存
        if use_cache:
            cached_data = load_cached_data(cache_key, CACHE_DIR)
            if cached_data is not None:
                logger.info(f"Using cached data for {cache_key}")
                return cached_data
                
        try:
            df = self.tv.get_hist(
                symbol=symbol,
                exchange=exchange,
                interval=interval,
                n_bars=n_bars
            )
            
            if df is not None and not df.empty:
                # 处理数据
                df = self._process_dataframe(df)
                
                # 缓存数据
                if use_cache:
                    cache_data(df, cache_key, CACHE_DIR)
                
                return df
                
        except Exception as e:
            logger.error(f"Error fetching data for {symbol} from {exchange}: {str(e)}")
            return None
            
    def get_multiple_symbols(self,
                           symbols: List[Dict[str, str]],
                           interval: Interval = Interval.in_daily,
                           n_bars: int = 1000) -> Dict[str, pd.DataFrame]:
        """
        获取多个交易品种的数据
        Args:
            symbols: 交易品种列表，格式为 [{"symbol": "AAPL", "exchange": "NASDAQ"}, ...]
            interval: 时间间隔
            n_bars: 获取的K线数量
        """
        results = {}
        for symbol_info in symbols:
            symbol = symbol_info["symbol"]
            exchange = symbol_info.get("exchange", "NASDAQ")
            
            df = self.get_symbol_data(
                symbol=symbol,
                exchange=exchange,
                interval=interval,
                n_bars=n_bars
            )
            
            if df is not None:
                results[f"{exchange}_{symbol}"] = df
                
        return results
        
    def _process_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        处理数据框架
        """
        # 确保索引是日期时间类型
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
            
        # 重命名列
        df = df.rename(columns={
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'volume': 'Volume'
        })
        
        return df
        
    def get_technical_indicators(self,
                               df: pd.DataFrame,
                               indicators: List[str] = None) -> pd.DataFrame:
        """
        计算技术指标
        Args:
            df: 价格数据
            indicators: 需要计算的指标列表
        """
        if indicators is None:
            indicators = ['SMA20', 'SMA50', 'RSI']
            
        result = df.copy()
        
        for indicator in indicators:
            if indicator.startswith('SMA'):
                period = int(indicator[3:])
                result[indicator] = result['Close'].rolling(window=period).mean()
            elif indicator == 'RSI':
                delta = result['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                result['RSI'] = 100 - (100 / (1 + rs))
                
        return result 