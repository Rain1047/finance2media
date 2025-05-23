"""
ASR 模块配置文件
"""

# 音频采集参数
AUDIO_CONFIG = {
    'sample_rate': 16000,        # 采样率
    'channels': 1,               # 通道数（单声道）
    'chunk_size': 1024,          # 缓冲区大小
    'format': 'int16',           # 采样格式
    'device_index': None,        # 音频设备索引（None 表示默认设备）
}

# FunASR 模型配置
FUNASR_CONFIG = {
    'model': 'paraformer',    # FunASR基础模型
    'model_dir': 'models/funasr',        # 模型保存目录
    'device': 'cpu',                     # 运行设备
    'batch_size': 1,                     # 批处理大小
    'hotword': None,                     # 热词列表
}

# VAD 配置
VAD_CONFIG = {
    'threshold': 0.5,            # VAD 阈值
    'min_speech_duration': 0.3,  # 最小语音片段长度（秒）
    'max_speech_duration': 30,   # 最大语音片段长度（秒）
    'min_silence_duration': 0.5, # 最小静音片段长度（秒）
}

# 流式识别配置
STREAMING_CONFIG = {
    'chunk_size': [0, 10, 5],    # 流式识别的块大小配置
    'encoder_chunk_look_back': 4, # 编码器回看块数
    'decoder_chunk_look_back': 1, # 解码器回看块数
    'mode': 'online',            # 使用在线模式
    'hotword_weight': 1.0,       # 热词权重
}

# 错误处理配置
ERROR_HANDLING = {
    'max_retries': 3,            # 最大重试次数
    'retry_delay': 1,            # 重试延迟（秒）
    'timeout': 30,               # 超时时间（秒）
} 