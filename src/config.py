import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# API Keys
FRED_API_KEY = os.getenv('FRED_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# 数据采集配置
FRED_SERIES = {
    'GDP': 'GDP',                    # 国内生产总值
    'UNRATE': 'UNRATE',             # 失业率
    'CPIAUCSL': 'CPIAUCSL',         # 消费者价格指数
    'FEDFUNDS': 'FEDFUNDS',         # 联邦基金利率
    'M2': 'M2',                     # M2货币供应量
}

# 数据存储配置
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
CACHE_DIR = os.path.join(DATA_DIR, 'cache')

# LLM 配置
LLM_MODEL = "gpt-3.5-turbo"
LLM_TEMPERATURE = 0.3

# 确保必要的目录存在
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)
