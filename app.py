"""
实时语音识别应用
"""

import streamlit as st
import numpy as np
import queue
import time
from src.asr.audio_capture import AudioCapture
from src.asr.audio_processor import AudioProcessor
from src.asr.funasr_recognizer import FunASRRecognizer

# 页面配置
st.set_page_config(
    page_title="实时语音识别",
    page_icon="🎤",
    layout="wide"
)

# 自定义CSS
st.markdown("""
<style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        padding: 10px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .recording-status {
        text-align: center;
        font-size: 1.2em;
        margin: 20px 0;
    }
    .result-box {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# 初始化组件
@st.cache_resource
def init_components():
    audio_capture = AudioCapture()
    audio_processor = AudioProcessor()
    recognizer = FunASRRecognizer()
    return audio_capture, audio_processor, recognizer

# 初始化会话状态
if 'recording' not in st.session_state:
    st.session_state.recording = False
if 'recognized_text' not in st.session_state:
    st.session_state.recognized_text = ""
if 'audio_chunks' not in st.session_state:
    st.session_state.audio_chunks = []

# 初始化组件
audio_capture, audio_processor, recognizer = init_components()

# 标题
st.title("🎤 实时语音识别")

# 录音控制
col1, col2 = st.columns(2)
with col1:
    if st.button("开始录音", disabled=st.session_state.recording):
        st.session_state.recording = True
        st.session_state.audio_chunks = []
        audio_capture.start()
with col2:
    if st.button("停止录音", disabled=not st.session_state.recording):
        st.session_state.recording = False
        audio_capture.stop()

# 显示录音状态
if st.session_state.recording:
    st.markdown('<div class="recording-status">🎤 正在录音...</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="recording-status">⏸️ 录音已停止</div>', unsafe_allow_html=True)

# 显示识别结果
st.markdown('<div class="result-box">', unsafe_allow_html=True)
st.markdown("### 识别结果")
st.markdown(st.session_state.recognized_text)
st.markdown('</div>', unsafe_allow_html=True)

# 主循环
if st.session_state.recording:
    try:
        # 读取音频数据
        audio_data = audio_capture.read()
        if audio_data is not None:
            # 处理音频数据
            processed_audio = audio_processor.process(audio_data)
            # 识别音频
            text = recognizer.recognize(processed_audio)
            if text:
                st.session_state.recognized_text += text + " "
                st.experimental_rerun()
    except Exception as e:
        st.error(f"处理音频时出错: {str(e)}")
        st.session_state.recording = False

# 使用说明
st.markdown("""
### 使用说明
1. 点击"开始录音"按钮开始录音
2. 说话时，识别结果会实时显示
3. 点击"停止录音"按钮停止录音
4. 识别结果会保留在页面上
""") 