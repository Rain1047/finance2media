# Finance2Media

本项目用于采集、缓存和展示经济数据，支持从FRED获取数据并使用SQLite数据库进行缓存。同时集成了语音命令系统，支持通过语音控制应用功能。

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

## 语音命令系统

项目集成了基于ASR的语音命令系统，支持通过语音控制应用程序。主要功能包括：

- 实时语音识别：基于FunASR的流式语音识别
- 命令分发与执行：支持文件操作、系统操作等多种命令
- 语音反馈：基于TTS的语音回复功能
- 图形用户界面：直观显示命令执行结果和实时识别状态

### 运行语音命令系统

以下是几种运行语音命令系统的方式：

1. 交互式命令模式：
   ```bash
   python examples/interactive_voice_command.py
   ```

2. 后台持续监听模式：
   ```bash
   python examples/background_voice_command.py
   ```

3. 图形界面模式（推荐）：
   ```bash
   python examples/gui_voice_command.py
   ```

4. 测试语音命令系统：
   ```bash
   python examples/test_voice_command.py
   ```

### 配置命令

语音命令系统的配置文件位于 `config/voice_command/commands.yaml`，可以根据需要添加、修改或禁用命令。

## 测试

运行测试：
```bash
python -m unittest tests/test_fed_collector.py -v
```

## 项目结构

- `src/collectors/fed_collector.py`: FRED数据采集器
- `src/models/database.py`: 数据库缓存模型
- `src/config.py`: 项目配置
- `src/voice_command/`: 语音命令系统模块
- `commands/`: 命令实现模块
- `examples/`: 使用示例
- `doc/`: 项目文档
- `tests/test_fed_collector.py`: 测试用例

## 文档

详细的语音命令系统文档请参阅 `doc/voice_command_system_summary.md`。

## 注意事项

- 数据库文件（`*.db`）已添加到 `.gitignore`，不会被git跟踪。
- 确保在运行前配置好环境变量。
- 语音命令系统需要麦克风输入设备。
