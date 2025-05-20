# ASR 语音识别操作指南

## 1. 环境准备

### 1.1 安装依赖

确保已安装以下依赖：
- Python 3.8+
- numpy
- soundfile
- pyaudio
- funasr
- torchaudio
- librosa
- gradio (可选，用于 Gradio 演示)

可以通过以下命令安装依赖：
```bash
pip install -e .
```

### 1.2 安装 ffmpeg

ffmpeg 是音频处理的重要依赖，请确保已安装：
- macOS: `brew install ffmpeg`
- Linux: `sudo apt-get install ffmpeg`
- Windows: 下载 ffmpeg 并添加到环境变量

## 2. 命令行演示

### 2.1 启动命令行演示

运行以下命令启动命令行演示：
```bash
python examples/asr_demo.py
```

### 2.2 命令行演示操作流程

1. 启动后，程序会自动下载并加载 FunASR 模型。
2. 按回车键开始录音，再次按回车键停止录音。
3. 录音结束后，程序会自动进行语音识别并显示识别结果。

## 3. Gradio 演示

### 3.1 启动 Gradio 演示

运行以下命令启动 Gradio 演示：
```bash
python examples/asr_gradio_demo.py
```

### 3.2 Gradio 演示操作流程

1. 启动后，程序会自动下载并加载 FunASR 模型。
2. 在浏览器中打开显示的 URL（通常是 http://127.0.0.1:7860）。
3. 在 Gradio 界面中，点击"录音"按钮开始录音，再次点击停止录音。
4. 录音结束后，程序会自动进行语音识别并显示识别结果。

### 3.3 注意事项

- 确保麦克风已正确连接并启用。
- 录音时尽量保持环境安静，以提高识别准确率。
- 如果识别结果为空或不准确，请检查录音环境或 FunASR 模型配置。

## 4. 常见问题

### 4.1 未检测到音频

- 确保麦克风已正确连接并启用。
- 检查系统音频设置，确保麦克风权限已授予。

### 4.2 识别结果为空

- 确保录音时环境噪音较小。
- 检查 FunASR 模型是否正确加载。

### 4.3 依赖安装失败

- 确保 Python 环境正确配置。
- 尝试使用 `pip install -e .` 重新安装依赖。

## 5. 联系方式

如有问题，请联系项目维护者。 