# Finance2Media

本项目用于采集、缓存和展示经济数据，支持从FRED获取数据并使用SQLite数据库进行缓存。

## 环境配置

1. 克隆仓库：
   ```bash
   git clone https://github.com/yourusername/finance2media.git
   cd finance2media
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 配置环境变量：
   在项目根目录创建 `.env` 文件，并添加以下内容：
   ```
   FRED_API_KEY=your_fred_api_key
   OPENAI_API_KEY=your_openai_api_key
   ```

## 数据采集与缓存

项目使用 `FedDataCollector` 类从FRED获取经济数据，并通过 `Database` 类将数据缓存到SQLite数据库中。主要功能包括：

- 获取单个系列数据：`get_series_data(series_id, start_date, end_date, use_cache=True)`
- 获取多个系列数据：`get_multiple_series(series_ids=None)`
- 获取最新数据摘要：`get_latest_data_summary()`

## 测试

运行测试：
```bash
python -m unittest tests/test_fed_collector.py -v
```

## 项目结构

- `src/collectors/fed_collector.py`: FRED数据采集器
- `src/models/database.py`: 数据库缓存模型
- `src/config.py`: 项目配置
- `tests/test_fed_collector.py`: 测试用例

## 注意事项

- 数据库文件（`*.db`）已添加到 `.gitignore`，不会被git跟踪。
- 确保在运行前配置好环境变量。
