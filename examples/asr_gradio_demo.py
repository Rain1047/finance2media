import gradio as gr
import numpy as np
import soundfile as sf
from src.asr.audio_processor import AudioProcessor
from src.asr.funasr_recognizer import FunASRRecognizer
import librosa


def recognize_audio(audio_np, samplerate=16000):
    """调用 ASR 识别"""
    audio_processor = AudioProcessor(sample_rate=samplerate)
    recognizer = FunASRRecognizer()
    processed = audio_processor.preprocess(audio_np)
    text = recognizer.recognize(processed)
    return text


def process_audio(audio):
    """处理音频并返回识别结果"""
    try:
        print(f"audio 类型: {type(audio)}")
        if audio is None:
            return "未检测到音频"
        # Gradio 可能返回 (np.ndarray, int) 或 np.ndarray 或 int
        if isinstance(audio, tuple) and len(audio) == 2:
            # 检查 audio[0] 和 audio[1] 的类型，确保 audio_np 是 np.ndarray
            if isinstance(audio[0], np.ndarray):
                audio_np, sr = audio
            elif isinstance(audio[1], np.ndarray):
                audio_np, sr = audio[1], audio[0]
            else:
                return f"音频格式不支持: audio[0]={type(audio[0])}, audio[1]={type(audio[1])}"
        elif isinstance(audio, np.ndarray):
            audio_np = audio
            sr = 16000  # 默认采样率
        else:
            return f"音频格式不支持: {type(audio)}"
        print(f"audio_np 类型: {type(audio_np)}, shape: {getattr(audio_np, 'shape', None)}, sr: {sr}")
        if not isinstance(audio_np, np.ndarray):
            return f"未检测到有效音频数据，audio_np 类型: {type(audio_np)}"
        # 确保 audio_np 的数据类型为浮点型
        if audio_np.dtype != np.float32 and audio_np.dtype != np.float64:
            audio_np = audio_np.astype(np.float32)
        if isinstance(sr, (np.ndarray, list)):
            sr = int(np.array(sr).flatten()[0])
        if sr != 16000:
            print(f"采样率为 {sr}，将自动重采样到 16kHz")
            audio_np = librosa.resample(audio_np, orig_sr=sr, target_sr=16000)
        text = recognize_audio(audio_np, samplerate=16000)
        return text
    except Exception as e:
        print(f"处理音频时出错: {str(e)}")
        return f"处理音频时出错: {str(e)}"


# 创建 Gradio 界面
demo = gr.Interface(
    fn=process_audio,
    inputs=gr.Audio(sources=["microphone"], type="numpy", label="录音或上传音频"),
    outputs=gr.Textbox(label="识别结果"),
    title="实时语音识别 Demo",
    description="录音或上传 wav 文件，系统将自动识别并返回文本结果。",
    examples=[],
    cache_examples=False,
)

if __name__ == "__main__":
    demo.launch(share=True) 